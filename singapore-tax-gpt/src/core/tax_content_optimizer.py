"""Tax-specific content optimization for better chunking and retrieval."""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class TaxContentSection:
    """Represents a tax-specific content section."""
    content: str
    section_type: str
    priority: int  # 1-10, higher is more important
    preserve_whole: bool
    metadata: Dict[str, Any]


class TaxContentOptimizer:
    """Optimizes content specifically for Singapore tax documents."""
    
    def __init__(self):
        """Initialize the optimizer with tax-specific patterns."""
        self._initialize_patterns()
        self._initialize_rules()
    
    def _initialize_patterns(self):
        """Initialize tax-specific patterns."""
        # Critical content patterns that should be preserved
        self.critical_patterns = {
            'tax_rate_table': r'(?:Tax\s+Rates?|Rate\s+Table)[\s\S]*?(?:\n\n|\Z)',
            'relief_table': r'(?:Tax\s+Reliefs?|Relief\s+Table)[\s\S]*?(?:\n\n|\Z)',
            'calculation_example': r'(?:Example\s+\d+|Illustration)[\s\S]*?(?=Example\s+\d+|\n\n|\Z)',
            'formula': r'(?:Formula|Calculation)[\s\S]*?(?:\n\n|\Z)',
            'definition': r'(?:Definition[s]?|"[^"]+"\s+means)[\s\S]*?(?:\n\n|\Z)',
            'timeline': r'(?:Timeline|Deadline[s]?|Key\s+Date[s]?)[\s\S]*?(?:\n\n|\Z)',
            'eligibility': r'(?:Eligibl[e|ility]|Qualifying\s+Conditions?)[\s\S]*?(?:\n\n|\Z)',
            'compliance': r'(?:Compliance|Requirement[s]?)[\s\S]*?(?:\n\n|\Z)'
        }
        
        # Tax computation patterns
        self.computation_patterns = {
            'rate_structure': r'\d+(?:\.\d+)?%\s+(?:on|for|of)',
            'amount_threshold': r'\$[\d,]+(?:\.\d+)?',
            'year_reference': r'(?:YA|Year\s+of\s+Assessment)\s*\d{4}',
            'section_reference': r'(?:Section|Regulation|Rule)\s+\d+[A-Za-z]?',
            'form_reference': r'(?:Form|Appendix)\s+[A-Z0-9]+',
            'circular_reference': r'Circular\s+No\.\s*\d+/\d+'
        }
        
        # Content boundaries
        self.boundary_patterns = {
            'section_start': r'^(?:\d+\.|\([a-z]\)|\([ivx]+\))\s+',
            'subsection': r'^\s{2,}(?:\d+\.|\([a-z]\))',
            'list_item': r'^(?:[-•*]|\d+\.)\s+',
            'table_start': r'(?:^\||\+-{3,})',
            'note_start': r'^(?:Note[s]?:|Important:|Remark[s]?:)',
            'example_start': r'^(?:Example\s+\d+:|Illustration:)'
        }
    
    def _initialize_rules(self):
        """Initialize optimization rules."""
        self.optimization_rules = {
            'preserve_tables': True,
            'preserve_examples': True,
            'preserve_formulas': True,
            'preserve_definitions': True,
            'group_related_sections': True,
            'maintain_context': True,
            'optimize_for_qa': True
        }
        
        # Chunk size recommendations by content type
        self.size_recommendations = {
            'tax_rate_table': (500, 3000),     # (min, max) characters
            'calculation_example': (300, 2000),
            'definition': (100, 1000),
            'general_text': (500, 1500),
            'formula': (100, 800),
            'compliance': (400, 1800),
            'eligibility': (300, 1500)
        }
    
    def optimize_content(self, text: str, doc_type: str = 'general') -> List[TaxContentSection]:
        """
        Optimize content for tax-specific chunking.
        
        Args:
            text: Raw text content
            doc_type: Type of document (act, guide, form, etc.)
            
        Returns:
            List of optimized content sections
        """
        sections = []
        
        # First, identify and extract critical sections
        critical_sections = self._extract_critical_sections(text)
        sections.extend(critical_sections)
        
        # Remove extracted sections from text
        remaining_text = text
        for section in critical_sections:
            remaining_text = remaining_text.replace(section.content, '')
        
        # Process remaining text
        if remaining_text.strip():
            regular_sections = self._process_regular_content(remaining_text, doc_type)
            sections.extend(regular_sections)
        
        # Apply optimization rules
        sections = self._apply_optimization_rules(sections)
        
        # Sort by position and priority
        sections = self._sort_and_prioritize(sections, text)
        
        return sections
    
    def _extract_critical_sections(self, text: str) -> List[TaxContentSection]:
        """Extract critical sections that should be preserved."""
        sections = []
        
        for section_type, pattern in self.critical_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                content = match.group(0).strip()
                
                # Skip if too short
                if len(content) < 50:
                    continue
                
                # Determine if should preserve whole
                preserve = self._should_preserve_whole(content, section_type)
                
                # Extract metadata
                metadata = self._extract_section_metadata(content, section_type)
                
                section = TaxContentSection(
                    content=content,
                    section_type=section_type,
                    priority=self._calculate_priority(section_type, content),
                    preserve_whole=preserve,
                    metadata=metadata
                )
                sections.append(section)
        
        return sections
    
    def _process_regular_content(self, text: str, doc_type: str) -> List[TaxContentSection]:
        """Process regular content that isn't critical."""
        sections = []
        
        # Split by major sections
        section_splits = re.split(r'\n(?=\d+\.\s+[A-Z])', text)
        
        for split in section_splits:
            if not split.strip():
                continue
            
            # Determine section type
            section_type = self._identify_section_type(split)
            
            # Check if needs further splitting
            min_size, max_size = self.size_recommendations.get(
                section_type, 
                self.size_recommendations['general_text']
            )
            
            if len(split) > max_size:
                # Split further by paragraphs
                subsections = self._smart_split(split, min_size, max_size)
                for subsection in subsections:
                    sections.append(TaxContentSection(
                        content=subsection,
                        section_type=section_type,
                        priority=5,  # Default priority
                        preserve_whole=False,
                        metadata={}
                    ))
            else:
                sections.append(TaxContentSection(
                    content=split,
                    section_type=section_type,
                    priority=5,
                    preserve_whole=len(split) < min_size * 1.5,
                    metadata={}
                ))
        
        return sections
    
    def _should_preserve_whole(self, content: str, section_type: str) -> bool:
        """Determine if content should be preserved as whole."""
        # Always preserve small critical sections
        if len(content) < 500 and section_type in ['formula', 'definition']:
            return True
        
        # Check for tables
        if '|' in content or re.search(r'\+-{3,}', content):
            return True
        
        # Check for complete examples
        if section_type == 'calculation_example':
            # Has both setup and result
            if 'therefore' in content.lower() or 'result' in content.lower():
                return True
        
        # Check size limits
        min_size, max_size = self.size_recommendations.get(
            section_type,
            (500, 1500)
        )
        
        return len(content) <= max_size
    
    def _extract_section_metadata(self, content: str, section_type: str) -> Dict[str, Any]:
        """Extract metadata from section content."""
        metadata = {
            'section_type': section_type,
            'char_count': len(content),
            'has_table': bool(re.search(r'\||\+-{3,}', content)),
            'has_formula': bool(re.search(r'[=+\-*/]', content)),
            'has_amounts': bool(re.search(r'\$[\d,]+', content)),
            'has_percentages': bool(re.search(r'\d+(?:\.\d+)?%', content))
        }
        
        # Extract specific references
        year_refs = re.findall(r'(?:YA\s*)?(\d{4})', content)
        if year_refs:
            metadata['years'] = list(set(year_refs))
        
        section_refs = re.findall(r'Section\s+(\d+[A-Za-z]?)', content)
        if section_refs:
            metadata['section_refs'] = section_refs
        
        form_refs = re.findall(r'Form\s+([A-Z0-9]+)', content)
        if form_refs:
            metadata['form_refs'] = form_refs
        
        return metadata
    
    def _calculate_priority(self, section_type: str, content: str) -> int:
        """Calculate priority score for a section."""
        base_priority = {
            'tax_rate_table': 10,
            'relief_table': 9,
            'calculation_example': 8,
            'formula': 8,
            'definition': 7,
            'eligibility': 7,
            'timeline': 6,
            'compliance': 6
        }.get(section_type, 5)
        
        # Adjust based on content
        if re.search(r'\bcurrent\b|\blatest\b|\b2024\b', content, re.IGNORECASE):
            base_priority += 1
        
        if re.search(r'\bimportant\b|\bcritical\b|\bmust\b', content, re.IGNORECASE):
            base_priority += 1
        
        return min(base_priority, 10)
    
    def _identify_section_type(self, text: str) -> str:
        """Identify the type of a text section."""
        text_lower = text.lower()[:500]  # Check first 500 chars
        
        if 'tax rate' in text_lower or 'rate table' in text_lower:
            return 'tax_rate_table'
        elif 'example' in text_lower or 'illustration' in text_lower:
            return 'calculation_example'
        elif 'definition' in text_lower or 'means' in text_lower:
            return 'definition'
        elif 'formula' in text_lower or 'calculation' in text_lower:
            return 'formula'
        elif 'eligible' in text_lower or 'qualify' in text_lower:
            return 'eligibility'
        elif 'compliance' in text_lower or 'requirement' in text_lower:
            return 'compliance'
        elif 'deadline' in text_lower or 'timeline' in text_lower:
            return 'timeline'
        else:
            return 'general_text'
    
    def _smart_split(self, text: str, min_size: int, max_size: int) -> List[str]:
        """Smart splitting that respects content boundaries."""
        chunks = []
        current_chunk = ""
        
        # Try splitting by paragraphs first
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if len(current_chunk) + len(para) <= max_size:
                current_chunk += para + '\n\n'
            else:
                if current_chunk and len(current_chunk) >= min_size:
                    chunks.append(current_chunk.strip())
                    current_chunk = para + '\n\n'
                else:
                    # Para too large, split by sentences
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) <= max_size:
                            current_chunk += sentence + ' '
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence + ' '
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _apply_optimization_rules(self, sections: List[TaxContentSection]) -> List[TaxContentSection]:
        """Apply optimization rules to sections."""
        optimized = []
        
        i = 0
        while i < len(sections):
            section = sections[i]
            
            # Group related sections if enabled
            if self.optimization_rules['group_related_sections']:
                # Look for related next section
                if i + 1 < len(sections):
                    next_section = sections[i + 1]
                    if self._are_related(section, next_section):
                        # Merge if combined size is reasonable
                        combined_size = len(section.content) + len(next_section.content)
                        max_size = self.size_recommendations.get(
                            section.section_type,
                            (500, 1500)
                        )[1]
                        
                        if combined_size <= max_size * 1.2:  # Allow 20% overflow
                            # Merge sections
                            merged = TaxContentSection(
                                content=f"{section.content}\n\n{next_section.content}",
                                section_type=section.section_type,
                                priority=max(section.priority, next_section.priority),
                                preserve_whole=section.preserve_whole or next_section.preserve_whole,
                                metadata={**section.metadata, **next_section.metadata}
                            )
                            optimized.append(merged)
                            i += 2
                            continue
            
            optimized.append(section)
            i += 1
        
        return optimized
    
    def _are_related(self, section1: TaxContentSection, section2: TaxContentSection) -> bool:
        """Check if two sections are related."""
        # Same type
        if section1.section_type == section2.section_type:
            return True
        
        # Sequential examples
        if 'example' in section1.section_type and 'example' in section2.section_type:
            return True
        
        # Definition followed by example
        if section1.section_type == 'definition' and section2.section_type == 'calculation_example':
            return True
        
        # Check for explicit references
        if any(ref in section2.content[:100] for ref in ['above', 'previous', 'following']):
            return True
        
        return False
    
    def _sort_and_prioritize(self, sections: List[TaxContentSection], original_text: str) -> List[TaxContentSection]:
        """Sort sections by original position and priority."""
        # Add position information
        for section in sections:
            pos = original_text.find(section.content[:50])
            section.metadata['position'] = pos if pos != -1 else float('inf')
        
        # Sort by position
        sections.sort(key=lambda s: s.metadata.get('position', float('inf')))
        
        return sections
    
    def optimize_for_retrieval(self, sections: List[TaxContentSection]) -> List[Dict[str, Any]]:
        """
        Optimize sections for RAG retrieval.
        
        Returns sections formatted for vector store with enhanced metadata.
        """
        optimized = []
        
        for section in sections:
            # Add context from surrounding sections if needed
            context = ""
            if section.metadata.get('position', 0) > 0:
                context = self._get_context_snippet(sections, section)
            
            doc = {
                'content': section.content,
                'metadata': {
                    'section_type': section.section_type,
                    'priority': section.priority,
                    'preserve_whole': section.preserve_whole,
                    'context': context,
                    **section.metadata
                }
            }
            
            # Add retrieval hints
            if section.section_type == 'tax_rate_table':
                doc['metadata']['search_keywords'] = ['tax rate', 'rate table', 'percentage']
            elif section.section_type == 'calculation_example':
                doc['metadata']['search_keywords'] = ['example', 'calculation', 'how to']
            elif section.section_type == 'eligibility':
                doc['metadata']['search_keywords'] = ['eligible', 'qualify', 'criteria']
            
            optimized.append(doc)
        
        return optimized
    
    def _get_context_snippet(self, sections: List[TaxContentSection], current: TaxContentSection) -> str:
        """Get context snippet from surrounding sections."""
        current_pos = current.metadata.get('position', 0)
        context_parts = []
        
        # Find previous section
        for section in sections:
            if section.metadata.get('position', 0) < current_pos:
                # Get last 100 chars of previous section
                context_parts.append(f"...{section.content[-100:].strip()}")
                break
        
        return ' '.join(context_parts) if context_parts else ""