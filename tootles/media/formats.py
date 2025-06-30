"""Media format detection and validation."""

import mimetypes
from enum import Enum
from pathlib import Path
from typing import Optional, Set


class MediaFormat(Enum):
    """Supported media formats."""

    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    UNKNOWN = "unknown"


class MediaFormatConfig:
    """Configuration for supported media formats."""

    SUPPORTED_IMAGE_FORMATS: Set[str] = {
        "jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "tiff"
    }

    SUPPORTED_VIDEO_FORMATS: Set[str] = {
        "mp4", "webm", "mov", "avi", "mkv", "m4v", "ogv"
    }

    SUPPORTED_AUDIO_FORMATS: Set[str] = {
        "mp3", "ogg", "wav", "m4a", "aac", "flac", "opus"
    }

    IMAGE_MIMETYPES: Set[str] = {
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "image/svg+xml", "image/bmp", "image/tiff"
    }

    VIDEO_MIMETYPES: Set[str] = {
        "video/mp4", "video/webm", "video/quicktime", "video/x-msvideo",
        "video/x-matroska", "video/ogg"
    }

    AUDIO_MIMETYPES: Set[str] = {
        "audio/mpeg", "audio/ogg", "audio/wav", "audio/mp4",
        "audio/aac", "audio/flac", "audio/opus"
    }


def get_media_format(url: str, mimetype: Optional[str] = None) -> MediaFormat:
    """Determine media format from URL and/or mimetype.

    Args:
        url: Media URL
        mimetype: Optional MIME type

    Returns:
        MediaFormat enum value
    """
    # First try mimetype if provided
    if mimetype:
        if mimetype in MediaFormatConfig.IMAGE_MIMETYPES:
            return MediaFormat.IMAGE
        elif mimetype in MediaFormatConfig.VIDEO_MIMETYPES:
            return MediaFormat.VIDEO
        elif mimetype in MediaFormatConfig.AUDIO_MIMETYPES:
            return MediaFormat.AUDIO

    # Fall back to file extension
    try:
        path = Path(url)
        extension = path.suffix.lower().lstrip('.')

        if extension in MediaFormatConfig.SUPPORTED_IMAGE_FORMATS:
            return MediaFormat.IMAGE
        elif extension in MediaFormatConfig.SUPPORTED_VIDEO_FORMATS:
            return MediaFormat.VIDEO
        elif extension in MediaFormatConfig.SUPPORTED_AUDIO_FORMATS:
            return MediaFormat.AUDIO
    except Exception:
        # Failed to parse URL or determine format from URL
        pass

    # Try mimetypes module as last resort
    try:
        guessed_type, _ = mimetypes.guess_type(url)
        if guessed_type:
            if guessed_type.startswith('image/'):
                return MediaFormat.IMAGE
            elif guessed_type.startswith('video/'):
                return MediaFormat.VIDEO
            elif guessed_type.startswith('audio/'):
                return MediaFormat.AUDIO
    except Exception:
        # Failed to parse URL or determine format from URL
        pass

    return MediaFormat.UNKNOWN


def is_supported_format(url: str, mimetype: Optional[str] = None) -> bool:
    """Check if media format is supported.

    Args:
        url: Media URL
        mimetype: Optional MIME type

    Returns:
        True if format is supported
    """
    return get_media_format(url, mimetype) != MediaFormat.UNKNOWN


def can_display_inline(url: str, mimetype: Optional[str] = None) -> bool:
    """Check if media can be displayed inline in terminal.

    Args:
        url: Media URL
        mimetype: Optional MIME type

    Returns:
        True if can display inline
    """
    format_type = get_media_format(url, mimetype)
    # Currently only images can be displayed inline
    return format_type == MediaFormat.IMAGE


def get_file_extension(url: str) -> str:
    """Extract file extension from URL.

    Args:
        url: Media URL

    Returns:
        File extension without dot
    """
    try:
        return Path(url).suffix.lower().lstrip('.')
    except Exception:
        return ""
