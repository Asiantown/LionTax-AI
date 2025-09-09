#!/usr/bin/env python
"""Benchmark suite for Singapore Tax Q&A system using DeepEval."""

import os
from dotenv import load_dotenv
load_dotenv()

from deepeval import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
    HallucinationMetric,
    BiasMetric,
    ToxicityMetric
)
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset

# Import our Q&A system
from qa_lite import answer_question

# Define test questions with expected answers
test_cases = [
    # Basic rate questions
    {
        "input": "What is the GST rate in Singapore?",
        "expected": "9%",
        "category": "rates"
    },
    {
        "input": "What is the corporate tax rate?",
        "expected": "17%",
        "category": "rates"
    },
    {
        "input": "What is the highest personal income tax rate?",
        "expected": "22%",
        "category": "rates"
    },
    
    # Tax calculations
    {
        "input": "Calculate tax for $80,000 annual income",
        "expected": "$3,350",
        "category": "calculation"
    },
    {
        "input": "Calculate tax for $150,000 annual income",
        "expected": "$13,950",
        "category": "calculation"
    },
    
    # Reliefs and deductions
    {
        "input": "What is the child relief amount?",
        "expected": "$4,000 per child",
        "category": "reliefs"
    },
    {
        "input": "What is the parent relief amount?",
        "expected": "$9,000 per parent",
        "category": "reliefs"
    },
    
    # Non-resident taxation
    {
        "input": "What is the tax rate for non-residents?",
        "expected": "15% for employment income or 24% for other income",
        "category": "non-resident"
    },
    
    # Chinese questions
    {
        "input": "新加坡的GST税率是多少？",
        "expected": "9%",
        "category": "chinese"
    },
    {
        "input": "个人所得税最高税率是多少？",
        "expected": "22%",
        "category": "chinese"
    },
    
    # Complex scenarios
    {
        "input": "I worked in Singapore for 183 days. Am I a tax resident?",
        "expected": "Yes, you are a tax resident",
        "category": "residency"
    },
    {
        "input": "Can I deduct home office expenses?",
        "expected": "Yes, under certain conditions",
        "category": "deductions"
    }
]

def create_test_cases():
    """Create DeepEval test cases from our questions."""
    deepeval_cases = []
    
    for test in test_cases:
        # Get actual answer from our system
        actual_output, sources = answer_question(test["input"])
        
        # Create test case
        test_case = LLMTestCase(
            input=test["input"],
            actual_output=actual_output,
            expected_output=test["expected"],
            context=sources,
            tags=[test["category"], "singapore-tax"]
        )
        deepeval_cases.append(test_case)
    
    return deepeval_cases

def run_benchmarks():
    """Run comprehensive benchmarks on the Q&A system."""
    print("🧪 Running Singapore Tax Q&A Benchmarks")
    print("=" * 60)
    
    # Create test cases
    test_cases = create_test_cases()
    
    # Initialize metrics
    answer_relevancy = AnswerRelevancyMetric(
        threshold=0.7,
        model="gpt-4o-mini",  # Using GPT-4 mini as judge
        include_reason=True
    )
    
    faithfulness = FaithfulnessMetric(
        threshold=0.7,
        model="gpt-4o-mini",
        include_reason=True
    )
    
    hallucination = HallucinationMetric(
        threshold=0.3,  # Lower is better
        model="gpt-4o-mini",
        include_reason=True
    )
    
    bias = BiasMetric(
        threshold=0.3,  # Lower is better
        model="gpt-4o-mini",
        include_reason=True
    )
    
    # Run evaluation
    results = evaluate(
        test_cases=test_cases,
        metrics=[answer_relevancy, faithfulness, hallucination, bias],
        show_indicator=True,
        print_results=True,
        write_cache=True
    )
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 BENCHMARK RESULTS SUMMARY")
    print("=" * 60)
    
    # Calculate category-wise performance
    category_scores = {}
    for test_case in test_cases:
        category = test_case.tags[0]
        if category not in category_scores:
            category_scores[category] = []
        
        # Add score calculation here based on metrics
        
    print("\n✅ Benchmarking complete!")
    print("View detailed results at: https://app.confident-ai.com")
    
    return results

if __name__ == "__main__":
    # Set up Confident AI
    os.environ["CONFIDENT_API_KEY"] = os.getenv("CONFIDENT_API_KEY")
    
    # Run benchmarks
    results = run_benchmarks()
    
    # Print test coverage
    print("\n📋 Test Coverage:")
    print(f"- Total test cases: {len(test_cases)}")
    print(f"- Categories tested: {len(set(t['category'] for t in test_cases))}")
    print(f"- Languages: English + Chinese")
    print(f"- Metrics evaluated: Answer Relevancy, Faithfulness, Hallucination, Bias")