"""Test metadata extraction on real IRAS documents."""

from src.core.metadata_extractor import MetadataExtractor, DocumentMetadata
from src.core.advanced_pdf_parser import IRASPDFParser
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_metadata_on_real_documents():
    """Test metadata extraction on real IRAS PDFs."""
    print("\n" + "="*60)
    print("TESTING METADATA EXTRACTION ON REAL DOCUMENTS")
    print("="*60)
    
    extractor = MetadataExtractor()
    parser = IRASPDFParser()
    
    # Test on available PDFs
    pdf_files = list(Path("./data/iras_docs").glob("*.pdf"))
    
    for pdf_file in pdf_files[:2]:  # Test first 2 PDFs
        print(f"\n📄 Processing: {pdf_file.name}")
        print("-" * 40)
        
        try:
            # Parse PDF
            sections = parser.parse_pdf(str(pdf_file))
            
            if sections:
                # Combine first few sections for metadata extraction
                sample_text = "\n\n".join([
                    f"{s.section_number or ''} {s.title}\n{s.content[:500]}"
                    for s in sections[:5]
                ])
                
                # Extract metadata
                metadata = extractor.extract_metadata(sample_text, pdf_file.name)
                
                # Add page count
                if sections:
                    metadata.pages = max(s.page_numbers[-1] for s in sections if s.page_numbers)
                
                # Display results
                print(extractor.format_metadata_summary(metadata))
                
                # Show additional details
                if metadata.sections:
                    print(f"\n   First 3 sections:")
                    for section in metadata.sections[:3]:
                        print(f"   - {section}")
                
                if metadata.reliefs_mentioned:
                    print(f"\n   Reliefs found: {', '.join(metadata.reliefs_mentioned[:5])}")
                
                if metadata.act_references:
                    print(f"\n   Act references: {', '.join(metadata.act_references[:3])}")
                
                if metadata.keywords:
                    print(f"\n   Keywords: {', '.join(metadata.keywords[:7])}")
        
        except Exception as e:
            print(f"   Error: {e}")
    
    # Test on text documents
    print("\n📄 Testing on text documents:")
    print("-" * 40)
    
    text_files = list(Path("./data/iras_docs").glob("*.txt"))[:3]
    
    for text_file in text_files:
        with open(text_file, 'r') as f:
            content = f.read()
        
        metadata = extractor.extract_metadata(content, text_file.name)
        print(f"\n{text_file.name}:")
        print(f"  Type: {metadata.document_type}")
        print(f"  Category: {metadata.tax_category}")
        
        if metadata.year_of_assessment:
            print(f"  YA: {', '.join(metadata.year_of_assessment)}")
        
        if metadata.tax_rates_mentioned:
            print(f"  Rates: {', '.join(metadata.tax_rates_mentioned[:3])}")
    
    print("\n" + "="*60)
    print("✅ METADATA EXTRACTION TEST COMPLETE")
    print("="*60)


def demonstrate_metadata_usage():
    """Show how metadata improves retrieval."""
    print("\n📊 METADATA USAGE DEMONSTRATION")
    print("-" * 40)
    
    print("\nScenario: User asks 'What are the GST rates for 2024?'")
    print("\nWithout Metadata:")
    print("  • Search through ALL documents")
    print("  • May retrieve income tax documents")
    print("  • Slower and less accurate")
    
    print("\nWith Metadata:")
    print("  • Filter: tax_category='gst'")
    print("  • Filter: year_of_assessment contains '2024'")
    print("  • Search only relevant GST documents")
    print("  • Faster and more accurate results")
    
    print("\n💡 Metadata enables:")
    print("  • Filtered search by category/year")
    print("  • Document versioning awareness")
    print("  • Better citation with dates")
    print("  • Compliance tracking (which docs are current)")
    print("  • Smart routing based on query type")


if __name__ == "__main__":
    test_metadata_on_real_documents()
    demonstrate_metadata_usage()