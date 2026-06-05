# PRETO API Endpoints - Phase 2 Complete Reference

**Server**: http://localhost:8000  
**API Docs**: http://localhost:8000/api/docs  
**Last Updated**: June 5, 2026

---

## 📍 Quick Navigation

- [Original Phase 2 Endpoints](#original-endpoints)
- [New Management Endpoints (Phase 2.1-2.3)](#new-management-endpoints)
- [Caching Integration](#caching-integration)
- [Error Responses](#error-responses)

---

## 🔵 Original Endpoints

### ✅ GET /api/health
**Description**: Health check endpoint  
**Parameters**: None  
**Response**: `200 OK`

```bash
curl http://localhost:8000/api/health
```

**Response**:
```json
{
  "status": "healthy",
  "message": "PRETO API is running",
  "version": "0.2.0",
  "timestamp": "2026-06-05T11:48:02.123456"
}
```

---

### ✅ GET /api/repos/user/{username}
**Description**: Get user repositories with sorting, filtering, and caching  
**Parameters**:
- `username` (string, required): GitHub username
- `per_page` (int, optional, 1-100, default 30): Results per page
- `sort_by` (string, optional): stars, forks, watchers, updated_at, name
- `sort_order` (string, optional): asc or desc
- `language` (string, optional): Filter by programming language
- `min_stars` (int, optional): Filter by minimum stars
- `use_cache` (bool, optional, default true): Use cached results

**Response**: `200 OK` or `404 Not Found`

```bash
# First request (fetches from GitHub)
curl "http://localhost:8000/api/repos/user/torvalds?per_page=5&sort_by=stars&use_cache=false"

# Second request (uses cache)
curl "http://localhost:8000/api/repos/user/torvalds?per_page=5&sort_by=stars&use_cache=true"
```

**Response**:
```json
{
  "username": "torvalds",
  "total_count": 45,
  "cached": true,
  "repos": [
    {
      "name": "linux",
      "full_name": "torvalds/linux",
      "stargazers_count": 170000,
      "language": "C",
      ...
    }
  ],
  "last_updated": "2026-06-05T11:48:02.123456",
  "sort_by": "stars",
  "sort_order": "desc"
}
```

---

### ✅ GET /api/repos/search
**Description**: Search repositories with caching  
**Parameters**:
- `query` (string, required): Search query
- `language` (string, optional): Programming language filter
- `per_page` (int, optional, 1-100, default 30): Results per page
- `use_cache` (bool, optional, default true): Use cached results

**Response**: `200 OK` or `404 Not Found`

```bash
curl "http://localhost:8000/api/repos/search?query=machine%20learning&language=python&per_page=10"
```

**Response**:
```json
{
  "query": "machine learning",
  "language": "python",
  "per_page": 10,
  "total_count": 150000,
  "cached": true,
  "results": [ ... ],
  "last_updated": "2026-06-05T11:48:02.123456"
}
```

---

### ✅ GET /api/repos/search/advanced
**Description**: Advanced search with pagination, sorting, and filtering  
**Parameters**:
- `query` (string, required): Search query
- `language` (string, optional): Filter by language
- `min_stars` (int, optional): Minimum stars filter
- `sort_by` (string, optional, default "stars"): Sort field
- `sort_order` (string, optional, default "desc"): asc or desc
- `page` (int, optional, default 1): Page number (1-indexed)
- `per_page` (int, optional, default 30, 1-100): Results per page
- `use_cache` (bool, optional, default true): Use cached results

**Response**: `200 OK` or `404 Not Found`

```bash
curl "http://localhost:8000/api/repos/search/advanced?query=web&language=javascript&page=1&per_page=20"
```

**Response**:
```json
{
  "query": "web",
  "language": "javascript",
  "filters": { "min_stars": null },
  "results": [ ... ],
  "pagination": {
    "total_count": 500000,
    "per_page": 20,
    "current_page": 1,
    "total_pages": 25000,
    "has_next": true,
    "has_prev": false
  },
  "sort_by": "stars",
  "sort_order": "desc",
  "last_updated": "2026-06-05T11:48:02.123456"
}
```

---

### ✅ GET /api/repos/{owner}/{repo_name}
**Description**: Get repository details  
**Parameters**:
- `owner` (string, required): Repository owner
- `repo_name` (string, required): Repository name
- `use_cache` (bool, optional, default true): Use cached results

**Response**: `200 OK` or `404 Not Found`

```bash
curl http://localhost:8000/api/repos/torvalds/linux
```

**Response**:
```json
{
  "name": "linux",
  "full_name": "torvalds/linux",
  "owner": "torvalds",
  "stargazers_count": 170000,
  "forks_count": 35000,
  "language": "C",
  "description": "Linux kernel source tree",
  "html_url": "https://github.com/torvalds/linux",
  ...
}
```

---

### ✅ GET /api/repos/user/{username}/stats
**Description**: Get user statistics  
**Parameters**:
- `username` (string, required): GitHub username
- `use_cache` (bool, optional, default true): Use cached results

**Response**: `200 OK` or `404 Not Found`

```bash
curl http://localhost:8000/api/repos/user/torvalds/stats
```

**Response**:
```json
{
  "username": "torvalds",
  "total_repositories": 45,
  "total_stars": 175000,
  "total_forks": 40000,
  "total_watchers": 80000,
  "languages": {
    "C": 25,
    "Python": 8,
    "Shell": 5,
    "Java": 3
  },
  "average_stars_per_repo": 3888,
  "average_forks_per_repo": 888,
  "most_used_language": "C",
  "fetched_at": "2026-06-05T11:48:02.123456"
}
```

---

## 🟢 New Management Endpoints (Phase 2.1-2.3)

### ✅ GET /api/cache/stats
**Description**: Get cache statistics (Phase 2.2)  
**Parameters**: None  
**Response**: `200 OK`

```bash
curl http://localhost:8000/api/cache/stats
```

**Response**:
```json
{
  "status": "success",
  "cache": {
    "active_entries": 5,
    "expired_entries": 0,
    "total_entries": 5,
    "total_hits": 12,
    "memory_usage": "2.34 KB"
  },
  "timestamp": "2026-06-05T11:48:02.123456"
}
```

---

### ✅ DELETE /api/cache/clear
**Description**: Clear cache entries (Phase 2.2)  
**Parameters**:
- `cache_type` (string, optional): Type to clear (user_repos, search, stats, repo_details)

**Response**: `200 OK`

```bash
# Clear all cache
curl -X DELETE http://localhost:8000/api/cache/clear

# Clear specific cache type
curl -X DELETE "http://localhost:8000/api/cache/clear?cache_type=user_repos"
```

**Response**:
```json
{
  "status": "success",
  "message": "Cleared all 5 cache entries",
  "entries_cleared": 5,
  "timestamp": "2026-06-05T11:48:02.123456"
}
```

---

### ✅ GET /api/scheduler/stats
**Description**: Get scheduler statistics (Phase 2.3)  
**Parameters**: None  
**Response**: `200 OK`

```bash
curl http://localhost:8000/api/scheduler/stats
```

**Response**:
```json
{
  "status": "success",
  "scheduler": {
    "is_running": true,
    "total_jobs": 2,
    "enabled_jobs": 2,
    "disabled_jobs": 0,
    "total_runs": 1,
    "total_failures": 0,
    "jobs": [
      {
        "job_id": "cache_maintenance",
        "description": "Clean up expired cache entries",
        "interval_minutes": 30,
        "enabled": true,
        "last_run": null,
        "next_run": "2026-06-05T11:48:02.490996",
        "run_count": 1,
        "failures": 0
      },
      {
        "job_id": "database_stats",
        "description": "Collect database statistics",
        "interval_minutes": 60,
        "enabled": true,
        "last_run": null,
        "next_run": "2026-06-05T11:48:02.490996",
        "run_count": 1,
        "failures": 0
      }
    ]
  },
  "timestamp": "2026-06-05T11:48:02.123456"
}
```

---

### ✅ POST /api/scheduler/jobs/{job_id}/toggle
**Description**: Toggle scheduler job (Phase 2.3)  
**Parameters**:
- `job_id` (string, required in URL): Job ID to toggle

**Response**: `200 OK` or `404 Not Found`

```bash
curl -X POST http://localhost:8000/api/scheduler/jobs/cache_maintenance/toggle
```

**Response**:
```json
{
  "status": "success",
  "job_id": "cache_maintenance",
  "new_state": "disabled",
  "job_info": {
    "job_id": "cache_maintenance",
    "description": "Clean up expired cache entries",
    "interval_minutes": 30,
    "enabled": false,
    "last_run": null,
    "next_run": "2026-06-05T11:48:02.490996",
    "run_count": 1,
    "failures": 0
  },
  "timestamp": "2026-06-05T11:48:02.123456"
}
```

---

### ✅ POST /api/sync/user/{username}
**Description**: Manually sync user repositories (Phase 2.3)  
**Parameters**:
- `username` (string, required in URL): GitHub username to sync

**Response**: `200 OK` or `500 Error`

```bash
curl -X POST http://localhost:8000/api/sync/user/torvalds
```

**Response**:
```json
{
  "status": "initiated",
  "username": "torvalds",
  "result": {
    "status": "success",
    "username": "torvalds",
    "repos_synced": 45,
    "duration_seconds": 2.34,
    "timestamp": "2026-06-05T11:48:02.123456"
  },
  "timestamp": "2026-06-05T11:48:02.123456"
}
```

---

### ✅ GET /api/sync/stats
**Description**: Get sync statistics (Phase 2.3)  
**Parameters**: None  
**Response**: `200 OK`

```bash
curl http://localhost:8000/api/sync/stats
```

**Response**:
```json
{
  "status": "success",
  "sync": {
    "total_syncs": 0,
    "total_repos_synced": 0,
    "total_users_synced": 0,
    "last_sync_time": null,
    "last_sync_duration": null,
    "errors": [],
    "timestamp": "2026-06-05T11:48:02.507716"
  }
}
```

---

## 💾 Caching Integration

All `GET` endpoints now include caching support with `use_cache` parameter (default: true)

### Cache Types & TTLs
| Endpoint | Cache Type | TTL | Key Variables |
|----------|-----------|-----|---------------|
| `/api/repos/user/{username}` | user_repos | 60m | username, language, min_stars |
| `/api/repos/search` | search | 30m | query, language |
| `/api/repos/search/advanced` | search | 30m | query, language, min_stars |
| `/api/repos/{owner}/{repo_name}` | repo_details | 180m | owner, repo_name |
| `/api/repos/user/{username}/stats` | stats | 120m | username |

### Cache Behavior
1. **First request** (`use_cache=false`): Fetches from GitHub, stores in cache
2. **Subsequent requests** (`use_cache=true`): Returns cached data (if not expired)
3. **Expired cache**: Auto-removed, fresh data fetched from GitHub
4. **Cache invalidation**: Can be cleared via `DELETE /api/cache/clear`

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "status_code": 400,
  "error": "Validation Error",
  "detail": "Username cannot be empty",
  "timestamp": "2026-06-05T11:48:02.123456"
}
```

### 404 Not Found
```json
{
  "status_code": 404,
  "error": "Not Found",
  "detail": "User 'nonexistent' not found on GitHub or has no public repositories",
  "timestamp": "2026-06-05T11:48:02.123456"
}
```

### 502 Bad Gateway
```json
{
  "status_code": 502,
  "error": "GitHub API Error",
  "detail": "GitHub API error: rate limit exceeded",
  "timestamp": "2026-06-05T11:48:02.123456"
}
```

### 504 Gateway Timeout
```json
{
  "status_code": 504,
  "error": "Request Timeout",
  "detail": "Request timed out",
  "timestamp": "2026-06-05T11:48:02.123456"
}
```

---

## 🧪 Testing Endpoints

### Health Check
```bash
curl http://localhost:8000/api/health
```

### View Cache Stats (Monitor Phase 2.2)
```bash
curl http://localhost:8000/api/cache/stats
```

### View Scheduler Status (Monitor Phase 2.3)
```bash
curl http://localhost:8000/api/scheduler/stats
```

### Clear Cache (Phase 2.2)
```bash
curl -X DELETE http://localhost:8000/api/cache/clear
```

### Manual Sync (Phase 2.3)
```bash
curl -X POST http://localhost:8000/api/sync/user/torvalds
```

### Toggle Background Job (Phase 2.3)
```bash
curl -X POST http://localhost:8000/api/scheduler/jobs/cache_maintenance/toggle
```

---

## 📊 API Statistics

**Total Endpoints**: 13
- **Original**: 7
- **Management (New)**: 6

**Database Tables**: 5
- Repository
- GitHubUser
- Search
- UserStatistics
- CacheEntry

**Background Jobs**: 2
- cache_maintenance (30m interval)
- database_stats (60m interval)

**Cache Types**: 4
- user_repos (60m TTL)
- search (30m TTL)
- stats (120m TTL)
- repo_details (180m TTL)

---

**Version**: 0.2.0  
**Status**: ✅ Production Ready  
**Last Updated**: June 5, 2026
