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
import os
import secrets

try:
    import bcrypt  # Phase 4: Production security upgrade
except ImportError:
    bcrypt = None

from app.models import SessionLocal

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_SECRET_KEY = "preto-dev-secret-change-before-production"
SECRET_KEY = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7

if SECRET_KEY == DEFAULT_SECRET_KEY:
    logger.warning("Using default development SECRET_KEY; set SECRET_KEY in production")

if bcrypt is None:
    logger.warning("bcrypt is not installed; using PBKDF2 fallback for local development")


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
# Password Utilities (bcrypt - Phase 4 Production Security)
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt (Phase 4 upgrade from SHA256)."""
    if bcrypt is None:
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            200_000,
        ).hex()
        return f"pbkdf2_sha256${salt}${digest}"

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash."""
    if hashed_password.startswith("pbkdf2_sha256$"):
        try:
            _, salt, expected = hashed_password.split("$", 2)
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt.encode("utf-8"),
                200_000,
            ).hex()
            return hmac.compare_digest(digest, expected)
        except ValueError:
            return False

    try:
        if bcrypt is not None:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:

        pass

    # Fallback for legacy SHA256 hashes (for migration period)
    legacy_hash = hashlib.sha256((plain_password + SECRET_KEY).encode()).hexdigest()
    if legacy_hash == hashed_password:
        logger.info("Legacy SHA256 password found, migrating to stronger hash")
        return True
    return False


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
    
    # Phase 4: Auto-migrate legacy SHA256 passwords to bcrypt
    if user.hashed_password.startswith(hashlib.sha256((password + SECRET_KEY).encode()).hexdigest()[:10]):
        logger.info(f"Migrating legacy password to bcrypt for user: {username}")
        user.hashed_password = hash_password(password)
        db.commit()
        db.refresh(user)
    
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
# ============================================================================
# API Key Authentication (Phase 4)
# ============================================================================

def create_api_key(db: Session, user_id: int, name: str, rate_limit: int = 100, days_until_expiry: int = None) -> tuple:
    """Create a new API key for a user.
    
    Returns:
        tuple: (APIKey object, raw_api_key)
    """
    from app.models.auth import APIKey
    
    # Generate key
    raw_key = APIKey.generate_key()
    key_hash = APIKey.hash_key(raw_key)
    prefix = APIKey.get_prefix(raw_key)
    
    # Set expiration if specified
    expires_at = None
    if days_until_expiry:
        expires_at = datetime.utcnow() + timedelta(days=days_until_expiry)
    
    api_key = APIKey(
        user_id=user_id,
        name=name,
        key_hash=key_hash,
        prefix=prefix,
        rate_limit=rate_limit,
        expires_at=expires_at
    )
    
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    logger.info(f"API key created: user_id={user_id}, name='{name}', prefix='{prefix}'")
    return api_key, raw_key


def verify_api_key(db: Session, raw_key: str) -> Optional['User']:
    """Verify an API key and return the associated user.
    
    Returns:
        User if valid, None otherwise
    """
    from app.models.auth import APIKey
    
    if not raw_key or not raw_key.startswith("pto_"):
        return None
    
    key_hash = APIKey.hash_key(raw_key)
    
    api_key = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    
    if not api_key:
        logger.warning(f"API key verification failed: key not found")
        return None
    
    if not api_key.is_active:
        logger.warning(f"API key verification failed: key is inactive")
        return None
    
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        logger.warning(f"API key verification failed: key expired")
        return None
    
    # Update last used
    api_key.last_used = datetime.utcnow()
    db.commit()
    
    # Get associated user
    from app.models.auth import User
    user = db.query(User).filter(User.id == api_key.user_id).first()
    
    if not user or not user.is_active:
        logger.warning(f"API key verification failed: user not found or inactive")
        return None
    
    logger.info(f"API key verified: user={user.username}, key_prefix={api_key.prefix}")
    return user


def get_user_api_keys(db: Session, user_id: int):
    """Get all API keys for a user (without showing the actual keys)."""
    from app.models.auth import APIKey
    
    return db.query(APIKey).filter(APIKey.user_id == user_id).order_by(
        APIKey.created_at.desc()
    ).all()


def delete_api_key(db: Session, key_id: int, user_id: int) -> bool:
    """Delete an API key."""
    from app.models.auth import APIKey
    
    api_key = db.query(APIKey).filter(
        (APIKey.id == key_id) & (APIKey.user_id == user_id)
    ).first()
    
    if not api_key:
        return False
    
    db.delete(api_key)
    db.commit()
    
    logger.info(f"API key deleted: id={key_id}")
    return True


