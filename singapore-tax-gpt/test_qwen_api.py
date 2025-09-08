#!/usr/bin/env python
"""Quick test to verify Qwen API works."""

import os
from dotenv import load_dotenv

load_dotenv()

# Check if API key exists
api_key = os.environ.get("DASHSCOPE_API_KEY")
if not api_key:
    print("❌ ERROR: DASHSCOPE_API_KEY not found in .env file")
    print("Please add: DASHSCOPE_API_KEY=sk-xxxxx to your .env file")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...")

try:
    import dashscope
    dashscope.api_key = api_key
    from dashscope import Generation
    
    print("\n🧪 Testing Qwen API...")
    
    # Test English
    print("\n1. English Test:")
    response = Generation.call(
        model='qwen-turbo',
        prompt='What is 2+2?'
    )
    print(f"   Response: {response.output.text}")
    
    # Test Chinese  
    print("\n2. Chinese Test:")
    response = Generation.call(
        model='qwen-turbo',
        prompt='新加坡的首都是什么？'
    )
    print(f"   Response: {response.output.text}")
    
    print("\n✅ Qwen API is working!")
    
except ImportError:
    print("❌ dashscope not installed. Run: pip install dashscope")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check your API key is correct")
    print("2. Make sure you have internet connection")
    print("3. Try: pip install --upgrade dashscope")