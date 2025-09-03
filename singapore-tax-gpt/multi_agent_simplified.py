#!/usr/bin/env python
"""Simplified Multi-Agent System for Singapore Tax GPT.

Following best practices:
- Stateless agents (pure functions)
- Clear task boundaries
- Parallel execution where possible
- Fast, focused agents
"""

import json
import re
import time
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings('ignore')

import os
from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# AGENT 1: FACT CHECKER (Ultra-fast, structured data lookup)
# ============================================================================

class FactAgent:
    """Lightning-fast agent for factual queries using structured data."""
    
    def __init__(self):
        # Load pre-computed facts (no LLM needed!)
        with open('singapore_tax_facts.json', 'r') as f:
            self.facts = json.load(f)
    
    def can_handle(self, query: str) -> bool:
        """Check if this agent can handle the query."""
        q = query.lower()
        patterns = [
            'tax rate', 'relief', 'deduction', 'threshold',
            'deadline', 'gst', 'stamp duty', 'calculate',
            'how much', 'what is the', 'marginal rate'
        ]
        return any(p in q for p in patterns)
    
    def process(self, query: str) -> Dict:
        """Process factual query instantly."""
        start = time.time()
        q = query.lower()
        
        # Tax rates
        if 'tax rate' in q and 'non-resident' in q:
            answer = f"Non-resident tax rate: **22% flat rate** on employment income"
            confidence = 1.0
        
        elif 'tax rate' in q or 'income tax' in q:
            rates = self.facts['income_tax']['resident_rates']
            answer = "**Singapore Tax Rates (2024):**\n"
            for r in rates[:5]:  # Show first 5 brackets
                answer += f"- {r['bracket']}: {r['rate']}%\n"
            answer += f"...up to 22% for income > $320,000"
            confidence = 1.0
        
        # Reliefs
        elif 'spouse relief' in q:
            answer = f"Spouse Relief: **$2,000** (if spouse's income ≤ $4,000)"
            confidence = 1.0
        
        elif 'child relief' in q:
            answer = f"Child Relief: **$4,000** per qualifying child, **$7,500** for handicapped"
            confidence = 1.0
        
        elif 'parent relief' in q:
            answer = f"Parent Relief: **$9,000** (age 55+, income ≤ $4,000, min support $2,000)"
            confidence = 1.0
        
        # Thresholds
        elif 'start paying' in q or 'threshold' in q:
            answer = f"Tax-free threshold: First **$20,000** of income is not taxed"
            confidence = 1.0
        
        elif 'highest' in q and 'rate' in q:
            answer = f"Highest marginal rate: **22%** for income above **$320,000**"
            confidence = 1.0
        
        # GST
        elif 'gst' in q:
            answer = f"GST Rate: **9%** (2024)\nRegistration threshold: $1,000,000 annual turnover"
            confidence = 1.0
        
        # Deadlines
        elif 'deadline' in q or 'filing' in q:
            answer = "Filing deadlines:\n- E-filing: **18 April**\n- Paper: **15 April**"
            confidence = 1.0
        
        else:
            answer = None
            confidence = 0.0
        
        return {
            "agent": "FactAgent",
            "answer": answer,
            "confidence": confidence,
            "time": time.time() - start,
            "source": "singapore_tax_facts.json"
        }


# ============================================================================
# AGENT 2: CALCULATOR (Pure math, no LLM)
# ============================================================================

