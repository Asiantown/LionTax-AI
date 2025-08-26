"""Interactive calculator testing - Try different scenarios."""

import os
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from src.singapore.tax_calculator import SingaporeTaxCalculator
from src.apis.stamp_duty_calculator import StampDutyCalculator
from src.core.enhanced_rag import EnhancedRAGEngine

def test_income_tax():
    """Test income tax with different amounts."""
    calc = SingaporeTaxCalculator()
    
    print("\n" + "="*60)
    print("💰 INCOME TAX CALCULATOR EXAMPLES")
    print("="*60)
    
    test_incomes = [50000, 80000, 120000, 200000, 500000, 1000000]
    
    for income in test_incomes:
        result = calc.calculate_income_tax(income)
        print(f"\nIncome: ${income:,}")
        print(f"  → Tax: ${result.tax_amount:,.0f}")
        print(f"  → Effective Rate: {result.effective_rate:.2f}%")
        print(f"  → Take Home: ${income - result.tax_amount:,.0f}")

def test_stamp_duty():
    """Test stamp duty for different scenarios."""
    calc = StampDutyCalculator()
    
    print("\n" + "="*60)
    print("🏠 STAMP DUTY CALCULATOR EXAMPLES")
    print("="*60)
    
    scenarios = [
        ("$800k - Citizen 1st Home", 800000, "singapore_citizen", 0),
        ("$800k - Citizen 2nd Home", 800000, "singapore_citizen", 1),
        ("$1.5M - PR 1st Home", 1500000, "pr", 0),
        ("$2M - Foreigner", 2000000, "foreigner", 0),
        ("$3M - Company", 3000000, "entity", 0),
    ]
    
    for desc, price, profile, props in scenarios:
        result = calc.calculate_property_stamp_duty(price, buyer_profile=profile, num_properties=props)
        print(f"\n{desc}:")
        print(f"  → BSD: ${result['buyer_stamp_duty']:,.0f}")
        print(f"  → ABSD: ${result['additional_buyer_stamp_duty']:,.0f}")
        print(f"  → Total: ${result['total_stamp_duty']:,.0f}")

def test_cpf():
    """Test CPF calculations."""
    calc = SingaporeTaxCalculator()
    
    print("\n" + "="*60)
    print("📊 CPF CALCULATOR EXAMPLES")
    print("="*60)
    
    salaries = [3000, 5000, 6000, 8000, 10000]
    
    for salary in salaries:
        result = calc.calculate_cpf(salary, age=30)
        print(f"\nMonthly Salary: ${salary:,}")
        print(f"  → Employee: ${result['monthly']['employee']:,.0f} ({result['rates']['employee']})")
        print(f"  → Employer: ${result['monthly']['employer']:,.0f} ({result['rates']['employer']})")
        print(f"  → Total CPF: ${result['monthly']['total']:,.0f}")
        print(f"  → Take Home: ${salary - result['monthly']['employee']:,.0f}")

def test_with_rag():
    """Test through RAG system with natural language."""
    engine = EnhancedRAGEngine()
    
    print("\n" + "="*60)
    print("💬 NATURAL LANGUAGE QUERIES (via RAG)")
    print("="*60)
    
    queries = [
        "Calculate tax for $100,000 income",
        "What's the stamp duty for a $1.5 million property?",
        "How much CPF for $5000 salary?",
        "Calculate stamp duty for foreigner buying $2 million property",
        "What's my take home pay if I earn $120,000 per year?",
    ]
    
    for query in queries:
        print(f"\n❓ {query}")
        response = engine.query_with_metadata(query)
        
        # Extract key numbers from response
        lines = response['answer'].split('\n')
        for line in lines:
            if '$' in line and any(word in line.lower() for word in ['tax', 'duty', 'cpf', 'total', 'take', 'bsd', 'absd']):
                print(f"   {line.strip()}")

def main():
    print("\n🧮 SINGAPORE TAX CALCULATOR TEST SUITE")
    print("=" * 60)
    print("Choose what to test:")
    print("1. Income Tax Calculator")
    print("2. Stamp Duty Calculator")
    print("3. CPF Calculator")
    print("4. Natural Language Queries (RAG)")
    print("5. Run All Tests")
    print("=" * 60)
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        test_income_tax()
    elif choice == "2":
        test_stamp_duty()
    elif choice == "3":
        test_cpf()
    elif choice == "4":
        test_with_rag()
    elif choice == "5":
        test_income_tax()
        test_stamp_duty()
        test_cpf()
        test_with_rag()
    else:
        print("Running all tests by default...")
        test_income_tax()
        test_stamp_duty()
        test_cpf()

if __name__ == "__main__":
    # You can either run interactively or just see all examples
    # Comment out main() and uncomment specific tests to run directly
    
    # Option 1: Interactive menu
    # main()
    
    # Option 2: Run all examples directly
    test_income_tax()
    test_stamp_duty()
    test_cpf()
    test_with_rag()