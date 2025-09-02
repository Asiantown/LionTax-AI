#!/usr/bin/env python
"""Enhanced Q&A system with structured facts + RAG hybrid approach."""

import os
import sys
import json
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['CHROMA_TELEMETRY'] = 'false'

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


class EnhancedTaxQA:
    """Enhanced Q&A system combining structured facts with RAG."""
    
    def __init__(self):
        """Initialize the enhanced Q&A system."""
        
        # Load structured facts
        self.tax_facts = self._load_tax_facts()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4-turbo-preview",
            openai_api_key=os.environ.get("OPENAI_API_KEY")
        )
        
        # Initialize vector database
        self.db = self._init_vector_db()
        
        # Question patterns for classification
        self.factual_patterns = [
            r"what (?:is|are) (?:the )?(?:current )?(?:tax )?rate",
            r"how much (?:is|are)",
            r"what (?:is the )?(?:maximum|minimum|cap|limit|threshold)",
            r"(?:list|what are) (?:all )?(?:the )?(?:tax )?(?:rates|reliefs|deductions)",
            r"calculate (?:tax|duty)",
            r"(?:tax|duty) (?:for|on) (?:\$|sgd|s\$)?[\d,]+",
            r"(?:deadline|due date|when)",
            r"(?:percentage|%|percent)",
            r"(?:relief|deduction) (?:amount|limit)",
            r"non-resident (?:rate|tax)",
            r"(?:gst|goods and services tax) rate",
            r"stamp duty (?:rate|calculation)",
            r"income (?:level|threshold|bracket)",
            r"marginal (?:tax )?rate",
            r"effective (?:tax )?rate"
        ]
        
        self.conceptual_patterns = [
            r"(?:how|why|explain|what is the purpose)",
            r"(?:can|should|must) (?:i|we|you)",
            r"(?:procedure|process|steps)",
            r"(?:qualify|eligible|criteria)",
            r"(?:difference between|compare)",
            r"(?:apply|claim|file)",
            r"(?:exemption|exception)",
            r"(?:regulation|law|act)",
            r"(?:definition|meaning|what does.*mean)"
        ]
    
    def _load_tax_facts(self) -> Dict:
        """Load structured tax facts from JSON."""
        facts_path = Path("singapore_tax_facts.json")
        
        if facts_path.exists():
            with open(facts_path, 'r') as f:
                return json.load(f)
        else:
            print("Warning: Tax facts file not found. Running with limited factual data.")
            return {}
    
    def _init_vector_db(self) -> Chroma:
        """Initialize or load the vector database."""
        db_path = "./data/chroma_db"
        
        if os.path.exists(db_path) and len(os.listdir(db_path)) > 0:
            embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAI_API_KEY"))
            return Chroma(
                persist_directory=db_path,
                embedding_function=embeddings
            )
        else:
            print("Warning: Vector database not found.")
            return None
    
    def classify_question(self, question: str) -> str:
        """Classify question as 'factual' or 'conceptual'."""
        question_lower = question.lower()
        
        # Check for factual patterns
        factual_score = sum(1 for pattern in self.factual_patterns 
                           if re.search(pattern, question_lower))
        
        # Check for conceptual patterns
        conceptual_score = sum(1 for pattern in self.conceptual_patterns 
                              if re.search(pattern, question_lower))
        
        # If asking for specific numbers or rates, it's factual
        if re.search(r'\$[\d,]+|sgd\s*[\d,]+|\d+\s*%|\d+k\s+income', question_lower):
            factual_score += 2
        
        # Determine classification
        if factual_score > conceptual_score:
            return "factual"
        elif conceptual_score > factual_score:
            return "conceptual"
        else:
            # Default to hybrid approach for ambiguous questions
            return "hybrid"
    
    def answer_factual_question(self, question: str) -> Tuple[str, List[str]]:
        """Answer factual questions using structured data."""
        question_lower = question.lower()
        
        # Income tax rates
        if re.search(r'(?:personal |individual )?income tax rate', question_lower):
            if 'non-resident' in question_lower or 'non resident' in question_lower:
                rate = self.tax_facts.get('income_tax', {}).get('non_resident_rate', 22)
                return (f"The tax rate for non-residents in Singapore is a flat **{rate}%** on employment income. "
                       f"This applies to individuals who are in Singapore for less than 183 days in a year."), ["singapore_tax_facts.json"]
            else:
                return self._format_income_tax_rates(), ["singapore_tax_facts.json"]
        
        # Specific income calculation
        income_match = re.search(r'\$?([\d,]+)(?:k)?(?:\s+income|\s+annually|\s+per\s+year)?', question_lower)
        if income_match and any(word in question_lower for word in ['calculate', 'tax for', 'tax on', 'earning']):
            income_str = income_match.group(1).replace(',', '')
            if 'k' in question_lower:
                income = float(income_str) * 1000
            else:
                income = float(income_str)
            
            return self._calculate_tax_with_explanation(income), ["singapore_tax_facts.json"]
        
        # Tax reliefs
        if 'relief' in question_lower:
            return self._format_reliefs(question_lower), ["singapore_tax_facts.json"]
        
        # GST rate
        if 'gst' in question_lower or 'goods and services' in question_lower:
            gst_rate = self.tax_facts.get('gst', {}).get('standard_rate', 9)
            threshold = self.tax_facts.get('gst', {}).get('registration_threshold', 1000000)
            return (f"The current GST rate in Singapore is **{gst_rate}%** (as of 2024). "
                   f"Businesses must register for GST if their annual taxable turnover exceeds S${threshold:,}."), ["singapore_tax_facts.json"]
        
        # Stamp duty
        if 'stamp duty' in question_lower:
            return self._format_stamp_duty_info(question_lower), ["singapore_tax_facts.json"]
        
        # Tax thresholds
        if any(word in question_lower for word in ['threshold', 'start paying', 'tax free', 'exempt']):
            threshold = self.tax_facts.get('key_thresholds', {}).get('start_paying_tax', 20000)
            return (f"In Singapore, you start paying income tax when your annual income exceeds **S${threshold:,}**. "
                   f"The first S${threshold:,} of income is tax-free for all tax residents."), ["singapore_tax_facts.json"]
        
        # Highest marginal rate
        if 'highest' in question_lower and 'rate' in question_lower:
            highest_rate = 22
            threshold = self.tax_facts.get('key_thresholds', {}).get('highest_marginal_rate_at', 320000)
            return (f"The highest marginal tax rate in Singapore is **{highest_rate}%**, "
                   f"which applies to income above S${threshold:,}."), ["singapore_tax_facts.json"]
        
        # Filing deadlines
        if any(word in question_lower for word in ['deadline', 'due date', 'when', 'file']):
            return self._format_deadlines(), ["singapore_tax_facts.json"]
        
        # Default to structured summary
        return self._provide_relevant_facts(question), ["singapore_tax_facts.json"]
    
    def _format_income_tax_rates(self) -> str:
        """Format income tax rates table."""
        rates = self.tax_facts.get('income_tax', {}).get('resident_rates', [])
        
        if not rates:
            return "Tax rate information not available."
        
        response = "## Singapore Resident Income Tax Rates (YA 2024)\n\n"
        response += "| Income Bracket | Rate | Tax Amount |\n"
        response += "|----------------|------|------------|\n"
        
        cumulative = 0
        for rate_info in rates:
            bracket = rate_info.get('bracket', '')
            rate = rate_info.get('rate', 0)
            tax = rate_info.get('tax', 0)
            
            if tax is not None:
                response += f"| {bracket} | {rate}% | S${tax:,} |\n"
            else:
                response += f"| {bracket} | {rate}% | - |\n"
        
        response += "\n**Key Points:**\n"
        response += "- First S$20,000 is tax-free\n"
        response += "- Tax rates are progressive (higher income portions taxed at higher rates)\n"
        response += "- Maximum rate of 22% applies to income above S$320,000"
        
        return response
    
    def _calculate_tax_with_explanation(self, income: float) -> str:
        """Calculate tax for given income with detailed breakdown."""
        rates = self.tax_facts.get('income_tax', {}).get('resident_rates', [])
        
        if not rates:
            return "Unable to calculate: Tax rate data not available."
        
        total_tax = 0
        remaining = income
        breakdown = []
        
        # Calculate based on brackets
        cumulative_limit = 0
        for rate_info in rates:
            bracket = rate_info.get('bracket', '')
            rate = rate_info.get('rate', 0)
            
            # Extract amount from bracket text
            if 'First' in bracket or 'Next' in bracket:
                amount_match = re.search(r'\$([\d,]+)', bracket)
                if amount_match:
                    bracket_amount = int(amount_match.group(1).replace(',', ''))
                    
                    if remaining <= 0:
                        break
                    
                    taxable = min(remaining, bracket_amount)
                    tax_amount = taxable * rate / 100
                    
                    if tax_amount > 0 or rate == 0:
                        breakdown.append(f"- {bracket}: S${taxable:,} × {rate}% = S${tax_amount:,.0f}")
                    
                    total_tax += tax_amount
                    remaining -= taxable
                    cumulative_limit += bracket_amount
            
            elif 'Above' in bracket and remaining > 0:
                # Final bracket
                tax_amount = remaining * rate / 100
                breakdown.append(f"- {bracket}: S${remaining:,} × {rate}% = S${tax_amount:,.0f}")
                total_tax += tax_amount
                break
        
        effective_rate = (total_tax / income) * 100 if income > 0 else 0
        
        response = f"## Tax Calculation for S${income:,.0f} Annual Income\n\n"
        response += "**Breakdown:**\n"
        response += "\n".join(breakdown)
        response += f"\n\n**Summary:**\n"
        response += f"- Total Tax: **S${total_tax:,.2f}**\n"
        response += f"- Effective Tax Rate: **{effective_rate:.2f}%**\n"
        response += f"- Take-Home Income: **S${income - total_tax:,.2f}**\n"
        response += f"- Monthly Take-Home: **S${(income - total_tax) / 12:,.2f}**"
        
        return response
    
    def _format_reliefs(self, question: str) -> str:
        """Format tax relief information."""
        reliefs = self.tax_facts.get('income_tax', {}).get('reliefs', {})
        
        response = "## Singapore Tax Reliefs (YA 2024)\n\n"
        
        # Check if asking about specific relief
        if 'spouse' in question:
            spouse_relief = reliefs.get('spouse_relief', 2000)
            response = f"**Spouse Relief:** S${spouse_relief:,}\n\n"
            response += "**Conditions:**\n"
            response += "- Your spouse must not have an annual income exceeding S$4,000\n"
            response += "- You must be legally married\n"
            response += "- Your spouse must be living with you or supported by you\n"
            return response
        
        if 'child' in question:
            child_relief = reliefs.get('qualifying_child_relief', 4000)
            handicapped = reliefs.get('handicapped_child_relief', 7500)
            response = f"**Child Relief:**\n"
            response += f"- Qualifying Child Relief (QCR): S${child_relief:,} per child\n"
            response += f"- Handicapped Child Relief (HCR): S${handicapped:,} per child\n\n"
            response += "**Conditions:**\n"
            response += "- Child must be unmarried\n"
            response += "- Child must be under 16, or studying full-time\n"
            response += "- For HCR, child must have physical/mental disabilities\n"
            return response
        
        if 'parent' in question:
            parent_relief = reliefs.get('parent_relief', 9000)
            handicapped_parent = reliefs.get('handicapped_parent_relief', 14000)
            response = f"**Parent Relief:**\n"
            response += f"- Parent Relief: S${parent_relief:,} per parent\n"
            response += f"- Handicapped Parent Relief: S${handicapped_parent:,} per parent\n\n"
            response += "**Conditions:**\n"
            response += "- Parent must be 55 years or above (or handicapped)\n"
            response += "- Parent's income must not exceed S$4,000 per year\n"
            response += "- You must have supported your parent with at least S$2,000 in the year\n"
            return response
        
        if 'earned income' in question:
            eir = reliefs.get('earned_income_relief', {})
            response = "**Earned Income Relief:**\n"
            response += f"- Amount: Lower of S$1,000 or 1% of earned income\n"
            response += f"- Maximum cap: S$1,000\n"
            response += "- Automatically granted to all tax residents with earned income\n"
            response += "- For disabled individuals: S$4,000 cap\n"
            return response
        
        # General reliefs listing
        response += "**Personal Reliefs Available:**\n\n"
        
        main_reliefs = {
            "Earned Income Relief": "Max S$1,000 (1% of income)",
            "Spouse Relief": "S$2,000",
            "Qualifying Child Relief": "S$4,000 per child",
            "Handicapped Child Relief": "S$7,500 per child",
            "Working Mother's Child Relief": "15% of earned income per child",
            "Parent Relief": "S$9,000",
            "Handicapped Parent Relief": "S$14,000",
            "Grandparent Caregiver Relief": "S$3,000",
            "Handicapped Sibling Relief": "S$5,500",
            "CPF Cash Top-up Relief": "S$8,000",
            "Course Fees Relief": "S$5,500",
            "NSman Relief": "S$3,000 (self), S$750 (wife/parent)",
            "Life Insurance Premium Relief": "Max S$5,000",
            "SRS Contribution": "S$15,300"
        }
        
        for relief_name, amount in main_reliefs.items():
            response += f"- **{relief_name}:** {amount}\n"
        
        return response
    
    def _format_stamp_duty_info(self, question: str) -> str:
        """Format stamp duty information."""
        bsd_rates = self.tax_facts.get('stamp_duty', {}).get('bsd_rates', [])
        absd_rates = self.tax_facts.get('stamp_duty', {}).get('absd_rates', {})
        
        response = "## Singapore Stamp Duty Rates (2024)\n\n"
        
        # Buyer's Stamp Duty
        response += "### Buyer's Stamp Duty (BSD)\n"
        response += "| Property Price | Rate |\n"
        response += "|---------------|------|\n"
        
        for rate_info in bsd_rates:
            price_range = rate_info.get('price_range', '')
            rate = rate_info.get('rate', 0)
            response += f"| {price_range} | {rate}% |\n"
        
        # Additional Buyer's Stamp Duty
        response += "\n### Additional Buyer's Stamp Duty (ABSD)\n"
        response += "| Buyer Profile | 1st Property | 2nd Property | 3rd+ Property |\n"
        response += "|--------------|--------------|--------------|---------------|\n"
        response += f"| Singapore Citizen | 0% | 20% | 30% |\n"
        response += f"| Permanent Resident | 5% | 30% | 35% |\n"
        response += f"| Foreigner | 60% | 60% | 60% |\n"
        response += f"| Entity | 65% | 65% | 65% |\n"
        
        return response
    
    def _format_deadlines(self) -> str:
        """Format tax filing deadlines."""
        deadlines = self.tax_facts.get('filing_deadlines', {})
        
        response = "## Singapore Tax Filing Deadlines (2024)\n\n"
        response += f"- **E-Filing Deadline:** {deadlines.get('e_filing', '18 April')}\n"
        response += f"- **Paper Filing Deadline:** {deadlines.get('paper_filing', '15 April')}\n"
        response += f"- **Corporate Tax Filing:** {deadlines.get('corporate', '30 November')}\n"
        response += f"- **GST Filing (Quarterly):** {deadlines.get('gst_quarterly', 'One month after quarter end')}\n\n"
        response += "**Note:** E-filing gives you 3 extra days compared to paper filing."
        
        return response
    
    def _provide_relevant_facts(self, question: str) -> str:
        """Provide relevant facts based on question keywords."""
        question_lower = question.lower()
        response_parts = []
        
        # Check what the question is about and provide relevant facts
        if 'income' in question_lower or 'personal' in question_lower:
            response_parts.append(self._format_income_tax_rates())
        
        if 'relief' in question_lower or 'deduction' in question_lower:
            response_parts.append(self._format_reliefs(question_lower))
        
        if 'gst' in question_lower:
            gst_rate = self.tax_facts.get('gst', {}).get('standard_rate', 9)
            response_parts.append(f"**GST Rate:** {gst_rate}% (current as of 2024)")
        
        if 'deadline' in question_lower or 'filing' in question_lower:
            response_parts.append(self._format_deadlines())
        
        if response_parts:
            return "\n\n".join(response_parts)
        else:
            return "Please specify what tax information you need (e.g., income tax rates, reliefs, GST, stamp duty, deadlines)."
    
    def answer_conceptual_question(self, question: str) -> Tuple[str, List[str]]:
        """Answer conceptual questions using RAG."""
        if not self.db:
            return "Vector database not available for conceptual questions.", []
        
        # Search for relevant documents
        docs = self.db.similarity_search(question, k=5)  # Increased from 3 to 5
        
        if not docs:
            return "No relevant information found in the documents.", []
        
        # Build context from documents
        context = "\n\n".join([doc.page_content for doc in docs])
        sources = list(set([doc.metadata.get('source', 'Unknown') for doc in docs]))
        
        # Create prompt for conceptual answer
        prompt = f"""You are a Singapore tax expert. Answer the question based on the context below.
        
Context from Singapore tax laws:
{context[:4000]}

Question: {question}

Provide a comprehensive answer explaining the concepts, procedures, and requirements.
If specific numbers or rates are mentioned in the context, include them.

Answer:"""
        
        # Get response from LLM
        response = self.llm.invoke(prompt)
        
        return response.content, sources
    
    def answer_hybrid_question(self, question: str) -> Tuple[str, List[str]]:
        """Answer questions that need both factual and conceptual information."""
        
        # Get factual answer
        factual_answer, fact_sources = self.answer_factual_question(question)
        
        # Get conceptual answer
        conceptual_answer, concept_sources = self.answer_conceptual_question(question)
        
        # Combine answers intelligently
        prompt = f"""Combine the following factual and conceptual information to provide a comprehensive answer:

Factual Information:
{factual_answer}

Conceptual Information:
{conceptual_answer}

Original Question: {question}

Provide a unified, comprehensive answer that includes both the specific facts/numbers and the conceptual explanation:"""
        
        response = self.llm.invoke(prompt)
        
        # Combine sources
        all_sources = list(set(fact_sources + concept_sources))
        
        return response.content, all_sources
    
    def answer_question(self, question: str) -> Tuple[str, List[str]]:
        """Main method to answer any question."""
        
        # Classify the question
        question_type = self.classify_question(question)
        
        print(f"[Question classified as: {question_type}]")
        
        # Route to appropriate handler
        if question_type == "factual":
            return self.answer_factual_question(question)
        elif question_type == "conceptual":
            return self.answer_conceptual_question(question)
        else:  # hybrid
            return self.answer_hybrid_question(question)


