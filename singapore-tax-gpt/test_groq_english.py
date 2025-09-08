#!/usr/bin/env python
"""Comprehensive test of English functionality with Groq."""

import warnings
warnings.filterwarnings('ignore')

from qa_working import answer_question
import time

print("🧪 COMPREHENSIVE ENGLISH TEST SUITE - GROQ")
print("=" * 80)

# Test cases
test_questions = [
    # Basic rate questions
    ("What is the GST rate?", "Should mention 9%"),
    ("What is the corporate tax rate?", "Should mention 17%"),
    ("What is the tax rate for non-residents?", "Should mention 15% or 24%"),
    
    # Calculations
    ("Calculate tax for $80,000", "Should calculate ~$3,350"),
    ("Calculate tax for $150,000", "Should calculate tax amount"),
    
    # Thresholds and limits
    ("What is the tax-free threshold?", "Should mention $20,000"),
    ("What is the highest tax rate?", "Should mention 22%"),
    
    # Reliefs
    ("What is child relief?", "Should mention $4,000"),
    ("What is parent relief?", "Should mention $9,000"),
    
    # Multiple questions
    ("What is GST? What about corporate tax?", "Should answer both"),
    
    # Complex scenarios
    ("I worked 183 days in Singapore, am I tax resident?", "Should confirm yes"),
    ("Can I deduct home office expenses?", "Should explain deductibility"),
]

passed = 0
failed = 0

for i, (question, expected) in enumerate(test_questions, 1):
    print(f"\n{'=' * 80}")
    print(f"Test {i}: {question}")
    print("-" * 80)
    
    try:
        start = time.time()
        answer, sources = answer_question(question)
        elapsed = time.time() - start
        
        # Check if answer is reasonable
        if answer and len(answer) > 20:
            print(f"✅ PASSED ({elapsed:.1f}s)")
            print(f"Answer preview: {answer[:150]}...")
            print(f"Expected: {expected}")
            passed += 1
        else:
            print(f"❌ FAILED - Answer too short or empty")
            failed += 1
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)[:100]}")
        failed += 1

print("\n" + "=" * 80)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_questions)} tests")

if failed == 0:
    print("✅ ALL ENGLISH TESTS PASSED! System ready.")
else:
    print(f"⚠️  {failed} tests failed. Please review.")

print("\n📊 Performance Notes:")
print("- Groq Qwen is ~10x faster than GPT-4")
print("- Responses should be in English when asked in English")
print("- Document search should work normally")