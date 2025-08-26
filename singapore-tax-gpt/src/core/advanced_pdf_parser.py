"""Advanced PDF Parser for IRAS Documents with Table Preservation and Structure Detection."""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import pdfplumber
from langchain.schema import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ParsedSection:
    """Represents a parsed section of an IRAS document."""
    section_number: Optional[str]
    title: str
    content: str
    page_numbers: List[int]
    section_type: str  # 'header', 'content', 'table', 'list', 'example'
    metadata: Dict[str, Any]


class IRASPDFParser:
    """Advanced PDF parser specifically designed for IRAS tax documents."""
    
    def __init__(self):
        """Initialize the IRAS PDF parser."""
        # Regex patterns for IRAS document structures
        self.patterns = {
            'section_header': r'^(\d+(?:\.\d+)*)\s+([A-Z][A-Z\s]+)$',
            'subsection': r'^(\d+\.\d+(?:\.\d+)*)\s+(.+)$',
            'year_assessment': r'(?:YA|Year of Assessment)\s*(\d{4})',
            'date_pattern': r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
            'tax_rate': r'(\d+(?:\.\d+)?)\s*%',
            'amount': r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            'bullet_point': r'^\s*[•·▪▫◦‣⁃]\s+(.+)$',
            'numbered_list': r'^\s*(\d+|[a-z]|[i-v]+)[.)]\s+(.+)$',
            'note_pattern': r'^(?:Note|Important|Reminder|Example)[:.]?\s*(.*)$'
        }
        
        # IRAS document type indicators
        self.doc_type_keywords = {
            'e-tax_guide': ['e-Tax Guide', 'IRAS e-Tax Guide'],
            'circular': ['Circular', 'IRAS Circular'],
            'form': ['Form', 'IRAS Form'],
            'act': ['Income Tax Act', 'GST Act', 'Property Tax Act'],
            'procedure': ['Filing', 'Procedure', 'How to']
        }
        
    def parse_pdf(self, file_path: str) -> List[ParsedSection]:
        """
        Parse an IRAS PDF document into structured sections.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of ParsedSection objects
        """
        logger.info(f"Parsing PDF: {file_path}")
        sections = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                # Extract document metadata
                doc_metadata = self._extract_document_metadata(pdf, file_path)
                
                # Process each page
                for page_num, page in enumerate(pdf.pages, 1):
                    page_sections = self._process_page(page, page_num, doc_metadata)
                    sections.extend(page_sections)
                
                # Post-process to merge related sections
                sections = self._merge_continued_sections(sections)
                
                logger.info(f"Successfully parsed {len(sections)} sections from {len(pdf.pages)} pages")
                
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            raise
        
        return sections
    
    def _extract_document_metadata(self, pdf: Any, file_path: str) -> Dict[str, Any]:
        """Extract metadata from the PDF document."""
        metadata = {
            'file_name': Path(file_path).name,
            'total_pages': len(pdf.pages),
            'doc_type': self._identify_document_type(pdf),
        }
        
        # Try to extract title from first page
        if pdf.pages:
            first_page_text = pdf.pages[0].extract_text() or ""
            lines = first_page_text.split('\n')[:10]  # Check first 10 lines
            
            # Look for title (usually in larger font or all caps)
            for line in lines:
                if line.strip() and len(line) > 10:
                    if line.isupper() or 'IRAS' in line or 'Tax' in line:
                        metadata['title'] = line.strip()
                        break
            
            # Extract Year of Assessment
            ya_match = re.search(self.patterns['year_assessment'], first_page_text)
            if ya_match:
                metadata['year_assessment'] = ya_match.group(1)
            
            # Extract last updated date
            date_matches = re.findall(self.patterns['date_pattern'], first_page_text)
            if date_matches:
                metadata['last_updated'] = date_matches[0]
        
        return metadata
    
    def _identify_document_type(self, pdf: Any) -> str:
        """Identify the type of IRAS document."""
        # Sample first few pages for type identification
        sample_text = ""
        for page in pdf.pages[:3]:
            text = page.extract_text()
            if text:
                sample_text += text[:1000]
        
        for doc_type, keywords in self.doc_type_keywords.items():
            for keyword in keywords:
                if keyword.lower() in sample_text.lower():
                    return doc_type
        
        return 'general'
    
    def _process_page(self, page: Any, page_num: int, doc_metadata: Dict) -> List[ParsedSection]:
        """Process a single page and extract sections."""
        sections = []
        
        # Extract text
        text = page.extract_text()
        if not text:
            return sections
        
        # Extract tables separately
        tables = page.extract_tables()
        if tables:
            for table_idx, table in enumerate(tables):
                table_section = self._process_table(table, page_num, table_idx)
                if table_section:
                    sections.append(table_section)
        
        # Process text content
        lines = text.split('\n')
        current_section = None
        buffer = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a section header
            header_match = re.match(self.patterns['section_header'], line)
            subsection_match = re.match(self.patterns['subsection'], line)
            
            if header_match or subsection_match:
                # Save previous section if exists
                if current_section and buffer:
                    current_section.content = '\n'.join(buffer)
                    sections.append(current_section)
                    buffer = []
                
                # Start new section
                if header_match:
                    current_section = ParsedSection(
                        section_number=header_match.group(1),
                        title=header_match.group(2),
                        content="",
                        page_numbers=[page_num],
                        section_type='header',
                        metadata=doc_metadata.copy()
                    )
                else:
                    current_section = ParsedSection(
                        section_number=subsection_match.group(1),
                        title=subsection_match.group(2),
                        content="",
                        page_numbers=[page_num],
                        section_type='content',
                        metadata=doc_metadata.copy()
                    )
            else:
                # Add to current buffer
                buffer.append(line)
                
                # Detect special content types
                if re.match(self.patterns['bullet_point'], line):
                    if current_section:
                        current_section.section_type = 'list'
                elif re.match(self.patterns['note_pattern'], line):
                    if current_section:
                        current_section.metadata['has_note'] = True
        
        # Save last section
        if current_section and buffer:
            current_section.content = '\n'.join(buffer)
            sections.append(current_section)
        
        # If no sections were found, create a general content section
        if not sections and text.strip():
            sections.append(ParsedSection(
                section_number=None,
                title=f"Page {page_num} Content",
                content=text.strip(),
                page_numbers=[page_num],
                section_type='content',
                metadata=doc_metadata.copy()
            ))
        
        return sections
    
    def _process_table(self, table: List[List[str]], page_num: int, table_idx: int) -> Optional[ParsedSection]:
        """Process a table and convert it to a structured section."""
        if not table or not table[0]:
            return None
        
        # Format table as markdown for better readability
        formatted_table = []
        
        # Assume first row is header
        headers = [str(cell).strip() if cell else '' for cell in table[0]]
        formatted_table.append(' | '.join(headers))
        formatted_table.append(' | '.join(['---'] * len(headers)))
        
        # Add data rows
        for row in table[1:]:
            cells = [str(cell).strip() if cell else '' for cell in row]
            # Pad row if necessary
            while len(cells) < len(headers):
                cells.append('')
            formatted_table.append(' | '.join(cells[:len(headers)]))
        
        # Determine table type based on content
        table_text = '\n'.join(formatted_table)
        table_type = 'table'
        
        # Check if it's a tax rate table
        if re.search(self.patterns['tax_rate'], table_text) and re.search(self.patterns['amount'], table_text):
            table_type = 'tax_rate_table'
        
        return ParsedSection(
            section_number=None,
            title=f"Table {table_idx + 1} (Page {page_num})",
            content=table_text,
            page_numbers=[page_num],
            section_type=table_type,
            metadata={'is_table': True, 'table_headers': headers}
        )
    
    def _merge_continued_sections(self, sections: List[ParsedSection]) -> List[ParsedSection]:
        """Merge sections that continue across pages."""
        if not sections:
            return sections
        
        merged = []
        current = sections[0]
        
        for section in sections[1:]:
            # Check if this section continues the previous one
            if (current.section_number and 
                section.section_number == current.section_number and 
                section.title == current.title):
                # Merge content
                current.content += '\n' + section.content
                current.page_numbers.extend(section.page_numbers)
            else:
                merged.append(current)
                current = section
        
        merged.append(current)
        return merged
    
    def sections_to_documents(self, sections: List[ParsedSection]) -> List[Document]:
        """Convert ParsedSections to LangChain Documents."""
        documents = []
        
        for section in sections:
            # Create comprehensive metadata (ChromaDB requires simple types)
            metadata = {
                'source': section.metadata.get('file_name', 'unknown'),
                'title': section.metadata.get('title', ''),
                'section_number': section.section_number or '',
                'section_title': section.title,
                'pages': str(section.page_numbers),  # Convert list to string for ChromaDB
                'page_start': min(section.page_numbers) if section.page_numbers else 0,
                'page_end': max(section.page_numbers) if section.page_numbers else 0,
                'section_type': section.section_type,
                'doc_type': section.metadata.get('doc_type', 'general'),
                'year_assessment': section.metadata.get('year_assessment', ''),
                'last_updated': section.metadata.get('last_updated', ''),
                'is_table': section.metadata.get('is_table', False)
            }
            
            # Format content with section header for context
            if section.section_number:
                content = f"Section {section.section_number}: {section.title}\n\n{section.content}"
            else:
                content = f"{section.title}\n\n{section.content}"
            
            documents.append(Document(
                page_content=content,
                metadata=metadata
            ))
        
        return documents


def test_parser():
    """Test the IRAS PDF parser with a sample document."""
    parser = IRASPDFParser()
    
    # Create a test PDF path (you would use a real IRAS PDF here)
    test_file = "./data/iras_docs/sample.pdf"
    
    if Path(test_file).exists():
        sections = parser.parse_pdf(test_file)
        
        print(f"Parsed {len(sections)} sections:")
        for i, section in enumerate(sections[:5]):  # Show first 5 sections
            print(f"\n--- Section {i+1} ---")
            print(f"Type: {section.section_type}")
            print(f"Number: {section.section_number}")
            print(f"Title: {section.title}")
            print(f"Pages: {section.page_numbers}")
            print(f"Content preview: {section.content[:200]}...")
            
        # Convert to documents
        documents = parser.sections_to_documents(sections)
        print(f"\nConverted to {len(documents)} LangChain documents")
    else:
        print(f"Test file {test_file} not found. Parser is ready for real IRAS PDFs.")


if __name__ == "__main__":
    test_parser()