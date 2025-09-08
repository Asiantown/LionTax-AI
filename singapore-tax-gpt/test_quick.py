#!/usr/bin/env python
"""Quick test without database rebuild."""

import warnings
warnings.filterwarnings('ignore')

# Test imports work
try:
    from langchain_community.embeddings import FakeEmbeddings
    print("✅ FakeEmbeddings imports successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")

# Test Groq connection
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    temperature=0,
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.environ.get("GROQ_API_KEY"),
    model_name="qwen/qwen3-32b"
)

print("\n🧪 Testing Groq...")

# English test
response = llm.invoke("What is Singapore GST rate? Answer in 1 sentence.")
print(f"English: {response.content[:100]}...")

# Chinese test
response = llm.invoke("新加坡的GST税率是多少？用一句话回答。")
print(f"Chinese: {response.content[:100]}...")

print("\n✅ System working - no heavy dependencies needed!")