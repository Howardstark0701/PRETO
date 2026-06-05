"""
Pydantic schemas for request/response validation

Phase 2: Data validation and API documentation
Task 1.6: Advanced Features (sorting, filtering)

Author: TANGO
Last Updated: June 5, 2026
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums for filtering and sorting
class SortBy(str, Enum):
    """Available sort options for repositories."""
    STARS = "stars"
    FORKS = "forks"
    WATCHERS = "watchers"
    UPDATED = "updated_at"
    NAME = "name"


class SortOrder(str, Enum):
    """Sort order options."""
    ASC = "asc"
    DESC = "desc"


class RepositoryResponse(BaseModel):
    """Response model for a single repository."""
    name: str
    full_name: str
    url: str
    description: Optional[str] = None
    language: Optional[str] = None
    stargazers_count: int = 0
    forks_count: int = 0
    watchers_count: int = 0
    updated_at: Optional[str] = None
    topics: Optional[List[str]] = None

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "name": "linux",
                "full_name": "torvalds/linux",
                "url": "https://github.com/torvalds/linux",
                "description": "Linux kernel source tree",
                "language": "C",
                "stargazers_count": 180000,
                "forks_count": 25000,
                "watchers_count": 5000,
                "updated_at": "2026-06-05T12:34:56Z",
                "topics": ["linux", "kernel", "os"]
            }
        }


class UserRepositoriesResponse(BaseModel):
    """Response model for user's repositories."""
    username: str
    total_count: int
    repos: List[RepositoryResponse]
    cached: bool = False
    last_updated: Optional[datetime] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None


class SearchResultsResponse(BaseModel):
    """Response model for search results."""
    query: str
    language: Optional[str] = None
    per_page: int = 30
    total_count: int
    results: List[RepositoryResponse]
    cached: bool = False
    last_updated: Optional[datetime] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None


class PaginationInfo(BaseModel):
    """Pagination information for responses."""
    total_count: int
    per_page: int
    current_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


class AdvancedSearchResponse(BaseModel):
    """Response model for advanced search with pagination."""
    query: str
    language: Optional[str] = None
    filters: Optional[dict] = None
    results: List[RepositoryResponse]
    pagination: PaginationInfo
    sort_by: str
    sort_order: str
    cached: bool = False
    last_updated: datetime


class UserStatsResponse(BaseModel):
    """Response model for user statistics."""
    username: str
    total_repositories: int
    total_stars: int
    total_forks: int
    total_watchers: int
    languages: dict = Field(default_factory=dict)
    average_stars_per_repo: int = 0
    average_forks_per_repo: int = 0
    most_used_language: Optional[str] = None
    fetched_at: datetime


class ErrorResponse(BaseModel):
    """Response model for errors."""
    status_code: int
    error: str
    detail: str
    timestamp: datetime
