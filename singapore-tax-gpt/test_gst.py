#!/usr/bin/env python
"""Test GST question only."""

from qa_lite import answer_question

question = "What is the current GST rate in Singapore?"

print("🧪 Testing GST Question")
print("=" * 60)
print(f"❓ Question: {question}")

answer, _ = answer_question(question)

print(f"📝 Answer: {answer}")
print(f"📊 Length: {len(answer.split())} words")