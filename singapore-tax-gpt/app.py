"""Singapore Tax GPT - Streamlit Cloud Deployment Version"""

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Page config
st.set_page_config(
    page_title="Singapore Tax GPT",
    page_icon="🏛️",
    layout="wide"
)

# CSS styling
st.markdown("""
<style>
    .main {background-color: #0f1419;}
    h1, h2, h3 {color: #f8fafc;}
    .stButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏛️ Singapore Tax GPT")
st.subheader("AI-Powered Singapore Tax Assistant")

# Check for API key
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)

if not api_key:
    st.error("⚠️ OpenAI API Key Required")
    st.info("""
    To use this application, add your OpenAI API key in the Streamlit Cloud Secrets:
    1. Go to your app settings
    2. Navigate to Secrets
    3. Add: `OPENAI_API_KEY = "your-api-key-here"`
    """)
    st.stop()

# Try to import modules
try:
    from src.singapore.tax_calculator import SingaporeTaxCalculator
    from src.apis.stamp_duty_calculator import StampDutyCalculator
    calculators_available = True
except:
    calculators_available = False
    
# Main interface
tab1, tab2, tab3 = st.tabs(["📊 Tax Calculator", "🏠 Stamp Duty", "📖 About"])

with tab1:
    if calculators_available:
        st.header("Income Tax Calculator")
        income = st.number_input("Annual Income (SGD)", min_value=0, value=80000, step=1000)
        
        if st.button("Calculate Tax"):
            calc = SingaporeTaxCalculator()
            result = calc.calculate_income_tax(income)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tax Payable", f"${result.tax_amount:,.2f}")
            with col2:
                st.metric("Effective Rate", f"{result.effective_rate:.2f}%")
            with col3:
                st.metric("Take Home", f"${income - result.tax_amount:,.2f}")
    else:
        st.info("Tax calculator is being initialized...")

with tab2:
    if calculators_available:
        st.header("Property Stamp Duty Calculator")
        price = st.number_input("Property Price (SGD)", min_value=0, value=1000000, step=10000)
        buyer_type = st.selectbox("Buyer Type", ["Singapore Citizen", "PR", "Foreigner", "Company"])
        
        if st.button("Calculate Stamp Duty"):
            calc = StampDutyCalculator()
            profiles = {
                "Singapore Citizen": "singapore_citizen",
                "PR": "pr", 
                "Foreigner": "foreigner",
                "Company": "entity"
            }
            result = calc.calculate_property_stamp_duty(price, profiles[buyer_type], 0)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("BSD", f"${result['buyer_stamp_duty']:,.2f}")
            with col2:
                st.metric("ABSD", f"${result['additional_buyer_stamp_duty']:,.2f}")
            with col3:
                st.metric("Total", f"${result['total_stamp_duty']:,.2f}")
    else:
        st.info("Stamp duty calculator is being initialized...")

with tab3:
    st.header("About Singapore Tax GPT")
    st.write("""
    This application provides:
    - **Income Tax Calculator**: Calculate your Singapore income tax
    - **Stamp Duty Calculator**: Calculate property stamp duties (BSD & ABSD)
    - **RAG-powered Q&A**: Ask questions about Singapore tax laws (requires database setup)
    
    Built with LangChain, OpenAI GPT-4, and ChromaDB.
    """)
    
    st.info("Note: The Q&A system requires the document database to be initialized.")