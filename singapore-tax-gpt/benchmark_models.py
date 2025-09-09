#!/usr/bin/env python
"""Benchmark LionTax against Claude, OpenAI, and other models."""

import os
from dotenv import load_dotenv
load_dotenv()

# Import model libraries
import openai
from anthropic import Anthropic
from qa_lite import answer_question

print("🏆 Multi-Model Tax Q&A Benchmark")
print("=" * 70)

# Comprehensive IRAS test questions
TEST_QUESTIONS = [
    # Basic Tax Rates & Brackets
    "What are the current personal income tax rates in Singapore?",
    "What is the current corporate tax rate in Singapore?",
    "What is the GST rate in Singapore?",
    "What is the tax-free personal income threshold?",
    "What are the income tax brackets for residents?",
    "How is tax calculated for income between $40,000 and $80,000?",
    "What is the maximum personal income tax rate?",
    "Are there different tax rates for different types of income?",
    
    # Tax Reliefs & Rebates
    "What tax reliefs are available for working mothers?",
    "How much is the earned income relief?",
    "What is the CPF relief amount?",
    "Can I claim relief for my children's education?",
    "What is the NSman relief?",
    "How much parent relief can I claim?",
    "What is the qualifying child relief amount?",
    "Are there any tax rebates for 2024?",
    "What is the foreign domestic worker levy relief?",
    "Can I claim relief for my disabled dependents?",
    
    # Filing Requirements & Deadlines
    "When is the tax filing deadline?",
    "Do I need to file taxes if my income is below $22,000?",
    "How do I file my income tax?",
    "What happens if I file late?",
    "Can I get an extension for filing?",
    "Is e-filing mandatory?",
    "What documents do I need for tax filing?",
    "When will I receive my tax bill?",
    
    # Employment Income
    "Is my bonus taxable?",
    "Are stock options taxable?",
    "How is commission income taxed?",
    "Are allowances like transport allowance taxable?",
    "Is overtime pay taxable?",
    "How are employment benefits like company car taxed?",
    "Are retrenchment benefits taxable?",
    "Is my AWS (13th month bonus) taxable?",
    
    # Investment & Rental Income
    "How is rental income taxed?",
    "Are dividends from Singapore companies taxable?",
    "How are capital gains taxed in Singapore?",
    "Is interest from bank deposits taxable?",
    "How is income from REITs taxed?",
    "Are foreign dividends taxable?",
    "How do I report cryptocurrency gains?",
    
    # Business & Trade Income
    "How is sole proprietorship income taxed?",
    "What is the difference between personal and corporate tax?",
    "Can I deduct business expenses?",
    "How is partnership income taxed?",
    "What is the partial tax exemption for companies?",
    "Are startup companies eligible for tax exemptions?",
    
    # Foreign Income & Tax Residency
    "How do I determine my tax residency status?",
    "I worked in Singapore for 6 months, am I a tax resident?",
    "How is foreign income taxed for Singapore residents?",
    "What is the 183-day rule?",
    "Do I need to pay tax on overseas income?",
    "What if I'm a tax resident of two countries?",
    "How are expatriates taxed in Singapore?",
    
    # Special Situations
    "I'm a freelancer, how do I file taxes?",
    "How are gig economy workers taxed?",
    "I'm retired, do I still need to file taxes?",
    "How is income from multiple sources taxed?",
    "What if I have no income for the year?",
    "I'm a student with part-time income, do I file taxes?",
    "How do non-residents file taxes?",
    
    # Deductions & Expenses
    "Can I deduct home office expenses?",
    "Are medical expenses deductible?",
    "Can I deduct education expenses?",
    "What donations are tax deductible?",
    "Can I deduct insurance premiums?",
    "Are professional membership fees deductible?",
    "Can I deduct mortgage interest?",
    
    # Administrative & Procedures
    "How do I register for a SingPass?",
    "How can I check my tax assessment?",
    "What payment methods are available for taxes?",
    "Can I pay tax by installments?",
    "How do I update my contact details with IRAS?",
    "How do I object to my tax assessment?",
    "What is GIRO and should I sign up?",
    
    # Penalties & Compliance
    "What is the penalty for late filing?",
    "What happens if I don't pay my taxes?",
    "Is there interest charged on late payment?",
    "What is tax evasion and its penalties?",
    "Can penalties be waived?",
    "What triggers a tax audit?",
    
    # Complex Scenarios
    "I left Singapore permanently in June, how is my tax calculated?",
    "I'm getting divorced, how does this affect my tax reliefs?",
    "I inherited property, is this taxable?",
    "I won the lottery, do I pay tax on winnings?",
    "My employer provides housing, how is this taxed?",
    "I work for multiple employers, how do I file?",
    "I receive income from YouTube/social media, is it taxable?",
    
    # GST-Related
    "Do I need to register for GST?",
    "What is the GST registration threshold?",
    "Which goods and services are GST-exempt?",
    "How do I claim GST refunds as a tourist?",
    "What is input tax and output tax?",
    
    # Property Tax
    "How is property tax calculated?",
    "What is the annual value of property?",
    "Are there property tax rebates?",
    "Is rental income related to property tax?",
    
    # Chinese Language Queries
    "新加坡的个人所得税率是多少？",
    "我需要缴税吗？",
    "什么是税务居民？",
    "如何申报所得税？",
    "税务减免有哪些？",
    
    # Edge Cases & Ambiguous Queries
    "pay tax?",
    "how much",
    "deadline",
    "help with taxes",
    "I don't understand my tax bill",
    "Is this taxable?",
    "Do I qualify?",
    "What's new in 2024 taxes?"
]

