#!/usr/bin/env python
"""Test multiple questions handling."""

import warnings
warnings.filterwarnings('ignore')

from qa_working import answer_question

print("🧪 MULTIPLE QUESTIONS TEST SUITE")
print("=" * 60)

# Test 1: Multiple questions on separate lines
test1 = """What are the current personal income tax rates for Singapore residents?
What is the tax rate for non-residents?
At what income level do I start paying income tax in Singapore?
What is the highest marginal tax rate for individuals?
How is tax calculated for someone earning S$80,000 annually?"""

print("\nTEST 1: Five Questions (newline separated)")
print("-" * 40)
answer, _ = answer_question(test1)
lines = answer.split('\n')
print(f"✅ Answered {answer.count('Question ')} questions")
print(f"✅ Total lines in response: {len(lines)}")

# Verify each question was answered
assert "Question 1:" in answer, "Missing Q1"
assert "Question 2:" in answer, "Missing Q2"
assert "Question 3:" in answer, "Missing Q3"
assert "Question 4:" in answer, "Missing Q4"
assert "Question 5:" in answer, "Missing Q5"
assert "$0 - $20,000: 0%" in answer, "Missing tax rates"
assert "15% flat rate" in answer, "Missing non-resident rate"
assert "$20,000" in answer and "tax-free" in answer, "Missing threshold"
assert "22%" in answer and "$320,000" in answer, "Missing highest rate"
assert "$3,350" in answer, "Missing $80k calculation"
print("✅ All questions answered correctly!")

# Test 2: Multiple questions with ? marks
test2 = "What is the GST rate? What about corporate tax? When is the filing deadline?"

print("\n\nTEST 2: Three Questions (? separated)")
print("-" * 40)
answer, _ = answer_question(test2)
print(f"✅ Answered {answer.count('Question ')} questions")

assert "9%" in answer, "Missing GST rate"
assert "17%" in answer, "Missing corporate tax rate"
assert "18 April" in answer or "filing" in answer.lower(), "Missing deadline"
print("✅ All questions answered correctly!")

# Test 3: Single question (should work as before)
test3 = "What is the tax rate for non-residents?"

print("\n\nTEST 3: Single Question")
print("-" * 40)
answer, _ = answer_question(test3)

# Should NOT have "Question 1:" for single questions
assert "Question 1:" not in answer, "Single question shouldn't be numbered"
assert "15%" in answer and "24%" in answer, "Missing non-resident rates"
print("✅ Single question handled correctly!")

# Test 4: Edge case - question with numbers but not multiple
test4 = "If I earn $125,000 in 2024, what is my tax?"

print("\n\nTEST 4: Single Question with Numbers")
print("-" * 40)
answer, _ = answer_question(test4)

assert "Question 1:" not in answer, "Shouldn't split on numbers alone"
assert "tax" in answer.lower() and "$" in answer, "Should provide tax amount"
print("✅ Numbers don't trigger multi-question mode!")

print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED!")
print("\nThe system now correctly:")
print("✅ Detects multiple questions (by ? or newlines)")
print("✅ Answers each question individually")
print("✅ Formats with clear separation")
print("✅ Still handles single questions normally")
print("✅ Doesn't get confused by numbers in text")