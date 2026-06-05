"""
Caching layer for API responses

Phase 2.2: Caching

Author: TANGO
Last Updated: June 5, 2026
"""

import json
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages API response caching."""
    
    # In-memory cache for fast access
    _memory_cache: Dict[str, Dict[str, Any]] = {}
    
    # Default TTL values (minutes)
    CACHE_TTL = {
        'user_repos': 60,           # Cache user repos for 1 hour
        'search': 30,               # Cache searches for 30 minutes
        'stats': 120,               # Cache stats for 2 hours
        'repo_details': 180,        # Cache repo details for 3 hours
    }
    
    @staticmethod
    def generate_cache_key(cache_type: str, **params) -> str:
        """Generate unique cache key from parameters."""
        # Create a sorted string of parameters
        params_str = json.dumps(params, sort_keys=True, default=str)
        
        # Hash it for shorter key
        hash_obj = hashlib.sha256(params_str.encode())
        cache_key = f"{cache_type}:{hash_obj.hexdigest()[:16]}"
        
        logger.debug(f"Generated cache key: {cache_key}")
        return cache_key
    
    @staticmethod
    def get(cache_type: str, **params) -> Optional[Any]:
        """Get value from cache."""
        cache_key = CacheManager.generate_cache_key(cache_type, **params)
        
        # Check memory cache first
        if cache_key in CacheManager._memory_cache:
            cache_entry = CacheManager._memory_cache[cache_key]
            
            # Check if expired
            if datetime.utcnow() < cache_entry['expires_at']:
                logger.info(f"Cache HIT: {cache_key}")
                cache_entry['hits'] += 1
                return cache_entry['data']
            else:
                # Expired, remove from cache
                logger.info(f"Cache EXPIRED: {cache_key}")
                del CacheManager._memory_cache[cache_key]
        
        logger.info(f"Cache MISS: {cache_key}")
        return None
    
    @staticmethod
    def set(cache_type: str, data: Any, **params) -> None:
        """Set value in cache."""
        cache_key = CacheManager.generate_cache_key(cache_type, **params)
        ttl = CacheManager.CACHE_TTL.get(cache_type, 60)
        
        expires_at = datetime.utcnow() + timedelta(minutes=ttl)
        
        CacheManager._memory_cache[cache_key] = {
            'data': data,
            'expires_at': expires_at,
            'created_at': datetime.utcnow(),
            'hits': 0,
            'ttl_minutes': ttl
        }
        
        logger.info(f"Cache SET: {cache_key} (TTL: {ttl}m)")
    
    @staticmethod
    def invalidate(cache_type: str, **params) -> bool:
        """Invalidate specific cache entry."""
        cache_key = CacheManager.generate_cache_key(cache_type, **params)
        
        if cache_key in CacheManager._memory_cache:
            del CacheManager._memory_cache[cache_key]
            logger.info(f"Cache INVALIDATED: {cache_key}")
            return True
        
        return False
    
    @staticmethod
    def invalidate_pattern(cache_type: str) -> int:
        """Invalidate all cache entries of a type."""
        prefix = f"{cache_type}:"
        keys_to_remove = [k for k in CacheManager._memory_cache.keys() if k.startswith(prefix)]
        
        for key in keys_to_remove:
            del CacheManager._memory_cache[key]
        
        logger.info(f"Cache INVALIDATED {len(keys_to_remove)} entries of type: {cache_type}")
        return len(keys_to_remove)
    
    @staticmethod
    def clear_expired() -> int:
        """Clear all expired cache entries."""
        now = datetime.utcnow()
        expired_keys = [
            k for k, v in CacheManager._memory_cache.items()
            if now >= v['expires_at']
        ]
        
        for key in expired_keys:
            del CacheManager._memory_cache[key]
        
        if expired_keys:
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    @staticmethod
    def get_stats() -> Dict:
        """Get cache statistics."""
        now = datetime.utcnow()
        active_entries = {
            k: v for k, v in CacheManager._memory_cache.items()
            if now < v['expires_at']
        }
        
        expired_entries = {
            k: v for k, v in CacheManager._memory_cache.items()
            if now >= v['expires_at']
        }
        
        total_hits = sum(v.get('hits', 0) for v in active_entries.values())
        
        return {
            'active_entries': len(active_entries),
            'expired_entries': len(expired_entries),
            'total_entries': len(CacheManager._memory_cache),
            'total_hits': total_hits,
            'memory_usage': f"{len(str(CacheManager._memory_cache)) / 1024:.2f} KB"
        }
    
    @staticmethod
    def clear_all() -> int:
        """Clear all cache entries."""
        count = len(CacheManager._memory_cache)
        CacheManager._memory_cache.clear()
        logger.info(f"Cache CLEARED - Removed {count} entries")
        return count


# Convenience functions
def cache_get(cache_type: str, **params) -> Optional[Any]:
    """Get from cache."""
    return CacheManager.get(cache_type, **params)


def cache_set(cache_type: str, data: Any, **params) -> None:
    """Set cache."""
    CacheManager.set(cache_type, data, **params)


def cache_invalidate(cache_type: str, **params) -> bool:
    """Invalidate cache."""
    return CacheManager.invalidate(cache_type, **params)


def cache_clear(cache_type: str) -> int:
    """Clear cache type."""
    return CacheManager.invalidate_pattern(cache_type)


def cache_stats() -> Dict:
    """Get cache stats."""
    return CacheManager.get_stats()
