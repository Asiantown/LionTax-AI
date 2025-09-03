#!/usr/bin/env python
"""Monitor Railway deployment until v2.2 is live."""

import time
import requests
import sys

url = "https://liontax-ai-production.up.railway.app"

print("Monitoring Railway deployment...")
print("Waiting for v2.2 to be deployed...")
print("="*50)

start_time = time.time()
max_wait = 300  # 5 minutes

while time.time() - start_time < max_wait:
    try:
        response = requests.get(url, timeout=10)
        
        # Check if v2.2 is in the response
        if "v2.2" in response.text:
            print("\n✅ Deployment successful! v2.2 is now live.")
            print(f"Deployment took {time.time() - start_time:.1f} seconds")
            
            # Quick test of formatting
            print("\nQuick formatting check:")
            if response.text.count('\n') > 100:
                print("✅ Line breaks appear to be working")
            else:
                print("⚠️ Line breaks might still be an issue")
            
            break
        else:
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(5)
            
    except requests.exceptions.RequestException as e:
        sys.stdout.write("x")
        sys.stdout.flush()
        time.sleep(5)
else:
    print("\n⚠️ Timeout waiting for deployment. Check Railway dashboard.")
    print("https://railway.app/dashboard")

print("\nTo test the live app:")
print(f"  Open: {url}")
print("  Ask: 'What are the current personal income tax rates for Singapore residents?'")
print("  Check: Tax rates should show on separate lines, not all on one line")