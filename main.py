"""
PRETO - Open-source OSINT and Public Data Analytics Platform
FastAPI Application Entry Point

Phase 2: Building REST API with database persistence

Author: TANGO
Last Updated: June 5, 2026
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
import os
import logging
import asyncio

from app.api.logging_config import configure_logging
from app.api.routes import router as repos_router
from app.api.auth_routes import router as auth_router
from app.api.insights_routes import router as insights_router
from app.api.advanced_routes import router as advanced_router
from app.api.dashboard import router as dashboard_router
from app.models import init_db
from app.api.scheduler import get_scheduler, init_scheduler, shutdown_scheduler
from app.api.sync import background_cache_maintenance, background_get_stats
from app.api.middleware import CombinedMiddleware
from app.api.metrics import metrics_collector


# Configure logging
configure_logging()
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize database
logger.info("Initializing database...")
init_db()
logger.info("Database initialized successfully")


# Initialize FastAPI application
app = FastAPI(
    title="PRETO API",
    description="Open-source OSINT and Public Data Analytics Platform",
    version="0.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Production Hardening Middleware (Phase 3.4)
# ============================================================================
# Combined middleware that handles all middleware in a single class to avoid
# async/await initialization issues with multiple middleware layers.

app.add_middleware(CombinedMiddleware, requests_per_minute=100, current_version="v1")

# Include routers
app.include_router(repos_router)
app.include_router(auth_router)
app.include_router(insights_router)
app.include_router(advanced_router)
app.include_router(dashboard_router)


# ============================================================================
# Application Lifecycle Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Initialize scheduler and background tasks on application startup.
    """
    try:
        logger.info("Starting up PRETO API...")
        
        # Initialize scheduler with background tasks
        jobs = {
            'cache_maintenance': (
                background_cache_maintenance,
                30,  # Run every 30 minutes
                'Clean up expired cache entries'
            ),
            'database_stats': (
                background_get_stats,
                60,  # Run every 60 minutes
                'Collect database statistics'
            )
        }
        
        await init_scheduler(jobs)
        logger.info("Scheduler initialized with background tasks")
        
        scheduler = get_scheduler()
        logger.info(f"Scheduler stats: {scheduler.get_stats()}")
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup resources on application shutdown.
    """
    try:
        logger.info("Shutting down PRETO API...")
        
        # Stop scheduler
        await shutdown_scheduler()
        logger.info("Scheduler stopped")
        
        logger.info("PRETO API shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)


# ============================================================================
# Global Exception Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for all unhandled exceptions.
    Logs error and returns structured response.
    """
    import traceback
    print(f"🔥 EXCEPTION: {type(exc).__name__}: {exc}")  # add this
    traceback.print_exc()  # add this

    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "status_code": 500,
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handler for validation errors."""
    logger.warning(f"Validation error: {str(exc)}")
    
    return JSONResponse(
        status_code=400,
        content={
            "status_code": 400,
            "error": "Validation Error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Health check endpoint
@app.get("/api/health", tags=["health"])
async def health_check():
    """
    Simple health check endpoint to verify API is running.
    
    Returns:
        dict: Status and timestamp
    """
    try:
        logger.info("Health check requested")
        return {
            "status": "healthy",
            "message": "PRETO API is running",
            "version": "0.2.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": "PRETO API encountered an error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }, 500


@app.get("/api/metrics", tags=["monitoring"], response_class=PlainTextResponse)
async def metrics():
    """Prometheus-compatible request metrics."""
    return PlainTextResponse(metrics_collector.to_prometheus(), media_type="text/plain")


# Welcome endpoint
@app.get("/", tags=["info"])
async def root():
    """
    Welcome endpoint with API information.
    
    Returns:
        dict: Welcome message and API documentation links
    """
    try:
        logger.info("Welcome endpoint accessed")
        return {
            "name": "PRETO",
            "description": "Open-source OSINT and Public Data Analytics Platform",
            "version": "0.2.0",
            "docs": "/api/docs",
            "redoc": "/api/redoc",
            "health": "/api/health",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Welcome endpoint error: {str(e)}")
        return {
            "error": "Unable to process request",
            "message": str(e)
        }, 500


# Planned REST Endpoints
"""
✅ Implemented in Phase 2:
   - GET /api/repos/user/{username}        → Get all repos for a user
   - GET /api/repos/search                 → Search repos by query + language
   - GET /api/repos/{owner}/{repo_name}    → Get specific repo details
   - GET /api/repos/user/{username}/stats  → Get user statistics

📋 To be implemented in Phase 3+:
   - POST /api/search                      → Save searches
   - GET /api/search/{search_id}           → Get saved search
   - GET /api/insights/analyze             → Claude-powered analysis
   - POST /api/insights/query              → Natural language queries
"""


# Run the application
if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment or use defaults
    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", 8000))
    reload = os.getenv("DEBUG_MODE", "True").lower() == "true"
    
    print(f"""
    ╔════════════════════════════════════════╗
    ║          PRETO API Starting            ║
    ║  Open-source OSINT Analytics Platform  ║
    ╚════════════════════════════════════════╝
    
    📍 Server: http://{host}:{port}
    📚 Docs:   http://{host}:{port}/api/docs
    🔄 Reload: {reload}
    """)
    
    # Start the uvicorn development server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
