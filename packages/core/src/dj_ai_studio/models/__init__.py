"""Data models for DJ AI Studio.

This module exports all core data models used throughout the application:
- Track: Music track with DJ-relevant metadata
- Set: Planned DJ set with ordered tracks and transitions
- SetTrack: A track within a set with transition information
- Playlist: Synchronized playlist from external services
- TrackStructure: Track structure markers (intro, outro, drop)
"""

from __future__ import annotations

from dj_ai_studio.models.playlist import Playlist
from dj_ai_studio.models.set import Set, SetTrack
from dj_ai_studio.models.track import Track, TrackStructure

__all__ = [
    "Playlist",
    "Set",
    "SetTrack",
    "Track",
    "TrackStructure",
]
