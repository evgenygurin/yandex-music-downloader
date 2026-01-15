"""Test fixtures for MCP server tests."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from dj_ai_studio.db.models import Base, SetORM, SetTrackORM, TrackORM


@pytest.fixture
def sample_tracks_data():
    """Sample track data for testing."""
    return [
        {
            "id": "track-1",
            "title": "Deep House Groove",
            "artists": "DJ Producer",
            "album": "Summer Vibes",
            "bpm": 124.0,
            "key": "Am",
            "camelot": "8A",
            "energy": 7,
            "duration_ms": 360000,
            "source": "yandex",
            "source_id": "12345",
        },
        {
            "id": "track-2",
            "title": "Tech House Banger",
            "artists": "Another Artist",
            "album": "Club Hits",
            "bpm": 126.0,
            "key": "Gm",
            "camelot": "6A",
            "energy": 8,
            "duration_ms": 420000,
            "source": "yandex",
            "source_id": "12346",
        },
        {
            "id": "track-3",
            "title": "Chill Out Track",
            "artists": "DJ Producer",
            "album": "Sunset Sessions",
            "bpm": 118.0,
            "key": "C",
            "camelot": "8B",
            "energy": 4,
            "duration_ms": 300000,
            "source": "yandex",
            "source_id": "12347",
        },
        {
            "id": "track-4",
            "title": "Progressive Journey",
            "artists": "Progressive DJ",
            "album": "Melodic Techno",
            "bpm": 122.0,
            "key": "Bm",
            "camelot": "10A",
            "energy": 6,
            "duration_ms": 480000,
            "source": "local",
            "source_id": "local-1",
        },
        {
            "id": "track-5",
            "title": "Harmonic Mix Ready",
            "artists": "Mix Master",
            "album": "DJ Tools",
            "bpm": 125.0,
            "key": "Em",
            "camelot": "9A",
            "energy": 7,
            "duration_ms": 390000,
            "source": "yandex",
            "source_id": "12348",
        },
    ]


@pytest_asyncio.fixture
async def async_engine():
    """Create async SQLite engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    """Create async session for testing."""
    async_session_maker = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def db_with_tracks(async_session, sample_tracks_data):
    """Database session with sample tracks."""
    for data in sample_tracks_data:
        track = TrackORM(**data)
        async_session.add(track)
    await async_session.commit()
    return async_session


@pytest_asyncio.fixture
async def db_with_set(db_with_tracks):
    """Database session with sample set and tracks."""
    session = db_with_tracks

    # Create a set
    dj_set = SetORM(
        id="set-1",
        name="Friday Night Mix",
        description="Opening set for club night",
    )
    session.add(dj_set)

    # Add first two tracks to the set
    set_track1 = SetTrackORM(
        set_id="set-1",
        track_id="track-1",
        position=1,
    )
    set_track2 = SetTrackORM(
        set_id="set-1",
        track_id="track-2",
        position=2,
    )
    session.add(set_track1)
    session.add(set_track2)

    await session.commit()
    return session
