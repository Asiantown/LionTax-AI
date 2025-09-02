#!/usr/bin/env python
"""Extract structured tax data from Singapore IRAS PDFs."""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# Same imports as qa_working.py
from dotenv import load_dotenv
load_dotenv()
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from langchain_community.document_loaders import PyPDFLoader

class TaxFactExtractor:
    """Extract structured tax facts from IRAS documents."""
    
    def __init__(self, pdf_dir: str = "./data/iras_docs"):
        self.pdf_dir = Path(pdf_dir)
        self.tax_facts = {
            "income_tax": {
                "resident_rates": [],
                "non_resident_rate": None,
                "reliefs": {},
                "deductions": {},
                "rebates": {}
            },
            "gst": {
                "standard_rate": None,
                "zero_rated_supplies": [],
                "exempt_supplies": []
            },
            "stamp_duty": {
                "bsd_rates": [],
                "absd_rates": {},
                "remission_rules": []
            },
            "property_tax": {
                "residential_rates": [],
                "non_residential_rates": []
            },
            "cpf": {
                "contribution_rates": [],
                "wage_ceiling": None
            },
            "key_thresholds": {},
            "filing_deadlines": {},
            "penalties": {}
        }
    
    def extract_all_facts(self) -> Dict:
        """Extract facts from all PDFs."""
        for pdf_path in self.pdf_dir.glob("*.pdf"):
            print(f"Processing: {pdf_path.name}")
            self._extract_from_pdf(pdf_path)
        
        # Add hardcoded current rates (since PDFs might have historical data)
        self._add_current_rates_2024()
        
        return self.tax_facts
    
    def _extract_from_pdf(self, pdf_path: Path) -> None:
        """Extract structured data from a single PDF."""
        try:
            loader = PyPDFLoader(str(pdf_path))
            pages = loader.load()
            
            full_text = ""
            tables_data = []  # PyPDF doesn't extract tables directly
            
            for page_num, page in enumerate(pages):
                # Extract text from each page
                page_text = page.page_content or ""
                full_text += page_text + "\n"
            
            # Process based on document type
            if "Income Tax Act" in pdf_path.name:
                self._extract_income_tax_facts(full_text, tables_data)
            elif "Goods and Services Tax" in pdf_path.name:
                self._extract_gst_facts(full_text, tables_data)
            elif "Stamp Duties" in pdf_path.name:
                self._extract_stamp_duty_facts(full_text, tables_data)
            elif "Property Tax" in pdf_path.name:
                self._extract_property_tax_facts(full_text, tables_data)
                    
        except Exception as e:
            print(f"Error processing {pdf_path.name}: {e}")
    
    def _extract_income_tax_facts(self, text: str, tables: List) -> None:
        """Extract income tax specific facts."""
        
        # Since PyPDF doesn't extract tables, we'll rely on regex patterns
        # Extract from text using regex patterns
        self._extract_rates_from_text(text)
        self._extract_reliefs_from_text(text)
        self._extract_deadlines_from_text(text)
    
    def _parse_tax_rate_row(self, row: List) -> None:
        """Parse a row that might contain tax rate information."""
        try:
            # Convert row to string for analysis
            row_str = " ".join([str(cell) if cell else "" for cell in row])
            
            # Pattern: "First $20,000" or "Next $10,000" followed by rate
            rate_pattern = r"(First|Next|Exceeding)\s+\$?([\d,]+).*?(\d+(?:\.\d+)?)\s*%"
            matches = re.finditer(rate_pattern, row_str, re.IGNORECASE)
            
            for match in matches:
                bracket_type = match.group(1)
                amount = int(match.group(2).replace(",", ""))
                rate = float(match.group(3))
                
                # Store in structured format
                if not any(r["amount"] == amount for r in self.tax_facts["income_tax"]["resident_rates"]):
                    self.tax_facts["income_tax"]["resident_rates"].append({
                        "type": bracket_type.lower(),
                        "amount": amount,
                        "rate": rate
                    })
        except Exception:
            pass
    
    def _parse_relief_row(self, row: List) -> None:
        """Parse a row containing relief information."""
        try:
            row_str = " ".join([str(cell) if cell else "" for cell in row])
            
            # Common relief patterns
            relief_patterns = [
                (r"Spouse\s+Relief.*?\$?([\d,]+)", "spouse_relief"),
                (r"Child\s+Relief.*?\$?([\d,]+)", "child_relief"),
                (r"Parent\s+Relief.*?\$?([\d,]+)", "parent_relief"),
                (r"Earned\s+Income\s+Relief.*?(\d+)\s*%.*?max.*?\$?([\d,]+)", "earned_income_relief"),
                (r"CPF\s+Relief", "cpf_relief"),
                (r"Course\s+Fees.*?\$?([\d,]+)", "course_fees_relief"),
                (r"NSman.*?\$?([\d,]+)", "nsman_relief")
            ]
            
            for pattern, relief_name in relief_patterns:
                match = re.search(pattern, row_str, re.IGNORECASE)
                if match:
                    if relief_name == "earned_income_relief":
                        self.tax_facts["income_tax"]["reliefs"][relief_name] = {
                            "percentage": int(match.group(1)),
                            "cap": int(match.group(2).replace(",", ""))
                        }
                    else:
                        amount = int(match.group(1).replace(",", ""))
                        self.tax_facts["income_tax"]["reliefs"][relief_name] = amount
        except Exception:
            pass
    
    def _extract_rates_from_text(self, text: str) -> None:
        """Extract tax rates from plain text."""
        
        # Non-resident rate
        non_resident_pattern = r"non-resident.*?(?:flat\s+rate|tax.*?rate).*?(\d+)\s*%"
        match = re.search(non_resident_pattern, text, re.IGNORECASE)
        if match:
            self.tax_facts["income_tax"]["non_resident_rate"] = float(match.group(1))
        
        # Tax-free threshold
        threshold_pattern = r"(?:first|initial|tax-free).*?\$?([\d,]+).*?(?:nil|0%|tax-free|no\s+tax)"
        match = re.search(threshold_pattern, text, re.IGNORECASE)
        if match:
            self.tax_facts["income_tax"]["tax_free_threshold"] = int(match.group(1).replace(",", ""))
    
    def _extract_reliefs_from_text(self, text: str) -> None:
        """Extract relief amounts from text."""
        
        # Define patterns for common reliefs with their typical amounts
        relief_patterns = {
            "spouse_relief": r"Spouse\s+Relief.*?\$\s?([\d,]+)",
            "child_relief": r"(?:Qualifying|Handicapped)?\s*Child\s+Relief.*?\$\s?([\d,]+)",
            "parent_relief": r"Parent\s+Relief.*?\$\s?([\d,]+)",
            "working_mother_child_relief": r"Working\s+Mother.*?Child\s+Relief.*?(\d+)\s*%",
            "grandparent_caregiver_relief": r"Grandparent\s+Caregiver\s+Relief.*?\$\s?([\d,]+)",
            "handicapped_brother_sister_relief": r"Handicapped\s+(?:Brother|Sister|Sibling).*?\$\s?([\d,]+)"
        }
        
        for relief_name, pattern in relief_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if "%" in pattern:
                        value = float(match.group(1))
                    else:
                        value = int(match.group(1).replace(",", ""))
                    
                    if relief_name not in self.tax_facts["income_tax"]["reliefs"]:
                        self.tax_facts["income_tax"]["reliefs"][relief_name] = value
                except Exception:
                    continue
    
    def _extract_deadlines_from_text(self, text: str) -> None:
        """Extract filing deadlines from text."""
        
        deadline_patterns = [
            (r"(?:e-filing|electronic\s+filing).*?deadline.*?(\d+\s+\w+)", "e_filing"),
            (r"(?:paper|hardcopy|manual).*?filing.*?deadline.*?(\d+\s+\w+)", "paper_filing"),
            (r"corporate\s+tax.*?filing.*?(\d+\s+\w+)", "corporate_filing")
        ]
        
        for pattern, deadline_type in deadline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                self.tax_facts["filing_deadlines"][deadline_type] = match.group(1)
    
    def _extract_gst_facts(self, text: str, tables: List) -> None:
        """Extract GST facts."""
        
        # Standard GST rate
        gst_pattern = r"(?:standard|general)?\s*GST\s+rate.*?(\d+)\s*%"
        match = re.search(gst_pattern, text, re.IGNORECASE)
        if match:
            self.tax_facts["gst"]["standard_rate"] = float(match.group(1))
        
        # Registration threshold
        threshold_pattern = r"GST\s+registration.*?threshold.*?\$\s?([\d,]+)"
        match = re.search(threshold_pattern, text, re.IGNORECASE)
        if match:
            self.tax_facts["gst"]["registration_threshold"] = int(match.group(1).replace(",", ""))
    
    def _extract_stamp_duty_facts(self, text: str, tables: List) -> None:
        """Extract stamp duty facts."""
        
        # BSD rates
        bsd_patterns = [
            r"First\s+\$?([\d,]+).*?(\d+(?:\.\d+)?)\s*%",
            r"Next\s+\$?([\d,]+).*?(\d+(?:\.\d+)?)\s*%",
            r"Exceeding\s+\$?([\d,]+).*?(\d+(?:\.\d+)?)\s*%"
        ]
        
        for pattern in bsd_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount = int(match.group(1).replace(",", ""))
                rate = float(match.group(2))
                self.tax_facts["stamp_duty"]["bsd_rates"].append({
                    "threshold": amount,
                    "rate": rate
                })
        
        # ABSD rates by buyer profile
        absd_pattern = r"(Singapore\s+Citizen|Permanent\s+Resident|Foreigner|Entity).*?(\d+)\s*%"
        matches = re.finditer(absd_pattern, text, re.IGNORECASE)
        for match in matches:
            buyer_type = match.group(1).lower().replace(" ", "_")
            rate = float(match.group(2))
            self.tax_facts["stamp_duty"]["absd_rates"][buyer_type] = rate
    
    def _extract_property_tax_facts(self, text: str, tables: List) -> None:
        """Extract property tax facts."""
        
        # Owner-occupied residential rates
        residential_pattern = r"owner-occupied.*?residential.*?(\d+(?:\.\d+)?)\s*%"
        matches = re.finditer(residential_pattern, text, re.IGNORECASE)
        for match in matches:
            rate = float(match.group(1))
            if rate not in self.tax_facts["property_tax"]["residential_rates"]:
                self.tax_facts["property_tax"]["residential_rates"].append(rate)
        
        # Non-residential rates
        non_residential_pattern = r"non-residential.*?(\d+(?:\.\d+)?)\s*%"
        match = re.search(non_residential_pattern, text, re.IGNORECASE)
        if match:
            self.tax_facts["property_tax"]["non_residential_rate"] = float(match.group(1))
    
    def _add_current_rates_2024(self) -> None:
        """Add hardcoded current 2024 tax rates and reliefs."""
        
        # Current income tax rates for YA 2024
        self.tax_facts["income_tax"]["resident_rates"] = [
            {"bracket": "First $20,000", "rate": 0, "tax": 0},
            {"bracket": "Next $10,000", "rate": 2, "tax": 200},
            {"bracket": "Next $10,000", "rate": 3.5, "tax": 350},
            {"bracket": "Next $40,000", "rate": 7, "tax": 2800},
            {"bracket": "Next $40,000", "rate": 11.5, "tax": 4600},
            {"bracket": "Next $40,000", "rate": 15, "tax": 6000},
            {"bracket": "Next $40,000", "rate": 18, "tax": 7200},
            {"bracket": "Next $40,000", "rate": 19, "tax": 7600},
            {"bracket": "Next $40,000", "rate": 19.5, "tax": 7800},
            {"bracket": "Next $40,000", "rate": 20, "tax": 8000},
            {"bracket": "Above $320,000", "rate": 22, "tax": None}
        ]
        
        # Current reliefs (YA 2024)
        self.tax_facts["income_tax"]["reliefs"].update({
            "personal_relief": 1000,  # Automatically granted
            "earned_income_relief": {"max": 1000, "calculation": "Lower of $1,000 or 1% of earned income"},
            "spouse_relief": 2000,
            "qualifying_child_relief": 4000,
            "handicapped_child_relief": 7500,
            "working_mother_child_relief": {"percentage": 15, "note": "15% of earned income per child"},
            "parent_relief": 9000,
            "handicapped_parent_relief": 14000,
            "grandparent_caregiver_relief": 3000,
            "handicapped_brother_sister_relief": 5500,
            "cpf_cash_top_up_relief": 8000,  # Combined with voluntary CPF contribution
            "cpf_relief": "Automatic for mandatory contributions",
            "course_fees_relief": 5500,
            "foreign_maid_levy_relief": {"amount": "2x foreign maid levy paid"},
            "life_insurance_relief": 5000,  # Combined CPF and insurance premium relief
            "supplementary_retirement_scheme": 15300,
            "nsman_relief": {"self": 3000, "wife": 750, "parent": 750}
        })
        
        # Non-resident rate
        self.tax_facts["income_tax"]["non_resident_rate"] = 22  # Or 15% for employment income < 183 days
        
        # GST
        self.tax_facts["gst"]["standard_rate"] = 9  # Increased to 9% in 2024
        self.tax_facts["gst"]["registration_threshold"] = 1000000
        
        # Property tax rates 2024
        self.tax_facts["property_tax"]["owner_occupied_rates"] = [
            {"av_range": "First $8,000", "rate": 0},
            {"av_range": "Next $47,000", "rate": 4},
            {"av_range": "Next $15,000", "rate": 6},
            {"av_range": "Next $15,000", "rate": 8},
            {"av_range": "Next $15,000", "rate": 10},
            {"av_range": "Next $15,000", "rate": 12},
            {"av_range": "Next $15,000", "rate": 14},
            {"av_range": "Above $130,000", "rate": 16}
        ]
        
        self.tax_facts["property_tax"]["non_owner_occupied_rates"] = [
            {"av_range": "First $30,000", "rate": 10},
            {"av_range": "Next $15,000", "rate": 12},
            {"av_range": "Next $15,000", "rate": 14},
            {"av_range": "Above $60,000", "rate": 16}
        ]
        
        # Stamp duty rates (BSD)
        self.tax_facts["stamp_duty"]["bsd_rates"] = [
            {"price_range": "First $180,000", "rate": 1},
            {"price_range": "Next $180,000", "rate": 2},
            {"price_range": "Next $640,000", "rate": 3},
            {"price_range": "Next $500,000", "rate": 4},
            {"price_range": "Next $1,500,000", "rate": 5},
            {"price_range": "Above $3,000,000", "rate": 6}
        ]
        
        # ABSD rates 2024
        self.tax_facts["stamp_duty"]["absd_rates"] = {
            "singapore_citizen_first": 0,
            "singapore_citizen_second": 20,
            "singapore_citizen_third_plus": 30,
            "permanent_resident_first": 5,
            "permanent_resident_second": 30,
            "permanent_resident_third_plus": 35,
            "foreigner_any": 60,
            "entity": 65
        }
        
        # Key dates
        self.tax_facts["filing_deadlines"] = {
            "e_filing": "18 April",
            "paper_filing": "15 April",
            "corporate": "30 November",
            "gst_quarterly": "End of month following quarter end"
        }
        
        # Important thresholds
        self.tax_facts["key_thresholds"] = {
            "tax_resident_days": 183,
            "start_paying_tax": 20000,
            "highest_marginal_rate_at": 320000,
            "cpf_ordinary_wage_ceiling": 6000,
            "cpf_additional_wage_ceiling": 102000
        }
    
    def save_to_json(self, output_path: str = "singapore_tax_facts.json") -> None:
        """Save extracted facts to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.tax_facts, f, indent=2, ensure_ascii=False)
        print(f"Tax facts saved to {output_path}")
    
    def calculate_tax_example(self, income: float) -> Dict:
        """Calculate tax for a given income to verify rates."""
        if not self.tax_facts["income_tax"]["resident_rates"]:
            return {"error": "No tax rates available"}
        
        total_tax = 0
        remaining_income = income
        breakdown = []
        
        cumulative_limit = 0
        for rate_info in self.tax_facts["income_tax"]["resident_rates"]:
            if "Next" in rate_info["bracket"] or "First" in rate_info["bracket"]:
                # Extract amount from bracket
                amount_match = re.search(r"\$([\d,]+)", rate_info["bracket"])
                if amount_match:
                    bracket_amount = int(amount_match.group(1).replace(",", ""))
                    
                    if remaining_income <= 0:
                        break
                    
                    taxable_in_bracket = min(remaining_income, bracket_amount)
                    tax_in_bracket = taxable_in_bracket * rate_info["rate"] / 100
                    
                    breakdown.append({
                        "bracket": rate_info["bracket"],
                        "amount": taxable_in_bracket,
                        "rate": rate_info["rate"],
                        "tax": tax_in_bracket
                    })
                    
                    total_tax += tax_in_bracket
                    remaining_income -= taxable_in_bracket
                    cumulative_limit += bracket_amount
            
            elif "Above" in rate_info["bracket"] and remaining_income > 0:
                # Final bracket
                tax_in_bracket = remaining_income * rate_info["rate"] / 100
                breakdown.append({
                    "bracket": rate_info["bracket"],
                    "amount": remaining_income,
                    "rate": rate_info["rate"],
                    "tax": tax_in_bracket
                })
                total_tax += tax_in_bracket
                break
        
        return {
            "income": income,
            "total_tax": round(total_tax, 2),
            "effective_rate": round((total_tax / income) * 100, 2),
            "take_home": round(income - total_tax, 2),
            "breakdown": breakdown
        }


def main():
    """Main function to extract and save tax facts."""
    print("Singapore Tax Facts Extractor")
    print("=" * 50)
    
    extractor = TaxFactExtractor()
    
    # Extract facts from all PDFs
    print("\nExtracting facts from PDFs...")
    tax_facts = extractor.extract_all_facts()
    
    # Save to JSON
    extractor.save_to_json()
    
    # Test calculation
    print("\nTesting tax calculation for $80,000 income:")
    result = extractor.calculate_tax_example(80000)
    print(f"Total Tax: ${result['total_tax']:,.2f}")
    print(f"Effective Rate: {result['effective_rate']}%")
    print(f"Take Home: ${result['take_home']:,.2f}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("Extraction Summary:")
    print(f"- Income Tax Rates: {len(tax_facts['income_tax']['resident_rates'])} brackets")
    print(f"- Tax Reliefs: {len(tax_facts['income_tax']['reliefs'])} types")
    print(f"- GST Rate: {tax_facts['gst']['standard_rate']}%")
    print(f"- Non-resident Rate: {tax_facts['income_tax']['non_resident_rate']}%")
    print(f"- Filing Deadlines: {len(tax_facts['filing_deadlines'])} dates")
    
    return tax_facts


if __name__ == "__main__":
    main()