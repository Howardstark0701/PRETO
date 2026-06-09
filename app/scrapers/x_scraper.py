"""
X (Twitter) scraper using the Twitter API v2.

Requires X_BEARER_TOKEN in environment variables.
When the token is not configured, returns a clear error payload so the
frontend can display a "token not configured" message rather than crashing.
"""

import httpx
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

X_API_BASE = "https://api.twitter.com/2"

# Fields to request for users and tweets
_USER_FIELDS = "public_metrics,description,created_at,profile_image_url,location,verified,url"
_TWEET_FIELDS = "public_metrics,created_at,author_id,lang,possibly_sensitive"


class XScraper:
    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token or os.getenv("X_BEARER_TOKEN", "").strip()
        if self.bearer_token:
            self.headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "User-Agent": "PRETO/1.0",
            }
        else:
            self.headers = {}

    @property
    def _configured(self) -> bool:
        return bool(self.bearer_token)

    def _no_token_user(self, username: str) -> dict:
        return {
            "username": username,
            "source": "x",
            "error": (
                "X API token not configured. "
                "Add X_BEARER_TOKEN to your .env file to enable X/Twitter lookups. "
                "Get a bearer token at https://developer.twitter.com"
            ),
        }

    async def get_user(self, username: str) -> Optional[dict]:
        """Fetch X/Twitter user profile via API v2."""
        if not self._configured:
            return self._no_token_user(username)

        async with httpx.AsyncClient(headers=self.headers, timeout=12.0) as client:
            try:
                resp = await client.get(
                    f"{X_API_BASE}/users/by/username/{username}",
                    params={"user.fields": _USER_FIELDS},
                )

                # Surface rate-limit and auth errors clearly
                if resp.status_code == 401:
                    return {
                        "username": username,
                        "source": "x",
                        "error": "X bearer token is invalid or expired.",
                    }
                if resp.status_code == 429:
                    return {
                        "username": username,
                        "source": "x",
                        "error": "X API rate limit reached. Please try again in 15 minutes.",
                    }

                resp.raise_for_status()
                data = resp.json().get("data")
                if not data:
                    return None

                metrics = data.get("public_metrics", {})
                return {
                    "username": username,
                    "source": "x",
                    "id": data.get("id"),
                    "display_name": data.get("name"),
                    "description": data.get("description", ""),
                    "location": data.get("location", ""),
                    "url": data.get("url", ""),
                    "verified": data.get("verified", False),
                    "followers_count": metrics.get("followers_count", 0),
                    "following_count": metrics.get("following_count", 0),
                    "tweet_count": metrics.get("tweet_count", 0),
                    "listed_count": metrics.get("listed_count", 0),
                    "created_at": data.get("created_at"),
                    "avatar_url": data.get("profile_image_url", "").replace("_normal", "_400x400"),
                    "profile_url": f"https://x.com/{username}",
                }
            except httpx.HTTPStatusError as exc:
                logger.warning(f"X API error for user {username}: {exc}")
                return None
            except httpx.HTTPError as exc:
                logger.warning(f"X network error for user {username}: {exc}")
                return None

    async def get_tweets(self, username: str, max_results: int = 10) -> list:
        """Fetch X/Twitter user's recent tweets via API v2."""
        if not self._configured:
            return []

        # Cap at API limits (max 100, min 5 for this endpoint)
        max_results = max(5, min(max_results, 100))

        async with httpx.AsyncClient(headers=self.headers, timeout=15.0) as client:
            try:
                # Step 1: resolve username → user ID
                user_resp = await client.get(
                    f"{X_API_BASE}/users/by/username/{username}",
                    params={"user.fields": "id"},
                )
                user_resp.raise_for_status()
                user_id = user_resp.json().get("data", {}).get("id")
                if not user_id:
                    return []

                # Step 2: fetch recent tweets
                tweets_resp = await client.get(
                    f"{X_API_BASE}/users/{user_id}/tweets",
                    params={
                        "max_results": max_results,
                        "tweet.fields": _TWEET_FIELDS,
                        "exclude": "retweets,replies",
                    },
                )

                if tweets_resp.status_code == 429:
                    logger.warning("X API rate limit on tweets endpoint")
                    return []

                tweets_resp.raise_for_status()
                data = tweets_resp.json().get("data") or []

                return [
                    {
                        "id": t.get("id"),
                        "text": t.get("text", ""),
                        "created_at": t.get("created_at"),
                        "lang": t.get("lang", ""),
                        "likes": t.get("public_metrics", {}).get("like_count", 0),
                        "retweets": t.get("public_metrics", {}).get("retweet_count", 0),
                        "replies": t.get("public_metrics", {}).get("reply_count", 0),
                        "impressions": t.get("public_metrics", {}).get("impression_count", 0),
                        "tweet_url": f"https://x.com/{username}/status/{t.get('id')}",
                        "source": "x",
                    }
                    for t in data
                ]
            except httpx.HTTPError as exc:
                logger.warning(f"X API tweets error for {username}: {exc}")
                return []
