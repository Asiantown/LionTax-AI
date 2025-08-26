"""Load all IRAS documents into the RAG system."""

import os
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from src.core.enhanced_rag import EnhancedRAGEngine
from pathlib import Path
import time

def load_all_documents():
    """Load all PDF documents into the vector store."""
    print("="*70)
    print("📚 LOADING ALL IRAS DOCUMENTS")
    print("="*70)
    
    # Initialize RAG engine
    print("\n🔧 Initializing RAG engine...")
    engine = EnhancedRAGEngine()
    
    # Get all PDF files
    pdf_dir = Path("./data/iras_docs")
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    print(f"\n📁 Found {len(pdf_files)} PDF documents:")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    
    # Process each document
    total_chunks = 0
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
        print("   ⏳ This may take a few minutes...")
        
        start_time = time.time()
        try:
            chunks = engine.add_pdf_document(str(pdf_file))
            elapsed = time.time() - start_time
            total_chunks += chunks
            
            print(f"   ✅ Added {chunks} chunks in {elapsed:.1f} seconds")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
    print(f"✅ DOCUMENT LOADING COMPLETE")
    print(f"   Total documents: {len(pdf_files)}")
    print(f"   Total chunks: {total_chunks}")
    print("="*70)
    
    return engine

def test_questions(engine):
    """Test the system with sample questions."""
    print("\n" + "="*70)
    print("🧪 TESTING Q&A SYSTEM")
    print("="*70)
    
    test_questions = [
        "What are the income tax rates for YA 2024?",
        "What is the deadline for filing income tax?",
        "What tax reliefs are available for parents?",
        "How is foreign income taxed in Singapore?",
        "What are the conditions for tax exemption?",
        "What is the penalty for late filing?",
        "How to claim spouse relief?",
        "What is the Section 13 deduction?",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n[{i}] Question: {question}")
        print("-" * 50)
        
        try:
            response = engine.query_with_metadata(question)
            
            # Show answer
            answer = response['answer']
            # Limit answer length for display
            if len(answer) > 500:
                answer = answer[:500] + "..."
            print(f"Answer: {answer}")
            
            # Show citations
            if response.get('citations'):
                print(f"\nSources ({len(response['citations'])} documents):")
                for citation in response['citations'][:2]:  # Show first 2 citations
                    print(f"  📄 {citation.get('source', 'Unknown')}")
                    if citation.get('section'):
                        print(f"     Section: {citation['section']}")
                    if citation.get('pages'):
                        print(f"     Pages: {citation['pages']}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "="*70)
    print("✅ TESTING COMPLETE")
    print("="*70)

if __name__ == "__main__":
    # Load all documents
    engine = load_all_documents()
    
    # Test with questions
    print("\n🔍 Ready to answer questions!")
    print("\nWould you like to:")
    print("1. Test with sample questions")
    print("2. Ask your own questions")
    print("3. Exit")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == "1":
        test_questions(engine)
    elif choice == "2":
        print("\n💬 Interactive Q&A Mode (type 'exit' to quit)")
        print("-" * 50)
        while True:
            question = input("\n❓ Your question: ").strip()
            if question.lower() in ['exit', 'quit', 'q']:
                break
            
            print("\n🔍 Searching...")
            response = engine.query_with_metadata(question)
            
            print("\n📝 Answer:")
            print(response['answer'])
            
            if response.get('citations'):
                print(f"\n📚 Sources: {len(response['citations'])} documents found")
    else:
        print("\n👋 Goodbye!")