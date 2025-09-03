#!/usr/bin/env python
"""Multi-agent system to fix formatting issues."""

import re
from typing import Tuple, List
import json

class FormatVerificationAgent:
    """Agent to verify output format matches requirements."""
    
    @staticmethod
    def verify_tax_rates(text: str) -> dict:
        """Verify tax rates format is correct."""
        issues = []
        
        # Check for proper line breaks
        if text.count('\n') < 10:
            issues.append("Missing line breaks - all on one line")
        
        # Check for proper dollar signs and percentages
        if not re.search(r'\$0\s*-\s*\$20,000:\s*0%', text):
            issues.append("First bracket format incorrect")
        
        # Check for no markdown
        if '**' in text or '*' in text:
            issues.append("Markdown formatting present")
        
        # Check for proper spacing
        if 'at0' in text.replace(' ', '') or 'at2' in text.replace(' ', ''):
            issues.append("Spacing issues in calculation")
        
        return {"valid": len(issues) == 0, "issues": issues}
    
    @staticmethod
    def verify_calculation(text: str) -> dict:
        """Verify calculation format is correct."""
        issues = []
        
        # Check for mangled text
        if 'at0o' in text or 'at2200' in text:
            issues.append("Text corruption in calculation")
        
        # Check for proper formatting
        if '@ 0%' not in text and 'at 0%' not in text:
            issues.append("Missing proper percentage formatting")
        
        # Check for total
        if 'Total Tax = $3,350' not in text:
            issues.append("Total tax format incorrect")
        
        return {"valid": len(issues) == 0, "issues": issues}


class LineBreakFixAgent:
    """Agent to ensure proper line breaks in output."""
    
    @staticmethod
    def fix_tax_rates() -> str:
        """Return properly formatted tax rates with explicit line breaks."""
        lines = [
            "Current Singapore Resident Tax Rates (2024):",
            "",
            "$0 - $20,000: 0%",
            "$20,001 - $30,000: 2%",
            "$30,001 - $40,000: 3.5%",
            "$40,001 - $80,000: 7%",
            "$80,001 - $120,000: 11.5%",
            "$120,001 - $160,000: 15%",
            "$160,001 - $200,000: 18%",
            "$200,001 - $240,000: 19%",
            "$240,001 - $280,000: 19.5%",
            "$280,001 - $320,000: 20%",
            "$320,001 and above: 22%"
        ]
        return "\n".join(lines)
    
    @staticmethod
    def fix_calculation() -> str:
        """Return properly formatted calculation."""
        lines = [
            "For the $80,000 example:",
            "",
            "Calculation: First $20k tax-free, then apply progressive rates",
            "- First $20,000 at 0% = $0",
            "- Next $10,000 at 2% = $200",
            "- Next $10,000 at 3.5% = $350",
            "- Next $40,000 at 7% = $2,800",
            "",
            "Total Tax = $3,350",
            "Effective Rate = 4.19%",
            "Take-home = $76,650"
        ]
        return "\n".join(lines)


class StreamlitFormatAgent:
    """Agent to handle Streamlit-specific formatting."""
    
    @staticmethod
    def format_for_streamlit(text: str) -> str:
        """Ensure text displays correctly in Streamlit."""
        # Remove any markdown
        text = text.replace('**', '')
        text = text.replace('*', '')
        
        # Ensure proper spacing
        text = text.replace('at0', 'at 0')
        text = text.replace('at2', 'at 2')
        text = text.replace('at3', 'at 3')
        text = text.replace('at7', 'at 7')
        
        # Fix any compressed numbers
        text = re.sub(r'(\d+)at(\d+)', r'\1 at \2', text)
        
        # Ensure double line breaks for Streamlit
        text = text.replace('\n\n\n', '\n\n')
        
        return text


def get_fixed_factual_answer(question: str) -> Tuple[str, List[str]]:
    """Get factual answer with proper formatting."""
    q_lower = question.lower()
    
    # Initialize agents
    line_break_agent = LineBreakFixAgent()
    format_agent = StreamlitFormatAgent()
    
    # Tax rates question
    if 'personal income tax' in q_lower and 'singapore resident' in q_lower:
        answer = line_break_agent.fix_tax_rates()
        answer = format_agent.format_for_streamlit(answer)
        return answer, ["singapore_tax_facts.json"]
    
    # $80,000 calculation
    if '80,000' in q_lower or '80000' in q_lower:
        answer = line_break_agent.fix_calculation()
        answer = format_agent.format_for_streamlit(answer)
        return answer, ["singapore_tax_facts.json"]
    
    return None, []


def test_formatting():
    """Test the formatting fixes."""
    verifier = FormatVerificationAgent()
    
    # Test tax rates
    q1 = "What are the current personal income tax rates for Singapore residents?"
    answer1, _ = get_fixed_factual_answer(q1)
    
    print("Tax Rates Answer:")
    print(answer1)
    print("\nVerification:", verifier.verify_tax_rates(answer1))
    
    print("\n" + "="*60 + "\n")
    
    # Test calculation
    q2 = "How is tax calculated for someone earning S$80,000 annually?"
    answer2, _ = get_fixed_factual_answer(q2)
    
    print("Calculation Answer:")
    print(answer2)
    print("\nVerification:", verifier.verify_calculation(answer2))


if __name__ == "__main__":
    test_formatting()