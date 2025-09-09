#!/usr/bin/env python
"""Confident AI Quickstart - Following official docs exactly."""

import os
from dotenv import load_dotenv
load_dotenv()

# Step 1: Set API keys
os.environ["CONFIDENT_API_KEY"] = "confident_us_FDfVbEnV7U0mP+ywkdeKj6Uhtic2VeNoVaO7dgqQTLY="
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

print("🚀 Confident AI Quickstart - Singapore Tax Benchmarking")
print("=" * 70)

# Import after setting keys
from deepeval.dataset import EvaluationDataset, Golden
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval import evaluate

# Import your LLM app
from qa_lite import answer_question

# Step 1: Create a dataset with IRAS questions
print("\n📊 Step 1: Creating dataset...")

goldens = [
    Golden(input="What is the GST rate in Singapore?"),
    Golden(input="What is the current corporate tax rate in Singapore?"),
    Golden(input="What is the maximum personal income tax rate?"),
    Golden(input="What is the tax-free personal income threshold?"),
    Golden(input="When is the tax filing deadline?"),
    Golden(input="How much is the earned income relief?"),
    Golden(input="What is the NSman relief?"),
    Golden(input="Is my bonus taxable?"),
    Golden(input="Are capital gains taxed in Singapore?"),
    Golden(input="What is the 183-day rule for tax residency?"),
    Golden(input="Can I deduct home office expenses?"),
    Golden(input="What is the child relief amount?"),
    Golden(input="How is rental income taxed?"),
    Golden(input="Are dividends from Singapore companies taxable?"),
    Golden(input="What is the penalty for late filing?"),
    Golden(input="新加坡的个人所得税率是多少？"),
    Golden(input="我需要缴税吗？"),
    Golden(input="什么是税务居民？"),
    Golden(input="How do I file my income tax?"),
    Golden(input="What documents do I need for tax filing?"),
]

# Create dataset
dataset = EvaluationDataset(goldens=goldens)

# Save to Confident AI
try:
    dataset.push(alias="singapore-tax-iras")
    print(f"✅ Dataset 'singapore-tax-iras' created with {len(goldens)} questions")
except Exception as e:
    print(f"⚠️ Dataset might already exist: {e}")

# Step 2: Create a metric
print("\n📏 Step 2: Creating metric...")
relevancy = AnswerRelevancyMetric()  # Using this for simplicity
print("✅ Created AnswerRelevancyMetric")

# Step 3: Configure evaluation model
print("\n🤖 Step 3: Evaluation model configured (using OpenAI)")

# Step 4: Create test cases
print("\n🧪 Step 4: Creating test cases...")

# Pull from Confident AI (in case it was already created)
dataset = EvaluationDataset()
dataset.pull(alias="singapore-tax-iras")

# Create test cases
for i, golden in enumerate(dataset.goldens, 1):
    print(f"  Processing {i}/{len(dataset.goldens)}: {golden.input[:50]}...")
    
    # Call your LLM app
    actual_output, _ = answer_question(golden.input)
    
    test_case = LLMTestCase(
        input=golden.input,
        actual_output=actual_output
    )
    dataset.add_test_case(test_case)

print(f"✅ Created {len(dataset.test_cases)} test cases")

# Step 5: Run evaluation
print("\n🎯 Step 5: Running evaluation...")
print("This will upload results to Confident AI...")

# Run an evaluation
results = evaluate(
    test_cases=dataset.test_cases, 
    metrics=[relevancy]
)

print("\n" + "=" * 70)
print("✅ EVALUATION COMPLETE!")
print("=" * 70)
print("\n📊 View your results at: https://app.confident-ai.com")
print("   Navigate to: Project > Test Runs")
print("\n📈 What you'll see:")
print("   - Testing report with all test cases")
print("   - Metric scores and distributions")
print("   - Pass/fail status for each question")
print("   - AI-generated insights")
print("\n🔄 Next steps:")
print("   1. Run again to create another test run for regression testing")
print("   2. Add more metrics (Correctness, Hallucination, etc.)")
print("   3. Compare different model versions")