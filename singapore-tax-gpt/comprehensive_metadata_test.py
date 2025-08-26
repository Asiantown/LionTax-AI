"""Comprehensive test of metadata extraction functionality."""

from src.core.metadata_extractor import MetadataExtractor
from src.core.advanced_pdf_parser import IRASPDFParser
from src.core.enhanced_rag import EnhancedRAGEngine
from src.core.smart_chunker import SmartTaxChunker
from pathlib import Path
import logging
from typing import Dict, List
from langchain.schema import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_metadata_extraction_comprehensive():
    """Comprehensive test of all metadata extraction features."""
    
    print("\n" + "="*70)
    print("🧪 COMPREHENSIVE METADATA EXTRACTION TEST")
    print("="*70)
    
    extractor = MetadataExtractor()
    test_results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # Test 1: Document Type Detection
    print("\n📝 TEST 1: Document Type Detection")
    print("-" * 50)
    
    test_docs = {
        'e-tax-guide': "IRAS e-Tax Guide\nIncome Tax Treatment",
        'circular': "IRAS Circular No. 2024/01\nTax Updates",
        'act': "Income Tax Act (Chapter 134)\nSection 1",
        'form': "IRAS Form IR8A\nEmployee Income Declaration",
        'order': "Income Tax (Exemption) Order 2024"
    }
    
    for expected_type, content in test_docs.items():
        metadata = extractor.extract_metadata(content)
        detected_type = metadata.document_type.replace('-', '_')
        
        if detected_type == expected_type.replace('-', '_'):
            print(f"  ✅ {expected_type}: Correctly identified")
            test_results['passed'].append(f"Document type: {expected_type}")
        else:
            print(f"  ❌ {expected_type}: Got '{detected_type}'")
            test_results['failed'].append(f"Document type: {expected_type}")
    
    # Test 2: Year of Assessment Extraction
    print("\n📅 TEST 2: Year of Assessment Extraction")
    print("-" * 50)
    
    ya_tests = [
        ("Year of Assessment 2024", ["2024"]),
        ("YA 2023 to 2025", ["2023", "2024", "2025"]),
        ("For YA2024 and YA2025", ["2024", "2025"]),
        ("Basis Year 2023", ["2023"])
    ]
    
    for content, expected_years in ya_tests:
        metadata = extractor.extract_metadata(content)
        if set(metadata.year_of_assessment) == set(expected_years):
            print(f"  ✅ '{content[:30]}...': {expected_years}")
            test_results['passed'].append(f"YA extraction: {expected_years}")
        else:
            print(f"  ❌ '{content[:30]}...': Expected {expected_years}, got {metadata.year_of_assessment}")
            test_results['failed'].append(f"YA extraction: {content[:30]}")
    
    # Test 3: Tax Category Classification
    print("\n🏷️ TEST 3: Tax Category Classification")
    print("-" * 50)
    
    category_tests = {
        'income': "Income Tax rates for individuals range from 0% to 24%",
        'gst': "GST rate is 9% for standard-rated supplies",
        'property': "Property Tax is calculated based on Annual Value",
        'corporate': "Corporate Tax rate is 17% for all companies",
        'stamp_duty': "Stamp Duty rates for property transactions"
    }
    
    for expected_cat, content in category_tests.items():
        metadata = extractor.extract_metadata(content)
        if metadata.tax_category == expected_cat:
            print(f"  ✅ {expected_cat}: Correctly classified")
            test_results['passed'].append(f"Category: {expected_cat}")
        else:
            print(f"  ❌ {expected_cat}: Got '{metadata.tax_category}'")
            test_results['failed'].append(f"Category: {expected_cat}")
    
    # Test 4: Date Extraction
    print("\n📆 TEST 4: Date Extraction")
    print("-" * 50)
    
    date_tests = [
        ("Last Updated: 15 January 2024", "last_updated", "15 January 2024"),
        ("Published: 1 March 2024", "publication_date", "1 March 2024"),
        ("Effective from: 1 April 2024", "effective_date", "1 April 2024")
    ]
    
    for content, date_field, expected_date in date_tests:
        metadata = extractor.extract_metadata(content)
        extracted_date = getattr(metadata, date_field)
        
        if extracted_date and expected_date in extracted_date:
            print(f"  ✅ {date_field}: '{expected_date}'")
            test_results['passed'].append(f"Date: {date_field}")
        else:
            print(f"  ❌ {date_field}: Expected '{expected_date}', got '{extracted_date}'")
            test_results['failed'].append(f"Date: {date_field}")
    
    # Test 5: Content Indicators
    print("\n📊 TEST 5: Content Indicators")
    print("-" * 50)
    
    content_with_table = """
    Tax Rates:
    | Income | Rate |
    |--------|------|
    | $20k   | 0%   |
    | $30k   | 2%   |
    """
    
    content_with_example = """
    Example 1: Mr. Tan earns $50,000 annually.
    His tax calculation would be as follows...
    """
    
    metadata_table = extractor.extract_metadata(content_with_table)
    metadata_example = extractor.extract_metadata(content_with_example)
    
    if metadata_table.has_tables:
        print(f"  ✅ Table detection: Working")
        test_results['passed'].append("Table detection")
    else:
        print(f"  ❌ Table detection: Failed")
        test_results['failed'].append("Table detection")
    
    if metadata_example.has_examples:
        print(f"  ✅ Example detection: Working")
        test_results['passed'].append("Example detection")
    else:
        print(f"  ❌ Example detection: Failed")
        test_results['failed'].append("Example detection")
    
    # Test 6: Rate and Relief Extraction
    print("\n💰 TEST 6: Rate and Relief Extraction")
    print("-" * 50)
    
    content_with_rates = """
    Tax rates: 0%, 2%, 3.5%, 7%, 11.5%, 15%, 18%, 20%, 22%, 24%
    GST is charged at 9%.
    """
    
    content_with_reliefs = """
    Available reliefs:
    - Earned Income Relief
    - Parent Relief
    - Child Relief
    - Spouse Relief
    """
    
    metadata_rates = extractor.extract_metadata(content_with_rates)
    metadata_reliefs = extractor.extract_metadata(content_with_reliefs)
    
    if len(metadata_rates.tax_rates_mentioned) >= 5:
        print(f"  ✅ Rate extraction: Found {len(metadata_rates.tax_rates_mentioned)} rates")
        test_results['passed'].append("Rate extraction")
    else:
        print(f"  ❌ Rate extraction: Only found {len(metadata_rates.tax_rates_mentioned)} rates")
        test_results['failed'].append("Rate extraction")
    
    if len(metadata_reliefs.reliefs_mentioned) >= 3:
        print(f"  ✅ Relief extraction: Found {len(metadata_reliefs.reliefs_mentioned)} reliefs")
        test_results['passed'].append("Relief extraction")
    else:
        print(f"  ❌ Relief extraction: Only found {len(metadata_reliefs.reliefs_mentioned)} reliefs")
        test_results['failed'].append("Relief extraction")
    
    # Test 7: Test on Real PDFs
    print("\n📄 TEST 7: Real PDF Processing")
    print("-" * 50)
    
    parser = IRASPDFParser()
    pdf_files = list(Path("./data/iras_docs").glob("*.pdf"))
    
    if pdf_files:
        for pdf_file in pdf_files[:2]:
            try:
                print(f"\n  Testing: {pdf_file.name}")
                sections = parser.parse_pdf(str(pdf_file))
                
                if sections:
                    # Combine first sections for metadata
                    sample_text = "\n".join([s.content[:500] for s in sections[:3]])
                    metadata = extractor.extract_metadata(sample_text, pdf_file.name)
                    
                    # Check key fields
                    checks = [
                        ('title', metadata.title != "Untitled Document"),
                        ('doc_type', metadata.document_type != "general"),
                        ('category', metadata.tax_category != "general"),
                        ('pages', len(sections) > 0)
                    ]
                    
                    for field, condition in checks:
                        if condition:
                            print(f"    ✅ {field}: Extracted")
                            test_results['passed'].append(f"PDF {field}")
                        else:
                            print(f"    ⚠️ {field}: Not extracted")
                            test_results['warnings'].append(f"PDF {field}")
                            
            except Exception as e:
                print(f"    ❌ Error: {e}")
                test_results['failed'].append(f"PDF processing: {pdf_file.name}")
    
    # Test 8: Integration with RAG
    print("\n🔗 TEST 8: RAG Integration")
    print("-" * 50)
    
    try:
        engine = EnhancedRAGEngine()
        chunker = SmartTaxChunker()
        
        test_content = """
        IRAS e-Tax Guide: GST
        Last Updated: 1 January 2024
        Year of Assessment 2024
        
        The GST rate is 9% from 1 January 2024.
        """
        
        metadata = extractor.extract_metadata(test_content)
        chunks = chunker.split_text(test_content)
        
        # Create document with metadata
        doc = Document(
            page_content=chunks[0] if chunks else test_content,
            metadata={
                'source': 'test_gst_guide.pdf',
                'document_type': metadata.document_type,
                'tax_category': metadata.tax_category,
                'year_of_assessment': ','.join(metadata.year_of_assessment),
                'last_updated': metadata.last_updated or '',
                'has_rates': bool(metadata.tax_rates_mentioned)
            }
        )
        
        engine.vectorstore.add_documents([doc])
        
        # Query and check if metadata is preserved
        response = engine.query_with_metadata("What is the GST rate?")
        
        if response['answer'] and '9%' in response['answer']:
            print(f"  ✅ RAG integration: Query answered correctly")
            test_results['passed'].append("RAG integration")
        else:
            print(f"  ❌ RAG integration: Query failed")
            test_results['failed'].append("RAG integration")
            
    except Exception as e:
        print(f"  ❌ RAG integration error: {e}")
        test_results['failed'].append("RAG integration")
    
    # Final Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    total_tests = len(test_results['passed']) + len(test_results['failed'])
    pass_rate = (len(test_results['passed']) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n✅ Passed: {len(test_results['passed'])} tests")
    print(f"❌ Failed: {len(test_results['failed'])} tests")
    print(f"⚠️ Warnings: {len(test_results['warnings'])} warnings")
    print(f"\n📈 Pass Rate: {pass_rate:.1f}%")
    
    if test_results['failed']:
        print("\n❌ Failed Tests:")
        for failure in test_results['failed']:
            print(f"  • {failure}")
    
    if pass_rate >= 80:
        print("\n🎉 METADATA EXTRACTION IS WORKING WELL!")
    elif pass_rate >= 60:
        print("\n⚠️ METADATA EXTRACTION NEEDS IMPROVEMENT")
    else:
        print("\n❌ METADATA EXTRACTION HAS ISSUES")
    
    return test_results


def test_metadata_performance():
    """Test performance of metadata extraction."""
    print("\n⚡ PERFORMANCE TEST")
    print("-" * 50)
    
    import time
    
    extractor = MetadataExtractor()
    
    # Create a large document
    large_doc = """
    IRAS e-Tax Guide: Comprehensive Income Tax
    Last Updated: 1 January 2024
    Year of Assessment 2024
    """ + "\n".join([f"Section {i}: Tax content..." for i in range(100)])
    
    start_time = time.time()
    metadata = extractor.extract_metadata(large_doc)
    extraction_time = time.time() - start_time
    
    print(f"  Document size: {len(large_doc)} characters")
    print(f"  Extraction time: {extraction_time:.3f} seconds")
    print(f"  Fields extracted: {sum(1 for field, value in metadata.__dict__.items() if value)}")
    
    if extraction_time < 1:
        print(f"  ✅ Performance: Excellent (<1s)")
    elif extraction_time < 3:
        print(f"  ⚠️ Performance: Acceptable (<3s)")
    else:
        print(f"  ❌ Performance: Slow (>3s)")


if __name__ == "__main__":
    # Run comprehensive tests
    results = test_metadata_extraction_comprehensive()
    
    # Run performance test
    test_metadata_performance()
    
    print("\n" + "="*70)
    print("✅ ALL METADATA TESTS COMPLETE")
    print("="*70)