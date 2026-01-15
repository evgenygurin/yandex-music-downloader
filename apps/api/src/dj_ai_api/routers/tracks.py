"""Track CRUD endpoints."""

from uuid import UUID

from dj_ai_studio.db import TrackORM
from dj_ai_studio.models import Track
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ..deps import DbSession

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.get("", response_model=list[Track])
async def list_tracks(
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    bpm_min: float | None = None,
    bpm_max: float | None = None,
    key: str | None = None,
    energy_min: int | None = Query(None, ge=1, le=10),
    energy_max: int | None = Query(None, ge=1, le=10),
    source: str | None = None,
) -> list[Track]:
    """List tracks with optional filters."""
    query = select(TrackORM)

    if bpm_min is not None:
        query = query.where(TrackORM.bpm >= bpm_min)
    if bpm_max is not None:
        query = query.where(TrackORM.bpm <= bpm_max)
    if key is not None:
        query = query.where(TrackORM.key == key)
    if energy_min is not None:
        query = query.where(TrackORM.energy >= energy_min)
    if energy_max is not None:
        query = query.where(TrackORM.energy <= energy_max)
    if source is not None:
        query = query.where(TrackORM.source == source)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    tracks = result.scalars().all()

    return [Track.model_validate(t, from_attributes=True) for t in tracks]


@router.get("/{track_id}", response_model=Track)
async def get_track(db: DbSession, track_id: UUID) -> Track:
    """Get a single track by ID."""
    result = await db.execute(select(TrackORM).where(TrackORM.id == str(track_id)))
    track = result.scalar_one_or_none()

    if track is None:
        raise HTTPException(status_code=404, detail="Track not found")

    return Track.model_validate(track, from_attributes=True)


@router.post("", response_model=Track, status_code=201)
async def create_track(db: DbSession, track: Track) -> Track:
    """Create a new track."""
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
        analyzed_at=track.analyzed_at,
    )

    try:
        db.add(db_track)
        await db.commit()
        await db.refresh(db_track)
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Track already exists") from e

    return Track.model_validate(db_track, from_attributes=True)


@router.patch("/{track_id}", response_model=Track)
async def update_track(
    db: DbSession,
    track_id: UUID,
    track_update: dict,
) -> Track:
    """Update a track (partial update)."""
    result = await db.execute(select(TrackORM).where(TrackORM.id == str(track_id)))
    db_track = result.scalar_one_or_none()

    if db_track is None:
        raise HTTPException(status_code=404, detail="Track not found")

    # Update only provided fields
    for field, value in track_update.items():
        if hasattr(db_track, field):
            setattr(db_track, field, value)

    await db.commit()
    await db.refresh(db_track)

    return Track.model_validate(db_track, from_attributes=True)


@router.delete("/{track_id}", status_code=204)
async def delete_track(db: DbSession, track_id: UUID) -> None:
    """Delete a track."""
    result = await db.execute(select(TrackORM).where(TrackORM.id == str(track_id)))
    db_track = result.scalar_one_or_none()

    if db_track is None:
        raise HTTPException(status_code=404, detail="Track not found")

    await db.delete(db_track)
    await db.commit()
