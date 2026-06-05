"""
AI Insights Module for PRETO - NVIDIA NIM Integration

Phase 3.2: NVIDIA NIM AI Integration (Replaces Claude)
"""

import logging
import os
import json
import asyncio
import time
from typing import Optional, Dict, List
import httpx
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)

# NVIDIA NIM Configuration
NIM_API_KEY = os.getenv("NIM_API_KEY", "")
NIM_API_URL = os.getenv("NIM_API_URL", "https://integrate.api.nvidia.com/v1")
NIM_MODEL = os.getenv("NIM_MODEL", "meta/llama-3.1-70b-instruct")

# Rate Limiting: 40 requests per minute
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "40"))
REQUEST_WINDOW_SECONDS = 60


class RateLimiter:
    """Rate limiter for NIM API (40 requests per minute)."""
    
    def __init__(self, max_requests: int = MAX_REQUESTS_PER_MINUTE, window_seconds: int = REQUEST_WINDOW_SECONDS):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
    
    async def wait_if_needed(self):
        """Wait if rate limit reached."""
        now = time.time()
        
        # Remove old requests outside window
        while self.requests and self.requests[0] < now - self.window_seconds:
            self.requests.popleft()
        
        # Check if limit reached
        if len(self.requests) >= self.max_requests:
            sleep_time = self.window_seconds - (now - self.requests[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached. Waiting {sleep_time:.2f} seconds...")
                await asyncio.sleep(sleep_time)
                # Recursively check again after sleep
                await self.wait_if_needed()
        
        # Add current request
        self.requests.append(now)
    
    def get_stats(self) -> Dict:
        """Get rate limiter statistics."""
        now = time.time()
        # Remove old requests
        while self.requests and self.requests[0] < now - self.window_seconds:
            self.requests.popleft()
        
        return {
            "requests_in_window": len(self.requests),
            "max_requests": self.max_requests,
            "available_slots": self.max_requests - len(self.requests),
            "window_seconds": self.window_seconds
        }


class NIMInsights:
    """NVIDIA NIM AI insights generator for OSINT analysis."""
    
    def __init__(self, api_key: str = NIM_API_KEY):
        self.api_key = api_key
        self.client = None
        self.rate_limiter = RateLimiter(MAX_REQUESTS_PER_MINUTE)
        
        if self.api_key and self.api_key != "sk-ant-your-api-key-here":
            self.client = httpx.Client(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "content-type": "application/json"
                },
                timeout=30.0
            )
            logger.info(f"NVIDIA NIM initialized. Rate limit: {MAX_REQUESTS_PER_MINUTE} req/min")
    
    async def analyze_repositories(self, repositories: List[Dict], analysis_type: str = "general") -> str:
        """
        Analyze a list of repositories using NVIDIA NIM.
        
        Args:
            repositories: List of repository data
            analysis_type: Type of analysis (general, security, trending, quality)
        
        Returns:
            Analysis text from NIM
        """
        if not self.client:
            return self._get_fallback_analysis(repositories, analysis_type)
        
        try:
            # Wait for rate limit
            await self.rate_limiter.wait_if_needed()
            
            # Prepare repository summary
            repo_summary = self._prepare_repo_summary(repositories)
            
            # Create analysis prompt based on type
            prompt = self._create_analysis_prompt(repo_summary, analysis_type)
            
            # Call NIM API
            response = await self._call_nim(prompt)
            
            logger.info(f"Repository analysis completed: {analysis_type} | Rate limit: {self.rate_limiter.get_stats()}")
            return response
        
        except Exception as e:
            logger.error(f"Error analyzing repositories: {str(e)}")
            return self._get_fallback_analysis(repositories, analysis_type)
    
    async def query_natural_language(self, query: str, context_data: Dict) -> str:
        """
        Process natural language query about OSINT data.
        
        Args:
            query: Natural language question
            context_data: Relevant context (repositories, users, stats)
        
        Returns:
            Answer from NIM
        """
        if not self.client:
            return f"Fallback response to: {query}"
        
        try:
            # Wait for rate limit
            await self.rate_limiter.wait_if_needed()
            
            prompt = self._create_query_prompt(query, context_data)
            response = await self._call_nim(prompt)
            
            logger.info(f"Natural language query processed | Rate limit: {self.rate_limiter.get_stats()}")
            return response
        
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"Unable to process query: {str(e)}"
    
    def _prepare_repo_summary(self, repositories: List[Dict]) -> str:
        """Prepare repository summary for analysis."""
        if not repositories:
            return "No repositories provided"
        
        summary_lines = [f"Total repositories: {len(repositories)}\n"]
        
        for i, repo in enumerate(repositories[:10], 1):  # Limit to first 10 for token efficiency
            summary_lines.append(
                f"{i}. {repo.get('name', 'Unknown')}\n"
                f"   Language: {repo.get('language', 'Unknown')}\n"
                f"   Stars: {repo.get('stargazers_count', 0)}\n"
                f"   Forks: {repo.get('forks_count', 0)}\n"
                f"   Description: {repo.get('description', 'N/A')[:100]}"
            )
        
        if len(repositories) > 10:
            summary_lines.append(f"\n... and {len(repositories) - 10} more repositories")
        
        return "\n".join(summary_lines)
    
    def _create_analysis_prompt(self, repo_summary: str, analysis_type: str) -> str:
        """Create analysis prompt based on type."""
        base_prompt = f"Analyze the following GitHub repositories:\n\n{repo_summary}\n\n"
        
        if analysis_type == "security":
            return base_prompt + (
                "Focus on security implications and best practices. "
                "Identify potential security risks, recommended security measures, "
                "and highlight repositories with good security practices."
            )
        elif analysis_type == "trending":
            return base_prompt + (
                "Identify trending technologies and patterns. "
                "Which technologies are most popular? What are the emerging trends? "
                "Which repositories are most promising for future growth?"
            )
        elif analysis_type == "quality":
            return base_prompt + (
                "Assess code quality indicators. "
                "Based on activity, stars, and other metrics, which repositories show signs of good maintenance? "
                "Which ones might have quality concerns?"
            )
        else:  # general
            return base_prompt + (
                "Provide a comprehensive analysis including: "
                "1. Key technologies and languages used\n"
                "2. Most popular and promising repositories\n"
                "3. Notable trends or patterns\n"
                "4. Recommendations for further exploration"
            )
    
    def _create_query_prompt(self, query: str, context_data: Dict) -> str:
        """Create prompt for natural language queries."""
        context_str = json.dumps(context_data, indent=2, default=str)[:1000]  # Limit context
        
        return (
            f"Based on the following OSINT/GitHub data:\n\n"
            f"{context_str}\n\n"
            f"Answer this question: {query}\n\n"
            f"Provide a clear, concise answer based on the provided data."
        )
    
    async def _call_nim(self, prompt: str) -> str:
        """Call NVIDIA NIM API."""
        if not self.client:
            raise ValueError("NIM client not initialized")
        
        try:
            response = self.client.post(
                f"{NIM_API_URL}/chat/completions",
                json={
                    "model": NIM_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1024
                }
            )
            
            if response.status_code != 200:
                logger.error(f"NIM API error: {response.status_code} - {response.text}")
                raise Exception(f"NIM API error: {response.status_code}")
            
            data = response.json()
            # NIM returns in OpenAI format
            return data.get("choices", [{}])[0].get("message", {}).get("content", "No response from NIM")
        
        except Exception as e:
            logger.error(f"NIM API call failed: {str(e)}")
            raise
    
    def _get_fallback_analysis(self, repositories: List[Dict], analysis_type: str) -> str:
        """Provide fallback analysis when NIM is not available."""
        if not repositories:
            return "No repositories to analyze."
        
        # Basic statistics
        total_stars = sum(r.get('stargazers_count', 0) for r in repositories)
        total_forks = sum(r.get('forks_count', 0) for r in repositories)
        languages = {}
        
        for repo in repositories:
            lang = repo.get('language', 'Unknown')
            languages[lang] = languages.get(lang, 0) + 1
        
        top_language = max(languages, key=languages.get) if languages else "Unknown"
        
        if analysis_type == "security":
            return (
                f"Based on {len(repositories)} repositories:\n"
                f"- Total stars: {total_stars} (indicates community trust)\n"
                f"- Total forks: {total_forks} (indicates ongoing development)\n"
                f"- Primary language: {top_language}\n"
                f"\nRecommendation: Review repositories with high star counts for security audits."
            )
        elif analysis_type == "trending":
            return (
                f"Trending observations:\n"
                f"- Most common language: {top_language} ({languages.get(top_language, 0)} repos)\n"
                f"- Average stars per repo: {total_stars // len(repositories)}\n"
                f"- Repository count: {len(repositories)}\n"
                f"\nTop repositories:\n"
            ) + "\n".join(
                f"- {r.get('name')}: {r.get('stargazers_count')} stars"
                for r in sorted(repositories, key=lambda x: x.get('stargazers_count', 0), reverse=True)[:5]
            )
        elif analysis_type == "quality":
            avg_stars = total_stars // len(repositories) if repositories else 0
            high_quality = [r for r in repositories if r.get('stargazers_count', 0) > avg_stars]
            return (
                f"Code quality indicators:\n"
                f"- Analyzed {len(repositories)} repositories\n"
                f"- High-quality repos (above average stars): {len(high_quality)}\n"
                f"- Average stars: {avg_stars}\n"
                f"- Primary language: {top_language}\n"
                f"\nHigh-quality candidates: {len(high_quality)} repositories with above-average engagement"
            )
        else:  # general
            return (
                f"Repository Analysis Summary\n"
                f"=============================\n"
                f"Total repositories: {len(repositories)}\n"
                f"Total stars: {total_stars}\n"
                f"Total forks: {total_forks}\n"
                f"Primary language: {top_language}\n"
                f"Languages used: {', '.join(languages.keys())}\n"
                f"\nTop 3 repositories by stars:\n"
            ) + "\n".join(
                f"{i+1}. {r.get('name', 'Unknown')} - {r.get('stargazers_count', 0)} stars"
                for i, r in enumerate(sorted(repositories, key=lambda x: x.get('stargazers_count', 0), reverse=True)[:3])
            )


# Global instance
_insights = None


def get_insights_manager() -> NIMInsights:
    """Get or create insights manager."""
    global _insights
    if _insights is None:
        _insights = NIMInsights()
    return _insights
