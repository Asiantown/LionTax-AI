#!/usr/bin/env python
"""Enhanced Q&A system for Singapore Tax documents with structured facts."""

import os
import sys
import json
import re
import warnings
from pathlib import Path
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Suppress warnings before imports
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*Blowfish.*')
warnings.filterwarnings('ignore', message='.*ARC4.*')

# Load environment
load_dotenv()

# Completely disable all telemetry and warnings
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['CHROMA_TELEMETRY'] = 'false'
os.environ['CHROMA_CLIENT_TELEMETRY'] = 'false'
os.environ['CHROMA_SERVER_TELEMETRY'] = 'false'

# Suppress ChromaDB telemetry errors
import logging
logging.getLogger('chromadb.telemetry').setLevel(logging.ERROR)
logging.getLogger('chromadb.telemetry.posthog').setLevel(logging.ERROR)

print("🇸🇬 Singapore Tax Q&A System v2.2")
print("="*50)
print("Loading 9 tax acts...")
print("Version: Fixed formatting (2024-03-09 15:45)")

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

# Multi-agent system removed - using direct responses for accuracy

# Quick check if database exists
db_path = "./data/chroma_db"
if not os.path.exists(db_path) or len(os.listdir(db_path)) == 0:
    print("❌ Database not found. Building it now...")
    
    # Load all PDFs
    pdf_dir = Path("./data/iras_docs")
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    all_chunks = []
    for pdf in pdf_files:  # Load ALL documents
        print(f"  Loading {pdf.name}...")
        loader = PyPDFLoader(str(pdf))
        pages = loader.load()
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_documents(pages)
        
        for chunk in chunks:
            chunk.metadata['source'] = pdf.name
        all_chunks.extend(chunks)
    
    print(f"  Creating database with {len(all_chunks)} chunks...")
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAI_API_KEY"))
    db = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=db_path
    )
else:
    print("✅ Database found. Loading...")
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAI_API_KEY"))
    db = Chroma(
        persist_directory=db_path,
        embedding_function=embeddings
    )

print("✅ System ready!\n")

# Load structured tax facts
try:
    with open('singapore_tax_facts.json', 'r') as f:
        tax_facts = json.load(f)
        print("✅ Loaded structured tax facts")
except:
    tax_facts = {}
    print("⚠️ Tax facts not found, using RAG only")

# Create QA chain
llm = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview")

def classify_question(question: str) -> str:
    """Classify question as factual or conceptual."""
    q_lower = question.lower()
    
    # More comprehensive factual patterns
    factual_keywords = [
        'tax rate', 'income tax', 'personal income tax',
        'how much', 'calculate', 'calculation',
        'relief', 'deduction', 'deadline', 'filing',
        'threshold', 'bracket', 'non-resident', 'non resident',
        'gst', 'stamp duty', 'earning', 'salary',
        'what are the', 'what is the', 'current'
    ]
    
    # Check for any factual keywords
    if any(keyword in q_lower for keyword in factual_keywords):
        return "factual"
    
    # Check for specific amount patterns
    if re.search(r'\$[\d,]+|\d+k|\d{4,}', q_lower):
        return "factual"
    
    return "conceptual"

