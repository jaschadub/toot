"""Smart caching system for media files."""

import asyncio
import hashlib
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

import aiofiles

logger = logging.getLogger(__name__)


class MediaCacheError(Exception):
    """Base exception for cache operations."""
    pass


class MemoryCache:
    """In-memory LRU cache for thumbnails and small media."""

    def __init__(self, maxsize: int = 50):
        """Initialize memory cache.

        Args:
            maxsize: Maximum cache size in MB
        """
        self.maxsize = maxsize * 1024 * 1024  # Convert to bytes
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.current_size = 0
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[bytes]:
        """Get item from cache.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found
        """
        async with self._lock:
            if key in self.cache:
                self.access_times[key] = time.time()
                return self.cache[key]['data']
            return None

    async def set(self, key: str, data: bytes) -> None:
        """Set item in cache.

        Args:
            key: Cache key
            data: Data to cache
        """
        async with self._lock:
            data_size = len(data)

            # Check if we need to evict items
            while (self.current_size + data_size > self.maxsize and
                   len(self.cache) > 0):
                await self._evict_lru()

            # Only cache if data fits
            if data_size <= self.maxsize:
                self.cache[key] = {
                    'data': data,
                    'size': data_size,
                    'timestamp': time.time()
                }
                self.access_times[key] = time.time()
                self.current_size += data_size

    async def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if not self.access_times:
            return

        lru_key = min(self.access_times.keys(),
                     key=lambda k: self.access_times[k])

        if lru_key in self.cache:
            self.current_size -= self.cache[lru_key]['size']
            del self.cache[lru_key]
            del self.access_times[lru_key]

    async def clear(self) -> None:
        """Clear all cached items."""
        async with self._lock:
            self.cache.clear()
            self.access_times.clear()
            self.current_size = 0


class DiskCache:
    """Disk-based cache for full-size media."""

    def __init__(self, cache_dir: str, max_size_mb: int = 500):
        """Initialize disk cache.

        Args:
            cache_dir: Cache directory path
            max_size_mb: Maximum cache size in MB
        """
        self.cache_dir = Path(cache_dir).expanduser()
        self.max_size = max_size_mb * 1024 * 1024  # Convert to bytes
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key.

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        # Use hash to create safe filename
        hash_key = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.cache"

    async def get(self, key: str) -> Optional[bytes]:
        """Get item from disk cache.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found
        """
        cache_path = self._get_cache_path(key)

        try:
            if cache_path.exists():
                async with aiofiles.open(cache_path, 'rb') as f:
                    data = await f.read()

                # Update access time
                cache_path.touch()
                return data
        except Exception:
            # Remove corrupted cache file
            try:
                cache_path.unlink(missing_ok=True)
            except Exception as e:
                logger.debug(f"Failed to remove cache file {cache_path}: {e}")

        return None

    async def set(self, key: str, data: bytes) -> None:
        """Set item in disk cache.

        Args:
            key: Cache key
            data: Data to cache
        """
        async with self._lock:
            cache_path = self._get_cache_path(key)

            try:
                # Check if we need to clean up space
                await self._cleanup_if_needed(len(data))

                # Write to temporary file first, then rename for atomicity
                temp_path = cache_path.with_suffix('.tmp')
                async with aiofiles.open(temp_path, 'wb') as f:
                    await f.write(data)

                temp_path.rename(cache_path)

            except Exception as e:
                # Clean up temp file if it exists
                try:
                    temp_path.unlink(missing_ok=True)
                except Exception as e:
                    logger.debug(f"Failed to clean up temp file {temp_path}: {e}")
                raise MediaCacheError(f"Failed to cache data: {e}") from e

    async def _cleanup_if_needed(self, new_data_size: int) -> None:
        """Clean up cache if needed to make space.

        Args:
            new_data_size: Size of new data to be cached
        """
        current_size = await self._get_cache_size()

        if current_size + new_data_size > self.max_size:
            # Get all cache files sorted by access time (oldest first)
            cache_files = []
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    stat = cache_file.stat()
                    cache_files.append((cache_file, stat.st_atime, stat.st_size))
                except Exception as e:
                    logger.debug(f"Failed to get file stats for {cache_file}: {e}")
                    continue

            cache_files.sort(key=lambda x: x[1])  # Sort by access time

            # Remove files until we have enough space
            for cache_file, _, file_size in cache_files:
                if current_size + new_data_size <= self.max_size:
                    break

                try:
                    cache_file.unlink()
                    current_size -= file_size
                except Exception as e:
                    logger.debug(f"Failed to get file stats for {cache_file}: {e}")
                    continue

    async def _get_cache_size(self) -> int:
        """Get current cache size in bytes.

        Returns:
            Total cache size in bytes
        """
        total_size = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                total_size += cache_file.stat().st_size
            except Exception as e:
                logger.debug(f"Failed to get file size for {cache_file}: {e}")
                continue
        return total_size

    async def clear(self) -> None:
        """Clear all cached files."""
        async with self._lock:
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.debug(f"Failed to get file stats for {cache_file}: {e}")
                    continue


class MediaCache:
    """Smart caching system with memory and disk tiers."""

    def __init__(
        self,
        memory_cache_mb: int = 50,
        disk_cache_mb: int = 500,
        cache_dir: str = "~/.cache/tootles/media"
    ):
        """Initialize media cache.

        Args:
            memory_cache_mb: Memory cache size in MB
            disk_cache_mb: Disk cache size in MB
            cache_dir: Disk cache directory
        """
        self.memory_cache = MemoryCache(memory_cache_mb)
        self.disk_cache = DiskCache(cache_dir, disk_cache_mb)

    def _get_cache_key(self, url: str, is_thumbnail: bool = False) -> str:
        """Generate cache key for URL.

        Args:
            url: Media URL
            is_thumbnail: Whether this is a thumbnail

        Returns:
            Cache key
        """
        prefix = "thumb_" if is_thumbnail else "full_"
        return f"{prefix}{url}"

    async def get_thumbnail(self, url: str) -> Optional[bytes]:
        """Get thumbnail from memory cache.

        Args:
            url: Media URL

        Returns:
            Thumbnail data or None
        """
        key = self._get_cache_key(url, is_thumbnail=True)
        return await self.memory_cache.get(key)

    async def get_full_media(self, url: str) -> Optional[bytes]:
        """Get full media from disk cache with memory fallback.

        Args:
            url: Media URL

        Returns:
            Media data or None
        """
        key = self._get_cache_key(url, is_thumbnail=False)

        # Try memory cache first (for smaller files)
        data = await self.memory_cache.get(key)
        if data:
            return data

        # Fall back to disk cache
        return await self.disk_cache.get(key)

    async def store_thumbnail(self, url: str, data: bytes) -> None:
        """Store thumbnail in memory cache.

        Args:
            url: Media URL
            data: Thumbnail data
        """
        key = self._get_cache_key(url, is_thumbnail=True)
        await self.memory_cache.set(key, data)

    async def store_full_media(self, url: str, data: bytes) -> None:
        """Store full media using appropriate cache tier.

        Args:
            url: Media URL
            data: Media data
        """
        key = self._get_cache_key(url, is_thumbnail=False)

        # Store small files in memory, large files on disk
        if len(data) < 1024 * 1024:  # < 1MB
            await self.memory_cache.set(key, data)
        else:
            await self.disk_cache.set(key, data)

    async def clear_all(self) -> None:
        """Clear all caches."""
        await self.memory_cache.clear()
        await self.disk_cache.clear()
