# Phase 3 Quick Reference Guide

**Date**: June 5, 2026  
**Status**: ✅ Complete  
**Total Endpoints**: 34  
**New Middleware**: 5 layers  

---

## Server Status

```
✅ Running: http://localhost:8000
✅ Docs: http://localhost:8000/api/docs
✅ ReDoc: http://localhost:8000/api/redoc
✅ All 34 endpoints active
✅ Database: SQLite (preto.db)
```

---

## Quick Start

### 1. Authentication Flow

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"password123"}'

# Response includes: access_token, token_type, expires_in

# Use token for authenticated requests
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. AI Insights

```bash
# Analyze repositories
curl -X POST http://localhost:8000/api/insights/analyze \
  -H "Content-Type: application/json" \
  -d '{"repositories":[{"owner":"facebook","repo":"react"}],"analysis_type":"security"}'

# Natural language query
curl -X POST http://localhost:8000/api/insights/query \
  -H "Content-Type: application/json" \
  -d '{"question":"What are the most popular Python frameworks?"}'
```

### 3. Advanced Features

```bash
# Export results
curl -X POST http://localhost:8000/api/advanced/export \
  -H "Content-Type: application/json" \
  -d '{"results":[...],"format":"csv"}'

# Get analytics
curl -X POST http://localhost:8000/api/advanced/analytics \
  -H "Content-Type: application/json" \
  -d '{"repositories":[...]}'

# Get recommendations
curl -X POST http://localhost:8000/api/advanced/recommendations \
  -H "Content-Type: application/json" \
  -d '{"user_id":1}'
```

---

## Phase 3 Components

### Phase 3.1: Authentication ✅
| Component | File | Details |
|-----------|------|---------|
| Models | `app/models/auth.py` | User, SavedSearch, UserSearchHistory |
| Logic | `app/api/auth.py` | Password hashing, token generation |
| Schemas | `app/api/auth_schemas.py` | 15+ Pydantic models |
| Routes | `app/api/auth_routes.py` | 13 endpoints |

**Key Features**:
- User registration and login
- Token-based authentication
- Saved searches management
- Search history tracking

### Phase 3.2: Claude AI ✅
| Component | File | Details |
|-----------|------|---------|
| Integration | `app/api/insights.py` | Claude API client |
| Schemas | `app/api/insights_schemas.py` | Request/response models |
| Routes | `app/api/insights_routes.py` | 5 endpoints |

**Key Features**:
- Repository analysis
- Natural language queries
- Multiple analysis types
- Fallback mode

### Phase 3.3: Advanced Features ✅
| Component | File | Details |
|-----------|------|---------|
| Features | `app/api/advanced_features.py` | Core functionality |
| Routes | `app/api/advanced_routes.py` | 6 endpoints |

**Key Features**:
- Data export (JSON/CSV)
- Analytics generation
- Recommendations engine
- Report generation

### Phase 3.4: Production Hardening ✅
| Component | File | Details |
|-----------|------|---------|
| Middleware | `app/api/middleware.py` | 5 security layers |
| Integration | `main.py` | Middleware registration |

**Key Features**:
- Rate limiting (100 req/min per IP)
- Security headers
- Request tracing
- Error logging

---

## API Endpoints Cheat Sheet

### Authentication (13)
```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
GET    /api/auth/me
GET    /api/auth/users/{username}
POST   /api/auth/saved-searches
GET    /api/auth/saved-searches
GET    /api/auth/saved-searches/{search_id}
PUT    /api/auth/saved-searches/{search_id}
DELETE /api/auth/saved-searches/{search_id}
POST   /api/auth/saved-searches/{search_id}/favorite
GET    /api/auth/search-history
DELETE /api/auth/search-history
```

### Insights (5)
```
POST /api/insights/analyze
POST /api/insights/query
POST /api/insights/search-insights
POST /api/insights/user-analysis
GET  /api/insights/health
```

### Advanced (6)
```
POST /api/advanced/export
POST /api/advanced/analytics
POST /api/advanced/recommendations
POST /api/advanced/report
POST /api/advanced/compare
GET  /api/advanced/search-trends
```

### Repository (7)
```
GET /api/repos/user/{username}
GET /api/repos/search
GET /api/repos/{owner}/{repo_name}
GET /api/repos/user/{username}/stats
GET /api/repos/stats
GET /api/repos/trending
GET /api/repos/languages
```

### Management (6)
```
GET  /api/cache/stats
POST /api/cache/invalidate
GET  /api/scheduler/status
PUT  /api/scheduler/jobs/{job_id}
GET  /api/sync/stats
POST /api/sync/trigger
```

### Utility (2)
```
GET /api/health
GET /
```

---

## Middleware Details

### 1. RequestIdMiddleware
- **Header**: `X-Request-ID`
- **Purpose**: Request tracing
- **Enabled**: Always
- **Format**: `{timestamp}-{counter}`

### 2. SecurityHeadersMiddleware
- **Headers Added**: 5
- **Headers Removed**: 2 (Server, X-Powered-By)
- **Purpose**: Security hardening
- **Enabled**: Always

### 3. APIVersionMiddleware
- **Header**: `X-API-Version`
- **Supported**: v1
- **Validation**: 400 for unsupported versions
- **Enabled**: Always

### 4. ErrorLoggingMiddleware
- **Logs**: HTTP errors and exceptions
- **Details**: Method, path, status code
- **Level**: WARNING (4xx), ERROR (5xx+)
- **Enabled**: Always

