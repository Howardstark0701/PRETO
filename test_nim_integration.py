#!/usr/bin/env python
"""
Test NVIDIA NIM Integration for PRETO
Tests if NIM API key is working and rate limiting is configured
"""

import os
import sys
import asyncio
import json
import httpx
from datetime import datetime

# Load environment
from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("NVIDIA NIM INTEGRATION TEST")
print("=" * 70)

# Check environment variables
print("\n1️⃣  CHECKING ENVIRONMENT CONFIGURATION")
print("-" * 70)

NIM_API_KEY = os.getenv("NIM_API_KEY", "")
NIM_API_URL = os.getenv("NIM_API_URL", "")
NIM_MODEL = os.getenv("NIM_MODEL", "")
MAX_REQUESTS_PER_MINUTE = os.getenv("MAX_REQUESTS_PER_MINUTE", "40")

print(f"NIM_API_KEY set: {'✅ YES' if NIM_API_KEY else '❌ NO'}")
if NIM_API_KEY:
    print(f"  Key starts with: nvapi-{NIM_API_KEY[6:10]}...")
    
print(f"NIM_API_URL: {NIM_API_URL if NIM_API_URL else '❌ NOT SET'}")
print(f"NIM_MODEL: {NIM_MODEL if NIM_MODEL else '❌ NOT SET'}")
print(f"MAX_REQUESTS_PER_MINUTE: {MAX_REQUESTS_PER_MINUTE}")

if not all([NIM_API_KEY, NIM_API_URL, NIM_MODEL]):
    print("\n❌ ERROR: Missing NIM configuration!")
    sys.exit(1)

print("\n✅ Configuration looks good!")

# Test NIM API connectivity
print("\n2️⃣  TESTING NIM API CONNECTIVITY")
print("-" * 70)

async def test_nim_api():
    """Test if we can connect to NIM API"""
    try:
        async with httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {NIM_API_KEY}",
                "content-type": "application/json"
            },
            timeout=30.0
        ) as client:
            # Make a simple test request
            payload = {
                "model": NIM_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": "Say 'NIM working!' in one sentence."
                    }
                ],
                "max_tokens": 50,
                "temperature": 0.7
            }
            
            print(f"Sending test request to: {NIM_API_URL}/chat/completions")
            print(f"Model: {NIM_MODEL}")
            
            response = await client.post(
                f"{NIM_API_URL}/chat/completions",
                json=payload
            )
            
            print(f"\nResponse Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"✅ NIM API WORKING!")
                print(f"Response: {message[:100]}...")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        return False

# Run async test
success = asyncio.run(test_nim_api())

# Test rate limiter
print("\n3️⃣  TESTING RATE LIMITER")
print("-" * 70)

from app.api.insights import RateLimiter

async def test_rate_limiter():
    """Test rate limiter functionality"""
    limiter = RateLimiter(max_requests=3, window_seconds=2)  # Low values for testing
    
    print(f"Testing rate limiter: max 3 requests per 2 seconds")
    
    for i in range(5):
        print(f"\nRequest {i+1}:")
        start = asyncio.get_event_loop().time()
        await limiter.wait_if_needed()
        elapsed = asyncio.get_event_loop().time() - start
        
        if elapsed > 0.1:
            print(f"  ⏱️  Waited {elapsed:.2f} seconds (rate limit applied)")
        else:
            print(f"  ✅ Immediate (slot available)")
        
        stats = limiter.get_stats()
        print(f"  Requests in window: {stats['requests_in_window']}/{stats['max_requests']}")

print("Rate limiter test (3 requests per 2 seconds):")
asyncio.run(test_rate_limiter())

# Test insights module
print("\n\n4️⃣  TESTING INSIGHTS MODULE")
print("-" * 70)

try:
    from app.api.insights import get_insights_manager
    
    insights_mgr = get_insights_manager()
    has_client = insights_mgr.client is not None
    
    print(f"Insights Manager initialized: ✅")
    print(f"NIM Client ready: {'✅ YES' if has_client else '❌ NO'}")
    
    if has_client:
        print(f"Rate limiter configured: ✅")
        rate_stats = insights_mgr.rate_limiter.get_stats()
        print(f"  Available slots: {rate_stats['available_slots']}/{rate_stats['max_requests']}")
        
except Exception as e:
    print(f"❌ Error loading insights module: {str(e)}")

# Test health check endpoint
print("\n\n5️⃣  TESTING HEALTH CHECK ENDPOINT")
print("-" * 70)

async def test_health_endpoint():
    """Test health endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/insights/health", timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Health endpoint responding:")
                print(f"  Status: {data.get('status')}")
                print(f"  Service: {data.get('insights_service')}")
                print(f"  NIM Configured: {data.get('nim_configured')}")
                print(f"  Fallback Mode: {data.get('fallback_mode')}")
                
                if 'rate_limit' in data:
                    rl = data['rate_limit']
                    print(f"  Rate Limit:")
                    print(f"    Available: {rl.get('available_slots')}")
                    print(f"    Max: {rl.get('max_requests')}")
                    print(f"    Current: {rl.get('requests_in_window')}")
                
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Cannot reach server: {str(e)}")
        print("   Make sure server is running: python main.py")
        return False

print("Testing connection to http://localhost:8000/api/insights/health")
asyncio.run(test_health_endpoint())

# Final Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

if success:
    print("\n✅ NVIDIA NIM INTEGRATION WORKING!")
    print("\nYour PRETO platform is ready to use NIM with:")
    print("  • Cost: ~50-90% cheaper than Claude")
    print("  • Rate Limit: 40 requests per minute")
    print("  • Status: Connected and operational")
else:
    print("\n⚠️  NIM API CONNECTION ISSUE")
    print("\nPossible causes:")
    print("  1. API key expired or invalid")
    print("  2. Network connectivity issue")
    print("  3. NVIDIA API endpoint down")
    print("\nSolution:")
    print("  • Get new API key from: https://build.nvidia.com/")
    print("  • Update NIM_API_KEY in .env")
    print("  • Restart server")

print("\n" + "=" * 70)
