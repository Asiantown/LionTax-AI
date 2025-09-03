#!/usr/bin/env python
"""Multi-Agent System for Singapore Tax GPT.

Following best practices from UserJot and Langflow:
- Two-tier architecture (Primary + Subagents)
- Stateless subagents (pure functions)
- Structured communication protocols
- Parallel execution where possible
"""

import json
import re
import time
import asyncio
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# COMMUNICATION PROTOCOL (Following UserJot pattern)
# ============================================================================

class AgentStatus(Enum):
    """Status codes for agent responses."""
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"
    TIMEOUT = "timeout"

@dataclass
class AgentTask:
    """Structured task for subagents (stateless, pure function input)."""
    task_id: str
    objective: str
    context: Dict[str, Any]
    constraints: Dict[str, Any]
    output_format: str

@dataclass
class AgentResponse:
    """Structured response from subagents."""
    task_id: str
    status: AgentStatus
    result: Any
    confidence: float
    processing_time: float
    metadata: Dict[str, Any]
    recommendations: List[str]

# ============================================================================
# SPECIALIZED SUBAGENTS (Stateless, Pure Functions)
# ============================================================================

class TaxCalculatorAgent:
    """Agent specialized in tax calculations."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-3.5-turbo",  # Fast model for calculations
            timeout=5
        )
        # Load tax facts for calculations
        with open('singapore_tax_facts.json', 'r') as f:
            self.tax_facts = json.load(f)
    
    def process(self, task: AgentTask) -> AgentResponse:
        """Calculate tax based on income and parameters."""
        start_time = time.time()
        
        try:
            income = task.context.get('income', 0)
            is_resident = task.context.get('is_resident', True)
            
            if not is_resident:
                # Non-resident flat rate
                tax = income * 0.22
                result = {
                    "income": income,
                    "tax": tax,
                    "effective_rate": 22.0,
                    "take_home": income - tax,
                    "breakdown": [{"description": "Flat rate 22%", "amount": tax}]
                }
            else:
                # Resident progressive rates
                tax, breakdown = self._calculate_progressive_tax(income)
                effective_rate = (tax / income * 100) if income > 0 else 0
                
                result = {
                    "income": income,
                    "tax": round(tax, 2),
                    "effective_rate": round(effective_rate, 2),
                    "take_home": round(income - tax, 2),
                    "breakdown": breakdown
                }
            
            return AgentResponse(
                task_id=task.task_id,
                status=AgentStatus.COMPLETE,
                result=result,
                confidence=1.0,
                processing_time=time.time() - start_time,
                metadata={"model": "calculation", "is_resident": is_resident},
                recommendations=[]
            )
            
        except Exception as e:
            return AgentResponse(
                task_id=task.task_id,
                status=AgentStatus.FAILED,
                result=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)},
                recommendations=["Retry with valid income amount"]
            )
    
    def _calculate_progressive_tax(self, income: float) -> Tuple[float, List[Dict]]:
        """Calculate progressive tax for residents."""
        brackets = [
            (20000, 0.00),
            (10000, 0.02),
            (10000, 0.035),
            (40000, 0.07),
            (40000, 0.115),
            (40000, 0.15),
            (40000, 0.18),
            (40000, 0.19),
            (40000, 0.195),
            (40000, 0.20),
            (float('inf'), 0.22)
        ]
        
        tax = 0
        breakdown = []
        remaining = income
        cumulative = 0
        
        for bracket_amount, rate in brackets:
            if remaining <= 0:
                break
            
            taxable = min(remaining, bracket_amount)
            tax_amount = taxable * rate
            
            if tax_amount > 0 or (rate == 0 and taxable > 0):
                if cumulative == 0:
                    desc = f"First ${taxable:,.0f}"
                elif bracket_amount == float('inf'):
                    desc = f"Above ${cumulative:,.0f}"
                else:
                    desc = f"Next ${taxable:,.0f}"
                
                breakdown.append({
                    "description": f"{desc} @ {rate*100:.1f}%",
                    "amount": round(tax_amount, 2)
                })
            
            tax += tax_amount
            remaining -= taxable
            if bracket_amount != float('inf'):
                cumulative += bracket_amount
        
        return tax, breakdown


class ReliefCheckerAgent:
    """Agent specialized in checking relief eligibility."""
    
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", timeout=5)
        with open('singapore_tax_facts.json', 'r') as f:
            self.tax_facts = json.load(f)
    
    def process(self, task: AgentTask) -> AgentResponse:
        """Check eligibility for various tax reliefs."""
        start_time = time.time()
        
        try:
            taxpayer_info = task.context.get('taxpayer_info', {})
            eligible_reliefs = []
            total_relief = 0
            
            # Check each relief type
            reliefs = self.tax_facts.get('income_tax', {}).get('reliefs', {})
            
            # Earned Income Relief (automatic)
            eligible_reliefs.append({
                "type": "Earned Income Relief",
                "amount": 1000,
                "reason": "Automatic for all residents"
            })
            total_relief += 1000
            
            # Spouse Relief
            if taxpayer_info.get('has_spouse') and taxpayer_info.get('spouse_income', 0) <= 4000:
                eligible_reliefs.append({
                    "type": "Spouse Relief",
                    "amount": 2000,
                    "reason": "Spouse income ≤ $4,000"
                })
                total_relief += 2000
            
            # Child Relief
            num_children = taxpayer_info.get('num_children', 0)
            if num_children > 0:
                child_relief = num_children * 4000
                eligible_reliefs.append({
                    "type": "Child Relief",
                    "amount": child_relief,
                    "reason": f"{num_children} qualifying children × $4,000"
                })
                total_relief += child_relief
            
            # Parent Relief
            if taxpayer_info.get('supporting_parents'):
                parent_relief = 9000 * taxpayer_info.get('num_parents', 1)
                eligible_reliefs.append({
                    "type": "Parent Relief",
                    "amount": parent_relief,
                    "reason": "Supporting parents (age 55+, income ≤ $4,000)"
                })
                total_relief += parent_relief
            
            # CPF Relief (automatic for mandatory contributions)
            if taxpayer_info.get('has_cpf', True):
                eligible_reliefs.append({
                    "type": "CPF Relief",
                    "amount": "Automatic",
                    "reason": "Based on mandatory CPF contributions"
                })
            
            result = {
                "eligible_reliefs": eligible_reliefs,
                "total_relief_amount": total_relief,
                "recommendations": self._get_recommendations(taxpayer_info)
            }
            
            return AgentResponse(
                task_id=task.task_id,
                status=AgentStatus.COMPLETE,
                result=result,
                confidence=0.95,
                processing_time=time.time() - start_time,
                metadata={"reliefs_checked": len(eligible_reliefs)},
                recommendations=[]
            )
            
        except Exception as e:
            return AgentResponse(
                task_id=task.task_id,
                status=AgentStatus.FAILED,
                result=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)},
                recommendations=["Provide taxpayer information"]
            )
    
    def _get_recommendations(self, taxpayer_info: Dict) -> List[str]:
        """Get recommendations for maximizing reliefs."""
        recommendations = []
        
        if not taxpayer_info.get('has_srs'):
            recommendations.append("Consider SRS contributions (up to $15,300 relief)")
        
        if not taxpayer_info.get('has_insurance'):
            recommendations.append("Consider life insurance (up to $5,000 relief with CPF)")
        
        if taxpayer_info.get('has_elderly_parents') and not taxpayer_info.get('parent_relief_claimed'):
            recommendations.append("Claim Parent Relief if supporting parents")
        
        return recommendations


class DocumentSearchAgent:
    """Agent specialized in searching tax documents."""
    
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", timeout=10)
        # Initialize vector store if available
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
    
    def process(self, task: AgentTask) -> AgentResponse:
        """Search for relevant information in documents."""
        start_time = time.time()
        
        try:
            query = task.context.get('query', '')
            num_results = task.constraints.get('max_results', 3)
            
            if not self.db:
                return AgentResponse(
                    task_id=task.task_id,
                    status=AgentStatus.FAILED,
                    result=None,
                    confidence=0.0,
                    processing_time=time.time() - start_time,
                    metadata={"error": "Vector database not available"},
                    recommendations=["Initialize vector database"]
                )
            
            # Search documents
            docs = self.db.similarity_search(query, k=num_results)
            
            results = []
            for doc in docs:
                results.append({
                    "content": doc.page_content[:500],
                    "source": doc.metadata.get('source', 'Unknown'),
                    "relevance": 0.8  # Placeholder score
                })
            
            return AgentResponse(
                task_id=task.task_id,
                status=AgentStatus.COMPLETE,
                result={"documents": results, "query": query},
                confidence=0.85,
                processing_time=time.time() - start_time,
                metadata={"num_docs": len(results)},
                recommendations=[]
            )
            
        except Exception as e:
            return AgentResponse(
                task_id=task.task_id,
                status=AgentStatus.FAILED,
                result=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)},
                recommendations=["Check query format"]
            )


class TaxPlannerAgent:
    """Agent specialized in tax planning and optimization."""
    
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.3, model="gpt-4-turbo-preview", timeout=15)
    
    def process(self, task: AgentTask) -> AgentResponse:
        """Provide tax planning recommendations."""
        start_time = time.time()
        
        try:
            income = task.context.get('income', 0)
            current_reliefs = task.context.get('current_reliefs', 0)
            tax_info = task.context.get('tax_calculation', {})
            
            prompt = f"""As a Singapore tax planning expert, provide optimization strategies for:
            
