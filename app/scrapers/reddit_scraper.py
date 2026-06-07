import httpx
from typing import Optional

REDDIT_API_BASE = "https://www.reddit.com"


class RedditScraper:
    def __init__(self):
        self.headers = {"User-Agent": "PRETO/1.0 (OSINT Intelligence Platform)"}

    async def get_user_info(self, username: str) -> Optional[dict]:
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            try:
                resp = await client.get(f"{REDDIT_API_BASE}/user/{username}/about.json")
                resp.raise_for_status()
                data = resp.json().get("data", {})
                return {
                    "username": username,
                    "source": "reddit",
                    "link_karma": data.get("link_karma", 0),
                    "comment_karma": data.get("comment_karma", 0),
                    "created_utc": data.get("created_utc"),
                    "is_gold": data.get("is_gold", False),
                    "is_mod": data.get("is_mod", False),
                    "subreddit": data.get("subreddit", {}).get("display_name_prefixed"),
                }
            except httpx.HTTPError:
                return None

    async def get_user_submissions(self, username: str, limit: int = 25) -> list:
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            try:
                resp = await client.get(
                    f"{REDDIT_API_BASE}/user/{username}/submitted.json",
                    params={"limit": limit, "sort": "new"},
                )
                resp.raise_for_status()
                children = resp.json().get("data", {}).get("children", [])
                posts = []
                for child in children[:limit]:
                    d = child.get("data", {})
                    posts.append({
                        "title": d.get("title"),
                        "url": d.get("url"),
                        "permalink": f"https://reddit.com{d.get('permalink')}",
                        "subreddit": d.get("subreddit_name_prefixed"),
                        "score": d.get("score", 0),
                        "num_comments": d.get("num_comments", 0),
                        "created_utc": d.get("created_utc"),
                        "source": "reddit",
                    })
                return posts
            except httpx.HTTPError:
                return []
