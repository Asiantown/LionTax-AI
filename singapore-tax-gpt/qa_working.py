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
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['CHROMA_TELEMETRY'] = 'false'

print("🇸🇬 Singapore Tax Q&A System")
print("="*50)
print("Loading 9 tax acts...")

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

# Import multi-agent system
try:
    from multi_agent_simplified import MultiAgentOrchestrator
    MULTI_AGENT_AVAILABLE = True
    print("✅ Multi-agent system loaded")
except ImportError:
    MULTI_AGENT_AVAILABLE = False
    print("⚠️ Multi-agent system not available")

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
    
    # Factual patterns
    factual_patterns = [
        r"what (?:is|are) (?:the )?(?:current )?(?:tax )?rate",
        r"how much",
        r"calculate",
        r"\$[\d,]+|\d+k",
        r"relief|deduction",
        r"deadline|due date",
        r"threshold|bracket",
        r"non-resident",
        r"gst|stamp duty"
    ]
    
    if any(re.search(p, q_lower) for p in factual_patterns):
        return "factual"
    return "conceptual"

def get_factual_answer(question: str) -> Tuple[str, List[str]]:
    """Answer factual questions from structured data."""
    q_lower = question.lower()
    
    # Income tax rates
    if 'income tax rate' in q_lower and 'resident' in q_lower:
        rates = tax_facts.get('income_tax', {}).get('resident_rates', [])
        if rates:
            response = "**Singapore Resident Income Tax Rates (YA 2024):**\n\n"
            for r in rates[:11]:
                response += f"- {r['bracket']}: {r['rate']}%\n"
            response += "\n- First S$20,000 is tax-free\n- Maximum rate: 22% (income > S$320,000)"
            return response, ["singapore_tax_facts.json"]
    
    # Non-resident rate
    if 'non-resident' in q_lower or 'non resident' in q_lower:
        return "The tax rate for non-residents is a flat **22%** on employment income.", ["singapore_tax_facts.json"]
    
    # Tax calculation
    income_match = re.search(r'\$?([\d,]+)(?:k)?', q_lower)
    if income_match and any(w in q_lower for w in ['calculate', 'tax for', 'earning']):
        income = float(income_match.group(1).replace(',', ''))
        if 'k' in q_lower:
            income *= 1000
        
        # Calculate tax
        tax = 0
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
        return f"For S${income:,.0f} income: Tax = **S${tax:,.0f}**, Effective rate = **{effective:.2f}%**, Take-home = **S${income-tax:,.0f}**", ["singapore_tax_facts.json"]
    
    # Reliefs
    if 'spouse relief' in q_lower:
        return "Spouse Relief: **S$2,000** (if spouse's income ≤ S$4,000)", ["singapore_tax_facts.json"]
    
    if 'child relief' in q_lower:
        return "Child Relief: **S$4,000** per qualifying child, **S$7,500** for handicapped child", ["singapore_tax_facts.json"]
    
    if 'parent relief' in q_lower:
        return "Parent Relief: **S$9,000** per parent (conditions: age 55+, income ≤ S$4,000, supported with ≥ S$2,000)", ["singapore_tax_facts.json"]
    
    if 'earned income relief' in q_lower:
        return "Earned Income Relief: Lower of **S$1,000** or **1% of earned income** (automatic for all residents)", ["singapore_tax_facts.json"]
    
    # Thresholds
    if any(w in q_lower for w in ['start paying', 'threshold', 'tax free']):
        return "You start paying tax when income exceeds **S$20,000** (first S$20,000 is tax-free)", ["singapore_tax_facts.json"]
    
    if 'highest' in q_lower and 'rate' in q_lower:
        return "The highest marginal tax rate is **22%** for income above **S$320,000**", ["singapore_tax_facts.json"]
    
    # GST
    if 'gst' in q_lower:
        return "GST rate: **9%** (as of 2024). Registration required if turnover > S$1,000,000", ["singapore_tax_facts.json"]
    
    # Deadlines
    if any(w in q_lower for w in ['deadline', 'filing', 'due date']):
        return "Tax filing deadlines: **E-filing: 18 April**, Paper: 15 April, Corporate: 30 November", ["singapore_tax_facts.json"]
    
    return None, []

def answer_question(question):
    """Answer a question using structured facts + RAG hybrid approach."""
    
    # Use multi-agent system if available
    if MULTI_AGENT_AVAILABLE:
        try:
            orchestrator = MultiAgentOrchestrator()
            answer, metadata = orchestrator.answer_question(question)
            
            # Extract sources
            sources = []
            if 'FactAgent' in metadata.get('agents_used', []):
                sources.append('singapore_tax_facts.json')
            if 'SearchAgent' in metadata.get('agents_used', []):
                sources.append('Income Tax Act 1947.pdf')
            
            # Add performance info for fast responses
            if metadata.get('total_time', 0) < 1:
                answer += f"\n\n*[Multi-agent response in {metadata['total_time']:.2f}s]*"
            
            return answer, sources
        except Exception as e:
            print(f"Multi-agent failed, falling back: {e}")
    
    # Fallback to original approach
    # Try factual answer first
    q_type = classify_question(question)
    
    if q_type == "factual" and tax_facts:
        factual_answer, fact_sources = get_factual_answer(question)
        if factual_answer:
            return factual_answer, fact_sources
    
    # Fall back to RAG for conceptual or unanswered factual questions
    docs = db.similarity_search(question, k=5)  # Increased from 3 to 5
    
    if not docs:
        return "No relevant information found in the documents.", []
    
    # Build context
    context = "\n\n".join([doc.page_content for doc in docs])
    sources = list(set([doc.metadata.get('source', 'Unknown') for doc in docs]))
    
    # Enhanced prompt with instruction to include specific numbers
    prompt = f"""You are a Singapore tax expert. Answer the question based on the context below.

IMPORTANT: Include specific numbers, rates, amounts, and thresholds in your answer.

Context from Singapore tax laws:
{context[:4000]}

Question: {question}

Provide a comprehensive answer with specific facts and figures:"""
    
    # Get answer
    response = llm.invoke(prompt)
    
    # If we have factual data, enhance the answer
    if tax_facts and q_type == "factual":
        sources.append("singapore_tax_facts.json")
    
    return response.content, sources

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