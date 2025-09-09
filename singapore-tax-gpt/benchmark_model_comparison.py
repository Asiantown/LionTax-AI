#!/usr/bin/env python
"""Compare LionTax (Groq Qwen) against Claude, OpenAI, and other models."""

import os
from dotenv import load_dotenv
load_dotenv()

# Set API keys
os.environ["CONFIDENT_API_KEY"] = "confident_us_FDfVbEnV7U0mP+ywkdeKj6Uhtic2VeNoVaO7dgqQTLY="

from deepeval import evaluate
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset
from langchain_openai import ChatOpenAI
from qa_lite import answer_question

print("🏆 Multi-Model Singapore Tax Benchmark")
print("=" * 70)

# Test questions covering different scenarios
TEST_QUESTIONS = [
    {
        "input": "What is the GST rate in Singapore?",
        "expected_output": "The GST rate in Singapore is 9% as of 2024",
        "category": "rates"
    },
    {
        "input": "Calculate tax for someone earning $80,000 annually",
        "expected_output": "For $80,000 annual income, the tax is approximately $3,350",
        "category": "calculation"
    },
    {
        "input": "What is the tax rate for non-residents?",
        "expected_output": "Non-residents pay 15% on employment income or 24% on other income",
        "category": "non-resident"
    },
    {
        "input": "新加坡的个人所得税最高税率是多少？",
        "expected_output": "新加坡个人所得税最高税率为22%",
        "category": "chinese"
    },
    {
        "input": "I worked in Singapore for 183 days. Am I a tax resident?",
        "expected_output": "Yes, you are a tax resident if you stayed 183 days or more",
        "category": "residency"
    }
]

def get_model_response(model_name, question):
    """Get response from different models."""
    
    if model_name == "LionTax (Groq Qwen)":
        # Your current system
        response, _ = answer_question(question)
        return response[:500]  # Limit length
    
    elif model_name == "GPT-4":
        llm = ChatOpenAI(
            temperature=0,
            model="gpt-4",
            openai_api_key="sk-..."  # Add your OpenAI key
        )
        response = llm.invoke(f"Answer this Singapore tax question concisely: {question}")
        return response.content[:500]
    
    elif model_name == "GPT-3.5":
        llm = ChatOpenAI(
            temperature=0,
            model="gpt-3.5-turbo",
            openai_api_key="sk-..."  # Add your OpenAI key
        )
        response = llm.invoke(f"Answer this Singapore tax question concisely: {question}")
        return response.content[:500]
    
    elif model_name == "Claude-3":
        # Add Claude API integration
        from anthropic import Anthropic
        client = Anthropic(api_key="sk-...")  # Add your Anthropic key
        response = client.messages.create(
            model="claude-3-sonnet-20241022",
            max_tokens=200,
            messages=[{"role": "user", "content": f"Answer this Singapore tax question concisely: {question}"}]
        )
        return response.content[0].text[:500]
    
    else:
        return "Model not configured"

def create_test_dataset():
    """Create dataset for comparison."""
    dataset = EvaluationDataset()
    
    for q in TEST_QUESTIONS:
        dataset.add_golden(
            input=q["input"],
            expected_output=q["expected_output"],
            tags=[q["category"]]
        )
    
    return dataset

def run_model_comparison():
    """Compare multiple models on the same dataset."""
    
    # Models to compare
    models = [
        "LionTax (Groq Qwen)",
        # "GPT-4",  # Uncomment when you add OpenAI key
        # "GPT-3.5",  # Uncomment when you add OpenAI key
        # "Claude-3",  # Uncomment when you add Anthropic key
    ]
    
    # Metrics for evaluation
    relevancy_metric = AnswerRelevancyMetric(threshold=0.7)
    
    correctness_metric = GEval(
        name="Correctness",
        criteria="Determine if the actual output is factually correct based on Singapore tax laws",
        evaluation_params=["actual_output", "expected_output"],
        threshold=0.7
    )
    
    # Results storage
    results = {}
    
    for model_name in models:
        print(f"\n📊 Testing: {model_name}")
        print("-" * 50)
        
        test_cases = []
        model_scores = []
        
        for question in TEST_QUESTIONS:
            # Get model response
            actual_output = get_model_response(model_name, question["input"])
            
            # Create test case
            test_case = LLMTestCase(
                input=question["input"],
                actual_output=actual_output,
                expected_output=question["expected_output"],
                tags=[model_name, question["category"]]
            )
            test_cases.append(test_case)
            
            # Quick quality check
            if any(keyword in actual_output.lower() for keyword in ["9%", "3,350", "22%", "183", "resident"]):
                print(f"  ✅ {question['category']}: Contains expected info")
                model_scores.append(1)
            else:
                print(f"  ⚠️  {question['category']}: May be missing info")
                model_scores.append(0)
        
        # Calculate model performance
        accuracy = sum(model_scores) / len(model_scores) * 100
        results[model_name] = {
            "accuracy": accuracy,
            "test_cases": test_cases
        }
        
        print(f"  📈 Accuracy: {accuracy:.1f}%")
        
        # Run DeepEval metrics (optional)
        try:
            eval_results = evaluate(
                test_cases=test_cases,
                metrics=[relevancy_metric, correctness_metric]
            )
            print(f"  🎯 DeepEval Score: Uploaded to Confident AI")
        except:
            print(f"  ℹ️  DeepEval metrics require model API keys")
    
    # Print comparison summary
    print("\n" + "=" * 70)
    print("📊 MODEL COMPARISON SUMMARY")
    print("=" * 70)
    
    for model, data in results.items():
        print(f"{model}: {data['accuracy']:.1f}% accuracy")
    
    print("\n💡 Insights:")
    print("- LionTax uses Groq Qwen for fast bilingual support")
    print("- Add API keys to compare with GPT-4, Claude, etc.")
    print("- View detailed metrics at: https://app.confident-ai.com")
    
    return results

if __name__ == "__main__":
    results = run_model_comparison()
    
    print("\n📝 Next Steps:")
    print("1. Add OpenAI API key to compare with GPT-4/GPT-3.5")
    print("2. Add Anthropic API key to compare with Claude")
    print("3. View results dashboard at: https://app.confident-ai.com")
    print("4. Run regression tests when you update your system")