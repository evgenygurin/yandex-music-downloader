"""Audio analysis endpoints."""

from typing import Annotated
from uuid import UUID

from dj_ai_studio.analysis import AnalysisResult, AudioAnalyzer
from dj_ai_studio.db import TrackORM
from dj_ai_studio.yandex import YandexClient, YandexClientConfig
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select

from ..deps import AppSettings, DbSession

router = APIRouter(prefix="/analysis", tags=["analysis"])


class AnalysisResponse(BaseModel):
    """Response from audio analysis."""

    bpm: float
    bpm_confidence: float
    key: str
    camelot: str
    is_minor: bool
    key_confidence: float
    energy: int
    duration_seconds: float


class TrackAnalysisResponse(BaseModel):
    """Response from track analysis with update confirmation."""

    track_id: str
    analysis: AnalysisResponse
    updated: bool


def get_analyzer() -> AudioAnalyzer:
    """Get audio analyzer instance."""
    return AudioAnalyzer(analysis_duration=60.0)


AnalyzerDep = Annotated[AudioAnalyzer, Depends(get_analyzer)]


def get_yandex_client(settings: AppSettings) -> YandexClient | None:
    """Get Yandex client if configured."""
    if not settings.yandex_token:
        return None
    config = YandexClientConfig(
        token=settings.yandex_token,
        timeout=settings.yandex_timeout,
        max_retries=settings.yandex_max_retries,
    )
    return YandexClient(config)


YandexDep = Annotated[YandexClient | None, Depends(get_yandex_client)]


def _result_to_response(result: AnalysisResult) -> AnalysisResponse:
    """Convert AnalysisResult to API response."""
    return AnalysisResponse(
        bpm=result.bpm.bpm,
        bpm_confidence=result.bpm.confidence,
        key=result.key.key,
        camelot=result.key.camelot,
        is_minor=result.key.is_minor,
        key_confidence=result.key.confidence,
        energy=result.energy.energy,
        duration_seconds=result.duration_seconds,
    )


FileDep = Annotated[UploadFile, File(...)]


@router.post("/file", response_model=AnalysisResponse)
async def analyze_file(
    analyzer: AnalyzerDep,
    file: FileDep,
) -> AnalysisResponse:
    """Analyze uploaded audio file.

    Accepts mp3, flac, wav, m4a files.
    Returns BPM, key, and energy analysis.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Get file extension
    ext = file.filename.split(".")[-1].lower()
    if ext not in {"mp3", "flac", "wav", "m4a", "ogg"}:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Use mp3, flac, wav, m4a, or ogg.",
        )

    content = await file.read()
    result = await analyzer.analyze_bytes_async(content, ext)

    return _result_to_response(result)


@router.post("/track/{track_id}", response_model=TrackAnalysisResponse)
async def analyze_track(
    track_id: UUID,
    db: DbSession,
    analyzer: AnalyzerDep,
    yandex: YandexDep,
) -> TrackAnalysisResponse:
    """Analyze a track from the database.

    Downloads audio from source (Yandex Music) if needed,
    analyzes it, and updates the track with results.
    """
    # Get track from database
    result = await db.execute(select(TrackORM).where(TrackORM.id == str(track_id)))
    db_track = result.scalar_one_or_none()

    if db_track is None:
        raise HTTPException(status_code=404, detail="Track not found")

    # Currently only Yandex tracks supported
    if db_track.source != "yandex":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not supported for source: {db_track.source}",
        )

    if yandex is None:
        raise HTTPException(
            status_code=503,
            detail="Yandex Music token not configured",
        )

    # Get track from Yandex
    yandex_track = await yandex.get_track(db_track.source_id)
    if yandex_track is None:
        raise HTTPException(status_code=404, detail="Track not found on Yandex Music")

    # Download and analyze
    audio_data = await yandex.download_track(yandex_track)
    analysis = await analyzer.analyze_bytes_async(audio_data, "mp3")
    response = _result_to_response(analysis)

    # Update track in database
    db_track.bpm = response.bpm
    db_track.key = response.key
    db_track.camelot = response.camelot
    db_track.energy = response.energy
    from datetime import datetime

    db_track.analyzed_at = datetime.now()

    await db.commit()

    return TrackAnalysisResponse(
        track_id=str(track_id),
        analysis=response,
        updated=True,
    )


@router.post("/batch", response_model=list[TrackAnalysisResponse])
async def analyze_batch(
    track_ids: list[UUID],
    db: DbSession,
    analyzer: AnalyzerDep,
    yandex: YandexDep,
) -> list[TrackAnalysisResponse]:
    """Analyze multiple tracks in batch.

    Processes tracks sequentially to avoid overloading.
    Returns results for all tracks (including failures).
    """
    if len(track_ids) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 tracks per batch",
        )

    results: list[TrackAnalysisResponse] = []

    for track_id in track_ids:
        try:
            result = await analyze_track(track_id, db, analyzer, yandex)
            results.append(result)
        except HTTPException:
            # Skip failed tracks but continue processing
            pass

    return results
