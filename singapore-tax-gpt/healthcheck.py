"""Simple health check endpoint for Railway"""

import streamlit as st

# Add a simple health check
if "health" in st.query_params:
    st.success("OK")
    st.stop()