"""
FastAPI routes/endpoints for GitHub scraper

Phase 2: REST API endpoints wrapping GitHubScraper
Task 1.6: Advanced Features (sorting, filtering, pagination)
Phase 2.1-2.3: Caching, persistence, and background tasks integration

Author: TANGO
Last Updated: June 5, 2026
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
import asyncio
import logging

from app.scrapers.github_scraper import GitHubScraper
from app.scrapers.gitlab_scraper import GitLabScraper
from app.scrapers.reddit_scraper import RedditScraper
from app.scrapers.hackernews_scraper import HackerNewsScraper
from app.scrapers.x_scraper import XScraper
from app.scrapers.devto_scraper import DevToScraper
from .schemas import (
    UserRepositoriesResponse,
    SearchResultsResponse,
    RepositoryResponse,
    AdvancedSearchResponse,
    UserStatsResponse,
    PaginationInfo,
    SortBy,
    SortOrder,
    ErrorResponse
)
from .filters import (
    sort_repositories,
    filter_repositories,
    paginate_repositories,
    get_language_stats,
    get_most_used_language
)
from .cache import cache_get, cache_set, cache_invalidate, cache_stats
from .sync import get_sync_manager
from .scheduler import get_scheduler

# Configure logging for error tracking
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create router for all GitHub-related endpoints
router = APIRouter(prefix="/api", tags=["repositories"])

# Initialize GitHub scraper (no token for now, will be enhanced later)
scraper = GitHubScraper()


# ============================================================================
# User Repositories Endpoints
# ============================================================================

@router.get(
    "/repos/user/{username}",
    response_model=UserRepositoriesResponse,
    summary="Get user repositories",
    description="Fetch all repositories for a given GitHub user with sorting and filtering",
    responses={
        200: {"description": "Successfully retrieved user repositories"},
        400: {"description": "Invalid parameters"},
        404: {"description": "User not found or has no public repositories"},
        502: {"description": "GitHub API error"},
        504: {"description": "Request timeout"},
        500: {"description": "Internal server error"}
    }
)
async def get_user_repos(
    username: str,
    per_page: int = Query(30, ge=1, le=100, description="Results per page"),
    sort_by: Optional[str] = Query(
        "stars",
        description="Sort by: stars, forks, watchers, updated_at, name"
    ),
    sort_order: Optional[str] = Query(
        "desc",
        description="Sort order: asc or desc"
    ),
    language: Optional[str] = Query(None, description="Filter by programming language"),
    min_stars: Optional[int] = Query(None, ge=0, description="Minimum number of stars"),
    use_cache: bool = Query(True, description="Use cached results if available")
):
    """
    Get repositories for a GitHub user with advanced sorting, filtering, and caching.
    
    Args:
        username (str): GitHub username (required)
        per_page (int): Results per page (1-100, default 30)
        sort_by (str): Sort field (stars, forks, watchers, updated_at, name)
        sort_order (str): Sort order (asc, desc)
        language (str): Filter by programming language
        min_stars (int): Filter by minimum stars
        use_cache (bool): Use cached results (default True)
    
    Returns:
        UserRepositoriesResponse: User and their repositories with sorting applied
    
    Status Codes:
        200: Success
        400: Invalid input
        404: User not found
        502: GitHub API error
        504: Timeout
    """
    try:
        # Validate username
        if not username or len(username.strip()) == 0:
            logger.warning("Empty username provided")
            raise HTTPException(status_code=400, detail="Username cannot be empty")
        
        if len(username) > 39:
            logger.warning(f"Invalid username format: {username}")
            raise HTTPException(status_code=400, detail="Username must be max 39 characters")
        
        # Validate sort parameters
        valid_sorts = ["stars", "forks", "watchers", "updated_at", "name"]
        if sort_by and sort_by not in valid_sorts:
            logger.warning(f"Invalid sort_by: {sort_by}")
            raise HTTPException(
                status_code=400,
                detail=f"sort_by must be one of: {', '.join(valid_sorts)}"
            )
        
        valid_orders = ["asc", "desc"]
        if sort_order and sort_order.lower() not in valid_orders:
            logger.warning(f"Invalid sort_order: {sort_order}")
            raise HTTPException(
                status_code=400,
                detail="sort_order must be 'asc' or 'desc'"
            )
        
        logger.info(f"Fetching repositories for {username}: sort_by={sort_by}, language={language}")
        
        # Try to get from cache
        repos = None
        cached = False
        
        if use_cache:
            cached_data = cache_get('user_repos', username=username, language=language, min_stars=min_stars)
            if cached_data:
                repos = cached_data
                cached = True
                logger.info(f"Using cached data for {username}")
        
        # Fetch from API if not in cache
        if not repos:
            repos = await asyncio.wait_for(
                scraper.get_user_repos(username, per_page=100),  # Get more for filtering
                timeout=15.0
            )
            
            if repos:
                # Cache the result
                cache_set('user_repos', repos, username=username, language=language, min_stars=min_stars)
                logger.info(f"Cached repos for {username}")
        
        if not repos:
            logger.warning(f"User not found: {username}")
            raise HTTPException(
                status_code=404,
                detail=f"User '{username}' not found on GitHub or has no public repositories"
            )
        
        # Apply filters
        if language or min_stars:
            repos = filter_repositories(
                repos,
                language=language,
                min_stars=min_stars
            )
        
        # Apply sorting
        if sort_by:
            repos = sort_repositories(
                repos,
                sort_by=sort_by,
                sort_order=sort_order.lower() if sort_order else "desc"
            )
        
        # Limit to per_page
        repos = repos[:per_page]
        
        logger.info(f"Retrieved {len(repos)} repositories for {username}")
        
        return UserRepositoriesResponse(
            username=username,
            total_count=len(repos),
            repos=repos,
            cached=cached,
            last_updated=datetime.utcnow(),
            sort_by=sort_by,
            sort_order=sort_order
        )
    
    except asyncio.TimeoutError:
        logger.error(f"Timeout fetching repos for: {username}")
        raise HTTPException(status_code=504, detail="Request timed out")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching repos: {str(e)}", exc_info=True)
        raise HTTPException(status_code=502, detail=f"GitHub API error: {str(e)}")


# ============================================================================
# Search Repositories Endpoints
# ============================================================================

@router.get(
    "/repos/search/advanced",
    response_model=AdvancedSearchResponse,
    summary="Advanced repository search",
    description="Search repositories with advanced filtering, sorting, and pagination",
    responses={
        200: {"description": "Search completed successfully"},
        400: {"description": "Invalid parameters"},
        404: {"description": "No repositories found"},
        502: {"description": "GitHub API error"},
        504: {"description": "Request timeout"},
        500: {"description": "Internal server error"}
    }
)
async def advanced_search(
    query: str = Query(..., min_length=1, max_length=256, description="Search query"),
    language: Optional[str] = Query(None, max_length=50, description="Programming language"),
    min_stars: Optional[int] = Query(None, ge=0, description="Minimum stars"),
    sort_by: Optional[str] = Query("stars", description="Sort by field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(30, ge=1, le=100, description="Results per page"),
    use_cache: bool = Query(True, description="Use cached results if available")
):
    """
    Advanced search with filtering, sorting, pagination, and caching.
    
    Args:
        query: Search query (required)
        language: Filter by language
        min_stars: Minimum stars filter
        sort_by: Sort field (stars, forks, watchers, updated_at, name)
        sort_order: Sort order (asc, desc)
        page: Page number (1-indexed)
        per_page: Results per page
        use_cache: Use cached results (default True)
    
    Returns:
        AdvancedSearchResponse: Results with pagination info
    """
    try:
        # Validate inputs
        if not query or len(query.strip()) < 1:
            logger.warning("Empty search query")
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
        valid_sorts = ["stars", "forks", "watchers", "updated_at", "name"]
        if sort_by and sort_by not in valid_sorts:
            raise HTTPException(
                status_code=400,
                detail=f"sort_by must be one of: {', '.join(valid_sorts)}"
            )
        
        logger.info(f"Advanced search: query='{query}', language={language}, sort_by={sort_by}")
        
        # Try to get from cache
        repos = None
        if use_cache:
            cached_data = cache_get('search', query=query, language=language, min_stars=min_stars)
            if cached_data:
                repos = cached_data
                logger.info(f"Using cached search results for '{query}'")
        
        # Search repositories
        if not repos:
            repos = await asyncio.wait_for(
                scraper.search_repos(query, language=language, per_page=100),
                timeout=15.0
            )
            
            if repos:
                cache_set('search', repos, query=query, language=language, min_stars=min_stars)
        
        if not repos:
            logger.info(f"No results for query: {query}")
            raise HTTPException(status_code=404, detail=f"No repositories found for: {query}")
        
        # Apply filters
        if min_stars:
            repos = filter_repositories(repos, min_stars=min_stars)
        
        # Apply sorting
        if sort_by:
            repos = sort_repositories(repos, sort_by=sort_by, sort_order=sort_order.lower())
        
        # Apply pagination
        paginated, total, total_pages, has_next, has_prev = paginate_repositories(
            repos, page=page, per_page=per_page
        )
        
        logger.info(f"Search completed: {total} results, page {page}/{total_pages}")
        
        return AdvancedSearchResponse(
            query=query,
            language=language,
            filters={"min_stars": min_stars},
            results=paginated,
            pagination=PaginationInfo(
                total_count=total,
                per_page=per_page,
                current_page=page,
                total_pages=total_pages,
                has_next=has_next,
                has_prev=has_prev
            ),
            sort_by=sort_by,
            sort_order=sort_order,
            last_updated=datetime.utcnow()
        )
    
    except asyncio.TimeoutError:
        logger.error("Search timeout")
        raise HTTPException(status_code=504, detail="Search request timed out")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=502, detail=f"GitHub API error: {str(e)}")


# Keep original search endpoint for backward compatibility
@router.get(
    "/repos/search",
    response_model=SearchResultsResponse,
    summary="Search repositories",
    description="Search for repositories across GitHub by keyword with optional language filter",
    responses={
        200: {"description": "Search completed successfully"},
        400: {"description": "Invalid query parameters"},
        404: {"description": "No repositories found"},
        502: {"description": "GitHub API error"},
        504: {"description": "Request timeout"},
        500: {"description": "Internal server error"}
    }
)
async def search_repositories(
    query: str = Query(..., min_length=1, max_length=256, description="Search query"),
    language: Optional[str] = Query(None, max_length=50, description="Programming language filter"),
    per_page: int = Query(30, ge=1, le=100, description="Results per page"),
    use_cache: bool = Query(True, description="Use cached results if available")
):
    """
    Search for repositories on GitHub with caching.
    
    Args:
        query (str): Search query (required, 1-256 chars)
        language (str, optional): Programming language filter
        per_page (int): Results per page (default 30, max 100)
        use_cache (bool): Use cached results (default True)
    
    Returns:
        SearchResultsResponse: Top matching repositories sorted by stars
    
    Raises:
        400: Invalid query parameters
        404: No repositories found
        502: GitHub API error
        504: Request timeout
    
    Examples:
        GET /api/repos/search?query=machine-learning&language=python
        GET /api/repos/search?query=web framework
    """
    try:
        # Validate query parameter
        if not query or len(query.strip()) < 1:
            logger.warning("Empty search query provided")
            raise HTTPException(
                status_code=400,
                detail="Search query cannot be empty"
            )
        
        if len(query) > 256:
            logger.warning(f"Query too long: {len(query)} characters")
            raise HTTPException(
                status_code=400,
                detail="Query must be 256 characters or less"
            )
        
        # Validate language parameter
        if language and len(language) > 50:
            logger.warning(f"Invalid language filter: {language}")
            raise HTTPException(
                status_code=400,
                detail="Language filter must be 50 characters or less"
            )
        
        # Validate per_page
        if per_page < 1 or per_page > 100:
            logger.warning(f"Invalid per_page value: {per_page}")
            raise HTTPException(
                status_code=400,
                detail="per_page must be between 1 and 100"
            )
        
        logger.info(f"Searching repos - query: '{query}', language: {language}, per_page: {per_page}")
        
        # Try to get from cache
        repos = None
        cached = False
        
        if use_cache:
            cached_data = cache_get('search', query=query, language=language)
            if cached_data:
                repos = cached_data
                cached = True
                logger.info(f"Using cached search for '{query}'")
        
        # Search repositories with timeout
        if not repos:
            repos = await asyncio.wait_for(
                scraper.search_repos(query, language=language, per_page=per_page),
                timeout=15.0
            )
            
            if repos:
                cache_set('search', repos, query=query, language=language)
        
        # Check if results found
        if not repos:
            logger.info(f"No results found for query: {query}")
            raise HTTPException(
                status_code=404,
                detail=f"No repositories found matching: '{query}'" + (f" in {language}" if language else "")
            )
        
        logger.info(f"Search completed - found {len(repos)} repositories")
        
        return SearchResultsResponse(
            query=query,
            language=language,
            per_page=per_page,
            total_count=len(repos),
            results=repos,
            cached=cached,
            last_updated=datetime.utcnow()
        )
    
    except asyncio.TimeoutError:
        logger.error(f"Request timeout for search query: {query}")
        raise HTTPException(
            status_code=504,
            detail="Search request timed out. GitHub API may be slow or overloaded."
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error during search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error during search: {str(e)}"
        )


# ============================================================================
# Repository Details Endpoints
# ============================================================================

@router.get(
    "/repos/{owner}/{repo_name}",
    summary="Get repository details",
    description="Get detailed information about a specific repository",
    responses={
        200: {"description": "Repository details retrieved"},
        400: {"description": "Invalid owner or repository name"},
        404: {"description": "Repository not found"},
        502: {"description": "GitHub API error"},
        504: {"description": "Request timeout"},
        500: {"description": "Internal server error"}
    }
)
async def get_repository_details(
    owner: str,
    repo_name: str,
    use_cache: bool = Query(True, description="Use cached results if available")
):
    """
    Get detailed information about a specific repository with caching.
    
    Args:
        owner (str): Repository owner username
        repo_name (str): Repository name
        use_cache (bool): Use cached results (default True)
    
    Returns:
        RepositoryResponse: Detailed repository information
    
    Raises:
        400: Invalid owner or repo_name format
        404: Repository not found
        502: GitHub API error
        504: Request timeout
    
    Examples:
        GET /api/repos/torvalds/linux
        GET /api/repos/facebook/react
    """
    try:
        # Validate parameters
        if not owner or len(owner.strip()) == 0:
            logger.warning("Empty owner provided")
            raise HTTPException(
                status_code=400,
                detail="Repository owner cannot be empty"
            )
        
        if not repo_name or len(repo_name.strip()) == 0:
            logger.warning("Empty repo_name provided")
            raise HTTPException(
                status_code=400,
                detail="Repository name cannot be empty"
            )
        
        if len(owner) > 39 or len(repo_name) > 255:
            logger.warning(f"Invalid repository identifiers - owner: {owner}, repo: {repo_name}")
            raise HTTPException(
                status_code=400,
                detail="Invalid owner or repository name format"
            )
        
        full_name = f"{owner}/{repo_name}"
        logger.info(f"Fetching details for repository: {full_name}")
        
        # Try to get from cache
        repo = None
        if use_cache:
            cached_data = cache_get('repo_details', owner=owner, repo_name=repo_name)
            if cached_data:
                repo = cached_data
                logger.info(f"Using cached data for {full_name}")
        
        # Search for the repo
        if not repo:
            repos = await asyncio.wait_for(
                scraper.search_repos(repo_name, per_page=1),
                timeout=15.0
            )
            
            if not repos:
                logger.warning(f"Repository not found: {full_name}")
                raise HTTPException(
                    status_code=404,
                    detail=f"Repository '{full_name}' not found"
                )
            
            # Find exact match
            for r in repos:
                if r['full_name'].lower() == full_name.lower():
                    repo = r
                    cache_set('repo_details', repo, owner=owner, repo_name=repo_name)
                    break
        
        if not repo:
            logger.warning(f"Exact match not found for: {full_name}")
            raise HTTPException(
                status_code=404,
                detail=f"Repository '{full_name}' not found"
            )
        
        logger.info(f"Successfully retrieved repository: {full_name}")
        return RepositoryResponse(**repo)
    
    except asyncio.TimeoutError:
        logger.error(f"Request timeout for repository: {owner}/{repo_name}")
        raise HTTPException(
            status_code=504,
            detail="Request timed out while fetching repository details"
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error fetching repo details for {owner}/{repo_name}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=502,
            detail=f"GitHub API error: {str(e)}"
        )


# ============================================================================
# Statistics Endpoints
# ============================================================================

@router.get(
    "/repos/user/{username}/stats",
    response_model=UserStatsResponse,
    summary="Get user statistics",
    description="Get detailed aggregated statistics about a user's repositories",
    responses={
        200: {"description": "User statistics retrieved"},
        400: {"description": "Invalid username format"},
        404: {"description": "User not found"},
        502: {"description": "GitHub API error"},
        504: {"description": "Request timeout"},
        500: {"description": "Internal server error"}
    }
)
async def get_user_stats(username: str, use_cache: bool = Query(True, description="Use cached results if available")):
    """
    Get detailed statistics about a GitHub user's repositories with caching.
    
    Args:
        username (str): GitHub username
        use_cache (bool): Use cached results (default True)
    
    Returns:
        UserStatsResponse: Comprehensive user statistics
    """
    try:
        # Validate username
        if not username or len(username.strip()) == 0:
            logger.warning("Empty username for stats")
            raise HTTPException(status_code=400, detail="Username cannot be empty")
        
        if len(username) > 39:
            logger.warning(f"Invalid username for stats: {username}")
            raise HTTPException(status_code=400, detail="Username must be 39 characters or less")
        
        logger.info(f"Fetching stats for user: {username}")
        
        # Try to get from cache
        repos = None
        if use_cache:
            cached_data = cache_get('stats', username=username)
            if cached_data:
                repos = cached_data
                logger.info(f"Using cached stats for {username}")
        
        # Fetch user repos
        if not repos:
            repos = await asyncio.wait_for(
                scraper.get_user_repos(username),
                timeout=15.0
            )
            
            if repos:
                cache_set('stats', repos, username=username)
        
        if not repos:
            logger.warning(f"User not found for stats: {username}")
            raise HTTPException(
                status_code=404,
                detail=f"User '{username}' not found on GitHub"
            )
        
        # Calculate statistics
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        total_forks = sum(repo.get('forks_count', 0) for repo in repos)
        total_watchers = sum(repo.get('watchers_count', 0) for repo in repos)
        
        # Get language statistics
        languages = get_language_stats(repos)
        most_used = get_most_used_language(repos)
        
        logger.info(f"Stats for {username}: {len(repos)} repos, {total_stars} stars")
        
        return UserStatsResponse(
            username=username,
            total_repositories=len(repos),
            total_stars=total_stars,
            total_forks=total_forks,
            total_watchers=total_watchers,
            languages=languages,
            average_stars_per_repo=total_stars // len(repos) if repos else 0,
            average_forks_per_repo=total_forks // len(repos) if repos else 0,
            most_used_language=most_used,
            fetched_at=datetime.utcnow()
        )
    
    except asyncio.TimeoutError:
        logger.error(f"Stats timeout for: {username}")
        raise HTTPException(status_code=504, detail="Request timed out")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stats error for {username}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=502, detail=f"GitHub API error: {str(e)}")


# ============================================================================
# Management Endpoints (Phase 2.1-2.3)
# ============================================================================

@router.post(
    "/sync/user/{username}",
    summary="Manually sync user repositories",
    description="Trigger a manual sync of repositories for a specific user",
    tags=["sync"]
)
async def sync_user_manual(username: str):
    """
    Manually trigger synchronization of user repositories to database.
    
    Args:
        username (str): GitHub username
    
    Returns:
        dict: Sync result with status and details
    """
    try:
        from app.api.sync import background_sync_user
        
        if not username or len(username.strip()) == 0:
            raise HTTPException(status_code=400, detail="Username cannot be empty")
        
        logger.info(f"Manual sync triggered for: {username}")
        
        result = await background_sync_user(username)
        return {
            "status": "initiated",
            "username": username,
            "result": result,
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Sync error for {username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@router.get(
    "/cache/stats",
    summary="Get cache statistics",
    description="Get current cache statistics and performance metrics",
    tags=["cache"]
)
async def get_cache_stats():
    """
    Get cache statistics including hit/miss counts and memory usage.
    
    Returns:
        dict: Cache statistics
    """
    try:
        logger.info("Cache stats requested")
        stats = cache_stats()
        return {
            "status": "success",
            "cache": stats,
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")


@router.delete(
    "/cache/clear",
    summary="Clear cache",
    description="Clear all cache entries",
    tags=["cache"]
)
async def clear_cache(cache_type: Optional[str] = Query(None, description="Cache type to clear (optional)")):
    """
    Clear cache entries. If cache_type is specified, only clear that type.
    
    Args:
        cache_type (str, optional): Type of cache to clear (user_repos, search, stats, repo_details)
    
    Returns:
        dict: Result of cache clear operation
    """
    try:
        from app.api.cache import CacheManager
        
        logger.info(f"Cache clear requested: type={cache_type}")
        
        if cache_type:
            count = CacheManager.invalidate_pattern(cache_type)
            return {
                "status": "success",
                "message": f"Cleared {count} {cache_type} cache entries",
                "entries_cleared": count,
                "timestamp": datetime.utcnow()
            }
        else:
            count = CacheManager.clear_all()
            return {
                "status": "success",
                "message": f"Cleared all {count} cache entries",
                "entries_cleared": count,
                "timestamp": datetime.utcnow()
            }
    
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


@router.get(
    "/scheduler/stats",
    summary="Get scheduler statistics",
    description="Get information about scheduled background tasks",
    tags=["scheduler"]
)
async def get_scheduler_stats():
    """
    Get scheduler statistics including task status and execution history.
    
    Returns:
        dict: Scheduler statistics
    """
    try:
        logger.info("Scheduler stats requested")
        scheduler = get_scheduler()
        stats = scheduler.get_stats()
        return {
            "status": "success",
            "scheduler": stats,
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Error getting scheduler stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting scheduler stats: {str(e)}")


@router.post(
    "/scheduler/jobs/{job_id}/toggle",
    summary="Toggle job enabled/disabled",
    description="Enable or disable a scheduled job",
    tags=["scheduler"]
)
async def toggle_scheduler_job(job_id: str):
    """
    Toggle a scheduler job between enabled and disabled state.
    
    Args:
        job_id (str): ID of the job to toggle
    
    Returns:
        dict: New state of the job
    """
    try:
        logger.info(f"Toggling job: {job_id}")
        scheduler = get_scheduler()
        
        job_info = scheduler.get_job_info(job_id)
        if not job_info:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        # Toggle the state
        if job_info['enabled']:
            scheduler.disable_job(job_id)
            new_state = "disabled"
        else:
            scheduler.enable_job(job_id)
            new_state = "enabled"
        
        return {
            "status": "success",
            "job_id": job_id,
            "new_state": new_state,
            "job_info": scheduler.get_job_info(job_id),
            "timestamp": datetime.utcnow()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error toggling job: {str(e)}")


@router.get(
    "/sync/stats",
    summary="Get sync statistics",
    description="Get information about background sync operations",
    tags=["sync"]
)
async def get_sync_stats():
    """
    Get sync manager statistics including sync history and errors.
    
    Returns:
        dict: Sync statistics
    """
    try:
        logger.info("Sync stats requested")
        manager = get_sync_manager()
        stats = manager.get_sync_stats()
        return {
            "status": "success",
            "sync": stats,
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Error getting sync stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting sync stats: {str(e)}")


# ============================================================================
# Contributors Endpoint (Session 3 — Graph expansion)
# ============================================================================

@router.get(
    "/repos/{owner}/{repo_name}/contributors",
    summary="Get repository contributors",
    description="Fetch top contributors for a repository (for graph analysis)",
    tags=["repositories"]
)
async def get_repo_contributors(
    owner: str,
    repo_name: str,
    per_page: int = Query(10, ge=1, le=30, description="Number of contributors"),
):
    """
    Fetch contributors for a repository via GitHub API.
    Used by the graph analysis page to expand the network.
    """
    import asyncio
    try:
        if not owner or not repo_name:
            raise HTTPException(status_code=400, detail="Owner and repo_name required")

        # Use the scraper's session/token
        import httpx
        import os

        token = os.getenv("GITHUB_TOKEN", "")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        url = f"https://api.github.com/repos/{owner}/{repo_name}/contributors"
        params = {"per_page": per_page, "anon": "false"}

        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            resp = await asyncio.wait_for(
                client.get(url, params=params),
                timeout=10.0
            )

        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Repository {owner}/{repo_name} not found")
        if resp.status_code == 403:
            raise HTTPException(status_code=429, detail="GitHub rate limit exceeded")
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"GitHub API error: {resp.status_code}")

        contributors = resp.json()

        return {
            "owner": owner,
            "repo": repo_name,
            "contributors": [
                {
                    "login":         c.get("login"),
                    "avatar_url":    c.get("avatar_url"),
                    "html_url":      c.get("html_url"),
                    "contributions": c.get("contributions", 0),
                    "type":          c.get("type", "User"),
                }
                for c in contributors
                if c.get("type") == "User"
            ],
            "count": len(contributors),
        }

    except HTTPException:
        raise
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        logger.error(f"Contributors error for {owner}/{repo_name}: {e}")
        raise HTTPException(status_code=502, detail=f"GitHub API error: {str(e)}")


# ============================================================================
# GitLab Endpoints (MACH1 — Phase 4a)
# ============================================================================

gitlab_scraper = GitLabScraper()
reddit_scraper = RedditScraper()
hn_scraper = HackerNewsScraper()
x_scraper = XScraper()
devto_scraper = DevToScraper()


@router.get(
    "/sources/gitlab/users/{username}/projects",
    summary="Get GitLab user projects",
    tags=["sources"]
)
async def get_gitlab_user_projects(username: str, per_page: int = 30):
    """Fetch public projects for a GitLab user."""
    try:
        projects = await gitlab_scraper.get_user_projects(username, per_page)
        return {"username": username, "source": "gitlab", "projects": projects, "count": len(projects)}
    except Exception as e:
        logger.error(f"GitLab error for {username}: {e}")
        raise HTTPException(status_code=502, detail=f"GitLab API error: {str(e)}")


@router.get(
    "/sources/gitlab/search",
    summary="Search GitLab projects",
    tags=["sources"]
)
async def search_gitlab_projects(query: str, per_page: int = 30):
    """Search GitLab projects by query."""
    try:
        results = await gitlab_scraper.search_projects(query, per_page)
        return {"query": query, "source": "gitlab", "results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"GitLab search error: {e}")
        raise HTTPException(status_code=502, detail=f"GitLab search error: {str(e)}")


# ============================================================================
# Reddit Endpoints (MACH1 — Phase 4b)
# ============================================================================

@router.get(
    "/sources/reddit/users/{username}",
    summary="Get Reddit user info",
    tags=["sources"]
)
async def get_reddit_user(username: str):
    """Fetch Reddit user profile info."""
    user = await reddit_scraper.get_user_info(username)
    if not user:
        raise HTTPException(status_code=404, detail=f"Reddit user {username} not found")
    return user


@router.get(
    "/sources/reddit/users/{username}/submissions",
    summary="Get Reddit user submissions",
    tags=["sources"]
)
async def get_reddit_submissions(username: str, limit: int = 25):
    """Fetch Reddit user's recent submissions."""
    posts = await reddit_scraper.get_user_submissions(username, limit)
    return {"username": username, "source": "reddit", "posts": posts, "count": len(posts)}


