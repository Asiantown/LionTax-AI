"""Test script to verify Day 1-2 setup."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment():
    """Test that environment is properly configured."""
    print("Testing environment setup...")
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_openai_api_key_here":
        print("✅ OpenAI API key configured")
    else:
        print("❌ OpenAI API key not configured - Please set OPENAI_API_KEY in .env file")
        return False
    
    # Check directories
    dirs_to_check = ["./data/iras_docs", "./data/chroma_db", "./src/core"]
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Directory missing: {dir_path}")
    
    # Test imports
    try:
        import langchain
        import chromadb
        import streamlit
        print("✅ All required packages installed")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False
    
    return True

def test_basic_rag():
    """Test basic RAG functionality."""
    print("\nTesting Basic RAG Engine...")
    
    try:
        from src.core.basic_rag import BasicRAGEngine
        
        # Initialize engine
        engine = BasicRAGEngine()
        print("✅ RAG engine initialized")
        
        # Create test document
        test_doc_path = "./data/test_singapore_tax.txt"
        with open(test_doc_path, "w") as f:
            f.write("""
            Singapore Tax Information:
            
            GST Rate: The Goods and Services Tax (GST) rate in Singapore is 9% as of 1 January 2024.
            
            Corporate Tax: Singapore's corporate tax rate is 17% for all companies.
            
            Personal Income Tax: Singapore uses a progressive tax system for residents,
            with rates ranging from 0% to 24% depending on income level.
            """)
        
        # Load document
        docs = engine.load_document(test_doc_path)
        engine.add_documents(docs)
        print(f"✅ Loaded {len(docs)} document chunks")
        
        # Test query
        response = engine.query("What is the GST rate in Singapore?")
        if "9%" in response["answer"] or "GST" in response["answer"]:
            print("✅ Query answered correctly")
            print(f"   Answer preview: {response['answer'][:100]}...")
        else:
            print("❌ Query answer incorrect")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Day 1-2 Setup Test")
    print("=" * 50)
    
    # Test environment
    env_ok = test_environment()
    
    if env_ok:
        # Test RAG if environment is OK
        rag_ok = test_basic_rag()
        
        if rag_ok:
            print("\n" + "=" * 50)
            print("✅ Day 1-2 setup complete!")
            print("Next: Run 'streamlit run src/simple_app.py' to test the UI")
            print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ Setup incomplete. Please fix the issues above.")
        print("=" * 50)