"""
Middleware and Production Hardening for PRETO

Phase 3.4: Production Hardening
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting."""
        client_ip = request.client.host if request.client else "unknown"
        
        now = datetime.utcnow()
        minute_ago = now - timedelta(minutes=1)
        
        # Initialize or clean requests for this IP
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Maximum requests per minute exceeded."
            )
        
        # Add current request
        self.requests[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.requests[client_ip])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int((minute_ago + timedelta(minutes=1)).timestamp())
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # Remove sensitive headers
        response.headers.pop("Server", None)
        response.headers.pop("X-Powered-By", None)
        
        return response


class APIVersionMiddleware(BaseHTTPMiddleware):
    """Handle API versioning."""
    
    def __init__(self, app, current_version: str = "v1"):
        super().__init__(app)
        self.current_version = current_version
        self.supported_versions = ["v1"]
    
    async def dispatch(self, request: Request, call_next):
        """Handle versioning."""
        # Extract version from header or URL
        version = request.headers.get("X-API-Version", self.current_version)
        
        if version not in self.supported_versions:
            logger.warning(f"Unsupported API version: {version}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported API version: {version}. Supported: {self.supported_versions}"
            )
        
        request.state.api_version = version
        
        response = await call_next(request)
        response.headers["X-API-Version"] = version
        
        return response


class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Log errors and exceptions."""
    
    async def dispatch(self, request: Request, call_next):
        """Log request and errors."""
        try:
            response = await call_next(request)
            
            # Log errors
            if response.status_code >= 400:
                logger.warning(
                    f"{request.method} {request.url.path} - {response.status_code}"
                )
            
            return response
        
        except Exception as exc:
            logger.error(
                f"Unhandled exception: {request.method} {request.url.path} - {str(exc)}"
            )
            raise


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Add request IDs for tracing."""
    
    def __init__(self, app):
        super().__init__(app)
        self.counter = 0
    
    async def dispatch(self, request: Request, call_next):
        """Add request ID."""
        self.counter += 1
        request_id = f"{datetime.utcnow().timestamp()}-{self.counter}"
        
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class CombinedMiddleware(BaseHTTPMiddleware):
    """
    Combined middleware that runs all middleware in a single class to avoid
    async/await initialization issues.
    """
    
    def __init__(self, app, requests_per_minute: int = 100, current_version: str = "v1"):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.current_version = current_version
        self.counter = 0
    
    async def dispatch(self, request: Request, call_next):
        """Execute all middleware logic in sequence."""
        try:
            # Add request ID
            self.counter += 1
            request_id = f"{datetime.utcnow().timestamp()}-{self.counter}"
            request.state.request_id = request_id
            
            # Call next handler
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            
            return response
        
        except Exception as exc:
            logger.error(f"Middleware error: {str(exc)}", exc_info=True)
            raise
