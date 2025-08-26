"""Calculation handler that integrates tax calculator with RAG system."""

import os
import re
from typing import Dict, Any, Optional, List, Tuple
from src.singapore.tax_calculator import SingaporeTaxCalculator
from src.core.query_enhancer import QueryEnhancer
import logging
from src.apis.stamp_duty_calculator import StampDutyCalculator

logger = logging.getLogger(__name__)


class CalculationHandler:
    """Handles tax calculations within the RAG system."""
    
    def __init__(self):
        """Initialize calculation handler."""
        self.calculator = SingaporeTaxCalculator()
        self.query_enhancer = QueryEnhancer()
        self.stamp_duty_calculator = StampDutyCalculator()
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """Initialize patterns for extracting calculation parameters."""
        self.calculation_patterns = {
            'income_tax': [
                r'tax (?:on|for) (?:\$)?([0-9,]+)',
                r'income (?:of|is) (?:\$)?([0-9,]+)',
                r'(?:earn|salary|income) (?:\$)?([0-9,]+)',
                r'(?:\$)?([0-9,]+) (?:income|salary|earnings?)',
            ],
            'gst': [
                r'gst (?:on|for) (?:\$)?([0-9,]+)',
                r'(?:\$)?([0-9,]+) (?:plus|with|including) gst',
                r'add gst to (?:\$)?([0-9,]+)',
            ],
            'property_tax': [
                r'property tax (?:on|for) (?:\$)?([0-9,]+)',
                r'annual value (?:of|is) (?:\$)?([0-9,]+)',
            ],
            'cpf': [
                r'cpf (?:on|for) (?:\$)?([0-9,]+)',
                r'(?:\$)?([0-9,]+) (?:salary|monthly)',
            ],
            'take_home': [
                r'take[- ]home (?:pay|salary) (?:for|on) (?:\$)?([0-9,]+)',
                r'net (?:pay|salary) (?:for|on) (?:\$)?([0-9,]+)',
            ],
            'stamp_duty': [
                r'stamp duty (?:on|for) (?:\$)?([0-9,]+)',
                r'(?:buy|purchase|buying) .*?(?:\$)?([0-9,]+).*?property',
                r'(?:\$)?([0-9,]+).*?(?:house|condo|flat|property)',
                r'absd (?:on|for) (?:\$)?([0-9,]+)',
            ]
        }
        
        # Relief patterns
        self.relief_patterns = {
            'spouse': r'(?:spouse|wife|husband) relief',
            'parent': r'parent relief',
            'child': r'(?:child|children|qualifying child) relief',
            'cpf': r'cpf (?:top[- ]up|voluntary|cash)',
            'srs': r'srs|supplementary retirement',
        }
    
    def should_calculate(self, query: str) -> bool:
        """
        Determine if query requires calculation.
        
        Args:
            query: User query
            
        Returns:
            True if calculation needed
        """
        query_lower = query.lower()
        
        # Check for calculation keywords
        calc_keywords = [
            'calculate', 'how much', 'what is the tax',
            'take home', 'net pay', 'after tax',
            'gst', 'property tax', 'cpf contribution'
        ]
        
        # Check for amounts in query
        has_amount = bool(re.search(r'\$?[0-9,]+', query))
        
        # Check for calculation keywords
        has_calc_keyword = any(keyword in query_lower for keyword in calc_keywords)
        
        return has_amount and has_calc_keyword
    
    def extract_calculation_params(self, query: str) -> Dict[str, Any]:
        """
        Extract parameters for calculation from query.
        
        Args:
            query: User query
            
        Returns:
            Dictionary of extracted parameters
        """
        params = {
            'type': None,
            'amount': None,
            'reliefs': {},
            'age': 30,  # Default age
            'is_resident': True,
            'year': 2024
        }
        
        query_lower = query.lower()
        
        # Determine calculation type
        if 'stamp duty' in query_lower or 'absd' in query_lower or 'bsd' in query_lower:
            params['type'] = 'stamp_duty'
        elif 'gst' in query_lower:
            params['type'] = 'gst'
        elif 'property tax' in query_lower:
            params['type'] = 'property_tax'
        elif 'cpf' in query_lower:
            params['type'] = 'cpf'
        elif 'take home' in query_lower or 'net pay' in query_lower:
            params['type'] = 'take_home'
        else:
            params['type'] = 'income_tax'
        
        # Extract amount based on type
        for pattern_list in self.calculation_patterns.get(params['type'], []):
            match = re.search(pattern_list, query_lower)
            if match:
                amount_str = match.group(1).replace(',', '')
                params['amount'] = float(amount_str)
                break
        
        # Extract age if mentioned
        age_match = re.search(r'age (?:is )?(\d+)', query_lower)
        if age_match:
            params['age'] = int(age_match.group(1))
        
        # Check for non-resident
        if 'non-resident' in query_lower or 'non resident' in query_lower:
            params['is_resident'] = False
        
        # Extract reliefs
        for relief_name, pattern in self.relief_patterns.items():
            if re.search(pattern, query_lower):
                # Try to extract relief amount
                amount_pattern = f'{pattern}.*?(?:\\$)?([0-9,]+)'
                amount_match = re.search(amount_pattern, query_lower)
                if amount_match:
                    params['reliefs'][relief_name] = float(amount_match.group(1).replace(',', ''))
                else:
                    # Use default relief amounts
                    default_amounts = {
                        'spouse': 2000,
                        'parent': 9000,
                        'child': 4000,
                        'cpf': 7000,
                        'srs': 15300
                    }
                    params['reliefs'][relief_name] = default_amounts.get(relief_name, 0)
        
        # Extract year
        year_match = re.search(r'(?:YA|year|for) ?(\d{4})', query, re.IGNORECASE)
        if year_match:
            params['year'] = int(year_match.group(1))
        
        return params
    
    def perform_calculation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform the actual calculation.
        
        Args:
            params: Calculation parameters
            
        Returns:
            Calculation results
        """
        calc_type = params['type']
        amount = params.get('amount', 0)
        
        if not amount:
            return {
                'error': 'No amount found in query',
                'type': calc_type
            }
        
        try:
            if calc_type == 'income_tax':
                result = self.calculator.calculate_income_tax(
                    amount,
                    reliefs=params.get('reliefs', {}),
                    is_resident=params.get('is_resident', True),
                    age=params.get('age', 30)
                )
                
                return {
                    'type': 'income_tax',
                    'gross_income': float(result.gross_income),
                    'tax_amount': float(result.tax_amount),
                    'effective_rate': float(result.effective_rate),
                    'marginal_rate': float(result.marginal_rate),
                    'chargeable_income': float(result.chargeable_income),
                    'reliefs_applied': result.reliefs_applied,
                    'breakdown': result.breakdown
                }
            
            elif calc_type == 'gst':
                # Determine if inclusive or exclusive
                is_inclusive = 'including' in params.get('query', '').lower()
                
                result = self.calculator.calculate_gst(
                    amount,
                    year=params.get('year', 2024),
                    is_inclusive=is_inclusive
                )
                
                return {
                    'type': 'gst',
                    **result
                }
            
            elif calc_type == 'property_tax':
                is_owner = 'owner' in params.get('query', '').lower()
                
                result = self.calculator.calculate_property_tax(
                    amount,
                    is_owner_occupied=is_owner
                )
                
                return {
                    'type': 'property_tax',
                    **result
                }
            
            elif calc_type == 'cpf':
                # For CPF, amount is monthly salary
                result = self.calculator.calculate_cpf(
                    amount,
                    age=params.get('age', 30)
                )
                
                return {
                    'type': 'cpf',
                    **result
                }
            
            elif calc_type == 'stamp_duty':
                query_lower = params.get('query', '').lower()
                
                # Extract buyer profile
                buyer_profile = 'singapore_citizen'  # Default
                if 'foreigner' in query_lower or 'foreign' in query_lower:
                    buyer_profile = 'foreigner'
                elif 'pr' in query_lower or 'permanent resident' in query_lower:
                    buyer_profile = 'pr'
                elif 'company' in query_lower or 'entity' in query_lower or 'corporate' in query_lower:
                    buyer_profile = 'entity'
                elif 'citizen' in query_lower:
                    buyer_profile = 'singapore_citizen'
                
                # Extract number of properties
                num_properties = 0
                
                # Check for first property
                if 'first' in query_lower or '1st' in query_lower or 'first home' in query_lower or 'first property' in query_lower:
                    num_properties = 0
                # Check for second property
                elif 'second' in query_lower or '2nd' in query_lower or 'second property' in query_lower:
                    num_properties = 1
                # Check for third property
                elif 'third' in query_lower or '3rd' in query_lower or 'third property' in query_lower:
                    num_properties = 2
                # Generic pattern
                else:
                    prop_match = re.search(r'(\d+)(?:st|nd|rd|th)?\s+propert', query_lower)
                    if prop_match:
                        num_properties = int(prop_match.group(1)) - 1
                
                # Use local stamp duty calculator
                result = self.stamp_duty_calculator.calculate_property_stamp_duty(
                    purchase_price=amount,
                    buyer_profile=buyer_profile,
                    num_properties=num_properties
                )
                
                return {
                    'type': 'stamp_duty',
                    **result
                }
            
            elif calc_type == 'take_home':
                result = self.calculator.calculate_take_home(
                    amount,
                    age=params.get('age', 30),
                    reliefs=params.get('reliefs', {}),
                    is_resident=params.get('is_resident', True)
                )
                
                return {
                    'type': 'take_home',
                    **result
                }
            
        except Exception as e:
            logger.error(f"Calculation error: {e}")
            return {
                'error': str(e),
                'type': calc_type
            }
    
    def format_calculation_response(self, result: Dict[str, Any]) -> str:
        """
        Format calculation result as human-readable response.
        
        Args:
            result: Calculation result
            
        Returns:
            Formatted response string
        """
        if 'error' in result:
            return f"Unable to calculate: {result['error']}"
        
        calc_type = result.get('type')
        
        if calc_type == 'income_tax':
            response = f"""Based on the income of ${result['gross_income']:,.0f}:

