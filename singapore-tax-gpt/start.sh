#!/bin/bash
# Start script for Railway deployment
PORT=${PORT:-8501}
echo "Starting Streamlit on port $PORT"

# Create Streamlit config directory
mkdir -p ~/.streamlit

# Create config file with proper settings
echo "\
[server]\n\
port = $PORT\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
headless = true\n\
address = '0.0.0.0'\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
serverAddress = '0.0.0.0'\n\
serverPort = $PORT\n\
" > ~/.streamlit/config.toml

# Start Streamlit
python -m streamlit run app_main.py