Income: ${income:,.0f}
Current Tax: ${tax_info.get('tax', 0):,.0f}
Current Reliefs: ${current_reliefs:,.0f}

Provide 3-5 specific, actionable recommendations to reduce tax liability.
Format as JSON list with 'strategy', 'potential_savings', and 'requirements'."""
            
            response = self.llm.invoke(prompt)
            
            # Parse response
            try:
                strategies = json.loads(response.content)
            except:
                # Fallback strategies
                strategies = [
                    {
                        "strategy": "Maximize SRS contributions",
                        "potential_savings": "Up to $3,366 (15,300 × 22%)",
                        "requirements": "Open SRS account before year end"
                    },
                    {
                        "strategy": "Claim all eligible parent reliefs",
                        "potential_savings": "Up to $1,980 (9,000 × 22%)",
                        "requirements": "Parents age 55+, income < $4,000"
                    }
                ]
            
            return AgentResponse(
                task_id=task.task_id,
                status=AgentStatus.COMPLETE,
                result={"strategies": strategies},
                confidence=0.9,
                processing_time=time.time() - start_time,
                metadata={"model": "gpt-4"},
                recommendations=[]
            )
            
        except Exception as e:
            return AgentResponse(
                task_id=task.task_id,
                status=AgentStatus.FAILED,
                result=None,
                confidence=0.0,
                processing_time=time.time() - start_time,
                metadata={"error": str(e)},
                recommendations=[]
            )


# ============================================================================
# PRIMARY ORCHESTRATOR AGENT (Following Two-Tier Model)
# ============================================================================

class TaxOrchestratorAgent:
    """Primary agent that orchestrates subagents."""
    
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview")
        
        # Initialize subagents
        self.calculator = TaxCalculatorAgent()
        self.relief_checker = ReliefCheckerAgent()
        self.document_searcher = DocumentSearchAgent()
        self.tax_planner = TaxPlannerAgent()
        
        # Task ID counter
        self.task_counter = 0
    
    def process_query(self, query: str, context: Dict = None) -> Dict:
        """Process user query using appropriate subagents."""
        
        # Classify query intent
        intent = self._classify_intent(query)
        
        # Route to appropriate processing pattern
        if intent == "calculation":
            return self._handle_calculation(query, context)
        elif intent == "relief":
            return self._handle_relief_check(query, context)
        elif intent == "planning":
            return self._handle_tax_planning(query, context)
        elif intent == "information":
            return self._handle_information_search(query)
        else:
            return self._handle_complex_query(query, context)
    
    def _classify_intent(self, query: str) -> str:
        """Classify the user's intent."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['calculate', 'tax for', 'earning', 'income']):
            return "calculation"
        elif any(word in query_lower for word in ['relief', 'deduction', 'claim']):
            return "relief"
        elif any(word in query_lower for word in ['optimize', 'reduce', 'save', 'plan']):
            return "planning"
        elif any(word in query_lower for word in ['what is', 'explain', 'how does']):
            return "information"
        else:
            return "complex"
    
    def _handle_calculation(self, query: str, context: Dict = None) -> Dict:
        """Handle tax calculation queries."""
        
        # Extract income from query
        income_match = re.search(r'\$?([\d,]+)(?:k)?', query.lower())
        if income_match:
            income = float(income_match.group(1).replace(',', ''))
            if 'k' in query.lower():
                income *= 1000
        else:
            income = context.get('income', 0) if context else 0
        
        # Check if non-resident
        is_resident = 'non-resident' not in query.lower()
        
        # Create task for calculator
        task = AgentTask(
            task_id=f"calc_{self.task_counter}",
            objective="Calculate income tax",
            context={"income": income, "is_resident": is_resident},
            constraints={"timeout": 5},
            output_format="structured_json"
        )
        self.task_counter += 1
        
        # Execute calculation
        calc_response = self.calculator.process(task)
        
        if calc_response.status == AgentStatus.COMPLETE:
            result = calc_response.result
            
            # Check for reliefs if resident
            if is_resident and context:
                relief_task = AgentTask(
                    task_id=f"relief_{self.task_counter}",
                    objective="Check eligible reliefs",
                    context={"taxpayer_info": context},
                    constraints={"timeout": 5},
                    output_format="structured_json"
                )
                self.task_counter += 1
                
                relief_response = self.relief_checker.process(relief_task)
                
                if relief_response.status == AgentStatus.COMPLETE:
                    result['reliefs'] = relief_response.result
            
            return {
                "status": "success",
                "type": "calculation",
                "result": result,
                "execution_time": calc_response.processing_time
            }
        else:
            return {
                "status": "error",
                "message": "Failed to calculate tax",
                "details": calc_response.metadata
            }
    
    def _handle_relief_check(self, query: str, context: Dict = None) -> Dict:
        """Handle relief eligibility queries."""
        
        task = AgentTask(
            task_id=f"relief_{self.task_counter}",
            objective="Check tax relief eligibility",
            context={"taxpayer_info": context or {}},
            constraints={"timeout": 5},
            output_format="structured_json"
        )
        self.task_counter += 1
        
        response = self.relief_checker.process(task)
        
        if response.status == AgentStatus.COMPLETE:
            return {
                "status": "success",
                "type": "relief_check",
                "result": response.result,
                "execution_time": response.processing_time
            }
        else:
            return {
                "status": "error",
                "message": "Failed to check reliefs",
                "details": response.metadata
            }
    
    def _handle_tax_planning(self, query: str, context: Dict = None) -> Dict:
        """Handle tax planning queries using MapReduce pattern."""
        
        # Parallel execution: Calculate current tax AND check reliefs
        with ThreadPoolExecutor(max_workers=2) as executor:
            
            # Task 1: Calculate current tax
            calc_task = AgentTask(
                task_id=f"calc_{self.task_counter}",
                objective="Calculate current tax",
                context={"income": context.get('income', 100000), "is_resident": True},
                constraints={"timeout": 5},
                output_format="structured_json"
            )
            self.task_counter += 1
            
            # Task 2: Check current reliefs
            relief_task = AgentTask(
                task_id=f"relief_{self.task_counter}",
                objective="Check current reliefs",
                context={"taxpayer_info": context or {}},
                constraints={"timeout": 5},
                output_format="structured_json"
            )
            self.task_counter += 1
            
            # Execute in parallel
            future_calc = executor.submit(self.calculator.process, calc_task)
            future_relief = executor.submit(self.relief_checker.process, relief_task)
            
            calc_result = future_calc.result()
            relief_result = future_relief.result()
        
        # Task 3: Generate planning strategies based on results
        planner_context = {
            "income": context.get('income', 100000),
            "tax_calculation": calc_result.result if calc_result.status == AgentStatus.COMPLETE else {},
            "current_reliefs": relief_result.result.get('total_relief_amount', 0) if relief_result.status == AgentStatus.COMPLETE else 0
        }
        
        plan_task = AgentTask(
            task_id=f"plan_{self.task_counter}",
            objective="Generate tax optimization strategies",
            context=planner_context,
            constraints={"timeout": 15},
            output_format="structured_json"
        )
        self.task_counter += 1
        
        plan_response = self.tax_planner.process(plan_task)
        
        # Combine results
        if plan_response.status == AgentStatus.COMPLETE:
            return {
                "status": "success",
                "type": "tax_planning",
                "result": {
                    "current_tax": calc_result.result if calc_result.status == AgentStatus.COMPLETE else None,
                    "current_reliefs": relief_result.result if relief_result.status == AgentStatus.COMPLETE else None,
                    "optimization_strategies": plan_response.result
                },
                "execution_time": max(calc_result.processing_time, relief_result.processing_time) + plan_response.processing_time
            }
        else:
            return {
                "status": "partial",
                "message": "Generated basic planning",
                "result": {
                    "current_tax": calc_result.result if calc_result.status == AgentStatus.COMPLETE else None,
                    "current_reliefs": relief_result.result if relief_result.status == AgentStatus.COMPLETE else None
                }
            }
    
    def _handle_information_search(self, query: str) -> Dict:
        """Handle information search queries."""
        
        task = AgentTask(
            task_id=f"search_{self.task_counter}",
            objective="Search tax documents",
            context={"query": query},
            constraints={"max_results": 5, "timeout": 10},
            output_format="structured_json"
        )
        self.task_counter += 1
        
        response = self.document_searcher.process(task)
        
        if response.status == AgentStatus.COMPLETE:
            return {
                "status": "success",
                "type": "information",
                "result": response.result,
                "execution_time": response.processing_time
            }
        else:
            return {
                "status": "error",
                "message": "Search failed",
                "details": response.metadata
            }
    
    def _handle_complex_query(self, query: str, context: Dict = None) -> Dict:
        """Handle complex queries using multiple agents."""
        
        # For complex queries, use all agents and synthesize
        results = {}
        
        # Search for information
        search_result = self._handle_information_search(query)
        if search_result['status'] == 'success':
            results['information'] = search_result['result']
        
        # Check if calculation needed
        if re.search(r'\$?([\d,]+)', query):
            calc_result = self._handle_calculation(query, context)
            if calc_result['status'] == 'success':
                results['calculation'] = calc_result['result']
        
        # Check for reliefs if context provided
        if context:
            relief_result = self._handle_relief_check(query, context)
            if relief_result['status'] == 'success':
                results['reliefs'] = relief_result['result']
        
        return {
            "status": "success",
            "type": "complex",
            "result": results
        }


