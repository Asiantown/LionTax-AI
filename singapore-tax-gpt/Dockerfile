# Backup Dockerfile if nixpacks doesn't work
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust for tiktoken
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Run streamlit
CMD ["streamlit", "run", "app_main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]