#!/usr/bin/env python
"""Quick test to verify Q&A improvements."""

import warnings
warnings.filterwarnings('ignore')

from qa_enhanced import EnhancedTaxQA
import time

def test_critical_questions():
    """Test the critical questions that were failing."""
    
    print("🧪 Testing Enhanced Q&A System")
    print("=" * 60)
    
    qa = EnhancedTaxQA()
    
    # Critical test questions
    test_questions = [
        ("What are the current personal income tax rates for Singapore residents?",
         ["0%", "20,000", "22%", "320,000"]),
        
        ("What is the tax rate for non-residents?",
         ["22%", "flat rate"]),
        
        ("How is tax calculated for someone earning S$80,000 annually?",
         ["3,350", "4.19%"]),
        
        ("How much can I claim for spouse relief if my spouse has no income?",
         ["2,000"]),
        
        ("What is the maximum amount I can claim for child relief?",
         ["4,000"]),
    ]
    
    results = []
    
    for i, (question, expected_facts) in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        print("-" * 50)
        
        start = time.time()
        answer, sources = qa.answer_question(question)
        elapsed = time.time() - start
        
        # Check for expected facts in answer
        answer_lower = answer.lower()
        facts_found = []
        facts_missing = []
        
        for fact in expected_facts:
            if fact.replace(",", "") in answer_lower.replace(",", ""):
                facts_found.append(fact)
            else:
                facts_missing.append(fact)
        
        accuracy = len(facts_found) / len(expected_facts) if expected_facts else 0
        
        # Check if answer is evasive
        is_evasive = any(phrase in answer_lower for phrase in [
            "context does not specify",
            "not available",
            "cannot provide"
        ])
        
        # Print results
        print(f"✅ Facts found: {facts_found}")
        if facts_missing:
            print(f"❌ Facts missing: {facts_missing}")
        
        print(f"📊 Accuracy: {accuracy:.0%}")
        print(f"⏱️ Response time: {elapsed:.2f}s")
        print(f"🎯 Evasive: {'Yes ⚠️' if is_evasive else 'No ✅'}")
        
        # Show snippet of answer
        print(f"\n📝 Answer snippet:")
        lines = answer.split('\n')
        for line in lines[:5]:
            if line.strip():
                print(f"   {line[:100]}")
        
        results.append({
            "question": question[:50],
            "accuracy": accuracy,
            "evasive": is_evasive,
            "time": elapsed
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    avg_accuracy = sum(r["accuracy"] for r in results) / len(results)
    perfect = sum(1 for r in results if r["accuracy"] == 1.0)
    evasive = sum(1 for r in results if r["evasive"])
    avg_time = sum(r["time"] for r in results) / len(results)
    
    print(f"✅ Average Accuracy: {avg_accuracy:.0%}")
    print(f"🎯 Perfect Answers: {perfect}/{len(results)}")
    print(f"⚠️ Evasive Answers: {evasive}/{len(results)}")
    print(f"⏱️ Avg Response Time: {avg_time:.2f}s")
    
    if avg_accuracy >= 0.8 and evasive == 0:
        print("\n🎉 SUCCESS: Q&A system is providing accurate, specific answers!")
    elif avg_accuracy >= 0.6:
        print("\n⚠️ PARTIAL SUCCESS: Q&A system is improved but needs more work.")
    else:
        print("\n❌ NEEDS WORK: Q&A system still has significant issues.")
    
    return avg_accuracy >= 0.8 and evasive == 0


if __name__ == "__main__":
    success = test_critical_questions()
    exit(0 if success else 1)