"""Set CRUD endpoints."""

from uuid import UUID

from dj_ai_studio.db import SetORM, SetTrackORM
from dj_ai_studio.models import Set, SetTrack
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..deps import DbSession

router = APIRouter(prefix="/sets", tags=["sets"])


@router.get("", response_model=list[Set])
async def list_sets(
    db: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> list[Set]:
    """List all sets."""
    query = select(SetORM).options(selectinload(SetORM.tracks)).offset(skip).limit(limit)
    result = await db.execute(query)
    sets = result.scalars().all()

    return [Set.model_validate(s, from_attributes=True) for s in sets]


@router.get("/{set_id}", response_model=Set)
async def get_set(db: DbSession, set_id: UUID) -> Set:
    """Get a single set by ID."""
    query = select(SetORM).options(selectinload(SetORM.tracks)).where(SetORM.id == set_id)
    result = await db.execute(query)
    dj_set = result.scalar_one_or_none()

    if dj_set is None:
        raise HTTPException(status_code=404, detail="Set not found")

    return Set.model_validate(dj_set, from_attributes=True)


@router.post("", response_model=Set, status_code=201)
async def create_set(db: DbSession, dj_set: Set) -> Set:
    """Create a new set."""
    db_set = SetORM(
        id=dj_set.id,
        name=dj_set.name,
        description=dj_set.description,
        target_duration_min=dj_set.target_duration_min,
        style=dj_set.style,
        energy_curve=dj_set.energy_curve,
        created_at=dj_set.created_at,
        updated_at=dj_set.updated_at,
    )

    db.add(db_set)
    await db.commit()
    await db.refresh(db_set)

    return Set.model_validate(db_set, from_attributes=True)


@router.patch("/{set_id}", response_model=Set)
async def update_set(
    db: DbSession,
    set_id: UUID,
    set_update: dict,
) -> Set:
    """Update a set (partial update)."""
    query = select(SetORM).options(selectinload(SetORM.tracks)).where(SetORM.id == set_id)
    result = await db.execute(query)
    db_set = result.scalar_one_or_none()

    if db_set is None:
        raise HTTPException(status_code=404, detail="Set not found")

    for field, value in set_update.items():
        if hasattr(db_set, field) and field != "tracks":
            setattr(db_set, field, value)

    await db.commit()
    await db.refresh(db_set)

    return Set.model_validate(db_set, from_attributes=True)


@router.delete("/{set_id}", status_code=204)
async def delete_set(db: DbSession, set_id: UUID) -> None:
    """Delete a set."""
    result = await db.execute(select(SetORM).where(SetORM.id == set_id))
    db_set = result.scalar_one_or_none()

    if db_set is None:
        raise HTTPException(status_code=404, detail="Set not found")

    await db.delete(db_set)
    await db.commit()


# Track management within sets


@router.post("/{set_id}/tracks", response_model=Set, status_code=201)
async def add_track_to_set(
    db: DbSession,
    set_id: UUID,
    track: SetTrack,
) -> Set:
    """Add a track to a set."""
    query = select(SetORM).options(selectinload(SetORM.tracks)).where(SetORM.id == set_id)
    result = await db.execute(query)
    db_set = result.scalar_one_or_none()

    if db_set is None:
        raise HTTPException(status_code=404, detail="Set not found")

    db_track = SetTrackORM(
        set_id=set_id,
        position=track.position,
        track_id=track.track_id,
        transition_type=track.transition_type,
        mix_in_point_ms=track.mix_in_point_ms,
        mix_out_point_ms=track.mix_out_point_ms,
        notes=track.notes,
    )

    db.add(db_track)
    await db.commit()

    # Refresh to get updated tracks list
    await db.refresh(db_set)

    return Set.model_validate(db_set, from_attributes=True)


@router.delete("/{set_id}/tracks/{position}", status_code=204)
async def remove_track_from_set(
    db: DbSession,
    set_id: UUID,
    position: int,
) -> None:
    """Remove a track from a set by position."""
    query = select(SetTrackORM).where(
        SetTrackORM.set_id == set_id,
        SetTrackORM.position == position,
    )
    result = await db.execute(query)
    db_track = result.scalar_one_or_none()

    if db_track is None:
        raise HTTPException(status_code=404, detail="Track not found at position")

    await db.delete(db_track)
    await db.commit()
