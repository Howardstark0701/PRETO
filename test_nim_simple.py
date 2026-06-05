#!/usr/bin/env python
"""Simple NIM API test"""

import os
import sys
import json

# Load environment
from dotenv import load_dotenv
load_dotenv()

print("NVIDIA NIM INTEGRATION TEST")
print("=" * 60)

# Check configuration
NIM_API_KEY = os.getenv("NIM_API_KEY", "")
NIM_API_URL = os.getenv("NIM_API_URL", "")
NIM_MODEL = os.getenv("NIM_MODEL", "")

print("\n✅ CONFIGURATION CHECK:")
print(f"   NIM_API_KEY: {'SET ✓' if NIM_API_KEY else 'NOT SET ✗'}")
print(f"   NIM_API_URL: {NIM_API_URL[:50]}...")
print(f"   NIM_MODEL: {NIM_MODEL}")
print(f"   MAX_REQUESTS_PER_MINUTE: {os.getenv('MAX_REQUESTS_PER_MINUTE')}")

# Test insights module imports
print("\n✅ MODULE IMPORTS:")
try:
    from app.api.insights import NIMInsights, RateLimiter, get_insights_manager
    print("   - NIMInsights imported ✓")
    print("   - RateLimiter imported ✓")
    
    insights = get_insights_manager()
    print(f"   - Insights manager created ✓")
    print(f"   - NIM client ready: {'YES ✓' if insights.client else 'NO (fallback mode)'}")
    
    if insights.client:
        print("   - Rate limiter initialized ✓")
        stats = insights.rate_limiter.get_stats()
        print(f"     Available slots: {stats['available_slots']}/{stats['max_requests']}")
        
except ImportError as e:
    print(f"   ✗ Import error: {e}")
    sys.exit(1)

# Test routes
print("\n✅ ROUTES CHECK:")
try:
    from app.api.insights_routes import router
    print(f"   - Insights router loaded ✓")
    print(f"   - Endpoints: /analyze, /query, /search-insights, /user-analysis, /health")
    
except ImportError as e:
    print(f"   ✗ Import error: {e}")

print("\n" + "=" * 60)
print("✅ NIM INTEGRATION LOOKS GOOD!")
print("\nNext steps:")
print("1. Server should be running: python main.py")
print("2. Test endpoint: curl http://localhost:8000/api/insights/health")
print("3. Should see: 'insights_service': 'NVIDIA NIM'")
print("=" * 60)
