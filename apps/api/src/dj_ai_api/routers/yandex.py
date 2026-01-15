"""Yandex Music integration endpoints."""

from typing import Annotated

from dj_ai_studio.yandex import (
    YandexClient,
    YandexClientConfig,
    YandexSyncService,
)
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..deps import AppSettings, DbSession

router = APIRouter(prefix="/yandex", tags=["yandex"])


class SyncPlaylistRequest(BaseModel):
    """Request to sync a specific playlist."""

    user_id: str
    playlist_id: str


class SyncPlaylistResponse(BaseModel):
    """Response from playlist sync."""

    playlist_id: str
    tracks_added: int
    tracks_updated: int
    tracks_skipped: int
    errors: list[str]


class SyncAllResponse(BaseModel):
    """Response from syncing all playlists."""

    playlists_synced: int
    total_tracks_added: int
    total_tracks_updated: int
    total_tracks_skipped: int
    errors: list[str]


class PlaylistInfo(BaseModel):
    """Basic playlist information."""

    id: str
    title: str
    track_count: int


def get_yandex_client(settings: AppSettings) -> YandexClient:
    """Get configured Yandex Music client."""
    if not settings.yandex_token:
        raise HTTPException(
            status_code=503,
            detail="Yandex Music token not configured. Set YANDEX_TOKEN environment variable.",
        )

    config = YandexClientConfig(
        token=settings.yandex_token,
        timeout=settings.yandex_timeout,
        max_retries=settings.yandex_max_retries,
    )
    return YandexClient(config)


# Type alias for Yandex client dependency
YandexDep = Annotated[YandexClient, Depends(get_yandex_client)]


@router.get("/playlists", response_model=list[PlaylistInfo])
async def list_playlists(client: YandexDep) -> list[PlaylistInfo]:
    """List all playlists for the authenticated user."""
    playlists = await client.get_user_playlists()

    return [
        PlaylistInfo(
            id=str(p.kind),
            title=p.title or "Untitled",
            track_count=p.track_count or 0,
        )
        for p in playlists
        if p.kind is not None
    ]


@router.post("/sync/playlist", response_model=SyncPlaylistResponse)
async def sync_playlist(
    request: SyncPlaylistRequest,
    db: DbSession,
    client: YandexDep,
) -> SyncPlaylistResponse:
    """Sync a specific playlist from Yandex Music.

    Imports all tracks from the playlist into the local database.
    Existing tracks (by source + source_id) are skipped.
    """
    service = YandexSyncService(client, db)
    result = await service.sync_playlist(request.user_id, request.playlist_id)

    return SyncPlaylistResponse(
        playlist_id=result.playlist_id,
        tracks_added=result.tracks_added,
        tracks_updated=result.tracks_updated,
        tracks_skipped=result.tracks_skipped,
        errors=result.errors,
    )


@router.post("/sync/liked", response_model=SyncPlaylistResponse)
async def sync_liked_tracks(
    db: DbSession,
    client: YandexDep,
) -> SyncPlaylistResponse:
    """Sync liked tracks from Yandex Music.

    Imports all liked tracks into the local database.
    """
    service = YandexSyncService(client, db)
    result = await service.sync_liked_tracks()

    return SyncPlaylistResponse(
        playlist_id="liked",
        tracks_added=result.tracks_added,
        tracks_updated=result.tracks_updated,
        tracks_skipped=result.tracks_skipped,
        errors=result.errors,
    )


@router.post("/sync/all", response_model=SyncAllResponse)
async def sync_all_playlists(
    db: DbSession,
    client: YandexDep,
    user_id: str | None = None,
) -> SyncAllResponse:
    """Sync all playlists from Yandex Music.

    Imports tracks from all user playlists into the local database.
    """
    service = YandexSyncService(client, db)
    stats = await service.sync_all_playlists(user_id)

    return SyncAllResponse(
        playlists_synced=stats.playlists_synced,
        total_tracks_added=stats.total_tracks_added,
        total_tracks_updated=stats.total_tracks_updated,
        total_tracks_skipped=stats.total_tracks_skipped,
        errors=stats.errors,
    )
