"""
Background sync manager for data persistence and cache management

Phase 2.3: Background Tasks & Sync Manager

Author: TANGO
Last Updated: June 5, 2026
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models import get_db, SessionLocal
from app.scrapers.github_scraper import GitHubScraper
from app.api.crud import (
    create_repositories_batch,
    update_user_statistics,
    create_search,
    clear_expired_cache as crud_clear_expired_cache,
    get_stats_summary
)
from app.api.cache import CacheManager

logger = logging.getLogger(__name__)


class SyncManager:
    """Manages background synchronization tasks."""
    
    def __init__(self):
        self.scraper = GitHubScraper()
        self.is_running = False
        self.last_sync = None
        self.sync_stats = {
            'total_syncs': 0,
            'total_repos_synced': 0,
            'total_users_synced': 0,
            'last_sync_time': None,
            'last_sync_duration': None,
            'errors': []
        }
    
    async def sync_user_repositories(self, username: str, db: Session) -> Dict:
        """Sync repositories for a user to database."""
        sync_start = datetime.utcnow()
        
        try:
            logger.info(f"Starting sync for user: {username}")
            
            # Fetch from GitHub
            repos = await self.scraper.get_user_repos(username, per_page=100)
            
            if not repos:
                logger.warning(f"No repositories found for user: {username}")
                return {"status": "error", "message": f"No repos found for {username}"}
            
            # Transform and save to database
            count = create_repositories_batch(db, repos)
            
            # Calculate user statistics
            total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
            total_forks = sum(repo.get('forks_count', 0) for repo in repos)
            total_watchers = sum(repo.get('watchers_count', 0) for repo in repos)
            
            # Get languages
            languages = {}
            for repo in repos:
                lang = repo.get('language')
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
            
            most_used = max(languages, key=languages.get) if languages else None
            
            # Update statistics
            stats_data = {
                'total_repositories': len(repos),
                'total_stars': total_stars,
                'total_forks': total_forks,
                'total_watchers': total_watchers,
                'languages': languages,
                'average_stars_per_repo': total_stars // len(repos) if repos else 0,
                'average_forks_per_repo': total_forks // len(repos) if repos else 0,
                'most_used_language': most_used
            }
            
            update_user_statistics(db, username, stats_data)
            
            sync_duration = (datetime.utcnow() - sync_start).total_seconds()
            
            logger.info(f"Sync completed for {username}: {count} repos in {sync_duration}s")
            
            self.sync_stats['total_syncs'] += 1
            self.sync_stats['total_repos_synced'] += count
            self.sync_stats['total_users_synced'] += 1
            self.sync_stats['last_sync_time'] = datetime.utcnow()
            self.sync_stats['last_sync_duration'] = sync_duration
            
            return {
                "status": "success",
                "username": username,
                "repos_synced": count,
                "duration_seconds": sync_duration,
                "timestamp": sync_start
            }
        
        except Exception as e:
            error_msg = f"Sync failed for {username}: {str(e)}"
            logger.error(error_msg)
            self.sync_stats['errors'].append(error_msg)
            
            return {
                "status": "error",
                "username": username,
                "error": str(e)
            }
    
    async def sync_multiple_users(self, usernames: List[str], db: Session) -> Dict:
        """Sync multiple users in parallel."""
        try:
            logger.info(f"Starting batch sync for {len(usernames)} users")
            
            # Run syncs concurrently
            tasks = [self.sync_user_repositories(username, db) for username in usernames]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'success')
            failed = len(results) - successful
            
            logger.info(f"Batch sync complete: {successful} successful, {failed} failed")
            
            return {
                "status": "complete",
                "total": len(usernames),
                "successful": successful,
                "failed": failed,
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Batch sync error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def maintain_cache(self) -> Dict:
        """Clean up expired cache entries."""
        try:
            logger.info("Running cache maintenance...")
            
            # Clear expired entries from memory cache
            expired_count = CacheManager.clear_expired()
            
            # Get cache stats
            stats = CacheManager.get_stats()
            
            logger.info(f"Cache maintenance complete: Cleared {expired_count} expired entries")
            
            return {
                "status": "success",
                "expired_entries_cleared": expired_count,
                "cache_stats": stats,
                "timestamp": datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Cache maintenance error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_database_stats(self, db: Session) -> Dict:
        """Get database statistics."""
        try:
            stats = get_stats_summary(db)
            logger.info(f"Database stats retrieved: {stats}")
            return stats
        
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def get_sync_stats(self) -> Dict:
        """Get sync statistics."""
        return {
            **self.sync_stats,
            "timestamp": datetime.utcnow()
        }


# Global sync manager instance
_sync_manager: Optional[SyncManager] = None


def get_sync_manager() -> SyncManager:
    """Get or create sync manager."""
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = SyncManager()
        logger.info("Sync manager initialized")
    return _sync_manager


# Convenience functions for background tasks
async def background_sync_user(username: str) -> Dict:
    """Background task to sync user."""
    db = SessionLocal()
    try:
        manager = get_sync_manager()
        result = await manager.sync_user_repositories(username, db)
        
        # Invalidate cache for this user
        from app.api.cache import cache_invalidate
        cache_invalidate('user_repos', username=username)
        cache_invalidate('stats', username=username)
        
        return result
    finally:
        db.close()


async def background_batch_sync(usernames: List[str]) -> Dict:
    """Background task to sync multiple users."""
    db = SessionLocal()
    try:
        manager = get_sync_manager()
        result = await manager.sync_multiple_users(usernames, db)
        
        # Clear all user cache
        from app.api.cache import cache_clear
        cache_clear('user_repos')
        cache_clear('stats')
        
        return result
    finally:
        db.close()


def background_cache_maintenance() -> Dict:
    """Background task for cache maintenance."""
    manager = get_sync_manager()
    return manager.maintain_cache()


def background_get_stats() -> Dict:
    """Background task to get stats."""
    db = SessionLocal()
    try:
        manager = get_sync_manager()
        return manager.get_database_stats(db)
    finally:
        db.close()
