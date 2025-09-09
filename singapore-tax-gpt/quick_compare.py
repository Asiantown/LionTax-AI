#!/usr/bin/env python
"""Quick comparison with 20 key questions."""

import os
from dotenv import load_dotenv
load_dotenv()

# Set API keys
os.environ["CONFIDENT_API_KEY"] = os.getenv("CONFIDENT_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

print("🏆 Quick Model Comparison (20 Questions)")
print("=" * 70)

from deepeval.dataset import EvaluationDataset, Golden
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval import evaluate
from qa_lite import answer_question
import openai
import time

# HARD EDGE CASES & CHINESE QUESTIONS
questions = [
    # Complex scenarios
    "I arrived in Singapore on March 15, left on July 20, returned September 1, and stayed till December 31. Am I a tax resident?",
    "My employer gave me $50,000 in stock options that vest over 3 years but I'm leaving Singapore after 1 year. How is this taxed?",
    "I earn $35,000 from my job, $15,000 from freelancing, and $8,000 from rental. How much tax do I pay?",
    "I'm divorced, my ex-spouse and I alternate claiming our child every year. This year is my turn but my ex already filed. What do I do?",
    "I sold my HDB for a $200,000 profit and bought a condo. Do I pay tax on the profit?",
    
    # Ambiguous/Tricky questions
    "GST going up or not?",
    "tax",
    "How to pay less tax legally?",
    "My friend says I don't need to declare cash income, true or not?",
    "I work in Singapore but my company is in Malaysia and pays me in Malaysia. Where do I pay tax?",
    
    # Chinese questions (testing bilingual capability)
    "新加坡的个人所得税最高是多少？",
    "我是外国人，在新加坡工作，需要交多少税？",
    "CPF可以扣税吗？怎么计算？",
    "我的花红需要缴税吗？",
    "在新加坡买卖股票赚的钱要交税吗？",
    
    # Very specific edge cases
    "I received a $100,000 inheritance from my uncle in Malaysia, invested it in Singapore REITs, and earned $5,000 dividends. What's taxable?",
    "I'm a Grab driver earning $3,000/month and also rent out my HDB room for $800/month. Do I need to register for GST?",
    "My company is relocating me to Hong Kong in June 2024 but I'll keep my Singapore PR. How does this affect my 2024 taxes?",
    "I day-trade cryptocurrency and made $500,000 profit but lost $450,000. Do I pay tax on the $50,000 net or $500,000 gross?",
    "I'm 17 years old working part-time earning $15,000/year. Do I file taxes? Can my parents claim relief for me?",
]

# Create dataset
dataset = EvaluationDataset()
dataset.goldens = [Golden(input=q) for q in questions]
print(f"Testing {len(questions)} key questions\n")

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
    print(f"  Q{i}/{len(dataset.goldens)}: {golden.input[:40]}...", end="", flush=True)
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
    print(f"  Q{i}/{len(dataset.goldens)}: {golden.input[:40]}...", end="", flush=True)
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Singapore tax expert."},
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

TO COMPARE IN CONFIDENT AI:
1. Go to https://app.confident-ai.com
2. Find 'Compare Test Results' in sidebar
3. Select both recent test runs
4. View side-by-side comparison
""")