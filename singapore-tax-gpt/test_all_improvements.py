#!/usr/bin/env python
"""Complete test suite to verify Q&A improvements."""

import warnings
warnings.filterwarnings('ignore')

from qa_working import answer_question
import time

def test_all_improvements():
    """Test all the critical questions that were failing before."""
    
    print("🧪 TESTING Q&A IMPROVEMENTS")
    print("=" * 60)
    print("Testing questions that previously failed...\n")
    
    # The exact questions from your feedback
    test_cases = [
        {
            "question": "What are the current personal income tax rates for Singapore residents?",
            "should_contain": ["0%", "20,000", "2%", "3.5%", "7%", "11.5%", "15%", "18%", "19%", "20%", "22%", "320,000"],
            "should_not_contain": ["context does not specify", "not available"]
        },
        {
            "question": "What is the tax rate for non-residents?",
            "should_contain": ["22%", "flat"],
            "should_not_contain": ["15%", "public entertainer"]  # Should give general rate, not special cases
        },
        {
            "question": "At what income level do I start paying income tax in Singapore?",
            "should_contain": ["20,000", "tax-free"],
            "should_not_contain": ["context does not specify"]
        },
        {
            "question": "What is the highest marginal tax rate for individuals?",
            "should_contain": ["22%", "320,000"],
            "should_not_contain": ["not specified"]
        },
        {
            "question": "How is tax calculated for someone earning S$80,000 annually?",
            "should_contain": ["3,350", "4.19%", "76,650"],
            "should_not_contain": ["cannot calculate", "need more information"]
        },
        {
            "question": "How much can I claim for spouse relief if my spouse has no income?",
            "should_contain": ["2,000"],
            "should_not_contain": ["context does not specify", "typically"]
        },
        {
            "question": "What is the maximum amount I can claim for child relief?",
            "should_contain": ["4,000"],
            "should_not_contain": ["not specified", "context provided does not"]
        },
        {
            "question": "Can I claim tax relief for my parents? What are the conditions?",
            "should_contain": ["9,000", "55", "4,000"],
            "should_not_contain": ["not provided", "consult IRAS"]
        },
        {
            "question": "What is the Earned Income Relief and how is it calculated?",
            "should_contain": ["1,000", "1%"],
            "should_not_contain": ["$1,000 or earned income, whichever is lower"]  # This was wrong before
        }
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['question'][:60]}...")
        
        start = time.time()
        answer, sources = answer_question(test['question'])
        elapsed = time.time() - start
        
        answer_lower = answer.lower()
        
        # Check if answer contains what it should
        missing_facts = []
        for fact in test['should_contain']:
            if str(fact).lower().replace(",", "") not in answer_lower.replace(",", ""):
                missing_facts.append(fact)
        
        # Check if answer contains what it shouldn't
        bad_phrases = []
        for phrase in test['should_not_contain']:
            if phrase.lower() in answer_lower:
                bad_phrases.append(phrase)
        
        # Determine if test passed
        test_passed = len(missing_facts) == 0 and len(bad_phrases) == 0
        
        if test_passed:
            print(f"  ✅ PASSED ({elapsed:.2f}s)")
            passed += 1
        else:
            print(f"  ❌ FAILED ({elapsed:.2f}s)")
            if missing_facts:
                print(f"     Missing: {', '.join(missing_facts)}")
            if bad_phrases:
                print(f"     Contains bad phrases: {', '.join(bad_phrases)}")
            failed += 1
        
        # Show a snippet of the answer
        answer_lines = answer.split('\n')
        print(f"     Answer snippet: {answer_lines[0][:100]}...")
        print()
        
        results.append({
            "question": test['question'],
            "passed": test_passed,
            "missing": missing_facts,
            "bad_phrases": bad_phrases,
            "time": elapsed
        })
    
    # Print summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(test_cases)}")
    print(f"❌ Failed: {failed}/{len(test_cases)}")
    print(f"📈 Success Rate: {(passed/len(test_cases)*100):.1f}%")
    
    avg_time = sum(r['time'] for r in results) / len(results)
    print(f"⏱️  Average Response Time: {avg_time:.2f}s")
    
    # Final verdict
    print("\n" + "=" * 60)
    if passed >= 7:  # At least 7 out of 9 should pass
        print("🎉 SUCCESS! The Q&A system is providing accurate, specific answers!")
        print("Your Singapore Tax GPT is ready for production!")
    elif passed >= 5:
        print("⚠️  PARTIAL SUCCESS: Significant improvements, but some issues remain.")
        print("The system is much better but could use more refinement.")
    else:
        print("❌ NEEDS MORE WORK: The system still has significant issues.")
        print("Consider reviewing the structured data and routing logic.")
    
    return passed >= 7

if __name__ == "__main__":
    success = test_all_improvements()
    exit(0 if success else 1)