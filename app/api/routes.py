"""
FastAPI routes/endpoints for GitHub scraper

Phase 2: REST API endpoints wrapping GitHubScraper

Author: TANGO
Last Updated: June 5, 2026
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import asyncio

from app.scrapers.github_scraper import GitHubScraper
from .schemas import (
    UserRepositoriesResponse,
    SearchResultsResponse,
    RepositoryResponse,
    ErrorResponse
)

# Create router for all GitHub-related endpoints
router = APIRouter(prefix="/api/repos", tags=["repositories"])

# Initialize GitHub scraper (no token for now, will be enhanced later)
scraper = GitHubScraper()


# ============================================================================
# User Repositories Endpoints
# ============================================================================

@router.get(
    "/user/{username}",
    response_model=UserRepositoriesResponse,
    summary="Get user repositories",
    description="Fetch all repositories for a given GitHub user with automatic pagination"
)
async def get_user_repos(
    username: str,
    per_page: int = Query(30, ge=1, le=100, description="Results per page")
):
    """
    Get repositories for a GitHub user.
    
    Args:
        username (str): GitHub username
        per_page (int): Results per page (default 30)
    
    Returns:
        UserRepositoriesResponse: User and their repositories data
    
    Status Codes:
        200: Success
        400: Invalid input
        502: GitHub API error
        504: Timeout
    """
    try:
        repos = await scraper.get_user_repos(username, per_page=per_page)
        
        return UserRepositoriesResponse(
            username=username,
            total_count=len(repos),
            repos=repos,
            cached=False,
            last_updated=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ============================================================================
# Search Repositories Endpoints
# ============================================================================

@router.get(
    "/search",
    response_model=SearchResultsResponse,
    summary="Search repositories",
    description="Search for repositories across GitHub by keyword with optional language filter"
)
async def search_repositories(
    query: str = Query(..., min_length=1, description="Search query"),
    language: Optional[str] = Query(None, description="Programming language filter"),
    per_page: int = Query(30, ge=1, le=100, description="Results per page")
):
    """
    Search for repositories on GitHub.
    
    Args:
        query: Search query (required, e.g., "machine-learning", "web framework")
        language: Optional programming language filter (e.g., "python", "javascript")
        per_page: Results per page (1-100, default 30)
    
    Returns:
        SearchResultsResponse: Top matching repositories sorted by stars
    
    Raises:
        HTTPException: 400 for invalid query, 500 for server errors
    
    Examples:
        GET /api/repos/search?query=machine-learning&language=python
        GET /api/repos/search?query=web framework
    """
    try:
        # Validate query
        if not query or len(query.strip()) < 1:
            raise HTTPException(
                status_code=400,
                detail="Search query cannot be empty"
            )
        
        # Search repositories
        repos = await scraper.search_repos(query, language=language, per_page=per_page)
        
        # Check if results found
        if not repos:
            raise HTTPException(
                status_code=404,
                detail=f"No repositories found matching query: '{query}'"
            )
        
        return SearchResultsResponse(
            query=query,
            language=language,
            per_page=per_page,
            total_count=len(repos),
            results=repos,
            cached=False,
            last_updated=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Search request timed out"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching repositories: {str(e)}"
        )


# ============================================================================
# Repository Details Endpoints
# ============================================================================

@router.get(
    "/{owner}/{repo_name}",
    summary="Get repository details",
    description="Get detailed information about a specific repository"
)
async def get_repository_details(
    owner: str,
    repo_name: str
):
    """
    Get detailed information about a specific repository.
    
    Args:
        owner: Repository owner username
        repo_name: Repository name
    
    Returns:
        RepositoryResponse: Detailed repository information
    
    Raises:
        HTTPException: 404 if repository not found, 500 for server errors
    
    Examples:
        GET /api/repos/torvalds/linux
        GET /api/repos/facebook/react
    """
    try:
        # Search for the repo as a placeholder
        repos = await scraper.search_repos(repo_name, per_page=1)
        
        if not repos:
            raise HTTPException(
                status_code=404,
                detail=f"Repository '{owner}/{repo_name}' not found"
            )
        
        # Find exact match
        for repo in repos:
            if repo['full_name'].lower() == f"{owner}/{repo_name}".lower():
                return RepositoryResponse(**repo)
        
        raise HTTPException(
            status_code=404,
            detail=f"Repository '{owner}/{repo_name}' not found"
        )
    
    except HTTPException:
        raise
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Request timed out"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching repository details: {str(e)}"
        )


# ============================================================================
# Statistics Endpoints
# ============================================================================

@router.get(
    "/user/{username}/stats",
    summary="Get user statistics",
    description="Get aggregated statistics about a user's repositories"
)
async def get_user_stats(username: str):
    """
    Get aggregated statistics about a GitHub user's repositories.
    
    Args:
        username: GitHub username
    
    Returns:
        dict: Statistics including total stars, forks, languages used
    
    Raises:
        HTTPException: 404 if user not found, 500 for server errors
    """
    try:
        repos = await scraper.get_user_repos(username)
        
        if not repos:
            raise HTTPException(
                status_code=404,
                detail=f"User '{username}' not found"
            )
        
        # Calculate statistics
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        total_forks = sum(repo.get('forks_count', 0) for repo in repos)
        
        # Get unique languages
        languages = {}
        for repo in repos:
            lang = repo.get('language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        return {
            "username": username,
            "total_repositories": len(repos),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "languages": languages,
            "average_stars_per_repo": total_stars // len(repos) if repos else 0,
            "fetched_at": datetime.utcnow()
        }
    
    except HTTPException:
        raise
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail=f"Request timed out while fetching stats for '{username}'"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching user statistics: {str(e)}"
        )
