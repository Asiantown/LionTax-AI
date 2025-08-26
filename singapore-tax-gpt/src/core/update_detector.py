"""Document update detection and version tracking system."""

import os
import json
import hashlib
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class DocumentVersion:
    """Represents a version of a document."""
    filename: str
    file_hash: str
    file_size: int
    last_modified: str
    version_date: Optional[str]  # Extracted from content
    year_of_assessment: Optional[str]
    document_type: str
    changes_detected: List[str]
    supersedes: Optional[str]  # Previous version filename
    is_current: bool


@dataclass
class UpdateReport:
    """Report of document updates."""
    total_documents: int
    new_documents: int
    updated_documents: int
    obsolete_documents: int
    unchanged_documents: int
    version_conflicts: List[Dict[str, Any]]
    recommendations: List[str]
    timestamp: str


class DocumentUpdateDetector:
    """Detects and tracks document updates and versions."""
    
    def __init__(self, version_db_path: str = "./data/version_db.json"):
        """
        Initialize the update detector.
        
        Args:
            version_db_path: Path to version database file
        """
        self.version_db_path = version_db_path
        self.version_db = self._load_version_db()
        self.version_patterns = self._initialize_version_patterns()
    
    def _load_version_db(self) -> Dict[str, DocumentVersion]:
        """Load version database from file."""
        if os.path.exists(self.version_db_path):
            try:
                with open(self.version_db_path, 'r') as f:
                    data = json.load(f)
                    # Convert dict back to DocumentVersion objects
                    return {
                        k: DocumentVersion(**v) 
                        for k, v in data.items()
                    }
            except Exception as e:
                logger.warning(f"Could not load version DB: {e}")
        return {}
    
    def _save_version_db(self):
        """Save version database to file."""
        try:
            os.makedirs(os.path.dirname(self.version_db_path), exist_ok=True)
            with open(self.version_db_path, 'w') as f:
                # Convert DocumentVersion objects to dict
                data = {
                    k: asdict(v) 
                    for k, v in self.version_db.items()
                }
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Could not save version DB: {e}")
    
    def _initialize_version_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize patterns for version extraction."""
        return {
            'version_date': re.compile(
                r'(?:Last\s+)?(?:Updated?|Revised?|Published?|Issued?)[\s:]+' +
                r'(\d{1,2}[\s\-/]\w+[\s\-/]\d{2,4})',
                re.IGNORECASE
            ),
            'year_assessment': re.compile(
                r'(?:YA|Year\s+of\s+Assessment)[\s:]*(\d{4})',
                re.IGNORECASE
            ),
            'supersedes': re.compile(
                r'(?:Supersedes?|Replaces?)[\s:]+([^\n]+)',
                re.IGNORECASE
            ),
            'version_number': re.compile(
                r'(?:Version|Rev(?:ision)?)[\s:]*(\d+(?:\.\d+)?)',
                re.IGNORECASE
            ),
            'effective_date': re.compile(
                r'(?:Effective|Valid)[\s:]+(?:from\s+)?(\d{1,2}[\s\-/]\w+[\s\-/]\d{2,4})',
                re.IGNORECASE
            )
        }
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def extract_version_info(self, file_path: str, content: str = None) -> Dict[str, Any]:
        """
        Extract version information from file and content.
        
        Args:
            file_path: Path to the file
            content: Optional text content (first 2000 chars of document)
            
        Returns:
            Dictionary with version information
        """
        version_info = {
            'version_date': None,
            'year_of_assessment': None,
            'version_number': None,
            'effective_date': None,
            'supersedes': None
        }
        
        # If no content provided, try to read file
        if content is None and file_path.endswith(('.txt', '.pdf')):
            try:
                if file_path.endswith('.pdf'):
                    # Use PDF parser if available
                    from .advanced_pdf_parser import IRASPDFParser
                    parser = IRASPDFParser()
                    sections = parser.parse_pdf(file_path)
                    if sections:
                        content = '\n'.join([s.content[:500] for s in sections[:3]])
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(2000)
            except Exception as e:
                logger.warning(f"Could not read file for version info: {e}")
                return version_info
        
        if not content:
            return version_info
        
        # Extract version information using patterns
        for key, pattern in self.version_patterns.items():
            match = pattern.search(content)
            if match:
                version_info[key] = match.group(1).strip()
        
        # Also check filename for year/version
        filename = os.path.basename(file_path)
        year_match = re.search(r'(\d{4})', filename)
        if year_match and not version_info['year_of_assessment']:
            version_info['year_of_assessment'] = year_match.group(1)
        
        return version_info
    
    def check_document_update(self, file_path: str, content: str = None) -> Tuple[str, List[str]]:
        """
        Check if a document has been updated.
        
        Args:
            file_path: Path to document
            content: Optional document content
            
        Returns:
            Tuple of (status, changes) where status is:
            - 'new': Document not seen before
            - 'updated': Document has changes
            - 'unchanged': Document unchanged
            - 'obsolete': Document is outdated
            changes is a list of detected changes
        """
        file_path = str(file_path)
        filename = os.path.basename(file_path)
        
        # Calculate current hash
        current_hash = self.calculate_file_hash(file_path)
        
        # Get file stats
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        last_modified = datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        
        # Extract version info
        version_info = self.extract_version_info(file_path, content)
        
        # Check if document exists in DB
        if filename not in self.version_db:
            return 'new', []
        
        stored_version = self.version_db[filename]
        changes = []
        
        # Check for changes
        if stored_version.file_hash != current_hash:
            changes.append('content_changed')
            
            # Detect specific changes
            if stored_version.file_size != file_size:
                size_diff = file_size - stored_version.file_size
                if size_diff > 0:
                    changes.append(f'size_increased_{size_diff}_bytes')
                else:
                    changes.append(f'size_decreased_{abs(size_diff)}_bytes')
            
            if version_info['version_date'] != stored_version.version_date:
                changes.append('version_date_changed')
            
            if version_info['year_of_assessment'] != stored_version.year_of_assessment:
                changes.append('year_of_assessment_changed')
            
            return 'updated', changes
        
        # Check if obsolete (older year of assessment)
        if version_info['year_of_assessment'] and stored_version.year_of_assessment:
            try:
                current_ya = int(version_info['year_of_assessment'])
                stored_ya = int(stored_version.year_of_assessment)
                if current_ya < stored_ya:
                    return 'obsolete', ['older_year_of_assessment']
            except ValueError:
                pass
        
        return 'unchanged', []
    
    def register_document(self, 
                         file_path: str, 
                         document_type: str = 'general',
                         content: str = None) -> DocumentVersion:
        """
        Register a document in the version database.
        
        Args:
            file_path: Path to document
            document_type: Type of document
            content: Optional document content
            
        Returns:
            DocumentVersion object
        """
        file_path = str(file_path)
        filename = os.path.basename(file_path)
        
        # Get file info
        file_hash = self.calculate_file_hash(file_path)
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        last_modified = datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        
        # Extract version info
        version_info = self.extract_version_info(file_path, content)
        
        # Check for superseded document
        supersedes = None
        if filename in self.version_db:
            supersedes = filename
        
        # Create version record
        version = DocumentVersion(
            filename=filename,
            file_hash=file_hash,
            file_size=file_size,
            last_modified=last_modified,
            version_date=version_info.get('version_date'),
            year_of_assessment=version_info.get('year_of_assessment'),
            document_type=document_type,
            changes_detected=[],
            supersedes=supersedes,
            is_current=True
        )
        
        # Mark previous version as not current
        if filename in self.version_db:
            self.version_db[filename].is_current = False
        
        # Store in database
        self.version_db[filename] = version
        self._save_version_db()
        
        return version
    
    def scan_directory(self, directory: str, pattern: str = "*.pdf") -> UpdateReport:
        """
        Scan directory for document updates.
        
        Args:
            directory: Directory to scan
            pattern: File pattern to match
            
        Returns:
            UpdateReport with scan results
        """
        directory_path = Path(directory)
        files = list(directory_path.glob(pattern))
        
        new_docs = []
        updated_docs = []
        obsolete_docs = []
        unchanged_docs = []
        version_conflicts = []
        
        logger.info(f"Scanning {len(files)} files for updates...")
        
        for file_path in files:
            try:
                status, changes = self.check_document_update(file_path)
                filename = file_path.name
                
                if status == 'new':
                    new_docs.append(filename)
                    self.register_document(file_path)
                elif status == 'updated':
                    updated_docs.append(filename)
                    # Update registration
                    self.register_document(file_path)
                elif status == 'obsolete':
                    obsolete_docs.append(filename)
                elif status == 'unchanged':
                    unchanged_docs.append(filename)
                
                # Check for version conflicts
                if status == 'updated' and 'year_of_assessment_changed' in changes:
                    # Check if we have multiple versions of same document type
                    doc_type = self._identify_document_family(filename)
                    conflicting = self._find_conflicting_versions(doc_type)
                    if len(conflicting) > 1:
                        version_conflicts.append({
                            'document_family': doc_type,
                            'conflicting_files': conflicting,
                            'reason': 'multiple_versions_same_type'
                        })
                        
            except Exception as e:
                logger.error(f"Error scanning {file_path}: {e}")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            new_docs, updated_docs, obsolete_docs, version_conflicts
        )
        
        report = UpdateReport(
            total_documents=len(files),
            new_documents=len(new_docs),
            updated_documents=len(updated_docs),
            obsolete_documents=len(obsolete_docs),
            unchanged_documents=len(unchanged_docs),
            version_conflicts=version_conflicts,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat()
        )
        
        return report
    
    def _identify_document_family(self, filename: str) -> str:
        """Identify document family/type from filename."""
        # Remove year and version info
        family = re.sub(r'\d{4}', '', filename)
        family = re.sub(r'v\d+(?:\.\d+)?', '', family, flags=re.IGNORECASE)
        family = re.sub(r'rev\d+', '', family, flags=re.IGNORECASE)
        family = family.strip('_- ')
        return family
    
    def _find_conflicting_versions(self, doc_family: str) -> List[str]:
        """Find potentially conflicting versions of same document type."""
        conflicting = []
        for filename, version in self.version_db.items():
            if version.is_current:
                if self._identify_document_family(filename) == doc_family:
                    conflicting.append(filename)
        return conflicting
    
    def _generate_recommendations(self,
                                 new_docs: List[str],
                                 updated_docs: List[str],
                                 obsolete_docs: List[str],
                                 conflicts: List[Dict]) -> List[str]:
        """Generate recommendations based on scan results."""
        recommendations = []
        
        if new_docs:
            recommendations.append(
                f"Process {len(new_docs)} new documents for indexing"
            )
        
        if updated_docs:
            recommendations.append(
                f"Re-process {len(updated_docs)} updated documents"
            )
        
        if obsolete_docs:
            recommendations.append(
                f"Consider removing {len(obsolete_docs)} obsolete documents from index"
            )
        
        if conflicts:
            recommendations.append(
                f"Resolve {len(conflicts)} version conflicts - multiple versions detected"
            )
            for conflict in conflicts[:3]:  # Show first 3
                files = ', '.join(conflict['conflicting_files'][:2])
                recommendations.append(f"  • Check versions: {files}")
        
        # Check for stale documents
        stale_threshold = datetime.now() - timedelta(days=365)
        stale_count = sum(
            1 for v in self.version_db.values()
            if v.is_current and 
            datetime.fromisoformat(v.last_modified) < stale_threshold
        )
        
        if stale_count > 0:
            recommendations.append(
                f"Review {stale_count} documents older than 1 year for updates"
            )
        
        return recommendations
    
    def get_current_version(self, document_name: str) -> Optional[DocumentVersion]:
        """Get the current version of a document."""
        # Try exact match first
        if document_name in self.version_db:
            return self.version_db[document_name]
        
        # Try to find by document family
        doc_family = self._identify_document_family(document_name)
        for filename, version in self.version_db.items():
            if version.is_current:
                if self._identify_document_family(filename) == doc_family:
                    return version
        
        return None
    
    def get_version_history(self, document_name: str) -> List[DocumentVersion]:
        """Get version history for a document family."""
        doc_family = self._identify_document_family(document_name)
        history = []
        
        for filename, version in self.version_db.items():
            if self._identify_document_family(filename) == doc_family:
                history.append(version)
        
        # Sort by modification date
        history.sort(
            key=lambda v: datetime.fromisoformat(v.last_modified),
            reverse=True
        )
        
        return history
    
    def generate_update_summary(self, report: UpdateReport) -> str:
        """Generate a human-readable update summary."""
        lines = [
            "=" * 70,
            "DOCUMENT UPDATE DETECTION REPORT",
            "=" * 70,
            f"Scan timestamp: {report.timestamp}",
            "",
            "SUMMARY",
            "-" * 40,
            f"Total documents scanned: {report.total_documents}",
            f"New documents: {report.new_documents}",
            f"Updated documents: {report.updated_documents}",
            f"Obsolete documents: {report.obsolete_documents}",
            f"Unchanged documents: {report.unchanged_documents}",
            ""
        ]
        
        if report.version_conflicts:
            lines.extend([
                "VERSION CONFLICTS",
                "-" * 40
            ])
            for conflict in report.version_conflicts:
                lines.append(f"Document family: {conflict['document_family']}")
                lines.append(f"Conflicting files: {', '.join(conflict['conflicting_files'][:3])}")
                lines.append(f"Reason: {conflict['reason']}")
                lines.append("")
        
        if report.recommendations:
            lines.extend([
                "RECOMMENDATIONS",
                "-" * 40
            ])
            for rec in report.recommendations:
                lines.append(f"• {rec}")
            lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)