#!/usr/bin/env python
"""End-to-End Testing for LionTax using DeepEval following official docs."""

import os
from dotenv import load_dotenv
load_dotenv()

# Set API keys
os.environ["CONFIDENT_API_KEY"] = "confident_us_FDfVbEnV7U0mP+ywkdeKj6Uhtic2VeNoVaO7dgqQTLY="
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "sk-dummy")

from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, GEval, FaithfulnessMetric
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset, Golden
from qa_lite import answer_question
import openai
from anthropic import Anthropic

print("🏆 Singapore Tax End-to-End Testing with DeepEval")
print("=" * 70)

# Create dataset with IRAS questions and expected outputs
def create_iras_dataset():
    """Create dataset with IRAS test questions and goldens."""
    dataset = EvaluationDataset()
    
    # Add comprehensive IRAS questions with expected outputs
    test_data = [
        {
            "input": "What is the GST rate in Singapore?",
            "expected_output": "The GST rate in Singapore is 9% as of 2024.",
            "tags": ["rates", "gst"]
        },
        {
            "input": "What is the current corporate tax rate in Singapore?",
            "expected_output": "The corporate tax rate in Singapore is 17%.",
            "tags": ["rates", "corporate"]
        },
        {
            "input": "What is the tax-free personal income threshold?",
            "expected_output": "The first $20,000 of chargeable income is tax-free for residents.",
            "tags": ["rates", "personal"]
        },
        {
            "input": "What is the maximum personal income tax rate?",
            "expected_output": "The maximum personal income tax rate in Singapore is 22% for income above $320,000.",
            "tags": ["rates", "personal"]
        },
        {
            "input": "How much is the earned income relief?",
            "expected_output": "The earned income relief is $1,000 for those below 55 years old.",
            "tags": ["reliefs", "earned-income"]
        },
        {
            "input": "When is the tax filing deadline?",
            "expected_output": "The tax filing deadline is 15 March for paper filing and 18 April for e-filing.",
            "tags": ["filing", "deadline"]
        },
        {
            "input": "Is my bonus taxable?",
            "expected_output": "Yes, bonuses including AWS are taxable as employment income.",
            "tags": ["employment", "bonus"]
        },
        {
            "input": "Are capital gains taxed in Singapore?",
            "expected_output": "Singapore does not tax capital gains.",
            "tags": ["investment", "capital-gains"]
        },
        {
            "input": "What is the 183-day rule?",
            "expected_output": "If you stay in Singapore for 183 days or more in a year, you qualify as a tax resident.",
            "tags": ["residency", "183-days"]
        },
        {
            "input": "新加坡的个人所得税率是多少？",
            "expected_output": "新加坡个人所得税率从0%到22%不等，最高税率为22%。",
            "tags": ["chinese", "rates"]
        }
    ]
    
    # Add goldens to dataset
    for item in test_data:
        golden = Golden(
            input=item["input"],
            expected_output=item["expected_output"],
            tags=item["tags"]
        )
        dataset.add_golden(golden)
    
    return dataset

def get_liontax_response(question):
    """Get response from LionTax (Groq Qwen)."""
    response, sources = answer_question(question)
    return response, sources

def get_gpt4_response(question):
    """Get response from GPT-4."""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Singapore tax expert. Answer concisely and accurately."},
                {"role": "user", "content": question}
            ],
            temperature=0,
            max_tokens=300
        )
        return response.choices[0].message.content, []
    except:
        return "GPT-4 not available", []

def get_claude_response(question):
    """Get response from Claude."""
    try:
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-3-sonnet-20241022",
            max_tokens=300,
            temperature=0,
            messages=[
                {"role": "user", "content": f"You are a Singapore tax expert. Answer this concisely and accurately: {question}"}
            ]
        )
        return response.content[0].text, []
    except:
        return "Claude not available", []

