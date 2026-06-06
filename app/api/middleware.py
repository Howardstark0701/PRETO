"""
Middleware and Production Hardening for PRETO

Phase 3.4 + Phase 6 (Observability): Combined middleware with metrics integration.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from threading import Lock
from typing import Dict

import logging

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.api.metrics import metrics_collector

logger = logging.getLogger(__name__)


class CombinedMiddleware:
    """
    Single ASGI middleware handling:
      - Request ID injection
      - Security headers
      - API version validation
      - Per-IP rate limiting
      - Error logging
      - Prometheus metrics recording
    """

    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 100,
        current_version: str = "v1",
    ) -> None:
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.current_version = current_version
        self.supported_versions = ["v1"]
        self._rate_requests: Dict[str, list] = defaultdict(list)
        self._lock = Lock()
        self._counter = 0

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start = metrics_collector.now()

        # ── Request ID ────────────────────────────────────────────────
        with self._lock:
            self._counter += 1
            request_id = f"{datetime.utcnow().timestamp()}-{self._counter}"

        # ── Rate limiting ─────────────────────────────────────────────
        client_ip = (request.client.host if request.client else "unknown")
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)

        with self._lock:
            self._rate_requests[client_ip] = [
                t for t in self._rate_requests[client_ip] if t > cutoff
            ]
            current_count = len(self._rate_requests[client_ip])

            if current_count >= self.requests_per_minute:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                response = JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded. Maximum requests per minute exceeded."},
                )
                await response(scope, receive, send)
                return

            self._rate_requests[client_ip].append(now)
            remaining_slots = self.requests_per_minute - current_count - 1

        # ── API version check ─────────────────────────────────────────
        version = request.headers.get("X-API-Version", self.current_version)
        if version not in self.supported_versions:
            logger.warning(f"Unsupported API version: {version}")
            response = JSONResponse(
                status_code=400,
                content={"error": f"Unsupported API version: {version}. Supported: {self.supported_versions}"},
            )
            await response(scope, receive, send)
            return

        # ── Wrap send to inject headers + record metrics ───────────────
        status_code_holder: list[int] = [200]

        async def send_with_extras(message: dict) -> None:
            if message["type"] == "http.response.start":
                status_code_holder[0] = message.get("status", 200)
                headers = dict(message.get("headers", []))

                headers[b"x-request-id"]          = request_id.encode()
                headers[b"x-api-version"]          = version.encode()
                headers[b"x-content-type-options"] = b"nosniff"
                headers[b"x-frame-options"]        = b"DENY"
                headers[b"x-xss-protection"]       = b"1; mode=block"
                headers[b"x-ratelimit-limit"]      = str(self.requests_per_minute).encode()
                headers[b"x-ratelimit-remaining"]  = str(remaining_slots).encode()
                headers.pop(b"server", None)
                headers.pop(b"x-powered-by", None)

                if status_code_holder[0] >= 400:
                    logger.warning(f"{request.method} {request.url.path} - {status_code_holder[0]}")

                message = {
                    "type": "http.response.start",
                    "status": status_code_holder[0],
                    "headers": list(headers.items()),
                }

            await send(message)

        # ── Call inner app ────────────────────────────────────────────
        try:
            await self.app(scope, receive, send_with_extras)
        except Exception as exc:
            logger.error(f"Middleware caught unhandled exception: {request.method} {request.url.path} - {exc}")
            raise
        finally:
            duration = metrics_collector.now() - start
            metrics_collector.record_request(
                method=request.method,
                path=request.url.path,
                status_code=status_code_holder[0],
                duration=duration,
            )


# ── Stubs kept for import compatibility ──────────────────────────────────────
from starlette.middleware.base import BaseHTTPMiddleware  # noqa: E402


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        return await call_next(request)


class APIVersionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, current_version: str = "v1"):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        return await call_next(request)


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        return await call_next(request)


class RequestIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        return await call_next(request)




















# """

# Middleware and Production Hardening for PRETO

# Phase 3.4: Production Hardening
# """

# from fastapi import Request, HTTPException, status
# from fastapi.responses import JSONResponse
# from starlette.middleware.base import BaseHTTPMiddleware
# from datetime import datetime, timedelta
# import logging
# from typing import Dict
# from uuid import uuid4

# from app.api.metrics import metrics_collector

# logger = logging.getLogger(__name__)


# class RateLimitMiddleware(BaseHTTPMiddleware):
#     """Rate limiting middleware."""
    
#     def __init__(self, app, requests_per_minute: int = 100):
#         super().__init__(app)
#         self.requests_per_minute = requests_per_minute
#         self.requests: Dict[str, list] = {}
    
#     async def dispatch(self, request: Request, call_next):
#         """Apply rate limiting."""
#         client_ip = request.client.host if request.client else "unknown"
        
#         now = datetime.utcnow()
#         minute_ago = now - timedelta(minutes=1)
        
#         # Initialize or clean requests for this IP
#         if client_ip not in self.requests:
#             self.requests[client_ip] = []
        
#         # Remove old requests
#         self.requests[client_ip] = [
#             req_time for req_time in self.requests[client_ip]
#             if req_time > minute_ago
#         ]
        
