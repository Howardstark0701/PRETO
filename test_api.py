"""
Comprehensive API Testing Script for PRETO

Tests all endpoints and features

Author: TANGO
Date: June 5, 2026
"""

import httpx
import json
import asyncio
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_health():
    """Test: Health check endpoint"""
    print("\n" + "="*60)
    print("✅ TEST 1: Health Check")
    print("="*60)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/health")
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(data, indent=2)}")
            return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_welcome():
    """Test: Welcome endpoint"""
    print("\n" + "="*60)
    print("✅ TEST 2: Welcome Endpoint")
    print("="*60)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/")
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Name: {data.get('name')}")
            print(f"Description: {data.get('description')}")
            print(f"Version: {data.get('version')}")
            return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_user_repos():
    """Test: Get user repositories"""
    print("\n" + "="*60)
    print("✅ TEST 3: Get User Repositories (torvalds)")
    print("="*60)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/repos/user/torvalds?per_page=3")
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Username: {data.get('username')}")
            print(f"Total Count: {data.get('total_count')}")
            print(f"Repos returned: {len(data.get('repos', []))}")
            print("\nTop 3 Repos:")
            for repo in data.get('repos', [])[:3]:
                print(f"  • {repo.get('name')}: {repo.get('stargazers_count')} ⭐")
            return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_sorting():
    """Test: Sorting by stars"""
    print("\n" + "="*60)
    print("✅ TEST 4: Sorting by Stars (Descending)")
    print("="*60)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/repos/user/guido?sort_by=stars&sort_order=desc&per_page=3"
            )
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Sort By: {data.get('sort_by')}")
            print(f"Sort Order: {data.get('sort_order')}")
            print("\nTop 3 Repos by Stars:")
            prev_stars = None
            for i, repo in enumerate(data.get('repos', [])[:3], 1):
                stars = repo.get('stargazers_count', 0)
                print(f"  {i}. {repo.get('name')}: {stars} ⭐")
                # Verify descending order
                if prev_stars is not None and stars > prev_stars:
                    print(f"    ⚠️ Warning: Not in descending order!")
                prev_stars = stars
            return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_filtering():
    """Test: Filter by language"""
    print("\n" + "="*60)
    print("✅ TEST 5: Filtering by Language")
    print("="*60)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/repos/user/gvanrossum?language=python&per_page=5"
            )
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Total Repos: {data.get('total_count')}")
            print("\nFiltered Repos (Python):")
            for repo in data.get('repos', []):
                lang = repo.get('language', 'Unknown')
                print(f"  • {repo.get('name')}: {lang}")
            return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_search():
    """Test: Search repositories"""
    print("\n" + "="*60)
    print("✅ TEST 6: Search Repositories")
    print("="*60)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/repos/search?query=machine-learning&language=python&per_page=3"
            )
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Query: {data.get('query')}")
            print(f"Language: {data.get('language')}")
            print(f"Total Results: {data.get('total_count')}")
            print("\nTop 3 Results:")
            for repo in data.get('results', [])[:3]:
                print(f"  • {repo.get('full_name')}: {repo.get('stargazers_count')} ⭐")
            return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_advanced_search():
    """Test: Advanced search with pagination"""
    print("\n" + "="*60)
    print("✅ TEST 7: Advanced Search with Pagination")
    print("="*60)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/repos/search/advanced?query=web&min_stars=500&page=1&per_page=5"
            )
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Query: {data.get('query')}")
            print(f"Filters: {json.dumps(data.get('filters'), indent=2)}")
            
            pagination = data.get('pagination', {})
            print(f"\nPagination:")
            print(f"  Total: {pagination.get('total_count')}")
            print(f"  Page: {pagination.get('current_page')}/{pagination.get('total_pages')}")
            print(f"  Has Next: {pagination.get('has_next')}")
            print(f"  Has Prev: {pagination.get('has_prev')}")
            
            print(f"\nResults on Page 1:")
            for i, repo in enumerate(data.get('results', [])[:3], 1):
                print(f"  {i}. {repo.get('full_name')}: {repo.get('stargazers_count')} ⭐")
            
            return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_user_stats():
    """Test: User statistics"""
    print("\n" + "="*60)
    print("✅ TEST 8: User Statistics")
    print("="*60)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/repos/user/torvalds/stats")
            data = response.json()
            print(f"Status: {response.status_code}")
            print(f"Username: {data.get('username')}")
            print(f"Total Repositories: {data.get('total_repositories')}")
            print(f"Total Stars: {data.get('total_stars')} ⭐")
            print(f"Total Forks: {data.get('total_forks')} 🔗")
            print(f"Total Watchers: {data.get('total_watchers')} 👀")
            print(f"Average Stars Per Repo: {data.get('average_stars_per_repo')}")
            print(f"Most Used Language: {data.get('most_used_language')}")
            print(f"\nLanguages Used:")
            for lang, count in sorted(data.get('languages', {}).items(), 
                                     key=lambda x: x[1], reverse=True)[:5]:
                print(f"  • {lang}: {count} repos")
            
            return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_error_handling():
    """Test: Error handling"""
    print("\n" + "="*60)
    print("✅ TEST 9: Error Handling")
    print("="*60)
    
    tests = [
        ("Empty username", f"{BASE_URL}/api/repos/user/", 400),
        ("Invalid per_page", f"{BASE_URL}/api/repos/user/torvalds?per_page=200", 400),
        ("User not found", f"{BASE_URL}/api/repos/user/nonexistent_user_xyz_123", 404),
        ("Empty search", f"{BASE_URL}/api/repos/search?query=", 400),
    ]
    
    all_passed = True
    async with httpx.AsyncClient() as client:
        for test_name, url, expected_status in tests:
            try:
                response = await client.get(url)
                status = response.status_code
                passed = status == expected_status
                symbol = "✅" if passed else "❌"
                print(f"{symbol} {test_name}: {status} (expected {expected_status})")
                if not passed:
                    all_passed = False
            except Exception as e:
                print(f"❌ {test_name}: {str(e)}")
                all_passed = False
    
    return all_passed


async def main():
    """Run all tests"""
    print("\n" + "🧪 PRETO API COMPREHENSIVE TESTING".center(60) + "\n")
    
    results = []
    
    # Run all tests
    results.append(("Health Check", await test_health()))
    results.append(("Welcome", await test_welcome()))
    results.append(("User Repos", await test_user_repos()))
    results.append(("Sorting", await test_sorting()))
    results.append(("Filtering", await test_filtering()))
    results.append(("Search", await test_search()))
    results.append(("Advanced Search", await test_advanced_search()))
    results.append(("User Stats", await test_user_stats()))
    results.append(("Error Handling", await test_error_handling()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        symbol = "✅" if result else "❌"
        print(f"{symbol} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    asyncio.run(main())
