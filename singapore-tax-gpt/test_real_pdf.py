"""Test the PDF parser with a real IRAS PDF."""

import os
from pathlib import Path
from src.core.advanced_pdf_parser import IRASPDFParser
from src.core.enhanced_rag import EnhancedRAGEngine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_real_pdf(pdf_path: str):
    """Test parsing a real PDF file."""
    print("\n" + "="*60)
    print(f"TESTING REAL PDF: {Path(pdf_path).name}")
    print("="*60)
    
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        print("\nPlease download an IRAS PDF and save it to:")
        print(f"  {pdf_path}")
        print("\nYou can download PDFs from:")
        print("  https://www.iras.gov.sg/quick-links/e-tax-guides")
        return
    
    # Initialize parser
    parser = IRASPDFParser()
    
    try:
        # Parse the PDF
        print("\n📄 Parsing PDF...")
        sections = parser.parse_pdf(pdf_path)
        
        print(f"\n✅ Successfully parsed {len(sections)} sections")
        
        # Show first 5 sections
        print("\n📋 Section Details:")
        print("-" * 40)
        
        for i, section in enumerate(sections[:5], 1):
            print(f"\nSection {i}:")
            print(f"  Type: {section.section_type}")
            if section.section_number:
                print(f"  Number: {section.section_number}")
            print(f"  Title: {section.title[:60]}...")
            print(f"  Pages: {section.page_numbers}")
            print(f"  Content preview: {section.content[:150]}...")
            
            # Show if it's a table
            if section.metadata.get('is_table'):
                print(f"  📊 Table with headers: {section.metadata.get('table_headers', [])}")
        
        # Show metadata extracted
        print("\n📊 Document Metadata:")
        print("-" * 40)
        if sections:
            first_section = sections[0]
            print(f"  File: {first_section.metadata.get('file_name', 'Unknown')}")
            print(f"  Type: {first_section.metadata.get('doc_type', 'Unknown')}")
            print(f"  Title: {first_section.metadata.get('title', 'Unknown')}")
            print(f"  Pages: {first_section.metadata.get('total_pages', 'Unknown')}")
            print(f"  Year: {first_section.metadata.get('year_assessment', 'Not found')}")
            print(f"  Updated: {first_section.metadata.get('last_updated', 'Not found')}")
        
        # Test with RAG engine
        print("\n🤖 Testing with RAG Engine...")
        engine = EnhancedRAGEngine()
        
        # Add the PDF to vector store
        num_chunks = engine.add_pdf_document(pdf_path)
        print(f"✅ Added {num_chunks} chunks to vector store")
        
        # Test some queries
        print("\n🔍 Testing Queries:")
        print("-" * 40)
        
        test_queries = [
            "What are the main topics in this document?",
            "What tax rates are mentioned?",
            "Are there any important deadlines mentioned?"
        ]
        
        for query in test_queries:
            print(f"\nQ: {query}")
            response = engine.query_with_metadata(query)
            print(f"A: {response['answer'][:200]}...")
            
            if response['citations']:
                print(f"Sources: {response['citations'][0]['source']}")
                if response['citations'][0]['section_number']:
                    print(f"Section: {response['citations'][0]['section_number']} - {response['citations'][0]['section']}")
        
        print("\n" + "="*60)
        print("✅ PDF PARSING TEST COMPLETE!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error parsing PDF: {e}")
        print("\nThis might happen if:")
        print("  1. The PDF is scanned (image-based, not text)")
        print("  2. The PDF has complex encryption")
        print("  3. The PDF structure is unusual")
        print("\nTry with a different IRAS e-Tax Guide PDF")


def list_available_pdfs():
    """List any PDFs already in the data directory."""
    pdf_dir = Path("./data/iras_docs")
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if pdf_files:
        print("\n📁 Available PDFs in data/iras_docs:")
        for pdf in pdf_files:
            print(f"  • {pdf.name}")
        return pdf_files
    else:
        print("\n📁 No PDFs found in data/iras_docs/")
        print("\nTo test, download an IRAS PDF and save it to:")
        print("  ./data/iras_docs/")
        return []


if __name__ == "__main__":
    print("🔍 REAL PDF PARSER TEST")
    
    # Check for existing PDFs
    pdfs = list_available_pdfs()
    
    if pdfs:
        # Test with the first available PDF
        test_pdf = str(pdfs[0])
        print(f"\n🧪 Testing with: {pdfs[0].name}")
        test_real_pdf(test_pdf)
    else:
        # Provide instructions for getting a PDF
        print("\n📥 How to test with a real PDF:")
        print("1. Download any IRAS e-Tax Guide from:")
        print("   https://www.iras.gov.sg/taxes/individual-income-tax")
        print("   https://www.iras.gov.sg/taxes/goods-services-tax-(gst)")
        print("\n2. Save it to: ./data/iras_docs/")
        print("\n3. Run this script again: uv run python test_real_pdf.py")
        
        # Try to test with a placeholder path
        test_path = "./data/iras_docs/sample_iras_guide.pdf"
        print(f"\n📋 Or specify a path directly in the script")
        print(f"   Current test path: {test_path}")
        test_real_pdf(test_path)