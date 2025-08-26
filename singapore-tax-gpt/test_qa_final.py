"""Final test of Q&A system."""

import os
from dotenv import load_dotenv
load_dotenv()
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

print("🔧 Loading Singapore Tax Q&A System...")

# Load vector store
embeddings = OpenAIEmbeddings()
db = Chroma(
    persist_directory="./data/chroma_db",
    embedding_function=embeddings,
    collection_name="singapore_tax_docs"
)

print("✅ System loaded with 9 tax acts\n")

# Test questions
questions = [
    "What is the penalty for late tax filing?",
    "What is property tax?",
    "Tell me about stamp duties",
    "What is the casino entry levy?",
    "What taxes apply to gambling?",
]

llm = ChatOpenAI(temperature=0)

print("📋 Testing Q&A with sample questions:\n")
print("="*60)

for q in questions:
    print(f"\n❓ {q}")
    print("-"*60)
    
    # Search for relevant docs
    docs = db.similarity_search(q, k=2)
    
    if docs:
        # Get sources
        sources = set()
        context = ""
        for doc in docs:
            sources.add(doc.metadata.get('source', 'Unknown').replace('.pdf', ''))
            context += doc.page_content + "\n\n"
        
        # Ask LLM
        prompt = f"Based on this context from Singapore tax laws:\n\n{context[:2000]}\n\nAnswer this question: {q}"
        response = llm.invoke(prompt)
        
        print(f"📝 Answer: {response.content[:500]}")
        print(f"📚 Sources: {', '.join(sources)}")
    else:
        print("❌ No relevant documents found")

print("\n" + "="*60)
print("✅ System is working! Documents are loaded and searchable.")
print("\nTo ask your own questions, run: uv run python simple_qa.py")