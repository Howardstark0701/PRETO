"""
Pydantic schemas for request/response validation

Phase 2: Data validation and API documentation

Author: TANGO
Last Updated: June 5, 2026
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


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


class UserRepositoriesResponse(BaseModel):
    """Response model for user's repositories."""
    username: str
    total_count: int
    repos: List[RepositoryResponse]
    cached: bool = False
    last_updated: Optional[datetime] = None


class SearchResultsResponse(BaseModel):
    """Response model for search results."""
    query: str
    language: Optional[str] = None
    per_page: int = 30
    total_count: int
    results: List[RepositoryResponse]
    cached: bool = False
    last_updated: Optional[datetime] = None


class ErrorResponse(BaseModel):
    """Response model for errors."""
    status_code: int
    error: str
    detail: str
    timestamp: datetime
