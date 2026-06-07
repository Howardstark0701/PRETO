import httpx
from typing import Optional

GITLAB_API_BASE = "https://gitlab.com/api/v4"


class GitLabScraper:
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        self.base_url = GITLAB_API_BASE

    async def get_user_projects(self, username: str, per_page: int = 30) -> list:
        projects = []
        page = 1

        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            while True:
                url = f"{self.base_url}/users/{username}/projects"
                params = {"per_page": per_page, "page": page, "sort": "updated"}
                try:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    if not data:
                        break
                    projects.extend(data)
                    page += 1
                except httpx.HTTPError:
                    break

        return [
            {
                "name": p.get("name"),
                "full_name": p.get("path_with_namespace"),
                "url": p.get("web_url"),
                "description": p.get("description"),
                "language": p.get("language"),
                "stargazers_count": p.get("star_count", 0),
                "forks_count": p.get("forks_count", 0),
                "watchers_count": 0,
                "updated_at": p.get("last_activity_at"),
                "topics": p.get("topics", []),
                "source": "gitlab",
            }
            for p in projects
        ]

    async def search_projects(self, query: str, per_page: int = 30) -> list:
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            url = f"{self.base_url}/search"
            params = {"scope": "projects", "search": query, "per_page": per_page}
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                return [
                    {
                        "name": p.get("name"),
                        "full_name": p.get("path_with_namespace"),
                        "url": p.get("web_url"),
                        "description": p.get("description"),
                        "language": p.get("language"),
                        "stargazers_count": p.get("star_count", 0),
                        "forks_count": p.get("forks_count", 0),
                        "watchers_count": 0,
                        "updated_at": p.get("last_activity_at"),
                        "topics": p.get("topics", []),
                        "source": "gitlab",
                    }
                    for p in data
                ]
            except httpx.HTTPError:
                return []
