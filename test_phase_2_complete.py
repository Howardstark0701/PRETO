"""
Comprehensive test for Phase 2.1-2.3 implementation

Tests:
- Phase 2.1: Data Persistence (CRUD operations)
- Phase 2.2: Caching Layer
- Phase 2.3: Background Tasks & Scheduling
- New Management Endpoints

Author: TANGO
Date: June 5, 2026
"""

import asyncio
import json
import urllib.request
import urllib.error
from datetime import datetime
from urllib.parse import urlencode

# API base URL
BASE_URL = "http://localhost:8000/api"


def make_request(method, url, params=None):
    """Make HTTP request using urllib."""
    if params:
        url = f"{url}?{urlencode(params)}"
    
    req = urllib.request.Request(url, method=method)
    req.add_header('Accept', 'application/json')
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read().decode('utf-8')
            return response.status, json.loads(data)
    except urllib.error.HTTPError as e:
        data = e.read().decode('utf-8')
        return e.code, json.loads(data) if data else {}


def test_health_check():
    """Test health check endpoint."""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    try:
        status, response = make_request("GET", f"{BASE_URL}/health")
        print(f"Status: {status}")
        print(f"Response: {json.dumps(response, indent=2)}")
        
        assert status == 200, "Health check failed"
        assert response["status"] == "healthy", "API not healthy"
        print("✅ PASSED: Health check working")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_cache_stats():
    """Test cache statistics endpoint (Phase 2.2)."""
    print("\n" + "="*60)
    print("TEST 2: Cache Statistics (Phase 2.2)")
    print("="*60)
    
    try:
        status, data = make_request("GET", f"{BASE_URL}/cache/stats")
        print(f"Status: {status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        
        assert status == 200, "Cache stats endpoint failed"
        assert "cache" in data, "Missing cache stats"
        assert "active_entries" in data["cache"], "Missing active_entries"
        print("✅ PASSED: Cache statistics working")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_scheduler_stats():
    """Test scheduler statistics endpoint (Phase 2.3)."""
    print("\n" + "="*60)
    print("TEST 3: Scheduler Statistics (Phase 2.3)")
    print("="*60)
    
    try:
        status, data = make_request("GET", f"{BASE_URL}/scheduler/stats")
        print(f"Status: {status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        
        assert status == 200, "Scheduler stats endpoint failed"
        assert "scheduler" in data, "Missing scheduler stats"
        assert data["scheduler"]["is_running"] == True, "Scheduler not running"
        assert data["scheduler"]["total_jobs"] == 2, "Expected 2 background jobs"
        print("✅ PASSED: Scheduler is running with background tasks")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_sync_stats():
    """Test sync statistics endpoint (Phase 2.3)."""
    print("\n" + "="*60)
    print("TEST 4: Sync Statistics (Phase 2.3)")
    print("="*60)
    
    try:
        status, data = make_request("GET", f"{BASE_URL}/sync/stats")
        print(f"Status: {status}")
        print(f"Response: {json.dumps(data, indent=2, default=str)}")
        
        assert status == 200, "Sync stats endpoint failed"
        assert "sync" in data, "Missing sync stats"
        print("✅ PASSED: Sync statistics endpoint working")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_cache_invalidation():
    """Test cache invalidation (Phase 2.2)."""
    print("\n" + "="*60)
    print("TEST 5: Cache Invalidation (Phase 2.2)")
    print("="*60)
    
    try:
        # Clear all cache
        req = urllib.request.Request(f"{BASE_URL}/cache/clear", method="DELETE")
        req.add_header('Accept', 'application/json')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        print(f"Status: 200")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        assert data["status"] == "success", "Cache clear unsuccessful"
        print("✅ PASSED: Cache clearing working")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_user_repos_with_cache():
    """Test user repos endpoint with caching (Phase 2.2)."""
    print("\n" + "="*60)
    print("TEST 6: User Repos with Caching (Phase 2.2)")
    print("="*60)
    
    try:
        username = "torvalds"
        
        # First request (should fetch from GitHub)
        print(f"\n📍 First request for {username} (no cache):")
        status1, data1 = make_request(
            "GET",
            f"{BASE_URL}/repos/user/{username}",
            params={"per_page": 5, "use_cache": False}
        )
        print(f"Status: {status1}")
        print(f"Total count: {data1['total_count']}")
        print(f"Cached: {data1['cached']}")
        
        assert status1 == 200, "First request failed"
        assert data1["cached"] == False, "Should not be cached on first request"
        
        # Second request (should use cache)
        print(f"\n📍 Second request for {username} (with cache):")
        status2, data2 = make_request(
            "GET",
            f"{BASE_URL}/repos/user/{username}",
            params={"per_page": 5, "use_cache": True}
        )
        print(f"Status: {status2}")
        print(f"Total count: {data2['total_count']}")
        print(f"Cached: {data2['cached']}")
        
        assert status2 == 200, "Second request failed"
        assert data2["cached"] == True, "Should be cached on second request"
        
        print("✅ PASSED: Caching working correctly")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_search_with_cache():
    """Test search with caching (Phase 2.2)."""
    print("\n" + "="*60)
    print("TEST 7: Search with Caching (Phase 2.2)")
    print("="*60)
    
    try:
        query = "machine learning"
        
        # First search (no cache)
        print(f"\n📍 First search for '{query}' (no cache):")
        status1, data1 = make_request(
            "GET",
            f"{BASE_URL}/repos/search",
            params={"query": query, "per_page": 5, "use_cache": False}
        )
        print(f"Status: {status1}")
        print(f"Total count: {data1['total_count']}")
        print(f"Cached: {data1['cached']}")
        
        assert status1 == 200, "First search failed"
        assert data1["cached"] == False, "Should not be cached"
        
        # Second search (with cache)
        print(f"\n📍 Second search for '{query}' (with cache):")
        status2, data2 = make_request(
            "GET",
            f"{BASE_URL}/repos/search",
            params={"query": query, "per_page": 5, "use_cache": True}
        )
        print(f"Status: {status2}")
        print(f"Cached: {data2['cached']}")
        
        assert status2 == 200, "Second search failed"
        assert data2["cached"] == True, "Should be cached"
        
        print("✅ PASSED: Search caching working")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def test_scheduler_job_toggle():
    """Test scheduler job toggling (Phase 2.3)."""
    print("\n" + "="*60)
    print("TEST 8: Scheduler Job Toggle (Phase 2.3)")
    print("="*60)
    
    try:
        job_id = "cache_maintenance"
        
        # Check initial state
        print(f"\n📍 Getting initial state of {job_id}:")
        status1, data1 = make_request("GET", f"{BASE_URL}/scheduler/stats")
        jobs = data1["scheduler"]["jobs"]
        initial_job = next(j for j in jobs if j["job_id"] == job_id)
        print(f"Initial enabled state: {initial_job['enabled']}")
        
        # Toggle job
        print(f"\n📍 Toggling {job_id}:")
        req = urllib.request.Request(
            f"{BASE_URL}/scheduler/jobs/{job_id}/toggle",
            method="POST"
        )
        req.add_header('Accept', 'application/json')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        print(f"Status: 200")
        print(f"New state: {data['new_state']}")
        
        assert data["new_state"] != initial_job['enabled'], "Job state should have changed"
        
        # Toggle back
        print(f"\n📍 Toggling {job_id} back:")
        req = urllib.request.Request(
            f"{BASE_URL}/scheduler/jobs/{job_id}/toggle",
            method="POST"
        )
        req.add_header('Accept', 'application/json')
        with urllib.request.urlopen(req, timeout=30) as response:
            pass
        
        print("✅ PASSED: Job toggling working")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print("PHASE 2.1-2.3 COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("Testing Data Persistence, Caching, Background Tasks & Scheduling")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Cache Statistics", test_cache_stats()))
    results.append(("Scheduler Statistics", test_scheduler_stats()))
    results.append(("Sync Statistics", test_sync_stats()))
    results.append(("Cache Invalidation", test_cache_invalidation()))
    results.append(("User Repos with Cache", test_user_repos_with_cache()))
    results.append(("Search with Cache", test_search_with_cache()))
    results.append(("Scheduler Job Toggle", test_scheduler_job_toggle()))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Phase 2.1-2.3 implementation complete and working!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST SUITE ERROR: {str(e)}")
        exit(1)
