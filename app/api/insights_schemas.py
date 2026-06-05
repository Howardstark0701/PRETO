"""
Insights API Schemas for PRETO

Phase 3.2: Claude AI Integration
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class AnalyzeRepositoriesRequest(BaseModel):
    """Request to analyze repositories."""
    repositories: List[Dict] = Field(..., description="List of repository objects")
    analysis_type: str = Field(
        default="general",
        description="Type of analysis: general, security, trending, quality"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "repositories": [
                    {
                        "name": "linux",
                        "language": "C",
                        "stargazers_count": 170000
                    }
                ],
                "analysis_type": "general"
            }
        }


class AnalyzeRepositoriesResponse(BaseModel):
    """Response from repository analysis."""
    status: str = Field(..., description="Status of analysis")
    analysis_type: str = Field(..., description="Type of analysis performed")
    analysis: str = Field(..., description="Analysis results from Claude")
    repository_count: int = Field(..., description="Number of repositories analyzed")
    timestamp: datetime = Field(..., description="When analysis was performed")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "analysis_type": "general",
                "analysis": "Repository analysis...",
                "repository_count": 5,
                "timestamp": "2026-06-05T12:00:00"
            }
        }


class NaturalLanguageQueryRequest(BaseModel):
    """Request for natural language query."""
    query: str = Field(..., min_length=1, description="Natural language question")
    context: Optional[Dict] = Field(None, description="Optional context data")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What are the most popular technologies in these repositories?",
                "context": {
                    "repositories": [],
                    "user": "torvalds"
                }
            }
        }


class NaturalLanguageQueryResponse(BaseModel):
    """Response to natural language query."""
    status: str = Field(..., description="Status")
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Answer from Claude")
    timestamp: datetime = Field(..., description="When query was processed")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "query": "What are the most popular technologies?",
                "answer": "Based on the data...",
                "timestamp": "2026-06-05T12:00:00"
            }
        }


class SearchInsightRequest(BaseModel):
    """Request for search insights."""
    search_query: str = Field(..., description="Search query")
    results: List[Dict] = Field(..., description="Search results")
    
    class Config:
        schema_extra = {
            "example": {
                "search_query": "machine learning",
                "results": []
            }
        }


class SearchInsightResponse(BaseModel):
    """Insights about search results."""
    status: str = Field(..., description="Status")
    search_query: str = Field(..., description="Search query")
    insight: str = Field(..., description="Insight about results")
    key_findings: List[str] = Field(..., description="Key findings")
    timestamp: datetime = Field(..., description="When insight was generated")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "search_query": "machine learning",
                "insight": "Insights about ML repos...",
                "key_findings": ["Finding 1", "Finding 2"],
                "timestamp": "2026-06-05T12:00:00"
            }
        }


class UserAnalysisRequest(BaseModel):
    """Request for user profile analysis."""
    username: str = Field(..., description="GitHub username")
    repositories: List[Dict] = Field(..., description="User's repositories")
    statistics: Optional[Dict] = Field(None, description="User statistics")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "torvalds",
                "repositories": [],
                "statistics": {}
            }
        }


class UserAnalysisResponse(BaseModel):
    """Analysis of GitHub user."""
    status: str = Field(..., description="Status")
    username: str = Field(..., description="GitHub username")
    analysis: str = Field(..., description="Analysis from Claude")
    expertise_areas: List[str] = Field(..., description="Identified expertise areas")
    contribution_style: str = Field(..., description="Contribution style")
    timestamp: datetime = Field(..., description="When analysis was performed")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "username": "torvalds",
                "analysis": "User analysis...",
                "expertise_areas": ["Systems", "C"],
                "contribution_style": "Focused",
                "timestamp": "2026-06-05T12:00:00"
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""
    status: str = Field(default="error")
    error: str = Field(..., description="Error message")
    timestamp: datetime = Field(..., description="When error occurred")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "error",
                "error": "Claude API key not configured",
                "timestamp": "2026-06-05T12:00:00"
            }
        }
