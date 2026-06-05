"""
Database models for PRETO

Task 2.0: Database Integration

Author: TANGO
Last Updated: June 5, 2026
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Import database configuration
from .database import Base, engine, SessionLocal, get_db, init_db

# Import auth models
from .auth import User, SavedSearch, UserSearchHistory


class Repository(Base):
    """Repository model - stores GitHub repository data."""
    
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    full_name = Column(String(512), unique=True, nullable=False, index=True)
    url = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(50), nullable=True, index=True)
    stargazers_count = Column(Integer, default=0)
    forks_count = Column(Integer, default=0)
    watchers_count = Column(Integer, default=0)
    updated_at = Column(DateTime, nullable=True)
    topics = Column(JSON, default=[])
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_synced = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for search performance
    __table_args__ = (
        Index('idx_language_stars', 'language', 'stargazers_count'),
        Index('idx_full_name', 'full_name'),
    )
    
    def __repr__(self):
        return f"<Repository(full_name='{self.full_name}', stars={self.stargazers_count})>"


class GitHubUser(Base):
    """GitHub user model - stores cached user data."""
    
    __tablename__ = "github_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(39), unique=True, nullable=False, index=True)
    public_repos = Column(Integer, default=0)
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_synced = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<GitHubUser(username='{self.username}', repos={self.public_repos})>"


class Search(Base):
    """Search model - stores search history and results."""
    
    __tablename__ = "searches"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(256), nullable=False)
    language = Column(String(50), nullable=True)
    results_count = Column(Integer, default=0)
    filters_applied = Column(JSON, default={})
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_query_created', 'query', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Search(query='{self.query}', results={self.results_count})>"


class UserStatistics(Base):
    """User statistics model - stores aggregated user stats."""
    
    __tablename__ = "user_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(39), unique=True, nullable=False, index=True)
    total_repositories = Column(Integer, default=0)
    total_stars = Column(Integer, default=0)
    total_forks = Column(Integer, default=0)
    total_watchers = Column(Integer, default=0)
    languages = Column(JSON, default={})
    average_stars_per_repo = Column(Integer, default=0)
    average_forks_per_repo = Column(Integer, default=0)
    most_used_language = Column(String(50), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserStatistics(username='{self.username}', stars={self.total_stars})>"


class CacheEntry(Base):
    """Cache model - stores API response cache."""
    
    __tablename__ = "cache_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(512), unique=True, nullable=False, index=True)
    cache_type = Column(String(50), nullable=False)  # 'user_repos', 'search', 'stats'
    cache_data = Column(JSON, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_cache_key_expires', 'cache_key', 'expires_at'),
    )
    
    def __repr__(self):
        return f"<CacheEntry(key='{self.cache_key}', type='{self.cache_type}')>"


# Export models and database functions
__all__ = [
    'Base',
    'engine',
    'SessionLocal',
    'get_db',
    'init_db',
    'Repository',
    'GitHubUser',
    'Search',
    'UserStatistics',
    'CacheEntry',
    'User',
    'SavedSearch',
    'UserSearchHistory'
]
