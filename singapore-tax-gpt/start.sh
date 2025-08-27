#!/bin/bash
# Start script for Railway deployment
PORT=${PORT:-8501}
echo "Starting Streamlit on port $PORT"
streamlit run app_main.py --server.port=$PORT --server.address=0.0.0.0