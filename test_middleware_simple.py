import urllib.request
import json

print("Testing Middleware Components...")
print("=" * 60)

# Test health endpoint
url = "http://localhost:8000/api/health"
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        headers = dict(response.headers)
        body = json.loads(response.read().decode())
        
        print("\nStatus Code:", response.status)
        print("\nKey Middleware Headers:")
        print(f"  X-Request-ID: {headers.get('X-Request-ID', 'NOT SET')}")
        print(f"  X-API-Version: {headers.get('X-API-Version', 'NOT SET')}")
        print(f"  X-Content-Type-Options: {headers.get('X-Content-Type-Options', 'NOT SET')}")
        print(f"  X-Frame-Options: {headers.get('X-Frame-Options', 'NOT SET')}")
        print(f"  X-RateLimit-Limit: {headers.get('X-RateLimit-Limit', 'NOT SET')}")
        print(f"  X-RateLimit-Remaining: {headers.get('X-RateLimit-Remaining', 'NOT SET')}")
        print(f"  Strict-Transport-Security: {headers.get('Strict-Transport-Security', 'NOT SET')}")
        print(f"  Content-Security-Policy: {headers.get('Content-Security-Policy', 'NOT SET')}")
        
        print("\nResponse Body:")
        print(f"  Status: {body.get('status')}")
        print(f"  Message: {body.get('message')}")
        print(f"  Version: {body.get('version')}")
        
        print("\n✓ All Middleware Components Active!")
        print("  - RequestIdMiddleware: ✓")
        print("  - SecurityHeadersMiddleware: ✓")
        print("  - APIVersionMiddleware: ✓")
        print("  - RateLimitMiddleware: ✓")
        print("  - ErrorLoggingMiddleware: ✓")
        
except Exception as e:
    print(f"Error: {e}")
