# Task 1.5: Error Handling Implementation Guide

**Date:** June 5, 2026  
**Status:** ✅ COMPLETE  
**Version:** 0.2.0

---

## Overview

Comprehensive error handling has been implemented across all API endpoints to ensure:
- ✅ Proper HTTP status codes for all scenarios
- ✅ Input validation on all parameters
- ✅ Structured error responses
- ✅ Logging for debugging
- ✅ Global exception handling
- ✅ Graceful error degradation

---

## HTTP Status Codes Reference

| Code | Name | When Used | Example |
|------|------|-----------|---------|
| **200** | OK | Request successful | Repos retrieved successfully |
| **400** | Bad Request | Invalid input parameters | Empty username, invalid per_page |
| **404** | Not Found | Resource doesn't exist | User not found, repo not found |
| **502** | Bad Gateway | GitHub API error | API returns error response |
| **504** | Gateway Timeout | Request takes too long | Timeout exceeds 15 seconds |
| **500** | Internal Error | Unexpected server error | Unhandled exception |

---

## Error Response Format

All error responses follow a consistent structure:

```json
{
  "status_code": 400,
  "error": "Validation Error",
  "detail": "Search query cannot be empty",
  "timestamp": "2026-06-05T12:34:56.789012"
}
```

**Fields:**
- `status_code` - HTTP status code
- `error` - Error category (short name)
- `detail` - Detailed error message (user-friendly)
- `timestamp` - When error occurred (ISO format)

---

## Endpoint Error Handling

### 1. GET /api/repos/user/{username}

**Valid Inputs:**
- `username` - Non-empty string, max 39 chars (GitHub limit)
- `per_page` - Integer 1-100 (default 30)

**Possible Errors:**

| Condition | Status | Response |
|-----------|--------|----------|
| Empty username | 400 | "Username cannot be empty" |
| Username > 39 chars | 400 | "Username must be a string of max 39 characters" |
| Invalid per_page | 400 | "per_page must be between 1 and 100" |
| User not found | 404 | "User '{username}' not found on GitHub..." |
| API timeout | 504 | "Request timed out while fetching repositories..." |
| GitHub API error | 502 | "GitHub API error: {error details}" |

**Example Error Response:**
```bash
curl -X GET "http://localhost:8000/api/repos/user/"

{
  "status_code": 400,
  "error": "Validation Error",
  "detail": "Username cannot be empty",
  "timestamp": "2026-06-05T12:34:56.789012"
}
```

---

### 2. GET /api/repos/search

**Valid Inputs:**
- `query` - Non-empty string, 1-256 characters (required)
- `language` - Optional, max 50 characters
- `per_page` - Integer 1-100 (default 30)

**Possible Errors:**

| Condition | Status | Response |
|-----------|--------|----------|
| Empty query | 400 | "Search query cannot be empty" |
| Query > 256 chars | 400 | "Query must be 256 characters or less" |
| Invalid language | 400 | "Language filter must be 50 characters or less" |
| Invalid per_page | 400 | "per_page must be between 1 and 100" |
| No results found | 404 | "No repositories found matching: '{query}'" |
| API timeout | 504 | "Search request timed out..." |
| GitHub API error | 502 | "GitHub API error during search: {error}" |

**Example Error Response:**
```bash
curl -X GET "http://localhost:8000/api/repos/search?query=&language=python"

{
  "status_code": 400,
  "error": "Validation Error",
  "detail": "Search query cannot be empty",
  "timestamp": "2026-06-05T12:34:56.789012"
}
```

---

### 3. GET /api/repos/{owner}/{repo_name}

**Valid Inputs:**
- `owner` - Non-empty username, max 39 chars
- `repo_name` - Non-empty string, max 255 chars

**Possible Errors:**

| Condition | Status | Response |
|-----------|--------|----------|
| Empty owner | 400 | "Repository owner cannot be empty" |
| Empty repo_name | 400 | "Repository name cannot be empty" |
| Invalid format | 400 | "Invalid owner or repository name format" |
| Repository not found | 404 | "Repository '{owner}/{repo_name}' not found" |
| API timeout | 504 | "Request timed out while fetching repository details" |
| GitHub API error | 502 | "GitHub API error: {error details}" |

**Example Error Response:**
```bash
curl -X GET "http://localhost:8000/api/repos/torvalds/"

{
  "status_code": 400,
  "error": "Validation Error",
  "detail": "Repository name cannot be empty",
  "timestamp": "2026-06-05T12:34:56.789012"
}
```

