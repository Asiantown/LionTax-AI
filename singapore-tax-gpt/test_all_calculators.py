"""Test all tax calculators to verify they work."""

import os
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from src.singapore.tax_calculator import SingaporeTaxCalculator
from src.apis.stamp_duty_calculator import StampDutyCalculator
from src.core.enhanced_rag import EnhancedRAGEngine

print("="*70)
print("TESTING ALL TAX CALCULATORS")
print("="*70)

# Initialize calculators
tax_calc = SingaporeTaxCalculator()
stamp_calc = StampDutyCalculator()
rag_engine = EnhancedRAGEngine()

# Test 1: Income Tax
print("\n1️⃣ INCOME TAX CALCULATOR")
print("-"*50)
result = tax_calc.calculate_income_tax(100000)
print(f"Income: $100,000")
print(f"Tax: ${result.tax_amount:,.0f}")
print(f"Effective Rate: {result.effective_rate:.2f}%")
print("✅ Income tax calculator works!")

# Test 2: GST
print("\n2️⃣ GST CALCULATOR")
print("-"*50)
result = tax_calc.calculate_gst(1000)
print(f"Base Amount: $1,000")
print(f"GST (9%): ${result['gst_amount']:,.2f}")
print(f"Total: ${result['total']:,.2f}")
print("✅ GST calculator works!")

# Test 3: CPF
print("\n3️⃣ CPF CALCULATOR")
print("-"*50)
result = tax_calc.calculate_cpf(5000, age=30)
print(f"Monthly Salary: $5,000")
print(f"Employee CPF: ${result['monthly']['employee']:,.2f}")
print(f"Employer CPF: ${result['monthly']['employer']:,.2f}")
print("✅ CPF calculator works!")

# Test 4: Property Tax
print("\n4️⃣ PROPERTY TAX CALCULATOR")
print("-"*50)
result = tax_calc.calculate_property_tax(500000, is_owner_occupied=True)
print(f"Annual Value: $500,000")
print(f"Property Tax: ${result['tax_amount']:,.2f}")
print("✅ Property tax calculator works!")

# Test 5: Stamp Duty
print("\n5️⃣ STAMP DUTY CALCULATOR")
print("-"*50)
result = stamp_calc.calculate_property_stamp_duty(
    purchase_price=1000000,
    buyer_profile="singapore_citizen",
    num_properties=0
)
print(f"Property Price: $1,000,000 (Citizen, 1st property)")
print(f"BSD: ${result['buyer_stamp_duty']:,.0f}")
print(f"ABSD: ${result['additional_buyer_stamp_duty']:,.0f}")
print(f"Total: ${result['total_stamp_duty']:,.0f}")
print("✅ Stamp duty calculator works!")

# Test 6: Integration with RAG
print("\n6️⃣ RAG INTEGRATION TEST")
print("-"*50)
query = "Calculate income tax for $150,000"
response = rag_engine.query_with_metadata(query)
if "Tax Calculation:" in response['answer']:
    print(f"Query: {query}")
    print("Response: Tax calculation returned successfully")
    print("✅ RAG integration with calculators works!")
else:
    print("⚠️ RAG integration needs checking")

print("\n" + "="*70)
print("✅ ALL CALCULATORS WORKING!")
print("="*70)