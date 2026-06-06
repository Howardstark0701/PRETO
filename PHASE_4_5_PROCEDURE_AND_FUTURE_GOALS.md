# PRETO Phase 4 and Phase 5 Procedure Record

**Date:** June 6, 2026  
**Status:** Phase 4 and Phase 5 implementation recorded  
**Scope:** Advanced security, API keys, rate limiting, production database/cache support, Docker deployment, CI records, and future goals for Phase 6 and Phase 7.

---

## Executive Summary

Phase 4 moved PRETO from basic user authentication toward production-grade access control. The main upgrades were bcrypt password hashing, API key management, combined Bearer/API-key authentication, and per-user rate-limit tracking.

Phase 5 prepared the platform for production scaling. The main upgrades were PostgreSQL support, Redis-backed caching with in-memory fallback, Docker deployment files, production compose services, and CI workflow records.

The server was already verified alive during this session at:

```text
GET http://127.0.0.1:8000/api/health
```

The response returned `status: healthy`, confirming the API process was running after the previous middleware simplification work.

---

## Phase 4: Advanced Security and API Access

### Goal

Strengthen PRETO authentication and make the API usable by scripts, integrations, and future clients without requiring username/password login for every request.

### Procedure Completed

1. Upgraded password hashing in `app/api/auth.py`.
   - Replaced simple SHA256 password hashing with bcrypt.
   - Added bcrypt salt generation through `bcrypt.gensalt()`.
   - Added password verification through `bcrypt.checkpw()`.
   - Kept a legacy SHA256 fallback so existing users can still log in during migration.
   - Added automatic migration intent for legacy hashes after successful login.

2. Added API key data model in `app/models/auth.py`.
   - Created `APIKey` model.
   - Stored only hashed API keys, not raw keys.
   - Added display prefix for key identification.
   - Added per-key `rate_limit`.
   - Added active/inactive status.
   - Added `created_at`, `last_used`, and optional `expires_at`.
   - Added index for user API key lookup.

3. Added API key utilities in `app/api/auth.py`.
   - `create_api_key()` generates `pto_` prefixed API keys.
   - `verify_api_key()` validates key hash, active state, expiration, and user status.
   - `get_user_api_keys()` lists stored key metadata.
   - `delete_api_key()` removes a key owned by the current user.
   - `toggle_api_key()` enables or disables a key.
   - `get_api_key_user()` supports `X-API-Key` authentication.
   - `get_authenticated_user()` accepts either Bearer token or API key.

4. Added API key endpoints in `app/api/auth_routes.py`.
   - `POST /api/auth/api-keys`
   - `GET /api/auth/api-keys`
   - `DELETE /api/auth/api-keys/{key_id}`
   - `POST /api/auth/api-keys/{key_id}/toggle`
   - `GET /api/auth/verify-auth`

5. Added per-user rate-limit status foundation.
   - Implemented `UserRateLimiter`.
   - Added one-minute request window tracking.
   - Added helpers for allowed/remaining/reset status.
   - Added `GET /api/auth/rate_limit`.

### Phase 4 Files Touched

```text
app/api/auth.py
app/api/auth_routes.py
app/models/auth.py
requirements.txt
```

### Phase 4 Result

PRETO now has stronger password storage, programmatic API access, API key lifecycle management, and the foundation for per-user rate-limit enforcement.

---

## Phase 5: Scaling and Production Deployment

### Goal

Prepare PRETO to run beyond local SQLite/in-memory development mode by adding production database/cache backends and container deployment records.

### Procedure Completed

1. Added PostgreSQL support in `app/models/database.py`.
   - `DATABASE_URL` now controls the database backend.
   - SQLite remains the default for local development.
   - PostgreSQL is used automatically when `DATABASE_URL` contains `postgresql`.
   - Added production pool settings:
     - `POSTGRES_POOL_SIZE`
     - `POSTGRES_MAX_OVERFLOW`
     - `POSTGRES_POOL_PRE_PING`
   - Added `get_db_url_safe()` to display database URLs with masked passwords.

2. Added Redis cache support in `app/api/cache.py`.
   - `REDIS_URL` controls whether Redis is used.
   - If Redis is not configured, cache falls back to the existing in-memory backend.
   - Added Redis get/set/delete operations.
   - Added pattern invalidation for Redis and memory.
   - Added Redis stats reporting.
   - Added Redis clear-all operation.
   - Kept TTL behavior for user repos, search, stats, and repo details.

3. Added production dependency records in `requirements.txt`.
   - PostgreSQL driver: `psycopg2-binary`.
   - Redis client: `redis`.
   - bcrypt: `bcrypt`.
   - production server support: `gunicorn`.
   - Docker/runtime-friendly dependency list for the API.

4. Added Docker deployment files.
   - `Dockerfile` builds a production image.
   - Uses Python 3.10 slim.
   - Installs PostgreSQL build/runtime support.
   - Copies application code.
   - Creates and runs as non-root `preto` user.
   - Adds container health check against `/api/health`.

5. Added Docker Compose records.
   - `docker-compose.yml` supports local containerized API usage with SQLite.
   - `docker-compose.prod.yml` supports production-style API, PostgreSQL, Redis, and optional Nginx.
   - PostgreSQL service includes health check.
   - Redis service includes persistence and health check.
   - API service waits for healthy database and started Redis.

6. Added CI workflow record.
   - `.github/workflows/ci.yml`
   - Installs dependencies.
   - Runs lint check.
   - Runs tests.
   - Builds Docker image.
   - Runs container health check.
   - Adds security scan steps.