# ============================================================================
# MAIN INTERFACE
# ============================================================================

def answer_with_agents(question: str, user_context: Dict = None) -> Tuple[str, Dict]:
    """Main function to answer questions using multi-agent system."""
    
    orchestrator = TaxOrchestratorAgent()
    
    # Process query through multi-agent system
    result = orchestrator.process_query(question, user_context)
    
    # Format response based on result type
    if result['type'] == 'calculation':
        calc = result['result']
        answer = f"""**Tax Calculation Results:**
        
Income: S${calc['income']:,.0f}
Tax Amount: **S${calc['tax']:,.0f}**
Effective Rate: **{calc['effective_rate']:.2f}%**
Take-Home: **S${calc['take_home']:,.0f}**

**Tax Breakdown:**"""
        for item in calc.get('breakdown', []):
            answer += f"\n- {item['description']}: S${item['amount']:,.2f}"
        
        if 'reliefs' in calc:
            answer += "\n\n**Eligible Reliefs:**"
            for relief in calc['reliefs']['eligible_reliefs']:
                answer += f"\n- {relief['type']}: S${relief['amount']:,}" if isinstance(relief['amount'], (int, float)) else f"\n- {relief['type']}: {relief['amount']}"
    
    elif result['type'] == 'relief_check':
        reliefs = result['result']
        answer = "**Eligible Tax Reliefs:**\n"
        for relief in reliefs['eligible_reliefs']:
            answer += f"\n- {relief['type']}: S${relief['amount']:,}" if isinstance(relief['amount'], (int, float)) else f"\n- {relief['type']}: {relief['amount']}"
            answer += f" ({relief['reason']})"
        
        answer += f"\n\n**Total Relief Amount: S${reliefs['total_relief_amount']:,}**"
        
        if reliefs['recommendations']:
            answer += "\n\n**Recommendations:**"
            for rec in reliefs['recommendations']:
                answer += f"\n- {rec}"
    
    elif result['type'] == 'tax_planning':
        plan = result['result']
        answer = "**Tax Optimization Analysis:**\n"
        
        if plan.get('current_tax'):
            answer += f"\nCurrent Tax: S${plan['current_tax']['tax']:,.0f}"
        
        if plan.get('optimization_strategies'):
            answer += "\n\n**Optimization Strategies:**"
            for strategy in plan['optimization_strategies']['strategies']:
                answer += f"\n\n✓ {strategy['strategy']}"
                answer += f"\n  Potential Savings: {strategy['potential_savings']}"
                answer += f"\n  Requirements: {strategy['requirements']}"
    
    elif result['type'] == 'information':
        docs = result['result']['documents']
        answer = f"**Information about: {result['result']['query']}**\n\n"
        for i, doc in enumerate(docs, 1):
            answer += f"{i}. {doc['content'][:200]}...\n"
            answer += f"   Source: {doc['source']}\n\n"
    
    else:
        # Complex query with multiple results
        answer = "**Comprehensive Answer:**\n"
        
        if 'calculation' in result.get('result', {}):
            calc = result['result']['calculation']
            answer += f"\n**Tax: S${calc['tax']:,.0f}** (Effective rate: {calc['effective_rate']:.2f}%)"
        
        if 'reliefs' in result.get('result', {}):
            answer += f"\n**Eligible reliefs: S${result['result']['reliefs']['total_relief_amount']:,}**"
        
        if 'information' in result.get('result', {}):
            answer += "\n\n**Additional Information:**"
            for doc in result['result']['information']['documents'][:2]:
                answer += f"\n{doc['content'][:150]}..."
    
    return answer, result


# ============================================================================
# TEST THE SYSTEM
# ============================================================================

def test_multi_agent_system():
    """Test the multi-agent system with various queries."""
    
    print("🤖 MULTI-AGENT TAX SYSTEM TEST")
    print("=" * 60)
    
    test_cases = [
        {
            "query": "Calculate tax for someone earning $150,000",
            "context": None
        },
        {
            "query": "What reliefs can I claim?",
            "context": {
                "has_spouse": True,
                "spouse_income": 3000,
                "num_children": 2,
                "supporting_parents": True,
                "num_parents": 1
            }
        },
        {
            "query": "How can I optimize my tax for $200,000 income?",
            "context": {"income": 200000}
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Query: {test['query']}")
        print("-" * 40)
        
        answer, result = answer_with_agents(test['query'], test['context'])
        
        print(answer)
        print(f"\n[Execution Time: {result.get('execution_time', 0):.2f}s]")
        print(f"[Status: {result['status']}]")


if __name__ == "__main__":
    test_multi_agent_system()