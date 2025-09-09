#!/usr/bin/env python
"""Test response lengths for various questions."""

from qa_lite import answer_question

test_questions = [
    "What is the GST rate in Singapore?",
    "What is the tax rate for non-residents?",
    "When is the deadline for filing my tax return?",
    "Is my 13th month bonus taxable?",
    "How do I determine if I'm a Singapore tax resident?",
    "What are the limits for course fee relief claims?",
    "Can I claim tax relief for my parents? What are the conditions?",
    "How is income from cryptocurrency trading taxed?",
]

print("🧪 Testing Response Lengths")
print("=" * 60)

for q in test_questions:
    print(f"\n❓ Q: {q}")
    answer, _ = answer_question(q)
    word_count = len(answer.split())
    
    print(f"📝 A: {answer}")
    print(f"📊 Length: {word_count} words")
    
    # Check if reasonable length
    if word_count <= 50:
        print("✅ Good length")
    elif word_count <= 100:
        print("⚠️ Bit long but acceptable")
    else:
        print("❌ Too long!")
    print("-" * 60)