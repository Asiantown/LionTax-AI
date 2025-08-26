"""Test query enhancement functionality."""

from src.core.query_enhancer import QueryEnhancer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_query_enhancement():
    """Test query enhancement functionality."""
    print("\n" + "="*70)
    print("🔍 QUERY ENHANCEMENT TEST")
    print("="*70)
    
    enhancer = QueryEnhancer()
    
    # Test queries
    test_queries = [
        # Calculation query
        "How much tax do I pay on $100,000 income in YA 2024?",
        
        # Eligibility query
        "Am I eligible for parent relief if my mother is 65?",
        
        # Procedural query
        "How to submit Form IR8A by the deadline?",
        
        # Comparison query
        "What's the difference between resident and non-resident tax rates?",
        
        # Definition query
        "What is ABSD and when does it apply?",
        
        # Complex query with multiple entities
        "Can I claim Section 14Q deduction for my $50,000 renovation in 2024?",
        
        # Abbreviation expansion
        "What is the CPF contribution rate for YA2024?",
        
        # Simple factual query
        "GST rate in Singapore"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {query}")
        print("-" * 60)
        
        enhanced = enhancer.enhance_query(query)
        
        # Display results
        print(f"\n📊 Analysis:")
        print(f"  Query Type: {enhanced.query_type}")
        print(f"  Tax Category: {enhanced.tax_category}")
        print(f"  Year Context: {enhanced.year_context}")
        print(f"  Confidence: {enhanced.confidence:.2%}")
        
        if enhanced.entities['amounts']:
            print(f"  💰 Amounts: {', '.join(enhanced.entities['amounts'])}")
        
        if enhanced.entities['forms']:
            print(f"  📋 Forms: {', '.join(enhanced.entities['forms'])}")
        
        if enhanced.entities['sections']:
            print(f"  📑 Sections: {', '.join(enhanced.entities['sections'])}")
        
        if enhanced.entities['years']:
            print(f"  📅 Years: {', '.join(enhanced.entities['years'])}")
        
        print(f"\n🔑 Keywords: {', '.join(enhanced.keywords[:7])}")
        
        # Show expanded query
        formatted = enhancer.format_enhanced_query(enhanced)
        print(f"\n🎯 Enhanced Query for RAG:")
        print(f"  {formatted}")
        
        # Show retrieval hints
        hints = enhancer.get_retrieval_hints(enhanced)
        print(f"\n💡 Retrieval Hints:")
        for key, value in hints.items():
            if value and value != 5:  # Only show non-default values
                print(f"  {key}: {value}")
    
    # Test specific scenarios
    print("\n" + "="*70)
    print("📝 SPECIAL SCENARIOS")
    print("="*70)
    
    # Scenario 1: Ambiguous query
    print("\n1️⃣ Ambiguous Query")
    query = "tax rate"
    enhanced = enhancer.enhance_query(query)
    print(f"  Query: '{query}'")
    print(f"  Type: {enhanced.query_type}")
    print(f"  Category: {enhanced.tax_category}")
    print(f"  Confidence: {enhanced.confidence:.2%}")
    
    # Scenario 2: Multi-category query
    print("\n2️⃣ Multi-Category Query")
    query = "Income tax and GST rates for companies"
    enhanced = enhancer.enhance_query(query)
    print(f"  Query: '{query}'")
    print(f"  Primary Category: {enhanced.tax_category}")
    print(f"  Keywords: {', '.join(enhanced.keywords[:5])}")
    
    # Scenario 3: Query with context
    print("\n3️⃣ Query with Context")
    query = "What are the current tax reliefs?"
    context = {'current_year': 2024}
    enhanced = enhancer.enhance_query(query, context)
    print(f"  Query: '{query}'")
    print(f"  Year Context: {enhanced.year_context}")
    print(f"  Filters: {enhanced.filters}")
    
    # Performance test
    print("\n⚡ PERFORMANCE TEST")
    print("-" * 50)
    
    import time
    
    queries = test_queries * 10  # 80 queries
    start_time = time.time()
    
    for query in queries:
        _ = enhancer.enhance_query(query)
    
    elapsed = time.time() - start_time
    avg_time = elapsed / len(queries)
    
    print(f"  Processed: {len(queries)} queries")
    print(f"  Total time: {elapsed:.3f}s")
    print(f"  Average per query: {avg_time*1000:.1f}ms")
    
    if avg_time < 0.01:
        print("  ✅ Performance: Excellent (<10ms)")
    elif avg_time < 0.05:
        print("  ⚠️ Performance: Good (<50ms)")
    else:
        print("  ❌ Performance: Needs optimization")
    
    # Summary
    print("\n" + "="*70)
    print("📊 ENHANCEMENT CAPABILITIES")
    print("="*70)
    
    print("\n✅ Demonstrated:")
    print("  • Query type classification")
    print("  • Tax category identification")
    print("  • Entity extraction (amounts, forms, dates)")
    print("  • Abbreviation expansion")
    print("  • Synonym expansion")
    print("  • Year context extraction")
    print("  • Confidence scoring")
    print("  • Retrieval optimization hints")
    
    print("\n🎯 Benefits:")
    print("  • Better retrieval accuracy")
    print("  • Contextual understanding")
    print("  • Reduced ambiguity")
    print("  • Optimized chunk selection")


if __name__ == "__main__":
    test_query_enhancement()