**Tax Calculation:**
- Gross Income: ${result['gross_income']:,.0f}
- Chargeable Income: ${result['chargeable_income']:,.0f}
- Tax Amount: **${result['tax_amount']:,.0f}**
- Effective Tax Rate: {result['effective_rate']:.2f}%
- Marginal Tax Rate: {result['marginal_rate']:.1f}%"""
            
            if result.get('reliefs_applied'):
                response += "\n\n**Reliefs Applied:**"
                for relief in result['reliefs_applied']:
                    response += f"\n- {relief['type']}: ${relief['amount']:,.0f}"
            
            if result.get('breakdown'):
                response += "\n\n**Tax Breakdown:**"
                for bracket in result['breakdown'][:3]:  # Show first 3 brackets
                    response += f"\n- {bracket['income_range']} at {bracket['rate']}: ${bracket['tax']:,.0f}"
        
        elif calc_type == 'gst':
            response = f"""**GST Calculation:**
- Base Amount: ${result['base_amount']:,.2f}
- GST ({result['gst_rate']:.0f}%): ${result['gst_amount']:,.2f}
- Total Amount: **${result['total']:,.2f}**"""
        
        elif calc_type == 'property_tax':
            response = f"""**Property Tax Calculation:**
- Annual Value: ${result['annual_value']:,.0f}
- Property Tax: **${result['tax_amount']:,.2f}**
- Type: {result['type']}"""
            
            if result.get('breakdown'):
                response += "\n\n**Tax Breakdown:**"
                for bracket in result['breakdown'][:3]:
                    response += f"\n- {bracket['av_range']} at {bracket['rate']}: ${bracket['tax']:,.2f}"
        
        elif calc_type == 'cpf':
            response = f"""**CPF Contribution:**

