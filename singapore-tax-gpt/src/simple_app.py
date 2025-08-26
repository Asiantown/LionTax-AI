"""Simple Streamlit UI for Day 1-2 MVP."""

import streamlit as st
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.basic_rag import BasicRAGEngine

st.set_page_config(
    page_title="Singapore Tax Assistant (MVP)",
    page_icon="🇸🇬",
    layout="centered"
)

st.title("🇸🇬 Singapore Tax Assistant - MVP")
st.caption("Day 1-2: Basic RAG Implementation")

# Initialize RAG engine
@st.cache_resource
def init_rag():
    return BasicRAGEngine()

# Disclaimer
st.info("⚠️ This is a test MVP. Not for production use.")

# Query input
question = st.text_input("Ask a tax question:", placeholder="e.g., What is the tax rate for residents?")

if st.button("Get Answer"):
    if question:
        with st.spinner("Searching..."):
            try:
                engine = init_rag()
                response = engine.query(question)
                
                # Display answer
                st.markdown("### Answer")
                st.write(response["answer"])
                
                # Display sources
                if response["sources"]:
                    st.markdown("### Sources")
                    for source in response["sources"]:
                        st.caption(f"📄 {source['source']}")
                        
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("Please enter a question.")

# Sidebar info
with st.sidebar:
    st.header("MVP Status")
    st.success("✅ Basic RAG engine")
    st.success("✅ ChromaDB vector store")
    st.success("✅ Document loading")
    st.success("✅ Simple Q&A")
    st.info("⏳ Next: Document processing pipeline")