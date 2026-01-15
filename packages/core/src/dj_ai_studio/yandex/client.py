"""Async wrapper for Yandex Music client."""

import asyncio
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from yandex_music import Client, Playlist, Track
from yandex_music.exceptions import NetworkError

from dj_ai_studio.yandex.api import (
    ApiTrackQuality,
    CustomDownloadInfo,
    download_track_data,
    get_download_info,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@dataclass
class YandexClientConfig:
    """Configuration for Yandex Music client."""

    token: str
    timeout: int = 20
    max_retries: int = 3
    retry_delay: int = 5


class YandexClient:
    """Async wrapper for Yandex Music API.

    Wraps the synchronous yandex-music library to provide
    an async interface compatible with FastAPI/asyncio.
    """

    def __init__(self, config: YandexClientConfig) -> None:
        """Initialize client with configuration.

        Args:
            config: Client configuration with token and network settings
        """
        self.config = config
        self._client: Client | None = None

    def _init_sync_client(self) -> Client:
        """Initialize the synchronous client with retry logic."""
        client = Client(self.config.token)
        client.request.set_timeout(self.config.timeout)

        original_wrapper = client.request._request_wrapper
        max_retries = self.config.max_retries
        retry_delay = self.config.retry_delay

        def retry_wrapper(*args, **kwargs):
            tries = 0
            while True:
                try:
                    return original_wrapper(*args, **kwargs)
                except NetworkError as error:
                    if max_retries == 0 or tries < max_retries:
                        tries += 1
                        time.sleep(retry_delay)
                        continue
                    raise error

        client.request._request_wrapper = retry_wrapper
        return client.init()

    async def _get_client(self) -> Client:
        """Get or create the sync client in thread pool."""
        if self._client is None:
            self._client = await asyncio.to_thread(self._init_sync_client)
        return self._client

    async def get_track(self, track_id: str | int) -> Track | None:
        """Get a single track by ID.

        Args:
            track_id: Yandex Music track ID

        Returns:
            Track object or None if not found
        """
        client = await self._get_client()
        tracks = await asyncio.to_thread(client.tracks, [track_id])
        return tracks[0] if tracks else None

    async def get_tracks(self, track_ids: list[str | int]) -> list[Track]:
        """Get multiple tracks by IDs.

        Args:
            track_ids: List of Yandex Music track IDs

        Returns:
            List of Track objects
        """
        client = await self._get_client()
        return await asyncio.to_thread(client.tracks, track_ids)

    async def get_playlist(self, user_id: str, playlist_id: str | int) -> Playlist | None:
        """Get a playlist by user and playlist ID.

        Args:
            user_id: Playlist owner's user ID
            playlist_id: Playlist ID (kind)

        Returns:
            Playlist object or None if not found
        """
        client = await self._get_client()
        return await asyncio.to_thread(client.users_playlists, playlist_id, user_id)

    async def get_user_playlists(self, user_id: str | None = None) -> list[Playlist]:
        """Get all playlists for a user.

        Args:
            user_id: User ID, or None for current user

        Returns:
            List of Playlist objects
        """
        client = await self._get_client()
        if user_id is None:
            return await asyncio.to_thread(client.users_playlists_list)
        return await asyncio.to_thread(client.users_playlists_list, user_id)

    async def get_playlist_tracks(
        self,
        user_id: str,
        playlist_id: str | int,
        page_size: int = 50,
    ) -> "AsyncGenerator[Track, None]":
        """Get all tracks from a playlist as async generator.

        Args:
            user_id: Playlist owner's user ID
            playlist_id: Playlist ID (kind)
            page_size: Number of tracks to fetch per request

        Yields:
            Track objects from the playlist
        """
        client = await self._get_client()
        playlist = await asyncio.to_thread(client.users_playlists, playlist_id, user_id)

        if playlist is None or playlist.tracks is None:
            return

        track_shorts = playlist.fetch_tracks()
        for i in range(0, len(track_shorts), page_size):
            batch_ids = [t.id for t in track_shorts[i : i + page_size]]
            tracks = await asyncio.to_thread(client.tracks, batch_ids)
            for track in tracks:
                yield track

    async def get_download_info(
        self,
        track: Track,
        quality: ApiTrackQuality = ApiTrackQuality.LOSSLESS,
    ) -> CustomDownloadInfo:
        """Get download info for a track.

        Args:
            track: Yandex Music track object
            quality: Desired quality level

        Returns:
            Download info with URLs and decryption key
        """
        return await asyncio.to_thread(get_download_info, track, quality)

    async def download_track(
        self,
        track: Track,
        quality: ApiTrackQuality = ApiTrackQuality.LOSSLESS,
    ) -> bytes:
        """Download track audio data.

        Args:
            track: Yandex Music track object
            quality: Desired quality level

        Returns:
            Raw audio data (decrypted)
        """
        client = await self._get_client()
        download_info = await self.get_download_info(track, quality)
        return await asyncio.to_thread(download_track_data, client, download_info)

    async def download_cover(
        self,
        track: Track,
        size: int = 400,
    ) -> bytes | None:
        """Download track cover image.

        Args:
            track: Yandex Music track object
            size: Cover size in pixels (or -1 for original)

        Returns:
            Cover image data or None if no cover
        """
        if track.cover_uri is None:
            return None

        size_str = "orig" if size == -1 else f"{size}x{size}"
        return await asyncio.to_thread(track.download_cover_bytes, size=size_str)

    async def get_liked_tracks(self, page_size: int = 50) -> "AsyncGenerator[Track, None]":
        """Get user's liked tracks as async generator.

        Args:
            page_size: Number of tracks to fetch per request

        Yields:
            Track objects from liked tracks
        """
        client = await self._get_client()
        likes = await asyncio.to_thread(client.users_likes_tracks)

        if likes is None or likes.tracks is None:
            return

        for i in range(0, len(likes.tracks), page_size):
            batch = likes.tracks[i : i + page_size]
            batch_ids = [t.id for t in batch]
            tracks = await asyncio.to_thread(client.tracks, batch_ids)
            for track in tracks:
                yield track

    async def close(self) -> None:
        """Close the client connection."""
        self._client = None
