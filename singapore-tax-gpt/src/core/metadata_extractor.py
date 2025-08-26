"""Advanced Metadata Extraction for IRAS Documents."""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """Comprehensive metadata for IRAS documents."""
    # Basic information
    title: str = ""
    document_type: str = ""  # e-tax-guide, circular, act, form, etc.
    
    # Temporal information
    year_of_assessment: List[str] = field(default_factory=list)
    publication_date: Optional[str] = None
    last_updated: Optional[str] = None
    effective_date: Optional[str] = None
    
    # Document classification
    tax_category: str = ""  # income, gst, property, corporate, stamp-duty
    subcategory: str = ""  # individual, business, etc.
    
    # Version information
    version: Optional[str] = None
    revision: Optional[str] = None
    supersedes: Optional[str] = None
    
    # Structural information
    sections: List[str] = field(default_factory=list)
    has_tables: bool = False
    has_forms: bool = False
    has_examples: bool = False
    
    # Legal references
    act_references: List[str] = field(default_factory=list)
    circular_references: List[str] = field(default_factory=list)
    
    # Content indicators
    keywords: List[str] = field(default_factory=list)
    tax_rates_mentioned: List[str] = field(default_factory=list)
    reliefs_mentioned: List[str] = field(default_factory=list)
    
    # Administrative
    issuing_authority: str = "IRAS"
    document_id: Optional[str] = None
    pages: int = 0