# ============================================================================
# Hacker News Endpoints (MACH1 — Phase 4b)
# ============================================================================

@router.get(
    "/sources/hackernews/users/{username}",
    summary="Get Hacker News user info",
    tags=["sources"]
)
async def get_hn_user(username: str):
    """Fetch Hacker News user profile."""
    user = await hn_scraper.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail=f"HN user {username} not found")
    return user


@router.get(
    "/sources/hackernews/users/{username}/submissions",
    summary="Get Hacker News user submissions",
    tags=["sources"]
)
async def get_hn_submissions(username: str, limit: int = 20):
    """Fetch Hacker News user's recent story submissions."""
    items = await hn_scraper.get_user_submissions(username, limit)
    return {"username": username, "source": "hackernews", "submissions": items, "count": len(items)}


# ============================================================================
# X / Twitter Endpoints (MACH1 — Phase 4c)
# ============================================================================

@router.get(
    "/sources/x/users/{username}",
    summary="Get X/Twitter user info",
    tags=["sources"]
)
async def get_x_user(username: str):
    """Fetch X/Twitter user profile info."""
    user = await x_scraper.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail=f"X user {username} not found")
    return user


@router.get(
    "/sources/x/users/{username}/tweets",
    summary="Get X/Twitter user tweets",
    tags=["sources"]
)
async def get_x_tweets(username: str, max_results: int = 10):
    """Fetch X/Twitter user's recent tweets."""
    tweets = await x_scraper.get_tweets(username, max_results)
    return {"username": username, "source": "x", "tweets": tweets, "count": len(tweets)}


