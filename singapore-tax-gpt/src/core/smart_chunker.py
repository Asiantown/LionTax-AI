"""Smart Chunking Strategy for IRAS Documents - Preserves Structure and Context."""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import logging
from langchain.schema import Document
from langchain.text_splitter import TextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ChunkMetadata:
    """Metadata for a chunk to track its characteristics."""
    chunk_type: str  # 'table', 'list', 'section', 'paragraph'
    has_table: bool
    has_list: bool
    section_level: int
    semantic_completeness: float  # 0-1 score of how complete the chunk is
    overlap_context: str  # Context from previous chunk


class SmartTaxChunker(TextSplitter):
    """
    Smart chunking specifically designed for Singapore tax documents.
    Preserves tables, lists, and logical sections.
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100,
        max_chunk_size: int = 3000,
        preserve_tables: bool = True,
        preserve_lists: bool = True,
        preserve_sections: bool = True
    ):
        """Initialize the smart chunker."""
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.preserve_tables = preserve_tables
        self.preserve_lists = preserve_lists
        self.preserve_sections = preserve_sections
        
        # Patterns for detecting structure
        self.patterns = {
            'table_start': r'^\|.*\|$|^[\s]*\+[-+]+\+$',
            'table_row': r'^\|.*\|$',
            'list_item': r'^\s*[•·▪▫◦‣⁃\-\*]\s+|^\s*\d+[.)]\s+|^\s*[a-z][.)]\s+',
            'section_header': r'^(?:Part|Section|Chapter|\d+\.)\s+[A-Z]',
            'subsection': r'^\d+\.\d+(?:\.\d+)*\s+',
            'paragraph_end': r'[.!?]\s*$',
            'tax_rate_mention': r'\d+(?:\.\d+)?%|\$\d+',
            'definition': r'^"[^"]+"?\s+means',
            'note_or_example': r'^(?:Note|Example|Important)[:.]',
        }
        
    def split_text(self, text: str) -> List[str]:
        """
        Split text using smart chunking strategy.
        
        Args:
            text: The text to split
            
        Returns:
            List of text chunks
        """
        # First, identify structural elements
        elements = self._identify_elements(text)
        
        # Then, group elements into chunks
        chunks = self._group_into_chunks(elements)
        
        # Finally, add overlap context
        chunks = self._add_overlap_context(chunks)
        
        return chunks
    
    def _identify_elements(self, text: str) -> List[Dict[str, Any]]:
        """Identify structural elements in the text."""
        elements = []
        lines = text.split('\n')
        current_element = {
            'type': 'paragraph',
            'content': [],
            'start_line': 0,
            'metadata': {}
        }
        
        in_table = False
        in_list = False
        
        for i, line in enumerate(lines):
            # Check if this is a table
            if self.preserve_tables and re.match(self.patterns['table_start'], line):
                # Save current element
                if current_element['content']:
                    current_element['content'] = '\n'.join(current_element['content'])
                    elements.append(current_element)
                
                # Start new table element
                current_element = {
                    'type': 'table',
                    'content': [line],
                    'start_line': i,
                    'metadata': {'columns': self._count_table_columns(line)}
                }
                in_table = True
                
            elif in_table and (re.match(self.patterns['table_row'], line) or line.strip().startswith('---')):
                # Continue table
                current_element['content'].append(line)
                
            elif in_table and not re.match(self.patterns['table_row'], line) and not line.strip().startswith('---'):
                # End table
                current_element['content'] = '\n'.join(current_element['content'])
                elements.append(current_element)
                in_table = False
                
                # Start new element
                current_element = {
                    'type': 'paragraph',
                    'content': [line] if line.strip() else [],
                    'start_line': i,
                    'metadata': {}
                }
                
            # Check if this is a list item
            elif self.preserve_lists and re.match(self.patterns['list_item'], line):
                if not in_list:
                    # Save current element
                    if current_element['content']:
                        current_element['content'] = '\n'.join(current_element['content'])
                        elements.append(current_element)
                    
                    # Start new list
                    current_element = {
                        'type': 'list',
                        'content': [line],
                        'start_line': i,
                        'metadata': {'list_type': self._identify_list_type(line)}
                    }
                    in_list = True
                else:
                    # Continue list
                    current_element['content'].append(line)
                    
            elif in_list and not re.match(self.patterns['list_item'], line) and line.strip():
                # Check if this is a continuation of the list item
                if line.startswith('  ') or line.startswith('\t'):
                    current_element['content'].append(line)
                else:
                    # End list
                    current_element['content'] = '\n'.join(current_element['content'])
                    elements.append(current_element)
                    in_list = False
                    
                    # Start new element
                    current_element = {
                        'type': 'paragraph',
                        'content': [line],
                        'start_line': i,
                        'metadata': {}
                    }
                    
            # Check if this is a section header
            elif self.preserve_sections and re.match(self.patterns['section_header'], line):
                # Save current element
                if current_element['content']:
                    current_element['content'] = '\n'.join(current_element['content'])
                    elements.append(current_element)
                
                # Create section header element
                current_element = {
                    'type': 'section_header',
                    'content': line,
                    'start_line': i,
                    'metadata': {'level': self._get_section_level(line)}
                }
                elements.append(current_element)
                
                # Start new paragraph
                current_element = {
                    'type': 'paragraph',
                    'content': [],
                    'start_line': i + 1,
                    'metadata': {}
                }
                
            else:
                # Regular content
                current_element['content'].append(line)
        
        # Save last element
        if current_element['content']:
            if isinstance(current_element['content'], list):
                current_element['content'] = '\n'.join(current_element['content'])
            elements.append(current_element)
        
        return elements
    
    def _group_into_chunks(self, elements: List[Dict[str, Any]]) -> List[str]:
        """Group elements into appropriately sized chunks."""
        chunks = []
        current_chunk = []
        current_size = 0
        
        for element in elements:
            element_text = element['content']
            element_size = len(element_text)
            
            # Special handling for tables and long lists
            if element['type'] in ['table', 'list'] and element_size <= self.max_chunk_size:
                # Keep tables and lists intact if they fit
                if current_chunk:
                    # Save current chunk
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                
                # Add table/list as its own chunk
                chunks.append(element_text)
                
            elif element['type'] == 'section_header':
                # Section headers should start new chunks
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_size = 0
                
                # Add header to new chunk
                current_chunk.append(element_text)
                current_size = element_size
                
            elif current_size + element_size > self.chunk_size:
                # Would exceed chunk size
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                
                # Handle oversized elements
                if element_size > self.max_chunk_size:
                    # Split large element
                    sub_chunks = self._split_large_element(element_text)
                    chunks.extend(sub_chunks)
                    current_chunk = []
                    current_size = 0
                else:
                    current_chunk = [element_text]
                    current_size = element_size
            else:
                # Add to current chunk
                current_chunk.append(element_text)
                current_size += element_size
        
        # Save last chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def _split_large_element(self, text: str) -> List[str]:
        """Split a large element that exceeds max chunk size."""
        # Use sentence splitting for large paragraphs
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            if current_size + len(sentence) > self.chunk_size:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_size = len(sentence)
            else:
                current_chunk.append(sentence)
                current_size += len(sentence)
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _add_overlap_context(self, chunks: List[str]) -> List[str]:
        """Add overlap context between chunks for better retrieval."""
        if not chunks or self.chunk_overlap == 0:
            return chunks
        
        enhanced_chunks = []
        
        for i, chunk in enumerate(chunks):
            if i > 0:
                # Get context from previous chunk
                prev_chunk = chunks[i-1]
                prev_sentences = re.split(r'(?<=[.!?])\s+', prev_chunk)
                
                # Take last sentences from previous chunk as context
                context_size = 0
                context_sentences = []
                
                for sentence in reversed(prev_sentences):
                    if context_size + len(sentence) <= self.chunk_overlap:
                        context_sentences.insert(0, sentence)
                        context_size += len(sentence)
                    else:
                        break
                
                if context_sentences:
                    # Add context marker
                    context = '[Context: ' + ' '.join(context_sentences) + ']\n\n'
                    enhanced_chunk = context + chunk
                else:
                    enhanced_chunk = chunk
            else:
                enhanced_chunk = chunk
            
            enhanced_chunks.append(enhanced_chunk)
        
        return enhanced_chunks
    
    def _count_table_columns(self, line: str) -> int:
        """Count the number of columns in a table row."""
        return line.count('|') - 1 if '|' in line else 0
    
    def _identify_list_type(self, line: str) -> str:
        """Identify the type of list (bullet, numbered, etc.)."""
        if re.match(r'^\s*\d+[.)]\s+', line):
            return 'numbered'
        elif re.match(r'^\s*[a-z][.)]\s+', line):
            return 'alphabetic'
        else:
            return 'bullet'
    
    def _get_section_level(self, line: str) -> int:
        """Determine the hierarchical level of a section."""
        if line.startswith('Part'):
            return 1
        elif line.startswith('Chapter'):
            return 2
        elif line.startswith('Section'):
            return 3
        else:
            # Count dots for subsection level
            dots = line.count('.')
            return min(4 + dots, 6)
    
    def create_documents_with_smart_chunks(
        self,
        text: str,
        metadata: Dict[str, Any]
    ) -> List[Document]:
        """
        Create LangChain documents with smart chunking and metadata.
        
        Args:
            text: The text to chunk
            metadata: Base metadata for all chunks
            
        Returns:
            List of Document objects with smart chunks
        """
        chunks = self.split_text(text)
        documents = []
        
        for i, chunk in enumerate(chunks):
            # Analyze chunk content
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                'chunk_index': i,
                'chunk_type': self._identify_chunk_type(chunk),
                'has_table': bool(re.search(self.patterns['table_row'], chunk)),
                'has_list': bool(re.search(self.patterns['list_item'], chunk)),
                'has_tax_rate': bool(re.search(self.patterns['tax_rate_mention'], chunk)),
                'has_definition': bool(re.search(self.patterns['definition'], chunk)),
                'chunk_size': len(chunk)
            })
            
            documents.append(Document(
                page_content=chunk,
                metadata=chunk_metadata
            ))
        
        return documents
    
    def _identify_chunk_type(self, chunk: str) -> str:
        """Identify the primary type of content in a chunk."""
        if re.search(self.patterns['table_row'], chunk):
            return 'table'
        elif re.search(self.patterns['list_item'], chunk):
            return 'list'
        elif re.search(self.patterns['section_header'], chunk):
            return 'section'
        elif re.search(self.patterns['definition'], chunk):
            return 'definition'
        else:
            return 'content'


def test_smart_chunker():
    """Test the smart chunking strategy."""
    print("\n" + "="*60)
    print("TESTING SMART CHUNKING STRATEGY")
    print("="*60)
    
    # Create test content with various structures
    test_content = """
