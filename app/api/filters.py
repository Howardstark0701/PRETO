"""
Filtering and sorting utilities for repository data

Task 1.6: Advanced Features

Author: TANGO
Last Updated: June 5, 2026
"""

from typing import List, Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def sort_repositories(
    repositories: List[Dict],
    sort_by: str = "stars",
    sort_order: str = "desc"
) -> List[Dict]:
    """
    Sort repositories by specified field.
    
    Args:
        repositories: List of repository dictionaries
        sort_by: Field to sort by (stars, forks, watchers, updated_at, name)
        sort_order: Sort order (asc, desc)
    
    Returns:
        Sorted list of repositories
    """
    if not repositories:
        return repositories
    
    try:
        # Map sort_by values to actual dictionary keys
        sort_map = {
            "stars": "stargazers_count",
            "forks": "forks_count",
            "watchers": "watchers_count",
            "updated_at": "updated_at",
            "name": "name"
        }
        
        sort_key = sort_map.get(sort_by, "stargazers_count")
        reverse = sort_order.lower() == "desc"
        
        logger.info(f"Sorting repositories by {sort_by} ({sort_order})")
        
        # Sort with None handling
        sorted_repos = sorted(
            repositories,
            key=lambda x: x.get(sort_key, 0) if x.get(sort_key) is not None else 0,
            reverse=reverse
        )
        
        return sorted_repos
    
    except Exception as e:
        logger.error(f"Error sorting repositories: {str(e)}")
        return repositories


def filter_repositories(
    repositories: List[Dict],
    language: Optional[str] = None,
    min_stars: Optional[int] = None,
    min_forks: Optional[int] = None,
    updated_after: Optional[str] = None
) -> List[Dict]:
    """
    Filter repositories by specified criteria.
    
    Args:
        repositories: List of repository dictionaries
        language: Filter by programming language
        min_stars: Minimum number of stars
        min_forks: Minimum number of forks
        updated_after: Filter repos updated after this date (ISO format)
    
    Returns:
        Filtered list of repositories
    """
    if not repositories:
        return repositories
    
    filtered = repositories
    
    try:
        # Filter by language
        if language:
            logger.info(f"Filtering by language: {language}")
            filtered = [
                repo for repo in filtered
                if repo.get("language", "").lower() == language.lower()
            ]
        
        # Filter by minimum stars
        if min_stars is not None and min_stars > 0:
            logger.info(f"Filtering by min stars: {min_stars}")
            filtered = [
                repo for repo in filtered
                if repo.get("stargazers_count", 0) >= min_stars
            ]
        
        # Filter by minimum forks
        if min_forks is not None and min_forks > 0:
            logger.info(f"Filtering by min forks: {min_forks}")
            filtered = [
                repo for repo in filtered
                if repo.get("forks_count", 0) >= min_forks
            ]
        
        # Filter by update date
        if updated_after:
            logger.info(f"Filtering by updated_after: {updated_after}")
            try:
                target_date = datetime.fromisoformat(updated_after.replace("Z", "+00:00"))
                filtered = [
                    repo for repo in filtered
                    if repo.get("updated_at") and 
                    datetime.fromisoformat(repo.get("updated_at", "").replace("Z", "+00:00")) > target_date
                ]
            except ValueError as e:
                logger.warning(f"Invalid date format: {updated_after}")
        
        logger.info(f"Filtering complete: {len(repositories)} -> {len(filtered)} repositories")
        return filtered
    
    except Exception as e:
        logger.error(f"Error filtering repositories: {str(e)}")
        return repositories


def paginate_repositories(
    repositories: List[Dict],
    page: int = 1,
    per_page: int = 30
) -> tuple:
    """
    Paginate repository list.
    
    Args:
        repositories: List of repository dictionaries
        page: Page number (1-indexed)
        per_page: Number of items per page
    
    Returns:
        Tuple of (paginated_list, total_count, total_pages, has_next, has_prev)
    """
    if not repositories:
        return [], 0, 0, False, False
    
    try:
        total_count = len(repositories)
        total_pages = (total_count + per_page - 1) // per_page
        
        # Validate page number
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        paginated = repositories[start_idx:end_idx]
        has_next = page < total_pages
        has_prev = page > 1
        
        logger.info(f"Pagination: page {page}/{total_pages}, items {start_idx}-{end_idx}")
        
        return paginated, total_count, total_pages, has_next, has_prev
    
    except Exception as e:
        logger.error(f"Error paginating repositories: {str(e)}")
        return repositories, len(repositories), 1, False, False


def get_language_stats(repositories: List[Dict]) -> Dict[str, int]:
    """
    Get language statistics from repositories.
    
    Args:
        repositories: List of repository dictionaries
    
    Returns:
        Dictionary with language counts
    """
    stats = {}
    
    for repo in repositories:
        language = repo.get("language")
        if language:
            stats[language] = stats.get(language, 0) + 1
    
    return dict(sorted(stats.items(), key=lambda x: x[1], reverse=True))


def get_most_used_language(repositories: List[Dict]) -> Optional[str]:
    """
    Get the most used programming language in repositories.
    
    Args:
        repositories: List of repository dictionaries
    
    Returns:
        Most used language or None
    """
    stats = get_language_stats(repositories)
    return max(stats, key=stats.get) if stats else None
