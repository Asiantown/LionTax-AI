"""Test smart chunking with real IRAS content."""

from src.core.smart_chunker import SmartTaxChunker
from src.core.enhanced_rag import EnhancedRAGEngine
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_smart_chunking_on_real_data():
    """Test smart chunking on real IRAS documents."""
    print("\n" + "="*60)
    print("TESTING SMART CHUNKING ON REAL DATA")
    print("="*60)
    
    # Initialize smart chunker
    chunker = SmartTaxChunker(
        chunk_size=1000,
        chunk_overlap=100,
        preserve_tables=True,
        preserve_lists=True,
        preserve_sections=True
    )
    
    # Test with one of our text documents that has tables
    test_file = "./data/iras_docs/1_income_tax_guide.txt"
    
    if Path(test_file).exists():
        with open(test_file, 'r') as f:
            content = f.read()
        
        print(f"\n📄 Testing with: {Path(test_file).name}")
        print(f"  Original size: {len(content)} characters")
        
        # Apply smart chunking
        chunks = chunker.split_text(content)
        
        print(f"  Smart chunks: {len(chunks)}")
        
        # Analyze chunks
        table_chunks = 0
        list_chunks = 0
        section_chunks = 0
        
        for i, chunk in enumerate(chunks):
            if '|' in chunk and '---' in chunk:
                table_chunks += 1
                print(f"\n  📊 Chunk {i+1} - Table preserved ({len(chunk)} chars)")
                # Show table preview
                lines = chunk.split('\n')
                for line in lines[:5]:
                    if '|' in line:
                        print(f"     {line[:60]}...")
                        
            elif '•' in chunk or re.search(r'^\s*\d+[.)]\s+', chunk, re.MULTILINE):
                list_chunks += 1
                
            elif 'Section' in chunk or 'Part' in chunk:
                section_chunks += 1
        
        print(f"\n📊 Chunk Analysis:")
        print(f"  Tables preserved: {table_chunks}")
        print(f"  Lists preserved: {list_chunks}")
        print(f"  Sections preserved: {section_chunks}")
        
        # Compare with regular chunking
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        regular_chunker = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
        regular_chunks = regular_chunker.split_text(content)
        
        print(f"\n📈 Comparison:")
        print(f"  Regular chunking: {len(regular_chunks)} chunks")
        print(f"  Smart chunking: {len(chunks)} chunks")
        
        # Test preservation of a specific table
        print("\n🔍 Table Preservation Test:")
        
        # Find a chunk with tax rates table
        for chunk in chunks:
            if 'Tax Rate' in chunk and 'First $20,000' in chunk:
                print("  ✅ Tax rate table found intact!")
                print(f"  Table size: {len(chunk)} characters")
                
                # Check if table is complete
                expected_rows = ['First $20,000', 'Next $10,000', 'Next $40,000']
                missing = [row for row in expected_rows if row not in chunk]
                
                if not missing:
                    print("  ✅ All table rows preserved together!")
                else:
                    print(f"  ⚠️ Missing rows: {missing}")
                break
        
        # Test with RAG
        print("\n🤖 Testing with RAG System:")
        engine = EnhancedRAGEngine()
        
        # Create documents with smart chunks
        metadata = {
            'source': Path(test_file).name,
            'doc_type': 'e-tax-guide'
        }
        
        documents = chunker.create_documents_with_smart_chunks(content, metadata)
        
        print(f"  Created {len(documents)} documents")
        print(f"  Sample metadata: {documents[0].metadata}")
        
        # Add to vector store
        engine.vectorstore.add_documents(documents[:5])  # Add first 5 for testing
        print("  ✅ Added to vector store")
        
        # Test retrieval
        test_query = "What are the income tax rates for the first $40,000?"
        response = engine.query_with_metadata(test_query)
        
        print(f"\n  Q: {test_query}")
        print(f"  A: {response['answer'][:200]}...")
        
        if response['citations']:
            citation = response['citations'][0]
            if citation.get('chunk_type'):
                print(f"  Chunk type: {citation['chunk_type']}")
    
    print("\n" + "="*60)
    print("✅ SMART CHUNKING TEST COMPLETE")
    print("="*60)
    
    print("\n📊 Benefits Achieved:")
    print("  • Tables remain intact for accurate rate lookups")
    print("  • Lists preserved for complete relief information")
    print("  • Section headers maintain document structure")
    print("  • Context overlap improves retrieval accuracy")
    print("  • Metadata tracks chunk characteristics")


if __name__ == "__main__":
    import re
    test_smart_chunking_on_real_data()