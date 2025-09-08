#!/usr/bin/env python
"""Simple test of Groq with tax questions."""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Setup Groq LLM
llm = ChatOpenAI(
    temperature=0,
    openai_api_base="https://api.groq.com/openai/v1",
    openai_api_key=os.environ.get("GROQ_API_KEY"),
    model_name="qwen/qwen3-32b"
)

print("🧪 Testing Groq Qwen for Tax Questions")
print("=" * 50)

# Test English
print("\n1. English Test:")
response = llm.invoke("What is the GST rate in Singapore? Answer briefly.")
print(f"Answer: {response.content}")

# Test Chinese
print("\n2. Chinese Test:")
response = llm.invoke("新加坡的个人所得税最高税率是多少？简短回答。")
print(f"Answer: {response.content}")

# Test calculation
print("\n3. Tax Calculation:")
response = llm.invoke("Calculate Singapore income tax for $80,000 annual income. Just give the tax amount.")
print(f"Answer: {response.content}")

print("\n✅ Groq is working! System ready for bilingual tax Q&A!")