"""Test document classification functionality."""

from src.core.document_classifier import DocumentClassifier, DocumentType, TaxCategory
from src.core.advanced_pdf_parser import IRASPDFParser
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_document_classifier():
    """Test document classification on various document types."""
    print("\n" + "="*70)
    print("🔍 DOCUMENT CLASSIFIER TEST")
    print("="*70)
    
    classifier = DocumentClassifier()
    test_results = {
        'passed': [],
        'failed': []
    }
    
    # Test 1: E-Tax Guide Classification
    print("\n📚 TEST 1: E-Tax Guide Classification")
    print("-" * 50)
    
    etax_guide_text = """
    IRAS e-Tax Guide
    GST: Major Exporter Scheme
    First published: 28 February 2013
    Last updated: 1 January 2024
    
    This e-tax guide provides guidance on the application of GST
    to major exporters under the Major Exporter Scheme.
    """
    
    result = classifier.classify(
        text=etax_guide_text,
        filename="gst_major_exporter_etax_guide.pdf",
        title="IRAS e-Tax Guide: GST Major Exporter Scheme"
    )
    
    if result.document_type == DocumentType.E_TAX_GUIDE:
        print(f"  ✅ Document type: {result.document_type.value}")
        test_results['passed'].append("E-Tax Guide classification")
    else:
        print(f"  ❌ Document type: Expected e-tax-guide, got {result.document_type.value}")
        test_results['failed'].append("E-Tax Guide classification")
    
    if result.tax_category == TaxCategory.GST:
        print(f"  ✅ Tax category: {result.tax_category.value}")
        test_results['passed'].append("GST category")
    else:
        print(f"  ❌ Tax category: Expected gst, got {result.tax_category.value}")
        test_results['failed'].append("GST category")
    
    print(f"  📊 Confidence: {result.confidence:.2%}")
    print(f"  🏷️ Sub-type: {result.sub_type}")
    print(f"  🔑 Keywords: {', '.join(result.keywords_found[:5])}")
    
    # Test 2: Income Tax Act Classification
    print("\n⚖️ TEST 2: Income Tax Act Classification")
    print("-" * 50)
    
    act_text = """
    INCOME TAX ACT
    (CHAPTER 134)
    
    An Act to impose a tax upon incomes and to regulate the
    collection thereof.
    
    PART I
    PRELIMINARY
    
    1. This Act may be cited as the Income Tax Act.
    
    2. In this Act, unless the context otherwise requires—
    "assessment" means an assessment made under this Act;
    """
    
    result = classifier.classify(
        text=act_text,
        filename="Income_Tax_Act_Chapter_134.pdf",
        title="Income Tax Act (Chapter 134)"
    )
    
    if result.document_type == DocumentType.ACT:
        print(f"  ✅ Document type: {result.document_type.value}")
        test_results['passed'].append("Act classification")
    else:
        print(f"  ❌ Document type: Expected act, got {result.document_type.value}")
        test_results['failed'].append("Act classification")
    
    if result.tax_category == TaxCategory.INCOME_TAX:
        print(f"  ✅ Tax category: {result.tax_category.value}")
        test_results['passed'].append("Income tax category")
    else:
        print(f"  ❌ Tax category: Expected income, got {result.tax_category.value}")
        test_results['failed'].append("Income tax category")
    
    print(f"  📊 Confidence: {result.confidence:.2%}")
    print(f"  🔑 Keywords: {', '.join(result.keywords_found[:5])}")
    
    # Test 3: Tax Form Classification
    print("\n📋 TEST 3: Tax Form Classification")
    print("-" * 50)
    
    form_text = """
    FORM IR8A
    APPENDIX 8A
    
    STATEMENT OF EMPLOYMENT INCOME FOR THE YEAR ENDED 31 DEC 2023
    
    Employee Name: _________________
    NRIC/FIN: _________________
    
    Please complete and submit this form to IRAS by 1 March 2024.
    """
    
    result = classifier.classify(
        text=form_text,
        filename="IR8A_2023.pdf",
        title="Form IR8A - Employment Income Declaration"
    )
    
    if result.document_type == DocumentType.FORM:
        print(f"  ✅ Document type: {result.document_type.value}")
        test_results['passed'].append("Form classification")
    else:
        print(f"  ❌ Document type: Expected form, got {result.document_type.value}")
        test_results['failed'].append("Form classification")
    
    print(f"  📊 Confidence: {result.confidence:.2%}")
    print(f"  🏷️ Sub-type: {result.sub_type}")
    
    # Test 4: Circular Classification
    print("\n📮 TEST 4: Circular Classification")
    print("-" * 50)
    
    circular_text = """
    IRAS CIRCULAR NO. 2024/01
    
    DATE: 15 January 2024
    
    SUBJECT: Clarification on Tax Treatment of Digital Assets
    
    This circular clarifies IRAS's position on the income tax
    treatment of gains from disposal of digital assets.
    """
    
    result = classifier.classify(
        text=circular_text,
        filename="IRAS_Circular_2024_01.pdf",
        title="IRAS Circular No. 2024/01"
    )
    
    if result.document_type == DocumentType.CIRCULAR:
        print(f"  ✅ Document type: {result.document_type.value}")
        test_results['passed'].append("Circular classification")
    else:
        print(f"  ❌ Document type: Expected circular, got {result.document_type.value}")
        test_results['failed'].append("Circular classification")
    
    print(f"  📊 Confidence: {result.confidence:.2%}")
    print(f"  🏷️ Sub-type: {result.sub_type}")
    
    # Test 5: Property Tax Classification
    print("\n🏠 TEST 5: Property Tax Document")
    print("-" * 50)
    
    property_text = """
    Property Tax Guide for Homeowners
    
    Property tax is calculated based on the Annual Value (AV) of your property.
    The AV is the estimated gross annual rent of the property if it were to be rented out.
    
    Owner-occupied residential properties enjoy lower tax rates.
    """
    
    result = classifier.classify(
        text=property_text,
        filename="property_tax_guide.pdf",
        title="Property Tax Guide"
    )
    
    if result.tax_category == TaxCategory.PROPERTY_TAX:
        print(f"  ✅ Tax category: {result.tax_category.value}")
        test_results['passed'].append("Property tax category")
    else:
        print(f"  ❌ Tax category: Expected property, got {result.tax_category.value}")
        test_results['failed'].append("Property tax category")
    
    print(f"  📊 Confidence: {result.confidence:.2%}")
    
    # Test 6: Stamp Duty Classification
    print("\n🏷️ TEST 6: Stamp Duty Document")
    print("-" * 50)
    
    stamp_duty_text = """
    Additional Buyer's Stamp Duty (ABSD) Rates
    
    Singapore Citizens buying first residential property: 0% ABSD
    Singapore Citizens buying second residential property: 20% ABSD
    
    Buyer's Stamp Duty (BSD) is payable on all property purchases.
    """
    
    result = classifier.classify(
        text=stamp_duty_text,
        filename="absd_rates_2024.pdf"
    )
    
    if result.tax_category == TaxCategory.STAMP_DUTY:
        print(f"  ✅ Tax category: {result.tax_category.value}")
        test_results['passed'].append("Stamp duty category")
    else:
        print(f"  ❌ Tax category: Expected stamp-duty, got {result.tax_category.value}")
        test_results['failed'].append("Stamp duty category")
    
    print(f"  📊 Confidence: {result.confidence:.2%}")
    
    # Test 7: Real PDF Classification
    print("\n📄 TEST 7: Real PDF Documents")
    print("-" * 50)
    
    parser = IRASPDFParser()
    pdf_files = list(Path("./data/iras_docs").glob("*.pdf"))[:2]
    
    for pdf_file in pdf_files:
        try:
            print(f"\n  Testing: {pdf_file.name}")
            sections = parser.parse_pdf(str(pdf_file))
            
            if sections:
                # Get first section for classification
                sample_text = "\n".join([
                    f"{s.title}\n{s.content[:500]}"
                    for s in sections[:3]
                ])
                
                result = classifier.classify(
                    text=sample_text,
                    filename=pdf_file.name,
                    title=sections[0].title if sections[0].title else ""
                )
                
                print(f"    Type: {result.document_type.value}")
                print(f"    Category: {result.tax_category.value}")
                print(f"    Confidence: {result.confidence:.2%}")
                
                if result.sub_type:
                    print(f"    Sub-type: {result.sub_type}")
                
                if result.confidence > 0.5:
                    test_results['passed'].append(f"PDF: {pdf_file.name}")
                else:
                    test_results['failed'].append(f"PDF: {pdf_file.name} (low confidence)")
                    
        except Exception as e:
            print(f"    ❌ Error: {e}")
            test_results['failed'].append(f"PDF: {pdf_file.name}")
    
    # Test 8: Batch Classification
    print("\n📦 TEST 8: Batch Classification")
    print("-" * 50)
    
    batch_docs = [
        {
            'text': "GST Registration Guide for New Businesses",
            'filename': "gst_registration.pdf",
            'title': "GST Registration"
        },
        {
            'text': "Corporate Tax Rates for YA 2024",
            'filename': "corporate_rates_2024.pdf",
            'title': "Corporate Tax Rates"
        },
        {
            'text': "Transfer Pricing Documentation Requirements",
            'filename': "tp_documentation.pdf",
            'title': "Transfer Pricing Guide"
        }
    ]
    
    results = classifier.classify_batch(batch_docs)
    
    for i, (doc, result) in enumerate(zip(batch_docs, results), 1):
        print(f"  {i}. {doc['filename']}")
        print(f"     Type: {result.document_type.value}")
        print(f"     Category: {result.tax_category.value}")
        print(f"     Confidence: {result.confidence:.2%}")
    
    if len(results) == 3:
        test_results['passed'].append("Batch classification")
    else:
        test_results['failed'].append("Batch classification")
    
    # Test 9: Edge Cases
    print("\n🔧 TEST 9: Edge Cases")
    print("-" * 50)
    
    # Empty document
    result = classifier.classify("", "", "")
    print(f"  Empty doc - Type: {result.document_type.value}, Category: {result.tax_category.value}")
    
    # Mixed content
    mixed_text = """
    This document contains information about both GST and Income Tax.
    GST rate is 9%. Income tax rates vary from 0% to 22%.
    Property tax is based on annual value.
    """
    
    result = classifier.classify(mixed_text)
    print(f"  Mixed content - Primary category: {result.tax_category.value}")
    print(f"  Keywords found: {', '.join(result.keywords_found[:5])}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    total_tests = len(test_results['passed']) + len(test_results['failed'])
    pass_rate = (len(test_results['passed']) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n✅ Passed: {len(test_results['passed'])} tests")
    print(f"❌ Failed: {len(test_results['failed'])} tests")
    print(f"\n📈 Pass Rate: {pass_rate:.1f}%")
    
    if test_results['failed']:
        print("\n❌ Failed Tests:")
        for failure in test_results['failed']:
            print(f"  • {failure}")
    
    if pass_rate >= 80:
        print("\n🎉 DOCUMENT CLASSIFIER IS WORKING WELL!")
    elif pass_rate >= 60:
        print("\n⚠️ DOCUMENT CLASSIFIER NEEDS IMPROVEMENT")
    else:
        print("\n❌ DOCUMENT CLASSIFIER HAS ISSUES")
    
    return test_results


def test_classifier_accuracy():
    """Test classifier accuracy metrics."""
    print("\n📊 CLASSIFIER ACCURACY TEST")
    print("-" * 50)
    
    classifier = DocumentClassifier()
    
    # Test confidence scores
    test_cases = [
        {
            'text': "IRAS e-Tax Guide on GST for Financial Services",
            'expected_type': DocumentType.E_TAX_GUIDE,
            'expected_category': TaxCategory.GST
        },
        {
            'text': "Income Tax (Exemption) Order 2024",
            'expected_type': DocumentType.ORDER,
            'expected_category': TaxCategory.INCOME_TAX
        },
        {
            'text': "Form IR8A - Statement of Employment Income",
            'expected_type': DocumentType.FORM,
            'expected_category': TaxCategory.INCOME_TAX
        }
    ]
    
    correct_type = 0
    correct_category = 0
    total_confidence = 0
    
    for case in test_cases:
        result = classifier.classify(case['text'])
        
        if result.document_type == case['expected_type']:
            correct_type += 1
        
        if result.tax_category == case['expected_category']:
            correct_category += 1
        
        total_confidence += result.confidence
    
    print(f"  Document type accuracy: {correct_type}/{len(test_cases)} ({correct_type/len(test_cases)*100:.0f}%)")
    print(f"  Tax category accuracy: {correct_category}/{len(test_cases)} ({correct_category/len(test_cases)*100:.0f}%)")
    print(f"  Average confidence: {total_confidence/len(test_cases):.2%}")


if __name__ == "__main__":
    # Run main tests
    test_document_classifier()
    
    # Run accuracy tests
    test_classifier_accuracy()
    
    print("\n" + "="*70)
    print("✅ ALL CLASSIFIER TESTS COMPLETE")
    print("="*70)