#!/usr/bin/env python
"""Test improved responses."""

from qa_lite import answer_question

# Test the specific question that was failing
test_questions = [
    "What are the limits for course fee relief claims?",
    "What is the GST rate in Singapore?",
    "Can I claim tax relief for my parents? What are the conditions?",
]

print("🧪 Testing Improved Responses")
print("=" * 60)

for q in test_questions:
    print(f"\n❓ Question: {q}")
    answer, _ = answer_question(q)
    word_count = len(answer.split())
    
    print(f"📝 Answer: {answer}")
    print(f"📊 Length: {word_count} words")
    print("-" * 60)