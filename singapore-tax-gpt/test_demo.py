"""Demo test without requiring OpenAI API key."""

import os
import sys

def test_environment_setup():
    """Test basic environment setup."""
    print("=" * 50)
    print("Testing Basic Setup (No API Required)")
    print("=" * 50)
    
    # Check Python version
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check directories
    dirs = ["./data", "./src", "./tests"]
    for d in dirs:
        if os.path.exists(d):
            print(f"✅ Directory exists: {d}")
        else:
            os.makedirs(d, exist_ok=True)
            print(f"✅ Created directory: {d}")
    
    # Test imports
    try:
        import langchain
        print(f"✅ LangChain version: {langchain.__version__}")
    except ImportError:
        print("❌ LangChain not installed")
    
    try:
        import chromadb
        print(f"✅ ChromaDB installed")
    except ImportError:
        print("❌ ChromaDB not installed")
    
    try:
        import streamlit
        print(f"✅ Streamlit version: {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit not installed")
    
    try:
        import openai
        print(f"✅ OpenAI package installed")
    except ImportError:
        print("❌ OpenAI package not installed")
    
    # Create sample Singapore tax content
    sample_content = """
    SINGAPORE TAX QUICK REFERENCE (2024)
    =====================================
    
    1. INCOME TAX RATES (RESIDENTS)
    --------------------------------
    First $20,000: 0%
    Next $10,000: 2%
    Next $10,000: 3.5%
    Next $40,000: 7%
    Next $40,000: 11.5%
    Next $40,000: 15%
    Next $40,000: 18%
    Next $40,000: 19%
    Next $40,000: 19.5%
    Next $40,000: 20%
    Next $180,000: 22%
    Next $500,000: 23%
    Above $1,000,000: 24%
    
    2. GST RATE
    -----------
    Current GST rate: 9% (from 1 Jan 2024)
    
    3. IMPORTANT DEADLINES
    ----------------------
    Paper Filing: 15 April
    E-Filing: 18 April
    
    4. CORPORATE TAX
    ----------------
    Standard rate: 17%
    
    5. PROPERTY TAX (OWNER-OCCUPIED)
    ----------------------------------
    First $8,000: 0%
    Next $47,000: 4%
    Next $15,000: 6%
    Above $70,000: Progressive rates up to 16%
    """
    
    # Save sample content
    sample_file = "./data/sample_tax_info.txt"
    with open(sample_file, "w") as f:
        f.write(sample_content)
    print(f"✅ Created sample tax document: {sample_file}")
    
    print("\n" + "=" * 50)
    print("Setup Test Complete!")
    print("=" * 50)
    print("\nNext Steps:")
    print("1. Add your OpenAI API key to .env file")
    print("2. Run: uv run python test_setup.py")
    print("3. Launch UI: uv run streamlit run src/simple_app.py")
    
    return True

if __name__ == "__main__":
    test_environment_setup()