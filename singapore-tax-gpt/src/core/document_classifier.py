"""Advanced Document Type Classifier for Singapore Tax Documents."""

from typing import Dict, List, Tuple, Optional
import re
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Document type enumeration."""
    E_TAX_GUIDE = "e-tax-guide"
    CIRCULAR = "circular"
    LEGISLATION = "legislation"
    ACT = "act"
    FORM = "form"
    ORDER = "order"
    REGULATION = "regulation"
    PRACTICE_STATEMENT = "practice-statement"
    ANNUAL_REPORT = "annual-report"
    FAQ = "faq"
    NEWSLETTER = "newsletter"
    GENERAL = "general"


class TaxCategory(Enum):
    """Tax category enumeration."""
    INCOME_TAX = "income"
    GST = "gst"
    PROPERTY_TAX = "property"
    CORPORATE_TAX = "corporate"
    STAMP_DUTY = "stamp-duty"
    WITHHOLDING_TAX = "withholding"
    TRANSFER_PRICING = "transfer-pricing"
    INTERNATIONAL_TAX = "international"
    ESTATE_DUTY = "estate-duty"
    GENERAL = "general"


@dataclass
class ClassificationResult:
    """Result of document classification."""
    document_type: DocumentType
    tax_category: TaxCategory
    confidence: float
    sub_type: Optional[str] = None
    keywords_found: List[str] = None
    
    def __post_init__(self):
        if self.keywords_found is None:
            self.keywords_found = []


class DocumentClassifier:
    """Advanced document classifier for Singapore tax documents."""
    
    def __init__(self):
        """Initialize the classifier with patterns and rules."""
        self._initialize_patterns()
        self._initialize_scoring_weights()
    
    def _initialize_patterns(self):
        """Initialize classification patterns."""
        # Document type patterns with weights
        self.doc_type_patterns = {
            DocumentType.E_TAX_GUIDE: {
                'patterns': [
                    r'e-tax\s+guide',
                    r'iras\s+e-tax\s+guide',
                    r'etax\s+guide'
                ],
                'keywords': ['guide', 'guidance', 'treatment', 'application'],
                'weight': 1.0
            },
            DocumentType.CIRCULAR: {
                'patterns': [
                    r'circular\s+no\.',
                    r'iras\s+circular',
                    r'tax\s+circular'
                ],
                'keywords': ['circular', 'clarification', 'announcement'],
                'weight': 0.95
            },
            DocumentType.ACT: {
                'patterns': [
                    r'income\s+tax\s+act',
                    r'goods\s+and\s+services\s+tax\s+act',
                    r'property\s+tax\s+act',
                    r'stamp\s+duties\s+act',
                    r'chapter\s+\d+[a-z]?',
                    r'act\s+\d+'
                ],
                'keywords': ['act', 'section', 'subsection', 'chapter', 'enactment'],
                'weight': 1.0
            },
            DocumentType.LEGISLATION: {
                'patterns': [
                    r'legislative\s+amendment',
                    r'bill\s+no\.',
                    r'gazette'
                ],
                'keywords': ['legislation', 'statutory', 'enacted', 'amendment'],
                'weight': 0.9
            },
            DocumentType.FORM: {
                'patterns': [
                    r'form\s+[a-z0-9]+',
                    r'iras\s+form',
                    r'ir[0-9]+[a-z]?',
                    r'appendix\s+[a-z0-9]+'
                ],
                'keywords': ['form', 'declaration', 'submission', 'application', 'return'],
                'weight': 0.85
            },
            DocumentType.ORDER: {
                'patterns': [
                    r'income\s+tax\s+\([^)]+\)\s+order',
                    r'exemption\s+order',
                    r'order\s+\d{4}'
                ],
                'keywords': ['order', 'exemption', 'relief', 'prescribed'],
                'weight': 0.9
            },
            DocumentType.REGULATION: {
                'patterns': [
                    r'income\s+tax\s+\([^)]+\)\s+regulations?',
                    r'gst\s+\([^)]+\)\s+regulations?',
                    r'regulations?\s+\d{4}'
                ],
                'keywords': ['regulation', 'rules', 'prescribed', 'requirement'],
                'weight': 0.9
            },
            DocumentType.PRACTICE_STATEMENT: {
                'patterns': [
                    r'practice\s+statement',
                    r'administrative\s+guidance',
                    r'iras\s+practice'
                ],
                'keywords': ['practice', 'procedure', 'administrative', 'guidance'],
                'weight': 0.85
            },
            DocumentType.ANNUAL_REPORT: {
                'patterns': [
                    r'annual\s+report',
                    r'yearly\s+report',
                    r'fy\s*\d{4}'
                ],
                'keywords': ['annual', 'report', 'statistics', 'performance'],
                'weight': 0.8
            },
            DocumentType.FAQ: {
                'patterns': [
                    r'frequently\s+asked\s+questions',
                    r'faqs?',
                    r'q\s*&\s*a'
                ],
                'keywords': ['question', 'answer', 'faq', 'queries'],
                'weight': 0.75
            },
            DocumentType.NEWSLETTER: {
                'patterns': [
                    r'tax\s+bytes?',
                    r'newsletter',
                    r'tax\s+news'
                ],
                'keywords': ['newsletter', 'update', 'news', 'bulletin'],
                'weight': 0.7
            }
        }
        
        # Tax category patterns
        self.tax_category_patterns = {
            TaxCategory.INCOME_TAX: {
                'patterns': [
                    r'income\s+tax',
                    r'individual\s+tax',
                    r'personal\s+tax',
                    r'employment\s+income',
                    r'taxable\s+income'
                ],
                'keywords': ['income', 'salary', 'employment', 'resident', 'non-resident', 
                           'relief', 'deduction', 'assessment'],
                'weight': 1.0
            },
            TaxCategory.GST: {
                'patterns': [
                    r'goods\s+and\s+services\s+tax',
                    r'gst',
                    r'value\s+added\s+tax',
                    r'vat'
                ],
                'keywords': ['gst', 'supply', 'input', 'output', 'registration', 
                           'zero-rated', 'standard-rated', 'exempt'],
                'weight': 1.0
            },
            TaxCategory.PROPERTY_TAX: {
                'patterns': [
                    r'property\s+tax',
                    r'annual\s+value',
                    r'owner-occupied'
                ],
                'keywords': ['property', 'annual value', 'building', 'land', 
                           'owner', 'tenant', 'assessment'],
                'weight': 0.95
            },
            TaxCategory.CORPORATE_TAX: {
                'patterns': [
                    r'corporate\s+tax',
                    r'company\s+tax',
                    r'business\s+tax',
                    r'enterprise\s+tax'
                ],
                'keywords': ['corporate', 'company', 'business', 'enterprise', 
                           'profit', 'loss', 'capital allowance'],
                'weight': 0.95
            },
            TaxCategory.STAMP_DUTY: {
                'patterns': [
                    r'stamp\s+dut(?:y|ies)',
                    r'additional\s+buyer[\'s]*\s+stamp\s+duty',
                    r'absd',
                    r'bsd'
                ],
                'keywords': ['stamp', 'duty', 'transfer', 'conveyance', 
                           'property', 'shares', 'document'],
                'weight': 0.9
            },
            TaxCategory.WITHHOLDING_TAX: {
                'patterns': [
                    r'withholding\s+tax',
                    r'tax\s+withheld',
                    r'non-resident\s+tax'
                ],
                'keywords': ['withholding', 'non-resident', 'royalty', 
                           'interest', 'dividend', 'treaty'],
                'weight': 0.9
            },
            TaxCategory.TRANSFER_PRICING: {
                'patterns': [
                    r'transfer\s+pricing',
                    r'arm[\'s]*\s+length',
                    r'related\s+party'
                ],
                'keywords': ['transfer pricing', 'arms length', 'related party', 
                           'documentation', 'benchmark', 'comparability'],
                'weight': 0.85
            },
            TaxCategory.INTERNATIONAL_TAX: {
                'patterns': [
                    r'double\s+tax',
                    r'tax\s+treaty',
                    r'foreign\s+income',
                    r'dta'
                ],
                'keywords': ['treaty', 'foreign', 'international', 'double taxation', 
                           'residence', 'source', 'credit'],
                'weight': 0.85
            }
        }
    
    def _initialize_scoring_weights(self):
        """Initialize scoring weights for classification."""
        self.scoring_weights = {
            'title_match': 3.0,
            'pattern_match': 2.0,
            'keyword_match': 1.0,
            'filename_match': 2.5,
            'header_match': 2.0,
            'content_match': 1.0
        }
    
    def classify(self, 
                 text: str, 
                 filename: str = "",
                 title: str = "") -> ClassificationResult:
        """
        Classify a document based on its content, filename, and title.
        
        Args:
            text: Document content
            filename: Optional filename
            title: Optional document title
            
        Returns:
            ClassificationResult with document type and tax category
        """
        # Prepare text samples
        text_lower = text.lower()
        title_lower = title.lower() if title else ""
        filename_lower = filename.lower() if filename else ""
        header_text = text[:2000].lower()  # First 2000 chars for header analysis
        
        # Classify document type
        doc_type_scores = self._score_document_types(
            text_lower, header_text, title_lower, filename_lower
        )
        best_doc_type = max(doc_type_scores.items(), key=lambda x: x[1])
        
        # Classify tax category
        tax_category_scores = self._score_tax_categories(
            text_lower, header_text, title_lower, filename_lower
        )
        best_tax_category = max(tax_category_scores.items(), key=lambda x: x[1])
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            best_doc_type[1], 
            best_tax_category[1],
            doc_type_scores,
            tax_category_scores
        )
        
        # Determine sub-type if applicable
        sub_type = self._determine_sub_type(best_doc_type[0], text_lower)
        
        # Extract keywords found
        keywords_found = self._extract_found_keywords(
            text_lower, best_doc_type[0], best_tax_category[0]
        )
        
        return ClassificationResult(
            document_type=best_doc_type[0],
            tax_category=best_tax_category[0],
            confidence=confidence,
            sub_type=sub_type,
            keywords_found=keywords_found
        )
    
    def _score_document_types(self, 
                             text: str, 
                             header: str,
                             title: str, 
                             filename: str) -> Dict[DocumentType, float]:
        """Score each document type based on patterns and keywords."""
        scores = {}
        
        for doc_type, config in self.doc_type_patterns.items():
            score = 0.0
            
            # Check patterns
            for pattern in config['patterns']:
                # Title match (highest weight)
                if title and re.search(pattern, title, re.IGNORECASE):
                    score += self.scoring_weights['title_match'] * config['weight']
                
                # Filename match
                if filename and re.search(pattern, filename, re.IGNORECASE):
                    score += self.scoring_weights['filename_match'] * config['weight']
                
                # Header match
                if re.search(pattern, header, re.IGNORECASE):
                    score += self.scoring_weights['header_match'] * config['weight']
                
                # Content match
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                if matches > 0:
                    score += min(matches * 0.5, 3.0) * self.scoring_weights['content_match'] * config['weight']
            
            # Check keywords
            for keyword in config['keywords']:
                if keyword in text:
                    score += self.scoring_weights['keyword_match'] * config['weight']
            
            scores[doc_type] = score
        
        # If no clear match, default to general
        if all(score < 1.0 for score in scores.values()):
            scores[DocumentType.GENERAL] = 1.0
        
        return scores
    
    def _score_tax_categories(self,
                             text: str,
                             header: str,
                             title: str,
                             filename: str) -> Dict[TaxCategory, float]:
        """Score each tax category based on patterns and keywords."""
        scores = {}
        
        for category, config in self.tax_category_patterns.items():
            score = 0.0
            
            # Check patterns
            for pattern in config['patterns']:
                # Title match
                if title and re.search(pattern, title, re.IGNORECASE):
                    score += self.scoring_weights['title_match'] * config['weight']
                
                # Filename match
                if filename and re.search(pattern, filename, re.IGNORECASE):
                    score += self.scoring_weights['filename_match'] * config['weight']
                
                # Header match
                if re.search(pattern, header, re.IGNORECASE):
                    score += self.scoring_weights['header_match'] * config['weight']
                
                # Content match
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                if matches > 0:
                    score += min(matches * 0.3, 2.0) * self.scoring_weights['content_match'] * config['weight']
            
            # Check keywords
            keyword_count = sum(1 for keyword in config['keywords'] if keyword in text)
            if keyword_count > 0:
                score += min(keyword_count * 0.5, 3.0) * self.scoring_weights['keyword_match'] * config['weight']
            
            scores[category] = score
        
        # If no clear match, default to general
        if all(score < 1.0 for score in scores.values()):
            scores[TaxCategory.GENERAL] = 1.0
        
        return scores
    
    def _calculate_confidence(self,
                            doc_type_score: float,
                            tax_cat_score: float,
                            all_doc_scores: Dict[DocumentType, float],
                            all_cat_scores: Dict[TaxCategory, float]) -> float:
        """Calculate classification confidence."""
        # Base confidence from absolute scores
        base_confidence = min((doc_type_score + tax_cat_score) / 20.0, 0.7)
        
        # Adjust based on score separation (how much better is the best score)
        doc_scores_sorted = sorted(all_doc_scores.values(), reverse=True)
        cat_scores_sorted = sorted(all_cat_scores.values(), reverse=True)
        
        doc_separation = 0.0
        cat_separation = 0.0
        
        if len(doc_scores_sorted) > 1 and doc_scores_sorted[0] > 0:
            doc_separation = (doc_scores_sorted[0] - doc_scores_sorted[1]) / doc_scores_sorted[0]
        
        if len(cat_scores_sorted) > 1 and cat_scores_sorted[0] > 0:
            cat_separation = (cat_scores_sorted[0] - cat_scores_sorted[1]) / cat_scores_sorted[0]
        
        separation_bonus = (doc_separation + cat_separation) * 0.15
        
        return min(base_confidence + separation_bonus, 1.0)
    
    def _determine_sub_type(self, doc_type: DocumentType, text: str) -> Optional[str]:
        """Determine document sub-type based on content."""
        sub_types = {
            DocumentType.E_TAX_GUIDE: {
                'filing': ['filing', 'submission', 'deadline'],
                'computation': ['computation', 'calculation', 'formula'],
                'compliance': ['compliance', 'requirement', 'obligation'],
                'exemption': ['exemption', 'relief', 'deduction'],
                'international': ['foreign', 'treaty', 'international']
            },
            DocumentType.FORM: {
                'income': ['ir8a', 'ir8e', 'ir8s', 'income'],
                'gst': ['gst', 'f5', 'f7', 'f8'],
                'corporate': ['c-s', 'ir', 'corporate'],
                'property': ['property', 'ptyb']
            },
            DocumentType.CIRCULAR: {
                'clarification': ['clarify', 'clarification', 'explanation'],
                'update': ['update', 'change', 'amendment'],
                'guidance': ['guidance', 'guide', 'procedure']
            }
        }
        
        if doc_type in sub_types:
            for sub_type, keywords in sub_types[doc_type].items():
                if any(keyword in text for keyword in keywords):
                    return sub_type
        
        return None
    
    def _extract_found_keywords(self,
                               text: str,
                               doc_type: DocumentType,
                               tax_category: TaxCategory) -> List[str]:
        """Extract keywords that were found in the text."""
        found_keywords = []
        
        # Check document type keywords
        if doc_type in self.doc_type_patterns:
            for keyword in self.doc_type_patterns[doc_type]['keywords']:
                if keyword in text:
                    found_keywords.append(keyword)
        
        # Check tax category keywords
        if tax_category in self.tax_category_patterns:
            for keyword in self.tax_category_patterns[tax_category]['keywords']:
                if keyword in text:
                    found_keywords.append(keyword)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in found_keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:10]  # Return top 10 keywords
    
    def classify_batch(self, documents: List[Dict[str, str]]) -> List[ClassificationResult]:
        """
        Classify multiple documents.
        
        Args:
            documents: List of dicts with 'text', 'filename', and 'title' keys
            
        Returns:
            List of ClassificationResult objects
        """
        results = []
        for doc in documents:
            result = self.classify(
                text=doc.get('text', ''),
                filename=doc.get('filename', ''),
                title=doc.get('title', '')
            )
            results.append(result)
            
            # Log classification
            logger.info(f"Classified {doc.get('filename', 'document')}: "
                       f"Type={result.document_type.value}, "
                       f"Category={result.tax_category.value}, "
                       f"Confidence={result.confidence:.2f}")
        
        return results