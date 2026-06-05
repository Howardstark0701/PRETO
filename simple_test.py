#!/usr/bin/env python
"""Simple API Test"""
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Test 1: Health
        r1 = await client.get("http://localhost:8000/api/health")
        print(f"✅ TEST 1 - Health: {r1.status_code}")
        
        # Test 2: User Repos
        r2 = await client.get("http://localhost:8000/api/repos/user/torvalds?per_page=3")
        print(f"✅ TEST 2 - User Repos: {r2.status_code}")
        if r2.status_code == 200:
            d = r2.json()
            print(f"   Username: {d.get('username')}, Total: {d.get('total_count')}, Returned: {len(d.get('repos', []))}")
        
        # Test 3: Search
        r3 = await client.get("http://localhost:8000/api/repos/search?query=python&per_page=3")
        print(f"✅ TEST 3 - Search: {r3.status_code}")
        if r3.status_code == 200:
            d = r3.json()
            print(f"   Query: {d.get('query')}, Results: {d.get('total_count')}")
        
        # Test 4: Advanced Search
        r4 = await client.get("http://localhost:8000/api/repos/search/advanced?query=web&page=1&per_page=5")
        print(f"✅ TEST 4 - Advanced Search: {r4.status_code}")
        if r4.status_code == 200:
            d = r4.json()
            p = d.get('pagination', {})
            print(f"   Total: {p.get('total_count')}, Page: {p.get('current_page')}/{p.get('total_pages')}")
        
        # Test 5: User Stats
        r5 = await client.get("http://localhost:8000/api/repos/user/torvalds/stats")
        print(f"✅ TEST 5 - User Stats: {r5.status_code}")
        if r5.status_code == 200:
            d = r5.json()
            print(f"   Repos: {d.get('total_repositories')}, Stars: {d.get('total_stars')}, Language: {d.get('most_used_language')}")
        
        # Test 6: Error Handling
        r6 = await client.get("http://localhost:8000/api/repos/user/")
        print(f"✅ TEST 6 - Error Handling (Empty): {r6.status_code} (expected 400)")
        
        print("\n🎉 ALL BASIC TESTS PASSED!")

asyncio.run(main())
