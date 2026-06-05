"""
Advanced Features Module for PRETO

Phase 3.3: Advanced Features (Export, Analytics, Recommendations)
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import csv
from io import StringIO

logger = logging.getLogger(__name__)


class AdvancedFeaturesManager:
    """Manages advanced features like export, analytics, and recommendations."""
    
    @staticmethod
    def export_search_results(
        repositories: List[Dict],
        format: str = "json"
    ) -> str:
        """
        Export search results in different formats.
        
        Args:
            repositories: List of repositories to export
            format: Export format (json, csv)
        
        Returns:
            Exported data as string
        """
        if format == "csv":
            return AdvancedFeaturesManager._export_csv(repositories)
        else:  # json
            return json.dumps(repositories, indent=2, default=str)
    
    @staticmethod
    def _export_csv(repositories: List[Dict]) -> str:
        """Export repositories as CSV."""
        if not repositories:
            return ""
        
        output = StringIO()
        fieldnames = ["name", "full_name", "language", "stargazers_count", "forks_count", "url"]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        for repo in repositories:
            writer.writerow({
                "name": repo.get("name", ""),
                "full_name": repo.get("full_name", ""),
                "language": repo.get("language", ""),
                "stargazers_count": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
                "url": repo.get("html_url", "")
            })
        
        return output.getvalue()
    
    @staticmethod
    def generate_analytics(
        repositories: List[Dict],
        period_days: int = 30
    ) -> Dict:
        """
        Generate analytics from repositories.
        
        Args:
            repositories: List of repositories
            period_days: Analysis period
        
        Returns:
            Analytics dictionary
        """
        if not repositories:
            return {
                "total_repos": 0,
                "total_stars": 0,
                "total_forks": 0,
                "analytics": {}
            }
        
        total_repos = len(repositories)
        total_stars = sum(r.get("stargazers_count", 0) for r in repositories)
        total_forks = sum(r.get("forks_count", 0) for r in repositories)
        total_watchers = sum(r.get("watchers_count", 0) for r in repositories)
        
        # Language distribution
        languages = {}
        for repo in repositories:
            lang = repo.get("language")
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        # Top repositories
        top_repos = sorted(
            repositories,
            key=lambda x: x.get("stargazers_count", 0),
            reverse=True
        )[:5]
        
        # Trending (recent updates)
        trending = sorted(
            repositories,
            key=lambda x: x.get("updated_at", ""),
            reverse=True
        )[:5]
        
        return {
            "total_repos": total_repos,
            "total_stars": total_stars,
            "total_forks": total_forks,
            "total_watchers": total_watchers,
            "average_stars_per_repo": total_stars // total_repos if total_repos > 0 else 0,
            "average_forks_per_repo": total_forks // total_repos if total_repos > 0 else 0,
            "languages": languages,
            "top_repos": [
                {
                    "name": r.get("name"),
                    "stars": r.get("stargazers_count", 0)
                }
                for r in top_repos
            ],
            "trending": [
                {
                    "name": r.get("name"),
                    "updated_at": r.get("updated_at")
                }
                for r in trending
            ]
        }
    
    @staticmethod
    def get_recommendations(
        search_history: List[Dict],
        repositories: List[Dict]
    ) -> List[Dict]:
        """
        Generate recommendations based on search history and data.
        
        Args:
            search_history: User's search history
            repositories: Available repositories
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if not repositories:
            return recommendations
        
        # Get most searched languages
        language_searches = {}
        for search in search_history[-10:]:  # Last 10 searches
            if "language" in search:
                lang = search["language"]
                language_searches[lang] = language_searches.get(lang, 0) + 1
        
        # Recommend similar to top searches
        if language_searches:
            top_language = max(language_searches, key=language_searches.get)
            
            # Find high-star repos in that language
            similar = [
                r for r in repositories
                if r.get("language") == top_language and r.get("stargazers_count", 0) > 1000
            ][:5]
            
            recommendations.extend([
                {
                    "type": "language_match",
                    "repository": r.get("name"),
                    "reason": f"You frequently search for {top_language} projects",
                    "stars": r.get("stargazers_count", 0)
                }
                for r in similar
            ])
        
        # Trending recommendations
        trending = sorted(
            repositories,
            key=lambda x: x.get("stargazers_count", 0),
            reverse=True
        )[:3]
        
        for repo in trending:
            recommendations.append({
                "type": "trending",
                "repository": repo.get("name"),
                "reason": "Currently trending on GitHub",
                "stars": repo.get("stargazers_count", 0)
            })
        
        return recommendations[:10]
    
    @staticmethod
    def generate_report(
        user_id: int,
        search_history: List[Dict],
        repositories: List[Dict],
        analytics: Dict
    ) -> Dict:
        """
        Generate comprehensive user report.
        
        Args:
            user_id: User ID
            search_history: User's search history
            repositories: User's repositories
            analytics: Analytics data
        
        Returns:
            Comprehensive report
        """
        recommendations = AdvancedFeaturesManager.get_recommendations(
            search_history,
            repositories
        )
        
        report = {
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_searches": len(search_history),
                "total_repositories_analyzed": analytics.get("total_repos", 0),
                "total_stars_analyzed": analytics.get("total_stars", 0)
            },
            "analytics": analytics,
            "recommendations": recommendations,
            "top_languages": list(analytics.get("languages", {}).keys())[:5],
            "report_sections": [
                "summary",
                "analytics",
                "recommendations",
                "trends"
            ]
        }
        
        return report
    
    @staticmethod
    def compare_repositories(
        repo_list_1: List[Dict],
        repo_list_2: List[Dict]
    ) -> Dict:
        """
        Compare two lists of repositories.
        
        Args:
            repo_list_1: First repository list
            repo_list_2: Second repository list
        
        Returns:
            Comparison metrics
        """
        stats_1 = AdvancedFeaturesManager.generate_analytics(repo_list_1)
        stats_2 = AdvancedFeaturesManager.generate_analytics(repo_list_2)
        
        return {
            "list_1": {
                "count": len(repo_list_1),
                "total_stars": stats_1["total_stars"],
                "avg_stars": stats_1["average_stars_per_repo"]
            },
            "list_2": {
                "count": len(repo_list_2),
                "total_stars": stats_2["total_stars"],
                "avg_stars": stats_2["average_stars_per_repo"]
            },
            "comparison": {
                "more_repos_in_list": "1" if len(repo_list_1) > len(repo_list_2) else "2",
                "higher_total_stars_in_list": "1" if stats_1["total_stars"] > stats_2["total_stars"] else "2",
                "higher_avg_quality_in_list": "1" if stats_1["average_stars_per_repo"] > stats_2["average_stars_per_repo"] else "2"
            }
        }


def get_advanced_features_manager() -> AdvancedFeaturesManager:
    """Get advanced features manager."""
    return AdvancedFeaturesManager()
