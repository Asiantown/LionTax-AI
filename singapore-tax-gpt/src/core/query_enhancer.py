"""Query enhancement system for better retrieval and understanding."""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class EnhancedQuery:
    """Enhanced query with extracted components."""
    original_query: str
    normalized_query: str
    query_type: str  # factual, calculation, eligibility, comparison, procedural
    tax_category: str
    year_context: Optional[str]
    entities: Dict[str, List[str]]  # amounts, dates, forms, sections
    keywords: List[str]
    expanded_terms: List[str]
    filters: Dict[str, Any]
    confidence: float


class QueryEnhancer:
    """Enhances user queries for better RAG retrieval."""
    
    def __init__(self):
        """Initialize the query enhancer."""
        self._initialize_patterns()
        self._initialize_synonyms()
        self._initialize_abbreviations()
    
    def _initialize_patterns(self):
        """Initialize patterns for query parsing."""
        self.patterns = {
            # Query type patterns
            'calculation': r'\b(?:how (?:much|to)|calculate|compute|work out|total|amount)\b',
            'eligibility': r'\b(?:eligible|qualify|can i|am i|requirement|criteria)\b',
            'comparison': r'\b(?:difference|compare|versus|vs|better|between)\b',
            'procedural': r'\b(?:how to|when to|where to|submit|file|apply|deadline)\b',
            'definition': r'\b(?:what is|what are|define|meaning|mean)\b',
            
            # Entity patterns
            'amount': r'\$[\d,]+(?:\.\d{2})?|\b\d+k\b',
            'percentage': r'\d+(?:\.\d+)?%',
            'year': r'\b(?:20\d{2}|YA\s*20\d{2})\b',
            'form': r'\b(?:Form|IR|Appendix)\s+[A-Z0-9]+\b',
            'section': r'\b(?:Section|Sec|S)\s+\d+[A-Za-z]?\b',
            'date': r'\b\d{1,2}[\s\/\-](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2})[\s\/\-]\d{2,4}\b',
            
            # Tax category patterns
            'income_tax': r'\b(?:income tax|personal tax|individual tax|salary|employment)\b',
            'gst': r'\b(?:gst|goods and services|value added)\b',
            'property_tax': r'\b(?:property tax|annual value|owner[- ]occupied)\b',
            'corporate_tax': r'\b(?:corporate|company|business tax|enterprise)\b',
            'stamp_duty': r'\b(?:stamp duty|absd|bsd|property purchase)\b',
            'cpf': r'\b(?:cpf|central provident|retirement|medisave)\b'
        }
        
        # Question word patterns
        self.question_patterns = {
            'what': r'^what\s+',
            'how': r'^how\s+',
            'when': r'^when\s+',
            'where': r'^where\s+',
            'who': r'^who\s+',
            'why': r'^why\s+',
            'which': r'^which\s+',
            'can': r'^can\s+i\s+',
            'do': r'^do\s+i\s+',
            'is': r'^is\s+',
            'are': r'^are\s+'
        }
    
    def _initialize_synonyms(self):
        """Initialize synonym mappings for query expansion."""
        self.synonyms = {
            'tax': ['taxation', 'levy', 'duty'],
            'income': ['earnings', 'salary', 'wages', 'remuneration'],
            'deduction': ['deductible', 'allowable expense', 'claim'],
            'relief': ['rebate', 'offset', 'concession'],
            'resident': ['tax resident', 'singapore resident', 'local'],
            'foreign': ['overseas', 'international', 'abroad'],
            'company': ['corporate', 'corporation', 'business', 'enterprise'],
            'property': ['real estate', 'house', 'flat', 'hdb', 'condo'],
            'eligible': ['qualify', 'entitled', 'can claim'],
            'submit': ['file', 'lodge', 'send', 'provide'],
            'deadline': ['due date', 'last date', 'cutoff', 'timeline'],
            'calculate': ['compute', 'work out', 'determine', 'figure out'],
            'rate': ['percentage', 'percent', '%'],
            'maximum': ['max', 'cap', 'limit', 'ceiling'],
            'minimum': ['min', 'floor', 'least']
        }
    
    def _initialize_abbreviations(self):
        """Initialize abbreviation expansions."""
        self.abbreviations = {
            'ya': 'year of assessment',
            'gst': 'goods and services tax',
            'cpf': 'central provident fund',
            'iras': 'inland revenue authority of singapore',
            'absd': 'additional buyer stamp duty',
            'bsd': 'buyer stamp duty',
            'srs': 'supplementary retirement scheme',
            'noa': 'notice of assessment',
            'ir8a': 'form ir8a employment income',
            'ir8e': 'form ir8e employee benefits',
            'hdb': 'housing development board',
            'oa': 'ordinary account',
            'sa': 'special account',
            'ma': 'medisave account'
        }
    
    def enhance_query(self, query: str, context: Dict[str, Any] = None) -> EnhancedQuery:
        """
        Enhance a user query for better retrieval.
        
        Args:
            query: Original user query
            context: Optional context (current year, user profile, etc.)
            
        Returns:
            EnhancedQuery object with extracted information
        """
        # Normalize query
        normalized = self._normalize_query(query)
        
        # Identify query type
        query_type = self._identify_query_type(normalized)
        
        # Extract entities
        entities = self._extract_entities(query)
        
        # Identify tax category
        tax_category = self._identify_tax_category(normalized)
        
        # Extract year context
        year_context = self._extract_year_context(query, context)
        
        # Extract keywords
        keywords = self._extract_keywords(normalized)
        
        # Expand query terms
        expanded_terms = self._expand_query_terms(normalized)
        
        # Build filters
        filters = self._build_filters(entities, tax_category, year_context)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            query_type, tax_category, entities, keywords
        )
        
        return EnhancedQuery(
            original_query=query,
            normalized_query=normalized,
            query_type=query_type,
            tax_category=tax_category,
            year_context=year_context,
            entities=entities,
            keywords=keywords,
            expanded_terms=expanded_terms,
            filters=filters,
            confidence=confidence
        )
    
    def _normalize_query(self, query: str) -> str:
        """Normalize the query text."""
        # Convert to lowercase
        normalized = query.lower()
        
        # Expand common abbreviations
        for abbr, expansion in self.abbreviations.items():
            pattern = r'\b' + abbr + r'\b'
            normalized = re.sub(pattern, expansion, normalized)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _identify_query_type(self, query: str) -> str:
        """Identify the type of query."""
        query_lower = query.lower()
        
        # Check patterns in order of priority
        if re.search(self.patterns['calculation'], query_lower):
            return 'calculation'
        elif re.search(self.patterns['eligibility'], query_lower):
            return 'eligibility'
        elif re.search(self.patterns['comparison'], query_lower):
            return 'comparison'
        elif re.search(self.patterns['procedural'], query_lower):
            return 'procedural'
        elif re.search(self.patterns['definition'], query_lower):
            return 'definition'
        else:
            return 'factual'
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract entities from the query."""
        entities = {
            'amounts': [],
            'percentages': [],
            'years': [],
            'forms': [],
            'sections': [],
            'dates': []
        }
        
        # Extract amounts
        amounts = re.findall(self.patterns['amount'], query)
        entities['amounts'] = amounts
        
        # Extract percentages
        percentages = re.findall(self.patterns['percentage'], query)
        entities['percentages'] = percentages
        
        # Extract years
        years = re.findall(self.patterns['year'], query)
        entities['years'] = [y.replace('YA', '').strip() for y in years]
        
        # Extract forms
        forms = re.findall(self.patterns['form'], query, re.IGNORECASE)
        entities['forms'] = forms
        
        # Extract sections
        sections = re.findall(self.patterns['section'], query, re.IGNORECASE)
        entities['sections'] = sections
        
        # Extract dates
        dates = re.findall(self.patterns['date'], query, re.IGNORECASE)
        entities['dates'] = dates
        
        return entities
    
    def _identify_tax_category(self, query: str) -> str:
        """Identify the tax category from the query."""
        query_lower = query.lower()
        
        # Check each category pattern
        for category, pattern in self.patterns.items():
            if category.endswith('_tax') or category == 'gst' or category == 'cpf':
                if re.search(pattern, query_lower):
                    return category.replace('_tax', '')
        
        return 'general'
    
    def _extract_year_context(self, query: str, context: Dict[str, Any] = None) -> Optional[str]:
        """Extract year context from query or use current year."""
        # Check for explicit year in query
        year_matches = re.findall(r'\b(20\d{2})\b', query)
        if year_matches:
            return year_matches[-1]  # Use most recent year mentioned
        
        # Check for YA references
        ya_matches = re.findall(r'YA\s*(20\d{2})', query, re.IGNORECASE)
        if ya_matches:
            return ya_matches[-1]
        
        # Use context if provided
        if context and 'current_year' in context:
            return str(context['current_year'])
        
        # Default to current year
        return str(datetime.now().year)
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract important keywords from the query."""
        # Remove stop words
        stop_words = {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'must', 'shall',
            'to', 'of', 'in', 'for', 'on', 'at', 'by', 'with', 'from',
            'up', 'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'under', 'further', 'then', 'once'
        }
        
        # Extract words
        words = re.findall(r'\b[a-z]+\b', query.lower())
        
        # Filter out stop words and short words
        keywords = [
            word for word in words 
            if word not in stop_words and len(word) > 2
        ]
        
        # Add important multi-word phrases
        important_phrases = [
            'income tax', 'tax relief', 'tax rate', 'tax resident',
            'year of assessment', 'central provident fund',
            'goods and services tax', 'property tax', 'stamp duty',
            'tax deduction', 'capital allowance', 'foreign income'
        ]
        
        for phrase in important_phrases:
            if phrase in query.lower():
                keywords.append(phrase.replace(' ', '_'))
        
        return list(set(keywords))  # Remove duplicates
    
    def _expand_query_terms(self, query: str) -> List[str]:
        """Expand query terms with synonyms."""
        expanded = []
        words = query.lower().split()
        
        for word in words:
            # Add original word
            expanded.append(word)
            
            # Add synonyms
            if word in self.synonyms:
                expanded.extend(self.synonyms[word])
        
        return list(set(expanded))  # Remove duplicates
    
    def _build_filters(self, 
                      entities: Dict[str, List[str]],
                      tax_category: str,
                      year_context: str) -> Dict[str, Any]:
        """Build filters for retrieval based on extracted information."""
        filters = {}
        
        # Add tax category filter
        if tax_category != 'general':
            filters['tax_category'] = tax_category
        
        # Add year filter
        if year_context:
            filters['year_of_assessment'] = year_context
        
        # Add form filter if specific form mentioned
        if entities['forms']:
            filters['forms'] = entities['forms']
        
        # Add section filter if specific section mentioned
        if entities['sections']:
            filters['sections'] = entities['sections']
        
        return filters
    
    def _calculate_confidence(self,
                             query_type: str,
                             tax_category: str,
                             entities: Dict[str, List[str]],
                             keywords: List[str]) -> float:
        """Calculate confidence score for query understanding."""
        confidence = 0.5  # Base confidence
        
        # Add confidence for clear query type
        if query_type != 'factual':
            confidence += 0.1
        
        # Add confidence for identified tax category
        if tax_category != 'general':
            confidence += 0.15
        
        # Add confidence for extracted entities
        entity_count = sum(len(v) for v in entities.values())
        if entity_count > 0:
            confidence += min(entity_count * 0.05, 0.2)
        
        # Add confidence for keywords
        if len(keywords) >= 3:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def format_enhanced_query(self, enhanced: EnhancedQuery) -> str:
        """Format enhanced query for RAG retrieval."""
        parts = []
        
        # Add normalized query
        parts.append(enhanced.normalized_query)
        
        # Add expanded terms if significantly different
        unique_expanded = set(enhanced.expanded_terms) - set(enhanced.normalized_query.split())
        if unique_expanded:
            parts.append(f"Related terms: {' '.join(list(unique_expanded)[:5])}")
        
        # Add year context
        if enhanced.year_context:
            parts.append(f"Year: {enhanced.year_context}")
        
        # Add specific entities
        if enhanced.entities['forms']:
            parts.append(f"Forms: {' '.join(enhanced.entities['forms'])}")
        
        if enhanced.entities['sections']:
            parts.append(f"Sections: {' '.join(enhanced.entities['sections'])}")
        
        return ' '.join(parts)
    
    def get_retrieval_hints(self, enhanced: EnhancedQuery) -> Dict[str, Any]:
        """Get hints for retrieval optimization."""
        hints = {
            'boost_recent': False,
            'require_examples': False,
            'require_rates': False,
            'require_procedures': False,
            'max_chunks': 5
        }
        
        # Adjust based on query type
        if enhanced.query_type == 'calculation':
            hints['require_examples'] = True
            hints['require_rates'] = True
            hints['max_chunks'] = 7
        elif enhanced.query_type == 'procedural':
            hints['require_procedures'] = True
            hints['max_chunks'] = 8
        elif enhanced.query_type == 'eligibility':
            hints['max_chunks'] = 6
        
        # Boost recent documents for current year queries
        if enhanced.year_context == str(datetime.now().year):
            hints['boost_recent'] = True
        
        return hints