def get_liontax_response(question):
    """Get response from your LionTax system (Groq Qwen)."""
    response, _ = answer_question(question)
    return response[:500]

def get_gpt4_response(question):
    """Get response from GPT-4."""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Singapore tax expert. Answer concisely."},
            {"role": "user", "content": question}
        ],
        temperature=0,
        max_tokens=200
    )
    return response.choices[0].message.content

def get_gpt35_response(question):
    """Get response from GPT-3.5."""
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Singapore tax expert. Answer concisely."},
            {"role": "user", "content": question}
        ],
        temperature=0,
        max_tokens=200
    )
    return response.choices[0].message.content

def get_claude_response(question):
    """Get response from Claude 3."""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-3-sonnet-20241022",
        max_tokens=200,
        temperature=0,
        messages=[
            {"role": "user", "content": f"You are a Singapore tax expert. Answer this concisely: {question}"}
        ]
    )
    return response.content[0].text

def benchmark_models():
    """Run benchmark across all models."""
    
    # Check which APIs are available
    models = {"LionTax (Groq)": get_liontax_response}
    
    if os.getenv("OPENAI_API_KEY"):
        models["GPT-4"] = get_gpt4_response
        models["GPT-3.5"] = get_gpt35_response
    
    if os.getenv("ANTHROPIC_API_KEY"):
        models["Claude-3"] = get_claude_response
    
    # Results storage
    results = {model: [] for model in models}
    
    # Limit questions for initial test (can increase later)
    questions_to_test = TEST_QUESTIONS[:5]  # Test first 5 questions initially
    
    print(f"\n📊 Testing {len(questions_to_test)} questions across {len(models)} models")
    print("=" * 70)
    
    # Test each question
    for q_num, question in enumerate(questions_to_test, 1):
        print(f"\n📝 Question {q_num}/{len(questions_to_test)}: {question[:60]}...")
        print("-" * 70)
        
        for model_name, model_func in models.items():
            try:
                print(f"  Testing {model_name}...", end="")
                response = model_func(question)
                results[model_name].append({
                    "question": question,
                    "response": response
                })
                print(" ✅")
                
            except Exception as e:
                print(f" ❌ Error: {str(e)[:50]}")
                results[model_name].append({
                    "question": question,
                    "response": f"Error: {str(e)}"
                })
    
    return results

