#!/usr/bin/env python
"""Test deployment to ensure formatting is working correctly."""

import warnings
warnings.filterwarnings('ignore')

print("DEPLOYMENT TEST v2.1")
print("=" * 60)

# Import the Q&A system
from qa_working import answer_question

# Test exact questions from screenshots
questions = [
    "What are the current personal income tax rates for Singapore residents?",
    "How is tax calculated for someone earning S$80,000 annually?"
]

for i, q in enumerate(questions, 1):
    print(f"\nQuestion {i}: {q}")
    print("-" * 40)
    
    answer, sources = answer_question(q)
    
    # Print raw answer to see exact format
    print("RAW ANSWER:")
    print(repr(answer))
    print()
    
    print("FORMATTED ANSWER:")
    print(answer)
    print()
    
    # Check for issues
    issues = []
    
    # Check line breaks
    if answer.count('\n') < 5:
        issues.append("❌ Missing line breaks")
    else:
        print("✅ Line breaks present")
    
    # Check for mangled text
    if 'at0' in answer.replace(' ', '') or '@' in answer:
        issues.append("❌ Mangled text detected")
    else:
        print("✅ Clean text")
    
    # Check for markdown
    if '**' in answer or '*' in answer:
        issues.append("❌ Markdown present")
    else:
        print("✅ No markdown")
    
    if issues:
        print("\nISSUES:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ ALL CHECKS PASSED")
    
    print("=" * 60)

print("\nFINAL VERDICT:")
print("If all checks pass locally but fail in deployment,")
print("you need to force redeploy with cache clear.")