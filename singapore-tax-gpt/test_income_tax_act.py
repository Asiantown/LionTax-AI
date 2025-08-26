"""Test the Income Tax Act PDF specifically."""

from src.core.advanced_pdf_parser import IRASPDFParser
from src.core.enhanced_rag import EnhancedRAGEngine
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_income_tax_act():
    """Test parsing the Income Tax Act PDF."""
    pdf_path = "./data/iras_docs/Income Tax Act 1947.pdf"
    
    print("\n" + "="*60)
    print("TESTING: Income Tax Act 1947")
    print(f"File size: {Path(pdf_path).stat().st_size / 1024 / 1024:.2f} MB")
    print("="*60)
    
    # Initialize parser
    parser = IRASPDFParser()
    
    try:
        # Parse the PDF
        print("\n📄 Parsing Income Tax Act (this may take a moment)...")
        sections = parser.parse_pdf(pdf_path)
        
        print(f"\n✅ Successfully parsed {len(sections)} sections")
        
        # Analyze content types
        content_types = {}
        for section in sections:
            ct = section.section_type
            content_types[ct] = content_types.get(ct, 0) + 1
        
        print("\n📊 Content Analysis:")
        print("-" * 40)
        for content_type, count in content_types.items():
            print(f"  {content_type}: {count} sections")
        
        # Show some interesting sections
        print("\n📋 Sample Sections:")
        print("-" * 40)
        
        # Look for important sections
        for i, section in enumerate(sections[:10]):
            if section.section_number or 'tax' in section.title.lower():
                print(f"\nSection {i+1}:")
                if section.section_number:
                    print(f"  Number: {section.section_number}")
                print(f"  Title: {section.title[:80]}...")
                print(f"  Type: {section.section_type}")
                print(f"  Pages: {section.page_numbers[:5]}..." if len(section.page_numbers) > 5 else f"  Pages: {section.page_numbers}")
                
                # Show if it contains key information
                content_lower = section.content.lower()
                if 'rate' in content_lower:
                    print("  📈 Contains: Tax rates")
                if 'deduction' in content_lower or 'relief' in content_lower:
                    print("  💰 Contains: Deductions/Reliefs")
                if 'penalty' in content_lower:
                    print("  ⚠️ Contains: Penalties")
        
        # Find tables
        tables = [s for s in sections if s.metadata.get('is_table')]
        if tables:
            print(f"\n📊 Found {len(tables)} tables")
            for table in tables[:3]:
                print(f"  - Table on page {table.page_numbers[0]}")
        
        # Test with RAG
        print("\n🤖 Adding to RAG system...")
        engine = EnhancedRAGEngine()
        num_chunks = engine.add_pdf_document(pdf_path)
        print(f"✅ Added {num_chunks} chunks to vector store")
        
        # Test specific tax queries
        print("\n🔍 Testing Tax-Specific Queries:")
        print("-" * 40)
        
        test_queries = [
            "What are the tax rates for individuals?",
            "What constitutes taxable income?",
            "What are the penalties for non-payment?",
            "What deductions are allowed?"
        ]
        
        for query in test_queries:
            print(f"\nQ: {query}")
            response = engine.query_with_metadata(query)
            answer = response['answer'][:250] + "..." if len(response['answer']) > 250 else response['answer']
            print(f"A: {answer}")
            
            if response['citations']:
                citation = response['citations'][0]
                print(f"📖 Source: {citation['source']}")
                if citation['section_number']:
                    print(f"   Section: {citation['section_number']} - {citation['section']}")
                print(f"   Pages: {citation['pages']}")
        
        # Show document stats
        print("\n📈 Document Statistics:")
        print("-" * 40)
        total_pages = max(s.page_numbers[-1] for s in sections if s.page_numbers)
        print(f"  Total pages: {total_pages}")
        print(f"  Total sections: {len(sections)}")
        print(f"  Sections with numbers: {sum(1 for s in sections if s.section_number)}")
        print(f"  Tables found: {len(tables)}")
        
        print("\n" + "="*60)
        print("✅ INCOME TAX ACT PARSING COMPLETE!")
        print("="*60)
        
        return sections
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    sections = test_income_tax_act()
    
    if sections:
        print("\n💡 Summary:")
        print("The Income Tax Act has been successfully parsed and indexed!")
        print("The system can now answer questions about:")
        print("  • Tax rates and calculations")
        print("  • Deductions and reliefs")
        print("  • Penalties and compliance")
        print("  • Legal definitions and provisions")