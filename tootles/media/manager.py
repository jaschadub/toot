"""Central media manager for coordinating all media operations."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from textual.widget import Widget

from .cache import MediaCache
from .external import ExternalViewerManager
from .formats import get_media_format, is_supported_format
from .loader import MediaLoader
from .renderer import MediaRenderer

logger = logging.getLogger(__name__)


class MediaManager:
    """Central coordinator for all media operations."""

    def __init__(self, config):
        """Initialize media manager.

        Args:
            config: MediaConfig object or Tootles configuration object
        """
        self.config = config
        # Handle both MediaConfig directly and config.media
        media_config = config if hasattr(config, 'memory_cache_size') else config.media

        self.cache = MediaCache(
            memory_cache_mb=media_config.memory_cache_size,
            disk_cache_mb=media_config.disk_cache_size,
            cache_dir=media_config.cache_directory
        )
        self.external_viewer = ExternalViewerManager(media_config.external_viewers)
        self.renderer = MediaRenderer(config, self.external_viewer)
        self._loader: Optional[MediaLoader] = None
        self._loader_lock = asyncio.Lock()

    async def _get_loader(self) -> MediaLoader:
        """Get or create media loader instance.

        Returns:
            MediaLoader instance
        """
        if self._loader is None:
            async with self._loader_lock:
                if self._loader is None:
                    self._loader = MediaLoader(self.cache)
                    await self._loader.__aenter__()
        return self._loader

    async def get_media_widget(
        self,
        attachment,
        size: str = "thumbnail",
        preload: bool = True
    ) -> Widget:
        """Get appropriate widget for media attachment.

        Args:
            attachment: MediaAttachment object
            size: Size hint ("thumbnail", "medium", "full")
            preload: Whether to preload media data

        Returns:
            Widget for displaying media
        """
        media_config = self.config if hasattr(self.config, 'memory_cache_size') else self.config.media
        if not media_config.show_media_previews:
            return self._create_disabled_placeholder(attachment)

        if not is_supported_format(attachment.url, attachment.type):
            return self.renderer._create_generic_placeholder(attachment)

        media_data = None
        if preload:
            try:
                loader = await self._get_loader()
                if size == "thumbnail":
                    media_data = await loader.load_thumbnail(attachment.url)
                else:
                    media_data = await loader.load_media(attachment.url, prefer_thumbnail=False)
            except Exception as e:
                logger.debug(f"Failed to preload media for {attachment.url}: {e}")

        return await self.renderer.create_media_widget(attachment, media_data, size)

    async def preload_media(self, attachments: List[Any]) -> None:
        """Preload media for better UX.

        Args:
            attachments: List of MediaAttachment objects
        """
        media_config = self.config if hasattr(self.config, 'memory_cache_size') else self.config.media
        if not media_config.show_media_previews or not attachments:
            return

        try:
            loader = await self._get_loader()
            urls = [att.url for att in attachments if is_supported_format(att.url, att.type)]
            if urls:
                await loader.preload_media(urls)
        except Exception as e:
            logger.debug(f"Failed to preload media: {e}")

    async def open_media_external(
        self,
        attachment,
        use_cached: bool = True
    ) -> bool:
        """Open media in external viewer.

        Args:
            attachment: MediaAttachment object
            use_cached: Whether to use cached data if available

        Returns:
            True if successfully opened
        """
        media_data = None

        if use_cached:
            try:
                # Try to get cached data first
                cached_data = await self.cache.get_full_media(attachment.url)
                if cached_data:
                    media_data = cached_data
                else:
                    # Load if not cached
                    loader = await self._get_loader()
                    media_data = await loader.load_media(attachment.url, prefer_thumbnail=False)
            except Exception as e:
                logger.debug(f"Failed to load cached media: {e}")

        return await self.renderer.open_external(attachment, media_data)

    async def get_media_data(
        self,
        url: str,
        prefer_thumbnail: bool = True
    ) -> Optional[bytes]:
        """Get media data for URL.

        Args:
            url: Media URL
            prefer_thumbnail: Whether to prefer thumbnail

        Returns:
            Media data or None
        """
        try:
            loader = await self._get_loader()
            return await loader.load_media(url, prefer_thumbnail)
        except Exception as e:
            logger.debug(f"Failed to get media data for {url}: {e}")
            return None

    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported media formats by type.

        Returns:
            Dict mapping format types to lists of supported formats
        """
        return self.renderer.get_supported_formats()

    def can_display_inline(self, attachment) -> bool:
        """Check if media can be displayed inline.

        Args:
            attachment: MediaAttachment object

        Returns:
            True if can display inline
        """
        return self.renderer.can_render_inline(attachment)

    def is_external_viewer_available(self, attachment) -> bool:
        """Check if external viewer is available for media.

        Args:
            attachment: MediaAttachment object

        Returns:
            True if external viewer is available
        """
        media_format = get_media_format(attachment.url, attachment.type)
        return self.external_viewer.is_viewer_available(media_format.value)

    def _create_disabled_placeholder(self, attachment) -> Widget:
        """Create placeholder when media previews are disabled.

        Args:
            attachment: MediaAttachment object

        Returns:
            Disabled placeholder widget
        """
        from textual.widgets import Static

        content = f"📎 {attachment.description or 'Media attachment'} (previews disabled)"
        widget = Static(content)
        widget.add_class("media-disabled-placeholder")
        return widget

    async def clear_cache(self) -> None:
        """Clear all media caches."""
        await self.cache.clear_all()

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict with cache statistics
        """
        # This would be enhanced with actual cache statistics
        return {
            "memory_cache_size": self.cache.memory_cache.current_size,
            "memory_cache_items": len(self.cache.memory_cache.cache),
            "disk_cache_available": True,
            "external_viewers": self.external_viewer.get_available_viewers()
        }

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self._loader:
            await self._loader.__aexit__(None, None, None)
            self._loader = None

        self.external_viewer.cleanup_temp_files()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
