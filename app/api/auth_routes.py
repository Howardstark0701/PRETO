"""
Authentication Routes for PRETO

Phase 3.1: User Authentication

Author: TANGO
Last Updated: June 5, 2026
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from .auth import (
    create_user,
    authenticate_user,
    get_current_user,
    create_access_token,
    create_refresh_token,
    verify_token,
    update_last_login,
    get_db,
    create_saved_search,
    get_user_saved_searches,
    delete_saved_search,
    toggle_search_favorite,
    log_search_history,
    get_user_search_history,
    clear_search_history,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from .auth_schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    TokenRefresh,
    UserResponse,
    UserProfile,
    SavedSearchCreate,
    SavedSearchUpdate,
    SavedSearchResponse,
    SavedSearchList,
    SearchHistoryResponse,
    SearchHistoryList,
    ErrorResponse,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/auth", tags=["authentication"])


# ============================================================================
# Authentication Endpoints
# ============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Args:
        user_data: User registration data (username, email, password, full_name)
    
    Returns:
        UserResponse: Created user information
    
    Raises:
        400: Username or email already exists
    """
    try:
        logger.info(f"Registration attempt for: {user_data.username}")
        
        # Validate input
        if len(user_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters"
            )
        
        # Create user
        user = create_user(
            db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        logger.info(f"User registered: {user.username}")
        return user
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login user and get access token.
    
    Args:
        credentials: Username/email and password
    
    Returns:
        TokenResponse: Access token, refresh token, and user info
    
    Raises:
        401: Invalid credentials
    """
    try:
        logger.info(f"Login attempt for: {credentials.username}")
        
        # Authenticate user
        user = authenticate_user(db, credentials.username, credentials.password)
        
        if not user:
            logger.warning(f"Login failed: invalid credentials for {credentials.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Update last login
        user = update_last_login(db, user)
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(data={"sub": user.username})
        
        logger.info(f"User logged in: {user.username}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse.model_validate(user)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Args:
        token_data: Refresh token
    
    Returns:
        TokenResponse: New access token
    
    Raises:
        401: Invalid or expired refresh token
    """
    try:
        payload = verify_token(token_data.refresh_token)
        username = payload.get("sub")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        access_token = create_access_token(
            data={"sub": username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        logger.info(f"Token refreshed for: {username}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=token_data.refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=0,
                username=username,
                email="",
                full_name=None,
                is_active=True,
                created_at=None,
                last_login=None
            )
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


# ============================================================================
# User Profile Endpoints
# ============================================================================

@router.get("/me", response_model=UserProfile)
async def get_profile(
    current_user = Depends(get_current_user)
):
    """Get current user profile."""
    logger.info(f"Profile accessed: {current_user.username}")
    return current_user


@router.get("/users/{username}", response_model=UserResponse)
async def get_user_public_profile(
    username: str,
    db: Session = Depends(get_db)
):
    """
    Get public user profile (limited info).
    
    Args:
        username: Username to get profile for
    
    Returns:
        UserResponse: User information
    """
    from app.api.auth import get_user_by_username
    
    user = get_user_by_username(db, username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


# ============================================================================
# Saved Search Endpoints
# ============================================================================

@router.post("/saved-searches", response_model=SavedSearchResponse, status_code=status.HTTP_201_CREATED)
async def create_saved_search_endpoint(
    search_data: SavedSearchCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Save a search for later use.
    
    Args:
        search_data: Search query and parameters
    
    Returns:
        SavedSearchResponse: Saved search information
    """
    try:
        saved_search = create_saved_search(
            db,
            user_id=current_user.id,
            query=search_data.query,
            language=search_data.language,
            filters=search_data.filters,
            description=search_data.description
        )
        
        logger.info(f"Search saved: user={current_user.username}, query='{search_data.query}'")
        return saved_search
    
    except Exception as e:
        logger.error(f"Error saving search: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save search"
        )


@router.get("/saved-searches", response_model=SavedSearchList)
async def list_saved_searches(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's saved searches."""
    searches = get_user_saved_searches(db, current_user.id)
    
    return SavedSearchList(
        total=len(searches),
        searches=searches
    )


@router.get("/saved-searches/{search_id}", response_model=SavedSearchResponse)
async def get_saved_search(
    search_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific saved search."""
    from app.models.auth import SavedSearch
    
    search = db.query(SavedSearch).filter(
        (SavedSearch.id == search_id) & (SavedSearch.user_id == current_user.id)
    ).first()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    return search


@router.put("/saved-searches/{search_id}", response_model=SavedSearchResponse)
async def update_saved_search(
    search_id: int,
    update_data: SavedSearchUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update saved search."""
    from app.models.auth import SavedSearch
    
    search = db.query(SavedSearch).filter(
        (SavedSearch.id == search_id) & (SavedSearch.user_id == current_user.id)
    ).first()
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    if update_data.description is not None:
        search.description = update_data.description
    
    db.commit()
    db.refresh(search)
    
    return search


@router.delete("/saved-searches/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_search_endpoint(
    search_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete saved search."""
    success = delete_saved_search(db, search_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )


@router.post("/saved-searches/{search_id}/favorite", response_model=SavedSearchResponse)
async def toggle_favorite(
    search_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle search as favorite."""
    from app.api.auth import toggle_search_favorite
    
    search = toggle_search_favorite(db, search_id, current_user.id)
    
    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found"
        )
    
    return search


# ============================================================================
# Search History Endpoints
# ============================================================================

@router.get("/search-history", response_model=SearchHistoryList)
async def get_history(
    limit: int = 50,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's search history."""
    history = get_user_search_history(db, current_user.id, limit)
    
    return SearchHistoryList(
        total=len(history),
        history=history
    )


@router.delete("/search-history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_history(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear user's search history."""
    clear_search_history(db, current_user.id)
