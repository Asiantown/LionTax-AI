"""Test document update detection functionality."""

from src.core.update_detector import DocumentUpdateDetector, DocumentVersion
from pathlib import Path
import logging
import json
import time
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_update_detection():
    """Test document update detection."""
    print("\n" + "="*70)
    print("🔄 DOCUMENT UPDATE DETECTION TEST")
    print("="*70)
    
    # Initialize detector with test database
    detector = DocumentUpdateDetector(version_db_path="./data/test_version_db.json")
    
    # Test 1: Version Information Extraction
    print("\n📝 TEST 1: Version Information Extraction")
    print("-" * 50)
    
    test_content = """
    IRAS e-Tax Guide
    Income Tax Treatment of Digital Assets
    Last Updated: 15 January 2024
    Year of Assessment 2024
    
    This guide supersedes the version dated 1 January 2023.
    Effective from 1 April 2024.
    """
    
    version_info = detector.extract_version_info("test_doc.pdf", test_content)
    
    print("  Extracted version information:")
    for key, value in version_info.items():
        if value:
            print(f"    {key}: {value}")
    
    if version_info['version_date'] and version_info['year_of_assessment']:
        print("  ✅ Version information extracted successfully")
    else:
        print("  ❌ Version extraction incomplete")
    
    # Test 2: New Document Registration
    print("\n📄 TEST 2: New Document Registration")
    print("-" * 50)
    
    # Register test documents
    pdf_files = list(Path("./data/iras_docs").glob("*.pdf"))[:2]
    
    if pdf_files:
        for pdf_file in pdf_files:
            print(f"  Registering: {pdf_file.name}")
            version = detector.register_document(
                str(pdf_file),
                document_type='act'
            )
            print(f"    Hash: {version.file_hash[:16]}...")
            print(f"    Size: {version.file_size} bytes")
            print(f"    YA: {version.year_of_assessment}")
    
    # Test 3: Update Detection
    print("\n🔍 TEST 3: Update Detection")
    print("-" * 50)
    
    if pdf_files:
        test_file = pdf_files[0]
        
        # Check unchanged document
        status, changes = detector.check_document_update(str(test_file))
        print(f"  First check - Status: {status}")
        
        if status == 'unchanged':
            print("  ✅ Correctly identified as unchanged")
        
        # Simulate update by touching the file
        # Note: This won't change the hash, so status should still be unchanged
        Path(test_file).touch()
        status, changes = detector.check_document_update(str(test_file))
        print(f"  After touch - Status: {status}")
    
    # Test 4: Directory Scanning
    print("\n📁 TEST 4: Directory Scanning")
    print("-" * 50)
    
    print("  Scanning ./data/iras_docs/...")
    report = detector.scan_directory("./data/iras_docs", "*.pdf")
    
    print(f"\n  Scan Results:")
    print(f"    Total documents: {report.total_documents}")
    print(f"    New documents: {report.new_documents}")
    print(f"    Updated documents: {report.updated_documents}")
    print(f"    Unchanged documents: {report.unchanged_documents}")
    print(f"    Obsolete documents: {report.obsolete_documents}")
    
    if report.recommendations:
        print(f"\n  Recommendations:")
        for rec in report.recommendations[:3]:
            print(f"    • {rec}")
    
    # Test 5: Version History
    print("\n📚 TEST 5: Version History")
    print("-" * 50)
    
    if pdf_files:
        test_doc = pdf_files[0].name
        
        # Get current version
        current = detector.get_current_version(test_doc)
        if current:
            print(f"  Current version of {test_doc}:")
            print(f"    Last modified: {current.last_modified}")
            print(f"    Is current: {current.is_current}")
        
        # Get version history
        history = detector.get_version_history(test_doc)
        print(f"\n  Version history entries: {len(history)}")
    
    # Test 6: Conflict Detection
    print("\n⚠️ TEST 6: Version Conflict Detection")
    print("-" * 50)
    
    # Simulate version conflict by registering similar documents
    if len(pdf_files) >= 2:
        # Register both as same document family
        doc_family = detector._identify_document_family(pdf_files[0].name)
        print(f"  Document family: {doc_family}")
        
        conflicting = detector._find_conflicting_versions(doc_family)
        if len(conflicting) > 1:
            print(f"  ⚠️ Version conflict detected!")
            print(f"    Conflicting files: {', '.join(conflicting)}")
        else:
            print(f"  No conflicts for this document family")
    
    # Test 7: Update Report Generation
    print("\n📊 TEST 7: Update Report Generation")
    print("-" * 50)
    
    summary = detector.generate_update_summary(report)
    print("\n" + summary)
    
    # Test 8: Performance
    print("\n⚡ TEST 8: Performance Test")
    print("-" * 50)
    
    start_time = time.time()
    
    # Test with multiple files
    test_files = list(Path("./data/iras_docs").glob("*"))[:10]
    for file in test_files:
        if file.is_file():
            detector.check_document_update(str(file))
    
    check_time = time.time() - start_time
    
    print(f"  Files checked: {len(test_files)}")
    print(f"  Time taken: {check_time:.3f}s")
    print(f"  Average per file: {check_time/len(test_files):.3f}s")
    
    if check_time / len(test_files) < 0.1:
        print("  ✅ Performance: Excellent (<0.1s per file)")
    else:
        print("  ⚠️ Performance: Could be optimized")
    
    # Cleanup test database
    test_db = Path("./data/test_version_db.json")
    if test_db.exists():
        test_db.unlink()
        print("\n  Test database cleaned up")
    
    print("\n" + "="*70)
    print("✅ UPDATE DETECTION TEST COMPLETE")
    print("="*70)


def test_real_world_scenario():
    """Test a real-world update scenario."""
    print("\n🌍 REAL-WORLD SCENARIO TEST")
    print("-" * 50)
    
    detector = DocumentUpdateDetector(version_db_path="./data/test_version_db.json")
    
    # Scenario: Monthly update check
    print("\n  Scenario: Monthly IRAS document update check")
    print("  " + "-" * 40)
    
    # Initial scan
    print("  📅 January 2024 - Initial scan:")
    initial_report = detector.scan_directory("./data/iras_docs", "*.pdf")
    print(f"    New documents found: {initial_report.new_documents}")
    
    # Simulate one month later
    print("\n  📅 February 2024 - Monthly check:")
    # In real scenario, some files would be updated
    followup_report = detector.scan_directory("./data/iras_docs", "*.pdf")
    
    print(f"    New: {followup_report.new_documents}")
    print(f"    Updated: {followup_report.updated_documents}")
    print(f"    Unchanged: {followup_report.unchanged_documents}")
    
    if followup_report.updated_documents > 0:
        print("    Action: Re-index updated documents")
    
    if followup_report.new_documents > 0:
        print("    Action: Process and index new documents")
    
    # Cleanup
    test_db = Path("./data/test_version_db.json")
    if test_db.exists():
        test_db.unlink()


if __name__ == "__main__":
    # Run main tests
    test_update_detection()
    
    # Run real-world scenario
    test_real_world_scenario()