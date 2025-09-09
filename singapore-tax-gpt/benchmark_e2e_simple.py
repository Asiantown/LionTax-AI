#!/usr/bin/env python
"""Simple E2E Testing for LionTax following DeepEval docs."""

import os
from dotenv import load_dotenv
load_dotenv()

# Set API keys
os.environ["CONFIDENT_API_KEY"] = "confident_us_FDfVbEnV7U0mP+ywkdeKj6Uhtic2VeNoVaO7dgqQTLY="

from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, GEval
from deepeval.test_case import LLMTestCase
from qa_lite import answer_question

print("🏆 Singapore Tax E2E Testing - Simple Version")
print("=" * 70)

# IRAS test questions with expected answers
test_questions = [
    # Add ALL your comprehensive questions here
    {"input": "What is the GST rate in Singapore?", "expected": "9%"},
    {"input": "What is the current corporate tax rate?", "expected": "17%"},
    {"input": "What is the maximum personal income tax rate?", "expected": "22%"},
    {"input": "What is the tax-free threshold for personal income?", "expected": "$20,000"},
    {"input": "When is the tax filing deadline?", "expected": "15 March or 18 April"},
    {"input": "What are the income tax brackets for residents?", "expected": "0% to 22%"},
    {"input": "How much is the earned income relief?", "expected": "$1,000"},
    {"input": "What is the NSman relief?", "expected": "$3,000 to $5,000"},
    {"input": "Is my bonus taxable?", "expected": "Yes"},
    {"input": "Are capital gains taxed in Singapore?", "expected": "No"},
    # Add more questions as needed - I'm keeping it to 10 for quick testing
]

def run_simple_e2e():
    """Run simple end-to-end testing."""
    
    print("\n📊 Creating test cases...")
    test_cases = []
    
    # Loop through questions and create test cases
    for i, test_data in enumerate(test_questions, 1):
        print(f"\n{i}. Testing: {test_data['input']}")
        
        # Get actual output from LionTax
        try:
            actual_output, sources = answer_question(test_data["input"])
            print(f"   ✅ Got response: {actual_output[:100]}...")
            
            # Create test case
            test_case = LLMTestCase(
                input=test_data["input"],
                actual_output=actual_output,
                expected_output=test_data["expected"],
                retrieval_context=sources if sources else None
            )
            test_cases.append(test_case)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            test_case = LLMTestCase(
                input=test_data["input"],
                actual_output=f"Error: {str(e)}",
                expected_output=test_data["expected"]
            )
            test_cases.append(test_case)
    
    print(f"\n✅ Created {len(test_cases)} test cases")
    
    # Define metrics
    print("\n📏 Defining metrics...")
    
    relevancy_metric = AnswerRelevancyMetric(
        threshold=0.5,
        model="gpt-3.5-turbo"
    )
    
    correctness_metric = GEval(
        name="Tax Accuracy",
        criteria="Check if the actual output contains the correct Singapore tax information matching the expected output",
        evaluation_params=["input", "actual_output", "expected_output"],
        threshold=0.6,
        model="gpt-3.5-turbo"
    )
    
    metrics = [relevancy_metric, correctness_metric]
    
    # Run evaluation
    print("\n🎯 Running evaluation...")
    
    try:
        results = evaluate(
            test_cases=test_cases,
            metrics=metrics
        )
        
        print("\n" + "=" * 70)
        print("✅ Evaluation Complete!")
        print("View results at: https://app.confident-ai.com")
        
    except Exception as e:
        print(f"\n⚠️ Evaluation error: {e}")
        print("But test cases were created successfully!")
    
    return test_cases

if __name__ == "__main__":
    test_cases = run_simple_e2e()
    
    print("\n📋 Summary:")
    print(f"- Questions tested: {len(test_cases)}")
    print("- Model: LionTax (Groq Qwen)")
    print("- Metrics: Answer Relevancy, Tax Accuracy")