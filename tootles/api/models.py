"""Data models for Mastodon API responses."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Account:
    """Represents a Mastodon account."""

    id: str
    username: str
    acct: str
    display_name: str
    locked: bool
    bot: bool
    discoverable: Optional[bool]
    group: bool
    created_at: datetime
    note: str
    url: str
    avatar: str
    avatar_static: str
    header: str
    header_static: str
    followers_count: int
    following_count: int
    statuses_count: int
    last_status_at: Optional[datetime]
    emojis: List[Dict[str, Any]]
    fields: List[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Account":
        """Create Account from API response data."""
        return cls(
            id=data["id"],
            username=data["username"],
            acct=data["acct"],
            display_name=data["display_name"],
            locked=data["locked"],
            bot=data["bot"],
            discoverable=data.get("discoverable"),
            group=data["group"],
            created_at=datetime.fromisoformat(
                data["created_at"].replace("Z", "+00:00")
            ),
            note=data["note"],
            url=data["url"],
            avatar=data["avatar"],
            avatar_static=data["avatar_static"],
            header=data["header"],
            header_static=data["header_static"],
            followers_count=data["followers_count"],
            following_count=data["following_count"],
            statuses_count=data["statuses_count"],
            last_status_at=datetime.fromisoformat(
                data["last_status_at"].replace("Z", "+00:00")
            ) if data.get("last_status_at") else None,
            emojis=data["emojis"],
            fields=data["fields"],
        )


@dataclass
class MediaAttachment:
    """Represents a media attachment."""

    id: str
    type: str
    url: str
    preview_url: str
    remote_url: Optional[str]
    text_url: Optional[str]
    meta: Dict[str, Any]
    description: Optional[str]
    blurhash: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MediaAttachment":
        """Create MediaAttachment from API response data."""
        return cls(
            id=data["id"],
            type=data["type"],
            url=data["url"],
            preview_url=data["preview_url"],
            remote_url=data.get("remote_url"),
            text_url=data.get("text_url"),
            meta=data["meta"],
            description=data.get("description"),
            blurhash=data.get("blurhash"),
        )


@dataclass
class Status:
    """Represents a Mastodon status (toot)."""

    id: str
    uri: str
    created_at: datetime
    account: Account
    content: str
    visibility: str
    sensitive: bool
    spoiler_text: str
    media_attachments: List[MediaAttachment]
    application: Optional[Dict[str, Any]]
    mentions: List[Dict[str, Any]]
    tags: List[Dict[str, Any]]
    emojis: List[Dict[str, Any]]
    reblogs_count: int
    favourites_count: int
    replies_count: int
    url: Optional[str]
    in_reply_to_id: Optional[str]
    in_reply_to_account_id: Optional[str]
    reblog: Optional["Status"]
    poll: Optional[Dict[str, Any]]
    card: Optional[Dict[str, Any]]
    language: Optional[str]
    text: Optional[str]
    favourited: bool
    reblogged: bool
    muted: bool
    bookmarked: bool
    pinned: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Status":
        """Create Status from API response data."""
        return cls(
            id=data["id"],
            uri=data["uri"],
            created_at=datetime.fromisoformat(
                data["created_at"].replace("Z", "+00:00")
            ),
            account=Account.from_dict(data["account"]),
            content=data["content"],
            visibility=data["visibility"],
            sensitive=data["sensitive"],
            spoiler_text=data["spoiler_text"],
            media_attachments=[
                MediaAttachment.from_dict(m) for m in data["media_attachments"]
            ],
            application=data.get("application"),
            mentions=data["mentions"],
            tags=data["tags"],
            emojis=data["emojis"],
            reblogs_count=data["reblogs_count"],
            favourites_count=data["favourites_count"],
            replies_count=data["replies_count"],
            url=data.get("url"),
            in_reply_to_id=data.get("in_reply_to_id"),
            in_reply_to_account_id=data.get("in_reply_to_account_id"),
            reblog=cls.from_dict(data["reblog"]) if data.get("reblog") else None,
            poll=data.get("poll"),
            card=data.get("card"),
            language=data.get("language"),
            text=data.get("text"),
            favourited=data.get("favourited", False),
            reblogged=data.get("reblogged", False),
            muted=data.get("muted", False),
            bookmarked=data.get("bookmarked", False),
            pinned=data.get("pinned", False),
        )


@dataclass
class Notification:
    """Represents a Mastodon notification."""

    id: str
    type: str
    created_at: datetime
    account: Account
    status: Optional[Status]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        """Create Notification from API response data."""
        return cls(
            id=data["id"],
            type=data["type"],
            created_at=datetime.fromisoformat(
                data["created_at"].replace("Z", "+00:00")
            ),
            account=Account.from_dict(data["account"]),
            status=Status.from_dict(data["status"]) if data.get("status") else None,
        )
