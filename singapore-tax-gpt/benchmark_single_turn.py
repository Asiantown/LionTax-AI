#!/usr/bin/env python
"""Single-Turn E2E Testing for LionTax - Following Confident AI Docs."""

import os
from dotenv import load_dotenv
load_dotenv()

# Set API keys from .env
os.environ["CONFIDENT_API_KEY"] = os.getenv("CONFIDENT_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

print("🏆 Singapore Tax Single-Turn Benchmarking")
print("=" * 70)

from deepeval.dataset import EvaluationDataset, Golden
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval import evaluate
from qa_lite import answer_question

# Step 1: Create comprehensive dataset
print("\n📊 Creating comprehensive IRAS dataset...")

# Your comprehensive IRAS questions
iras_questions = [
    "What is the GST rate in Singapore?",
    "What is the current corporate tax rate?",
    "What is the maximum personal income tax rate?",
    "What is the tax-free personal income threshold?",
    "When is the tax filing deadline?",
    "How much is the earned income relief?",
    "What is the NSman relief?",
    "Is my bonus taxable?",
    "Are capital gains taxed in Singapore?",
    "What is the 183-day rule for tax residency?",
    "Can I deduct home office expenses?",
    "What is the child relief amount?",
    "How is rental income taxed?",
    "Are dividends from Singapore companies taxable?",
    "What is the penalty for late filing?",
    "How do I file my income tax?",
    "What documents do I need for tax filing?",
    "Are stock options taxable?",
    "How is commission income taxed?",
    "Is overtime pay taxable?",
    "How are employment benefits taxed?",
    "Are retrenchment benefits taxable?",
    "How is sole proprietorship income taxed?",
    "What is the partial tax exemption for companies?",
    "How do I determine my tax residency status?",
    "Do I need to pay tax on overseas income?",
    "How are expatriates taxed in Singapore?",
    "Are medical expenses deductible?",
    "What donations are tax deductible?",
    "Can I deduct insurance premiums?",
    "How can I check my tax assessment?",
    "What payment methods are available for taxes?",
    "Can I pay tax by installments?",
    "What is GIRO and should I sign up?",
    "Is there interest charged on late payment?",
    "What is tax evasion and its penalties?",
    "Can penalties be waived?",
    "What triggers a tax audit?",
    "I inherited property, is this taxable?",
    "I won the lottery, do I pay tax on winnings?",
    "Do I need to register for GST?",
    "What is the GST registration threshold?",
    "Which goods and services are GST-exempt?",
    "How is property tax calculated?",
    "What is the annual value of property?",
    "新加坡的个人所得税率是多少？",
    "我需要缴税吗？",
    "什么是税务居民？",
    "如何申报所得税？",
    "税务减免有哪些？",
]

# Create goldens
goldens = [Golden(input=q) for q in iras_questions]

# Create dataset
dataset = EvaluationDataset(goldens=goldens)

# Push to Confident AI
try:
    dataset.push(alias="singapore-tax-comprehensive")
    print(f"✅ Pushed {len(goldens)} questions to 'singapore-tax-comprehensive'")
except:
    dataset.pull(alias="singapore-tax-comprehensive")
    print(f"✅ Using existing dataset with {len(dataset.goldens)} questions")

# Step 2: Define metrics
print("\n📏 Defining evaluation metrics...")

relevancy = AnswerRelevancyMetric(
    threshold=0.7,
    model="gpt-3.5-turbo"
)

accuracy = GEval(
    name="Singapore Tax Accuracy",
    criteria="Evaluate if the answer contains accurate Singapore tax information including correct rates, thresholds, deadlines, and regulations",
    evaluation_params=["input", "actual_output"],
    threshold=0.7,
    model="gpt-3.5-turbo"
)

completeness = GEval(
    name="Answer Completeness",
    criteria="Check if the answer fully addresses all aspects of the tax question without missing important details",
    evaluation_params=["input", "actual_output"],
    threshold=0.7,
    model="gpt-3.5-turbo"
)

metrics = [relevancy, accuracy, completeness]
print(f"✅ Created {len(metrics)} metrics")

# Step 3: Generate test cases
print(f"\n🧪 Generating test cases for {len(dataset.goldens)} questions...")

test_cases = []
for i, golden in enumerate(dataset.goldens, 1):
    if i % 10 == 0:
        print(f"  Processing {i}/{len(dataset.goldens)}...")
    
    # Get LionTax response
    actual_output, sources = answer_question(golden.input)
    
    # Create test case
    test_case = LLMTestCase(
        input=golden.input,
        actual_output=actual_output,
        retrieval_context=sources if sources else None
    )
    test_cases.append(test_case)
    dataset.add_test_case(test_case)

print(f"✅ Created {len(test_cases)} test cases")

# Step 4: Run evaluation
print("\n🎯 Running evaluation on Confident AI...")
print("This will take a few minutes...")

results = evaluate(
    test_cases=test_cases,
    metrics=metrics,
    hyperparameters={
        "model": "LionTax-Groq-Qwen",
        "dataset": "singapore-tax-comprehensive",
        "questions": len(test_cases)
    }
)

print("\n" + "=" * 70)
print("✅ EVALUATION COMPLETE!")
print("=" * 70)

print("\n📊 Results Summary:")
print(f"  - Questions tested: {len(test_cases)}")
print(f"  - Metrics used: {', '.join([m.name for m in metrics])}")
print(f"  - Model: LionTax (Groq Qwen)")

print("\n🌐 View detailed results at:")
print("   https://app.confident-ai.com")
print("   → Project → Test Runs")

print("\n📈 What you'll see:")
print("  • Pass/fail rate for each metric")
print("  • Score distribution across all questions")
print("  • Detailed breakdown per test case")
print("  • AI-generated insights on failures")

print("\n🔄 To compare with other models:")
print("  1. Run this script again after modifying to use GPT-4/Claude")
print("  2. Go to 'Compare Test Results' in Confident AI")
print("  3. Select multiple test runs to compare side-by-side")