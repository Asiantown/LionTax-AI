#!/usr/bin/env python
"""Compare LionTax vs GPT-4 vs Claude on Confident AI."""

import os
from dotenv import load_dotenv
load_dotenv()

# Set API keys
os.environ["CONFIDENT_API_KEY"] = "confident_us_FDfVbEnV7U0mP+ywkdeKj6Uhtic2VeNoVaO7dgqQTLY="
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

print("🏆 Model Comparison: LionTax vs GPT-4 vs Claude")
print("=" * 70)

from deepeval.dataset import EvaluationDataset
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval import evaluate, assert_test
import openai
from anthropic import Anthropic
from qa_lite import answer_question

# Pull existing dataset
print("\n📊 Pulling dataset from Confident AI...")
dataset = EvaluationDataset()
dataset.pull(alias="singapore-tax-iras")
print(f"✅ Loaded {len(dataset.goldens)} questions")

# Define metrics
relevancy = AnswerRelevancyMetric()
correctness = GEval(
    name="Correctness",
    criteria="Check if the answer contains accurate Singapore tax information",
    evaluation_params=["input", "actual_output"],
    threshold=0.7
)
metrics = [relevancy, correctness]

def run_liontax_eval():
    """Run evaluation for LionTax."""
    print("\n🤖 Testing LionTax (Groq Qwen)...")
    test_cases = []
    
    for golden in dataset.goldens:
        actual_output, _ = answer_question(golden.input)
        test_case = LLMTestCase(
            input=golden.input,
            actual_output=actual_output
        )
        test_cases.append(test_case)
    
    # Run evaluation
    evaluate(
        test_cases=test_cases,
        metrics=metrics
    )
    print("✅ LionTax evaluation complete")

def run_gpt4_eval():
    """Run evaluation for GPT-4."""
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
            temperature=0
        )
        
        test_case = LLMTestCase(
            input=golden.input,
            actual_output=response.choices[0].message.content
        )
        test_cases.append(test_case)
    
    # Run evaluation
    evaluate(
        test_cases=test_cases,
        metrics=metrics
    )
    print("✅ GPT-4 evaluation complete")

def run_claude_eval():
    """Run evaluation for Claude."""
    print("\n🤖 Testing Claude-3...")
    client = Anthropic()
    test_cases = []
    
    for golden in dataset.goldens:
        response = client.messages.create(
            model="claude-3-sonnet-20241022",
            max_tokens=500,
            temperature=0,
            messages=[
                {"role": "user", "content": f"You are a Singapore tax expert. Answer concisely: {golden.input}"}
            ]
        )
        
        test_case = LLMTestCase(
            input=golden.input,
            actual_output=response.content[0].text
        )
        test_cases.append(test_case)
    
    # Run evaluation
    evaluate(
        test_cases=test_cases,
        metrics=metrics
    )
    print("✅ Claude-3 evaluation complete")

if __name__ == "__main__":
    print("\n📋 Running evaluations for all models...")
    print("This will create separate test runs for each model")
    
    # Run LionTax
    try:
        run_liontax_eval()
    except Exception as e:
        print(f"❌ LionTax error: {e}")
    
    # Run GPT-4
    if os.getenv("OPENAI_API_KEY"):
        try:
            run_gpt4_eval()
        except Exception as e:
            print(f"❌ GPT-4 error: {e}")
    else:
        print("⚠️ Skipping GPT-4 (no API key)")
    
    # Run Claude
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            run_claude_eval()
        except Exception as e:
            print(f"❌ Claude error: {e}")
    else:
        print("⚠️ Skipping Claude (no API key)")
    
    print("\n" + "=" * 70)
    print("✅ ALL EVALUATIONS COMPLETE!")
    print("=" * 70)
    print("\n📊 To compare models:")
    print("1. Go to https://app.confident-ai.com")
    print("2. Click 'Compare Test Results' in the sidebar")
    print("3. Select the test runs to compare:")
    print("   - LionTax (Groq Qwen)")
    print("   - GPT-4")
    print("   - Claude-3 Sonnet")
    print("\n📈 You'll see:")
    print("   - Side-by-side accuracy comparison")
    print("   - Which model performs best on each question")
    print("   - Cost vs performance analysis")