def evaluate_responses(results):
    """Evaluate and compare model responses."""
    print("\n" + "=" * 70)
    print("📊 EVALUATION RESULTS")
    print("=" * 70)
    
    # Key information expected in responses (mapped to question patterns)
    expected_keywords = {
        "personal income tax rates": ["0%", "2%", "3.5%", "7%", "11.5%", "15%", "18%", "19%", "19.5%", "20%", "22%"],
        "corporate tax rate": ["17%", "seventeen"],
        "GST rate": ["9%", "nine percent"],
        "tax-free": ["22,000", "$22,000", "22000"],
        "maximum personal": ["22%", "twenty-two"],
        "earned income relief": ["1,000", "$1,000", "1000"],
        "CPF relief": ["relief", "deduction"],
        "NSman": ["3,000", "5,000", "$3,000", "$5,000"],
        "filing deadline": ["april", "18 apr", "15 mar"],
        "bonus taxable": ["yes", "taxable"],
        "capital gains": ["no tax", "not taxable", "tax-free"],
        "183": ["resident", "tax resident"],
        "GIRO": ["automatic", "payment", "deduction"],
        "penalty": ["5%", "penalty", "fine"],
        "新加坡": ["22%", "9%", "税"],
    }
    
    model_scores = {model: [] for model in results}
    
    for model_name, responses in results.items():
        print(f"\n{model_name}:")
        
        for i, resp_data in enumerate(responses):
            question = resp_data["question"].lower()
            response = resp_data["response"].lower()
            
            # Check if response is an error
            if "error:" in response:
                print(f"  ❌ Q{i+1}: Error occurred")
                model_scores[model_name].append(0)
                continue
            
            # Find relevant keywords for this question
            found_match = False
            for keyword_group, expected_values in expected_keywords.items():
                if any(kw in question for kw in keyword_group.split()):
                    if any(val.lower() in response for val in expected_values):
                        print(f"  ✅ Q{i+1}: Contains expected information")
                        model_scores[model_name].append(1)
                        found_match = True
                        break
            
            if not found_match:
                # Check if response is substantive (not empty or too short)
                if len(response) > 20:
                    print(f"  ℹ️  Q{i+1}: Response provided")
                    model_scores[model_name].append(0.5)
                else:
                    print(f"  ⚠️  Q{i+1}: May be missing information")
                    model_scores[model_name].append(0)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📈 ACCURACY SUMMARY")
    print("=" * 70)
    
    questions_tested = len(list(results.values())[0]) if results else 0
    
    for model, scores in model_scores.items():
        if scores:
            total_score = sum(scores)
            accuracy = (total_score / len(scores)) * 100
            print(f"{model}: {total_score:.1f}/{len(scores)} ({accuracy:.0f}%)")
    
    # Performance insights
    print("\n💡 PERFORMANCE INSIGHTS:")
    print("- LionTax uses Groq Qwen for fast bilingual support")
    print("- Testing with comprehensive IRAS questions")
    print(f"- Total questions in bank: {len(TEST_QUESTIONS)}")
    print(f"- Questions tested: {questions_tested}")

if __name__ == "__main__":
    # Check API keys
    print("🔑 API Keys Status:")
    print(f"  - LionTax (Groq): ✅ Ready")
    print(f"  - OpenAI: {'✅ Found' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"  - Anthropic: {'✅ Found' if os.getenv('ANTHROPIC_API_KEY') else '❌ Missing'}")
    
    # Run benchmark
    results = benchmark_models()
    
    # Evaluate results
    evaluate_responses(results)
    
    print("\n📝 To add missing models:")
    if not os.getenv("OPENAI_API_KEY"):
        print("  1. Get OpenAI key from: https://platform.openai.com/api-keys")
        print("     Add to .env: OPENAI_API_KEY=sk-...")
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("  2. Get Anthropic key from: https://console.anthropic.com/")
        print("     Add to .env: ANTHROPIC_API_KEY=sk-ant-...")