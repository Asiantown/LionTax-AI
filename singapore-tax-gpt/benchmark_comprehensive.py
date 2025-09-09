#!/usr/bin/env python
"""Comprehensive benchmark with all major tax categories."""

import os
from dotenv import load_dotenv
load_dotenv()

# Set API keys
os.environ["CONFIDENT_API_KEY"] = os.getenv("CONFIDENT_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

print("🏆 Comprehensive Tax Questions Benchmark")
print("=" * 70)

from deepeval.dataset import EvaluationDataset, Golden
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval import evaluate
from qa_lite import answer_question
import openai
import time

# Comprehensive tax questions
questions = [
    # Tax Rates & Brackets
    "What are the current personal income tax rates for Singapore residents?",
    "What is the tax rate for non-residents?",
    "At what income level do I start paying income tax in Singapore?",
    "What is the highest marginal tax rate for individuals?",
    "How is tax calculated for someone earning S$80,000 annually?",
    
    # Tax Reliefs & Rebates
    "What personal reliefs am I entitled to as a Singapore resident?",
    "How much can I claim for spouse relief if my spouse has no income?",
    "What is the maximum amount I can claim for child relief?",
    "Can I claim tax relief for my parents? What are the conditions?",
    "What is the Earned Income Relief and how is it calculated?",
    "What reliefs are available for CPF contributions?",
    "Can I claim relief for insurance premiums? What types qualify?",
    
    # Filing Requirements & Deadlines
    "When is the deadline for filing my tax return?",
    "Who is required to file a tax return in Singapore?",
    "What happens if I file my tax return late?",
    "Can I get an extension for filing my tax return?",
    "How long should I keep my tax records?",
    
    # Employment Income
    "Is my 13th month bonus taxable?",
    "How are stock options taxed in Singapore?",
    "Are overseas allowances taxable for Singapore tax residents?",
    "How is director's fee taxed?",
    "What employment benefits are tax-exempt?",
    
    # Investment & Rental Income
    "Do I need to pay tax on dividends received from Singapore companies?",
    "How is rental income from my property taxed?",
    "Are capital gains from selling shares taxable?",
    "How do I report foreign investment income?",
    "What about interest income from savings accounts?",
]

# Create dataset
dataset = EvaluationDataset()
dataset.goldens = [Golden(input=q) for q in questions]
print(f"Testing {len(questions)} comprehensive questions\n")

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

# 2. GPT-4 with progress
print("\n🤖 Testing GPT-4...")
client = openai.OpenAI()
gpt4_cases = []
start_time = time.time()

for i, golden in enumerate(dataset.goldens, 1):
    print(f"  Q{i}/{len(dataset.goldens)}: {golden.input[:50]}...", end="", flush=True)
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Singapore tax expert. Answer concisely."},
                {"role": "user", "content": golden.input}
            ],
            temperature=0,
            max_tokens=300
        )
        gpt4_cases.append(LLMTestCase(input=golden.input, actual_output=response.choices[0].message.content))
        print(" ✅")
    except Exception as e:
        print(f" ❌ {str(e)[:30]}")
        gpt4_cases.append(LLMTestCase(input=golden.input, actual_output="Error occurred"))

gpt4_time = time.time() - start_time
print(f"✅ GPT-4 complete ({gpt4_time:.1f}s, {len(gpt4_cases)} cases)")

# Upload results
print("\n📤 Uploading to Confident AI...")

try:
    # LionTax
    print("  Uploading LionTax results...", end="")
    evaluate(
        test_cases=liontax_cases,
        metrics=[metric],
        hyperparameters={"model": "LionTax", "time": f"{liontax_time:.1f}s"}
    )
    print(" ✅")
except Exception as e:
    print(f" ❌ {e}")

try:
    # GPT-4
    print("  Uploading GPT-4 results...", end="")
    evaluate(
        test_cases=gpt4_cases,
        metrics=[metric],
        hyperparameters={"model": "GPT-4", "time": f"{gpt4_time:.1f}s"}
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
- GPT-4: {gpt4_time:.1f}s for {len(questions)} questions

Speed difference: {gpt4_time/liontax_time:.1f}x

TO COMPARE IN CONFIDENT AI:
1. Go to https://app.confident-ai.com
2. Find 'Compare Test Results' in sidebar
3. Select both recent test runs
4. View side-by-side comparison
""")