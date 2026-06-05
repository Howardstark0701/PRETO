# 🚀 PRETO Phase 2 Quick Start Guide

**Welcome to PRETO v0.2.0!** The server is running and ready to use.

---

## 🟢 Server Status

✅ **Server Running**: http://localhost:8000  
✅ **API Docs**: http://localhost:8000/api/docs  
✅ **Background Tasks**: Running (Cache maintenance + Database stats)  
✅ **Database**: Initialized with 5 tables

---

## 🎯 5-Minute Start

### 1. Test Health Check
```bash
curl http://localhost:8000/api/health
```

### 2. Search Repositories
```bash
curl "http://localhost:8000/api/repos/search?query=machine%20learning&per_page=5"
```

### 3. Get User Repos (with caching!)
```bash
# First request (fetches from GitHub)
curl "http://localhost:8000/api/repos/user/torvalds?per_page=5&use_cache=false"

# Second request (uses cache)
curl "http://localhost:8000/api/repos/user/torvalds?per_page=5&use_cache=true"
```

### 4. Check Cache Status
```bash
curl http://localhost:8000/api/cache/stats
```

### 5. Check Scheduler
```bash
curl http://localhost:8000/api/scheduler/stats
```

---

## 📚 Key Endpoints

### GET Endpoints (with Caching ✅)
```
GET /api/repos/user/{username}           - Get user repos
GET /api/repos/search                    - Search repos
GET /api/repos/search/advanced           - Advanced search (pagination)
GET /api/repos/{owner}/{repo_name}       - Repo details
GET /api/repos/user/{username}/stats     - User statistics
GET /api/health                          - Health check
```

**All include**: `use_cache=true/false` parameter

### Management Endpoints (New!)
```
GET /api/cache/stats                     - Cache statistics
DELETE /api/cache/clear                  - Clear cache
GET /api/scheduler/stats                 - Scheduler status
POST /api/scheduler/jobs/{id}/toggle     - Enable/disable jobs
POST /api/sync/user/{username}           - Manual sync
GET /api/sync/stats                      - Sync statistics
```

---

## 💾 Caching Guide

### How Caching Works
1. **First request** (`use_cache=false`): Fetches from GitHub, saves to cache
2. **Next request** (`use_cache=true`): Returns cached data instantly
3. **Cache expires**: Automatically removed after TTL

### Cache Types & TTLs
- **user_repos**: 60 minutes
- **search**: 30 minutes
- **stats**: 120 minutes
- **repo_details**: 180 minutes

### Clear Cache When Needed
```bash
# Clear all cache
curl -X DELETE http://localhost:8000/api/cache/clear

# Clear specific type
curl -X DELETE "http://localhost:8000/api/cache/clear?cache_type=search"
```

---

## ⏱️ Background Tasks

### Running Tasks
1. **cache_maintenance** - Every 30 minutes (cleanup expired entries)
2. **database_stats** - Every 60 minutes (collect statistics)

### Monitor Tasks
```bash
curl http://localhost:8000/api/scheduler/stats
```

### Toggle Tasks
```bash
# Disable cache maintenance
curl -X POST http://localhost:8000/api/scheduler/jobs/cache_maintenance/toggle

# Enable it again
curl -X POST http://localhost:8000/api/scheduler/jobs/cache_maintenance/toggle
```

---

## 🔄 Manual Sync

### Sync User Repositories
```bash
curl -X POST http://localhost:8000/api/sync/user/torvalds
```

### Check Sync Status
```bash
curl http://localhost:8000/api/sync/stats
```

---

## 📊 Usage Examples

### Search Python Projects
```bash
curl "http://localhost:8000/api/repos/search?query=django&language=python&per_page=10"
```

### Get Top JavaScript Repos
```bash
curl "http://localhost:8000/api/repos/search/advanced?query=framework&language=javascript&sort_by=stars&page=1"
```

### Get User Statistics
```bash
curl http://localhost:8000/api/repos/user/guido/stats
```

### Get Repository Details
```bash
curl http://localhost:8000/api/repos/python/cpython
```

