"""
PRETO - Open-source OSINT and Public Data Analytics Platform
FastAPI Application Entry Point

Phase 2: Building REST API with database persistence

Author: TANGO
Last Updated: June 5, 2026
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
import os

from app.api.routes import router as repos_router

# Load environment variables from .env
load_dotenv()

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

# Include routers
app.include_router(repos_router)


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Simple health check endpoint to verify API is running.
    
    Returns:
        dict: Status and timestamp
    """
    return {
        "status": "healthy",
        "message": "PRETO API is running",
        "version": "0.2.0"
    }


# Welcome endpoint
@app.get("/")
async def root():
    """
    Welcome endpoint with API information.
    
    Returns:
        dict: Welcome message and API documentation links
    """
    return {
        "name": "PRETO",
        "description": "Open-source OSINT and Public Data Analytics Platform",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "health": "/api/health"
    }


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
