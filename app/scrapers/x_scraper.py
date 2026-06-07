import httpx
import os
from typing import Optional

X_API_BASE = "https://api.twitter.com/2"


class XScraper:
    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token or os.getenv("X_BEARER_TOKEN", "")
        self.headers = {"Authorization": f"Bearer {self.bearer_token}"} if self.bearer_token else {}

    async def get_user(self, username: str) -> Optional[dict]:
        if not self.bearer_token:
            return {"username": username, "source": "x", "error": "X API token not configured"}
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            try:
                resp = await client.get(
                    f"{X_API_BASE}/users/by/username/{username}",
                    params={"user.fields": "public_metrics,description,created_at,profile_image_url"},
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                metrics = data.get("public_metrics", {})
                return {
                    "username": username,
                    "source": "x",
                    "display_name": data.get("name"),
                    "description": data.get("description"),
                    "followers_count": metrics.get("followers_count", 0),
                    "following_count": metrics.get("following_count", 0),
                    "tweet_count": metrics.get("tweet_count", 0),
                    "created_at": data.get("created_at"),
                    "avatar_url": data.get("profile_image_url"),
                }
            except httpx.HTTPError:
                return None

    async def get_tweets(self, username: str, max_results: int = 10) -> list:
        if not self.bearer_token:
            return []
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            try:
                user_resp = await client.get(
                    f"{X_API_BASE}/users/by/username/{username}",
                )
                user_resp.raise_for_status()
                user_id = user_resp.json().get("data", {}).get("id")
                if not user_id:
                    return []
                tweets_resp = await client.get(
                    f"{X_API_BASE}/users/{user_id}/tweets",
                    params={"max_results": max_results, "tweet.fields": "public_metrics,created_at"},
                )
                tweets_resp.raise_for_status()
                data = tweets_resp.json().get("data", [])
                return [
                    {
                        "id": t.get("id"),
                        "text": t.get("text", "")[:200],
                        "created_at": t.get("created_at"),
                        "likes": t.get("public_metrics", {}).get("like_count", 0),
                        "retweets": t.get("public_metrics", {}).get("retweet_count", 0),
                        "replies": t.get("public_metrics", {}).get("reply_count", 0),
                        "source": "x",
                    }
                    for t in data
                ]
            except httpx.HTTPError:
                return []
