#!/usr/bin/env python
"""Benchmark LionTax vs GPT-4 vs Claude on Confident AI."""

import os
from dotenv import load_dotenv
load_dotenv()

# Set API keys from .env
os.environ["CONFIDENT_API_KEY"] = os.getenv("CONFIDENT_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

print("🏆 Multi-Model Singapore Tax Benchmarking")
print("=" * 70)

from deepeval.dataset import EvaluationDataset, Golden
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval import evaluate
from qa_lite import answer_question
import openai
from anthropic import Anthropic

# Define test questions (subset for faster testing)
test_questions = [
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
    "How is rental income taxed?",
    "What is the penalty for late filing?",
    "新加坡的个人所得税率是多少？",
    "什么是税务居民？",
]

# Use existing dataset (FREE plan only allows 1 dataset)
print("\n📊 Using existing dataset...")
dataset = EvaluationDataset()
dataset.pull(alias="singapore-tax-iras")
print(f"✅ Loaded existing dataset with {len(dataset.goldens)} questions")

# Use subset for faster testing
dataset.goldens = dataset.goldens[:15]  # Use first 15 questions
print(f"📝 Using {len(dataset.goldens)} questions for comparison")

# Define metrics
print("\n📏 Setting up metrics...")
metrics = [
    AnswerRelevancyMetric(threshold=0.7, model="gpt-3.5-turbo"),
    GEval(
        name="Tax Accuracy",
        criteria="Check if the answer contains accurate Singapore tax information",
        evaluation_params=["input", "actual_output"],
        threshold=0.7,
        model="gpt-3.5-turbo"
    )
]

def test_liontax():
    """Test LionTax (Groq Qwen)."""
    print("\n🤖 Testing LionTax...")
    test_cases = []
    
    for golden in dataset.goldens:
        actual_output, sources = answer_question(golden.input)
        test_case = LLMTestCase(
            input=golden.input,
            actual_output=actual_output,
            retrieval_context=sources if sources else None
        )
        test_cases.append(test_case)
    
    # Run evaluation with model identifier
    evaluate(
        test_cases=test_cases,
        metrics=metrics,
        hyperparameters={"model": "LionTax-Groq-Qwen", "provider": "Groq"}
    )
    print("✅ LionTax evaluation complete")
    return test_cases

def test_gpt4():
    """Test GPT-4."""
    print("\n🤖 Testing GPT-4...")
    client = openai.OpenAI()
    test_cases = []
    
    for golden in dataset.goldens:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Singapore tax expert. Provide accurate, concise answers."},
                {"role": "user", "content": golden.input}
            ],
            temperature=0,
            max_tokens=500
        )
        
        test_case = LLMTestCase(
            input=golden.input,
            actual_output=response.choices[0].message.content
        )
        test_cases.append(test_case)
    
    # Run evaluation with model identifier
    evaluate(
        test_cases=test_cases,
        metrics=metrics,
        hyperparameters={"model": "GPT-4", "provider": "OpenAI"}
    )
    print("✅ GPT-4 evaluation complete")
    return test_cases

def test_claude():
    """Test Claude-3."""
    print("\n🤖 Testing Claude-3 Sonnet...")
    client = Anthropic()
    test_cases = []
    
    for golden in dataset.goldens:
        response = client.messages.create(
            model="claude-3-sonnet-20241022",
            max_tokens=500,
            temperature=0,
            messages=[
                {"role": "user", "content": f"You are a Singapore tax expert. Answer this concisely and accurately: {golden.input}"}
            ]
        )
        
        test_case = LLMTestCase(
            input=golden.input,
            actual_output=response.content[0].text
        )
        test_cases.append(test_case)
    
    # Run evaluation with model identifier
    evaluate(
        test_cases=test_cases,
        metrics=metrics,
        hyperparameters={"model": "Claude-3-Sonnet", "provider": "Anthropic"}
    )
    print("✅ Claude-3 evaluation complete")
    return test_cases

# Run all model tests
print("\n" + "=" * 70)
print("🚀 RUNNING ALL MODEL EVALUATIONS")
print("=" * 70)

results = {}

# Test LionTax
try:
    results["LionTax"] = test_liontax()
except Exception as e:
    print(f"❌ LionTax error: {e}")

# Test GPT-4
if os.getenv("OPENAI_API_KEY"):
    try:
        results["GPT-4"] = test_gpt4()
    except Exception as e:
        print(f"❌ GPT-4 error: {e}")
else:
    print("\n⚠️ Skipping GPT-4 (no API key)")

# Test Claude
if os.getenv("ANTHROPIC_API_KEY"):
    try:
        results["Claude-3"] = test_claude()
    except Exception as e:
        print(f"❌ Claude error: {e}")
else:
    print("\n⚠️ Skipping Claude (no API key)")

print("\n" + "=" * 70)
print("✅ ALL EVALUATIONS COMPLETE!")
print("=" * 70)

print("\n📊 COMPARING MODELS ON CONFIDENT AI:")
print("1. Go to: https://app.confident-ai.com")
print("2. Click 'Compare Test Results' in sidebar")
print("3. Select the test runs labeled:")
for model in results.keys():
    print(f"   • {model}")

print("\n📈 The comparison will show:")
print("  • Side-by-side accuracy scores")
print("  • Which model performs best per question")
print("  • Cost vs performance analysis")
print("  • Detailed metric breakdowns")

print(f"\n✨ Total test runs created: {len(results)}")
print(f"   Questions per model: {len(test_questions)}")
print(f"   Metrics evaluated: Answer Relevancy, Tax Accuracy")