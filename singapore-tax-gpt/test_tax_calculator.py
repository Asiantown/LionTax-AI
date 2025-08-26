"""Test Singapore tax calculator functionality."""

from src.singapore.tax_calculator import SingaporeTaxCalculator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_tax_calculator():
    """Test tax calculation functionality."""
    print("\n" + "="*70)
    print("💰 SINGAPORE TAX CALCULATOR TEST")
    print("="*70)
    
    calculator = SingaporeTaxCalculator(year_of_assessment=2024)
    
    # Test 1: Basic Income Tax Calculation
    print("\n📊 TEST 1: Income Tax for Different Income Levels")
    print("-" * 50)
    
    test_incomes = [40000, 60000, 80000, 100000, 150000, 250000, 500000, 1000000]
    
    for income in test_incomes:
        result = calculator.calculate_income_tax(income)
        print(f"\n💵 Income: ${income:,}")
        print(f"  Tax Amount: ${result.tax_amount:,.0f}")
        print(f"  Effective Rate: {result.effective_rate}%")
        print(f"  Marginal Rate: {result.marginal_rate:.1f}%")
    
    # Test 2: Income Tax with Reliefs
    print("\n📊 TEST 2: Income Tax with Reliefs")
    print("-" * 50)
    
    income = 100000
    reliefs = {
        'spouse': 2000,
        'qualifying_child': 4000,
        'parent': 9000,
        'cpf_cash_top_up': 7000
    }
    
    result = calculator.calculate_income_tax(income, reliefs, age=35)
    
    print(f"\n💵 Gross Income: ${income:,}")
    print(f"📋 Reliefs Applied:")
    for relief in result.reliefs_applied:
        print(f"  - {relief['type']}: ${relief['amount']:,.0f}")
    print(f"\n💰 Chargeable Income: ${result.chargeable_income:,.0f}")
    print(f"💸 Tax Amount: ${result.tax_amount:,.0f}")
    print(f"📈 Effective Rate: {result.effective_rate}%")
    
    # Test 3: Non-Resident Tax
    print("\n📊 TEST 3: Non-Resident vs Resident Tax")
    print("-" * 50)
    
    income = 120000
    
    resident_result = calculator.calculate_income_tax(income, is_resident=True)
    non_resident_result = calculator.calculate_income_tax(income, is_resident=False)
    
    print(f"\n💵 Income: ${income:,}")
    print(f"\n🏠 Resident Tax: ${resident_result.tax_amount:,.0f} ({resident_result.effective_rate}%)")
    print(f"✈️ Non-Resident Tax: ${non_resident_result.tax_amount:,.0f} ({non_resident_result.effective_rate}%)")
    print(f"Difference: ${abs(non_resident_result.tax_amount - resident_result.tax_amount):,.0f}")
    
    # Test 4: GST Calculation
    print("\n📊 TEST 4: GST Calculations")
    print("-" * 50)
    
    # GST exclusive
    amount = 1000
    gst_result = calculator.calculate_gst(amount, year=2024, is_inclusive=False)
    print(f"\n🛍️ Purchase Amount (excl. GST): ${amount:,.2f}")
    print(f"  GST ({gst_result['gst_rate']}%): ${gst_result['gst_amount']:,.2f}")
    print(f"  Total with GST: ${gst_result['total']:,.2f}")
    
    # GST inclusive
    total = 1090
    gst_result = calculator.calculate_gst(total, year=2024, is_inclusive=True)
    print(f"\n🛍️ Total Amount (incl. GST): ${total:,.2f}")
    print(f"  Base Amount: ${gst_result['base_amount']:,.2f}")
    print(f"  GST Component: ${gst_result['gst_amount']:,.2f}")
    
    # Test 5: Property Tax
    print("\n📊 TEST 5: Property Tax Calculation")
    print("-" * 50)
    
    annual_values = [50000, 100000, 150000]
    
    for av in annual_values:
        result = calculator.calculate_property_tax(av, is_owner_occupied=True)
        print(f"\n🏠 Annual Value: ${av:,}")
        print(f"  Property Tax: ${result['tax_amount']:,.2f}")
        print(f"  Type: {result['type']}")
    
    # Test 6: CPF Calculations
    print("\n📊 TEST 6: CPF Contributions")
    print("-" * 50)
    
    test_cases = [
        (5000, 30, "Below 55"),
        (8000, 45, "Below 55 (capped)"),
        (6000, 58, "55-60"),
        (5000, 65, "65-70")
    ]
    
    for salary, age, description in test_cases:
        cpf_result = calculator.calculate_cpf(salary, age)
        print(f"\n👤 {description}: ${salary:,}/month, Age {age}")
        print(f"  Employee: ${cpf_result['monthly']['employee']:,.2f}/month")
        print(f"  Employer: ${cpf_result['monthly']['employer']:,.2f}/month")
        print(f"  Total: ${cpf_result['monthly']['total']:,.2f}/month")
        print(f"  Annual CPF: ${cpf_result['annual']['total']:,.2f}")
    
    # Test 7: Take-Home Pay Calculation
    print("\n📊 TEST 7: Take-Home Pay Calculation")
    print("-" * 50)
    
    test_salaries = [
        (60000, 30, "Junior Professional"),
        (100000, 35, "Mid-Level"),
        (180000, 40, "Senior Professional")
    ]
    
    for annual_income, age, role in test_salaries:
        take_home = calculator.calculate_take_home(
            annual_income, 
            age=age,
            reliefs={'spouse': 2000}
        )
        
        print(f"\n💼 {role}: ${annual_income:,}/year")
        print(f"  Monthly Gross: ${take_home['breakdown']['gross_monthly']:,.2f}")
        print(f"  CPF Deduction: ${take_home['breakdown']['cpf_deduction']:,.2f}")
        print(f"  Tax Deduction: ${take_home['breakdown']['tax_deduction']:,.2f}")
        print(f"  Net Monthly: ${take_home['breakdown']['net_monthly']:,.2f}")
        print(f"  Annual Take-Home: ${take_home['take_home']['annual']:,.2f}")
    
    # Test 8: Tax Planning Scenario
    print("\n📊 TEST 8: Tax Planning Scenario")
    print("-" * 50)
    
    income = 150000
    
    # Without optimization
    basic_result = calculator.calculate_income_tax(income, age=40)
    
    # With tax optimization
    optimized_reliefs = {
        'spouse': 2000,
        'qualifying_child': 8000,  # 2 children
        'parent': 9000,
        'cpf_voluntary': 15300,
        'srs': 15300,
        'course_fees': 5500
    }
    
    optimized_result = calculator.calculate_income_tax(income, optimized_reliefs, age=40)
    
    print(f"\n💵 Income: ${income:,}")
    print(f"\n📊 Without Tax Planning:")
    print(f"  Tax: ${basic_result.tax_amount:,.0f}")
    print(f"  Effective Rate: {basic_result.effective_rate}%")
    
    print(f"\n📊 With Tax Planning:")
    print(f"  Total Reliefs: ${optimized_result.tax_reliefs:,.0f}")
    print(f"  Tax: ${optimized_result.tax_amount:,.0f}")
    print(f"  Effective Rate: {optimized_result.effective_rate}%")
    print(f"\n💰 Tax Savings: ${basic_result.tax_amount - optimized_result.tax_amount:,.0f}")
    
    # Summary
    print("\n" + "="*70)
    print("✅ TAX CALCULATOR TEST COMPLETE")
    print("="*70)
    
    print("\n📊 Features Tested:")
    print("  • Progressive tax calculation")
    print("  • Tax relief application")
    print("  • Resident vs non-resident rates")
    print("  • GST calculations")
    print("  • Property tax")
    print("  • CPF contributions")
    print("  • Take-home pay")
    print("  • Tax optimization scenarios")


if __name__ == "__main__":
    test_tax_calculator()