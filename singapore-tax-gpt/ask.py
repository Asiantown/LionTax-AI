#!/usr/bin/env python
"""Simple Q&A interface for Singapore Tax GPT."""

import os
import sys
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from src.core.enhanced_rag import EnhancedRAGEngine

def main():
    # Get question from command line or prompt
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        interactive = False
    else:
        print("="*60)
        print("🇸🇬 SINGAPORE TAX GPT - Q&A System")
        print("="*60)
        print("Type your question (or 'exit' to quit):")
        print()
        interactive = True
    
    # Initialize engine
    print("🔧 Loading system...\n")
    engine = EnhancedRAGEngine()
    
    if not interactive:
        # Single question mode
        print(f"❓ Question: {question}\n")
        print("🔍 Searching...\n")
        
        response = engine.query_with_metadata(question)
        
        print("📝 Answer:")
        print("-" * 50)
        print(response['answer'])
        
        if response.get('citations'):
            print(f"\n📚 Sources: Found in {len(response['citations'])} documents")
            for citation in response['citations'][:3]:
                print(f"  • {citation.get('source', 'Unknown')}", end="")
                if citation.get('pages'):
                    print(f" (Pages: {citation['pages'][:3]}...)" if len(citation['pages']) > 3 else f" (Pages: {citation['pages']})")
                else:
                    print()
    else:
        # Interactive mode
        print("💬 Ready! Ask any Singapore tax question.\n")
        
        while True:
            try:
                question = input("❓ Your question: ").strip()
                
                if question.lower() in ['exit', 'quit', 'q', 'bye']:
                    print("\n👋 Goodbye!")
                    break
                
                if not question:
                    continue
                
                print("\n🔍 Searching...\n")
                response = engine.query_with_metadata(question)
                
                print("📝 Answer:")
                print("-" * 50)
                print(response['answer'])
                print("-" * 50)
                
                if response.get('citations'):
                    print(f"\n📚 Sources: Found in {len(response['citations'])} documents")
                    for citation in response['citations'][:3]:
                        print(f"  • {citation.get('source', 'Unknown')}", end="")
                        if citation.get('pages'):
                            print(f" (Pages: {citation['pages'][:3]}...)" if len(citation['pages']) > 3 else f" (Pages: {citation['pages']})")
                        else:
                            print()
                
                print()  # Empty line before next question
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    main()