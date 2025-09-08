#!/usr/bin/env python
"""Test Groq API with Qwen model."""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("❌ Please add GROQ_API_KEY to .env file")
    print("Get free key at: https://console.groq.com/")
    exit(1)

print(f"✅ Groq API Key found: {api_key[:15]}...")

# Test with requests (simpler than OpenAI client)
import requests
import json

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Test English
print("\n🧪 Testing Groq's Qwen-3-32B...")
print("-" * 40)

data = {
    "model": "qwen/qwen3-32b",
    "messages": [
        {"role": "user", "content": "What's the GST rate in Singapore? Answer in 1 line."}
    ],
    "temperature": 0
}

response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    result = response.json()
    print("✅ English: " + result['choices'][0]['message']['content'])
else:
    print(f"❌ Error: {response.text}")

# Test Chinese
data['messages'][0]['content'] = "新加坡的GST税率是多少？用一句话回答。"

response = requests.post(url, headers=headers, json=data)
if response.status_code == 200:
    result = response.json()
    print("✅ Chinese: " + result['choices'][0]['message']['content'])
    print("\n🚀 Groq API working! Super fast inference ready!")
else:
    print(f"❌ Error: {response.text}")

print("\nSpeed: ~400 tokens/second (10x faster than GPT-4!)")
print("Cost: $0.00029 per 1K input tokens (vs GPT-4 at $0.03)")