def main():
    """Main function for testing the enhanced Q&A system."""
    print("🇸🇬 Enhanced Singapore Tax Q&A System")
    print("=" * 50)
    
    # Initialize system
    qa_system = EnhancedTaxQA()
    print("✅ System initialized with structured facts + RAG\n")
    
    # Test questions that previously failed
    test_questions = [
        "What are the current personal income tax rates for Singapore residents?",
        "What is the tax rate for non-residents?",
        "At what income level do I start paying income tax in Singapore?",
        "What is the highest marginal tax rate for individuals?",
        "How is tax calculated for someone earning S$80,000 annually?",
        "What personal reliefs am I entitled to as a Singapore resident?",
        "How much can I claim for spouse relief if my spouse has no income?",
        "What is the maximum amount I can claim for child relief?",
        "Can I claim tax relief for my parents? What are the conditions?",
        "What is the Earned Income Relief and how is it calculated?"
    ]
    
    if len(sys.argv) > 1:
        # Use command line argument as question
        question = " ".join(sys.argv[1:])
        print(f"Question: {question}\n")
        answer, sources = qa_system.answer_question(question)
        print(f"Answer:\n{answer}\n")
        if sources:
            print(f"Sources: {', '.join(sources)}")
    else:
        # Interactive mode or test mode
        print("Running test questions...\n")
        
        for i, question in enumerate(test_questions[:3], 1):  # Test first 3
            print(f"{i}. {question}")
            answer, sources = qa_system.answer_question(question)
            print(f"\nAnswer: {answer[:500]}...")  # Show first 500 chars
            print(f"Sources: {sources}")
            print("-" * 50 + "\n")
        
        # Interactive mode
        print("\nEnter your tax questions (type 'exit' to quit):\n")
        
        while True:
            question = input("❓ Your question: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not question:
                continue
            
            print("\nSearching...\n")
            answer, sources = qa_system.answer_question(question)
            
            print(f"📝 Answer:\n{answer}\n")
            if sources:
                print(f"📚 Sources: {', '.join(sources)}\n")
            print("-" * 50 + "\n")


if __name__ == "__main__":
    main()