---

## 🧪 Browser Testing

### Open Swagger UI
Visit: http://localhost:8000/api/docs

Features:
- Test all endpoints interactively
- See response schemas
- Try parameters
- Auto-generated documentation

### Endpoints in Swagger UI
All 13 endpoints are documented with:
- Description
- Parameters
- Response examples
- Error codes

---

## ⚙️ Configuration

### Cache TTLs (Edit in app/api/cache.py)
```python
CACHE_TTL = {
    'user_repos': 60,
    'search': 30,
    'stats': 120,
    'repo_details': 180,
}
```

### Job Intervals (Edit in main.py startup)
```python
jobs = {
    'cache_maintenance': (func, 30, "description"),  # 30 minutes
    'database_stats': (func, 60, "description"),      # 60 minutes
}
```

---

## 🐛 Troubleshooting

### Cache Not Working?
1. Check cache stats: `curl http://localhost:8000/api/cache/stats`
2. Clear cache: `curl -X DELETE http://localhost:8000/api/cache/clear`
3. Verify use_cache=true in request

### Background Jobs Not Running?
1. Check scheduler: `curl http://localhost:8000/api/scheduler/stats`
2. Verify is_running = true
3. Check enabled_jobs = 2

### Sync Failed?
1. Check username exists on GitHub
2. Verify GitHub API is responding
3. Check /api/sync/stats for errors

### Database Issues?
1. Database file: `preto.db`
2. Tables created automatically
3. Check logs for SQL errors

---

## 📈 Monitoring

### Real-time Monitoring
```bash
# Watch cache performance
watch 'curl -s http://localhost:8000/api/cache/stats | python -m json.tool'

# Watch scheduler
watch 'curl -s http://localhost:8000/api/scheduler/stats | python -m json.tool'

# Watch sync stats
watch 'curl -s http://localhost:8000/api/sync/stats | python -m json.tool'
```

---

## 📝 Response Examples

### Successful Search
```json
{
  "query": "machine learning",
  "total_count": 150000,
  "cached": true,
  "results": [
    {
      "name": "tensorflow",
      "full_name": "tensorflow/tensorflow",
      "stargazers_count": 180000,
      ...
    }
  ]
}
```

### Cache Stats
```json
{
  "status": "success",
  "cache": {
    "active_entries": 5,
    "total_hits": 12,
    "memory_usage": "2.34 KB"
  }
}
```

### Scheduler Status
```json
{
  "status": "success",
  "scheduler": {
    "is_running": true,
    "total_jobs": 2,
    "jobs": [
      {
        "job_id": "cache_maintenance",
        "enabled": true,
        "run_count": 1,
        "failures": 0
      }
    ]
  }
}
```

---

## 🔐 Security Notes

- ✅ Input validation on all endpoints
- ✅ Error messages non-revealing
- ⚠️ No authentication (add in Phase 3)
- ⚠️ No rate limiting (add in Phase 3)
- ✅ Database transactions with rollback

---

## 🚀 Next Steps

1. **Test all endpoints** via Swagger UI
2. **Monitor cache performance** using /api/cache/stats
3. **Trigger manual sync** to populate database
4. **Watch scheduler** run background jobs
5. **Prepare for Phase 3** (auth, AI integration)

---

## 📚 More Information

- **Full API Reference**: See `API_ENDPOINTS_PHASE_2.md`
- **Implementation Details**: See `PHASE_2_1_2_3_COMPLETE.md`
- **Architecture Overview**: See `FINAL_PHASE_2_SUMMARY.md`

---

## 🎯 You're All Set! 🎉

**Phase 2.1-2.3 is complete and running:**
- ✅ Data Persistence (CRUD)
- ✅ Caching System (TTL-based)
- ✅ Background Tasks (Scheduler)
- ✅ Management Endpoints (6 new)

**Ready to use the PRETO platform!**

---

*PRETO v0.2.0 - OSINT Analytics Platform*  
*Phase 2.1-2.3 Complete*  
*Server: http://localhost:8000*