### Phase 5 Files Touched

```text
app/api/cache.py
app/models/database.py
requirements.txt
Dockerfile
docker-compose.yml
docker-compose.prod.yml
.github/workflows/ci.yml
```

### Phase 5 Result

PRETO now has a clear path from local SQLite/in-memory operation to production PostgreSQL/Redis deployment using Docker and CI records.

---

## Important Current Notes

1. Generated files should not be treated as source records.
   - `__pycache__` changes are runtime artifacts.
   - `preto.db` changes are local database state.
   - These should normally stay out of Phase 4/5 source commits unless there is a specific reason to version sample database state.

2. `docker-compose.prod.yml` references optional Nginx files.
   - `nginx.conf` and `ssl/` are expected if the Nginx service is used.
   - A future phase should either add these files or document Nginx as optional/commented.

3. CI references `tests/`.
   - The repository currently has root-level test scripts.
   - A future phase should normalize tests into a `tests/` directory or adjust the CI command.

4. Secrets need production hardening.
   - `SECRET_KEY` is still hardcoded in the auth utility.
   - Phase 6 should move it into environment configuration and add rotation guidance.

---

## Phase 6 Future Goals: Monitoring, Reliability, and Security Hardening

### Main Goal

Make PRETO observable, reliable, and safer for long-running production use.

### Recommended Phase 6 Tasks

1. Add structured logging.
   - Request IDs in every log line.
   - JSON logs for container environments.
   - Redaction for tokens, API keys, and passwords.

2. Add metrics and monitoring.
   - Prometheus metrics endpoint.
   - Request count, latency, error rate, cache hit rate, DB connection stats.
   - Grafana dashboard templates.

3. Add alerting.
   - Health check failures.
   - High 5xx rate.
   - Redis/PostgreSQL connection failures.
   - GitHub/NIM API failure spikes.

4. Finish rate-limit enforcement.
   - Apply per-user/API-key rate limiting to protected endpoints.
   - Move distributed rate limits into Redis for multi-container deployments.
   - Return standard `X-RateLimit-*` headers.

5. Harden authentication.
   - Move `SECRET_KEY` to environment variables.
   - Add key rotation process.
   - Add optional OAuth2 provider support.
   - Add admin-only API key oversight endpoints.

6. Normalize tests.
   - Move tests into `tests/`.
   - Add test fixtures for SQLite.
   - Add API key tests.
   - Add Redis fallback tests.
   - Add PostgreSQL integration test profile.

7. Improve deployment safety.
   - Add `.dockerignore`.
   - Add production environment template.
   - Remove hardcoded production passwords from compose examples.
   - Add migration strategy for schema changes.

### Phase 6 Completion Criteria

```text
- CI passes on every commit.
- Health, metrics, and logs are production-readable.
- API key and user rate limits are enforced.
- Secrets are environment-driven.
- Docker production deploy has documented, non-hardcoded secrets.
```

---

## Phase 7 Future Goals: Product Layer and Client Experience

### Main Goal

Turn PRETO from a backend-first API into a usable intelligence product with client workflows, reports, and operator-friendly surfaces.

### Recommended Phase 7 Tasks

1. Build a frontend dashboard.
   - Repository search workspace.
   - Saved searches.
   - Search history.
   - Analytics views.
   - User/API key management.

2. Add report workflows.
   - Export analysis to PDF/CSV/JSON.
   - Scheduled reports.
   - Shareable report links with access controls.

3. Add advanced OSINT workflows.
   - Watchlists for users/repos/topics.
   - Change detection over time.
   - Risk scoring.
   - Trend dashboards.

4. Add team features.
   - Organizations/workspaces.
   - Role-based access control.
   - Shared saved searches.
   - Audit log for sensitive actions.

5. Add client SDKs or examples.
   - Python API client.
   - JavaScript examples.
   - API key usage examples.
   - Postman/Bruno collection.

6. Add deployment polish.
   - Hosted demo profile.
   - Seed data mode.
   - Admin setup command.
   - Production onboarding guide.

### Phase 7 Completion Criteria

```text
- Users can operate PRETO without directly calling raw API endpoints.
- Reports and saved workflows are usable from a UI.
- API keys and account settings are manageable through the product surface.
- The project has demo, docs, and onboarding flow ready for external users.
```

---

## Suggested Commit Scope

Stage and commit the intentional source/config/documentation records:

```text
app/api/auth.py
app/api/auth_routes.py
app/api/cache.py
app/models/auth.py
app/models/database.py
requirements.txt
Dockerfile
docker-compose.yml
docker-compose.prod.yml
.github/workflows/ci.yml
PHASE_4_5_PROCEDURE_AND_FUTURE_GOALS.md
```

Avoid committing generated runtime artifacts unless explicitly required:

```text
__pycache__/
preto.db
```

Suggested commit message:

```text
Phase 4-5: Advanced security and production scaling

- Add bcrypt password hashing and legacy migration path
- Add API key model, utilities, and management endpoints
- Add per-user rate-limit status foundation
- Add PostgreSQL database configuration support
- Add Redis cache backend with memory fallback
- Add Docker, production compose, CI, and phase documentation
```

---

## Final Status

Phase 4 and Phase 5 are recorded as implementation-complete from the current workspace state. Phase 6 should focus on observability, security hardening, testing, and operational reliability. Phase 7 should focus on dashboard/product workflows, reporting, team features, and external usability.
