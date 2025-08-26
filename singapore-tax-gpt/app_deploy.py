"""Singapore Tax GPT - Deployment Ready Version"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()
os.environ['ANONYMIZED_TELEMETRY'] = 'False'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

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
        letter-spacing: -0.02em;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1a202c;
        border-right: 1px solid #2d3748;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 0.5rem;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(16, 185, 129, 0.3);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #1a202c;
        color: #e2e8f0;
        border: 1px solid #2d3748;
        border-radius: 0.5rem;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: #1a202c;
        border: 1px solid #2d3748;
        border-radius: 0.5rem;
        color: #e2e8f0;
    }
    
    /* Success message */
    .element-container div[data-testid="stAlert"] > div[kind="success"] {
        background-color: rgba(16, 185, 129, 0.1);
        border: 1px solid #10b981;
    }
    
    /* Error message */
    .element-container div[data-testid="stAlert"] > div[kind="error"] {
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
    }
    
    /* Metrics */
    div[data-testid="metric-container"] {
        background-color: #1a202c;
        border: 1px solid #2d3748;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }
    
    div[data-testid="metric-container"] > div {
        color: #e2e8f0;
    }
    
    /* Custom hero section */
    .hero-section {
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
        padding: 3rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        border: 1px solid #4a5568;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #10b981 0%, #4ade80 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: #a0aec0;
        font-weight: 400;
    }
    
    /* Feature cards */
    .feature-card {
        background: #1a202c;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border: 1px solid #2d3748;
        margin-bottom: 1rem;
        transition: all 0.3s;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        border-color: #10b981;
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #f8fafc;
        margin-bottom: 0.5rem;
    }
    
    .feature-description {
        color: #a0aec0;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Check for OpenAI API key
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)

if not api_key:
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🏛️ Singapore Tax GPT</h1>
        <p class="hero-subtitle">AI-Powered Singapore Tax Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.error("⚠️ OpenAI API Key Required")
    st.info("""
    To use this application, you need to provide an OpenAI API key.
    
    **For deployment:**
    1. If using Streamlit Cloud: Add `OPENAI_API_KEY` in your app's Secrets settings
    2. If using Heroku/Railway: Set `OPENAI_API_KEY` as an environment variable
    3. If running locally: Create a `.env` file with `OPENAI_API_KEY=your-key-here`
    
    Get your API key from: https://platform.openai.com/api-keys
    """)
    st.stop()

# Import modules after API key check
try:
    from qa_working import answer_question
    from src.singapore.tax_calculator import SingaporeTaxCalculator
    from src.apis.stamp_duty_calculator import StampDutyCalculator
    qa_available = True
except Exception as e:
    qa_available = False
    st.warning(f"Q&A system initialization issue: {str(e)}")

# Hero Section
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">🏛️ Singapore Tax GPT</h1>
    <p class="hero-subtitle">AI-Powered Singapore Tax Assistant with RAG Technology</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("## 🎯 Select Function")
mode = st.sidebar.selectbox(
    "Choose your tool:",
    ["Q&A System", "Income Tax Calculator", "Stamp Duty Calculator", "About"]
)

# Main content
if mode == "Q&A System":
    st.markdown("## 💬 Ask Questions About Singapore Tax Laws")
    
    if not qa_available:
        st.error("Q&A system is not available. Please check the database initialization.")
    else:
        st.info("📚 Knowledge base includes 9 Singapore tax acts: Income Tax, GST, Stamp Duties, Property Tax, and more")
        
        question = st.text_input("Ask your tax question:", placeholder="e.g., What are the income tax rates for 2024?")
        
        if st.button("🔍 Get Answer", type="primary"):
            if question:
                with st.spinner("Searching through tax documents..."):
                    try:
                        answer, sources = answer_question(question)
                        
                        st.success("✅ Answer found!")
                        st.markdown(f"**Answer:** {answer}")
                        
                        if sources:
                            st.markdown("**Sources:**")
                            for source in sources:
                                st.markdown(f"- 📄 {source}")
                    except Exception as e:
                        st.error(f"Error processing question: {str(e)}")
            else:
                st.warning("Please enter a question")

elif mode == "Income Tax Calculator":
    st.markdown("## 💰 Income Tax Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        income = st.number_input("Annual Income (SGD)", min_value=0, value=80000, step=1000)
        age = st.number_input("Age", min_value=18, max_value=100, value=35)
        
    with col2:
        is_resident = st.checkbox("Tax Resident", value=True)
        st.markdown("### Reliefs")
        earned_income_relief = st.checkbox("Earned Income Relief", value=True)
        cpf_relief = st.checkbox("CPF Relief", value=True)
    
    if st.button("Calculate Tax", type="primary"):
        calc = SingaporeTaxCalculator()
        
        reliefs = {}
        if earned_income_relief:
            reliefs['earned_income'] = min(1000, income * 0.4) if age < 55 else min(6000, income * 0.4)
        if cpf_relief:
            reliefs['cpf'] = min(income * 0.2, 37740)
        
        result = calc.calculate_income_tax(income, reliefs, is_resident, age)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tax Payable", f"${result.tax_amount:,.2f}")
        with col2:
            st.metric("Effective Rate", f"{result.effective_rate:.2f}%")
        with col3:
            st.metric("Take Home", f"${income - result.tax_amount:,.2f}")
        
        if result.breakdown:
            st.markdown("### Tax Breakdown")
            for bracket in result.breakdown[:5]:
                if bracket['tax'] > 0:
                    st.text(f"{bracket['income_range']}: ${bracket['tax']:,.2f} ({bracket['rate']})")

elif mode == "Stamp Duty Calculator":
    st.markdown("## 🏠 Property Stamp Duty Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        price = st.number_input("Property Price (SGD)", min_value=0, value=1000000, step=10000)
        buyer_type = st.selectbox("Buyer Profile", 
            ["Singapore Citizen", "Permanent Resident", "Foreigner", "Company/Entity"])
    
    with col2:
        if buyer_type in ["Singapore Citizen", "Permanent Resident"]:
            num_properties = st.number_input("Properties Already Owned", min_value=0, max_value=5, value=0)
        else:
            num_properties = 0
    
    if st.button("Calculate Stamp Duty", type="primary"):
        calc = StampDutyCalculator()
        
        profiles = {
            "Singapore Citizen": "singapore_citizen",
            "Permanent Resident": "pr",
            "Foreigner": "foreigner",
            "Company/Entity": "entity"
        }
        
        result = calc.calculate_property_stamp_duty(
            price, profiles[buyer_type], num_properties
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("BSD", f"${result['buyer_stamp_duty']:,.2f}")
        with col2:
            st.metric("ABSD", f"${result['additional_buyer_stamp_duty']:,.2f}")
        with col3:
            st.metric("Total Stamp Duty", f"${result['total_stamp_duty']:,.2f}")
        
        total_cost = price + result['total_stamp_duty']
        st.info(f"💵 Total Cost (Property + Stamp Duty): ${total_cost:,.2f}")

else:  # About
    st.markdown("## 📖 About Singapore Tax GPT")
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <div class="feature-title">RAG-Powered Intelligence</div>
        <div class="feature-description">
            Uses Retrieval-Augmented Generation to search through official Singapore tax documents
            and provide accurate, context-aware answers.
        </div>
    </div>
    
    <div class="feature-card">
        <div class="feature-icon">📚</div>
        <div class="feature-title">Comprehensive Tax Database</div>
        <div class="feature-description">
            Indexed 9 major Singapore tax acts including Income Tax, GST, Stamp Duties, 
            Property Tax, and more - over 5,000 document chunks.
        </div>
    </div>
    
    <div class="feature-card">
        <div class="feature-icon">🧮</div>
        <div class="feature-title">Built-in Calculators</div>
        <div class="feature-description">
            Accurate tax calculators for income tax, property stamp duty, GST, and CPF
            based on latest IRAS rates and regulations.
        </div>
    </div>
    
    <div class="feature-card">
        <div class="feature-icon">🔒</div>
        <div class="feature-title">Privacy First</div>
        <div class="feature-description">
            All calculations are performed locally. Your financial data never leaves your device
            unless you explicitly ask a question to the AI.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("*Built with LangChain, OpenAI GPT-4, and ChromaDB*")