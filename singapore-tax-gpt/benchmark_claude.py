#!/usr/bin/env python
"""Benchmark comparing LionTax with Claude."""

import os
from dotenv import load_dotenv
load_dotenv()

# Set API keys
os.environ["CONFIDENT_API_KEY"] = os.getenv("CONFIDENT_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

print("🏆 LionTax vs Claude Benchmark")
print("=" * 70)

from deepeval.dataset import EvaluationDataset, Golden
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval import evaluate
from qa_lite import answer_question
import anthropic
import time
import time as sleep_time

# All comprehensive tax questions
questions = [
    # Foreign Income & Tax Residency
    "How do I determine if I'm a Singapore tax resident?",
    "Do I need to pay Singapore tax on my overseas income?",
    "What is foreign tax credit and how do I claim it?",
    "How many days must I be in Singapore to be considered a tax resident?",
    "What if I'm a new citizen or PR - when does tax residency start?",
    
    # Special Situations
    "How is retrenchment benefit taxed?",
    "What about income from freelancing or gig economy work?",
    "How are gambling winnings taxed?",
    "Do I pay tax on inheritance received?",
    "How is income from cryptocurrency trading taxed?",
    
    # Deductions & Expenses
    "Can I claim deduction for medical expenses?",
    "What course fees are eligible for tax relief?",
    "Can I deduct home office expenses if I work from home?",
    "Are donations to charities tax deductible? Which organizations qualify?",
    "What are the limits for course fee relief claims?",
    
    # Administrative Procedures
    "How do I submit my tax return online?",
    "Can I authorize someone to file my tax return for me?",
    "How do I appeal against my tax assessment?",
    "What documents do I need to support my tax return?",
    "How can I check the status of my tax refund?",
    
    # Penalties & Compliance
    "What are the penalties for not filing tax returns?",
    "What happens if I underdeclare my income?",
    "Can IRAS audit my tax return? What triggers an audit?",
    "What are the penalties for late payment of taxes?",
    "How do I report errors in my previously filed tax return?",
    
    # Complex Scenarios (Edge Cases)
    "I worked in Singapore for 6 months and overseas for 6 months. How do I file my taxes?",
    "I'm divorced and share custody of my child. Who can claim the child relief?",
    "My employer provided me with a company car. Is this a taxable benefit?",
    "I received a lump sum pension withdrawal. How is this taxed?",
    "I'm a foreign talent on an employment pass. What tax obligations do I have?",
    
    # GST-Related Questions
    "Do I need to register for GST for my small business?",
    "What is the current GST rate in Singapore?",
    "What purchases are GST-exempt?",
    "How do I claim GST input tax?",
    "When must I charge GST to my customers?",
    
    # Property Tax
    "How is property tax calculated for my HDB flat?",
    "What's the difference between owner-occupied and non-owner-occupied property tax rates?",
    "Do I pay property tax on overseas properties?",
    
    # Test Edge Cases & Ambiguous Queries
    "My friend told me I don't need to pay tax on my side income, is this true?",
    "What tax do I pay?",
    "I think IRAS made a mistake on my assessment, what should I do?",
    "Is Bitcoin income taxable?",
    "My company wants to relocate me overseas, what are the tax implications?",
]

# Create dataset
dataset = EvaluationDataset()
dataset.goldens = [Golden(input=q) for q in questions]
print(f"Testing {len(questions)} questions across all categories\n")

# Simple metric
metric = AnswerRelevancyMetric(threshold=0.5, model="gpt-3.5-turbo")

print("="*70)
print("TESTING BOTH MODELS")
print("="*70)

# 1. LionTax with progress
print("\n🤖 Testing LionTax (Groq)...")
liontax_cases = []
start_time = time.time()

for i, golden in enumerate(dataset.goldens, 1):
    print(f"  Q{i}/{len(dataset.goldens)}: {golden.input[:50]}...", end="", flush=True)
    try:
        output, _ = answer_question(golden.input)
        liontax_cases.append(LLMTestCase(input=golden.input, actual_output=output))
        print(" ✅")
    except Exception as e:
        print(f" ❌ {str(e)[:30]}")
        liontax_cases.append(LLMTestCase(input=golden.input, actual_output="Error occurred"))
        
liontax_time = time.time() - start_time
print(f"✅ LionTax complete ({liontax_time:.1f}s, {len(liontax_cases)} cases)")

# 2. Claude with progress
print("\n🤖 Testing Claude (Anthropic)...")
client = anthropic.Anthropic()
claude_cases = []
start_time = time.time()

for i, golden in enumerate(dataset.goldens, 1):
    print(f"  Q{i}/{len(dataset.goldens)}: {golden.input[:50]}...", end="", flush=True)
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            temperature=0,
            system="You are a Singapore tax expert. Answer concisely.",
            messages=[
                {"role": "user", "content": golden.input}
            ]
        )
        claude_cases.append(LLMTestCase(input=golden.input, actual_output=response.content[0].text))
        print(" ✅")
        time.sleep(0.5)  # Small delay to avoid rate limiting
    except Exception as e:
        print(f" ❌ Error: {str(e)}")
        claude_cases.append(LLMTestCase(input=golden.input, actual_output=f"Error: {str(e)[:100]}"))

claude_time = time.time() - start_time
print(f"✅ Claude complete ({claude_time:.1f}s, {len(claude_cases)} cases)")

# Upload results
print("\n📤 Uploading to Confident AI...")

try:
    # LionTax
    print("  Uploading LionTax results...", end="")
    evaluate(
        test_cases=liontax_cases,
        metrics=[metric],
        hyperparameters={"model": "LionTax", "time": f"{liontax_time:.1f}s", "questions": len(questions)}
    )
    print(" ✅")
except Exception as e:
    print(f" ❌ {e}")

try:
    # Claude
    print("  Uploading Claude results...", end="")
    evaluate(
        test_cases=claude_cases,
        metrics=[metric],
        hyperparameters={"model": "Claude-3.5-Sonnet", "time": f"{claude_time:.1f}s", "questions": len(questions)}
    )
    print(" ✅")
except Exception as e:
    print(f" ❌ {e}")

print("\n" + "="*70)
print("✅ COMPLETE!")
print("="*70)
print(f"""
Performance Summary:
- LionTax: {liontax_time:.1f}s for {len(questions)} questions
- Claude: {claude_time:.1f}s for {len(questions)} questions

Speed difference: {claude_time/liontax_time:.1f}x

TO COMPARE IN CONFIDENT AI:
1. Go to https://app.confident-ai.com
2. Find 'Compare Test Results' in sidebar
3. Select both recent test runs
4. View side-by-side comparison
""")