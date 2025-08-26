"""Rebuild the vector database properly."""

import os
import shutil
from dotenv import load_dotenv

load_dotenv()
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import chromadb
from chromadb.config import Settings

def rebuild_database():
    print("🔧 Rebuilding Vector Database")
    print("="*60)
    
    # Clear old database
    db_path = "./data/chroma_db"
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    os.makedirs(db_path, exist_ok=True)
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings()
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", "! ", "? ", ", ", " ", ""]
    )
    
    # Get all PDFs
    pdf_dir = Path("./data/iras_docs")
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")
    
    all_documents = []
    
    # Process each PDF
    for pdf_file in pdf_files:
        print(f"\n📄 Processing: {pdf_file.name}")
        try:
            # Load PDF
            loader = PyPDFLoader(str(pdf_file))
            pages = loader.load()
            print(f"   Loaded {len(pages)} pages")
            
            # Split into chunks
            chunks = text_splitter.split_documents(pages)
            
            # Add source metadata
            for chunk in chunks:
                chunk.metadata['source'] = pdf_file.name
            
            all_documents.extend(chunks)
            print(f"   Created {len(chunks)} chunks")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Total documents to index: {len(all_documents)}")
    
    # Create vector store with all documents at once
    print("\n🔄 Creating vector store (this may take a few minutes)...")
    
    vectorstore = Chroma.from_documents(
        documents=all_documents,
        embedding=embeddings,
        persist_directory=db_path,
        collection_name="singapore_tax_docs"
    )
    
    # Force persist
    vectorstore.persist()
    
    print("✅ Database created and persisted!")
    
    # Test the database
    print("\n🧪 Testing database...")
    test_queries = [
        "stamp duty",
        "GST rate",
        "income tax",
        "property tax"
    ]
    
    for query in test_queries:
        results = vectorstore.similarity_search(query, k=1)
        if results:
            source = results[0].metadata.get('source', 'Unknown')
            print(f"   ✓ '{query}' → Found in {source}")
        else:
            print(f"   ✗ '{query}' → No results")
    
    print("\n✅ Database rebuild complete!")
    return vectorstore

if __name__ == "__main__":
    rebuild_database()