"""
Advanced Features Routes for PRETO

Phase 3.3: Advanced Features
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Optional
import logging

from .advanced_features import get_advanced_features_manager
from .auth import get_db, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/advanced", tags=["advanced"])


@router.post("/export")
async def export_results(
    repositories: List[Dict] = None,
    format: str = Query("json", description="Export format: json or csv"),
    current_user = None,
    db: Session = Depends(get_db)
):
    """
    Export search results.
    
    Args:
        repositories: Repositories to export
        format: Format (json or csv)
    
    Returns:
        Exported data
    """
    try:
        if not repositories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Repositories required"
            )
        
        manager = get_advanced_features_manager()
        exported = manager.export_search_results(repositories, format)
        
        media_type = "text/csv" if format == "csv" else "application/json"
        
        return {
            "status": "success",
            "format": format,
            "data": exported,
            "timestamp": datetime.utcnow()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )


@router.post("/analytics")
async def get_analytics(
    repositories: List[Dict],
    period_days: int = Query(30, ge=1, le=365),
    current_user = None,
    db: Session = Depends(get_db)
):
    """
    Generate analytics from repositories.
    
    Args:
        repositories: Repositories to analyze
        period_days: Analysis period
    
    Returns:
        Analytics data
    """
    try:
        if not repositories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Repositories required"
            )
        
        manager = get_advanced_features_manager()
        analytics = manager.generate_analytics(repositories, period_days)
        
        return {
            "status": "success",
            "analytics": analytics,
            "period_days": period_days,
            "timestamp": datetime.utcnow()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics generation failed: {str(e)}"
        )


@router.post("/recommendations")
async def get_recommendations(
    search_history: List[Dict] = None,
    repositories: List[Dict] = None,
    current_user = None,
    db: Session = Depends(get_db)
):
    """
    Get recommendations based on history and data.
    
    Args:
        search_history: User's search history
        repositories: Available repositories
    
    Returns:
        Recommendations list
    """
    try:
        manager = get_advanced_features_manager()
        
        history = search_history or []
        repos = repositories or []
        
        recommendations = manager.get_recommendations(history, repos)
        
        return {
            "status": "success",
            "recommendations": recommendations,
            "count": len(recommendations),
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Recommendation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation generation failed: {str(e)}"
        )


@router.post("/report")
async def generate_report(
    user_id: int,
    search_history: List[Dict],
    repositories: List[Dict],
    current_user = None,
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive user report.
    
    Args:
        user_id: User ID
        search_history: Search history
        repositories: Repositories analyzed
    
    Returns:
        Comprehensive report
    """
    try:
        manager = get_advanced_features_manager()
        analytics = manager.generate_analytics(repositories)
        
        report = manager.generate_report(
            user_id,
            search_history,
            repositories,
            analytics
        )
        
        logger.info(f"Report generated for user: {user_id}")
        
        return {
            "status": "success",
            "report": report,
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}"
        )


@router.post("/compare")
async def compare_searches(
    repositories_1: List[Dict],
    repositories_2: List[Dict],
    current_user = None,
    db: Session = Depends(get_db)
):
    """
    Compare two search results.
    
    Args:
        repositories_1: First search results
        repositories_2: Second search results
    
    Returns:
        Comparison metrics
    """
    try:
        manager = get_advanced_features_manager()
        
        comparison = manager.compare_repositories(repositories_1, repositories_2)
        
        logger.info("Repository comparison completed")
        
        return {
            "status": "success",
            "comparison": comparison,
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Comparison error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison failed: {str(e)}"
        )


@router.get("/search-trends")
async def get_search_trends(
    limit: int = Query(10, ge=1, le=50),
    current_user = None,
    db: Session = Depends(get_db)
):
    """
    Get trending search topics.
    
    Args:
        limit: Number of trends to return
    
    Returns:
        Trending searches
    """
    try:
        from app.models.auth import UserSearchHistory
        
        # Get top searches
        top_searches = db.query(UserSearchHistory.query).with_entities(
            UserSearchHistory.query
        ).group_by(UserSearchHistory.query).order_by(
            db.func.count(UserSearchHistory.id).desc()
        ).limit(limit).all()
        
        trends = [s[0] for s in top_searches]
        
        return {
            "status": "success",
            "trends": trends,
            "count": len(trends),
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Trends error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trends retrieval failed: {str(e)}"
        )
