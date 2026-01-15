"""Playlist synchronization service for Yandex Music."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dj_ai_studio.db import PlaylistORM, TrackORM
from dj_ai_studio.models import Track
from dj_ai_studio.yandex.client import YandexClient
from dj_ai_studio.yandex.converter import yandex_track_to_track

if TYPE_CHECKING:
    from yandex_music import Playlist as YandexPlaylist


@dataclass
class SyncResult:
    """Result of playlist synchronization."""

    playlist_id: str
    tracks_added: int = 0
    tracks_updated: int = 0
    tracks_skipped: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class SyncStats:
    """Statistics for a full sync operation."""

    playlists_synced: int = 0
    total_tracks_added: int = 0
    total_tracks_updated: int = 0
    total_tracks_skipped: int = 0
    errors: list[str] = field(default_factory=list)


class YandexSyncService:
    """Service for synchronizing Yandex Music playlists to local database."""

    def __init__(self, client: YandexClient, session: AsyncSession) -> None:
        """Initialize sync service.

        Args:
            client: Initialized YandexClient
            session: Database session
        """
        self.client = client
        self.session = session

    async def sync_playlist(
        self,
        user_id: str,
        playlist_id: str | int,
    ) -> SyncResult:
        """Sync a single playlist from Yandex Music.

        Args:
            user_id: Playlist owner's user ID
            playlist_id: Playlist ID (kind)

        Returns:
            SyncResult with statistics
        """
        result = SyncResult(playlist_id=str(playlist_id))

        try:
            # Get playlist info
            playlist = await self.client.get_playlist(user_id, playlist_id)
            if playlist is None:
                result.errors.append(f"Playlist {playlist_id} not found")
                return result

            # Get or create playlist in DB
            db_playlist = await self._get_or_create_playlist(playlist)

            # Sync tracks
            track_ids: list[str] = []
            async for yandex_track in self.client.get_playlist_tracks(user_id, playlist_id):
                try:
                    track = await self._sync_track(yandex_track)
                    track_ids.append(str(track.id))

                    if track.analyzed_at is None:
                        result.tracks_added += 1
                    else:
                        result.tracks_skipped += 1

                except Exception as e:
                    result.errors.append(f"Track {yandex_track.id}: {e}")

            # Update playlist track IDs
            db_playlist.track_ids = track_ids
            db_playlist.synced_at = datetime.now()
            await self.session.commit()

        except Exception as e:
            result.errors.append(str(e))
            await self.session.rollback()

        return result

    async def sync_liked_tracks(self) -> SyncResult:
        """Sync user's liked tracks from Yandex Music.

        Returns:
            SyncResult with statistics
        """
        result = SyncResult(playlist_id="liked")

        try:
            async for yandex_track in self.client.get_liked_tracks():
                try:
                    track = await self._sync_track(yandex_track)

                    if track.analyzed_at is None:
                        result.tracks_added += 1
                    else:
                        result.tracks_skipped += 1

                except Exception as e:
                    result.errors.append(f"Track {yandex_track.id}: {e}")

            await self.session.commit()

        except Exception as e:
            result.errors.append(str(e))
            await self.session.rollback()

        return result

    async def sync_all_playlists(self, user_id: str | None = None) -> SyncStats:
        """Sync all playlists for a user.

        Args:
            user_id: User ID, or None for current user

        Returns:
            SyncStats with overall statistics
        """
        stats = SyncStats()

        try:
            playlists = await self.client.get_user_playlists(user_id)

            for playlist in playlists:
                if playlist.kind is None or playlist.owner is None:
                    continue

                owner_id = (
                    playlist.owner.login
                    if hasattr(playlist.owner, "login")
                    else str(playlist.owner.uid)
                )
                result = await self.sync_playlist(owner_id, playlist.kind)

                stats.playlists_synced += 1
                stats.total_tracks_added += result.tracks_added
                stats.total_tracks_updated += result.tracks_updated
                stats.total_tracks_skipped += result.tracks_skipped
                stats.errors.extend(result.errors)

        except Exception as e:
            stats.errors.append(str(e))

        return stats

    async def _sync_track(self, yandex_track) -> Track:
        """Sync a single track to database.

        Args:
            yandex_track: Yandex Music track object

        Returns:
            Track model (existing or newly created)
        """
        # Check if track already exists
        result = await self.session.execute(
            select(TrackORM).where(
                TrackORM.source == "yandex",
                TrackORM.source_id == str(yandex_track.id),
            )
        )
        db_track = result.scalar_one_or_none()

        if db_track is not None:
            # Return existing track
            return Track.model_validate(db_track, from_attributes=True)

        # Create new track
        track = yandex_track_to_track(yandex_track)

        db_track = TrackORM(
            id=str(track.id),
            title=track.title,
            artists=track.artists,
            album=track.album,
            duration_ms=track.duration_ms,
            bpm=track.bpm,
            key=track.key,
            camelot=track.camelot,
            energy=track.energy,
            mood=track.mood,
            genre=track.genre,
            vocals=track.vocals,
            structure=track.structure.model_dump() if track.structure else None,
            rating=track.rating,
            tags=track.tags,
            notes=track.notes,
            source=track.source,
            source_id=track.source_id,
            cover_url=track.cover_url,
            created_at=track.created_at,
            analyzed_at=None,  # Not analyzed yet
        )

        self.session.add(db_track)
        await self.session.flush()

        return track

    async def _get_or_create_playlist(
        self,
        yandex_playlist: "YandexPlaylist",
    ) -> PlaylistORM:
        """Get or create playlist in database.

        Args:
            yandex_playlist: Yandex Music playlist object

        Returns:
            PlaylistORM instance
        """
        source_id = str(yandex_playlist.kind)

        result = await self.session.execute(
            select(PlaylistORM).where(
                PlaylistORM.source == "yandex",
                PlaylistORM.source_id == source_id,
            )
        )
        db_playlist = result.scalar_one_or_none()

        if db_playlist is not None:
            # Update existing playlist name
            db_playlist.name = yandex_playlist.title or "Untitled"
            return db_playlist

        # Create new playlist
        db_playlist = PlaylistORM(
            name=yandex_playlist.title or "Untitled",
            source="yandex",
            source_id=source_id,
            track_ids=[],
            synced_at=datetime.now(),
        )
        self.session.add(db_playlist)
        await self.session.flush()

        return db_playlist
