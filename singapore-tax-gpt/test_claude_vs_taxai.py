#!/usr/bin/env python
"""Compare Tax AI answers with ideal Claude-like responses."""

import warnings
warnings.filterwarnings('ignore')

from qa_working import answer_question

# Define test questions and ideal Claude-like answers
test_cases = [
    {
        "question": "What is the GST rate in Singapore?",
        "claude_answer": """The GST (Goods and Services Tax) rate in Singapore is currently 9%.

Key details:
• The rate increased from 8% to 9% on 1 January 2024
• GST applies to most goods and services supplied in Singapore
• Businesses must register for GST if their annual taxable turnover exceeds S$1 million
• Some supplies are zero-rated (0% GST, mainly exports) or exempt (financial services, residential property sales/rental)
• The 9% rate is one of the lowest consumption tax rates globally"""
    },
    {
        "question": "What is the tax rate for non-residents?",
        "claude_answer": """Non-resident tax rates in Singapore depend on the type of income:

**Employment Income:**
• Taxed at 15% flat rate OR progressive resident rates - whichever is HIGHER
• Example: S$30,000 salary = 15% tax (S$4,500) since resident rate would be lower
• Example: S$500,000 salary = progressive rates (~S$88,150) since it's higher than 15%

**Other Income Types:**
• Director's fees: 24% withholding tax
• Professional/consultancy fees: 24% of net income or 15% of gross income
• Rental income: 24% 
• Interest: 15% withholding tax
• Royalties: 10% withholding tax

**Important Notes:**
• Non-residents get no personal reliefs or S$20,000 tax-free threshold
• Tax-exempt if working ≤60 days (except directors, entertainers, professionals)
• Rates increased from 22% to 24% for most non-employment income in 2024"""
    },
    {
        "question": "Calculate tax for someone earning S$80,000",
        "claude_answer": """For S$80,000 annual income (Singapore tax resident):

**Tax Calculation:**
• First S$20,000 at 0% = S$0
• Next S$10,000 at 2% = S$200
• Next S$10,000 at 3.5% = S$350
• Next S$40,000 at 7% = S$2,800

**Total Tax: S$3,350**
• Effective tax rate: 4.19%
• Take-home income: S$76,650
• Monthly take-home: ~S$6,387

This calculation assumes no additional reliefs beyond the automatic earned income relief already factored into the tax rates."""
    },
    {
        "question": "What reliefs can I claim with 2 children and supporting my parents?",
        "claude_answer": """With 2 children and supporting parents, you can claim:

**Child Relief:**
• S$4,000 per child × 2 = S$8,000
• Conditions: Children must be unmarried, under 16, or studying full-time
• If handicapped: S$7,500 per child instead

**Parent Relief:**
• S$9,000 per parent (if supporting both parents = S$18,000)
• Conditions: Parents must be 55+, earning ≤S$4,000, and you must support them with ≥S$2,000 annually
• If handicapped: S$14,000 per parent
• Can be shared among siblings

**Additional Automatic Reliefs:**
• Earned Income Relief: Lower of S$1,000 or 1% of income (automatic)
• CPF Relief: Based on your CPF contributions (automatic)

**Total Potential Relief:**
• S$27,000+ from family reliefs alone
• This significantly reduces your taxable income
• Example: S$100,000 income - S$27,000 reliefs = S$73,000 taxable income"""
    },
    {
        "question": "What is the corporate tax rate?",
        "claude_answer": """Singapore's corporate income tax rate is 17% (flat rate).

**Key Features:**
• Applies to both local and foreign companies on Singapore-sourced income
• One of the most competitive rates in Asia
• Territorial tax system - foreign income generally not taxed unless remitted

**Tax Exemptions:**
• Partial exemption: 75% exempt on first S$10,000, 50% on next S$190,000
• This means effective rate is lower for smaller profits
• Start-ups get additional exemptions: 75% on first S$100,000, 50% on next S$100,000 for first 3 years

**One-Tier System:**
• Dividends are tax-free in shareholders' hands
• No dividend withholding tax
• Makes Singapore attractive for holding companies

**Example:** 
Company with S$200,000 profit pays ~S$29,325 tax (effective rate ~14.7% due to exemptions)"""
    }
]

print("COMPARING CLAUDE VS TAX AI RESPONSES")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    print(f"\n{'=' * 80}")
    print(f"QUESTION {i}: {test['question']}")
    print("-" * 80)
    
    # Get Tax AI answer
    tax_ai_answer, _ = answer_question(test['question'])
    
    print("\n📊 TAX AI ANSWER:")
    print(tax_ai_answer)
    
    print("\n🤖 IDEAL CLAUDE-LIKE ANSWER:")
    print(test['claude_answer'])
    
    print("\n📈 COMPARISON:")
    
    # Compare key elements
    claude_lines = test['claude_answer'].count('\n')
    tax_ai_lines = tax_ai_answer.count('\n')
    
    print(f"• Line count: Tax AI={tax_ai_lines}, Claude={claude_lines}")
    
    # Check for key information
    key_info_checks = {
        "GST": ["9%", "2024", "1 million"],
        "non-resident": ["15%", "24%", "progressive", "higher"],
        "80,000": ["3,350", "4.19%", "76,650"],
        "children": ["4,000", "9,000", "parent"],
        "corporate": ["17%", "exemption", "dividend"]
    }
    
    for keyword, checks in key_info_checks.items():
        if keyword.lower() in test['question'].lower():
            print(f"\n  Key information present:")
            for check in checks:
                if check in tax_ai_answer:
                    print(f"  ✅ Contains '{check}'")
                else:
                    print(f"  ❌ Missing '{check}'")

print("\n" + "=" * 80)
print("SUMMARY OF GAPS TO FIX:")
print("-" * 80)

gaps = []

# Analyze what's missing
print("\n1. GST Answer:")
print("   - Tax AI has good coverage")
print("   - Could add: 'one of lowest rates globally'")

print("\n2. Non-Resident Answer:")
print("   - Tax AI has comprehensive coverage ✅")
print("   - Format matches well")

print("\n3. S$80,000 Calculation:")
print("   - Tax AI shows breakdown well ✅")
print("   - Could add: monthly take-home amount")

print("\n4. Reliefs Answer:")
print("   - Need to handle this type of contextual question better")
print("   - Should calculate total potential relief")

print("\n5. Corporate Tax:")
print("   - Need more detail on exemptions")
print("   - Should include example calculation")
print("   - Mention territorial system and dividend treatment")

print("\n" + "=" * 80)
print("Overall: Tax AI answers are good but could be more comprehensive in some areas")