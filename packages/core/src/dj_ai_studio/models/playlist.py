"""Playlist data model for DJ AI Studio.

Represents a synchronized playlist from external music services
like Yandex Music or Spotify.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Playlist(BaseModel):
    """A synchronized playlist from an external music service.

    Playlists are imported from streaming services and contain
    references to Track objects in the local library.

    Attributes:
        id: Unique identifier for the playlist.
        name: Playlist name.
        description: Optional playlist description.
        source: Source platform (yandex, spotify, etc.).
        source_id: ID on the source platform.
        source_url: URL to the playlist on the source platform.
        track_ids: List of Track UUIDs in playlist order.
        cover_url: Playlist cover image URL.
        owner: Playlist owner/creator name.
        is_public: Whether the playlist is public on the source.
        synced_at: When the playlist was last synced.
        created_at: When the playlist was first imported.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique playlist identifier")
    name: str = Field(..., min_length=1, max_length=300, description="Playlist name")
    description: str | None = Field(default=None, description="Playlist description")
    source: Literal["yandex", "spotify", "soundcloud", "beatport", "local"] = Field(
        ..., description="Source platform"
    )
    source_id: str = Field(..., min_length=1, description="ID on source platform")
    source_url: str | None = Field(
        default=None, description="URL to playlist on source"
    )
    track_ids: list[UUID] = Field(
        default_factory=list, description="Ordered list of Track UUIDs"
    )
    cover_url: str | None = Field(default=None, description="Cover image URL")
    owner: str | None = Field(default=None, description="Playlist owner name")
    is_public: bool = Field(default=True, description="Whether playlist is public")
    synced_at: datetime = Field(
        default_factory=datetime.now, description="Last sync timestamp"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="First import timestamp"
    )

    @property
    def track_count(self) -> int:
        """Get the number of tracks in the playlist."""
        return len(self.track_ids)

    def add_track(self, track_id: UUID, position: int | None = None) -> None:
        """Add a track to the playlist.

        Args:
            track_id: UUID of the track to add.
            position: Optional position (0-indexed). If None, adds to end.
        """
        if position is None:
            self.track_ids.append(track_id)
        else:
            self.track_ids.insert(position, track_id)

    def remove_track(self, track_id: UUID) -> bool:
        """Remove a track from the playlist.

        Args:
            track_id: UUID of the track to remove.

        Returns:
            True if track was found and removed, False otherwise.
        """
        try:
            self.track_ids.remove(track_id)
            return True
        except ValueError:
            return False

    def reorder_track(self, from_index: int, to_index: int) -> bool:
        """Move a track from one position to another.

        Args:
            from_index: Current position (0-indexed).
            to_index: Target position (0-indexed).

        Returns:
            True if reorder was successful, False otherwise.
        """
        if not 0 <= from_index < len(self.track_ids):
            return False
        if not 0 <= to_index < len(self.track_ids):
            return False

        track_id = self.track_ids.pop(from_index)
        self.track_ids.insert(to_index, track_id)
        return True

    def contains(self, track_id: UUID) -> bool:
        """Check if a track is in the playlist.

        Args:
            track_id: UUID of the track to check.

        Returns:
            True if track is in playlist, False otherwise.
        """
        return track_id in self.track_ids

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "My Techno Collection",
                    "description": "Dark and driving techno tracks",
                    "source": "spotify",
                    "source_id": "37i9dQZF1DX6J5NfMJS675",
                    "source_url": "https://open.spotify.com/playlist/37i9dQZF1DX6J5NfMJS675",
                    "track_ids": [],
                    "owner": "Spotify",
                    "is_public": True,
                }
            ]
        }
    }
