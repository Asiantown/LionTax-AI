"""Test integration of tax calculator with RAG system."""

import os
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from src.core.enhanced_rag import EnhancedRAGEngine
from src.core.calculation_handler import CalculationHandler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_calculation_integration():
    """Test calculation integration with RAG."""
    print("\n" + "="*70)
    print("🧮 TAX CALCULATION + RAG INTEGRATION TEST")
    print("="*70)
    
    # Initialize components
    engine = EnhancedRAGEngine()
    calc_handler = CalculationHandler()
    
    # Test queries that should trigger calculations
    calculation_queries = [
        "How much tax do I pay on $100,000 income?",
        "Calculate tax for $80,000 salary with spouse relief",
        "What is my take home pay for $120,000 annual income?",
        "Add GST to $1000",
        "Calculate property tax for $100,000 annual value",
        "How much CPF for $5000 monthly salary age 35?",
        "What's the tax on $150,000 for non-resident?",
    ]
    
    print("\n📊 Testing Calculation Queries:")
    print("-" * 50)
    
    for i, query in enumerate(calculation_queries, 1):
        print(f"\n{i}. Query: {query}")
        
        # Test if calculation is detected
        should_calc = calc_handler.should_calculate(query)
        print(f"   Should calculate: {should_calc}")
        
        if should_calc:
            # Extract parameters
            params = calc_handler.extract_calculation_params(query)
            print(f"   Type: {params['type']}")
            print(f"   Amount: ${params.get('amount', 0):,.0f}" if params.get('amount') else "   Amount: Not found")
            
            # Get response through RAG engine
            response = engine.query_with_metadata(query)
            
            # Check if calculation was used
            if response.get('metadata', {}).get('used_calculator'):
                print("   ✅ Calculator used")
                # Show first part of answer
                answer_preview = response['answer'].split('\n')[0]
                print(f"   Result: {answer_preview}")
            else:
                print("   ❌ Calculator not triggered")
    
    # Test mixed queries (should use both RAG and calculator)
    print("\n\n📚 Testing Mixed Queries (RAG + Calculation):")
    print("-" * 50)
    
    mixed_queries = [
        "What are the tax rates and how much tax for $100,000?",
        "Explain GST and calculate GST on $500",
    ]
    
    for query in mixed_queries:
        print(f"\n❓ Query: {query}")
        response = engine.query_with_metadata(query)
        
        # Show response type
        if response.get('metadata', {}).get('used_calculator'):
            print("   Type: Calculation Response")
        else:
            print("   Type: RAG Response")
        
        # Show preview
        answer_lines = response['answer'].split('\n')[:3]
        print("   Answer preview:")
        for line in answer_lines:
            if line.strip():
                print(f"   {line}")
    
    # Test parameter extraction
    print("\n\n🔍 Testing Parameter Extraction:")
    print("-" * 50)
    
    test_cases = [
        ("Tax on $85,000 with $2000 spouse relief and $4000 child relief", 
         {'amount': 85000, 'reliefs': {'spouse': 2000, 'child': 4000}}),
        ("Calculate tax for age 60 earning $100,000",
         {'amount': 100000, 'age': 60}),
        ("Non-resident tax on $150,000",
         {'amount': 150000, 'is_resident': False}),
    ]
    
    for query, expected in test_cases:
        print(f"\n Query: {query}")
        params = calc_handler.extract_calculation_params(query)
        
        # Check amount
        if params.get('amount') == expected.get('amount'):
            print(f"   ✅ Amount: ${params['amount']:,.0f}")
        else:
            print(f"   ❌ Amount: Expected ${expected.get('amount', 0):,.0f}, got ${params.get('amount', 0):,.0f}")
        
        # Check other params
        if 'age' in expected:
            print(f"   Age: {params.get('age')} (expected {expected['age']})")
        
        if 'is_resident' in expected:
            print(f"   Resident: {params.get('is_resident')} (expected {expected['is_resident']})")
        
        if 'reliefs' in expected:
            print(f"   Reliefs: {params.get('reliefs')}")
    
    print("\n" + "="*70)
    print("✅ CALCULATION INTEGRATION TEST COMPLETE")
    print("="*70)
    
    print("\n🎯 Integration Features:")
    print("  • Automatic calculation detection")
    print("  • Parameter extraction from natural language")
    print("  • Seamless RAG + Calculator responses")
    print("  • Support for complex queries with reliefs")
    print("  • Age and residency status handling")


if __name__ == "__main__":
    test_calculation_integration()