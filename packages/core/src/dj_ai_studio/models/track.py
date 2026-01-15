"""Track data model for DJ AI Studio.

Represents a music track with all DJ-relevant metadata including
BPM, key, energy level, and analysis results.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class TrackStructure(BaseModel):
    """Structure markers for a track in milliseconds."""

    intro_ms: int | None = Field(default=None, ge=0, description="Intro end position")
    outro_ms: int | None = Field(default=None, ge=0, description="Outro start position")
    drop_ms: int | None = Field(default=None, ge=0, description="Main drop position")
    breakdown_ms: int | None = Field(
        default=None, ge=0, description="Breakdown start position"
    )


class Track(BaseModel):
    """A music track with DJ-relevant metadata and analysis.

    Attributes:
        id: Unique identifier for the track.
        title: Track title.
        artists: List of artist names.
        album: Album name if available.
        duration_ms: Track duration in milliseconds.
        bpm: Beats per minute.
        key: Musical key (e.g., "Am", "C", "F#m").
        camelot: Camelot wheel notation (e.g., "8A", "5B").
        energy: Energy level from 1 (low) to 10 (high).
        mood: List of mood descriptors.
        genre: List of genre tags.
        vocals: Amount of vocals in the track.
        structure: Track structure markers.
        rating: User rating from 1 to 5 stars.
        tags: Custom user tags.
        notes: User notes about the track.
        source: Source platform for the track.
        source_id: ID on the source platform.
        cover_url: URL to album/track cover art.
        created_at: When the track was added to the library.
        analyzed_at: When the track was last analyzed.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique track identifier")
    title: str = Field(..., min_length=1, description="Track title")
    artists: list[str] = Field(
        default_factory=list, min_length=1, description="List of artist names"
    )
    album: str | None = Field(default=None, description="Album name")
    duration_ms: int = Field(..., gt=0, description="Duration in milliseconds")

    # Core DJ attributes
    bpm: float = Field(..., gt=0, le=300, description="Beats per minute")
    key: str = Field(..., min_length=1, max_length=3, description="Musical key")
    camelot: str = Field(
        ..., pattern=r"^(1[0-2]|[1-9])[AB]$", description="Camelot wheel notation"
    )
    energy: int = Field(..., ge=1, le=10, description="Energy level 1-10")

    # Extended analysis
    mood: list[str] = Field(default_factory=list, description="Mood descriptors")
    genre: list[str] = Field(default_factory=list, description="Genre tags")
    vocals: Literal["none", "some", "heavy"] = Field(
        default="none", description="Amount of vocals"
    )
    structure: TrackStructure = Field(
        default_factory=TrackStructure, description="Track structure markers"
    )

    # User data
    rating: int | None = Field(default=None, ge=1, le=5, description="User rating 1-5")
    tags: list[str] = Field(default_factory=list, description="Custom user tags")
    notes: str | None = Field(default=None, description="User notes")

    # Source tracking
    source: Literal["yandex", "spotify", "local", "soundcloud", "beatport"] = Field(
        ..., description="Source platform"
    )
    source_id: str = Field(..., min_length=1, description="ID on source platform")
    cover_url: str | None = Field(default=None, description="Cover art URL")

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.now, description="When track was added"
    )
    analyzed_at: datetime | None = Field(
        default=None, description="When track was last analyzed"
    )

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        """Validate musical key format."""
        # Valid keys: C, C#, Db, D, D#, Eb, E, F, F#, Gb, G, G#, Ab, A, A#, Bb, B
        # With optional 'm' for minor
        valid_notes = {
            "C",
            "C#",
            "Db",
            "D",
            "D#",
            "Eb",
            "E",
            "F",
            "F#",
            "Gb",
            "G",
            "G#",
            "Ab",
            "A",
            "A#",
            "Bb",
            "B",
        }
        # Check if key ends with 'm' for minor
        if v.endswith("m"):
            note = v[:-1]
        else:
            note = v

        if note not in valid_notes:
            msg = f"Invalid musical key: {v}. Must be a valid note (C, C#, D, etc.) optionally followed by 'm' for minor"
            raise ValueError(msg)
        return v

    @field_validator("artists")
    @classmethod
    def validate_artists_not_empty(cls, v: list[str]) -> list[str]:
        """Ensure artists list is not empty."""
        if not v:
            msg = "At least one artist is required"
            raise ValueError(msg)
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Strobe",
                    "artists": ["deadmau5"],
                    "album": "For Lack of a Better Name",
                    "duration_ms": 637000,
                    "bpm": 128.0,
                    "key": "Am",
                    "camelot": "8A",
                    "energy": 7,
                    "mood": ["euphoric", "progressive"],
                    "genre": ["progressive house"],
                    "vocals": "none",
                    "source": "spotify",
                    "source_id": "0VjIjW4GlUZAMYd2vXMi3b",
                }
            ]
        }
    }
