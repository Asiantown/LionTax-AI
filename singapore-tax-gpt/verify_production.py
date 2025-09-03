#!/usr/bin/env python
"""Comprehensive production verification."""

import warnings
warnings.filterwarnings('ignore')

print("🔍 PRODUCTION VERIFICATION")
print("="*60)

# Test local version
print("\n1. LOCAL VERSION TEST:")
print("-"*40)

from qa_working import answer_question

# Test questions
test_questions = [
    "What are the current personal income tax rates for Singapore residents?",
    "How is tax calculated for someone earning S$80,000 annually?"
]

local_results = []

for q in test_questions:
    answer, _ = answer_question(q)
    local_results.append({
        'question': q,
        'answer': answer,
        'line_breaks': answer.count('\n'),
        'has_rates': '$0 - $20,000: 0%' in answer,
        'has_total': 'Total Tax = $3,350' in answer,
        'clean_text': 'at0' not in answer.replace(' ', '') and '@' not in answer
    })

# Print local results
for i, result in enumerate(local_results, 1):
    print(f"\nQ{i}: {result['question'][:50]}...")
    print(f"  Line breaks: {result['line_breaks']}")
    print(f"  Has rates: {result['has_rates']}")
    print(f"  Has total: {result['has_total']}")
    print(f"  Clean text: {result['clean_text']}")
    
    if i == 1:
        # For tax rates question
        if result['has_rates'] and result['line_breaks'] >= 10:
            print("  ✅ LOCAL: Tax rates formatted correctly")
        else:
            print("  ❌ LOCAL: Tax rates formatting issue")
    
    if i == 2:
        # For calculation question
        if result['has_total'] and result['line_breaks'] >= 5 and result['clean_text']:
            print("  ✅ LOCAL: Calculation formatted correctly")
        else:
            print("  ❌ LOCAL: Calculation formatting issue")

print("\n" + "="*60)
print("\n2. PRODUCTION URL:")
print("-"*40)
print("URL: https://liontax-ai-production.up.railway.app")
print("\n📋 MANUAL TESTING INSTRUCTIONS:")
print("1. Open the URL above in your browser")
print("2. Ask: 'What are the current personal income tax rates for Singapore residents?'")
print("3. Check:")
print("   - Tax rates should appear on SEPARATE LINES")
print("   - Should start with 'Current Singapore Resident Tax Rates (2024):'")
print("   - Should show '$0 - $20,000: 0%' on its own line")
print("   - NO markdown symbols (** or *)")
print("   - NO mangled text like 'at0o' or '20,000at0'")
print()
print("4. Ask: 'How is tax calculated for someone earning S$80,000 annually?'")
print("5. Check:")
print("   - Should show 'For the $80,000 example:' at the top")
print("   - Each calculation step on its own line")
print("   - Should show 'Total Tax = $3,350'")
print("   - Clean formatting with 'at 0%' not 'at0o'")

print("\n" + "="*60)
print("\n✅ LOCAL TESTS COMPLETE")
print("🚀 Railway should be deploying v2.2 now...")
print("⏱️ Deployment typically takes 2-5 minutes")
print("\nIf formatting is still broken after deployment:")
print("1. Check Railway logs for errors")
print("2. Clear Railway build cache in settings")
print("3. Restart the service")
print("4. Check environment variables are set correctly")