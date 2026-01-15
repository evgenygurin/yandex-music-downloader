"""Yandex Music integration module."""

from dj_ai_studio.yandex.api import (
    ApiTrackQuality,
    Codec,
    Container,
    CustomDownloadInfo,
    FileFormat,
    decrypt_data,
    download_track_data,
    get_download_info,
)
from dj_ai_studio.yandex.client import YandexClient, YandexClientConfig
from dj_ai_studio.yandex.converter import (
    camelot_to_key,
    key_to_camelot,
    yandex_track_to_track,
)
from dj_ai_studio.yandex.mime_utils import MimeType, guess_mime_type
from dj_ai_studio.yandex.sync import SyncResult, SyncStats, YandexSyncService

__all__ = [
    # API
    "ApiTrackQuality",
    "Codec",
    "Container",
    "CustomDownloadInfo",
    "FileFormat",
    "decrypt_data",
    "download_track_data",
    "get_download_info",
    # Client
    "YandexClient",
    "YandexClientConfig",
    # Converter
    "yandex_track_to_track",
    "key_to_camelot",
    "camelot_to_key",
    # Utils
    "MimeType",
    "guess_mime_type",
    # Sync
    "YandexSyncService",
    "SyncResult",
    "SyncStats",
]
