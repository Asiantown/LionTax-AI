"""Singapore Tax GPT - Professional Dark Theme Interface"""

import streamlit as st
import os
import warnings
from dotenv import load_dotenv

# Suppress warnings before any imports that might trigger them
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*Blowfish.*')
warnings.filterwarnings('ignore', message='.*ARC4.*')

load_dotenv()

# Suppress telemetry and parallel processing warnings
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['CHROMA_TELEMETRY'] = 'false'
os.environ['CHROMA_CLIENT_TELEMETRY'] = 'false'
os.environ['CHROMA_SERVER_TELEMETRY'] = 'false'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

# Suppress ChromaDB telemetry errors
import logging
logging.getLogger('chromadb.telemetry').setLevel(logging.ERROR)
logging.getLogger('chromadb.telemetry.posthog').setLevel(logging.ERROR)

from qa_lite import answer_question  # Using lightweight version for deployment

# Page config
st.set_page_config(
    page_title="Singapore Tax GPT",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Dark Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Dark Theme */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #0f1419;
        color: #e2e8f0;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        background-color: #0f1419;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #f8fafc;
        font-weight: 600;
        line-height: 1.3;
    }
    
    h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #60a5fa 0%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Sidebar - Professional Dark */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #1a202c;
        border-right: 1px solid #2d3748;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #cbd5e0;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f7fafc;
        border-bottom: 1px solid #2d3748;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Sidebar sections */
    [data-testid="stSidebar"] .element-container {
        background-color: #1a202c;
    }
    
    /* Chat-style message containers */
    .chat-message {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    .user-message {
        background-color: #1e40af;
        border: 1px solid #3b82f6;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        margin-right: 2rem;
    }
    
    /* Buttons - Professional styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
        transform: translateY(-1px);
    }
    
    /* Primary button for main actions */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        box-shadow: 0 2px 4px rgba(5, 150, 105, 0.2);
        font-size: 1.1rem;
        padding: 1rem 2rem;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 4px 8px rgba(5, 150, 105, 0.3);
    }
    
    /* Input fields - Dark theme */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
        padding: 0.75rem !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }
    
    /* Text area - Chat input styling */
    .stTextArea textarea {
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
        padding: 1rem !important;
        resize: vertical !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #1e293b;
        border: 1px solid #475569;
        border-radius: 8px;
        color: #f8fafc;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Metrics - Professional cards */
    [data-testid="metric-container"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
    }
    
    [data-testid="metric-container"]:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.2);
    }
    
    [data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #064e3b;
        border: 1px solid #059669;
        border-radius: 8px;
        color: #6ee7b7;
    }
    
    .stError {
        background-color: #7f1d1d;
        border: 1px solid #dc2626;
        border-radius: 8px;
        color: #fca5a5;
    }
    
    .stWarning {
        background-color: #78350f;
        border: 1px solid #d97706;
        border-radius: 8px;
        color: #fcd34d;
    }
    
    .stInfo {
        background-color: #1e3a8a;
        border: 1px solid #3b82f6;
        border-radius: 8px;
        color: #93c5fd;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        color: #f8fafc;
        font-weight: 500;
    }
    
    .streamlit-expanderContent {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-top: none;
        border-radius: 0 0 8px 8px;
    }
    
    /* Loading spinner */
    .stSpinner {
        color: #3b82f6;
    }
    
    /* Professional section dividers */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #334155, transparent);
        margin: 2rem 0;
    }
    
    /* Custom professional badge */
    .pro-badge {
        background: linear-gradient(135deg, #1e40af 0%, #059669 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Tax category pills */
    .tax-pill {
        background-color: #1e293b;
        border: 1px solid #3b82f6;
        color: #60a5fa;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem;
        display: inline-block;
    }
    
    /* Response formatting */
    .response-container {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        line-height: 1.6;
    }
    
    /* Quick action buttons */
    .quick-action {
        background-color: #1e293b;
        border: 1px solid #475569;
        border-radius: 8px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        color: #cbd5e0;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .quick-action:hover {
        border-color: #3b82f6;
        background-color: #1e40af;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    # Calculators removed - using Groq for all calculations

# Professional sidebar
with st.sidebar:
    st.markdown('<span class="pro-badge">Professional</span>', unsafe_allow_html=True)
    st.title("Singapore Tax GPT")
    
    st.subheader("Tax Categories")
    categories = [
        "Income Tax", "Corporate Tax", "GST", "Stamp Duty", 
        "Property Tax", "Withholding Tax", "Tax Reliefs"
    ]
    
    for category in categories:
        if st.button(category):
            st.session_state.selected_category = category
    
    st.markdown("---")
    
    st.subheader("Quick Tools")
    st.button("Income Tax Calculator")
    st.button("Stamp Duty Calculator")
    st.button("GST Calculator")
    st.button("CPF Calculator")
    
    st.markdown("---")
    
    st.subheader("System Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Documents", "9")
    with col2:
        st.metric("Status", "Online")

# Main interface
st.title("Singapore Tax GPT")
st.markdown("*Professional AI tax assistant powered by official IRAS regulations*")
st.warning("⚠️ **Tax rates current as of December 2024.** Tax regulations change annually. Please verify critical information with [IRAS](https://www.iras.gov.sg) directly.")

# Quick action pills
st.markdown("**Popular Topics:**")
quick_topics = [
    "What are the current income tax rates?",
    "How to calculate GST?", 
    "Stamp duty for property purchase",
    "Corporate tax obligations",
    "Tax filing deadlines 2024"
]

cols = st.columns(3)
for i, topic in enumerate(quick_topics):
    with cols[i % 3]:
        if st.button(topic, key=f"topic_{i}"):
            st.session_state.question = topic

# Main chat interface
st.subheader("Ask Your Tax Question")

# Question input with professional styling
question = st.text_area(
    "Your Question",
    placeholder="Ask about Singapore taxes, regulations, calculations, or compliance requirements...",
    height=100,
    key="main_question",
    value=st.session_state.get('question', ''),
    label_visibility="hidden"
)

# Action buttons
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    submit_btn = st.button("Get Professional Answer", type="primary", key="submit")
with col2:
    st.button("Clear", key="clear")
with col3:
    show_sources = st.checkbox("Show Sources")

# Process question
if submit_btn and question:
    with st.spinner("Analyzing tax regulations..."):
        try:
            answer, sources = answer_question(question)
            
            # Display response in professional format
            st.markdown("### Professional Tax Guidance")
            # Convert newlines to HTML breaks for proper formatting
            formatted_answer = answer.replace('\n', '<br>')
            st.markdown(f"""
            <div class="response-container">
                {formatted_answer}
            </div>
            """, unsafe_allow_html=True)
            
            # Show sources if requested
            if show_sources and sources:
                st.subheader("Official Sources")
                for i, source in enumerate(sources, 1):
                    st.markdown(f"**{i}.** {source}")
                    
        except Exception as e:
            st.error(f"Unable to process request: {str(e)}")
            st.info("Please try rephrasing your question or contact support.")

elif submit_btn:
    st.warning("Please enter a tax question to get started")

# Professional calculators section
st.markdown("---")
st.subheader("Professional Tax Calculators")

tab1, tab2 = st.tabs(["Income Tax Calculator", "Stamp Duty Calculator"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Calculate Income Tax**")
        income = st.number_input(
            "Annual Income (SGD)", 
            min_value=0, 
            value=100000, 
            step=1000,
            key="income_calc"
        )
        
        is_resident = st.selectbox(
            "Tax Residency", 
            ["Singapore Tax Resident", "Non-Resident"],
            key="residency"
        )
        
        if st.button("Calculate Tax", key="calc_income"):
            result = st.session_state.tax_calc.calculate_income_tax(
                income, 
                is_resident=(is_resident == "Singapore Tax Resident")
            )
            st.session_state.tax_result = result
    
    with col2:
        if 'tax_result' in st.session_state:
            result = st.session_state.tax_result
            
            st.metric("Tax Payable", f"${result.tax_amount:,.0f}")
            st.metric("Effective Rate", f"{result.effective_rate:.2f}%")
            st.metric("Take Home", f"${income - result.tax_amount:,.0f}")

with tab2:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Calculate Stamp Duty**")
        price = st.number_input(
            "Property Price (SGD)", 
            min_value=0, 
            value=1000000, 
            step=10000,
            key="property_price"
        )
        
        buyer_type = st.selectbox(
            "Buyer Profile",
            ["Singapore Citizen", "Permanent Resident", "Foreigner", "Company"],
            key="buyer_profile"
        )
        
        if st.button("Calculate Stamp Duty", key="calc_stamp"):
            buyer_map = {
                "Singapore Citizen": "singapore_citizen",
                "Permanent Resident": "pr", 
                "Foreigner": "foreigner",
                "Company": "entity"
            }
            
            result = st.session_state.stamp_calc.calculate_property_stamp_duty(
                price, 
                buyer_map[buyer_type]
            )
            st.session_state.stamp_result = result
    
    with col2:
        if 'stamp_result' in st.session_state:
            result = st.session_state.stamp_result
            
            st.metric("Buyer's Stamp Duty", f"${result['buyer_stamp_duty']:,.0f}")
            st.metric("Additional BSD", f"${result['additional_buyer_stamp_duty']:,.0f}")
            st.metric("Total Stamp Duty", f"${result['total_stamp_duty']:,.0f}")

# Professional footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 0.9rem;">
    <strong>Singapore Tax GPT</strong> - Professional AI Tax Assistant<br>
    Powered by official IRAS regulations and tax law databases<br>
    <em>For official guidance, always consult IRAS or qualified tax professionals</em>
</div>
""", unsafe_allow_html=True)