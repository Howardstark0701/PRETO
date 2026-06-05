"""
Authentication utilities for PRETO

Phase 3.1: User Authentication (Simplified - minimal dependencies)

Author: TANGO
Last Updated: June 5, 2026
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import json
import base64
import hmac
import hashlib

from app.models import SessionLocal

logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = "preto-secret-key-change-in-production-9d8f7e6c5b4a3z2x1w0v"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ============================================================================
# Helper to extract bearer token from header
# ============================================================================

async def extract_bearer_token(authorization: Optional[str] = Header(None)) -> str:
    """Extract bearer token from authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    return authorization[7:]  # Remove "Bearer " prefix


# ============================================================================
# Password Utilities (Simple SHA256 - upgrade to bcrypt in production)
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return hash_password(plain_password) == hashed_password


# ============================================================================
# JWT Token Utilities (Simplified - no external JWT library)
# ============================================================================

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT-like access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire.timestamp()})
    
    # Simple JWT implementation
    header = {"alg": "HS256", "typ": "JWT"}
    payload = to_encode
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    
    message = f"{header_b64}.{payload_b64}"
    signature = base64.urlsafe_b64encode(
        hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
    ).decode().rstrip('=')
    
    token = f"{message}.{signature}"
    logger.info(f"Access token created for user: {data.get('sub')}")
    
    return token


def create_refresh_token(data: Dict) -> str:
    """Create JWT-like refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire.timestamp(), "type": "refresh"})
    
    header = {"alg": "HS256", "typ": "JWT"}
    payload = to_encode
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    
    message = f"{header_b64}.{payload_b64}"
    signature = base64.urlsafe_b64encode(
        hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
    ).decode().rstrip('=')
    
    token = f"{message}.{signature}"
    logger.info(f"Refresh token created for user: {data.get('sub')}")
    
    return token


def verify_token(token: str) -> Dict:
    """Verify and decode JWT-like token."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        
        header_b64, payload_b64, signature = parts
        
        # Verify signature
        message = f"{header_b64}.{payload_b64}"
        expected_signature = base64.urlsafe_b64encode(
            hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
        ).decode().rstrip('=')
        
        if signature != expected_signature:
            raise ValueError("Invalid token signature")
        
        # Decode payload
        payload_json = base64.urlsafe_b64decode(payload_b64 + '==')
        payload = json.loads(payload_json)
        
        # Check expiration
        if payload.get("exp", 0) < datetime.utcnow().timestamp():
            logger.warning("Token verification failed: token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token verification failed: no username in payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return payload
    
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# ============================================================================
# Dependency Functions
# ============================================================================

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(extract_bearer_token),
    db: Session = Depends(get_db)
):
    """Get current authenticated user."""
    payload = verify_token(token)
    username: str = payload.get("sub")
    
    # Import here to avoid circular imports
    from app.models.auth import User
    
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        logger.warning(f"User not found: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        logger.warning(f"User inactive: {username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_admin_user(current_user = Depends(get_current_user)):
    """Get current admin user."""
    if not current_user.is_admin:
        logger.warning(f"Non-admin user tried to access admin resource: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


# ============================================================================
# User CRUD Operations
# ============================================================================

def create_user(db: Session, username: str, email: str, password: str, full_name: str = None) -> 'User':
    """Create a new user."""
    from app.models.auth import User
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        logger.warning(f"User creation failed: username or email already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )
    
    # Create new user
    hashed_pwd = hash_password(password)
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_pwd,
        full_name=full_name
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    logger.info(f"User created: {username}")
    return db_user


def get_user_by_username(db: Session, username: str) -> Optional['User']:
    """Get user by username."""
    from app.models.auth import User
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional['User']:
    """Authenticate user by username and password."""
    user = get_user_by_username(db, username)
    
    if not user:
        logger.warning(f"Authentication failed: user not found: {username}")
        return None
    
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed: invalid password for user: {username}")
        return None
    
    logger.info(f"User authenticated: {username}")
    return user


def update_last_login(db: Session, user: 'User') -> 'User':
    """Update user's last login timestamp."""
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


# ============================================================================
# Saved Search Operations
# ============================================================================

def create_saved_search(
    db: Session,
    user_id: int,
    query: str,
    language: str = None,
    filters: str = None,
    description: str = None
) -> 'SavedSearch':
    """Create a saved search."""
    from app.models.auth import SavedSearch
    
    saved_search = SavedSearch(
        user_id=user_id,
        query=query,
        language=language,
        filters=filters,
        description=description
    )
    
    db.add(saved_search)
    db.commit()
    db.refresh(saved_search)
    
    logger.info(f"Saved search created: user_id={user_id}, query='{query}'")
    return saved_search


def get_user_saved_searches(db: Session, user_id: int):
    """Get all saved searches for a user."""
    from app.models.auth import SavedSearch
    
    return db.query(SavedSearch).filter(
        SavedSearch.user_id == user_id
    ).order_by(SavedSearch.created_at.desc()).all()


def delete_saved_search(db: Session, search_id: int, user_id: int) -> bool:
    """Delete a saved search."""
    from app.models.auth import SavedSearch
    
    search = db.query(SavedSearch).filter(
        (SavedSearch.id == search_id) & (SavedSearch.user_id == user_id)
    ).first()
    
    if not search:
        return False
    
    db.delete(search)
    db.commit()
    logger.info(f"Saved search deleted: id={search_id}")
    return True


def toggle_search_favorite(db: Session, search_id: int, user_id: int) -> Optional['SavedSearch']:
    """Toggle search as favorite."""
    from app.models.auth import SavedSearch
    
    search = db.query(SavedSearch).filter(
        (SavedSearch.id == search_id) & (SavedSearch.user_id == user_id)
    ).first()
    
    if not search:
        return None
    
    search.is_favorite = not search.is_favorite
    db.commit()
    db.refresh(search)
    
    logger.info(f"Search favorite toggled: id={search_id}, favorite={search.is_favorite}")
    return search


# ============================================================================
# Search History Operations
# ============================================================================

def log_search_history(
    db: Session,
    user_id: int,
    query: str,
    results_count: int = 0,
    execution_time_ms: int = 0,
    used_cache: bool = False
) -> 'UserSearchHistory':
    """Log a search to user history."""
    from app.models.auth import UserSearchHistory
    
    history = UserSearchHistory(
        user_id=user_id,
        query=query,
        results_count=results_count,
        execution_time_ms=execution_time_ms,
        used_cache=used_cache
    )
    
    db.add(history)
    db.commit()
    db.refresh(history)
    
    return history


def get_user_search_history(db: Session, user_id: int, limit: int = 50):
    """Get user's search history."""
    from app.models.auth import UserSearchHistory
    
    return db.query(UserSearchHistory).filter(
        UserSearchHistory.user_id == user_id
    ).order_by(UserSearchHistory.created_at.desc()).limit(limit).all()


def clear_search_history(db: Session, user_id: int) -> int:
    """Clear user's search history."""
    from app.models.auth import UserSearchHistory
    
    count = db.query(UserSearchHistory).filter(
        UserSearchHistory.user_id == user_id
    ).delete()
    
    db.commit()
    logger.info(f"Search history cleared: user_id={user_id}, deleted={count}")
    return count
