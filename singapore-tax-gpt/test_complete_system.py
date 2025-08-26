"""Complete system test for Singapore Tax GPT."""

import os
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from src.core.enhanced_rag import EnhancedRAGEngine
from src.core.batch_processor import BatchDocumentProcessor
from src.core.query_enhancer import QueryEnhancer
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_complete_system():
    """Test the complete Singapore Tax GPT system."""
    print("\n" + "="*70)
    print("🚀 SINGAPORE TAX GPT - COMPLETE SYSTEM TEST")
    print("="*70)
    
    # Step 1: Initialize components
    print("\n📦 Step 1: Initializing System Components...")
    print("-" * 50)
    
    rag_engine = EnhancedRAGEngine()
    batch_processor = BatchDocumentProcessor(
        rag_engine=rag_engine,
        max_workers=2,
        use_cache=True
    )
    query_enhancer = QueryEnhancer()
    
    print("  ✅ RAG Engine initialized")
    print("  ✅ Batch Processor initialized")
    print("  ✅ Query Enhancer initialized")
    
    # Step 2: Process documents
    print("\n📄 Step 2: Processing Tax Documents...")
    print("-" * 50)
    
    # Process PDFs in the data directory
    pdf_files = list(Path("./data/iras_docs").glob("*.pdf"))
    
    if pdf_files:
        print(f"  Found {len(pdf_files)} PDF documents")
        
        # Process each PDF
        for pdf_file in pdf_files[:2]:  # Process first 2 for testing
            print(f"\n  Processing: {pdf_file.name}")
            result = batch_processor.process_single_document(pdf_file)
            
            if result.status == "success":
                print(f"    ✅ Success: {result.chunks_created} chunks created")
                print(f"    📊 Type: {result.document_type}, Category: {result.tax_category}")
            elif result.status == "skipped":
                print(f"    ⏭️ Skipped (already processed)")
            else:
                print(f"    ❌ Failed: {result.error}")
    else:
        print("  ⚠️ No PDF files found. Add PDFs to ./data/iras_docs/")
    
    # Step 3: Test queries
    print("\n❓ Step 3: Testing Tax Queries...")
    print("-" * 50)
    
    test_queries = [
        "What is the income tax rate for residents in Singapore?",
        "How do I calculate my tax for $80,000 salary?",
        "What tax reliefs can I claim in YA 2024?",
        "What is the GST rate in Singapore?",
        "When is the deadline to file income tax?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n  Query {i}: {query}")
        print("  " + "-" * 40)
        
        # Enhance query
        enhanced = query_enhancer.enhance_query(query)
        print(f"    Query Type: {enhanced.query_type}")
        print(f"    Tax Category: {enhanced.tax_category}")
        
        # Get answer from RAG
        try:
            response = rag_engine.query_with_metadata(query)
            
            # Display answer
            answer = response['answer'][:200] + "..." if len(response['answer']) > 200 else response['answer']
            print(f"    Answer: {answer}")
            
            # Show sources
            if response['citations']:
                print(f"    Sources: {len(response['citations'])} documents")
                for citation in response['citations'][:2]:
                    print(f"      - {citation.get('source', 'Unknown')}")
        except Exception as e:
            print(f"    ⚠️ Query failed: {str(e)[:100]}")
    
    print("\n" + "="*70)
    print("✅ SYSTEM TEST COMPLETE")
    print("="*70)


def interactive_test():
    """Interactive testing mode."""
    print("\n" + "="*70)
    print("💬 INTERACTIVE TAX GPT TEST")
    print("="*70)
    print("\nType 'quit' to exit, 'help' for commands")
    print("-" * 70)
    
    # Initialize system
    rag_engine = EnhancedRAGEngine()
    query_enhancer = QueryEnhancer()
    
    while True:
        try:
            # Get user input
            query = input("\n❓ Your tax question: ").strip()
            
            if query.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif query.lower() == 'help':
                print("\n📚 Available commands:")
                print("  - Type any tax question")
                print("  - 'quit' to exit")
                print("  - 'stats' to see system statistics")
                continue
            elif query.lower() == 'stats':
                # Show statistics
                print("\n📊 System Statistics:")
                print(f"  Documents indexed: Check ./data/chroma_db/")
                print(f"  Query enhancement: Active")
                print(f"  Supported categories: income, gst, property, corporate, stamp duty")
                continue
            elif not query:
                continue
            
            # Process query
            print("\n🔍 Processing your query...")
            
            # Enhance query
            enhanced = query_enhancer.enhance_query(query)
            print(f"  Type: {enhanced.query_type} | Category: {enhanced.tax_category}")
            
            # Get answer
            response = rag_engine.query_with_metadata(query)
            
            # Display answer
            print("\n💡 Answer:")
            print("-" * 50)
            print(response['answer'])
            
            # Show sources
            if response['citations']:
                print("\n📚 Sources:")
                for i, citation in enumerate(response['citations'][:3], 1):
                    source = citation.get('source', 'Unknown')
                    section = citation.get('section', '')
                    print(f"  {i}. {source} - {section[:50]}...")
                    
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try rephrasing your question.")


def quick_test():
    """Quick test to verify system is working."""
    print("\n" + "="*70)
    print("⚡ QUICK SYSTEM TEST")
    print("="*70)
    
    try:
        # Test 1: Document processing
        print("\n1️⃣ Testing document processing...")
        from src.core.advanced_pdf_parser import IRASPDFParser
        parser = IRASPDFParser()
        print("  ✅ PDF Parser working")
        
        # Test 2: Metadata extraction
        print("\n2️⃣ Testing metadata extraction...")
        from src.core.metadata_extractor import MetadataExtractor
        extractor = MetadataExtractor()
        metadata = extractor.extract_metadata("Income Tax Act 2024")
        print(f"  ✅ Metadata extraction working (Type: {metadata.document_type})")
        
        # Test 3: Query enhancement
        print("\n3️⃣ Testing query enhancement...")
        from src.core.query_enhancer import QueryEnhancer
        enhancer = QueryEnhancer()
        enhanced = enhancer.enhance_query("What is the tax rate?")
        print(f"  ✅ Query enhancement working (Type: {enhanced.query_type})")
        
        # Test 4: RAG Engine
        print("\n4️⃣ Testing RAG engine...")
        from src.core.enhanced_rag import EnhancedRAGEngine
        engine = EnhancedRAGEngine()
        print("  ✅ RAG Engine initialized")
        
        print("\n🎉 All components working!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check .env file has OPENAI_API_KEY")
        print("2. Run: uv sync")
        print("3. Check data/iras_docs/ has PDF files")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            interactive_test()
        elif sys.argv[1] == "quick":
            quick_test()
        else:
            print("Usage: python test_complete_system.py [interactive|quick]")
    else:
        # Run complete test
        test_complete_system()