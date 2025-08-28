#!/usr/bin/env python
"""Working Q&A system for Singapore Tax documents."""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

print("🇸🇬 Singapore Tax Q&A System")
print("="*50)
print("Loading 9 tax acts...")

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from pathlib import Path

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

# Create QA chain
llm = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview")

def answer_question(question):
    """Answer a question using the documents."""
    # Search for relevant chunks
    docs = db.similarity_search(question, k=3)
    
    if not docs:
        return "No relevant information found in the documents.", []
    
    # Build context
    context = "\n\n".join([doc.page_content for doc in docs])
    sources = list(set([doc.metadata.get('source', 'Unknown') for doc in docs]))
    
    # Create prompt
    prompt = f"""You are a Singapore tax expert. Answer the question based ONLY on the context below.

Context from Singapore tax laws:
{context[:3000]}

Question: {question}

Answer (be specific and cite the document if possible):"""
    
    # Get answer
    response = llm.invoke(prompt)
    
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
        # Interactive mode
        print("Ask any question about Singapore taxes (type 'exit' to quit)\n")
        
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