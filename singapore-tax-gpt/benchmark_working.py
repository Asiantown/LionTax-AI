#!/usr/bin/env python
"""WORKING benchmark script that will actually create test runs on Confident AI."""

import os
from dotenv import load_dotenv
load_dotenv()

# Set API keys - USING YOUR PROVIDED KEYS
os.environ["CONFIDENT_API_KEY"] = os.getenv("CONFIDENT_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY")

print("🏆 Singapore Tax Benchmarking - WORKING VERSION")
print("=" * 70)

from deepeval.dataset import EvaluationDataset
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval import evaluate
from qa_lite import answer_question
import openai
from anthropic import Anthropic

# Create curated list of 20 diverse questions
print("\n📊 Creating curated test dataset...")
from deepeval.dataset import Golden

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

# Create dataset with curated questions
dataset = EvaluationDataset()
for q in curated_questions:
    dataset.goldens.append(Golden(input=q))

print(f"📝 Testing with {len(dataset.goldens)} curated questions from all sectors")

# Simple metric (just relevancy to avoid complex errors)
print("\n📏 Setting up simple metric...")
metric = AnswerRelevancyMetric(
    threshold=0.5,
    model="gpt-3.5-turbo"
)

def test_liontax():
    """Test LionTax - SIMPLIFIED."""
    print("\n🤖 Testing LionTax (Groq Qwen)...")
    test_cases = []
    
    for i, golden in enumerate(dataset.goldens, 1):
        print(f"  Processing {i}/{len(dataset.goldens)}: {golden.input[:40]}...")
        
        # Get response
        actual_output, _ = answer_question(golden.input)
        
        # Create SIMPLE test case - no retrieval context
        test_case = LLMTestCase(
            input=golden.input,
            actual_output=actual_output
        )
        test_cases.append(test_case)
    
    print(f"✅ Created {len(test_cases)} test cases")
    
    # Run evaluation with hyperparameters to identify model
    print("\n📤 Uploading to Confident AI as 'LionTax'...")
    try:
        results = evaluate(
            test_cases=test_cases,
            metrics=[metric],
            hyperparameters={"model": "LionTax", "provider": "Groq", "llm": "Qwen3-32B"}
        )
        print("✅ LionTax evaluation complete!")
        print("🌐 Check https://app.confident-ai.com for results")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_gpt4():
    """Test GPT-4 - SIMPLIFIED."""
    print("\n🤖 Testing GPT-4...")
    client = openai.OpenAI()
    test_cases = []
    
    for i, golden in enumerate(dataset.goldens, 1):
        print(f"  Processing {i}/{len(dataset.goldens)}: {golden.input[:40]}...")
        
        # Get GPT-4 response
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Singapore tax expert."},
                {"role": "user", "content": golden.input}
            ],
            temperature=0,
            max_tokens=300
        )
        
        # Create SIMPLE test case
        test_case = LLMTestCase(
            input=golden.input,
            actual_output=response.choices[0].message.content
        )
        test_cases.append(test_case)
    
    print(f"✅ Created {len(test_cases)} test cases")
    
    # Run evaluation with hyperparameters to identify model
    print("\n📤 Uploading to Confident AI as 'GPT-4'...")
    try:
        results = evaluate(
            test_cases=test_cases,
            metrics=[metric],
            hyperparameters={"model": "GPT-4", "provider": "OpenAI", "version": "gpt-4"}
        )
        print("✅ GPT-4 evaluation complete!")
        print("🌐 Check https://app.confident-ai.com for results")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Main execution
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀 STARTING EVALUATIONS")
    print("=" * 70)
    
    success_count = 0
    
    # Test LionTax
    if test_liontax():
        success_count += 1
    
    # Test GPT-4 - YOU PROVIDED THE KEY
    if test_gpt4():
        success_count += 1
    
    # Test Claude if funds available
    # Note: Your Anthropic account is out of credits
    # if test_claude():
    #     success_count += 1
    
    print("\n" + "=" * 70)
    print(f"✅ COMPLETE! Created {success_count} test runs")
    print("=" * 70)
    
    if success_count > 0:
        print("\n🎉 SUCCESS! Your test runs are on Confident AI")
        print("\n📊 TO VIEW RESULTS:")
        print("1. Go to: https://app.confident-ai.com")
        print("2. You should see new test runs in the dashboard")
        print("3. Click on a test run to see details")
        print("\n📈 TO COMPARE MODELS:")
        print("1. Click 'Compare Test Results' in sidebar")
        print("2. Select multiple test runs")
        print("3. View side-by-side comparison")
    else:
        print("\n❌ No test runs created - check errors above")