"""Media rendering for different display contexts."""

import logging
from typing import Optional, Tuple

from textual.widget import Widget
from textual.widgets import Static

from .external import ExternalViewerManager
from .formats import MediaFormat, can_display_inline, get_media_format

logger = logging.getLogger(__name__)


class MediaRenderError(Exception):
    """Exception raised when media rendering fails."""
    pass


class MediaRenderer:
    """Handles different media rendering strategies."""

    def __init__(self, config, external_viewer_manager: Optional[ExternalViewerManager] = None):
        """Initialize media renderer.

        Args:
            config: Tootles configuration
            external_viewer_manager: External viewer manager instance
        """
        self.config = config
        self.external_viewer = external_viewer_manager or ExternalViewerManager()
        self._textual_available = self._check_textual_image_support()

    def _check_textual_image_support(self) -> bool:
        """Check if terminal supports inline image display.

        Returns:
            True if inline images are supported
        """
        # For now, assume basic support - this could be enhanced
        # to detect specific terminal capabilities
        return True

    async def create_media_widget(
        self,
        attachment,
        media_data: Optional[bytes] = None,
        size: str = "thumbnail"
    ) -> Widget:
        """Create appropriate widget for media attachment.

        Args:
            attachment: MediaAttachment object
            media_data: Optional media data
            size: Size hint ("thumbnail", "medium", "full")

        Returns:
            Widget for displaying media
        """
        media_format = get_media_format(attachment.url, attachment.type)

        if media_format == MediaFormat.IMAGE and can_display_inline(attachment.url):
            return await self._create_image_widget(attachment, media_data, size)
        elif media_format == MediaFormat.VIDEO:
            return self._create_video_placeholder(attachment)
        elif media_format == MediaFormat.AUDIO:
            return self._create_audio_placeholder(attachment)
        else:
            return self._create_generic_placeholder(attachment)

    async def _create_image_widget(
        self,
        attachment,
        media_data: Optional[bytes],
        size: str
    ) -> Widget:
        """Create widget for image display.

        Args:
            attachment: MediaAttachment object
            media_data: Optional image data
            size: Size hint

        Returns:
            Image widget
        """
        if media_data and self._textual_available:
            # Try to create inline image widget
            try:
                return await self._create_inline_image(attachment, media_data, size)
            except Exception as e:
                logger.debug(f"Failed to create inline image: {e}")

        # Fall back to placeholder with preview info
        return self._create_image_placeholder(attachment)

    async def _create_inline_image(
        self,
        attachment,
        image_data: bytes,
        size: str
    ) -> Widget:
        """Create inline image widget using Textual capabilities.

        Args:
            attachment: MediaAttachment object
            image_data: Image data
            size: Size hint

        Returns:
            Inline image widget
        """
        # For now, create a placeholder that shows image info
        # This would be enhanced with actual image rendering
        # when Textual image widgets become available

        dimensions = self._get_image_dimensions(image_data)
        size_kb = len(image_data) // 1024

        content = []
        content.append(f"🖼️ {attachment.description or 'Image'}")
        if dimensions:
            content.append(f"📐 {dimensions[0]}×{dimensions[1]}")
        content.append(f"💾 {size_kb}KB")

        widget = Static("\n".join(content))
        widget.add_class("media-image-preview")
        return widget

    def _get_image_dimensions(self, image_data: bytes) -> Optional[Tuple[int, int]]:
        """Get image dimensions from data.

        Args:
            image_data: Image data

        Returns:
            (width, height) tuple or None
        """
        try:
            import io

            from PIL import Image

            with Image.open(io.BytesIO(image_data)) as img:
                return img.size
        except Exception:
            return None

    def _create_image_placeholder(self, attachment) -> Widget:
        """Create placeholder widget for images.

        Args:
            attachment: MediaAttachment object

        Returns:
            Image placeholder widget
        """
        content = []
        content.append(f"🖼️ {attachment.description or 'Image'}")

        if hasattr(attachment, 'meta') and attachment.meta:
            original = attachment.meta.get('original', {})
            if 'width' in original and 'height' in original:
                content.append(f"📐 {original['width']}×{original['height']}")
            if 'size' in original:
                size_kb = int(original['size']) // 1024
                content.append(f"💾 {size_kb}KB")

        content.append("👁️ Press Enter to view")

        widget = Static("\n".join(content))
        widget.add_class("media-image-placeholder")
        return widget

    def _create_video_placeholder(self, attachment) -> Widget:
        """Create placeholder widget for videos.

        Args:
            attachment: MediaAttachment object

        Returns:
            Video placeholder widget
        """
        content = []
        content.append(f"🎬 {attachment.description or 'Video'}")

        if hasattr(attachment, 'meta') and attachment.meta:
            original = attachment.meta.get('original', {})
            if 'width' in original and 'height' in original:
                content.append(f"📐 {original['width']}×{original['height']}")
            if 'duration' in original:
                duration = float(original['duration'])
                mins, secs = divmod(int(duration), 60)
                content.append(f"⏱️ {mins:02d}:{secs:02d}")
            if 'size' in original:
                size_mb = int(original['size']) // (1024 * 1024)
                content.append(f"💾 {size_mb}MB")

        content.append("▶️ Press Enter to play")

        widget = Static("\n".join(content))
        widget.add_class("media-video-placeholder")
        return widget

    def _create_audio_placeholder(self, attachment) -> Widget:
        """Create placeholder widget for audio.

        Args:
            attachment: MediaAttachment object

        Returns:
            Audio placeholder widget
        """
        content = []
        content.append(f"🎵 {attachment.description or 'Audio'}")

        if hasattr(attachment, 'meta') and attachment.meta:
            original = attachment.meta.get('original', {})
            if 'duration' in original:
                duration = float(original['duration'])
                mins, secs = divmod(int(duration), 60)
                content.append(f"⏱️ {mins:02d}:{secs:02d}")
            if 'size' in original:
                size_mb = int(original['size']) // (1024 * 1024)
                content.append(f"💾 {size_mb}MB")

        content.append("🔊 Press Enter to play")

        widget = Static("\n".join(content))
        widget.add_class("media-audio-placeholder")
        return widget

    def _create_generic_placeholder(self, attachment) -> Widget:
        """Create placeholder widget for unknown media types.

        Args:
            attachment: MediaAttachment object

        Returns:
            Generic placeholder widget
        """
        content = []
        content.append(f"📎 {attachment.description or 'Media file'}")
        content.append("🔗 Press Enter to open")

        widget = Static("\n".join(content))
        widget.add_class("media-generic-placeholder")
        return widget

    async def open_external(self, attachment, media_data: Optional[bytes] = None) -> bool:
        """Open media in external viewer.

        Args:
            attachment: MediaAttachment object
            media_data: Optional media data

        Returns:
            True if successfully opened
        """
        try:
            return await self.external_viewer.open_media(attachment.url, media_data)
        except Exception as e:
            logger.error(f"Failed to open media externally: {e}")
            return False

    def can_render_inline(self, attachment) -> bool:
        """Check if media can be rendered inline.

        Args:
            attachment: MediaAttachment object

        Returns:
            True if can render inline
        """
        return (can_display_inline(attachment.url, attachment.type) and
                self._textual_available)

    def get_supported_formats(self) -> dict:
        """Get supported media formats.

        Returns:
            Dict of supported formats by type
        """
        return {
            'inline': ['image'] if self._textual_available else [],
            'external': list(self.external_viewer.get_available_viewers().keys())
        }