Part 1: INCOME TAX RATES

The following tax rates apply for Year of Assessment 2024:

| Chargeable Income | Tax Rate | Tax Payable |
| --- | --- | --- |
| First $20,000 | 0% | $0 |
| Next $10,000 | 2% | $200 |
| Next $10,000 | 3.5% | $350 |
| Next $40,000 | 7% | $2,800 |

Section 1.1 Tax Reliefs

The following reliefs are available to resident individuals:

• Earned Income Relief: Up to $1,000 for individuals below 55 years
• Spouse Relief: $2,000 if spouse's income does not exceed $4,000
• Qualifying Child Relief: $4,000 per qualifying child
• Parent Relief: $9,000 if living with parent, $5,500 if not

Note: Total personal reliefs cannot exceed 80% of income.

Section 1.2 Definitions

"Chargeable income" means the income of any person for any year of assessment after deduction of reliefs.

"Resident" means a person who resides in Singapore except for temporary absences.
"""
    
    # Test smart chunker
    chunker = SmartTaxChunker(
        chunk_size=500,
        chunk_overlap=50,
        preserve_tables=True,
        preserve_lists=True,
        preserve_sections=True
    )
    
    chunks = chunker.split_text(test_content)
    
    print(f"\n📊 Chunking Results:")
    print(f"  Original size: {len(test_content)} characters")
    print(f"  Number of chunks: {len(chunks)}")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"\n--- Chunk {i} ({len(chunk)} chars) ---")
        print(chunk[:200] + "..." if len(chunk) > 200 else chunk)
        
        # Analyze chunk
        if '|' in chunk:
            print("  ✅ Table preserved")
        if '•' in chunk:
            print("  ✅ List preserved")
        if 'Section' in chunk or 'Part' in chunk:
            print("  ✅ Section header preserved")
    
    print("\n" + "="*60)
    print("✅ SMART CHUNKING TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    test_smart_chunker()