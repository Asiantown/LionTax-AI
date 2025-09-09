#!/usr/bin/env python
"""Test Claude API connection."""

import os
from dotenv import load_dotenv
load_dotenv()

import anthropic

print("🧪 Testing Claude API")
print("=" * 50)

# Set API key
api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")
print(f"API Key preview: {api_key[:20]}..." if api_key else "No API key")

try:
    # Initialize client
    client = anthropic.Anthropic(api_key=api_key)
    print("\n✅ Client initialized")
    
    # Test simple question
    print("\n📝 Testing simple question...")
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        temperature=0,
        system="You are a Singapore tax expert. Answer concisely.",
        messages=[
            {"role": "user", "content": "What is the GST rate in Singapore?"}
        ]
    )
    
    print(f"✅ Response received: {response.content[0].text}")
    
    # Test another question
    print("\n📝 Testing another question...")
    response2 = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=200,
        temperature=0,
        system="You are a Singapore tax expert. Answer concisely.",
        messages=[
            {"role": "user", "content": "How do I appeal against my tax assessment?"}
        ]
    )
    
    print(f"✅ Response 2: {response2.content[0].text}")
    
    print("\n✅ Claude API is working properly!")
    
except anthropic.APIConnectionError as e:
    print(f"\n❌ Connection error: {e}")
except anthropic.RateLimitError as e:
    print(f"\n❌ Rate limit error: {e}")
except anthropic.APIStatusError as e:
    print(f"\n❌ API error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response}")
except Exception as e:
    print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")