class MetadataExtractor:
    """Extract comprehensive metadata from IRAS documents."""
    
    def __init__(self):
        """Initialize the metadata extractor with patterns."""
        
        # Date patterns
        self.date_patterns = {
            'full_date': r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})',
            'short_date': r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            'year_only': r'(?:19|20)\d{2}',
            'month_year': r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})'
        }
        
        # Year of Assessment patterns
        self.ya_patterns = {
            'explicit': r'(?:Year of Assessment|YA)\s*(\d{4})',
            'range': r'YA\s*(\d{4})\s*(?:to|-)\s*(\d{4})',
            'basis_year': r'Basis Year\s*(\d{4})',
            'tax_year': r'Tax Year\s*(\d{4})'
        }
        
        # Document type indicators
        self.doc_type_patterns = {
            'e_tax_guide': r'(?:IRAS\s+)?e-Tax Guide|e-Tax\s+Guide',
            'circular': r'(?:IRAS\s+)?Circular\s*(?:No\.)?\s*([A-Z0-9/]+)',
            'act': r'Income Tax Act|GST Act|Property Tax Act|Stamp Duties Act',
            'form': r'(?:IRAS\s+)?Form\s+([A-Z0-9/-]+)',
            'bulletin': r'Tax Bulletin|IRAS Bulletin',
            'order': r'(?:Income Tax|GST|Property Tax)\s+(?:\([^)]+\))?\s*Order',
            'regulation': r'(?:Income Tax|GST)\s+(?:\([^)]+\))?\s*Regulations?'
        }
        
        # Tax category patterns
        self.tax_category_patterns = {
            'income': r'Income Tax|Individual Tax|Personal Tax',
            'gst': r'GST|Goods and Services Tax|Value Added Tax',
            'property': r'Property Tax|Real Estate Tax',
            'corporate': r'Corporate Tax|Company Tax|Business Tax',
            'stamp_duty': r'Stamp Dut(?:y|ies)|Stamp Tax',
            'withholding': r'Withholding Tax',
            'transfer_pricing': r'Transfer Pricing'
        }
        
        # Version/Revision patterns
        self.version_patterns = {
            'version': r'Version\s*[:\s]*([0-9.]+)',
            'revision': r'Rev(?:ision)?\s*[:\s]*([0-9.]+)',
            'edition': r'(\d+)(?:st|nd|rd|th)\s+Edition',
            'supersedes': r'Supersedes?\s*[:\s]*([^,\n]+)'
        }
        
        # Section patterns
        self.section_patterns = {
            'numbered': r'^(\d+(?:\.\d+)*)\s+([A-Z][^.!?\n]+)',
            'part': r'^Part\s+([IVX]+|\d+)[:\s]+([^.!?\n]+)',
            'chapter': r'^Chapter\s+(\d+)[:\s]+([^.!?\n]+)',
            'appendix': r'^Appendix\s+([A-Z\d]+)[:\s]+([^.!?\n]+)',
            'annex': r'^Annex\s+([A-Z\d]+)[:\s]+([^.!?\n]+)'
        }
        
        # Relief and deduction patterns
        self.relief_patterns = [
            r'([A-Za-z\s]+)\s+Relief',
            r'([A-Za-z\s]+)\s+Deduction',
            r'([A-Za-z\s]+)\s+Allowance',
            r'([A-Za-z\s]+)\s+Rebate',
            r'([A-Za-z\s]+)\s+Exemption'
        ]
        
        # Rate patterns
        self.rate_patterns = [
            r'(\d+(?:\.\d+)?)\s*%',
            r'tax rate[s]?\s*(?:of|:)?\s*(\d+(?:\.\d+)?)\s*%',
            r'(\d+(?:\.\d+)?)\s*percent'
        ]
    
    def extract_metadata(self, text: str, filename: str = "") -> DocumentMetadata:
        """
        Extract comprehensive metadata from document text.
        
        Args:
            text: The document text
            filename: Optional filename for additional context
            
        Returns:
            DocumentMetadata object with extracted information
        """
        metadata = DocumentMetadata()
        
        # Extract from filename if available
        if filename:
            metadata = self._extract_from_filename(filename, metadata)
        
        # Extract title
        metadata.title = self._extract_title(text)
        
        # Extract document type
        metadata.document_type = self._identify_document_type(text)
        
        # Extract dates
        metadata = self._extract_dates(text, metadata)
        
        # Extract Year of Assessment
        metadata.year_of_assessment = self._extract_year_of_assessment(text)
        
        # Extract tax category
        metadata.tax_category = self._identify_tax_category(text)
        
        # Extract version information
        metadata = self._extract_version_info(text, metadata)
        
        # Extract sections
        metadata.sections = self._extract_sections(text)
        
        # Extract legal references
        metadata = self._extract_legal_references(text, metadata)
        
        # Extract content indicators
        metadata = self._extract_content_indicators(text, metadata)
        
        # Determine subcategory
        metadata.subcategory = self._determine_subcategory(text, metadata)
        
        return metadata
    
    def _extract_from_filename(self, filename: str, metadata: DocumentMetadata) -> DocumentMetadata:
        """Extract metadata from filename."""
        # Extract year from filename
        year_match = re.search(r'(\d{4})', filename)
        if year_match:
            year = year_match.group(1)
            if 1990 <= int(year) <= 2030:  # Reasonable year range
                if not metadata.year_of_assessment:
                    metadata.year_of_assessment = [year]
        
        # Extract document ID if present
        id_match = re.search(r'[A-Z]{2,}\d+[A-Z]*', filename)
        if id_match:
            metadata.document_id = id_match.group(0)
        
        return metadata
    
    def _extract_title(self, text: str) -> str:
        """Extract document title from the beginning of text."""
        # Look for title in first 500 characters
        first_part = text[:500]
        lines = first_part.split('\n')
        
        # Common title patterns
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line and len(line) > 10:
                # Check for IRAS or tax-related keywords
                if any(keyword in line.upper() for keyword in ['IRAS', 'TAX', 'GST', 'GUIDE', 'CIRCULAR']):
                    # Clean up the title
                    title = re.sub(r'\s+', ' ', line)
                    title = title.strip('.,;:')
                    return title
        
        # Fallback to first substantial line
        for line in lines:
            if line.strip() and len(line.strip()) > 20:
                return line.strip()[:200]
        
        return "Untitled Document"
    
    def _identify_document_type(self, text: str) -> str:
        """Identify the type of document."""
        text_sample = text[:2000].lower()  # Check first 2000 chars
        
        for doc_type, pattern in self.doc_type_patterns.items():
            if re.search(pattern, text_sample, re.IGNORECASE):
                return doc_type.replace('_', '-')
        
        # Check for common indicators
        if 'guide' in text_sample:
            return 'guide'
        elif 'form' in text_sample and ('fill' in text_sample or 'submit' in text_sample):
            return 'form'
        elif 'act' in text_sample and 'section' in text_sample:
            return 'legislation'
        
        return 'general'
    
    def _extract_dates(self, text: str, metadata: DocumentMetadata) -> DocumentMetadata:
        """Extract various dates from the document."""
        # Look for publication date
        pub_patterns = [
            r'Published[:\s]+' + self.date_patterns['full_date'],
            r'Issue[d]?[:\s]+' + self.date_patterns['full_date'],
            r'Date[d]?[:\s]+' + self.date_patterns['full_date']
        ]
        
        for pattern in pub_patterns:
            match = re.search(pattern, text[:1000], re.IGNORECASE)
            if match:
                metadata.publication_date = match.group(0).split(':')[-1].strip()
                break
        
        # Look for last updated date
        update_patterns = [
            r'Last [Uu]pdated[:\s]*' + self.date_patterns['full_date'],
            r'Updated[:\s]+' + self.date_patterns['full_date'],
            r'Revised[:\s]+' + self.date_patterns['full_date']
        ]
        
        for pattern in update_patterns:
            match = re.search(pattern, text[:1000], re.IGNORECASE)
            if match:
                metadata.last_updated = re.search(self.date_patterns['full_date'], match.group(0)).group(0)
                break
        
        # Look for effective date
        effective_patterns = [
            r'Effective[:\s]+(?:from[:\s]+)?' + self.date_patterns['full_date'],
            r'With effect from[:\s]+' + self.date_patterns['full_date'],
            r'Effective from[:\s]+' + self.date_patterns['full_date']
        ]
        
        for pattern in effective_patterns:
            match = re.search(pattern, text[:2000], re.IGNORECASE)
            if match:
                metadata.effective_date = re.search(self.date_patterns['full_date'], match.group(0)).group(0)
                break
        
        return metadata
    
    def _extract_year_of_assessment(self, text: str) -> List[str]:
        """Extract Year of Assessment information."""
        years = set()
        
        # Look for explicit YA mentions
        for pattern_name, pattern in self.ya_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if pattern_name == 'range':
                    # Add all years in range
                    start_year = int(match.group(1))
                    end_year = int(match.group(2))
                    for year in range(start_year, end_year + 1):
                        years.add(str(year))
                else:
                    years.add(match.group(1))
        
        return sorted(list(years))
    
    def _identify_tax_category(self, text: str) -> str:
        """Identify the primary tax category."""
        text_sample = text[:3000].lower()
        
        # Count occurrences of each category
        category_counts = {}
        for category, pattern in self.tax_category_patterns.items():
            matches = re.findall(pattern, text_sample, re.IGNORECASE)
            category_counts[category] = len(matches)
        
        # Return the most frequently mentioned category
        if category_counts:
            return max(category_counts, key=category_counts.get)
        
        return 'general'
    
    def _extract_version_info(self, text: str, metadata: DocumentMetadata) -> DocumentMetadata:
        """Extract version and revision information."""
        text_sample = text[:1000]
        
        for version_type, pattern in self.version_patterns.items():
            match = re.search(pattern, text_sample, re.IGNORECASE)
            if match:
                if version_type == 'version':
                    metadata.version = match.group(1)
                elif version_type == 'revision':
                    metadata.revision = match.group(1)
                elif version_type == 'supersedes':
                    metadata.supersedes = match.group(1).strip()
        
        return metadata
    
    def _extract_sections(self, text: str) -> List[str]:
        """Extract section headers from the document."""
        sections = []
        
        # Look for various section patterns
        for section_type, pattern in self.section_patterns.items():
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                if section_type in ['numbered', 'part', 'chapter']:
                    section_id = match.group(1)
                    section_title = match.group(2).strip()
                    sections.append(f"{section_id}: {section_title}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_sections = []
        for section in sections:
            if section not in seen:
                seen.add(section)
                unique_sections.append(section)
        
        return unique_sections[:20]  # Return first 20 sections
    
    def _extract_legal_references(self, text: str, metadata: DocumentMetadata) -> DocumentMetadata:
        """Extract references to acts and circulars."""
        # Extract Act references
        act_pattern = r'(?:Income Tax Act|GST Act|Property Tax Act|Stamp Duties Act)(?:\s+\([^)]+\))?'
        act_matches = re.findall(act_pattern, text)
        metadata.act_references = list(set(act_matches))[:5]
        
        # Extract Circular references
        circular_pattern = r'Circular\s+(?:No\.\s*)?([A-Z0-9/\-]+)'
        circular_matches = re.findall(circular_pattern, text)
        metadata.circular_references = list(set(circular_matches))[:5]
        
        return metadata
    
    def _extract_content_indicators(self, text: str, metadata: DocumentMetadata) -> DocumentMetadata:
        """Extract content indicators like rates, reliefs, etc."""
        # Check for tables
        metadata.has_tables = bool(re.search(r'\|.*\|', text))
        
        # Check for forms
        metadata.has_forms = bool(re.search(r'Form [A-Z0-9]|Annex [A-Z]|Appendix [A-Z\d]', text))
        
        # Check for examples
        metadata.has_examples = bool(re.search(r'Example \d+|Example:|For example', text, re.IGNORECASE))
        
        # Extract tax rates mentioned
        rate_matches = []
        for pattern in self.rate_patterns:
            matches = re.findall(pattern, text)
            rate_matches.extend(matches)
        metadata.tax_rates_mentioned = list(set(rate_matches))[:10]
        
        # Extract reliefs mentioned
        relief_matches = []
        for pattern in self.relief_patterns:
            matches = re.findall(pattern, text)
            relief_matches.extend([m.strip() for m in matches if len(m.strip()) > 3])
        metadata.reliefs_mentioned = list(set(relief_matches))[:10]
        
        # Extract keywords (common tax terms)
        keywords = []
        keyword_patterns = [
            'deduction', 'exemption', 'relief', 'allowance', 'rebate',
            'assessment', 'chargeable', 'taxable', 'resident', 'non-resident',
            'filing', 'submission', 'penalty', 'compliance'
        ]
        for keyword in keyword_patterns:
            if keyword in text.lower():
                keywords.append(keyword)
        metadata.keywords = keywords
        
        return metadata
    
    def _determine_subcategory(self, text: str, metadata: DocumentMetadata) -> str:
        """Determine the subcategory based on content."""
        text_lower = text[:3000].lower()
        
        if metadata.tax_category == 'income':
            if 'individual' in text_lower or 'personal' in text_lower:
                return 'individual'
            elif 'employment' in text_lower:
                return 'employment'
            elif 'self-employed' in text_lower:
                return 'self-employed'
        elif metadata.tax_category == 'gst':
            if 'registration' in text_lower:
                return 'registration'
            elif 'filing' in text_lower or 'return' in text_lower:
                return 'filing'
            elif 'import' in text_lower or 'export' in text_lower:
                return 'international'
        elif metadata.tax_category == 'property':
            if 'residential' in text_lower:
                return 'residential'
            elif 'commercial' in text_lower or 'industrial' in text_lower:
                return 'commercial'
        
        return 'general'
    
    def format_metadata_summary(self, metadata: DocumentMetadata) -> str:
        """Format metadata into a readable summary."""
        summary = []
        summary.append(f"📄 Document: {metadata.title}")
        summary.append(f"   Type: {metadata.document_type}")
        summary.append(f"   Category: {metadata.tax_category}")
        
        if metadata.year_of_assessment:
            summary.append(f"   Year(s): {', '.join(metadata.year_of_assessment)}")
        
        if metadata.last_updated:
            summary.append(f"   Updated: {metadata.last_updated}")
        
        if metadata.version:
            summary.append(f"   Version: {metadata.version}")
        
        if metadata.sections:
            summary.append(f"   Sections: {len(metadata.sections)}")
        
        if metadata.has_tables:
            summary.append("   ✓ Contains tables")
        
        if metadata.tax_rates_mentioned:
            summary.append(f"   Rates: {', '.join(metadata.tax_rates_mentioned[:3])}")
        
        return '\n'.join(summary)


def test_metadata_extraction():
    """Test the metadata extractor."""
    print("\n" + "="*60)
    print("TESTING METADATA EXTRACTION")
    print("="*60)
    
    extractor = MetadataExtractor()
    
    # Test document 1: Income Tax Guide
    test_doc1 = """
    IRAS e-Tax Guide
    INCOME TAX TREATMENT OF INDIVIDUALS
    Last Updated: 15 January 2024
    Year of Assessment 2024
    Version 2.1
    
    This guide supersedes the version dated 1 January 2023.
    
    1. Introduction
    This guide provides information on income tax for individuals.
    
    2. Tax Rates
    The tax rate for residents ranges from 0% to 24%.
    
    3. Reliefs Available
    - Earned Income Relief
    - Parent Relief
    - Child Relief
    """
    
    metadata1 = extractor.extract_metadata(test_doc1, "IRAS_Income_Tax_Guide_2024.pdf")
    print("\n" + extractor.format_metadata_summary(metadata1))
    
    # Test document 2: GST Circular
    test_doc2 = """
    IRAS Circular No. GST/2024/03
    
    GOODS AND SERVICES TAX
    GST Registration Requirements
    
    Published: 1 March 2024
    Effective from: 1 April 2024
    
    This circular clarifies the GST registration threshold of $1 million.
    The GST rate remains at 9%.
    """
    
    metadata2 = extractor.extract_metadata(test_doc2, "GST_Circular_2024_03.pdf")
    print("\n" + extractor.format_metadata_summary(metadata2))
    
    print("\n" + "="*60)
    print("✅ METADATA EXTRACTION TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    test_metadata_extraction()