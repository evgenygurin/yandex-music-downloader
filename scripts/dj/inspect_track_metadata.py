#!/usr/bin/env python3
"""Исследование доступных метаданных трека в Yandex Music API"""

import sys

from yandex_music import Client

TOKEN = sys.argv[1] if len(sys.argv) > 1 else None
PLAYLIST_ID = "250905515/1113"

if not TOKEN:
    print("Usage: python inspect_track_metadata.py <TOKEN>")
    sys.exit(1)

# Инициализация
client = Client(TOKEN).init()
owner_id, kind = PLAYLIST_ID.split("/")
playlist = client.users_playlists(kind, owner_id)

# Берем первый трек для анализа
track_short = playlist.tracks[0]
track = track_short.track

print("=" * 80)
print(f"АНАЛИЗ ТРЕКА: {track.artists[0].name} - {track.title}")
print("=" * 80)

# Все доступные атрибуты трека
print("\n📋 АТРИБУТЫ ОБЪЕКТА TRACK:")
for attr in sorted(dir(track)):
    if not attr.startswith("_"):
        try:
            value = getattr(track, attr)
            if not callable(value):
                print(f"  {attr:30} = {repr(value)[:100]}")
        except:
            pass

# Проверяем albums
if track.albums:
    album = track.albums[0]
    print("\n📀 АТРИБУТЫ АЛЬБОМА:")
    for attr in sorted(dir(album)):
        if not attr.startswith("_"):
            try:
                value = getattr(album, attr)
                if not callable(value):
                    print(f"  {attr:30} = {repr(value)[:100]}")
            except:
                pass

# Проверяем artists
if track.artists:
    artist = track.artists[0]
    print("\n🎤 АТРИБУТЫ ИСПОЛНИТЕЛЯ:")
    for attr in sorted(dir(artist)):
        if not attr.startswith("_"):
            try:
                value = getattr(artist, attr)
                if not callable(value):
                    print(f"  {attr:30} = {repr(value)[:100]}")
            except:
                pass

# Получаем полную информацию о треке
print("\n🔍 ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ API:")
try:
    # Попытка получить дополнительные данные
    track_full = client.tracks([track.id])[0]
    print(f"  Supplement available: {hasattr(track_full, 'supplement')}")
    if hasattr(track_full, "supplement") and track_full.supplement:
        print(f"  Supplement: {track_full.supplement}")
except Exception as e:
    print(f"  Error: {e}")

# Проверяем метаданные через download_info
print("\n📥 DOWNLOAD INFO:")
try:
    download_info = track.get_download_info()
    if download_info:
        for info in download_info[:2]:  # первые 2
            print(f"  Codec: {info.codec}, Bitrate: {info.bitrate_in_kbps}kbps")
except Exception as e:
    print(f"  Error: {e}")

print("\n" + "=" * 80)
