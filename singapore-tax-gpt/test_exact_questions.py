#!/usr/bin/env python
"""Test the EXACT questions from user screenshots."""

import warnings
warnings.filterwarnings('ignore')

from qa_working import answer_question

def test_exact_questions():
    """Test the exact questions from user screenshots."""
    
    print("Testing EXACT User Questions")
    print("=" * 60)
    
    # Exact question from screenshot 1
    q1 = "What are the current personal income tax rates for Singapore residents?"
    print(f"\nQ1: {q1}")
    answer1, _ = answer_question(q1)
    print("Answer:")
    print(answer1)
    print("\nExpected format:")
    print("Current Singapore Resident Tax Rates (2024):")
    print("$0 - $20,000: 0%")
    print("$20,001 - $30,000: 2%")
    print("...etc")
    
    # Check if answer matches expected format
    if answer1.startswith("Current Singapore Resident Tax Rates (2024):") and "$0 - $20,000: 0%" in answer1:
        print("✅ FORMAT CORRECT")
    else:
        print("❌ FORMAT WRONG - Getting RAG response instead of structured data")
    
    print("\n" + "-" * 60)
    
    # Exact question from screenshot 2
    q2 = "How is tax calculated for someone earning S$80,000 annually?"
    print(f"\nQ2: {q2}")
    answer2, _ = answer_question(q2)
    print("Answer:")
    print(answer2)
    print("\nExpected format:")
    print("For the $80,000 example:")
    print("Calculation: First $20k tax-free, then apply progressive rates")
    print("- First $20,000 at 0% = $0")
    print("...etc")
    print("Total Tax = $3,350")
    
    # Check if answer matches expected format
    if "For the $80,000 example:" in answer2 and "Total Tax = $3,350" in answer2 and "@" not in answer2:
        print("✅ FORMAT CORRECT - No @ symbols, clean text")
    else:
        print("❌ FORMAT WRONG - Check for markdown or @ symbols")
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    
    # Final check
    issues = []
    if not answer1.startswith("Current Singapore Resident Tax Rates (2024):"):
        issues.append("Q1 not using structured data")
    if "@" in answer2:
        issues.append("Q2 has @ symbols in formatting")
    if "**" in answer1 or "**" in answer2:
        issues.append("Markdown formatting still present")
    
    if not issues:
        print("✅ ALL TESTS PASSED - Ready for deployment!")
    else:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")

if __name__ == "__main__":
    test_exact_questions()