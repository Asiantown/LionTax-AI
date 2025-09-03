#!/usr/bin/env python
"""Final test to ensure formatting is perfect."""

import warnings
warnings.filterwarnings('ignore')

from qa_working import answer_question

def test_final_formatting():
    """Test that formatting is exactly as required."""
    
    print("FINAL FORMAT TEST")
    print("=" * 60)
    
    # Test 1: Tax rates
    q1 = "What are the current personal income tax rates for Singapore residents?"
    answer1, _ = answer_question(q1)
    
    print(f"Q1: {q1}\n")
    print("ACTUAL OUTPUT:")
    print(answer1)
    print("\n" + "-" * 40)
    print("EXPECTED OUTPUT:")
    print("Current Singapore Resident Tax Rates (2024):\n")
    print("$0 - $20,000: 0%")
    print("$20,001 - $30,000: 2%")
    print("...etc")
    
    # Check critical issues from screenshots
    issues = []
    
    # Check if all on one line (missing line breaks)
    if answer1.count('\n') < 10:
        issues.append("❌ Missing line breaks - text all on one line!")
    else:
        print("✅ Line breaks working")
    
    # Check for mangled text
    if 'at0o' in answer1 or '—' in answer1 or '{}' in answer1:
        issues.append("❌ Text corruption detected!")
    else:
        print("✅ No text corruption")
    
    # Check for markdown
    if '**' in answer1 or '*' in answer1:
        issues.append("❌ Markdown still present!")
    else:
        print("✅ No markdown")
    
    print("\n" + "=" * 60 + "\n")
    
    # Test 2: $80,000 calculation
    q2 = "How is tax calculated for someone earning S$80,000 annually?"
    answer2, _ = answer_question(q2)
    
    print(f"Q2: {q2}\n")
    print("ACTUAL OUTPUT:")
    print(answer2)
    print("\n" + "-" * 40)
    print("EXPECTED OUTPUT:")
    print("For the $80,000 example:\n")
    print("Calculation: First $20k tax-free, then apply progressive rates")
    print("- First $20,000 at 0% = $0")
    print("...etc")
    
    # Check for mangled calculation
    if 'at0o' in answer2 or 'at2200' in answer2:
        issues.append("❌ Calculation text corrupted!")
    else:
        print("✅ Calculation text clean")
    
    if answer2.count('\n') < 5:
        issues.append("❌ Calculation missing line breaks!")
    else:
        print("✅ Calculation has line breaks")
    
    # Final verdict
    print("\n" + "=" * 60)
    print("FINAL VERDICT:")
    
    if not issues:
        print("✅✅✅ ALL FORMATTING PERFECT - READY TO DEPLOY! ✅✅✅")
    else:
        print("❌❌❌ FORMATTING ISSUES DETECTED ❌❌❌")
        for issue in issues:
            print(f"  {issue}")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = test_final_format()
    exit(0 if success else 1)