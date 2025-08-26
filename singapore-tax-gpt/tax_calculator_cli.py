#!/usr/bin/env python
"""Singapore Tax Calculator with document search."""

import os
from dotenv import load_dotenv
load_dotenv()
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from src.singapore.tax_calculator import SingaporeTaxCalculator
from src.apis.stamp_duty_calculator import StampDutyCalculator

def calculate_income_tax(income):
    """Calculate income tax for a given income."""
    calc = SingaporeTaxCalculator()
    result = calc.calculate_income_tax(income)
    
    print(f"\n💰 Income Tax Calculation for ${income:,}")
    print("="*50)
    print(f"Gross Income: ${income:,}")
    print(f"Tax Amount: ${result.tax_amount:,.2f}")
    print(f"Effective Rate: {result.effective_rate:.2f}%")
    print(f"Take Home: ${income - result.tax_amount:,.2f}")
    
    # Show breakdown
    if result.breakdown:
        print("\nTax Breakdown:")
        for bracket in result.breakdown[:5]:  # Show first 5 brackets
            if bracket['tax'] > 0:
                print(f"  {bracket['income_range']}: ${bracket['tax']:,.2f} ({bracket['rate']})")
    
    print("\n*Based on YA 2024 rates for tax residents")

def calculate_stamp_duty(price, buyer_type="citizen", num_props=0):
    """Calculate stamp duty for property."""
    calc = StampDutyCalculator()
    
    buyer_profiles = {
        "citizen": "singapore_citizen",
        "pr": "pr",
        "foreigner": "foreigner",
        "company": "entity"
    }
    
    profile = buyer_profiles.get(buyer_type.lower(), "singapore_citizen")
    
    result = calc.calculate_property_stamp_duty(
        purchase_price=price,
        buyer_profile=profile,
        num_properties=num_props
    )
    
    print(f"\n🏠 Stamp Duty for ${price:,} Property")
    print(f"Buyer: {profile.replace('_', ' ').title()}")
    if num_props > 0:
        print(f"Property #: {num_props + 1}")
    print("="*50)
    print(f"BSD: ${result['buyer_stamp_duty']:,.2f}")
    print(f"ABSD: ${result['additional_buyer_stamp_duty']:,.2f}")
    print(f"Total: ${result['total_stamp_duty']:,.2f}")

if __name__ == "__main__":
    print("🧮 Singapore Tax Calculator")
    print("="*50)
    print("\nWhat would you like to calculate?")
    print("1. Income Tax")
    print("2. Stamp Duty")
    print("3. Quick Examples")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == "1":
        income = float(input("Enter annual income: $").replace(",", ""))
        calculate_income_tax(income)
        
    elif choice == "2":
        price = float(input("Property price: $").replace(",", ""))
        print("\nBuyer type:")
        print("1. Singapore Citizen")
        print("2. Permanent Resident")
        print("3. Foreigner")
        print("4. Company/Entity")
        buyer_choice = input("Choice (1-4): ").strip()
        
        buyer_types = ["citizen", "pr", "foreigner", "company"]
        buyer_type = buyer_types[int(buyer_choice)-1] if buyer_choice.isdigit() else "citizen"
        
        if buyer_type in ["citizen", "pr"]:
            num_props = int(input("Number of properties already owned (0 for first): "))
        else:
            num_props = 0
            
        calculate_stamp_duty(price, buyer_type, num_props)
        
    else:
        # Quick examples
        print("\n📊 Quick Examples:")
        print("-"*50)
        
        # Income tax examples
        for income in [80000, 135000, 200000]:
            calc = SingaporeTaxCalculator()
            result = calc.calculate_income_tax(income)
            print(f"Income ${income:,} → Tax ${result.tax_amount:,.0f} → Take home ${income - result.tax_amount:,.0f}")
        
        print()
        
        # Stamp duty examples
        calc = StampDutyCalculator()
        
        # $1M citizen first home
        result = calc.calculate_property_stamp_duty(1000000, "singapore_citizen", 0)
        print(f"$1M (Citizen 1st) → BSD ${result['buyer_stamp_duty']:,.0f} + ABSD $0 = ${result['total_stamp_duty']:,.0f}")
        
        # $1M foreigner
        result = calc.calculate_property_stamp_duty(1000000, "foreigner", 0)
        print(f"$1M (Foreigner) → BSD ${result['buyer_stamp_duty']:,.0f} + ABSD ${result['additional_buyer_stamp_duty']:,.0f} = ${result['total_stamp_duty']:,.0f}")