#         # Check rate limit
#         if len(self.requests[client_ip]) >= self.requests_per_minute:
#             logger.warning(f"Rate limit exceeded for IP: {client_ip}")
#             raise HTTPException(
#                 status_code=status.HTTP_429_TOO_MANY_REQUESTS,
#                 detail="Rate limit exceeded. Maximum requests per minute exceeded."
#             )
        
#         # Add current request
#         self.requests[client_ip].append(now)
        
#         # Process request
#         response = await call_next(request)
        
#         # Add rate limit headers
#         response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
#         response.headers["X-RateLimit-Remaining"] = str(
#             self.requests_per_minute - len(self.requests[client_ip])
#         )
#         response.headers["X-RateLimit-Reset"] = str(
#             int((minute_ago + timedelta(minutes=1)).timestamp())
#         )
        
#         return response


# class SecurityHeadersMiddleware(BaseHTTPMiddleware):
#     """Add security headers to responses."""
    
#     async def dispatch(self, request: Request, call_next):
#         """Add security headers."""
#         response = await call_next(request)
        
#         # Security headers
#         response.headers["X-Content-Type-Options"] = "nosniff"
#         response.headers["X-Frame-Options"] = "DENY"
#         response.headers["X-XSS-Protection"] = "1; mode=block"
#         response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
#         response.headers["Content-Security-Policy"] = "default-src 'self'"
        
#         # Remove sensitive headers
#         response.headers.pop("Server", None)
#         response.headers.pop("X-Powered-By", None)
        
#         return response


# class APIVersionMiddleware(BaseHTTPMiddleware):
#     """Handle API versioning."""
    
#     def __init__(self, app, current_version: str = "v1"):
#         super().__init__(app)
#         self.current_version = current_version
#         self.supported_versions = ["v1"]
    
#     async def dispatch(self, request: Request, call_next):
#         """Handle versioning."""
#         # Extract version from header or URL
#         version = request.headers.get("X-API-Version", self.current_version)
        
#         if version not in self.supported_versions:
#             logger.warning(f"Unsupported API version: {version}")
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"Unsupported API version: {version}. Supported: {self.supported_versions}"
#             )
        
#         request.state.api_version = version
        
#         response = await call_next(request)
#         response.headers["X-API-Version"] = version
        
#         return response


# class ErrorLoggingMiddleware(BaseHTTPMiddleware):
#     """Log errors and exceptions."""
    
#     async def dispatch(self, request: Request, call_next):
#         """Log request and errors."""
#         try:
#             response = await call_next(request)
            
#             # Log errors
#             if response.status_code >= 400:
#                 logger.warning(
#                     f"{request.method} {request.url.path} - {response.status_code}"
#                 )
            
#             return response
        
#         except Exception as exc:
#             logger.error(
#                 f"Unhandled exception: {request.method} {request.url.path} - {str(exc)}"
#             )
#             raise


# class RequestIdMiddleware(BaseHTTPMiddleware):
#     """Add request IDs for tracing."""
    
#     def __init__(self, app):
#         super().__init__(app)
#         self.counter = 0
    
#     async def dispatch(self, request: Request, call_next):
#         """Add request ID."""
#         self.counter += 1
#         request_id = f"{datetime.utcnow().timestamp()}-{self.counter}"
        
#         request.state.request_id = request_id
        
#         response = await call_next(request)
#         response.headers["X-Request-ID"] = request_id
        
#         return response


# class CombinedMiddleware(BaseHTTPMiddleware):
#     """
#     Combined middleware that runs all middleware in a single class to avoid
#     async/await initialization issues.
#     """
    
#     def __init__(self, app, requests_per_minute: int = 100, current_version: str = "v1"):
#         super().__init__(app)
#         self.requests_per_minute = requests_per_minute
#         self.current_version = current_version
#         self.counter = 0
    
#     async def dispatch(self, request: Request, call_next):
#         """Execute all middleware logic in sequence."""
#         start = metrics_collector.now()
#         status_code = 500
#         try:
#             # Add request ID
#             self.counter += 1
#             request_id = request.headers.get("X-Request-ID") or str(uuid4())
#             request.state.request_id = request_id
            
#             # Call next handler
#             response = await call_next(request)
#             status_code = response.status_code
            
#             # Add security headers
#             response.headers["X-Request-ID"] = request_id
#             response.headers["X-Content-Type-Options"] = "nosniff"
#             response.headers["X-Frame-Options"] = "DENY"
#             response.headers["X-XSS-Protection"] = "1; mode=block"
            
#             return response
        
#         except Exception as exc:
#             status_code = getattr(exc, "status_code", 500)
#             logger.error(f"Middleware error: {str(exc)}", exc_info=True)
#             if isinstance(exc, HTTPException):
#                 headers = dict(exc.headers or {})
#                 headers["X-Request-ID"] = getattr(request.state, "request_id", "")
#                 return JSONResponse(
#                     status_code=exc.status_code,
#                     content={"detail": exc.detail},
#                     headers=headers,
#                 )
#             raise
#         finally:
#             duration = metrics_collector.now() - start
#             metrics_collector.record_request(
#                 request.method,
#                 request.url.path,
#                 status_code,
#                 duration,
#             )
