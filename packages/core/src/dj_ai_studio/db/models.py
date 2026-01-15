"""SQLAlchemy ORM models for DJ AI Studio.

These models mirror the Pydantic models in dj_ai_studio.models
but are optimized for database persistence with proper indexes
and relationships.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Boolean,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dj_ai_studio.db.base import Base

if TYPE_CHECKING:
    pass


class TrackORM(Base):
    """ORM model for music tracks.

    Stores all DJ-relevant metadata including BPM, key, energy,
    and analysis results.
    """

    __tablename__ = "tracks"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    # Basic info
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    artists: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    album: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    # Core DJ attributes
    bpm: Mapped[float] = mapped_column(Float, nullable=False)
    key: Mapped[str] = mapped_column(String(3), nullable=False)
    camelot: Mapped[str] = mapped_column(String(3), nullable=False)
    energy: Mapped[int] = mapped_column(Integer, nullable=False)

    # Extended analysis
    mood: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    genre: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    vocals: Mapped[str] = mapped_column(
        String(10), nullable=False, default="none"
    )
    structure: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # User data
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Source tracking
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    source_id: Mapped[str] = mapped_column(String(200), nullable=False)
    cover_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_tracks_source_source_id", "source", "source_id", unique=True),
        Index("ix_tracks_created_at", "created_at"),
        Index("ix_tracks_bpm", "bpm"),
        Index("ix_tracks_key", "key"),
        Index("ix_tracks_camelot", "camelot"),
        Index("ix_tracks_energy", "energy"),
    )

    def __repr__(self) -> str:
        return f"<TrackORM(id={self.id!r}, title={self.title!r}, artists={self.artists!r})>"


class SetORM(Base):
    """ORM model for DJ sets.

    A set contains an ordered list of tracks with transition information.
    """

    __tablename__ = "sets"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_duration_min: Mapped[int] = mapped_column(
        Integer, nullable=False, default=60
    )

    # Set parameters
    style: Mapped[str | None] = mapped_column(String(20), nullable=True)
    energy_curve: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    # Relationships
    tracks: Mapped[list["SetTrackORM"]] = relationship(
        "SetTrackORM",
        back_populates="set",
        cascade="all, delete-orphan",
        order_by="SetTrackORM.position",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_sets_created_at", "created_at"),
        Index("ix_sets_name", "name"),
    )

    def __repr__(self) -> str:
        return f"<SetORM(id={self.id!r}, name={self.name!r})>"


class SetTrackORM(Base):
    """ORM model for tracks within a DJ set.

    Stores the position and transition information for each track in a set.
    """

    __tablename__ = "set_tracks"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    # Foreign key to set
    set_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sets.id", ondelete="CASCADE"), nullable=False
    )

    # Track reference and position
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    track_id: Mapped[str] = mapped_column(String(36), nullable=False)

    # Transition info
    transition_type: Mapped[str] = mapped_column(
        String(10), nullable=False, default="mix"
    )
    mix_in_point_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mix_out_point_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    set: Mapped["SetORM"] = relationship("SetORM", back_populates="tracks")

    __table_args__ = (
        Index("ix_set_tracks_set_id_position", "set_id", "position", unique=True),
        Index("ix_set_tracks_track_id", "track_id"),
    )

    def __repr__(self) -> str:
        return f"<SetTrackORM(id={self.id!r}, set_id={self.set_id!r}, position={self.position})>"


class PlaylistORM(Base):
    """ORM model for synchronized playlists.

    Stores playlists imported from external music services.
    """

    __tablename__ = "playlists"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    # Basic info
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Source tracking
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    source_id: Mapped[str] = mapped_column(String(200), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Playlist content
    track_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    cover_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Metadata
    owner: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Timestamps
    synced_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )

    __table_args__ = (
        Index("ix_playlists_source_source_id", "source", "source_id", unique=True),
        Index("ix_playlists_created_at", "created_at"),
        Index("ix_playlists_name", "name"),
    )

    def __repr__(self) -> str:
        return f"<PlaylistORM(id={self.id!r}, name={self.name!r}, source={self.source!r})>"