def run_e2e_testing():
    """Run end-to-end testing following DeepEval docs."""
    
    # Step 1: Create dataset with goldens
    print("\n📊 Step 1: Creating dataset with goldens...")
    dataset = create_iras_dataset()
    print(f"✅ Created dataset with {len(dataset.goldens)} test questions")
    
    # Step 2: Define metrics
    print("\n📏 Step 2: Defining evaluation metrics...")
    
    # Answer relevancy metric
    relevancy_metric = AnswerRelevancyMetric(
        threshold=0.7,
        model="gpt-3.5-turbo",
        include_reason=True
    )
    
    # Correctness metric using G-Eval
    correctness_metric = GEval(
        name="Correctness",
        criteria="Determine if the actual output is factually correct and matches Singapore tax laws. The output should contain accurate tax rates, thresholds, and regulations.",
        evaluation_params=["input", "actual_output", "expected_output"],
        threshold=0.7,
        model="gpt-3.5-turbo"
    )
    
    # Faithfulness metric (if retrieval context available)
    faithfulness_metric = FaithfulnessMetric(
        threshold=0.7,
        model="gpt-3.5-turbo",
        include_reason=True
    )
    
    metrics = [relevancy_metric, correctness_metric]
    
    print("✅ Defined 2 evaluation metrics")
    
    # Step 3: Test multiple models
    models = {
        "LionTax": get_liontax_response,
        "GPT-4": get_gpt4_response,
        "Claude-3": get_claude_response
    }
    
    results_by_model = {}
    
    for model_name, model_func in models.items():
        print(f"\n🤖 Step 3: Testing {model_name}...")
        
        # Create test cases for this model
        test_cases = []
        
        for golden in dataset.goldens:
            print(f"  Testing: {golden.input[:50]}...", end="")
            
            try:
                # Get actual output from model
                actual_output, retrieval_context = model_func(golden.input)
                
                # Create test case
                test_case = LLMTestCase(
                    input=golden.input,
                    actual_output=actual_output,
                    expected_output=golden.expected_output,
                    retrieval_context=retrieval_context if retrieval_context else None,
                    tags=golden.tags + [model_name]
                )
                test_cases.append(test_case)
                dataset.add_test_case(test_case)
                print(" ✅")
                
            except Exception as e:
                print(f" ❌ Error: {e}")
                # Create test case with error
                test_case = LLMTestCase(
                    input=golden.input,
                    actual_output=f"Error: {str(e)}",
                    expected_output=golden.expected_output,
                    tags=golden.tags + [model_name, "error"]
                )
                test_cases.append(test_case)
        
        # Store test cases for this model
        results_by_model[model_name] = test_cases
        
        print(f"  Created {len(test_cases)} test cases for {model_name}")
    
    # Step 4: Run evaluation
    print("\n🎯 Step 4: Running evaluation...")
    
    # Evaluate all test cases
    results = evaluate(
        test_cases=dataset.test_cases,
        metrics=metrics,
        print_results=True,
        show_indicator=True,
        run_name=f"Singapore Tax E2E Testing",
        hyperparameters={
            "models_tested": list(models.keys()),
            "dataset_size": len(dataset.goldens),
            "framework": "deepeval",
            "test_type": "end-to-end"
        }
    )
    
    print("\n" + "=" * 70)
    print("✅ E2E Testing Complete!")
    print("=" * 70)
    print("\n📊 Results Summary:")
    print(f"- Total test cases: {len(dataset.test_cases)}")
    print(f"- Models tested: {', '.join(models.keys())}")
    print(f"- Metrics used: Answer Relevancy, Correctness")
    print("\n📈 View detailed results at: https://app.confident-ai.com")
    
    # Optional: Save dataset for future use
    try:
        dataset.push(alias="singapore-tax-e2e")
        print("\n💾 Dataset saved to Confident AI as 'singapore-tax-e2e'")
    except:
        print("\n⚠️ Could not save dataset to Confident AI")
    
    return results

if __name__ == "__main__":
    # Check API keys
    print("\n🔑 API Keys Status:")
    print(f"  - Confident AI: ✅ Set")
    print(f"  - OpenAI: {'✅ Found' if os.getenv('OPENAI_API_KEY') and 'sk-proj' in os.getenv('OPENAI_API_KEY') else '⚠️ Not set'}")
    print(f"  - Anthropic: {'✅ Found' if os.getenv('ANTHROPIC_API_KEY') else '⚠️ Not set'}")
    
    # Run e2e testing
    results = run_e2e_testing()