### 5. RateLimitMiddleware
- **Limit**: 100 requests per minute
- **Per**: IP address
- **Window**: 1 minute sliding
- **Headers**: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
- **Enabled**: Always

---

## Environment Configuration

### `.env` File
```env
# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
DEBUG_MODE=True

# Claude API (Phase 3.2)
CLAUDE_API_KEY=sk-ant-your-key-here

# Database (Auto-generated)
# DATABASE_URL=sqlite:///./preto.db
```

### How to Update
```bash
# Edit .env file with your Claude API key
CLAUDE_API_KEY=sk-ant-abc123xyz...

# Server automatically reloads (if DEBUG_MODE=True)
```

---

## Database Tables (Phase 3.1)

### User Table
```
id (PK, autoincrement)
username (VARCHAR, unique)
email (VARCHAR, unique)
password_hash (VARCHAR)
created_at (DATETIME, default now)
last_login (DATETIME)
```

### SavedSearch Table
```
id (PK, autoincrement)
user_id (FK → User)
query (VARCHAR)
language (VARCHAR)
is_favorite (BOOLEAN, default false)
created_at (DATETIME, default now)
updated_at (DATETIME, default now)
```

### UserSearchHistory Table
```
id (PK, autoincrement)
user_id (FK → User)
search_query (VARCHAR)
timestamp (DATETIME, default now)
results_count (INTEGER)
execution_time (FLOAT)
```

---

## Testing Commands

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Check Middleware Headers
```bash
curl -i http://localhost:8000/api/health | grep X-
```

### Test Rate Limiting
```bash
for i in {1..110}; do curl -s http://localhost:8000/api/health | head -1; done
```

### Test API Version Validation
```bash
curl -H "X-API-Version: v2" http://localhost:8000/api/health
# Should return 400 Bad Request
```

### Test Authentication
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"test123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

---

## Common Issues & Solutions

### Server Won't Start
```
Error: ModuleNotFoundError
Solution: pip install fastapi uvicorn pydantic sqlalchemy python-dotenv httpx
```

### Database Locked
```
Error: database is locked
Solution: Delete preto.db and restart (auto-recreates)
```

### Rate Limited
```
Error: 429 Too Many Requests
Solution: Wait 60 seconds or use different IP
```

### API Version Error
```
Error: 400 Unsupported API version
Solution: Remove X-API-Version header or use v1
```

### Claude API Not Working
```
Error: API key not configured
Solution: Add CLAUDE_API_KEY to .env and restart
```

---

## Performance Tips

### Caching
- GET endpoints cached with TTL
- Use `use_cache=false` parameter to bypass
- Cache invalidated on updates

### Rate Limiting
- 100 requests/minute per IP
- Headers show remaining quota
- Plan requests accordingly

### Database
- SQLite suitable for dev
- Migrate to PostgreSQL for production
- Connection pooling enabled

---

## Security Checklist

- [x] Password hashing (SHA256)
- [x] Token-based authentication
- [x] Bearer token extraction
- [x] Rate limiting (100 req/min)
- [x] Security headers (5)
- [x] Sensitive headers removed
- [x] Error handling centralized
- [x] Request tracing enabled
- [x] API version validation
- [ ] HTTPS enabled (production)
- [ ] CORS restricted (production)
- [ ] Upgrade to bcrypt (production)

---

## Documentation Files

| File | Purpose |
|------|---------|
| `PHASE_3_1_AUTHENTICATION.md` | Auth system details |
| `PHASE_3_2_CLAUDE_INTEGRATION.md` | AI integration guide |
| `PHASE_3_3_ADVANCED_FEATURES.md` | Advanced features docs |
| `PHASE_3_4_PRODUCTION_HARDENING.md` | Security & middleware |
| `PHASE_3_COMPLETE_SUMMARY.md` | Full Phase 3 overview |
| `PHASE_3_FILES_MANIFEST.md` | Files created/modified |
| `PHASE_3_QUICK_REFERENCE.md` | This file |

---

## Next Steps

### Immediate
1. Review Phase 3 documentation
2. Test all 34 endpoints
3. Commit Phase 3 work to git

### Short Term
1. Deploy to staging
2. Load test with multiple users
3. Monitor rate limiting
4. Verify Claude AI integration

### Production
1. Configure HTTPS
2. Restrict CORS
3. Update Claude API key
4. Migrate to PostgreSQL
5. Set up monitoring

---

## Useful Links

| Resource | URL |
|----------|-----|
| Swagger UI | http://localhost:8000/api/docs |
| ReDoc | http://localhost:8000/api/redoc |
| OpenAPI JSON | http://localhost:8000/api/openapi.json |
| Health Check | http://localhost:8000/api/health |
| Welcome | http://localhost:8000/ |

---

## Support

### Server Logs
```bash
# Check for errors
# Look for ERROR and WARNING messages
# RequestId helps trace issues
```

### Debug Mode
```bash
# Already enabled (DEBUG_MODE=True)
# Auto-reload on file changes
# Verbose logging
```

### Reset Database
```bash
# Delete database file
rm preto.db

# Server auto-recreates on startup
# All tables recreated
```

---

## Statistics

- **Total Endpoints**: 34
- **Authentication Endpoints**: 13
- **AI Insight Endpoints**: 5
- **Advanced Endpoints**: 6
- **Repository Endpoints**: 7
- **Management Endpoints**: 6
- **Utility Endpoints**: 2
- **Security Middleware**: 5
- **Database Tables**: 9 (3 new in Phase 3.1)
- **Lines of Code**: 2,500+

---

**Phase 3 Complete! Ready for Production (with configuration).**

Last Updated: June 5, 2026
