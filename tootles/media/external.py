"""External viewer integration for media files."""

import asyncio
import logging
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional

from .formats import MediaFormat, get_media_format

logger = logging.getLogger(__name__)


class ExternalViewerError(Exception):
    """Exception raised when external viewer operations fail."""
    pass


class ExternalViewerManager:
    """Manages external media viewers."""

    def __init__(self, viewer_config: Optional[Dict[str, str]] = None):
        """Initialize external viewer manager.

        Args:
            viewer_config: Dict mapping media types to viewer commands
        """
        self.viewers = viewer_config or self._get_default_viewers()
        self._temp_files: list[Path] = []

    def _get_default_viewers(self) -> Dict[str, str]:
        """Get default external viewers based on available programs.

        Returns:
            Dict mapping media types to viewer commands
        """
        viewers = {}

        # Image viewers
        for viewer in ['feh', 'eog', 'xviewer', 'gwenview', 'ristretto']:
            if shutil.which(viewer):
                viewers['image'] = viewer
                break

        # Video/audio players
        for player in ['mpv', 'vlc', 'mplayer', 'totem']:
            if shutil.which(player):
                viewers['video'] = player
                viewers['audio'] = player
                break

        # Fallback to xdg-open
        if shutil.which('xdg-open'):
            if 'image' not in viewers:
                viewers['image'] = 'xdg-open'
            if 'video' not in viewers:
                viewers['video'] = 'xdg-open'
            if 'audio' not in viewers:
                viewers['audio'] = 'xdg-open'

        return viewers

    def get_viewer_for_url(self, url: str) -> Optional[str]:
        """Get appropriate viewer command for media URL.

        Args:
            url: Media URL

        Returns:
            Viewer command or None if no viewer available
        """
        media_format = get_media_format(url)

        if media_format == MediaFormat.IMAGE:
            return self.viewers.get('image')
        elif media_format == MediaFormat.VIDEO:
            return self.viewers.get('video')
        elif media_format == MediaFormat.AUDIO:
            return self.viewers.get('audio')

        return None

    async def open_media(self, url: str, media_data: Optional[bytes] = None) -> bool:
        """Open media in external viewer.

        Args:
            url: Media URL
            media_data: Optional media data (if None, viewer will download)

        Returns:
            True if successfully opened
        """
        viewer_cmd = self.get_viewer_for_url(url)
        if not viewer_cmd:
            logger.warning(f"No external viewer available for {url}")
            return False

        try:
            if media_data:
                # Save to temporary file and open
                return await self._open_from_data(viewer_cmd, url, media_data)
            else:
                # Open URL directly
                return await self._open_from_url(viewer_cmd, url)
        except Exception as e:
            logger.error(f"Failed to open media in external viewer: {e}")
            raise ExternalViewerError(f"Failed to open media: {e}") from e

    async def _open_from_data(self, viewer_cmd: str, url: str, data: bytes) -> bool:
        """Open media from data using temporary file.

        Args:
            viewer_cmd: Viewer command
            url: Original URL (for file extension)
            data: Media data

        Returns:
            True if successfully opened
        """
        # Create temporary file with appropriate extension
        suffix = Path(url).suffix or '.tmp'
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        temp_file = Path(temp_path)

        try:
            # Close the file descriptor and write data to temporary file
            import os
            os.close(fd)
            temp_file.write_bytes(data)
            self._temp_files.append(temp_file)

            # Open with viewer
            return await self._execute_viewer(viewer_cmd, str(temp_file))

        except Exception as e:
            # Clean up temp file on error
            try:
                temp_file.unlink(missing_ok=True)
                if temp_file in self._temp_files:
                    self._temp_files.remove(temp_file)
            except Exception as cleanup_error:
                logger.debug(f"Failed to clean up temp file {temp_file}: {cleanup_error}")
            raise e

    async def _open_from_url(self, viewer_cmd: str, url: str) -> bool:
        """Open media directly from URL.

        Args:
            viewer_cmd: Viewer command
            url: Media URL

        Returns:
            True if successfully opened
        """
        return await self._execute_viewer(viewer_cmd, url)

    async def _execute_viewer(self, viewer_cmd: str, target: str) -> bool:
        """Execute viewer command.

        Args:
            viewer_cmd: Viewer command
            target: File path or URL to open

        Returns:
            True if successfully executed
        """
        try:
            # Split command to handle arguments
            cmd_parts = viewer_cmd.split()
            cmd_parts.append(target)

            # Execute in background (don't wait for completion)
            process = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
                start_new_session=True  # Detach from parent
            )

            # Don't wait for the viewer to close
            logger.debug(f"Opened {target} with {viewer_cmd} (PID: {process.pid})")
            return True

        except Exception as e:
            logger.error(f"Failed to execute viewer command '{viewer_cmd}': {e}")
            return False

    def is_viewer_available(self, media_type: str) -> bool:
        """Check if external viewer is available for media type.

        Args:
            media_type: Media type ('image', 'video', 'audio')

        Returns:
            True if viewer is available
        """
        viewer_cmd = self.viewers.get(media_type)
        if not viewer_cmd:
            return False

        # Check if command exists
        cmd_name = viewer_cmd.split()[0]
        return shutil.which(cmd_name) is not None

    def get_available_viewers(self) -> Dict[str, str]:
        """Get dict of available viewers.

        Returns:
            Dict mapping media types to available viewer commands
        """
        available = {}
        for media_type, viewer_cmd in self.viewers.items():
            if self.is_viewer_available(media_type):
                available[media_type] = viewer_cmd
        return available

    def cleanup_temp_files(self) -> None:
        """Clean up temporary files created for external viewers."""
        for temp_file in self._temp_files[:]:
            try:
                temp_file.unlink(missing_ok=True)
                self._temp_files.remove(temp_file)
            except Exception as e:
                logger.debug(f"Failed to clean up temp file {temp_file}: {e}")

    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup_temp_files()
