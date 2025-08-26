"""Batch document processing system for efficient PDF handling."""

import os
import time
import json
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import hashlib
import logging

from .advanced_pdf_parser import IRASPDFParser
from .smart_chunker import SmartTaxChunker
from .metadata_extractor import MetadataExtractor
from .document_classifier import DocumentClassifier
from .enhanced_rag import EnhancedRAGEngine

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of processing a single document."""
    filename: str
    status: str  # success, failed, skipped
    chunks_created: int
    processing_time: float
    document_type: str
    tax_category: str
    metadata: Dict[str, Any]
    error: Optional[str] = None
    file_hash: Optional[str] = None


@dataclass
class BatchProcessingReport:
    """Report for batch processing operation."""
    total_files: int
    successful: int
    failed: int
    skipped: int
    total_chunks: int
    total_time: float
    average_time_per_file: float
    results: List[ProcessingResult]
    timestamp: str


class DocumentCache:
    """Simple cache for tracking processed documents."""
    
    def __init__(self, cache_file: str = "./data/processing_cache.json"):
        """Initialize document cache."""
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load cache from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save cache: {e}")
    
    def get_file_hash(self, file_path: str) -> str:
        """Calculate file hash for change detection."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def is_file_processed(self, file_path: str) -> bool:
        """Check if file has been processed and hasn't changed."""
        file_path = str(file_path)
        if file_path not in self.cache:
            return False
        
        current_hash = self.get_file_hash(file_path)
        cached_hash = self.cache[file_path].get('hash')
        
        return current_hash == cached_hash
    
    def mark_processed(self, file_path: str, result: ProcessingResult):
        """Mark file as processed."""
        file_path = str(file_path)
        self.cache[file_path] = {
            'hash': result.file_hash,
            'timestamp': datetime.now().isoformat(),
            'chunks': result.chunks_created,
            'document_type': result.document_type,
            'tax_category': result.tax_category
        }
        self._save_cache()
    
    def clear_cache(self):
        """Clear all cache entries."""
        self.cache = {}
        self._save_cache()


