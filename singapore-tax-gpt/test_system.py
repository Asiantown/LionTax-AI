#!/usr/bin/env python
"""Test the Singapore Tax Q&A System with various questions."""

import os
from dotenv import load_dotenv
load_dotenv()
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from qa_working import answer_question
import time

print("🧪 SINGAPORE TAX Q&A SYSTEM TEST")
print("="*70)
print("Testing with various tax questions...\n")

# Test questions covering different acts
test_questions = [
    # Income Tax
    "What are the income tax rates in Singapore?",
    "What is the penalty for late filing of income tax?",
    "What tax reliefs are available?",
    
    # GST
    "What is the GST rate?",
    "When must a company register for GST?",
    "What goods are exempt from GST?",
    
    # Property/Stamp Duty
    "What is stamp duty for buying property?",
    "How is property tax calculated?",
    "What is ABSD (Additional Buyer's Stamp Duty)?",
    
    # Casino/Gambling
    "What is the casino entry levy?",
    "What taxes apply to casino winnings?",
    "How are gambling operators taxed?",
    
    # General
    "What happens if I don't pay my taxes?",
    "Can foreigners claim tax reliefs?",
    "How do I calculate my taxable income?",
]

for i, question in enumerate(test_questions, 1):
    print(f"[{i}/{len(test_questions)}] ❓ {question}")
    print("-"*70)
    
    start = time.time()
    answer, sources = answer_question(question)
    elapsed = time.time() - start
    
    # Truncate long answers for display
    if len(answer) > 500:
        answer = answer[:500] + "..."
    
    print(f"📝 Answer ({elapsed:.1f}s):")
    print(answer)
    
    if sources:
        print(f"\n📚 Sources: {', '.join(sources)}")
    
    print("\n" + "="*70 + "\n")
    time.sleep(0.5)  # Small delay between questions

print("✅ TEST COMPLETE!")
print("\nTo ask your own questions, run: uv run python qa_working.py")