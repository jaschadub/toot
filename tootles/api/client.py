"""Mastodon API client implementation."""

import json
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx

from .models import Account, Notification, Status


class MastodonAPIError(Exception):
    """Base exception for Mastodon API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class MastodonClient:
    """Async Mastodon API client."""

    def __init__(self, instance_url: str, access_token: Optional[str] = None):
        """Initialize the Mastodon client.

        Args:
            instance_url: Base URL of the Mastodon instance
            access_token: OAuth access token for authenticated requests
        """
        self.instance_url = instance_url.rstrip("/")
        self.access_token = access_token
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _ensure_client(self):
        """Ensure HTTP client is initialized."""
        if not self._client:
            headers = {"User-Agent": "Tootles/1.0.0"}
            if self.access_token:
                headers["Authorization"] = f"Bearer {self.access_token}"

            self._client = httpx.AsyncClient(
                headers=headers,
                timeout=30.0,
                follow_redirects=True
            )

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an authenticated request to the Mastodon API.

        Args:
            method: HTTP method
            endpoint: API endpoint (without leading slash)
            params: Query parameters
            json_data: JSON request body

        Returns:
            Parsed JSON response

        Raises:
            MastodonAPIError: If the request fails
        """
        await self._ensure_client()

        url = urljoin(f"{self.instance_url}/api/v1/", endpoint)

        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=json_data
            )

            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", f"HTTP {response.status_code}")
                except (json.JSONDecodeError, KeyError):
                    error_msg = f"HTTP {response.status_code}: {response.text}"

                raise MastodonAPIError(error_msg, response.status_code)

            return response.json()

        except httpx.RequestError as e:
            raise MastodonAPIError(f"Request failed: {e}") from e

    async def verify_credentials(self) -> Account:
        """Verify account credentials and return account info.

        Returns:
            Account information for the authenticated user
        """
        data = await self._request("GET", "accounts/verify_credentials")
        return Account.from_dict(data)

    async def get_home_timeline(
        self,
        max_id: Optional[str] = None,
        since_id: Optional[str] = None,
        min_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Status]:
        """Get the home timeline.

        Args:
            max_id: Return results older than this ID
            since_id: Return results newer than this ID
            min_id: Return results immediately newer than this ID
            limit: Maximum number of results (1-40, default 20)

        Returns:
            List of Status objects
        """
        params = {"limit": min(max(limit, 1), 40)}

        if max_id:
            params["max_id"] = max_id
        if since_id:
            params["since_id"] = since_id
        if min_id:
            params["min_id"] = min_id

        data = await self._request("GET", "timelines/home", params=params)
        return [Status.from_dict(status) for status in data]

    async def get_public_timeline(
        self,
        local: bool = False,
        remote: bool = False,
        only_media: bool = False,
        max_id: Optional[str] = None,
        since_id: Optional[str] = None,
        min_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Status]:
        """Get the public timeline.

        Args:
            local: Show only local statuses
            remote: Show only remote statuses
            only_media: Show only statuses with media attachments
            max_id: Return results older than this ID
            since_id: Return results newer than this ID
            min_id: Return results immediately newer than this ID
            limit: Maximum number of results (1-40, default 20)

        Returns:
            List of Status objects
        """
        params = {"limit": min(max(limit, 1), 40)}

        if local:
            params["local"] = "true"
        if remote:
            params["remote"] = "true"
        if only_media:
            params["only_media"] = "true"
        if max_id:
            params["max_id"] = max_id
        if since_id:
            params["since_id"] = since_id
        if min_id:
            params["min_id"] = min_id

        data = await self._request("GET", "timelines/public", params=params)
        return [Status.from_dict(status) for status in data]

    async def get_notifications(
        self,
        max_id: Optional[str] = None,
        since_id: Optional[str] = None,
        min_id: Optional[str] = None,
        limit: int = 15,
        exclude_types: Optional[List[str]] = None
    ) -> List[Notification]:
        """Get notifications.

        Args:
            max_id: Return results older than this ID
            since_id: Return results newer than this ID
            min_id: Return results immediately newer than this ID
            limit: Maximum number of results (1-30, default 15)
            exclude_types: Array of notification types to exclude

        Returns:
            List of Notification objects
        """
        params = {"limit": min(max(limit, 1), 30)}

        if max_id:
            params["max_id"] = max_id
        if since_id:
            params["since_id"] = since_id
        if min_id:
            params["min_id"] = min_id
        if exclude_types:
            for exclude_type in exclude_types:
                params["exclude_types[]"] = exclude_type

        data = await self._request("GET", "notifications", params=params)
        return [Notification.from_dict(notification) for notification in data]

    async def post_status(
        self,
        status: str,
        in_reply_to_id: Optional[str] = None,
        media_ids: Optional[List[str]] = None,
        sensitive: bool = False,
        spoiler_text: Optional[str] = None,
        visibility: str = "public",
        language: Optional[str] = None
    ) -> Status:
        """Post a new status.

        Args:
            status: Text content of the status
            in_reply_to_id: ID of the status being replied to
            media_ids: Array of media attachment IDs
            sensitive: Mark status as sensitive
            spoiler_text: Text to be shown as warning before the actual content
            visibility: Visibility of the post (public, unlisted, private, direct)
            language: ISO 639 language code for the status

        Returns:
            The created Status object
        """
        json_data = {
            "status": status,
            "visibility": visibility,
            "sensitive": sensitive
        }

        if in_reply_to_id:
            json_data["in_reply_to_id"] = in_reply_to_id
        if media_ids:
            json_data["media_ids"] = media_ids
        if spoiler_text:
            json_data["spoiler_text"] = spoiler_text
        if language:
            json_data["language"] = language

        data = await self._request("POST", "statuses", json_data=json_data)
        return Status.from_dict(data)

    async def favourite_status(self, status_id: str) -> Status:
        """Favourite a status.

        Args:
            status_id: ID of the status to favourite

        Returns:
            The favourited Status object
        """
        data = await self._request("POST", f"statuses/{status_id}/favourite")
        return Status.from_dict(data)

    async def unfavourite_status(self, status_id: str) -> Status:
        """Unfavourite a status.

        Args:
            status_id: ID of the status to unfavourite

        Returns:
            The unfavourited Status object
        """
        data = await self._request("POST", f"statuses/{status_id}/unfavourite")
        return Status.from_dict(data)

    async def reblog_status(self, status_id: str) -> Status:
        """Reblog a status.

        Args:
            status_id: ID of the status to reblog

        Returns:
            The reblogged Status object
        """
        data = await self._request("POST", f"statuses/{status_id}/reblog")
        return Status.from_dict(data)

    async def unreblog_status(self, status_id: str) -> Status:
        """Unreblog a status.

        Args:
            status_id: ID of the status to unreblog

        Returns:
            The unreblogged Status object
        """
        data = await self._request("POST", f"statuses/{status_id}/unreblog")
        return Status.from_dict(data)