---

### 4. GET /api/repos/user/{username}/stats

**Valid Inputs:**
- `username` - Non-empty string, max 39 chars

**Possible Errors:**

| Condition | Status | Response |
|-----------|--------|----------|
| Empty username | 400 | "Username cannot be empty" |
| Username > 39 chars | 400 | "Username must be 39 characters or less" |
| User not found | 404 | "User '{username}' not found on GitHub..." |
| API timeout | 504 | "Request timed out while fetching statistics..." |
| GitHub API error | 502 | "GitHub API error: {error details}" |

**Example Error Response:**
```bash
curl -X GET "http://localhost:8000/api/repos/user/invalid%20name/stats"

{
  "status_code": 400,
  "error": "Validation Error",
  "detail": "Username must be 39 characters or less",
  "timestamp": "2026-06-05T12:34:56.789012"
}
```

---

### 5. GET /api/health

**No input parameters**

**Possible Errors:**

| Condition | Status | Response |
|-----------|--------|----------|
| Unexpected error | 500 | Returns status: "unhealthy" |

---

### 6. GET /

**No input parameters**

**Possible Errors:**

| Condition | Status | Response |
|-----------|--------|----------|
| Unexpected error | 500 | Returns error message |

---

## Input Validation

### Parameter Validation Rules

#### Username
```python
# Validation:
- Must not be empty
- Must be a string
- Maximum length: 39 characters (GitHub limit)
- Pattern: alphanumeric + hyphens only

# Examples:
✅ Valid: "torvalds", "guido", "python-dev"
❌ Invalid: "", "a"*40, "user@domain"
```

#### Repository Name
```python
# Validation:
- Must not be empty
- Must be a string
- Maximum length: 255 characters
- Can contain hyphens, dots, underscores

# Examples:
✅ Valid: "linux", "flask-web", "node.js"
❌ Invalid: "", "r"*256
```

#### Search Query
```python
# Validation:
- Must not be empty
- Must be a string
- Length: 1-256 characters
- Can contain special characters

# Examples:
✅ Valid: "machine-learning", "web framework", "react+vue"
❌ Invalid: "", "x"*257
```

#### Language Filter
```python
# Validation:
- Optional (can be omitted)
- Must be a string if provided
- Maximum length: 50 characters

# Examples:
✅ Valid: "python", "javascript", "c++"
❌ Invalid: "x"*51
```

#### per_page
```python
# Validation:
- Must be an integer
- Range: 1-100 (inclusive)
- Default: 30

# Examples:
✅ Valid: 1, 30, 100
❌ Invalid: 0, -1, 101, "thirty"
```

---

## Logging

All endpoints log important events for debugging:

```python
# Example log messages:

# INFO level (important events)
logger.info(f"Fetching repositories for user: torvalds (per_page: 30)")
logger.info(f"Successfully retrieved 12 repositories for torvalds")
logger.info(f"Searching repos - query: 'machine-learning', language: python")

# WARNING level (validation failures)
logger.warning(f"Empty username provided")
logger.warning(f"User not found or has no public repositories: unknown_user_123")

# ERROR level (unexpected errors)
logger.error(f"Request timeout for user: torvalds", exc_info=True)
logger.error(f"Unexpected error fetching repos for torvalds: Connection refused")
```

**Log Format:**
```
2026-06-05 12:34:56,789 - app.api.routes - INFO - Fetching repositories for user: torvalds
```

**Viewing Logs:**
When you run the server with `python main.py`, logs appear in console:
```
2026-06-05 12:34:56.123456 - app.api.routes - INFO - Fetching repositories for user: torvalds
2026-06-05 12:34:56.234567 - app.api.routes - INFO - Successfully retrieved 12 repositories for torvalds
```

---

## Global Exception Handlers

### Main Exception Handler

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catches ALL unhandled exceptions and returns structured response.
    Status: 500 Internal Server Error
    """
```

**Triggers when:**
- Any uncaught exception occurs
- HTTPException is not handled by specific handler

**Response:**
```json
{
  "status_code": 500,
  "error": "Internal Server Error",
  "detail": "An unexpected error occurred. Please try again later.",
  "timestamp": "2026-06-05T12:34:56.789012"
}
```

### Validation Error Handler

```python
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Catches ValueError exceptions.
    Status: 400 Bad Request
    """
```

**Triggers when:**
- Value doesn't match expected type
- Invalid conversion attempted

---

## Error Handling Flow

```
User Request
    ↓
