import httpx
from typing import Optional

DEVTO_API_BASE = "https://dev.to/api"


class DevToScraper:
    def __init__(self, api_key: Optional[str] = None):
        self.headers = {"api-key": api_key} if api_key else {}

    async def get_user(self, username: str) -> Optional[dict]:
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            try:
                resp = await client.get(f"{DEVTO_API_BASE}/users/by_username", params={"url": username})
                resp.raise_for_status()
                data = resp.json()
                return {
                    "username": username,
                    "source": "devto",
                    "name": data.get("name"),
                    "bio": data.get("summary"),
                    "github_username": data.get("github_username"),
                    "twitter_username": data.get("twitter_username"),
                    "website_url": data.get("website_url"),
                    "location": data.get("location"),
                    "joined_at": data.get("joined_at"),
                    "profile_image": data.get("profile_image_90"),
                }
            except httpx.HTTPError:
                return None

    async def get_articles(self, username: str, per_page: int = 20) -> list:
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            try:
                resp = await client.get(
                    f"{DEVTO_API_BASE}/articles",
                    params={"username": username, "per_page": per_page},
                )
                resp.raise_for_status()
                data = resp.json()
                return [
                    {
                        "title": a.get("title"),
                        "url": a.get("url"),
                        "description": a.get("description"),
                        "tags": a.get("tag_list", []),
                        "positive_reactions": a.get("positive_reactions_count", 0),
                        "comments_count": a.get("comments_count", 0),
                        "published_at": a.get("published_at"),
                        "reading_time_minutes": a.get("reading_time_minutes", 0),
                        "source": "devto",
                    }
                    for a in data
                ]
            except httpx.HTTPError:
                return []