class CalculatorAgent:
    """Pure calculation agent for tax computations."""
    
    def can_handle(self, query: str) -> bool:
        """Check if query needs calculation."""
        q = query.lower()
        return bool(re.search(r'\$?[\d,]+', q) and 
                   any(w in q for w in ['calculate', 'tax for', 'earning', 'income']))
    
    def process(self, query: str) -> Dict:
        """Calculate tax from income."""
        start = time.time()
        
        # Extract income
        match = re.search(r'\$?([\d,]+)(?:k)?', query.lower())
        if not match:
            return {"agent": "CalculatorAgent", "answer": None, "confidence": 0.0}
        
        income = float(match.group(1).replace(',', ''))
        if 'k' in query.lower():
            income *= 1000
        
        # Check if non-resident
        if 'non-resident' in query.lower():
            tax = income * 0.22
            answer = f"**Non-Resident Tax Calculation:**\n"
            answer += f"Income: ${income:,.0f}\n"
            answer += f"Tax (22% flat): **${tax:,.0f}**\n"
            answer += f"Take-home: ${income - tax:,.0f}"
        else:
            # Resident calculation
            tax, breakdown = self._calculate_resident_tax(income)
            effective = (tax / income * 100) if income > 0 else 0
            
            answer = f"**Tax Calculation for ${income:,.0f}:**\n\n"
            answer += f"Tax Amount: **${tax:,.0f}**\n"
            answer += f"Effective Rate: **{effective:.2f}%**\n"
            answer += f"Take-Home: **${income - tax:,.0f}**\n"
            answer += f"Monthly Take-Home: ${(income - tax) / 12:,.0f}\n\n"
            
            if len(breakdown) <= 5:
                answer += "**Breakdown:**\n"
                for item in breakdown:
                    answer += f"- {item}\n"
        
        return {
            "agent": "CalculatorAgent",
            "answer": answer,
            "confidence": 1.0,
            "time": time.time() - start,
            "calculation": {"income": income, "tax": tax}
        }
    
    def _calculate_resident_tax(self, income: float) -> Tuple[float, List[str]]:
        """Calculate progressive tax."""
        brackets = [
            (20000, 0.00, "First $20,000 @ 0%"),
            (10000, 0.02, "Next $10,000 @ 2%"),
            (10000, 0.035, "Next $10,000 @ 3.5%"),
            (40000, 0.07, "Next $40,000 @ 7%"),
            (40000, 0.115, "Next $40,000 @ 11.5%"),
            (40000, 0.15, "Next $40,000 @ 15%"),
            (40000, 0.18, "Next $40,000 @ 18%"),
            (40000, 0.19, "Next $40,000 @ 19%"),
            (40000, 0.195, "Next $40,000 @ 19.5%"),
            (40000, 0.20, "Next $40,000 @ 20%"),
        ]
        
        tax = 0
        breakdown = []
        remaining = income
        
        for amount, rate, desc in brackets:
            if remaining <= 0:
                break
            taxable = min(remaining, amount)
            tax_amount = taxable * rate
            if tax_amount > 0 or rate == 0:
                breakdown.append(f"{desc} = ${tax_amount:,.0f}")
            tax += tax_amount
            remaining -= taxable
        
        # Above 320k
        if remaining > 0:
            tax_amount = remaining * 0.22
            tax += tax_amount
            breakdown.append(f"Above $320,000 @ 22% = ${tax_amount:,.0f}")
        
        return round(tax, 2), breakdown


# ============================================================================
# AGENT 3: DOCUMENT SEARCHER (Uses existing RAG)
# ============================================================================

class SearchAgent:
    """Agent for searching tax documents."""
    
    def __init__(self):
        # Reuse existing vector store
        try:
            from langchain_community.vectorstores import Chroma
            from langchain_openai import OpenAIEmbeddings
            
            db_path = "./data/chroma_db"
            if os.path.exists(db_path):
                embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAI_API_KEY"))
                self.db = Chroma(persist_directory=db_path, embedding_function=embeddings)
            else:
                self.db = None
        except:
            self.db = None
    
    def can_handle(self, query: str) -> bool:
        """Check if query needs document search."""
        q = query.lower()
        conceptual = ['how', 'why', 'explain', 'what is', 'procedure', 'process', 'qualify']
        return any(w in q for w in conceptual)
    
    def process(self, query: str) -> Dict:
        """Search documents for answer."""
        start = time.time()
        
        if not self.db:
            return {
                "agent": "SearchAgent",
                "answer": None,
                "confidence": 0.0,
                "error": "Database not available"
            }
        
        # Search
        docs = self.db.similarity_search(query, k=3)
        
        if docs:
            answer = "**From Singapore Tax Laws:**\n\n"
            for i, doc in enumerate(docs[:2], 1):
                content = doc.page_content[:300]
                answer += f"{content}...\n\n"
            
            sources = list(set([doc.metadata.get('source', 'Unknown') for doc in docs]))
            answer += f"*Sources: {', '.join(sources)}*"
            
            return {
                "agent": "SearchAgent",
                "answer": answer,
                "confidence": 0.8,
                "time": time.time() - start,
                "sources": sources
            }
        
        return {
            "agent": "SearchAgent",
            "answer": None,
            "confidence": 0.0
        }


# ============================================================================
# AGENT 4: SYNTHESIZER (Combines results from other agents)
# ============================================================================

