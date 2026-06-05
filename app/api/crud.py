"""
CRUD operations for database models

Phase 2.1: Data Persistence

Author: TANGO
Last Updated: June 5, 2026
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timedelta
import logging
from typing import List, Optional, Dict

from app.models import (
    Repository,
    GitHubUser,
    Search,
    UserStatistics,
    CacheEntry
)

logger = logging.getLogger(__name__)


# ============================================================================
# Repository CRUD Operations
# ============================================================================

def create_repository(db: Session, repo_data: Dict) -> Repository:
    """Create a new repository record."""
    try:
        repo = Repository(**repo_data)
        db.add(repo)
        db.commit()
        db.refresh(repo)
        logger.info(f"Repository created: {repo.full_name}")
        return repo
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating repository: {str(e)}")
        raise


def create_repositories_batch(db: Session, repos_data: List[Dict]) -> int:
    """Create multiple repositories at once."""
    try:
        count = 0
        for repo_data in repos_data:
            try:
                repo = Repository(**repo_data)
                db.add(repo)
                count += 1
            except Exception as e:
                logger.warning(f"Skipping repository: {str(e)}")
                continue
        
        db.commit()
        logger.info(f"Batch created {count} repositories")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Error in batch creation: {str(e)}")
        raise


def get_repository(db: Session, repo_id: int) -> Optional[Repository]:
    """Get repository by ID."""
    return db.query(Repository).filter(Repository.id == repo_id).first()


def get_repository_by_fullname(db: Session, full_name: str) -> Optional[Repository]:
    """Get repository by full name (owner/repo)."""
    return db.query(Repository).filter(Repository.full_name == full_name).first()


def get_repositories_by_language(db: Session, language: str, limit: int = 100) -> List[Repository]:
    """Get repositories by language."""
    return db.query(Repository).filter(
        Repository.language == language
    ).order_by(desc(Repository.stargazers_count)).limit(limit).all()


def update_repository(db: Session, repo_id: int, update_data: Dict) -> Optional[Repository]:
    """Update repository data."""
    try:
        repo = get_repository(db, repo_id)
        if not repo:
            return None
        
        for key, value in update_data.items():
            setattr(repo, key, value)
        
        repo.last_synced = datetime.utcnow()
        db.commit()
        db.refresh(repo)
        logger.info(f"Repository updated: {repo.full_name}")
        return repo
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating repository: {str(e)}")
        raise


def delete_repository(db: Session, repo_id: int) -> bool:
    """Delete repository."""
    try:
        repo = get_repository(db, repo_id)
        if not repo:
            return False
        
        db.delete(repo)
        db.commit()
        logger.info(f"Repository deleted: {repo.full_name}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting repository: {str(e)}")
        raise


# ============================================================================
# GitHub User CRUD Operations
# ============================================================================

def create_github_user(db: Session, user_data: Dict) -> GitHubUser:
    """Create a new GitHub user record."""
    try:
        user = GitHubUser(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"GitHub user created: {user.username}")
        return user
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating GitHub user: {str(e)}")
        raise


def get_github_user(db: Session, username: str) -> Optional[GitHubUser]:
    """Get GitHub user by username."""
    return db.query(GitHubUser).filter(GitHubUser.username == username).first()


def update_github_user(db: Session, username: str, update_data: Dict) -> Optional[GitHubUser]:
    """Update GitHub user data."""
    try:
        user = get_github_user(db, username)
        if not user:
            return None
        
        for key, value in update_data.items():
            setattr(user, key, value)
        
        user.last_synced = datetime.utcnow()
        db.commit()
        db.refresh(user)
        logger.info(f"GitHub user updated: {username}")
        return user
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating GitHub user: {str(e)}")
        raise


# ============================================================================
# Search CRUD Operations
# ============================================================================

def create_search(db: Session, search_data: Dict) -> Search:
    """Create a new search record."""
    try:
        search = Search(**search_data)
        db.add(search)
        db.commit()
        db.refresh(search)
        logger.info(f"Search created: {search.query}")
        return search
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating search: {str(e)}")
        raise


def get_search_history(db: Session, query: str, limit: int = 10) -> List[Search]:
    """Get search history for a query."""
    return db.query(Search).filter(
        Search.query == query
    ).order_by(desc(Search.created_at)).limit(limit).all()


def get_recent_searches(db: Session, limit: int = 20) -> List[Search]:
    """Get recent searches."""
    return db.query(Search).order_by(desc(Search.created_at)).limit(limit).all()


# ============================================================================
# User Statistics CRUD Operations
# ============================================================================

def create_user_statistics(db: Session, stats_data: Dict) -> UserStatistics:
    """Create user statistics record."""
    try:
        stats = UserStatistics(**stats_data)
        db.add(stats)
        db.commit()
        db.refresh(stats)
        logger.info(f"User statistics created: {stats.username}")
        return stats
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user statistics: {str(e)}")
        raise


def get_user_statistics(db: Session, username: str) -> Optional[UserStatistics]:
    """Get user statistics."""
    return db.query(UserStatistics).filter(UserStatistics.username == username).first()


def update_user_statistics(db: Session, username: str, stats_data: Dict) -> Optional[UserStatistics]:
    """Update user statistics."""
    try:
        stats = get_user_statistics(db, username)
        if stats:
            for key, value in stats_data.items():
                setattr(stats, key, value)
            stats.last_updated = datetime.utcnow()
        else:
            stats_data['username'] = username
            stats = create_user_statistics(db, stats_data)
        
        db.commit()
        db.refresh(stats)
        logger.info(f"User statistics updated: {username}")
        return stats
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user statistics: {str(e)}")
        raise


# ============================================================================
# Cache CRUD Operations
# ============================================================================

def create_cache_entry(db: Session, cache_key: str, cache_type: str, 
                      cache_data: Dict, ttl_minutes: int = 60) -> CacheEntry:
    """Create cache entry with expiration."""
    try:
        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        cache = CacheEntry(
            cache_key=cache_key,
            cache_type=cache_type,
            cache_data=cache_data,
            expires_at=expires_at
        )
        db.add(cache)
        db.commit()
        db.refresh(cache)
        logger.info(f"Cache entry created: {cache_key} (expires in {ttl_minutes}m)")
        return cache
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating cache entry: {str(e)}")
        raise


def get_cache_entry(db: Session, cache_key: str) -> Optional[CacheEntry]:
    """Get cache entry if not expired."""
    entry = db.query(CacheEntry).filter(CacheEntry.cache_key == cache_key).first()
    
    if not entry:
        return None
    
    # Check if expired
    if entry.expires_at and entry.expires_at < datetime.utcnow():
        logger.info(f"Cache entry expired: {cache_key}")
        delete_cache_entry(db, entry.id)
        return None
    
    logger.info(f"Cache hit: {cache_key}")
    return entry


def delete_cache_entry(db: Session, cache_id: int) -> bool:
    """Delete cache entry."""
    try:
        entry = db.query(CacheEntry).filter(CacheEntry.id == cache_id).first()
        if entry:
            db.delete(entry)
            db.commit()
            logger.info(f"Cache entry deleted: {cache_id}")
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting cache entry: {str(e)}")
        raise


def clear_expired_cache(db: Session) -> int:
    """Clear all expired cache entries."""
    try:
        now = datetime.utcnow()
        count = db.query(CacheEntry).filter(CacheEntry.expires_at < now).delete()
        db.commit()
        logger.info(f"Cleared {count} expired cache entries")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Error clearing expired cache: {str(e)}")
        raise


# ============================================================================
# Utility Functions
# ============================================================================

def get_stats_summary(db: Session) -> Dict:
    """Get database statistics summary."""
    try:
        repos_count = db.query(Repository).count()
        users_count = db.query(GitHubUser).count()
        searches_count = db.query(Search).count()
        cache_count = db.query(CacheEntry).count()
        stats_count = db.query(UserStatistics).count()
        
        return {
            "repositories": repos_count,
            "github_users": users_count,
            "searches": searches_count,
            "cache_entries": cache_count,
            "user_statistics": stats_count,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error getting stats summary: {str(e)}")
        return {}
