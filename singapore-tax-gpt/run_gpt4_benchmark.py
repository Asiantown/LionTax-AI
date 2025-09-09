#!/usr/bin/env python
"""Run GPT-4 benchmark separately to create a comparable test run."""

import os
from dotenv import load_dotenv
load_dotenv()

# Set API keys
os.environ["CONFIDENT_API_KEY"] = os.getenv("CONFIDENT_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

print("🏆 GPT-4 Singapore Tax Benchmark")
print("=" * 70)

from deepeval.dataset import EvaluationDataset, Golden
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval import evaluate
import openai

# Same 20 questions as LionTax
curated_questions = [
    # Tax Rates (3)
    "What is the GST rate in Singapore?",
    "What is the tax rate for non-residents?",
    "How is tax calculated for someone earning S$80,000 annually?",
    
    # Reliefs & Rebates (3)
    "What is the Earned Income Relief and how is it calculated?",
    "Can I claim tax relief for my parents? What are the conditions?",
    "What reliefs are available for CPF contributions?",
    
    # Filing & Deadlines (2)
    "When is the deadline for filing my tax return?",
    "What happens if I file my tax return late?",
    
    # Employment Income (2)
    "Is my 13th month bonus taxable?",
    "How are stock options taxed in Singapore?",
    
    # Investment & Business (2)
    "Do I need to pay tax on dividends received from Singapore companies?",
    "Are capital gains from selling shares taxable?",
    
    # Foreign Income & Residency (2)
    "How do I determine if I'm a Singapore tax resident?",
    "How many days must I be in Singapore to be considered a tax resident?",
    
    # Special Situations (2)
    "How is income from cryptocurrency trading taxed?",
    "Do I pay tax on inheritance received?",
    
    # Deductions & Admin (2)
    "Are donations to charities tax deductible? Which organizations qualify?",
    "How do I appeal against my tax assessment?",
    
    # Penalties & Property (2)
    "What are the penalties for not filing tax returns?",
    "How is property tax calculated for my HDB flat?",
]

# Create dataset
dataset = EvaluationDataset()
for q in curated_questions:
    dataset.goldens.append(Golden(input=q))

print(f"📝 Testing GPT-4 with {len(dataset.goldens)} questions")

# Set up metric
metric = AnswerRelevancyMetric(
    threshold=0.5,
    model="gpt-3.5-turbo"
)

# Test GPT-4
print("\n🤖 Getting GPT-4 responses...")
client = openai.OpenAI()
test_cases = []

for i, golden in enumerate(dataset.goldens, 1):
    print(f"  Processing {i}/{len(dataset.goldens)}: {golden.input[:40]}...")
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Singapore tax expert. Provide accurate, concise answers."},
            {"role": "user", "content": golden.input}
        ],
        temperature=0,
        max_tokens=300
    )
    
    test_case = LLMTestCase(
        input=golden.input,
        actual_output=response.choices[0].message.content
    )
    test_cases.append(test_case)

print(f"✅ Created {len(test_cases)} test cases")

# Run evaluation
print("\n📤 Uploading GPT-4 results to Confident AI...")
try:
    results = evaluate(
        test_cases=test_cases,
        metrics=[metric],
        hyperparameters={"model": "GPT-4", "provider": "OpenAI"}
    )
    print("\n" + "=" * 70)
    print("✅ GPT-4 EVALUATION COMPLETE!")
    print("=" * 70)
    print("\n📊 Now you have 2 test runs to compare:")
    print("  1. LionTax (Groq Qwen)")
    print("  2. GPT-4 (OpenAI)")
    print("\n🔍 TO COMPARE:")
    print("  1. Go to https://app.confident-ai.com")
    print("  2. Click 'Compare Test Results' in sidebar")
    print("  3. Select both test runs")
    print("  4. View side-by-side comparison!")
except Exception as e:
    print(f"❌ Error: {e}")