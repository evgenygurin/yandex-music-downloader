"""Convert Yandex Music objects to DJ AI Studio models."""

from datetime import datetime
from typing import TYPE_CHECKING

from dj_ai_studio.models import Track

if TYPE_CHECKING:
    from yandex_music import Track as YandexTrack


# Default values for DJ attributes when not yet analyzed
DEFAULT_BPM = 120.0  # Placeholder BPM
DEFAULT_KEY = "C"  # Placeholder key (C major)
DEFAULT_CAMELOT = "8B"  # Camelot for C major
DEFAULT_ENERGY = 5  # Middle energy level


def yandex_track_to_track(
    yandex_track: "YandexTrack",
    *,
    bpm: float | None = None,
    key: str | None = None,
    camelot: str | None = None,
    energy: int | None = None,
    cover_size: int = 400,
) -> Track:
    """Convert Yandex Music track to DJ AI Studio Track.

    Creates a Track with available metadata from Yandex Music.
    DJ-specific attributes (bpm, key, camelot, energy) use provided
    values or placeholders if not analyzed yet.

    Args:
        yandex_track: Yandex Music track object
        bpm: Analyzed BPM or None for placeholder
        key: Analyzed musical key or None for placeholder
        camelot: Analyzed Camelot notation or None for placeholder
        energy: Analyzed energy level or None for placeholder
        cover_size: Cover image size for URL generation

    Returns:
        Track model instance
    """
    # Extract artists
    artists: list[str] = []
    if yandex_track.artists:
        artists = [a.name for a in yandex_track.artists if a.name]
    if not artists:
        artists = ["Unknown Artist"]

    # Extract album info
    album_title: str | None = None
    album_genre: list[str] = []
    if yandex_track.albums:
        album = yandex_track.albums[0]
        album_title = _full_title(album)
        if album.genre:
            album_genre = [album.genre]

    # Build cover URL
    cover_url: str | None = None
    if yandex_track.cover_uri:
        cover_url = f"https://{yandex_track.cover_uri.replace('%%', f'{cover_size}x{cover_size}')}"

    # Track duration in milliseconds
    duration_ms = (yandex_track.duration_ms or 0) if hasattr(yandex_track, "duration_ms") else 0
    if duration_ms == 0 and yandex_track.duration_ms:
        duration_ms = yandex_track.duration_ms

    return Track(
        title=_full_title(yandex_track),
        artists=artists,
        album=album_title,
        duration_ms=duration_ms,
        bpm=bpm if bpm is not None else DEFAULT_BPM,
        key=key if key is not None else DEFAULT_KEY,
        camelot=camelot if camelot is not None else DEFAULT_CAMELOT,
        energy=energy if energy is not None else DEFAULT_ENERGY,
        genre=album_genre,
        source="yandex",
        source_id=str(yandex_track.id),
        cover_url=cover_url,
        created_at=datetime.now(),
    )


def _full_title(obj) -> str:
    """Get full title including version suffix.

    Args:
        obj: Yandex Music object with title and version attributes

    Returns:
        Full title string
    """
    title = obj.title or ""
    if hasattr(obj, "version") and obj.version:
        title = f"{title} ({obj.version})"
    return title


def key_to_camelot(key: str) -> str:
    """Convert musical key to Camelot wheel notation.

    Args:
        key: Musical key (e.g., "Am", "C", "F#m")

    Returns:
        Camelot notation (e.g., "8A", "8B", "2A")
    """
    # Camelot wheel mapping
    # Major keys (B suffix)
    major_map = {
        "C": "8B",
        "G": "9B",
        "D": "10B",
        "A": "11B",
        "E": "12B",
        "B": "1B",
        "F#": "2B",
        "Gb": "2B",
        "Db": "3B",
        "C#": "3B",
        "Ab": "4B",
        "G#": "4B",
        "Eb": "5B",
        "D#": "5B",
        "Bb": "6B",
        "A#": "6B",
        "F": "7B",
    }

    # Minor keys (A suffix)
    minor_map = {
        "Am": "8A",
        "Em": "9A",
        "Bm": "10A",
        "F#m": "11A",
        "Gbm": "11A",
        "C#m": "12A",
        "Dbm": "12A",
        "G#m": "1A",
        "Abm": "1A",
        "D#m": "2A",
        "Ebm": "2A",
        "A#m": "3A",
        "Bbm": "3A",
        "Fm": "4A",
        "Cm": "5A",
        "Gm": "6A",
        "Dm": "7A",
    }

    if key in minor_map:
        return minor_map[key]
    if key in major_map:
        return major_map[key]

    # Fallback
    return "8B"


def camelot_to_key(camelot: str) -> str:
    """Convert Camelot notation to musical key.

    Args:
        camelot: Camelot notation (e.g., "8A", "8B")

    Returns:
        Musical key (e.g., "Am", "C")
    """
    camelot_map = {
        "1A": "G#m",
        "2A": "D#m",
        "3A": "A#m",
        "4A": "Fm",
        "5A": "Cm",
        "6A": "Gm",
        "7A": "Dm",
        "8A": "Am",
        "9A": "Em",
        "10A": "Bm",
        "11A": "F#m",
        "12A": "C#m",
        "1B": "B",
        "2B": "F#",
        "3B": "Db",
        "4B": "Ab",
        "5B": "Eb",
        "6B": "Bb",
        "7B": "F",
        "8B": "C",
        "9B": "G",
        "10B": "D",
        "11B": "A",
        "12B": "E",
    }
    return camelot_map.get(camelot, "C")
