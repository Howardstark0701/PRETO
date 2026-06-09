import httpx
import asyncio
from typing import Optional

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"


class HackerNewsScraper:
    def __init__(self):
        self.base_url = HN_API_BASE

    async def get_user(self, username: str) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(f"{self.base_url}/user/{username}.json")
                resp.raise_for_status()
                data = resp.json()
                if not data:
                    return None
                return {
                    "username": username,
                    "source": "hackernews",
                    "karma": data.get("karma", 0),
                    "created_utc": data.get("created"),
                    "about": data.get("about", ""),
                    "submitted_count": len(data.get("submitted", [])),
                }
            except httpx.HTTPError:
                return None

    async def get_user_submissions(self, username: str, limit: int = 20) -> list:
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                user_resp = await client.get(f"{self.base_url}/user/{username}.json")
                user_resp.raise_for_status()
                user_data = user_resp.json()
                if not user_data:
                    return []

                # Fetch only the most recent IDs, then resolve concurrently
                item_ids = user_data.get("submitted", [])[:limit * 3]  # over-fetch since we filter to stories only

                async def fetch_item(item_id: int) -> Optional[dict]:
                    try:
                        r = await client.get(f"{self.base_url}/item/{item_id}.json", timeout=8.0)
                        r.raise_for_status()
                        item = r.json()
                        if item and item.get("type") == "story":
                            return {
                                "id": item.get("id"),
                                "title": item.get("title"),
                                "url": item.get("url") or f"https://news.ycombinator.com/item?id={item.get('id')}",
                                "score": item.get("score", 0),
                                "descendants": item.get("descendants", 0),
                                "time": item.get("time"),
                                "source": "hackernews",
                            }
                    except (httpx.HTTPError, Exception):
                        pass
                    return None

                # Run all item fetches concurrently (max 10 at a time to avoid hammering Firebase)
                sem = asyncio.Semaphore(10)

                async def fetch_with_sem(item_id):
                    async with sem:
                        return await fetch_item(item_id)

                results = await asyncio.gather(*[fetch_with_sem(i) for i in item_ids])
                items = [r for r in results if r is not None][:limit]
                return items

            except httpx.HTTPError:
                return []