def toggle_api_key(db: Session, key_id: int, user_id: int) -> Optional['APIKey']:
    """Toggle an API key active/inactive."""
    from app.models.auth import APIKey
    
    api_key = db.query(APIKey).filter(
        (APIKey.id == key_id) & (APIKey.user_id == user_id)
    ).first()
    
    if not api_key:
        return None
    
    api_key.is_active = not api_key.is_active
    db.commit()
    db.refresh(api_key)
    
    logger.info(f"API key toggled: id={key_id}, is_active={api_key.is_active}")
    return api_key


async def get_api_key_user(
    api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """Dependency to get user from API key header.
    
    Usage: Add this as a dependency to protected endpoints.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header"
        )
    
    user = verify_api_key(db, api_key)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
    
    return user


# Combined authentication - accepts either Bearer token or API key
async def get_authenticated_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db)
):
    """Dependency that accepts either JWT Bearer token or API key."""
    
    # Try API key first
    if api_key:
        user = verify_api_key(db, api_key)
        if user:
            return user
    
    # Try Bearer token
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        try:
            payload = verify_token(token)
            username = payload.get("sub")
            
            from app.models.auth import User
            user = db.query(User).filter(User.username == username).first()
            
            if user and user.is_active:
                return user
        except Exception:
            pass
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
    )


async def enforce_authenticated_rate_limit(
    current_user = Depends(get_authenticated_user),
):
    """Apply per-user rate limiting to authenticated routes."""
    status_info = check_user_rate_limit(current_user.id)

    if not status_info["allowed"]:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(status_info["limit"]),
                "X-RateLimit-Remaining": str(status_info["remaining"]),
                "X-RateLimit-Reset": str(status_info["reset_in_seconds"]),
            },
        )

    return current_user
# ============================================================================
# Per-User Rate Limiting (Phase 4)
# ============================================================================

from collections import defaultdict
from datetime import datetime, timedelta
import threading

class UserRateLimiter:
    """In-memory rate limiter per user."""
    
    def __init__(self, default_limit: int = 100):
        self.default_limit = default_limit
        self.requests = defaultdict(list)  # user_id -> list of timestamps
        self.lock = threading.Lock()
    
    def is_allowed(self, user_id: int, limit: int = None) -> tuple:
        """Check if request is allowed for user.
        
        Returns:
            tuple: (allowed: bool, remaining: int, reset_seconds: int)
        """
        limit = limit or self.default_limit
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=1)
        
        with self.lock:
            # Clean old requests outside the window
            self.requests[user_id] = [
                ts for ts in self.requests[user_id] 
                if ts > window_start
            ]
            
            # Check if limit exceeded
            if len(self.requests[user_id]) >= limit:
                # Calculate reset time
                oldest = min(self.requests[user_id])
                reset_seconds = int((oldest + timedelta(minutes=1) - now).total_seconds())
                return False, 0, max(1, reset_seconds)
            
            # Add current request
            self.requests[user_id].append(now)
            
            remaining = limit - len(self.requests[user_id])
            return True, remaining, 60
    
    def get_remaining(self, user_id: int, limit: int = None) -> int:
        """Get remaining requests for user in current window."""
        limit = limit or self.default_limit
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=1)
        
        with self.lock:
            self.requests[user_id] = [
                ts for ts in self.requests[user_id] 
                if ts > window_start
            ]
            return max(0, limit - len(self.requests[user_id]))
    
    def reset(self, user_id: int):
        """Reset rate limit for user."""
        with self.lock:
            if user_id in self.requests:
                del self.requests[user_id]


# Global rate limiter instance
user_rate_limiter = UserRateLimiter(default_limit=100)


def check_user_rate_limit(user_id: int, rate_limit: int = None) -> dict:
    """Check rate limit for a user.
    
    Returns dict with:
        - allowed: bool
        - remaining: int
        - reset_in_seconds: int
        - limit: int
    """
    allowed, remaining, reset_seconds = user_rate_limiter.is_allowed(user_id, rate_limit)
    limit = rate_limit or user_rate_limiter.default_limit
    
    return {
        "allowed": allowed,
        "remaining": remaining,
        "reset_in_seconds": reset_seconds,
        "limit": limit
    }


def get_user_rate_limit_status(user_id: int, rate_limit: int = None) -> dict:
    """Get current rate limit status for a user without making a request."""
    limit = rate_limit or user_rate_limiter.default_limit
    remaining = user_rate_limiter.get_remaining(user_id, rate_limit)
    
    return {
        "limit": limit,
        "remaining": remaining,
        "used": limit - remaining,
        "window_seconds": 60
    }
