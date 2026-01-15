#!/usr/bin/env python3
"""
Подготовка DJ-сета с максимальным использованием Yandex Music API
+ анализ аудио для BPM и Key
"""

import sys
import logging
import json
import csv
from pathlib import Path
from yandex_music import Client

# Настройка логирования
log_level = logging.DEBUG if "--debug" in sys.argv else logging.INFO
logging.basicConfig(
    level=log_level,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Параметры
args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
TOKEN = args[0] if args else None
PLAYLIST_ID = "250905515/1113"
PROJECT_DIR = Path(__file__).parent
DJ_SET_DIR = PROJECT_DIR / "dj_set_techno_2025"

if not TOKEN:
    logger.error("Токен не указан")
    logger.info("Usage: python prepare_dj_set.py <TOKEN> [--debug]")
    sys.exit(1)

# Инициализация
logger.info("🔐 Авторизация в Яндекс.Музыке...")
client = Client(TOKEN).init()
logger.info(f"✓ Авторизован как: {client.me.account.display_name}")

# Получение плейлиста
owner_id, kind = PLAYLIST_ID.split("/")
logger.info(f"📋 Загрузка плейлиста {PLAYLIST_ID}...")
playlist = client.users_playlists(kind, owner_id)
logger.info(f"✓ Плейлист '{playlist.title}' ({len(playlist.tracks)} треков)")

# Сбор метаданных
logger.info("\n🎵 Сбор метаданных треков...")
tracks_metadata = []

for idx, track_short in enumerate(playlist.tracks, 1):
    track = track_short.track

    # Базовые данные
    artists = ", ".join([artist.name for artist in track.artists])
    title = track.title

    # Альбом и жанр
    album_title = track.albums[0].title if track.albums else "Unknown"
    genre = track.albums[0].genre if track.albums and hasattr(track.albums[0], 'genre') else "Unknown"
    release_date = track.albums[0].release_date if track.albums and track.albums[0].release_date else None

    # Лейбл
    label = track.albums[0].labels[0].name if track.albums and track.albums[0].labels else "Unknown"

    # Громкость (ReplayGain)
    loudness = track.r128.i if track.r128 and hasattr(track.r128, 'i') else None

    # Длительность
    duration_ms = track.duration_ms
    duration_min = duration_ms / 1000 / 60 if duration_ms else 0

    # Имя файла
    filename = f"{idx:02d} - {artists} - {title}.m4a".replace("/", "_").replace(":", " -")
    file_path = DJ_SET_DIR / filename

    metadata = {
        "position": idx,
        "artist": artists,
        "title": title,
        "album": album_title,
        "genre": genre,
        "label": label,
        "release_date": release_date,
        "duration_ms": duration_ms,
        "duration_min": f"{duration_min:.2f}",
        "loudness_lufs": loudness,
        "file_path": str(file_path),
        "filename": filename,
        "track_id": track.id,
        # Поля для DJ (будут заполнены при анализе аудио)
        "bpm": None,
        "key": None,
        "energy": None,
    }

    tracks_metadata.append(metadata)
    logger.info(f"✅ [{idx:02d}/{len(playlist.tracks)}] {artists} - {title}")
    logger.debug(f"    Genre: {genre}, Label: {label}, Loudness: {loudness} LUFS")

# Экспорт метаданных
logger.info("\n📊 Экспорт метаданных...")

# 1. JSON для программной обработки
json_file = DJ_SET_DIR / "tracklist_metadata.json"
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump({
        "playlist_title": playlist.title,
        "playlist_id": PLAYLIST_ID,
        "total_tracks": len(tracks_metadata),
        "tracks": tracks_metadata
    }, f, ensure_ascii=False, indent=2)
logger.info(f"✓ JSON: {json_file}")

# 2. CSV для Excel/DJ софта
csv_file = DJ_SET_DIR / "tracklist.csv"
with open(csv_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=tracks_metadata[0].keys())
    writer.writeheader()
    writer.writerows(tracks_metadata)
logger.info(f"✓ CSV: {csv_file}")

# 3. M3U8 плейлист для DJ Pro AI
m3u_file = DJ_SET_DIR / "techno_2025.m3u8"
with open(m3u_file, 'w', encoding='utf-8') as f:
    f.write("#EXTM3U\n")
    for track in tracks_metadata:
        # Расширенные теги M3U
        f.write(f"#EXTINF:{int(track['duration_ms']/1000)},{track['artist']} - {track['title']}\n")
        f.write(f"#EXTGENRE:{track['genre']}\n")
        if track['bpm']:
            f.write(f"#EXTBPM:{track['bpm']}\n")
        if track['key']:
            f.write(f"#EXTKEY:{track['key']}\n")
        f.write(f"{track['filename']}\n")
logger.info(f"✓ M3U8: {m3u_file}")

# 4. Текстовый tracklist для постов
txt_file = DJ_SET_DIR / "tracklist.txt"
with open(txt_file, 'w', encoding='utf-8') as f:
    f.write(f"🎧 {playlist.title}\n")
    f.write(f"{'=' * 60}\n\n")
    for track in tracks_metadata:
        f.write(f"{track['position']:02d}. {track['artist']} - {track['title']}\n")
        f.write(f"    [{track['label']}] {track['genre']}\n\n")
logger.info(f"✓ TXT: {txt_file}")

# Статистика
logger.info("\n" + "=" * 60)
logger.info("📊 СТАТИСТИКА ПЛЕЙЛИСТА")
logger.info("=" * 60)
logger.info(f"Всего треков:     {len(tracks_metadata)}")

# Подсчет жанров
genres = {}
for track in tracks_metadata:
    g = track['genre']
    genres[g] = genres.get(g, 0) + 1
logger.info(f"\nЖанры:")
for genre, count in sorted(genres.items(), key=lambda x: x[1], reverse=True):
    logger.info(f"  {genre:20} {count:3d} треков")

# Подсчет лейблов
labels = {}
for track in tracks_metadata:
    l = track['label']
    labels[l] = labels.get(l, 0) + 1
logger.info(f"\nТоп-5 лейблов:")
for label, count in sorted(labels.items(), key=lambda x: x[1], reverse=True)[:5]:
    logger.info(f"  {label:30} {count:3d} треков")

# Общая длительность
total_duration = sum(t['duration_ms'] for t in tracks_metadata) / 1000 / 60
logger.info(f"\nОбщая длительность: {total_duration:.1f} минут ({total_duration/60:.1f} часов)")

logger.info("=" * 60)
logger.info("\n✨ ГОТОВО! Метаданные экспортированы")
logger.info("\n💡 СЛЕДУЮЩИЙ ШАГ: Анализ аудио для BPM и Key")
logger.info("   Установите: pip install librosa essentia-tensorflow")
logger.info("   Затем запустите: python analyze_audio.py")
