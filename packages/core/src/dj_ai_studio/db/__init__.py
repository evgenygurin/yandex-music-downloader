"""Database module for DJ AI Studio.

This module provides SQLAlchemy ORM models and async database utilities:
- TrackORM: Music track with DJ-relevant metadata
- SetORM: DJ set with ordered tracks
- SetTrackORM: Track within a set with transition info
- PlaylistORM: Synchronized playlist from external services

Usage:
    from dj_ai_studio.db import init_db, get_db_url, get_session, TrackORM

    # Initialize database
    await init_db(get_db_url("./dj_studio.db"))

    # Use session
    async for session in get_session():
        track = TrackORM(title="Test", ...)
        session.add(track)
"""

from __future__ import annotations

from dj_ai_studio.db.base import (
    Base,
    close_db,
    get_db_url,
    get_session,
    get_session_context,
    init_db,
)
from dj_ai_studio.db.models import (
    PlaylistORM,
    SetORM,
    SetTrackORM,
    TrackORM,
)

__all__ = [
    # Base and utilities
    "Base",
    "close_db",
    "get_db_url",
    "get_session",
    "get_session_context",
    "init_db",
    # ORM models
    "PlaylistORM",
    "SetORM",
    "SetTrackORM",
    "TrackORM",
]
