#!/usr/bin/env python
"""Run both models with proper comparison setup for Confident AI."""

import os
from dotenv import load_dotenv
load_dotenv()

# Set API keys
os.environ["CONFIDENT_API_KEY"] = os.getenv("CONFIDENT_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

print("🏆 Model Comparison for Confident AI")
print("=" * 70)

from deepeval.dataset import EvaluationDataset, Golden
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from deepeval import evaluate
from qa_lite import answer_question
import openai

# Comprehensive IRAS test questions
questions = [
    # Tax Rates & Brackets
    "What are the current personal income tax rates for Singapore residents?",
    "What is the tax rate for non-residents?",
    "At what income level do I start paying income tax in Singapore?",
    "What is the highest marginal tax rate for individuals?",
    "How is tax calculated for someone earning S$80,000 annually?",
    "What is the GST rate in Singapore?",
    "What is the corporate tax rate in Singapore?",
    
    # Tax Reliefs & Rebates
    "What personal reliefs am I entitled to as a Singapore resident?",
    "How much can I claim for spouse relief if my spouse has no income?",
    "What is the maximum amount I can claim for child relief?",
    "Can I claim tax relief for my parents? What are the conditions?",
    "What is the Earned Income Relief and how is it calculated?",
    "What reliefs are available for CPF contributions?",
    "Can I claim relief for insurance premiums? What types qualify?",
    
    # Filing Requirements & Deadlines
    "When is the deadline for filing my tax return?",
    "Who is required to file a tax return in Singapore?",
    "What happens if I file my tax return late?",
    "Can I get an extension for filing my tax return?",
    "How long should I keep my tax records?",
    
    # Employment Income
    "Is my 13th month bonus taxable?",
    "How are stock options taxed in Singapore?",
    "Are overseas allowances taxable for Singapore tax residents?",
    "How is director's fee taxed?",
    "What employment benefits are tax-exempt?",
    
    # Investment & Rental Income
    "Do I need to pay tax on dividends received from Singapore companies?",
    "How is rental income from my property taxed?",
    "Are capital gains from selling shares taxable?",
    "How do I report foreign investment income?",
    "What about interest income from savings accounts?",
    
    # Business & Trade Income
    "How do I calculate taxable income for my sole proprietorship?",
    "What business expenses can I deduct?",
    "How is partnership income taxed?",
    "Can I claim depreciation on business assets?",
    
    # Foreign Income & Tax Residency
    "How do I determine if I'm a Singapore tax resident?",
    "Do I need to pay Singapore tax on my overseas income?",
    "What is foreign tax credit and how do I claim it?",
    "How many days must I be in Singapore to be considered a tax resident?",
    "What if I'm a new citizen or PR - when does tax residency start?",
    
    # Special Situations
    "How is retrenchment benefit taxed?",
    "What about income from freelancing or gig economy work?",
    "How are gambling winnings taxed?",
    "Do I pay tax on inheritance received?",
    "How is income from cryptocurrency trading taxed?",
    
    # Deductions & Expenses
    "Can I claim deduction for medical expenses?",
    "What course fees are eligible for tax relief?",
    "Can I deduct home office expenses if I work from home?",
    "Are donations to charities tax deductible? Which organizations qualify?",
    "What are the limits for course fee relief claims?",
    
    # Administrative Procedures
    "How do I submit my tax return online?",
    "Can I authorize someone to file my tax return for me?",
    "How do I appeal against my tax assessment?",
    "What documents do I need to support my tax return?",
    "How can I check the status of my tax refund?",
    
    # Penalties & Compliance
    "What are the penalties for not filing tax returns?",
    "What happens if I underdeclare my income?",
    "Can IRAS audit my tax return? What triggers an audit?",
    "What are the penalties for late payment of taxes?",
    "How do I report errors in my previously filed tax return?",
    
    # Complex Scenarios
    "I worked in Singapore for 6 months and overseas for 6 months. How do I file?",
    "I'm divorced and share custody of my child. Who can claim the child relief?",
    "My employer provided me with a company car. Is this a taxable benefit?",
    "I received a lump sum pension withdrawal. How is this taxed?",
    "I'm a foreign talent on an employment pass. What tax obligations do I have?",
    
    # GST-Related
    "Do I need to register for GST for my small business?",
    "What purchases are GST-exempt?",
    "How do I claim GST input tax?",
    "When must I charge GST to my customers?",
    
    # Property Tax
    "How is property tax calculated for my HDB flat?",
    "What's the difference between owner-occupied and non-owner-occupied property tax rates?",
    "Do I pay property tax on overseas properties?",
    
    # Edge Cases
    "My friend told me I don't need to pay tax on my side income, is this true?",
    "What tax do I pay?",
    "I think IRAS made a mistake on my assessment, what should I do?",
    "Is Bitcoin income taxable?",
    "My company wants to relocate me overseas, what are the tax implications?",
]

# Pull dataset
dataset = EvaluationDataset()
dataset.pull(alias="singapore-tax-iras")

# Use ALL comprehensive questions
dataset.goldens = [Golden(input=q) for q in questions]
print(f"Testing {len(questions)} comprehensive IRAS questions\n")

# Simple metric
metric = AnswerRelevancyMetric(threshold=0.5, model="gpt-3.5-turbo")

# RUN BOTH MODELS IN SAME SCRIPT
print("="*70)
print("RUNNING BOTH MODELS FOR COMPARISON")
print("="*70)

# 1. LionTax
print("\n🤖 Model 1: LionTax")
liontax_cases = []
for i, golden in enumerate(dataset.goldens, 1):
    print(f"  Processing {i}/{len(dataset.goldens)}: {golden.input[:50]}...", end="")
    try:
        output, _ = answer_question(golden.input)
        liontax_cases.append(LLMTestCase(input=golden.input, actual_output=output))
        print(" ✅")
    except Exception as e:
        print(f" ❌ Error: {e}")
        liontax_cases.append(LLMTestCase(input=golden.input, actual_output=f"Error: {str(e)}"))
print(f"✅ {len(liontax_cases)} test cases ready")

# 2. GPT-4
print("\n🤖 Model 2: GPT-4")
client = openai.OpenAI()
gpt4_cases = []
for golden in dataset.goldens:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "Singapore tax expert"}, {"role": "user", "content": golden.input}],
        temperature=0
    )
    gpt4_cases.append(LLMTestCase(input=golden.input, actual_output=response.choices[0].message.content))
print(f"✅ {len(gpt4_cases)} test cases ready")

# EVALUATE BOTH
print("\n📤 Uploading to Confident AI...")

# LionTax evaluation
evaluate(
    test_cases=liontax_cases,
    metrics=[metric],
    hyperparameters={"model": "LionTax"}
)
print("✅ LionTax uploaded")

# GPT-4 evaluation  
evaluate(
    test_cases=gpt4_cases,
    metrics=[metric],
    hyperparameters={"model": "GPT-4"}
)
print("✅ GPT-4 uploaded")

print("\n" + "="*70)
print("✅ DONE! Both models tested")
print("="*70)
print("""
TO COMPARE SIDE-BY-SIDE:

1. Go to https://app.confident-ai.com
2. Find 'Compare Test Results' in sidebar
3. Select the 2 most recent test runs
4. Click Compare

You'll see side-by-side comparison!
""")