# ============================================================================
# Dev.to Endpoints (MACH1 — Phase 4c)
# ============================================================================

@router.get(
    "/sources/devto/users/{username}",
    summary="Get Dev.to user info",
    tags=["sources"]
)
async def get_devto_user(username: str):
    """Fetch Dev.to user profile."""
    user = await devto_scraper.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail=f"Dev.to user {username} not found")
    return user


@router.get(
    "/sources/devto/users/{username}/articles",
    summary="Get Dev.to user articles",
    tags=["sources"]
)
async def get_devto_articles(username: str, per_page: int = 20):
    """Fetch Dev.to user's articles."""
    articles = await devto_scraper.get_articles(username, per_page)
    return {"username": username, "source": "devto", "articles": articles, "count": len(articles)}


# ============================================================================
# GitHub Enhancements (MACH1 — Phase 4c)
# ============================================================================

@router.get(
    "/repos/trending",
    summary="Get trending GitHub repositories",
    description="Fetch trending repos by language and date range",
    tags=["repositories"]
)
async def get_trending_repos(
    language: str = "",
    since: str = "weekly",
    per_page: int = 25,
):
    """Fetch trending repositories using GitHub search sorted by stars."""
    try:
        q = "stars:>100"
        if language:
            q += f" language:{language}"
        results = await scraper.search_repos(q, per_page=per_page)
        results.sort(key=lambda r: r.get("stargazers_count", 0), reverse=True)
        return {"language": language, "since": since, "trending": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Trending repos error: {e}")
        raise HTTPException(status_code=502, detail=f"GitHub API error: {str(e)}")
