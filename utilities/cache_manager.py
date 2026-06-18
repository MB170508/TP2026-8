"""Caching system for API responses with TTL and offline support.

Stores cached data locally to avoid repeated API calls and provide
fallback data while loading.
"""

import json
import time
from pathlib import Path
from typing import Any, Optional

from utilities.logger import get_logger

logger = get_logger(__name__)

CACHE_DIR = Path.home() / ".ittoolbox" / "cache"


class CacheManager:
    """Simple file-based cache with TTL support."""

    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key."""
        # Sanitize key for filename
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        return self.cache_dir / f"{safe_key}.json"

    def set(self, key: str, data: Any, ttl_seconds: int = 3600) -> bool:
        """Cache data with TTL.

        Args:
            key: Cache key
            data: Data to cache (must be JSON-serializable)
            ttl_seconds: Time to live in seconds (default 1 hour)

        Returns:
            True if cached successfully
        """
        try:
            cache_path = self._get_cache_path(key)
            cache_entry = {
                "timestamp": time.time(),
                "ttl": ttl_seconds,
                "data": data,
            }
            with open(cache_path, "w") as f:
                json.dump(cache_entry, f)
            logger.debug(f"Cached {key} (TTL: {ttl_seconds}s)")
            return True
        except Exception as e:
            logger.error(f"Failed to cache {key}: {e}")
            return False

    def get(self, key: str, check_ttl: bool = True) -> Optional[Any]:
        """Retrieve cached data if valid.

        Args:
            key: Cache key
            check_ttl: If True, check if data has expired

        Returns:
            Cached data or None if not found/expired
        """
        try:
            cache_path = self._get_cache_path(key)
            if not cache_path.exists():
                return None

            with open(cache_path, "r") as f:
                cache_entry = json.load(f)

            timestamp = cache_entry.get("timestamp", 0)
            ttl = cache_entry.get("ttl", 0)
            data = cache_entry.get("data")

            if check_ttl:
                age = time.time() - timestamp
                if age > ttl:
                    logger.debug(f"Cache expired for {key} (age: {age:.0f}s, TTL: {ttl}s)")
                    return None

            logger.debug(f"Retrieved cached {key}")
            return data
        except Exception as e:
            logger.error(f"Failed to retrieve cache for {key}: {e}")
            return None

    def get_ignore_ttl(self, key: str) -> Optional[Any]:
        """Get cached data regardless of TTL (for offline fallback).

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found
        """
        return self.get(key, check_ttl=False)

    def clear(self, key: str) -> bool:
        """Clear cache entry.

        Args:
            key: Cache key

        Returns:
            True if cleared successfully
        """
        try:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
                logger.debug(f"Cleared cache for {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache for {key}: {e}")
            return False

    def clear_all(self) -> bool:
        """Clear all cache entries.

        Returns:
            True if all cleared successfully
        """
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.debug("Cleared all cache entries")
            return True
        except Exception as e:
            logger.error(f"Failed to clear all cache: {e}")
            return False

    def get_cache_info(self, key: str) -> Optional[dict]:
        """Get cache metadata (age, TTL, etc).

        Args:
            key: Cache key

        Returns:
            Dict with timestamp, ttl, age_seconds, or None if not found
        """
        try:
            cache_path = self._get_cache_path(key)
            if not cache_path.exists():
                return None

            with open(cache_path, "r") as f:
                cache_entry = json.load(f)

            timestamp = cache_entry.get("timestamp", 0)
            ttl = cache_entry.get("ttl", 0)
            age = time.time() - timestamp
            is_expired = age > ttl

            return {
                "timestamp": timestamp,
                "ttl": ttl,
                "age_seconds": age,
                "is_expired": is_expired,
                "expires_in": max(0, ttl - age),
            }
        except Exception as e:
            logger.error(f"Failed to get cache info for {key}: {e}")
            return None


# Global instance
cache_manager = CacheManager()
