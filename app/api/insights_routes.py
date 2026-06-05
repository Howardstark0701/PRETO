"""
Insights Routes for PRETO

Phase 3.2: NVIDIA NIM AI Integration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from .insights import get_insights_manager
from .insights_schemas import (
    AnalyzeRepositoriesRequest,
    AnalyzeRepositoriesResponse,
    NaturalLanguageQueryRequest,
    NaturalLanguageQueryResponse,
    SearchInsightRequest,
    SearchInsightResponse,
    UserAnalysisRequest,
    UserAnalysisResponse,
    ErrorResponse
)
from .auth import get_db, log_search_history

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.post("/analyze", response_model=AnalyzeRepositoriesResponse)
async def analyze_repositories(
    request: AnalyzeRepositoriesRequest,
    current_user = None,
    db: Session = Depends(get_db)
):
    """
    Analyze repositories using NVIDIA NIM.
    
    Args:
        request: Repository data and analysis type
        current_user: Current user (optional)
        db: Database session
    
    Returns:
        AnalyzeRepositoriesResponse: Analysis from NIM (40 req/min rate limit)
    """
    try:
        if not request.repositories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one repository is required"
            )
        
        insights_manager = get_insights_manager()
        analysis = await insights_manager.analyze_repositories(
            request.repositories,
            request.analysis_type
        )
        
        logger.info(f"Repository analysis completed: {request.analysis_type}")
        
        return AnalyzeRepositoriesResponse(
            status="success",
            analysis_type=request.analysis_type,
            analysis=analysis,
            repository_count=len(request.repositories),
            timestamp=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing repositories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/query", response_model=NaturalLanguageQueryResponse)
async def natural_language_query(
    request: NaturalLanguageQueryRequest,
    current_user = None,
    db: Session = Depends(get_db)
):
    """
    Process natural language queries about OSINT data using NVIDIA NIM.
    
    Args:
        request: Query and optional context
        current_user: Current user (optional)
        db: Database session
    
    Returns:
        NaturalLanguageQueryResponse: Answer from NIM (40 req/min rate limit)
    """
    try:
        if not request.query or len(request.query.strip()) < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )
        
        insights_manager = get_insights_manager()
        context = request.context or {}
        
        answer = await insights_manager.query_natural_language(request.query, context)
        
        logger.info(f"Natural language query processed")
        
        return NaturalLanguageQueryResponse(
            status="success",
            query=request.query,
            answer=answer,
            timestamp=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query processing failed: {str(e)}"
        )


@router.post("/search-insights", response_model=SearchInsightResponse)
async def get_search_insights(
    request: SearchInsightRequest,
    current_user = None,
    db: Session = Depends(get_db)
):
    """
    Get insights about search results using NVIDIA NIM.
    
    Args:
        request: Search query and results
        current_user: Current user (optional)
        db: Database session
    
    Returns:
        SearchInsightResponse: Insights about results (40 req/min rate limit)
    """
    try:
        if not request.results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one result is required"
            )
        
        insights_manager = get_insights_manager()
        
        prompt = (
            f"Analyze these search results for '{request.search_query}':\n\n"
            f"Results: {request.results[:5]}\n\n"  # Limit to first 5
            f"Provide 3 key findings about these results."
        )
        
        # Get insights from NIM
        insights_text = await insights_manager.query_natural_language(
            prompt,
            {"search_query": request.search_query}
        )
        
        # Extract key findings (simple split by numbered list)
        key_findings = [
            f.strip() for f in insights_text.split('\n')
            if f.strip() and any(c.isdigit() for c in f[:3])
        ][:3]
        
        if not key_findings:
            key_findings = [insights_text[:200]]  # Fallback
        
        logger.info(f"Search insights generated for: {request.search_query}")
        
        return SearchInsightResponse(
            status="success",
            search_query=request.search_query,
            insight=insights_text,
            key_findings=key_findings,
            timestamp=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating search insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Insight generation failed: {str(e)}"
        )


@router.post("/user-analysis", response_model=UserAnalysisResponse)
async def analyze_user_profile(
    request: UserAnalysisRequest,
    current_user = None,
    db: Session = Depends(get_db)
):
    """
    Analyze GitHub user's profile and contributions using NVIDIA NIM.
    
    Args:
        request: User data and repositories
        current_user: Current user (optional)
        db: Database session
    
    Returns:
        UserAnalysisResponse: User analysis from NIM (40 req/min rate limit)
    """
    try:
        if not request.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is required"
            )
        
        insights_manager = get_insights_manager()
        
        # Create context for analysis
        context = {
            "username": request.username,
            "repository_count": len(request.repositories),
            "statistics": request.statistics or {},
            "top_repos": sorted(
                request.repositories,
                key=lambda x: x.get('stargazers_count', 0),
                reverse=True
            )[:5]
        }
        
        # Create analysis prompt
        prompt = (
            f"Analyze the GitHub profile of {request.username}:\n\n"
            f"Repositories: {len(request.repositories)}\n"
            f"Statistics: {context['statistics']}\n\n"
            f"Identify expertise areas and contribution style. "
            f"Format as: Expertise areas: [list], Contribution style: [description]"
        )
        
        analysis = await insights_manager.query_natural_language(prompt, context)
        
        # Parse expertise areas from response
        expertise_areas = []
        contribution_style = "Collaborative"
        
        if "Expertise areas:" in analysis:
            parts = analysis.split("Expertise areas:")
            if len(parts) > 1:
                expertise_str = parts[1].split("Contribution style:")[0]
                expertise_areas = [
                    e.strip() for e in expertise_str.split(',')
                    if e.strip()
                ][:5]
        
        if "Contribution style:" in analysis:
            parts = analysis.split("Contribution style:")
            if len(parts) > 1:
                contribution_style = parts[1].strip()[:100]
        
        if not expertise_areas:
            # Fallback: extract from repositories
            languages = set()
            for repo in request.repositories[:10]:
                if repo.get('language'):
                    languages.add(repo.get('language'))
            expertise_areas = list(languages)[:5]
        
        logger.info(f"User analysis completed for: {request.username}")
        
        return UserAnalysisResponse(
            status="success",
            username=request.username,
            analysis=analysis,
            expertise_areas=expertise_areas or ["Developer"],
            contribution_style=contribution_style,
            timestamp=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User analysis failed: {str(e)}"
        )


@router.get("/health")
async def insights_health():
    """Health check for insights service - NVIDIA NIM."""
    insights_manager = get_insights_manager()
    has_api_key = insights_manager.client is not None
    rate_limit_stats = insights_manager.rate_limiter.get_stats()
    
    return {
        "status": "healthy",
        "insights_service": "NVIDIA NIM",
        "nim_configured": has_api_key,
        "fallback_mode": not has_api_key,
        "rate_limit": rate_limit_stats,
        "rate_limit_per_minute": 40,
        "timestamp": datetime.utcnow()
    }