Monthly:
- Employee Contribution: ${result['monthly']['employee']:,.2f}
- Employer Contribution: ${result['monthly']['employer']:,.2f}
- Total Monthly CPF: ${result['monthly']['total']:,.2f}

Annual:
- Total Annual CPF: ${result['annual']['total']:,.2f}

Rates Applied: {result['age_bracket']}
- Employee: {result['rates']['employee']}
- Employer: {result['rates']['employer']}"""
        
        elif calc_type == 'stamp_duty':
            response = f"""**Stamp Duty Calculation:**

Property Price: ${result['consideration']:,.0f}
Buyer Profile: {result.get('buyer_profile', 'Singapore Citizen').replace('_', ' ').title()}

**Stamp Duty Breakdown:**
- Buyer's Stamp Duty (BSD): ${result['buyer_stamp_duty']:,.0f}
- Additional Buyer's Stamp Duty (ABSD): ${result['additional_buyer_stamp_duty']:,.0f}
- **Total Stamp Duty: ${result['total_stamp_duty']:,.0f}**

*Note: Calculated using current stamp duty rates (YA 2024)*"""
        
        elif calc_type == 'take_home':
            response = f"""**Take-Home Pay Calculation:**

Annual:
- Gross Income: ${result['gross_income']:,.0f}
- Income Tax: ${result['tax']['annual']:,.0f}
- CPF (Employee): ${result['cpf']['annual']:,.2f}
- **Net Take-Home: ${result['take_home']['annual']:,.2f}**

Monthly:
- Gross Salary: ${result['breakdown']['gross_monthly']:,.2f}
- Tax Deduction: ${result['breakdown']['tax_deduction']:,.2f}
- CPF Deduction: ${result['breakdown']['cpf_deduction']:,.2f}
- **Net Monthly: ${result['breakdown']['net_monthly']:,.2f}**

Effective Tax Rate: {result['tax']['effective_rate']:.2f}%"""
        
        else:
            response = "Calculation completed but formatting not available."
        
        return response
    
    def handle_calculation_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Main method to handle calculation queries.
        
        Args:
            query: User query
            
        Returns:
            Tuple of (is_calculation, response)
        """
        # Check if calculation is needed
        if not self.should_calculate(query):
            return False, None
        
        # Extract parameters
        params = self.extract_calculation_params(query)
        params['query'] = query  # Store original query for context
        
        # Perform calculation
        result = self.perform_calculation(params)
        
        # Format response
        response = self.format_calculation_response(result)
        
        # Add disclaimer
        response += "\n\n*Note: This is a calculation based on current tax rates. Please consult IRAS or a tax professional for official advice.*"
        
        return True, response