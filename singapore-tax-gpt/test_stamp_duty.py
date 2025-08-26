"""Test stamp duty calculation with IRAS API integration."""

import os
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from src.core.enhanced_rag import EnhancedRAGEngine
from src.apis.stamp_duty_calculator import StampDutyCalculator
import logging

logging.basicConfig(level=logging.INFO)


def test_stamp_duty():
    """Test stamp duty calculations."""
    print("\n" + "="*70)
    print("🏠 STAMP DUTY CALCULATION TEST")
    print("="*70)
    
    # Test with stamp duty calculator
    calc = StampDutyCalculator()
    
    print("\n📊 Buyer's Stamp Duty (BSD) Test:")
    print("-" * 50)
    
    test_prices = [500000, 1000000, 1500000, 3000000, 5000000]
    
    for price in test_prices:
        bsd = calc.calculate_bsd(price)
        print(f"Property Price: ${price:,} → BSD: ${bsd:,.0f}")
    
    print("\n📊 Additional Buyer's Stamp Duty (ABSD) Test:")
    print("-" * 50)
    
    test_cases = [
        (1000000, "singapore_citizen", 0, "Citizen - 1st property"),
        (1000000, "singapore_citizen", 1, "Citizen - 2nd property"),
        (1000000, "singapore_citizen", 2, "Citizen - 3rd property"),
        (1000000, "pr", 0, "PR - 1st property"),
        (1000000, "foreigner", 0, "Foreigner"),
        (1000000, "entity", 0, "Company/Entity"),
    ]
    
    for price, profile, num_props, description in test_cases:
        absd = calc.calculate_absd(price, profile, num_props)
        rate = (absd / price * 100) if price > 0 else 0
        print(f"{description}: ${price:,} → ABSD: ${absd:,.0f} ({rate:.0f}%)")
    
    print("\n💬 Testing Through RAG System:")
    print("-" * 50)
    
    # Test through the RAG system
    engine = EnhancedRAGEngine()
    
    test_queries = [
        "Calculate stamp duty for $1,500,000 property",
        "What's the stamp duty for a foreigner buying $2,000,000 property?",
        "Stamp duty for PR buying 2nd property worth $1,000,000",
        "How much ABSD for $3,000,000 property as Singapore citizen first home?",
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        response = engine.query_with_metadata(query)
        
        # Extract key numbers from response
        answer_lines = response['answer'].split('\n')
        for line in answer_lines:
            if 'Total Stamp Duty' in line or 'BSD' in line or 'ABSD' in line:
                print(f"   {line.strip()}")
    
    print("\n" + "="*70)
    print("✅ STAMP DUTY TEST COMPLETE")
    print("="*70)


def test_complete_scenario():
    """Test complete property purchase scenario."""
    print("\n🏡 COMPLETE PROPERTY PURCHASE SCENARIO")
    print("-" * 50)
    
    engine = EnhancedRAGEngine()
    
    scenarios = [
        {
            'description': "First-time buyer (Citizen)",
            'query': "I'm a Singapore citizen buying my first property for $1.2 million. What's my stamp duty?"
        },
        {
            'description': "Second property (Citizen)",
            'query': "Singapore citizen buying 2nd property for $800,000. Calculate stamp duty."
        },
        {
            'description': "Foreign buyer",
            'query': "Foreigner buying $2.5 million condo. What's the total stamp duty?"
        },
        {
            'description': "Company purchase",
            'query': "Company buying $5 million property. Calculate stamp duty."
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📌 {scenario['description']}")
        print(f"Query: {scenario['query']}")
        
        response = engine.query_with_metadata(scenario['query'])
        
        # Show the calculation part
        answer_lines = response['answer'].split('\n')
        in_breakdown = False
        for line in answer_lines:
            if 'Stamp Duty Breakdown' in line:
                in_breakdown = True
            if in_breakdown and line.strip():
                print(f"  {line}")
            if 'Total Stamp Duty' in line:
                break


if __name__ == "__main__":
    test_stamp_duty()
    test_complete_scenario()