#!/bin/bash
# Start script for Railway deployment
PORT=${PORT:-8501}
echo "Starting Streamlit on port $PORT"

# Create Streamlit config directory
mkdir -p ~/.streamlit

# Create config file with proper settings
cat > ~/.streamlit/config.toml << EOF
[server]
port = $PORT
enableCORS = false
enableXsrfProtection = false
headless = true
address = "0.0.0.0"

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"
serverPort = $PORT
EOF

# Start Streamlit
python -m streamlit run app_main.py