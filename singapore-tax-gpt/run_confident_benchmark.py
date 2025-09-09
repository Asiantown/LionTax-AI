#!/usr/bin/env python
"""Run benchmarks and upload to Confident AI."""

import os
from dotenv import load_dotenv
load_dotenv()

# IMPORTANT: Set the Confident AI key
os.environ["CONFIDENT_API_KEY"] = "confident_us_FDfVbEnV7U0mP+ywkdeKj6Uhtic2VeNoVaO7dgqQTLY="

print("🔑 Setting up Confident AI...")
print(f"API Key: {os.environ.get('CONFIDENT_API_KEY', 'NOT SET')[:20]}...")

# Now import DeepEval AFTER setting the key
from deepeval import login_with_confident_api_key, evaluate
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase
from qa_lite import answer_question

# Login to Confident AI
try:
    login_with_confident_api_key(api_key=os.environ["CONFIDENT_API_KEY"])
    print("✅ Logged in to Confident AI")
except Exception as e:
    print(f"⚠️ Login warning: {e}")

print("\n🏆 Running Singapore Tax Benchmarks")
print("=" * 70)

# Test questions
test_questions = [
    "What is the GST rate in Singapore?",
    "What is the corporate tax rate?",
    "What is the maximum personal income tax rate?",
    "When is the tax filing deadline?",
    "Are capital gains taxed in Singapore?"
]

# Create test cases
test_cases = []
for q in test_questions:
    print(f"\nTesting: {q}")
    actual_output, _ = answer_question(q)
    print(f"Response: {actual_output[:100]}...")
    
    test_case = LLMTestCase(
        input=q,
        actual_output=actual_output
    )
    test_cases.append(test_case)

# Define metric
relevancy_metric = AnswerRelevancyMetric(
    threshold=0.5,
    model="gpt-3.5-turbo"
)

# Run evaluation - this uploads to Confident AI
print("\n📤 Uploading to Confident AI...")
try:
    results = evaluate(
        test_cases=test_cases,
        metrics=[relevancy_metric]
    )
    print("\n✅ Results uploaded to Confident AI!")
    print("📊 View at: https://app.confident-ai.com")
except Exception as e:
    print(f"\n❌ Upload failed: {e}")
    print("Make sure you have a Confident AI account and the API key is correct")

print("\nTo view results:")
print("1. Go to https://app.confident-ai.com")
print("2. Log in with your account")
print("3. Check the 'Test Runs' section")