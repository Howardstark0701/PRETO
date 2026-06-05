"""
Authentication Models for PRETO

Phase 3.1: User Authentication

Author: TANGO
Last Updated: June 5, 2026
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from datetime import datetime
import logging

from .database import Base

logger = logging.getLogger(__name__)


class User(Base):
    """User model - stores authenticated user accounts."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_admin = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_username_active', 'username', 'is_active'),
        Index('idx_email_active', 'email', 'is_active'),
    )
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class SavedSearch(Base):
    """Saved search model - stores user's saved searches."""
    
    __tablename__ = "saved_searches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    query = Column(String(256), nullable=False)
    language = Column(String(50), nullable=True)
    filters = Column(String(512), nullable=True)  # JSON string of filters
    description = Column(String(512), nullable=True)
    is_favorite = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_executed = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_user_id_fav', 'user_id', 'is_favorite'),
    )
    
    def __repr__(self):
        return f"<SavedSearch(user_id={self.user_id}, query='{self.query}')>"


class UserSearchHistory(Base):
    """User search history model - tracks all user searches."""
    
    __tablename__ = "user_search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    query = Column(String(256), nullable=False)
    results_count = Column(Integer, default=0)
    execution_time_ms = Column(Integer, default=0)
    used_cache = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_search_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<UserSearchHistory(user_id={self.user_id}, query='{self.query}')>"


# Export models
__all__ = [
    'User',
    'SavedSearch',
    'UserSearchHistory'
]