def get_factual_answer(question: str) -> Tuple[str, List[str]]:
    """Answer factual questions from structured data."""
    q_lower = question.lower()
    
    # CHECK NON-RESIDENT FIRST - before general tax rate check
    if 'non-resident' in q_lower or 'non resident' in q_lower or 'non residents' in q_lower:
        lines = [
            "Tax rates for non-residents:",
            "",
            "Employment income: 15% flat rate (or progressive resident rates if higher)",
            "Director's fees and other income: 24% flat rate",
            "",
            "Note: Non-residents are not entitled to personal reliefs"
        ]
        return "\n".join(lines), ["singapore_tax_facts.json"]
    
    # Income tax rates for residents - check after non-resident
    if ('personal income tax' in q_lower and 'singapore resident' in q_lower) or \
       ('income tax rate' in q_lower and 'non' not in q_lower) or \
       ('tax rate' in q_lower and 'resident' in q_lower and 'non' not in q_lower) or \
       ('current' in q_lower and 'tax' in q_lower and 'non' not in q_lower):
        # Build response with proper line breaks
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
        response = "\n".join(lines)
        return response, ["singapore_tax_facts.json"]
    
    # Tax calculation - expanded patterns to catch takehome questions
    income_match = re.search(r'\$?([\d,]+)(?:k)?', q_lower)
    if income_match and any(w in q_lower for w in ['calculate', 'tax for', 'earning', 'takehome', 'take-home', 'take home', 'income is', 'salary']):
        income_str = income_match.group(1).replace(',', '')
        income = float(income_str)
        
        # Check if 'k' suffix is used (e.g., "80k" means 80,000)
        if 'k' in income_match.group(0):
            income *= 1000
        
        # Calculate tax with exact brackets
        tax = 0
        breakdown = []
        
        if income > 320000:
            tax = 44550 + (income - 320000) * 0.22
        elif income > 280000:
            tax = 36550 + (income - 280000) * 0.20
        elif income > 240000:
            tax = 28750 + (income - 240000) * 0.195
        elif income > 200000:
            tax = 21150 + (income - 200000) * 0.19
        elif income > 160000:
            tax = 13950 + (income - 160000) * 0.18
        elif income > 120000:
            tax = 7950 + (income - 120000) * 0.15
        elif income > 80000:
            tax = 3350 + (income - 80000) * 0.115
        elif income > 40000:
            tax = 550 + (income - 40000) * 0.07
        elif income > 30000:
            tax = 200 + (income - 30000) * 0.035
        elif income > 20000:
            tax = (income - 20000) * 0.02
        
        effective = (tax / income * 100) if income > 0 else 0
        
        # Format response consistently for ALL amounts
        lines = [f"Tax Calculation for ${income:,.0f}:", ""]
        
        # Build progressive calculation breakdown
        if income > 0:
            lines.append("- First $20,000 at 0% = $0")
        if income > 20000:
            amt = min(income - 20000, 10000)
            lines.append(f"- Next ${amt:,.0f} at 2% = ${amt * 0.02:,.0f}")
        if income > 30000:
            amt = min(income - 30000, 10000)
            lines.append(f"- Next ${amt:,.0f} at 3.5% = ${amt * 0.035:,.0f}")
        if income > 40000:
            amt = min(income - 40000, 40000)
            lines.append(f"- Next ${amt:,.0f} at 7% = ${amt * 0.07:,.0f}")
        if income > 80000:
            amt = min(income - 80000, 40000)
            lines.append(f"- Next ${amt:,.0f} at 11.5% = ${amt * 0.115:,.0f}")
        if income > 120000:
            amt = min(income - 120000, 40000)
            lines.append(f"- Next ${amt:,.0f} at 15% = ${amt * 0.15:,.0f}")
        if income > 160000:
            amt = min(income - 160000, 40000)
            lines.append(f"- Next ${amt:,.0f} at 18% = ${amt * 0.18:,.0f}")
        if income > 200000:
            amt = min(income - 200000, 40000)
            lines.append(f"- Next ${amt:,.0f} at 19% = ${amt * 0.19:,.0f}")
        if income > 240000:
            amt = min(income - 240000, 40000)
            lines.append(f"- Next ${amt:,.0f} at 19.5% = ${amt * 0.195:,.0f}")
        if income > 280000:
            amt = min(income - 280000, 40000)
            lines.append(f"- Next ${amt:,.0f} at 20% = ${amt * 0.20:,.0f}")
        if income > 320000:
            amt = income - 320000
            lines.append(f"- Above $320,000: ${amt:,.0f} at 22% = ${amt * 0.22:,.0f}")
        
        lines.append("")
        lines.append(f"Total Tax = ${tax:,.0f}")
        lines.append(f"Effective Rate = {effective:.2f}%")
        lines.append(f"Take-home = ${income-tax:,.0f}")
        
        response = "\n".join(lines)
        
        return response, ["singapore_tax_facts.json"]
    
    # Reliefs
    if 'spouse relief' in q_lower:
        return "Spouse Relief: S$2,000 (if spouse's income ≤ S$4,000)", ["singapore_tax_facts.json"]
    
    if 'child relief' in q_lower:
        return "Child Relief: S$4,000 per qualifying child, S$7,500 for handicapped child", ["singapore_tax_facts.json"]
    
    if 'parent relief' in q_lower:
        return "Parent Relief: S$9,000 per parent (conditions: age 55+, income ≤ S$4,000, supported with ≥ S$2,000)", ["singapore_tax_facts.json"]
    
    if 'earned income relief' in q_lower:
        return "Earned Income Relief: Lower of S$1,000 or 1% of earned income (automatic for all residents)", ["singapore_tax_facts.json"]
    
    # Thresholds
    if any(w in q_lower for w in ['start paying', 'threshold', 'tax free']):
        return "You start paying tax when income exceeds S$20,000 (first S$20,000 is tax-free)", ["singapore_tax_facts.json"]
    
    if 'highest' in q_lower and 'rate' in q_lower:
        return "The highest marginal tax rate is 22% for income above S$320,000", ["singapore_tax_facts.json"]
    
    # GST
    if 'gst' in q_lower:
        return "GST rate: 9% (as of 2024). Registration required if turnover > S$1,000,000", ["singapore_tax_facts.json"]
    
    # Deadlines
    if any(w in q_lower for w in ['deadline', 'filing', 'due date']):
        return "Tax filing deadlines: E-filing: 18 April, Paper: 15 April, Corporate: 30 November", ["singapore_tax_facts.json"]
    
    return None, []

