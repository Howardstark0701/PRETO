"""
Reddit scraper using PullPush API (primary) with public JSON fallback.

PullPush: https://api.pullpush.io/reddit/search/submission
  - Free, no auth, generous rate limits
  - Data is archived (minutes to hours delay)
  - Timeout: 8s, 1 retry (2 attempts total)

Fallback: reddit.com public JSON
  - Used when PullPush fails
  - Unreliable (frequent 403/429)
  - Silent — users never know which source served the data
"""

import httpx
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

REDDIT_API_BASE = "https://www.reddit.com"
PULLPUSH_BASE = "https://api.pullpush.io/reddit/search/submission"

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


class RedditScraper:
    def __init__(self):
        self.headers = _HEADERS

    async def get_user_info(self, username: str) -> Optional[dict]:
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            try:
                resp = await client.get(
                    f"{REDDIT_API_BASE}/user/{username}/about.json",
                    follow_redirects=True
                )
                if resp.status_code == 403:
                    logger.warning(f"Reddit 403 for user {username} — blocked")
                    return None
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()

                json_data = resp.json()
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
            except httpx.HTTPError as e:
                logger.warning(f"Reddit API error for {username}: {e}")
                return None

    async def get_user_submissions(self, username: str, limit: int = 25) -> list:
        posts = await self._try_pullpush(username, limit)
        if posts:
            return posts
        posts = await self._try_public_json(username, limit)
        if posts:
            return posts
        return []

    async def _try_pullpush(self, username: str, limit: int) -> list:
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    params = {
                        "author": username,
                        "size": min(limit, 100),
                        "sort": "desc",
                        "sort_type": "created_utc",
                    }
                    resp = await client.get(PULLPUSH_BASE, params=params)
                    if resp.status_code != 200:
                        logger.warning(f"PullPush HTTP {resp.status_code} for {username} (attempt {attempt+1})")
                        continue
                    data = resp.json()
                    raw = data.get("data", [])
                    if not raw:
                        return []
                    return [
                        {
                            "title": p.get("title", ""),
                            "url": p.get("url", f"https://reddit.com{p.get('permalink', '')}"),
                            "permalink": f"https://reddit.com{p.get('permalink', '')}",
                            "subreddit": f"r/{p.get('subreddit', '')}",
                            "score": p.get("score", 0),
                            "ups": p.get("score", 0),
                            "upvote_ratio": p.get("upvote_ratio", 0),
                            "num_comments": p.get("num_comments", 0),
                            "created_utc": p.get("created_utc"),
                            "created": p.get("created_utc"),
                            "is_self": p.get("is_self", False),
                            "domain": p.get("domain", ""),
                            "source": "reddit",
                        }
                        for p in raw
                    ]
            except httpx.TimeoutException:
                logger.warning(f"PullPush timeout for {username} (attempt {attempt+1})")
            except httpx.HTTPError as e:
                logger.warning(f"PullPush HTTP error for {username} (attempt {attempt+1}): {e}")
            except Exception as e:
                logger.error(f"PullPush unexpected error for {username} (attempt {attempt+1}): {e}")
        return []

    async def _try_public_json(self, username: str, limit: int) -> list:
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
                resp = await client.get(
                    f"{REDDIT_API_BASE}/user/{username}/submitted.json",
                    params={"limit": min(limit, 100), "sort": "new"},
                    follow_redirects=True
                )
                if resp.status_code in (403, 404):
                    return []
                resp.raise_for_status()
                json_data = resp.json()
                children = json_data.get("data", {}).get("children", [])
                return [
                    {
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
                    }
                    for child in children[:limit]
                    if (d := child.get("data", {}))
                ]
        except httpx.HTTPError as e:
            logger.warning(f"Reddit public JSON error for {username}: {e}")
            return []
