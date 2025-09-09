#!/usr/bin/env python
"""Test LionTax with comprehensive IRAS questions."""

import os
from dotenv import load_dotenv
load_dotenv()

from qa_lite import answer_question
import time

print("🏆 LionTax IRAS Comprehensive Test")
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
]

def test_liontax():
    """Test LionTax with IRAS questions."""
    
    # Select subset to test
    questions_to_test = TEST_QUESTIONS[:10]  # Test first 10
    
    results = []
    correct = 0
    
    print(f"\nTesting {len(questions_to_test)} questions...")
    print("-" * 70)
    
    for i, question in enumerate(questions_to_test, 1):
        print(f"\n📝 Q{i}: {question}")
        
        try:
            start = time.time()
            response, sources = answer_question(question)
            elapsed = time.time() - start
            
            # Truncate response for display
            display_response = response[:200] + "..." if len(response) > 200 else response
            print(f"✅ Response ({elapsed:.1f}s): {display_response}")
            
            # Basic validation - check if response is substantive
            if len(response) > 50:
                correct += 1
                results.append({"question": question, "response": response, "status": "success"})
            else:
                results.append({"question": question, "response": response, "status": "short"})
                
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({"question": question, "response": str(e), "status": "error"})
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Questions tested: {len(questions_to_test)}")
    print(f"Successful responses: {correct}/{len(questions_to_test)} ({correct/len(questions_to_test)*100:.0f}%)")
    
    # Check specific expected values
    print("\n🎯 Spot Checks:")
    
    # Check GST question
    gst_q = next((r for r in results if "GST rate" in r["question"]), None)
    if gst_q and "9%" in gst_q["response"]:
        print("✅ GST rate correctly identified as 9%")
    else:
        print("⚠️ GST rate may not be correct")
    
    # Check corporate tax
    corp_q = next((r for r in results if "corporate tax rate" in r["question"]), None)
    if corp_q and "17%" in corp_q["response"]:
        print("✅ Corporate tax rate correctly identified as 17%")
    else:
        print("⚠️ Corporate tax rate may not be correct")
    
    # Check personal income tax
    personal_q = next((r for r in results if "personal income tax rates" in r["question"]), None)
    if personal_q and "22%" in personal_q["response"]:
        print("✅ Maximum personal tax rate mentioned (22%)")
    else:
        print("⚠️ Personal tax rates may not be complete")
    
    print("\n💡 Next Steps:")
    print("1. To test all questions, change questions_to_test = TEST_QUESTIONS")
    print("2. To compare with other models, run benchmark_models.py")
    print("3. Results show LionTax is responding to IRAS questions")
    
    return results

if __name__ == "__main__":
    results = test_liontax()