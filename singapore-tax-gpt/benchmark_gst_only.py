#!/usr/bin/env python
"""Benchmark with GST question only."""

import os
from dotenv import load_dotenv
load_dotenv()

# Set API keys
os.environ["CONFIDENT_API_KEY"] = os.getenv("CONFIDENT_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

print("🏆 GST Question Benchmark")
print("=" * 70)

from deepeval.dataset import EvaluationDataset, Golden
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval import evaluate
from qa_lite import answer_question
import openai
import time

# Single GST question
questions = [
    "What is the current GST rate in Singapore?",
]

# Create dataset
dataset = EvaluationDataset()
dataset.goldens = [Golden(input=q) for q in questions]
print(f"Testing {len(questions)} question\n")

# Simple metric
metric = AnswerRelevancyMetric(threshold=0.5, model="gpt-3.5-turbo")

print("="*70)
print("TESTING BOTH MODELS")
print("="*70)

# 1. LionTax
print("\n🤖 Testing LionTax (Groq)...")
liontax_cases = []
start_time = time.time()

for golden in dataset.goldens:
    output, _ = answer_question(golden.input)
    liontax_cases.append(LLMTestCase(input=golden.input, actual_output=output))
    print(f"  Answer: {output}")
        
liontax_time = time.time() - start_time
print(f"✅ LionTax complete ({liontax_time:.1f}s)")

# 2. GPT-4
print("\n🤖 Testing GPT-4...")
client = openai.OpenAI()
gpt4_cases = []
start_time = time.time()

for golden in dataset.goldens:
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
    print(f"  Answer: {response.choices[0].message.content}")

gpt4_time = time.time() - start_time
print(f"✅ GPT-4 complete ({gpt4_time:.1f}s)")

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