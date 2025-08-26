"""Test batch document processing system."""

from src.core.batch_processor import BatchDocumentProcessor, DocumentCache
from src.core.enhanced_rag import EnhancedRAGEngine
from pathlib import Path
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_batch_processor():
    """Test batch processing functionality."""
    print("\n" + "="*70)
    print("📦 BATCH PROCESSING TEST")
    print("="*70)
    
    # Initialize processor
    processor = BatchDocumentProcessor(
        max_workers=2,  # Use 2 workers for testing
        use_cache=True
    )
    
    # Test 1: Cache functionality
    print("\n💾 TEST 1: Cache Functionality")
    print("-" * 50)
    
    cache = DocumentCache()
    
    # Clear cache for fresh test
    cache.clear_cache()
    print("  ✅ Cache cleared")
    
    # Check if file is processed (should be False)
    test_file = Path("./data/iras_docs").glob("*.pdf").__next__()
    is_processed = cache.is_file_processed(test_file)
    
    if not is_processed:
        print(f"  ✅ Cache correctly reports {test_file.name} as unprocessed")
    else:
        print(f"  ❌ Cache incorrectly reports {test_file.name} as processed")
    
    # Test 2: Single document processing
    print("\n📄 TEST 2: Single Document Processing")
    print("-" * 50)
    
    pdf_files = list(Path("./data/iras_docs").glob("*.pdf"))
    
    if pdf_files:
        test_pdf = pdf_files[0]
        print(f"  Processing: {test_pdf.name}")
        
        result = processor.process_single_document(test_pdf, skip_if_processed=False)
        
        print(f"  Status: {result.status}")
        print(f"  Chunks created: {result.chunks_created}")
        print(f"  Processing time: {result.processing_time:.2f}s")
        print(f"  Document type: {result.document_type}")
        print(f"  Tax category: {result.tax_category}")
        
        if result.status == "success":
            print("  ✅ Single document processed successfully")
        else:
            print(f"  ❌ Processing failed: {result.error}")
    
    # Test 3: Process same document again (should skip)
    print("\n🔄 TEST 3: Cache Skip Test")
    print("-" * 50)
    
    if pdf_files:
        print(f"  Re-processing: {test_pdf.name}")
        
        result = processor.process_single_document(test_pdf, skip_if_processed=True)
        
        if result.status == "skipped":
            print("  ✅ Document correctly skipped (already in cache)")
        else:
            print(f"  ❌ Document not skipped: {result.status}")
    
    # Test 4: Batch processing directory
    print("\n📁 TEST 4: Directory Batch Processing")
    print("-" * 50)
    
    print("  Processing all PDFs in ./data/iras_docs/")
    
    report = processor.process_directory(
        "./data/iras_docs",
        file_pattern="*.pdf",
        recursive=False,
        skip_processed=True
    )
    
    print(f"\n  Results:")
    print(f"    Total files: {report.total_files}")
    print(f"    Successful: {report.successful}")
    print(f"    Failed: {report.failed}")
    print(f"    Skipped: {report.skipped}")
    print(f"    Total chunks: {report.total_chunks}")
    print(f"    Total time: {report.total_time:.2f}s")
    
    if report.successful > 0 or report.skipped > 0:
        print("  ✅ Batch processing completed")
    else:
        print("  ❌ No files processed successfully")
    
    # Test 5: Generate and save report
    print("\n📊 TEST 5: Report Generation")
    print("-" * 50)
    
    report_text = processor.generate_report(report)
    print("\n" + report_text)
    
    # Save report
    processor.save_report(report)
    print("  ✅ Report saved to ./data/reports/")
    
    # Test 6: Process specific files
    print("\n📋 TEST 6: Process Specific Files")
    print("-" * 50)
    
    if len(pdf_files) >= 2:
        specific_files = [str(f) for f in pdf_files[:2]]
        print(f"  Processing {len(specific_files)} specific files")
        
        report = processor.process_files(specific_files, skip_processed=False)
        
        print(f"  Processed: {report.successful} files")
        print(f"  Total chunks: {report.total_chunks}")
        
        if report.successful > 0:
            print("  ✅ Specific files processed")
    
    # Test 7: Parallel processing performance
    print("\n⚡ TEST 7: Parallel Processing Performance")
    print("-" * 50)
    
    # Test with 1 worker
    processor_single = BatchDocumentProcessor(max_workers=1, use_cache=False)
    
    # Clear cache for fair comparison
    if processor_single.cache:
        processor_single.cache.clear_cache()
    
    start_time = time.time()
    report_single = processor_single.process_directory(
        "./data/iras_docs",
        file_pattern="*.pdf",
        recursive=False,
        skip_processed=False
    )
    single_time = time.time() - start_time
    
    # Test with 4 workers
    processor_multi = BatchDocumentProcessor(max_workers=4, use_cache=False)
    
    start_time = time.time()
    report_multi = processor_multi.process_directory(
        "./data/iras_docs",
        file_pattern="*.pdf",
        recursive=False,
        skip_processed=False
    )
    multi_time = time.time() - start_time
    
    print(f"  Single worker: {single_time:.2f}s")
    print(f"  Multi workers (4): {multi_time:.2f}s")
    
    if multi_time < single_time:
        speedup = single_time / multi_time
        print(f"  ✅ Parallel processing {speedup:.1f}x faster")
    else:
        print("  ⚠️ Parallel processing not faster (possibly due to few files)")
    
    print("\n" + "="*70)
    print("✅ BATCH PROCESSING TEST COMPLETE")
    print("="*70)


def test_integration_with_rag():
    """Test batch processor integration with RAG engine."""
    print("\n🔗 INTEGRATION TEST: Batch Processor + RAG")
    print("-" * 50)
    
    # Initialize RAG engine
    rag_engine = EnhancedRAGEngine()
    
    # Initialize processor with RAG engine
    processor = BatchDocumentProcessor(
        rag_engine=rag_engine,
        max_workers=2,
        use_cache=True
    )
    
    # Process documents
    report = processor.process_directory(
        "./data/iras_docs",
        file_pattern="*.pdf",
        skip_processed=False
    )
    
    print(f"  Documents processed: {report.successful}")
    print(f"  Chunks added to RAG: {report.total_chunks}")
    
    # Test query
    if report.successful > 0:
        response = rag_engine.query_with_metadata("What is the income tax rate?")
        
        if response['answer']:
            print("  ✅ RAG query successful after batch processing")
            print(f"  Answer preview: {response['answer'][:100]}...")
        else:
            print("  ❌ RAG query failed")
    
    print("\n✅ Integration test complete")


if __name__ == "__main__":
    # Run main batch processing tests
    test_batch_processor()
    
    # Run integration test
    test_integration_with_rag()