class SynthesisAgent:
    """Agent that combines results from multiple agents."""
    
    def __init__(self):
        from langchain_openai import ChatOpenAI
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-3.5-turbo",  # Fast model for synthesis
            timeout=10
        )
    
    def synthesize(self, query: str, agent_results: List[Dict]) -> str:
        """Combine results from multiple agents."""
        
        # Filter successful results
        valid_results = [r for r in agent_results if r.get('answer') and r.get('confidence', 0) > 0.5]
        
        if not valid_results:
            return "I couldn't find specific information about that. Please try rephrasing your question."
        
        # If only one result, return it
        if len(valid_results) == 1:
            return valid_results[0]['answer']
        
        # Combine multiple results
        combined = f"**Comprehensive Answer:**\n\n"
        
        # Prioritize by confidence and agent type
        valid_results.sort(key=lambda x: (x.get('confidence', 0), x['agent'] == 'FactAgent'), reverse=True)
        
        for result in valid_results:
            if result['agent'] == 'FactAgent':
                combined += f"**Tax Facts:**\n{result['answer']}\n\n"
            elif result['agent'] == 'CalculatorAgent':
                combined += f"{result['answer']}\n\n"
            elif result['agent'] == 'SearchAgent':
                combined += f"**Additional Information:**\n{result['answer']}\n\n"
        
        return combined.strip()


# ============================================================================
# ORCHESTRATOR (Routes queries to agents)
# ============================================================================

class MultiAgentOrchestrator:
    """Main orchestrator following two-tier architecture."""
    
    def __init__(self):
        self.fact_agent = FactAgent()
        self.calc_agent = CalculatorAgent()
        self.search_agent = SearchAgent()
        self.synthesizer = SynthesisAgent()
    
    def answer_question(self, query: str) -> Tuple[str, Dict]:
        """Process query using appropriate agents."""
        
        start_time = time.time()
        
        # Determine which agents can handle this query
        agents_to_use = []
        
        if self.fact_agent.can_handle(query):
            agents_to_use.append(('fact', self.fact_agent))
        
        if self.calc_agent.can_handle(query):
            agents_to_use.append(('calc', self.calc_agent))
        
        if self.search_agent.can_handle(query):
            agents_to_use.append(('search', self.search_agent))
        
        # If no specific agent, use search
        if not agents_to_use:
            agents_to_use.append(('search', self.search_agent))
        
        # Execute agents in parallel (MapReduce pattern)
        results = []
        
        if len(agents_to_use) > 1:
            # Parallel execution
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {executor.submit(agent.process, query): name 
                          for name, agent in agents_to_use}
                
                for future in futures:
                    try:
                        result = future.result(timeout=5)
                        results.append(result)
                    except Exception as e:
                        print(f"Agent failed: {e}")
        else:
            # Single agent
            results.append(agents_to_use[0][1].process(query))
        
        # Synthesize results
        answer = self.synthesizer.synthesize(query, results)
        
        # Gather metadata
        metadata = {
            "agents_used": [r['agent'] for r in results if r.get('answer')],
            "total_time": time.time() - start_time,
            "agent_times": {r['agent']: r.get('time', 0) for r in results},
            "confidence": max([r.get('confidence', 0) for r in results]) if results else 0
        }
        
        return answer, metadata


# ============================================================================
# ENHANCED Q&A FUNCTION (Drop-in replacement)
# ============================================================================

def answer_question_with_agents(query: str) -> Tuple[str, List[str]]:
    """Enhanced Q&A using multi-agent system.
    
    This is a drop-in replacement for the original answer_question function.
    """
    orchestrator = MultiAgentOrchestrator()
    answer, metadata = orchestrator.answer_question(query)
    
    # Extract sources
    sources = []
    if 'FactAgent' in metadata.get('agents_used', []):
        sources.append('singapore_tax_facts.json')
    if 'SearchAgent' in metadata.get('agents_used', []):
        sources.extend(['Income Tax Act 1947.pdf', 'Goods and Services Tax Act 1993.pdf'])
    
    # Add performance info
    if metadata['total_time'] < 1:
        answer += f"\n\n*[Answered in {metadata['total_time']:.2f}s using {', '.join(metadata['agents_used'])}]*"
    
    return answer, sources


# ============================================================================
# TEST THE SYSTEM
# ============================================================================

def test_multi_agent():
    """Test the multi-agent system."""
    
    print("🤖 MULTI-AGENT SYSTEM TEST")
    print("=" * 60)
    
    test_queries = [
        "What are the current income tax rates?",
        "Calculate tax for someone earning $120,000",
        "What is the spouse relief amount?",
        "Explain how tax residency works in Singapore",
        "What is the highest marginal tax rate and at what income?",
        "Calculate tax for a non-resident earning $80,000"
    ]
    
    orchestrator = MultiAgentOrchestrator()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 50)
        
        answer, metadata = orchestrator.answer_question(query)
        
        print(answer[:500] + "..." if len(answer) > 500 else answer)
        print(f"\n📊 Metadata:")
        print(f"   Agents: {', '.join(metadata['agents_used'])}")
        print(f"   Time: {metadata['total_time']:.2f}s")
        print(f"   Confidence: {metadata['confidence']:.1%}")


if __name__ == "__main__":
    test_multi_agent()