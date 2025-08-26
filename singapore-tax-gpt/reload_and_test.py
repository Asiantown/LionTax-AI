"""Reload all documents and test Q&A."""

import os
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from src.core.enhanced_rag import EnhancedRAGEngine
from pathlib import Path

print("🔧 Initializing system...")
engine = EnhancedRAGEngine()

# Force reload all PDFs
pdf_dir = Path("./data/iras_docs")
pdf_files = list(pdf_dir.glob("*.pdf"))

print(f"\n📚 Loading {len(pdf_files)} documents...")

for pdf in pdf_files[:3]:  # Load first 3 for testing
    print(f"  Loading: {pdf.name}")
    try:
        engine.add_pdf_document(str(pdf))
    except Exception as e:
        print(f"  Error: {e}")

print("\n✅ Documents loaded!")

# Test questions
test_questions = [
    "What taxes are there in Singapore?",
    "Tell me about property tax",
    "What is stamp duty?",
    "Income tax rates",
    "GST information"
]

print("\n🧪 Testing Q&A:\n")

for q in test_questions:
    print(f"Q: {q}")
    try:
        response = engine.query_with_metadata(q)
        answer = response['answer'][:300] + "..." if len(response['answer']) > 300 else response['answer']
        print(f"A: {answer}")
        
        if response.get('citations'):
            sources = set(c.get('source', '').replace('.pdf', '') for c in response['citations'])
            if sources:
                print(f"   Sources: {', '.join(list(sources)[:3])}")
    except Exception as e:
        print(f"Error: {e}")
    print()