Parameter Validation
    ├─ Invalid? → 400 Error Response
    └─ Valid? → Continue
    ↓
Fetch from GitHub API (with timeout)
    ├─ Timeout? → 504 Error Response
    ├─ API Error? → 502 Error Response
    ├─ Not Found? → 404 Error Response
    └─ Success? → Continue
    ↓
Transform & Return Response
    ├─ Error? → 500 Error Response
    └─ Success? → 200 with Data
```

---

## Testing Error Scenarios

### Test 1: Empty Username

```bash
curl -X GET "http://localhost:8000/api/repos/user/" \
  -H "Accept: application/json"
```

**Expected Response:**
```
Status: 400
Body: {
  "status_code": 400,
  "error": "Validation Error",
  "detail": "Username cannot be empty"
}
```

---

### Test 2: Invalid per_page

```bash
curl -X GET "http://localhost:8000/api/repos/user/torvalds?per_page=150" \
  -H "Accept: application/json"
```

**Expected Response:**
```
Status: 400
Body: {
  "status_code": 400,
  "error": "Validation Error",
  "detail": "per_page must be between 1 and 100"
}
```

---

### Test 3: User Not Found

```bash
curl -X GET "http://localhost:8000/api/repos/user/nonexistent_user_xyz123" \
  -H "Accept: application/json"
```

**Expected Response:**
```
Status: 404
Body: {
  "status_code": 404,
  "error": "Not Found",
  "detail": "User 'nonexistent_user_xyz123' not found on GitHub or has no public repositories"
}
```

---

### Test 4: Valid Request

```bash
curl -X GET "http://localhost:8000/api/repos/user/torvalds?per_page=5" \
  -H "Accept: application/json"
```

**Expected Response:**
```
Status: 200
Body: {
  "username": "torvalds",
  "total_count": 5,
  "repos": [...],
  "cached": false,
  "last_updated": "2026-06-05T12:34:56.789012"
}
```

---

## Best Practices Implemented

✅ **Always validate input** - Check parameters before using them  
✅ **Return appropriate status codes** - 400 for validation, 404 for not found, 502 for API errors  
✅ **Provide clear error messages** - Users know what went wrong  
✅ **Log all errors** - For debugging and monitoring  
✅ **Use consistent error format** - Users expect same structure  
✅ **Add timeouts** - Prevent infinite hangs  
✅ **Graceful degradation** - Don't crash on first error  
✅ **Document errors** - Users know what to expect  

---

## Files Modified for Error Handling

### 1. `app/api/routes.py`
- ✅ Added logging module
- ✅ Added input validation to all endpoints
- ✅ Enhanced error messages
- ✅ Added timeout handling
- ✅ Improved exception catching

### 2. `main.py`
- ✅ Added Request import
- ✅ Added JSONResponse import
- ✅ Added logging configuration
- ✅ Added global exception handlers
- ✅ Enhanced health check endpoint
- ✅ Enhanced welcome endpoint

### 3. Supporting Files
- ✅ `app/scrapers/github_scraper.py` - Already has error handling
- ✅ `app/api/schemas.py` - Pydantic models handle validation

---

## Next Steps (Optional Enhancements)

For Phase 3, consider adding:

1. **Rate Limiting** - Limit requests per IP/user
2. **Request Logging** - Log all requests and responses
3. **Metrics** - Track error rates and response times
4. **Alerting** - Alert on critical errors
5. **Custom Error Codes** - More granular error classifications
6. **Error Recovery** - Automatic retry logic for transient failures
7. **Circuit Breaker** - Stop calling GitHub API if it's down

---

## Verification Checklist

- ✅ All endpoints have input validation
- ✅ All error scenarios return appropriate status codes
- ✅ Error messages are clear and user-friendly
- ✅ Logging configured on all endpoints
- ✅ Global exception handlers in place
- ✅ Timeout protection on all API calls
- ✅ Tests pass without errors
- ✅ Documentation complete

---

## Summary

**Task 1.5: Error Handling** is now **100% COMPLETE**.

All endpoints properly:
- Validate input parameters
- Handle errors gracefully
- Return appropriate HTTP status codes
- Provide structured error responses
- Log important events
- Protect against timeouts
- Give users clear feedback

The API is now **production-ready** for Phase 2 testing! 🚀

---

**Last Updated:** June 5, 2026  
**Author:** TANGO  
**Version:** 0.2.0  
**Status:** ✅ Complete & Verified
