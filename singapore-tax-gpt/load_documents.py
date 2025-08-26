"""Load the 5 IRAS documents into the RAG system."""

from src.core.basic_rag import BasicRAGEngine
import os
from glob import glob

def load_iras_documents():
    """Load all IRAS documents into the vector store."""
    print("Loading IRAS documents into RAG system...")
    
    # Initialize engine
    engine = BasicRAGEngine()
    
    # Find all documents in iras_docs folder
    doc_files = glob("./data/iras_docs/*.txt")
    
    if not doc_files:
        print("No documents found in ./data/iras_docs/")
        return
    
    total_chunks = 0
    
    # Load each document
    for doc_file in doc_files:
        print(f"\nProcessing: {os.path.basename(doc_file)}")
        chunks = engine.load_document(doc_file)
        engine.add_documents(chunks)
        total_chunks += len(chunks)
        print(f"  Added {len(chunks)} chunks")
    
    print(f"\n✅ Successfully loaded {len(doc_files)} documents ({total_chunks} total chunks)")
    
    # Test with a few queries
    print("\n" + "="*50)
    print("Testing loaded documents with sample queries:")
    print("="*50)
    
    test_queries = [
        "What is the GST rate?",
        "What are the property tax rates for owner-occupied homes?",
        "When is the e-filing deadline?",
        "What is the corporate tax rate?"
    ]
    
    for query in test_queries:
        print(f"\nQ: {query}")
        response = engine.query(query)
        print(f"A: {response['answer'][:200]}...")
        print(f"Sources: {[s['source'] for s in response['sources']]}")

if __name__ == "__main__":
    load_iras_documents()