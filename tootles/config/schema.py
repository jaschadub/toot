"""Configuration schema and validation for Tootles."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class MediaConfig:
    """Media-specific configuration."""

    # Display settings
    show_media_previews: bool = True
    inline_image_max_height: int = 20  # Terminal rows
    thumbnail_size: Tuple[int, int] = (150, 150)  # Pixels

    # Cache settings
    memory_cache_size: int = 50  # MB for thumbnails
    disk_cache_size: int = 500   # MB for full images
    cache_directory: str = "~/.cache/tootles/media"
    cache_expiry_days: int = 7

    # External viewers
    external_viewers: Dict[str, str] = field(default_factory=lambda: {
        "image": "feh",
        "video": "mpv",
        "audio": "mpv"
    })

    # Format support
    supported_image_formats: List[str] = field(default_factory=lambda: [
        "jpg", "jpeg", "png", "gif", "webp", "svg"
    ])
    supported_video_formats: List[str] = field(default_factory=lambda: [
        "mp4", "webm", "mov", "avi"
    ])
    supported_audio_formats: List[str] = field(default_factory=lambda: [
        "mp3", "ogg", "wav", "m4a"
    ])


@dataclass
class TootlesConfig:
    """Main configuration structure for Tootles."""

    # Instance settings
    instance_url: str = ""
    access_token: str = ""

    # UI settings
    theme: str = "standard"
    auto_refresh: bool = True
    refresh_interval: int = 60
    show_media_previews: bool = True

    # Timeline settings
    timeline_limit: int = 40
    enable_streaming: bool = True
    mark_notifications_read: bool = True

    # Search settings
    search_history_size: int = 100
    enable_fuzzy_search: bool = True

    # Theme settings
    theme_directory: str = "~/.config/tootles/themes"
    enable_theme_hot_reload: bool = False

    # Advanced settings
    cache_size: int = 1000
    rate_limit_requests: int = 300
    rate_limit_window: int = 300

    # Custom timelines
    timelines: Dict[str, Dict[str, str]] = field(default_factory=dict)

    # Media configuration
    media: MediaConfig = field(default_factory=MediaConfig)

    def get_theme_directory(self) -> Path:
        """Get the theme directory as a Path object."""
        return Path(self.theme_directory).expanduser()

    def validate(self) -> None:
        """Validate configuration values."""
        if self.timeline_limit < 1 or self.timeline_limit > 100:
            raise ValueError("timeline_limit must be between 1 and 100")

        if self.refresh_interval < 10:
            raise ValueError("refresh_interval must be at least 10 seconds")

        if self.search_history_size < 0:
            raise ValueError("search_history_size must be non-negative")

        if self.cache_size < 0:
            raise ValueError("cache_size must be non-negative")

        if self.rate_limit_requests < 1:
            raise ValueError("rate_limit_requests must be positive")

        if self.rate_limit_window < 1:
            raise ValueError("rate_limit_window must be positive")
