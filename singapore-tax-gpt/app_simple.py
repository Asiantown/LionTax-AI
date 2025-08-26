"""Simple Streamlit UI focused on Calculator Testing."""

import streamlit as st
import os
os.environ['ANONYMIZED_TELEMETRY'] = 'False'

from src.core.enhanced_rag import EnhancedRAGEngine

# Page config
st.set_page_config(
    page_title="Singapore Tax Calculator",
    page_icon="🧮",
    layout="wide"
)

# Initialize RAG engine
if 'rag_engine' not in st.session_state:
    with st.spinner("Loading..."):
        st.session_state.rag_engine = EnhancedRAGEngine()

st.title("🧮 Singapore Tax Calculator")
st.markdown("Test all tax calculators with sample queries")

# Create two columns
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📊 Quick Calculations")
    
    st.subheader("💰 Income Tax")
    if st.button("Calculate tax on $80,000", use_container_width=True):
        st.session_state.query = "Calculate income tax for $80,000"
    if st.button("Calculate tax on $120,000", use_container_width=True):
        st.session_state.query = "Calculate income tax for $120,000"
    if st.button("Calculate tax on $200,000", use_container_width=True):
        st.session_state.query = "Calculate income tax for $200,000"
    
    st.subheader("🏠 Stamp Duty")
    if st.button("$1M - Citizen 1st home", use_container_width=True):
        st.session_state.query = "Calculate stamp duty for $1,000,000 property as Singapore citizen first home"
    if st.button("$1.5M - Citizen 2nd home", use_container_width=True):
        st.session_state.query = "Calculate stamp duty for $1,500,000 property as Singapore citizen second property"
    if st.button("$2M - Foreigner", use_container_width=True):
        st.session_state.query = "Calculate stamp duty for foreigner buying $2,000,000 property"
    
    st.subheader("📈 Other Calculations")
    if st.button("CPF for $5,000 salary", use_container_width=True):
        st.session_state.query = "What's the CPF contribution for $5,000 monthly salary?"
    if st.button("Take home pay for $100k", use_container_width=True):
        st.session_state.query = "What's my take home pay if I earn $100,000 per year?"
    if st.button("Add GST to $1,000", use_container_width=True):
        st.session_state.query = "Add GST to $1,000"

with col2:
    st.header("💬 Ask Your Question")
    
    # Use session state query if available
    default_query = st.session_state.get('query', '')
    
    # Query input
    query = st.text_area(
        "Enter your tax question or click a button on the left:",
        value=default_query,
        height=100,
        placeholder="e.g., Calculate stamp duty for $1.5 million property"
    )
    
    # Submit button
    if st.button("🔍 Calculate", type="primary", use_container_width=True):
        if query:
            with st.spinner("Calculating..."):
                response = st.session_state.rag_engine.query_with_metadata(query)
                
                # Display response
                st.success("✅ Calculation Complete")
                
                # Show the answer in a nice box
                with st.container():
                    st.markdown("### 📋 Result:")
                    st.markdown(response['answer'])
                
                # Show metadata if calculation
                if response.get('metadata', {}).get('response_type') == 'calculation':
                    st.info("💡 This was calculated using the built-in tax calculator")
        else:
            st.warning("Please enter a question or click one of the calculator buttons")
    
    # Clear button
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.query = ""
        st.experimental_rerun()

# Examples section at bottom
st.markdown("---")
st.header("📚 Example Queries You Can Try")

example_cols = st.columns(3)

with example_cols[0]:
    st.markdown("""
    **Income Tax:**
    - Calculate tax for $50,000
    - Tax on $150,000 income
    - What's the tax rate for $80,000?
    - Income tax for $1 million
    """)

with example_cols[1]:
    st.markdown("""
    **Stamp Duty:**
    - Stamp duty for PR buying 2nd property worth $1M
    - ABSD for $3M property as citizen
    - Company buying $5M property
    - Foreigner buying $800k condo
    """)

with example_cols[2]:
    st.markdown("""
    **Other:**
    - CPF for $8,000 salary age 45
    - Property tax for $500,000 AV
    - Take home pay for $200,000
    - GST on $5,000 purchase
    """)