class BatchDocumentProcessor:
    """Batch processor for efficient document handling."""
    
    def __init__(self, 
                 rag_engine: Optional[EnhancedRAGEngine] = None,
                 max_workers: int = 4,
                 use_cache: bool = True):
        """
        Initialize batch processor.
        
        Args:
            rag_engine: RAG engine to add documents to
            max_workers: Maximum parallel workers
            use_cache: Whether to use caching for duplicate detection
        """
        self.rag_engine = rag_engine or EnhancedRAGEngine()
        self.pdf_parser = IRASPDFParser()
        self.chunker = SmartTaxChunker()
        self.metadata_extractor = MetadataExtractor()
        self.classifier = DocumentClassifier()
        self.max_workers = max_workers
        self.use_cache = use_cache
        self.cache = DocumentCache() if use_cache else None
    
    def process_single_document(self, 
                              file_path: Path,
                              skip_if_processed: bool = True) -> ProcessingResult:
        """
        Process a single document.
        
        Args:
            file_path: Path to document
            skip_if_processed: Skip if already in cache
            
        Returns:
            ProcessingResult object
        """
        start_time = time.time()
        filename = file_path.name
        
        try:
            # Check cache
            if self.use_cache and skip_if_processed:
                if self.cache.is_file_processed(file_path):
                    logger.info(f"Skipping {filename} (already processed)")
                    return ProcessingResult(
                        filename=filename,
                        status="skipped",
                        chunks_created=0,
                        processing_time=0,
                        document_type="cached",
                        tax_category="cached",
                        metadata={}
                    )
            
            # Calculate file hash
            file_hash = self.cache.get_file_hash(file_path) if self.use_cache else None
            
            logger.info(f"Processing {filename}...")
            
            # Parse PDF
            sections = self.pdf_parser.parse_pdf(str(file_path))
            
            if not sections:
                raise ValueError("No sections extracted from PDF")
            
            # Extract text for classification
            sample_text = "\n".join([
                f"{s.title or ''}\n{s.content[:1000]}"
                for s in sections[:5]
            ])
            
            # Classify document
            classification = self.classifier.classify(
                text=sample_text,
                filename=filename,
                title=sections[0].title if sections[0].title else ""
            )
            
            # Extract metadata
            metadata = self.metadata_extractor.extract_metadata(
                sample_text, 
                filename
            )
            
            # Convert sections to documents with enhanced metadata
            documents = []
            for section in sections:
                # Smart chunking based on section type
                if section.section_type in ['table', 'tax_rate_table']:
                    # For tables, check size and split if needed
                    if len(section.content) > 8000:
                        # Split large tables into smaller chunks
                        chunks = self.chunker.split_text(section.content)
                    else:
                        chunks = [section.content]  # Don't split small tables
                else:
                    chunks = self.chunker.split_text(section.content)
                
                # Further split any chunks that are still too large
                final_chunks = []
                for chunk in chunks:
                    if len(chunk) > 8000:  # ~2000 tokens approximately
                        # Force split large chunks
                        from langchain.text_splitter import RecursiveCharacterTextSplitter
                        emergency_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=8000,
                            chunk_overlap=200
                        )
                        sub_chunks = emergency_splitter.split_text(chunk)
                        final_chunks.extend(sub_chunks)
                    else:
                        final_chunks.append(chunk)
                
                for chunk in final_chunks:
                    doc = {
                        'page_content': chunk,
                        'metadata': {
                            'source': filename,
                            'section_title': section.title,
                            'section_number': section.section_number,
                            'section_type': section.section_type,
                            'pages': ','.join(map(str, section.page_numbers)),
                            'document_type': classification.document_type.value,
                            'tax_category': classification.tax_category.value,
                            'year_of_assessment': ','.join(metadata.year_of_assessment),
                            'last_updated': metadata.last_updated or '',
                            'has_tables': metadata.has_tables,
                            'has_examples': metadata.has_examples
                        }
                    }
                    documents.append(doc)
            
            # Add to RAG engine in batches to avoid token limits
            if self.rag_engine:
                from langchain.schema import Document as LangchainDoc
                
                # Process in batches of 10 documents to avoid token limits
                batch_size = 10
                for i in range(0, len(documents), batch_size):
                    batch = documents[i:i+batch_size]
                    langchain_docs = [
                        LangchainDoc(
                            page_content=doc['page_content'],
                            metadata=doc['metadata']
                        )
                        for doc in batch
                    ]
                    try:
                        self.rag_engine.vectorstore.add_documents(langchain_docs)
                    except Exception as e:
                        if "max_tokens" in str(e):
                            # If still too large, process one by one
                            for doc in langchain_docs:
                                try:
                                    self.rag_engine.vectorstore.add_documents([doc])
                                except Exception as single_error:
                                    logger.warning(f"Skipping oversized chunk: {single_error}")
                        else:
                            raise e
            
            processing_time = time.time() - start_time
            
            result = ProcessingResult(
                filename=filename,
                status="success",
                chunks_created=len(documents),
                processing_time=processing_time,
                document_type=classification.document_type.value,
                tax_category=classification.tax_category.value,
                metadata={
                    'title': metadata.title,
                    'year_of_assessment': metadata.year_of_assessment,
                    'sections': len(sections),
                    'classification_confidence': classification.confidence
                },
                file_hash=file_hash
            )
            
            # Update cache
            if self.use_cache:
                self.cache.mark_processed(file_path, result)
            
            logger.info(f"✅ Processed {filename}: {len(documents)} chunks in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to process {filename}: {e}")
            return ProcessingResult(
                filename=filename,
                status="failed",
                chunks_created=0,
                processing_time=time.time() - start_time,
                document_type="unknown",
                tax_category="unknown",
                metadata={},
                error=str(e)
            )
    
    def process_directory(self,
                         directory: str,
                         file_pattern: str = "*.pdf",
                         recursive: bool = True,
                         skip_processed: bool = True) -> BatchProcessingReport:
        """
        Process all documents in a directory.
        
        Args:
            directory: Directory path
            file_pattern: File pattern to match
            recursive: Search recursively
            skip_processed: Skip already processed files
            
        Returns:
            BatchProcessingReport
        """
        start_time = time.time()
        directory_path = Path(directory)
        
        # Find all matching files
        if recursive:
            files = list(directory_path.rglob(file_pattern))
        else:
            files = list(directory_path.glob(file_pattern))
        
        logger.info(f"Found {len(files)} files to process")
        
        results = []
        total_chunks = 0
        successful = 0
        failed = 0
        skipped = 0
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(
                    self.process_single_document, 
                    file, 
                    skip_processed
                ): file 
                for file in files
            }
            
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result.status == "success":
                        successful += 1
                        total_chunks += result.chunks_created
                    elif result.status == "failed":
                        failed += 1
                    elif result.status == "skipped":
                        skipped += 1
                        
                except Exception as e:
                    logger.error(f"Unexpected error processing {file}: {e}")
                    failed += 1
                    results.append(ProcessingResult(
                        filename=file.name,
                        status="failed",
                        chunks_created=0,
                        processing_time=0,
                        document_type="unknown",
                        tax_category="unknown",
                        metadata={},
                        error=str(e)
                    ))
        
        total_time = time.time() - start_time
        
        report = BatchProcessingReport(
            total_files=len(files),
            successful=successful,
            failed=failed,
            skipped=skipped,
            total_chunks=total_chunks,
            total_time=total_time,
            average_time_per_file=total_time / len(files) if files else 0,
            results=results,
            timestamp=datetime.now().isoformat()
        )
        
        return report
    
    def process_files(self, 
                     file_paths: List[str],
                     skip_processed: bool = True) -> BatchProcessingReport:
        """
        Process specific files.
        
        Args:
            file_paths: List of file paths
            skip_processed: Skip already processed files
            
        Returns:
            BatchProcessingReport
        """
        start_time = time.time()
        files = [Path(f) for f in file_paths if Path(f).exists()]
        
        if len(files) < len(file_paths):
            logger.warning(f"Some files not found. Processing {len(files)} of {len(file_paths)} files")
        
        results = []
        total_chunks = 0
        successful = 0
        failed = 0
        skipped = 0
        
        for file in files:
            result = self.process_single_document(file, skip_processed)
            results.append(result)
            
            if result.status == "success":
                successful += 1
                total_chunks += result.chunks_created
            elif result.status == "failed":
                failed += 1
            elif result.status == "skipped":
                skipped += 1
        
        total_time = time.time() - start_time
        
        report = BatchProcessingReport(
            total_files=len(files),
            successful=successful,
            failed=failed,
            skipped=skipped,
            total_chunks=total_chunks,
            total_time=total_time,
            average_time_per_file=total_time / len(files) if files else 0,
            results=results,
            timestamp=datetime.now().isoformat()
        )
        
        return report
    
    def generate_report(self, report: BatchProcessingReport) -> str:
        """Generate a formatted report."""
        lines = [
            "=" * 70,
            "BATCH PROCESSING REPORT",
            "=" * 70,
            f"Timestamp: {report.timestamp}",
            "",
            "SUMMARY",
            "-" * 40,
            f"Total files: {report.total_files}",
            f"Successful: {report.successful}",
            f"Failed: {report.failed}",
            f"Skipped: {report.skipped}",
            f"Total chunks created: {report.total_chunks}",
            f"Total time: {report.total_time:.2f}s",
            f"Average time per file: {report.average_time_per_file:.2f}s",
            ""
        ]
        
        if report.successful > 0:
            lines.extend([
                "SUCCESSFUL PROCESSING",
                "-" * 40
            ])
            for result in report.results:
                if result.status == "success":
                    lines.append(
                        f"✅ {result.filename}: {result.chunks_created} chunks, "
                        f"{result.processing_time:.2f}s, "
                        f"Type: {result.document_type}, "
                        f"Category: {result.tax_category}"
                    )
            lines.append("")
        
        if report.failed > 0:
            lines.extend([
                "FAILED PROCESSING",
                "-" * 40
            ])
            for result in report.results:
                if result.status == "failed":
                    lines.append(f"❌ {result.filename}: {result.error}")
            lines.append("")
        
        if report.skipped > 0:
            lines.extend([
                "SKIPPED FILES (Already Processed)",
                "-" * 40
            ])
            for result in report.results:
                if result.status == "skipped":
                    lines.append(f"⏭️ {result.filename}")
            lines.append("")
        
        # Document type distribution
        doc_types = {}
        for result in report.results:
            if result.status == "success":
                doc_types[result.document_type] = doc_types.get(result.document_type, 0) + 1
        
        if doc_types:
            lines.extend([
                "DOCUMENT TYPE DISTRIBUTION",
                "-" * 40
            ])
            for doc_type, count in sorted(doc_types.items()):
                lines.append(f"  {doc_type}: {count}")
            lines.append("")
        
        # Tax category distribution
        tax_cats = {}
        for result in report.results:
            if result.status == "success":
                tax_cats[result.tax_category] = tax_cats.get(result.tax_category, 0) + 1
        
        if tax_cats:
            lines.extend([
                "TAX CATEGORY DISTRIBUTION",
                "-" * 40
            ])
            for cat, count in sorted(tax_cats.items()):
                lines.append(f"  {cat}: {count}")
            lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def save_report(self, report: BatchProcessingReport, filename: str = None):
        """Save report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"./data/reports/batch_report_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        logger.info(f"Report saved to {filename}")
        
        # Also save text version
        text_filename = filename.replace('.json', '.txt')
        with open(text_filename, 'w') as f:
            f.write(self.generate_report(report))
        
        logger.info(f"Text report saved to {text_filename}")