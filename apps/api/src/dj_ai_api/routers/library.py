"""Library stats endpoints."""

from dj_ai_studio.db import SetORM, TrackORM
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import func, select

from ..deps import DbSession

router = APIRouter(prefix="/library", tags=["library"])


class LibraryStats(BaseModel):
    """Library statistics."""

    total_tracks: int
    analyzed_tracks: int
    total_sets: int
    bpm_range: tuple[float, float] | None
    avg_energy: float | None


@router.get("/stats", response_model=LibraryStats)
async def get_library_stats(db: DbSession) -> LibraryStats:
    """Get library statistics."""
    # Total tracks
    total_result = await db.execute(select(func.count(TrackORM.id)))
    total_tracks = total_result.scalar() or 0

    # Analyzed tracks (have BPM)
    analyzed_result = await db.execute(
        select(func.count(TrackORM.id)).where(TrackORM.bpm.isnot(None))
    )
    analyzed_tracks = analyzed_result.scalar() or 0

    # Total sets
    sets_result = await db.execute(select(func.count(SetORM.id)))
    total_sets = sets_result.scalar() or 0

    # BPM range
    bpm_min_result = await db.execute(select(func.min(TrackORM.bpm)))
    bpm_max_result = await db.execute(select(func.max(TrackORM.bpm)))
    bpm_min = bpm_min_result.scalar()
    bpm_max = bpm_max_result.scalar()

    bpm_range = None
    if bpm_min is not None and bpm_max is not None:
        bpm_range = (bpm_min, bpm_max)

    # Average energy
    avg_energy_result = await db.execute(select(func.avg(TrackORM.energy)))
    avg_energy = avg_energy_result.scalar()

    return LibraryStats(
        total_tracks=total_tracks,
        analyzed_tracks=analyzed_tracks,
        total_sets=total_sets,
        bpm_range=bpm_range,
        avg_energy=avg_energy,
    )
