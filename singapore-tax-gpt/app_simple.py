"""Singapore Tax GPT - Ultra Simple Version"""

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

st.title("🏛️ Singapore Tax GPT")
st.subheader("AI-Powered Singapore Tax Assistant")

# Simple tax calculator
st.header("📊 Quick Income Tax Calculator")

income = st.number_input("Annual Income (SGD)", min_value=0, value=80000, step=1000)

if st.button("Calculate Tax"):
    # Singapore tax brackets for YA 2024
    if income <= 20000:
        tax = 0
    elif income <= 30000:
        tax = (income - 20000) * 0.02
    elif income <= 40000:
        tax = 200 + (income - 30000) * 0.035
    elif income <= 80000:
        tax = 550 + (income - 40000) * 0.07
    elif income <= 120000:
        tax = 3350 + (income - 80000) * 0.115
    elif income <= 160000:
        tax = 7950 + (income - 120000) * 0.15
    elif income <= 200000:
        tax = 13950 + (income - 160000) * 0.18
    elif income <= 240000:
        tax = 21150 + (income - 200000) * 0.19
    elif income <= 280000:
        tax = 28750 + (income - 240000) * 0.195
    elif income <= 320000:
        tax = 36550 + (income - 280000) * 0.20
    elif income <= 500000:
        tax = 44550 + (income - 320000) * 0.22
    elif income <= 1000000:
        tax = 84150 + (income - 500000) * 0.23
    else:
        tax = 199150 + (income - 1000000) * 0.24
    
    effective_rate = (tax / income * 100) if income > 0 else 0
    take_home = income - tax
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tax Payable", f"${tax:,.2f}")
    with col2:
        st.metric("Effective Rate", f"{effective_rate:.2f}%")
    with col3:
        st.metric("Take Home", f"${take_home:,.2f}")

st.markdown("---")

# Stamp duty calculator
st.header("🏠 Property Stamp Duty Calculator")

price = st.number_input("Property Price (SGD)", min_value=0, value=1000000, step=10000)
buyer_type = st.selectbox("Buyer Type", ["Singapore Citizen (1st)", "Singapore Citizen (2nd)", "PR (1st)", "Foreigner"])

if st.button("Calculate Stamp Duty"):
    # BSD calculation
    if price <= 180000:
        bsd = price * 0.01
    elif price <= 360000:
        bsd = 1800 + (price - 180000) * 0.02
    elif price <= 1000000:
        bsd = 5400 + (price - 360000) * 0.03
    elif price <= 1500000:
        bsd = 24600 + (price - 1000000) * 0.04
    elif price <= 3000000:
        bsd = 44600 + (price - 1500000) * 0.05
    else:
        bsd = 119600 + (price - 3000000) * 0.06
    
    # ABSD rates
    absd_rates = {
        "Singapore Citizen (1st)": 0,
        "Singapore Citizen (2nd)": 0.20,
        "PR (1st)": 0.05,
        "Foreigner": 0.60
    }
    
    absd = price * absd_rates.get(buyer_type, 0)
    total = bsd + absd
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("BSD", f"${bsd:,.2f}")
    with col2:
        st.metric("ABSD", f"${absd:,.2f}")
    with col3:
        st.metric("Total", f"${total:,.2f}")

st.markdown("---")
st.info("Note: This is a simplified calculator. For comprehensive tax advice, consult IRAS or a tax professional.")