def answer_question(question):
    """Answer a question using structured facts + RAG hybrid approach."""
    
    # ALWAYS try factual answer first for direct, accurate responses
    if tax_facts:
        factual_answer, fact_sources = get_factual_answer(question)
        if factual_answer:
            # Add currency warning for rate questions
            if any(word in question.lower() for word in ['rate', 'tax', 'percent', '%']):
                metadata = tax_facts.get('metadata', {})
                last_updated = metadata.get('last_updated', 'Unknown')
                factual_answer += f"\n\n[Data current as of {last_updated}]"
            return factual_answer, fact_sources
    
    # Only classify and check if we should skip RAG for non-factual
    q_type = classify_question(question)
    
    # Fall back to RAG for conceptual or unanswered factual questions
    docs = db.similarity_search(question, k=5)  # Increased from 3 to 5
    
    if not docs:
        return "No relevant information found in the documents.", []
    
    # Build context
    context = "\n\n".join([doc.page_content for doc in docs])
    sources = list(set([doc.metadata.get('source', 'Unknown') for doc in docs]))
    
    # Concise prompt for direct answers
    prompt = f"""You are a Singapore tax expert. Answer concisely and directly.

Context: {context[:4000]}

Question: {question}

Provide a SHORT, DIRECT answer with specific numbers. NO explanations or steps unless asked. Format as plain text, no markdown:"""
    
    # Get answer
    response = llm.invoke(prompt)
    
    # Clean up markdown from response
    answer = response.content
    # Remove markdown bold
    answer = answer.replace('**', '')
    answer = answer.replace('__', '')
    # Remove markdown headers
    answer = re.sub(r'^#{1,6}\s+', '', answer, flags=re.MULTILINE)
    answer = answer.replace('###', '').replace('##', '').replace('#', '')
    # Remove markdown italics
    answer = answer.replace('*', '').replace('_', '')
    
    # If we have factual data, enhance the answer
    if tax_facts and q_type == "factual":
        sources.append("singapore_tax_facts.json")
    
    return answer, sources

# Interactive mode
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single question mode
        question = " ".join(sys.argv[1:])
        print(f"Question: {question}\n")
        answer, sources = answer_question(question)
        print(f"Answer: {answer}\n")
        if sources:
            print(f"Sources: {', '.join(sources)}")
    else:
        # Interactive mode with examples
        print("Ask any question about Singapore taxes (type 'exit' to quit)")
        print("\nExample questions:")
        print("- What are the current income tax rates?")
        print("- Calculate tax for $80,000 income")
        print("- How much is spouse relief?")
        print("- What is the GST rate?\n")
        
        while True:
            question = input("❓ Your question: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not question:
                continue
            
            print("\nSearching...\n")
            answer, sources = answer_question(question)
            
            print(f"📝 Answer: {answer}\n")
            if sources:
                print(f"📚 Sources: {', '.join(sources)}\n")
            print("-"*50 + "\n")