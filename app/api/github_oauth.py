"""
GitHub OAuth2 Integration for PRETO

Handles GitHub OAuth flow to get user tokens with 5000 req/hr rate limit.
Uses manual OAuth flow — no extra dependencies needed.

Flow:
  1. GET /api/auth/github              → redirect to GitHub
  2. GitHub redirects to /api/auth/github/callback?code=xxx
  3. Backend exchanges code for access_token
  4. Creates/updates PRETO user linked to GitHub account
  5. Returns JWT + github_token stored in DB

Author: TANGO
"""

import os
import logging
import httpx
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from .auth import (
    create_access_token,
    create_refresh_token,
    get_db,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["github-oauth"])

GITHUB_OAUTH_AUTHORIZE = "https://github.com/login/oauth/authorize"
GITHUB_OAUTH_TOKEN     = "https://github.com/login/oauth/access_token"
GITHUB_API_USER        = "https://api.github.com/user"
GITHUB_API_EMAILS      = "https://api.github.com/user/emails"

# ── Read config lazily so load_dotenv() in main.py runs first ────────────
def _cfg():
    return {
        "client_id":     os.getenv("GITHUB_CLIENT_ID", ""),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
        "redirect_uri":  os.getenv("GITHUB_REDIRECT_URI",  "http://localhost:8000/api/auth/github/callback"),
        "frontend_url":  os.getenv("FRONTEND_URL",          "http://localhost:5173"),
    }

# ── OAuth routes ────────────────────────────────────────────────────────────

@router.get("/github")
async def github_login():
    cfg = _cfg()
    if not cfg["client_id"]:
        raise HTTPException(
            status_code=501,
            detail="GitHub OAuth not configured. Add GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET to .env"
        )
    params = (
        f"client_id={cfg['client_id']}"
        f"&redirect_uri={cfg['redirect_uri']}"
        f"&scope=read:user+user:email+public_repo"
        f"&allow_signup=true"
    )
    return RedirectResponse(f"{GITHUB_OAUTH_AUTHORIZE}?{params}")


@router.get("/github/callback")
async def github_callback(
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Handle GitHub OAuth callback.
    Exchanges code for access token, creates/updates user, returns JWT.
    """
    if error:
        logger.warning(f"GitHub OAuth error: {error}")
        return RedirectResponse(f"{_cfg()['frontend_url']}/auth?error={error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    cfg = _cfg()

    # Step 1: Exchange code for GitHub access token
    github_token = await _exchange_code_for_token(code, cfg)
    if not github_token:
        return RedirectResponse(f"{cfg['frontend_url']}/auth?error=token_exchange_failed")

    # Step 2: Fetch GitHub user profile
    github_user = await _fetch_github_user(github_token)
    if not github_user:
        return RedirectResponse(f"{cfg['frontend_url']}/auth?error=profile_fetch_failed")

    # Step 3: Get email (may be private on profile)
    email = github_user.get("email") or await _fetch_github_primary_email(github_token)
    if not email:
        email = f"{github_user['login']}@github.noreply"

    # Step 4: Create or update PRETO user
    user = _upsert_github_user(db, github_user, email, github_token)

    # Step 5: Create PRETO JWT
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(data={"sub": user.username})

    logger.info(f"GitHub OAuth success: {user.username} (gh:{github_user['login']})")

    return RedirectResponse(
        f"{cfg['frontend_url']}/auth/callback"
        f"#access_token={access_token}"
        f"&refresh_token={refresh_token}"
        f"&username={user.username}"
    )


@router.get("/github/status")
async def github_oauth_status():
    cfg = _cfg()
    configured = bool(cfg["client_id"] and cfg["client_secret"])
    return {
        "configured": configured,
        "client_id_set": bool(cfg["client_id"]),
        "redirect_uri": cfg["redirect_uri"],
        "message": (
            "GitHub OAuth ready" if configured
            else "Add GITHUB_CLIENT_ID + GITHUB_CLIENT_SECRET to .env. "
                 "Create app at https://github.com/settings/developers"
        )
    }


# ── Internal helpers ─────────────────────────────────────────────────────────

async def _exchange_code_for_token(code: str, cfg: dict) -> Optional[str]:
    """Exchange OAuth code for GitHub access token."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                GITHUB_OAUTH_TOKEN,
                json={
                    "client_id":     cfg["client_id"],
                    "client_secret": cfg["client_secret"],
                    "code":          code,
                    "redirect_uri":  cfg["redirect_uri"],
                },
                headers={"Accept": "application/json"}
            )
            data = resp.json()
            token = data.get("access_token")
            if not token:
                logger.error(f"GitHub token exchange failed: {data}")
            return token
    except Exception as e:
        logger.error(f"GitHub token exchange error: {e}")
        return None


async def _fetch_github_user(token: str) -> Optional[dict]:
    """Fetch GitHub user profile using access token."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                GITHUB_API_USER,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                }
            )
            if resp.status_code == 200:
                return resp.json()
            logger.error(f"GitHub user fetch failed: {resp.status_code}")
            return None
    except Exception as e:
        logger.error(f"GitHub user fetch error: {e}")
        return None


async def _fetch_github_primary_email(token: str) -> Optional[str]:
    """Fetch primary email from GitHub (handles private emails)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                GITHUB_API_EMAILS,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                }
            )
            if resp.status_code == 200:
                emails = resp.json()
                # Find primary email
                for e in emails:
                    if e.get("primary") and e.get("verified"):
                        return e["email"]
                # Fallback: first verified
                for e in emails:
                    if e.get("verified"):
                        return e["email"]
            return None
    except Exception as e:
        logger.error(f"GitHub email fetch error: {e}")
        return None


def _upsert_github_user(db: Session, github_user: dict, email: str, github_token: str):
    """Create or update a PRETO user from GitHub OAuth data."""
    from app.models.auth import User
    import hashlib
    import secrets

    login    = github_user["login"]
    gh_id    = str(github_user["id"])
    username = f"gh_{login}"  # prefix to avoid collisions with manual accounts

    # Try find by github_id first, then by username
    user = (
        db.query(User).filter(User.github_id == gh_id).first()
        or db.query(User).filter(User.username == username).first()
    )

    if user:
        # Update token + profile
        user.github_token  = github_token
        user.github_id     = gh_id
        user.github_login  = login
        user.avatar_url    = github_user.get("avatar_url", "")
        user.last_login    = datetime.utcnow()
        db.commit()
        db.refresh(user)
        logger.info(f"GitHub user updated: {username}")
    else:
        # Create new PRETO user
        # Give them a random password they can never use directly
        random_pw_hash = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
        user = User(
            username       = username,
            email          = email,
            hashed_password= random_pw_hash,
            full_name      = github_user.get("name", login),
            github_id      = gh_id,
            github_login   = login,
            github_token   = github_token,
            avatar_url     = github_user.get("avatar_url", ""),
            is_active      = True,
            last_login     = datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"GitHub user created: {username}")

    return user
