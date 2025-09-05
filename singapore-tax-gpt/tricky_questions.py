#!/usr/bin/env python
"""Tricky questions to test the system."""

import warnings
warnings.filterwarnings('ignore')

from qa_working import answer_question

# Collection of tricky questions that test document search
tricky_questions = [
    # Residency and days questions
    "I worked in Singapore for 182.5 days - am I a tax resident?",
    "What if I spent exactly 183 days in Singapore?",
    "I was in Singapore for 60 days - do I need to pay tax?",
    
    # Remote work scenarios
    "What happens if I work remotely from Malaysia for a Singapore company?",
    "I live in Thailand but work for a Singapore firm - how am I taxed?",
    "Can I avoid Singapore tax by working from Bali?",
    
    # Investment and crypto
    "What are the tax implications of cryptocurrency trading?",
    "How is Bitcoin mining income taxed?",
    "What about NFT sales - are they taxable?",
    "If I receive income from selling virtual real estate in the metaverse, how is it taxed?",
    
    # Stock options and equity
    "How is tax calculated for stock options?",
    "What if my startup gives me shares instead of salary?",
    "Are RSUs taxed differently than stock options?",
    
    # Unusual income scenarios
    "What if my income is negative?",
    "How is lottery winning taxed in Singapore?",
    "What about income from OnlyFans or content creation?",
    "Is inheritance taxable?",
    
    # Deductions and expenses
    "Can I deduct home office expenses?",
    "What about gym membership as a health expense?",
    "Can I claim my Netflix subscription as a business expense?",
    "Are work-from-home internet bills deductible?",
    
    # International scenarios
    "What about tax on overseas investment income?",
    "I have rental income from a property in Malaysia - is it taxed?",
    "Do I pay tax on foreign dividends?",
    "What if I'm paid in USD by a US company?",
    
    # Edge cases
    "What if I earn exactly $19,999.99?",
    "What if I earn exactly $20,000?",
    "What's the tax on $1?",
    "Can I pay someone else's tax for them?",
    
    # Complex scenarios
    "I'm a digital nomad with no fixed address - how am I taxed?",
    "What if I work on a cruise ship in international waters?",
    "I'm an influencer - how are sponsorships taxed?",
    "Are tips and gratuities taxable income?"
]

print("🎯 TRICKY QUESTIONS FOR TESTING")
print("=" * 80)
print(f"Total: {len(tricky_questions)} questions")
print("=" * 80)

# You can test any of these by uncommenting:
# for i, q in enumerate(tricky_questions[:5], 1):  # Test first 5
#     print(f"\n{i}. {q}")
#     print("-" * 60)
#     answer, sources = answer_question(q)
#     print(answer[:300] + "...")
#     print(f"Sources: {sources}")

# Or test a specific question:
test_question = "I worked in Singapore for 182.5 days - am I a tax resident?"
print(f"\nTest Question: {test_question}")
print("-" * 60)
answer, sources = answer_question(test_question)
print("Answer:")
print(answer)
print(f"\nSources: {sources}")