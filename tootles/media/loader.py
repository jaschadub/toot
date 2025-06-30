"""Async media loading and downloading."""

import asyncio
import io
import logging
from typing import Optional, Tuple

import httpx
from PIL import Image

from .cache import MediaCache
from .formats import MediaFormat, get_media_format

logger = logging.getLogger(__name__)


class MediaLoadError(Exception):
    """Exception raised when media loading fails."""
    pass


class MediaLoader:
    """Handles async loading and processing of media files."""

    def __init__(self, cache: MediaCache, timeout: int = 30):
        """Initialize media loader.

        Args:
            cache: Media cache instance
            timeout: Request timeout in seconds
        """
        self.cache = cache
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._semaphore = asyncio.Semaphore(5)  # Limit concurrent downloads

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def load_media(
        self,
        url: str,
        prefer_thumbnail: bool = True
    ) -> Optional[bytes]:
        """Load media from URL with caching.

        Args:
            url: Media URL
            prefer_thumbnail: Whether to prefer thumbnail if available

        Returns:
            Media data or None if loading fails
        """
        # Try cache first
        if prefer_thumbnail:
            cached_data = await self.cache.get_thumbnail(url)
            if cached_data:
                return cached_data

        cached_data = await self.cache.get_full_media(url)
        if cached_data:
            return cached_data

        # Download if not cached
        try:
            async with self._semaphore:
                data = await self._download_media(url)
                if data:
                    # Store in appropriate cache
                    await self.cache.store_full_media(url, data)

                    # Generate and cache thumbnail for images
                    if prefer_thumbnail and self._is_image(url):
                        thumbnail = await self._generate_thumbnail(data)
                        if thumbnail:
                            await self.cache.store_thumbnail(url, thumbnail)
                            return thumbnail

                    return data
        except Exception as e:
            logger.warning(f"Failed to load media from {url}: {e}")
            raise MediaLoadError(f"Failed to load media: {e}") from e

        return None

    async def load_thumbnail(self, url: str, size: Tuple[int, int] = (150, 150)) -> Optional[bytes]:
        """Load or generate thumbnail for media.

        Args:
            url: Media URL
            size: Thumbnail size (width, height)

        Returns:
            Thumbnail data or None
        """
        # Check thumbnail cache first
        cached_thumbnail = await self.cache.get_thumbnail(url)
        if cached_thumbnail:
            return cached_thumbnail

        # Check if we have full media cached
        cached_media = await self.cache.get_full_media(url)
        if cached_media and self._is_image(url):
            thumbnail = await self._generate_thumbnail(cached_media, size)
            if thumbnail:
                await self.cache.store_thumbnail(url, thumbnail)
                return thumbnail

        # Download and generate thumbnail
        try:
            async with self._semaphore:
                data = await self._download_media(url)
                if data and self._is_image(url):
                    # Store full media
                    await self.cache.store_full_media(url, data)

                    # Generate thumbnail
                    thumbnail = await self._generate_thumbnail(data, size)
                    if thumbnail:
                        await self.cache.store_thumbnail(url, thumbnail)
                        return thumbnail
        except Exception as e:
            logger.warning(f"Failed to load thumbnail from {url}: {e}")

        return None

    async def _download_media(self, url: str) -> Optional[bytes]:
        """Download media from URL.

        Args:
            url: Media URL

        Returns:
            Media data or None
        """
        if not self._client:
            raise MediaLoadError("HTTP client not initialized")

        try:
            response = await self._client.get(url)
            response.raise_for_status()

            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > 50 * 1024 * 1024:  # 50MB limit
                raise MediaLoadError("Media file too large")

            return response.content

        except httpx.HTTPError as e:
            raise MediaLoadError(f"HTTP error: {e}") from e
        except Exception as e:
            raise MediaLoadError(f"Download failed: {e}") from e

    async def _generate_thumbnail(
        self,
        image_data: bytes,
        size: Tuple[int, int] = (150, 150)
    ) -> Optional[bytes]:
        """Generate thumbnail from image data.

        Args:
            image_data: Original image data
            size: Thumbnail size (width, height)

        Returns:
            Thumbnail data or None
        """
        try:
            # Run image processing in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            thumbnail_data = await loop.run_in_executor(
                None,
                self._process_thumbnail,
                image_data,
                size
            )
            return thumbnail_data
        except Exception as e:
            logger.warning(f"Failed to generate thumbnail: {e}")
            return None

    def _process_thumbnail(self, image_data: bytes, size: Tuple[int, int]) -> bytes:
        """Process thumbnail in thread pool.

        Args:
            image_data: Original image data
            size: Thumbnail size

        Returns:
            Thumbnail data
        """
        with Image.open(io.BytesIO(image_data)) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            # Generate thumbnail maintaining aspect ratio
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Save as JPEG
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()

    def _is_image(self, url: str) -> bool:
        """Check if URL points to an image.

        Args:
            url: Media URL

        Returns:
            True if URL is an image
        """
        return get_media_format(url) == MediaFormat.IMAGE

    async def preload_media(self, urls: list[str]) -> None:
        """Preload multiple media files.

        Args:
            urls: List of media URLs to preload
        """
        tasks = []
        for url in urls:
            if self._is_image(url):
                # Preload thumbnails for images
                task = asyncio.create_task(self.load_thumbnail(url))
            else:
                # Just check cache for non-images
                task = asyncio.create_task(self.cache.get_full_media(url))
            tasks.append(task)

        if tasks:
            # Wait for all preload tasks with timeout
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.debug("Media preload timed out")
