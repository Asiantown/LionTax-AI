#!/usr/bin/env python
"""Test if LionTax responses are now concise like GPT-4."""

from qa_lite import answer_question

test_questions = [
    "What is the GST rate in Singapore?",
    "What is the tax rate for non-residents?",
    "新加坡的个人所得税最高是多少？",
    "Is my bonus taxable?",
    "tax"
]

print("🧪 Testing Concise Responses")
print("=" * 60)

for q in test_questions:
    print(f"\n❓ Question: {q}")
    answer, _ = answer_question(q)
    word_count = len(answer.split())
    char_count = len(answer)
    
    print(f"📝 Answer: {answer}")
    print(f"📊 Length: {word_count} words, {char_count} chars")
    
    # Check if it's concise enough
    if word_count <= 100:
        print("✅ GOOD: Concise response")
    else:
        print(f"⚠️ TOO LONG: {word_count} words (target: <100)")
    print("-" * 60)