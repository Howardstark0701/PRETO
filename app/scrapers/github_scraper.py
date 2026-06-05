import asyncio
import httpx
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_BASE = "https://api.github.com"

class GitHubScraper:
    def __init__(self, token: Optional[str] = None):
        self.token = token or GITHUB_TOKEN
        self.headers = {
            "Authorization": f"token {self.token}" if self.token else "",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = GITHUB_API_BASE
    
    async def get_user_repos(self, username: str, per_page: int = 30) -> list:
        """Fetch all repos for a user with pagination"""
        repos = []
        page = 1
        
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            while True:
                url = f"{self.base_url}/users/{username}/repos"
                params = {"per_page": per_page, "page": page, "sort": "updated"}
                
                try:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    
                    data = response.json()
                    if not data:
                        break
                    
                    repos.extend(data)
                    page += 1
                    
                except httpx.HTTPError as e:
                    print(f"Error fetching repos: {e}")
                    break
        
        # Transform to match RepositoryResponse schema
        transformed_repos = []
        for repo in repos:
            transformed_repos.append({
                "name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "url": repo.get("html_url"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stargazers_count": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
                "watchers_count": repo.get("watchers_count", 0),
                "updated_at": repo.get("updated_at"),
                "topics": repo.get("topics", [])
            })
        
        return transformed_repos
    
    async def search_repos(self, query: str, language: Optional[str] = None, per_page: int = 30) -> list:
        """Search repositories by query"""
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            url = f"{self.base_url}/search/repositories"
            params = {"q": search_query, "per_page": per_page, "sort": "stars"}
            
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Transform to match RepositoryResponse schema
                items = data.get("items", [])
                transformed_items = []
                for repo in items:
                    transformed_items.append({
                        "name": repo.get("name"),
                        "full_name": repo.get("full_name"),
                        "url": repo.get("html_url"),
                        "description": repo.get("description"),
                        "language": repo.get("language"),
                        "stargazers_count": repo.get("stargazers_count", 0),
                        "forks_count": repo.get("forks_count", 0),
                        "watchers_count": repo.get("watchers_count", 0),
                        "updated_at": repo.get("updated_at"),
                        "topics": repo.get("topics", [])
                    })
                return transformed_items
            except httpx.HTTPError as e:
                print(f"Error searching repos: {e}")
                return []


async def main():
    print("Script started...")
    scraper = GitHubScraper()
    print("Scraper initialized")
    
    try:
        print("Fetching repos from torvalds (with timeout)...")
        repos = await asyncio.wait_for(scraper.get_user_repos("torvalds"), timeout=5.0)
        print(f"Found {len(repos)} repos from torvalds")
        
        print("Searching for ML repos (with timeout)...")
        results = await asyncio.wait_for(scraper.search_repos("machine-learning", language="python"), timeout=5.0)
        print(f"Found {len(results)} ML repos in Python")
    except asyncio.TimeoutError:
        print("Request timed out - GitHub API might be slow or blocked")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()




# -------------T  E  S  T  ------------------------------

#     print("Test: Script started")
#     scraper = GitHubScraper()
#     print("Test: Scraper initialized")
#     print("Test: Done")


# if __name__ == "__main__":
#     asyncio.run(main())






    # print("Script started...")
    # scraper = GitHubScraper()
    # print("Scraper initialized")
    
    # try:
    #     print("Fetching repos from torvalds...")
    #     repos = await scraper.get_user_repos("torvalds")
    #     print(f"Found {len(repos)} repos from torvalds")
        
    #     print("Searching for ML repos...")
    #     results = await scraper.search_repos("machine-learning", language="python")
    #     print(f"Found {len(results)} ML repos in Python")
    # except Exception as e:
    #     print(f"Error: {e}")
    #     import traceback
    #     traceback.print_exc()


    # scraper = GitHubScraper()
    
    # # Test: fetch repos from a user
    # repos = await scraper.get_user_repos("torvalds")
    # print(f"Found {len(repos)} repos from torvalds")
    
    # # Test: search for Python ML projects
    # results = await scraper.search_repos("machine-learning", language="python")
    # print(f"Found {len(results)} ML repos in Python")


if __name__ == "__main__":
    asyncio.run(main())