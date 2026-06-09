"""
Reddit scraper using public JSON API (no OAuth required).

Handles Reddit's aggressive rate-limiting with retries and proper headers.
"""

import httpx
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

REDDIT_API_BASE = "https://www.reddit.com"

# Reddit blocks default user-agent strings; use a descriptive one
_HEADERS = {
    "User-Agent": "PRETO/1.0 OSINT Platform (https://github.com/preto; contact@preto.dev)",
    "Accept": "application/json",
}


async def _reddit_get(client: httpx.AsyncClient, url: str, params: dict = None) -> Optional[dict]:
    """
    Perform a GET to Reddit's public JSON API with a single retry on 429.
    Returns parsed JSON or None on failure.
    """
    for attempt in range(2):
        try:
            resp = await client.get(url, params=params, timeout=12.0)
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", "2"))
                logger.warning(f"Reddit 429 – sleeping {retry_after}s (attempt {attempt+1})")
                await asyncio.sleep(retry_after)
                continue
            resp.raise_for_status()
            return resp.json()
        except (httpx.HTTPStatusError, httpx.HTTPError) as exc:
            logger.warning(f"Reddit request failed ({url}): {exc}")
            return None
    return None


class RedditScraper:
    def __init__(self):
        self.headers = _HEADERS

    async def get_user_info(self, username: str) -> Optional[dict]:
        """Fetch Reddit user profile via the public about.json endpoint."""
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            json_data = await _reddit_get(client, f"{REDDIT_API_BASE}/user/{username}/about.json")
            if not json_data:
                return None

            data = json_data.get("data", {})
            if not data or data.get("is_suspended"):
                return None

            return {
                "username": username,
                "source": "reddit",
                "link_karma": data.get("link_karma", 0),
                "comment_karma": data.get("comment_karma", 0),
                "total_karma": data.get("total_karma", 0),
                "created_utc": data.get("created_utc"),
                "is_gold": data.get("is_gold", False),
                "is_mod": data.get("is_mod", False),
                "has_verified_email": data.get("has_verified_email", False),
                "icon_img": data.get("icon_img", "").split("?")[0] or None,
                "subreddit": data.get("subreddit", {}).get("display_name_prefixed"),
                "profile_url": f"https://reddit.com/u/{username}",
            }

    async def get_user_submissions(self, username: str, limit: int = 25) -> list:
        """Fetch a user's recent posts/submissions."""
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            json_data = await _reddit_get(
                client,
                f"{REDDIT_API_BASE}/user/{username}/submitted.json",
                params={"limit": min(limit, 100), "sort": "new"},
            )
            if not json_data:
                return []

            children = json_data.get("data", {}).get("children", [])
            posts = []
            for child in children[:limit]:
                d = child.get("data", {})
                posts.append({
                    "title": d.get("title", ""),
                    "url": d.get("url", ""),
                    "permalink": f"https://reddit.com{d.get('permalink', '')}",
                    "subreddit": d.get("subreddit_name_prefixed", ""),
                    "score": d.get("score", 0),
                    "upvote_ratio": d.get("upvote_ratio", 0),
                    "num_comments": d.get("num_comments", 0),
                    "created_utc": d.get("created_utc"),
                    "is_self": d.get("is_self", False),
                    "domain": d.get("domain", ""),
                    "source": "reddit",
                })
            return posts
