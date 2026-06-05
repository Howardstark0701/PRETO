"""
Authentication Schemas for PRETO

Phase 3.1: User Authentication

Author: TANGO
Last Updated: June 5, 2026
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============================================================================
# User Registration & Login
# ============================================================================

class UserRegister(BaseModel):
    """User registration request."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secure_password_123",
                "full_name": "John Doe"
            }
        }


class UserLogin(BaseModel):
    """User login request."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "secure_password_123"
            }
        }


class TokenResponse(BaseModel):
    """Token response after login."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: 'UserResponse' = Field(..., description="User information")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
                "user": {
                    "id": 1,
                    "username": "john_doe",
                    "email": "john@example.com",
                    "full_name": "John Doe",
                    "is_active": True,
                    "created_at": "2026-06-05T12:00:00"
                }
            }
        }


class TokenRefresh(BaseModel):
    """Token refresh request."""
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


# ============================================================================
# User Response Models
# ============================================================================

class UserResponse(BaseModel):
    """User response model."""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "created_at": "2026-06-05T12:00:00",
                "last_login": "2026-06-05T15:30:00"
            }
        }


class UserProfile(BaseModel):
    """User profile response."""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============================================================================
# Saved Search Models
# ============================================================================

class SavedSearchCreate(BaseModel):
    """Create saved search request."""
    query: str = Field(..., min_length=1, max_length=256, description="Search query")
    language: Optional[str] = Field(None, max_length=50, description="Programming language")
    filters: Optional[str] = Field(None, description="Filters as JSON string")
    description: Optional[str] = Field(None, max_length=512, description="Search description")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "machine learning",
                "language": "python",
                "description": "ML projects in Python"
            }
        }


class SavedSearchUpdate(BaseModel):
    """Update saved search request."""
    description: Optional[str] = Field(None, max_length=512)
    is_favorite: Optional[bool] = Field(None)
    
    class Config:
        schema_extra = {
            "example": {
                "description": "Updated description",
                "is_favorite": True
            }
        }


class SavedSearchResponse(BaseModel):
    """Saved search response."""
    id: int
    query: str
    language: Optional[str]
    description: Optional[str]
    is_favorite: bool
    created_at: datetime
    updated_at: datetime
    last_executed: Optional[datetime]
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "query": "machine learning",
                "language": "python",
                "description": "ML projects in Python",
                "is_favorite": True,
                "created_at": "2026-06-05T12:00:00",
                "updated_at": "2026-06-05T12:00:00",
                "last_executed": None
            }
        }


class SavedSearchList(BaseModel):
    """List of saved searches."""
    total: int
    searches: list[SavedSearchResponse]
    
    class Config:
        schema_extra = {
            "example": {
                "total": 5,
                "searches": []
            }
        }


# ============================================================================
# Search History Models
# ============================================================================

class SearchHistoryResponse(BaseModel):
    """Search history response."""
    id: int
    query: str
    results_count: int
    execution_time_ms: int
    used_cache: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "query": "django framework",
                "results_count": 45000,
                "execution_time_ms": 1234,
                "used_cache": False,
                "created_at": "2026-06-05T15:30:00"
            }
        }


class SearchHistoryList(BaseModel):
    """List of search history."""
    total: int
    history: list[SearchHistoryResponse]
    
    class Config:
        schema_extra = {
            "example": {
                "total": 10,
                "history": []
            }
        }


# ============================================================================
# Error Response Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response model."""
    status_code: int
    error: str
    detail: str
    timestamp: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "status_code": 400,
                "error": "Validation Error",
                "detail": "Username already exists",
                "timestamp": "2026-06-05T12:00:00"
            }
        }


# ============================================================================
# Update Forward References
# ============================================================================

TokenResponse.model_rebuild()
SavedSearchList.model_rebuild()
SearchHistoryList.model_rebuild()
