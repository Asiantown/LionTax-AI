"""Simple test script to verify Singapore Tax GPT is working."""

import os
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

print("\n" + "="*70)
print("🇸🇬 SINGAPORE TAX GPT - SIMPLE TEST")
print("="*70)

try:
    # Import components
    from src.core.enhanced_rag import EnhancedRAGEngine
    from src.core.query_enhancer import QueryEnhancer
    
    print("\n✅ Imports successful")
    
    # Initialize
    print("\n📦 Initializing components...")
    engine = EnhancedRAGEngine()
    enhancer = QueryEnhancer()
    print("✅ Components initialized")
    
    # Test query enhancement
    print("\n🔍 Testing query enhancement...")
    query = "What is the income tax rate for $80,000?"
    enhanced = enhancer.enhance_query(query)
    print(f"  Query type: {enhanced.query_type}")
    print(f"  Tax category: {enhanced.tax_category}")
    print(f"  Confidence: {enhanced.confidence:.0%}")
    
    # Test RAG query
    print("\n💬 Testing RAG query...")
    print(f"  Question: {query}")
    
    response = engine.query_with_metadata(query)
    
    # Show answer
    answer = response['answer'][:200] + "..." if len(response['answer']) > 200 else response['answer']
    print(f"\n  Answer: {answer}")
    
    # Show sources
    if response['citations']:
        print(f"\n  Sources found: {len(response['citations'])}")
        for citation in response['citations'][:2]:
            print(f"    - {citation.get('source', 'Unknown')}")
    
    print("\n" + "="*70)
    print("🎉 SYSTEM IS WORKING!")
    print("="*70)
    
    print("\n📚 Next steps:")
    print("1. Run the Streamlit UI: uv run streamlit run app.py")
    print("2. Add more PDF documents to ./data/iras_docs/")
    print("3. Try the interactive mode: uv run python test_complete_system.py interactive")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check your .env file has OPENAI_API_KEY")
    print("2. Run: uv sync")
    print("3. Make sure you have PDFs in ./data/iras_docs/")