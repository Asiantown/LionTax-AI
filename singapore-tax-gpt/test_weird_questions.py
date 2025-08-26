"""Test the system with unusual and complex tax questions."""

import os
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from src.core.enhanced_rag import EnhancedRAGEngine
import time

def test_weird_questions():
    """Test with weird, complex, and edge-case questions."""
    print("="*70)
    print("🤔 TESTING WITH WEIRD & COMPLEX QUESTIONS")
    print("="*70)
    
    # Initialize engine
    print("\n🔧 Loading system...")
    engine = EnhancedRAGEngine()
    
    # Weird and complex questions
    weird_questions = [
        # Gambling + Property combo
        "If I win money at Marina Bay Sands casino and use it to buy a property, what taxes do I pay?",
        
        # Dead person taxes
        "Can a deceased person's estate claim tax deductions for donations made after death?",
        
        # Very specific scenario
        "What happens if I'm a non-resident who becomes resident halfway through the year and I have casino winnings?",
        
        # Cross-reference question
        "Do I pay GST on stamp duty fees?",
        
        # Weird timing question
        "If I buy a property at 11:59 PM on December 31st, which year's stamp duty rates apply?",
        
        # Casino + GST
        "Is there GST on casino entry levy?",
        
        # Multiple acts intersection
        "If a company owns a casino and rents out property above it, how many different taxes apply?",
        
        # Historical question
        "What was the estate duty rate in 2007 before it was abolished?",
        
        # Super specific deduction
        "Can I claim tax deduction for buying a guard dog for my rental property?",
        
        # Appraiser related
        "Who can legally value my property for tax purposes and what act governs this?",
        
        # Edge case on refunds
        "If I overpaid stamp duty because the property purchase fell through, how long do I have to claim a refund?",
        
        # Weird GST scenario
        "If I import goods worth exactly $400, do I pay GST?",
        
        # Casino employee question
        "Do casino dealers pay income tax on tips from gamblers?",
        
        # Mixed income source
        "I'm a Singapore PR working in Malaysia but I rent out property in Singapore. Which country taxes what?",
        
        # Penalty calculation
        "If I'm 3 years late filing taxes with $50,000 owed, what's my total penalty?",
    ]
    
    for i, question in enumerate(weird_questions, 1):
        print(f"\n{'='*70}")
        print(f"[{i}/15] 🤪 WEIRD QUESTION:")
        print(f"{question}")
        print("-" * 70)
        
        try:
            start = time.time()
            response = engine.query_with_metadata(question)
            elapsed = time.time() - start
            
            # Show answer
            answer = response['answer']
            
            # Truncate very long answers
            if len(answer) > 800:
                answer = answer[:800] + "\n... [truncated for display]"
            
            print(f"📝 Answer ({elapsed:.1f}s):")
            print(answer)
            
            # Check quality indicators
            citations = response.get('citations', [])
            if citations:
                print(f"\n✅ Found evidence in {len(citations)} source(s):")
                for cite in citations[:3]:
                    source = cite.get('source', 'Unknown')
                    # Clean up source name
                    if '.pdf' in source:
                        source = source.replace('.pdf', '')
                    print(f"  • {source}")
            else:
                print("\n⚠️  No specific citations found - answer may be general")
            
            # Check if it admitted uncertainty
            uncertain_phrases = ["cannot", "no information", "not found", "unclear", "not specified", "insufficient"]
            if any(phrase in answer.lower() for phrase in uncertain_phrases):
                print("📌 System appropriately indicated uncertainty")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(0.5)  # Brief pause between questions
    
    print("\n" + "="*70)
    print("✅ WEIRD QUESTION TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_weird_questions()