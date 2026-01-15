#!/usr/bin/env python3
"""Переименование треков плейлиста в порядке плейлиста"""

import logging
import shutil
import sys
from pathlib import Path

from yandex_music import Client

# Настройка уровня логирования
log_level = logging.DEBUG if "--debug" in sys.argv else logging.INFO

# Настройка логирования
logging.basicConfig(
    level=log_level, format="%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Получение токена (исключаем --debug из argv)
args = [arg for arg in sys.argv[1:] if arg != "--debug"]
TOKEN = args[0] if args else None
PLAYLIST_ID = "250905515/1113"
PROJECT_DIR = Path(__file__).parent  # Директория где находится скрипт
SOURCE_DIR = PROJECT_DIR / "music_download"
TARGET_DIR = PROJECT_DIR / "dj_set_techno_2025"

if not TOKEN:
    logger.error("Токен не указан")
    logger.info("Usage: python reorder_playlist.py <TOKEN> [--debug]")
    sys.exit(1)

# Инициализация клиента
logger.info("🔐 Авторизация в Яндекс.Музыке...")
try:
    client = Client(TOKEN).init()
    logger.info(f"✓ Авторизован как: {client.me.account.display_name}")
except Exception as e:
    logger.error(f"Ошибка авторизации: {e}")
    sys.exit(1)

# Получение плейлиста
owner_id, kind = PLAYLIST_ID.split("/")
logger.info(f"📋 Загрузка плейлиста {PLAYLIST_ID}...")
try:
    playlist = client.users_playlists(kind, owner_id)
    logger.info(f"✓ Плейлист '{playlist.title}' ({len(playlist.tracks)} треков)")
except Exception as e:
    logger.error(f"Ошибка загрузки плейлиста: {e}")
    sys.exit(1)

# Создание целевой директории
TARGET_DIR.mkdir(exist_ok=True)
logger.info(f"📁 Целевая директория: {TARGET_DIR}")
logger.info("")

# Статистика
stats = {"success": 0, "not_found": 0, "errors": 0}

for idx, track_short in enumerate(playlist.tracks, 1):
    track = track_short.track

    # Формирование имени файла
    artists = ", ".join([artist.name for artist in track.artists])
    title = track.title

    logger.debug(f"[{idx:02d}/{len(playlist.tracks)}] Обработка: {artists} - {title}")

    # Поиск файла в SOURCE_DIR
    found_file = None
    candidates = []

    logger.debug(f"  Поиск по названию: '{title}'")
    for file_path in SOURCE_DIR.rglob("*.m4a"):
        # Пропускаем целевую директорию чтобы не копировать файлы сами на себя
        if TARGET_DIR in file_path.parents:
            continue
        if title in file_path.name or file_path.stem.endswith(title):
            candidates.append(file_path)

    logger.debug(f"  Найдено кандидатов: {len(candidates)}")

    # Если найден только один кандидат - используем его
    if len(candidates) == 1:
        found_file = candidates[0]
        logger.debug(f"  ✓ Единственный кандидат: {found_file.name}")
    # Если несколько - пробуем найти по исполнителю
    elif len(candidates) > 1:
        logger.debug("  Множественные кандидаты, поиск по исполнителю...")
        for candidate in candidates:
            if any(artist.name in str(candidate.parent) for artist in track.artists):
                found_file = candidate
                logger.debug(f"  ✓ Найден по исполнителю: {candidate.name}")
                break
        # Если не нашли по исполнителю - берем первого кандидата
        if not found_file:
            found_file = candidates[0]
            logger.debug(f"  → Используется первый кандидат: {found_file.name}")

    if not found_file:
        logger.warning(f"⚠️  [{idx:02d}/{len(playlist.tracks)}] НЕ НАЙДЕН: {artists} - {title}")
        stats["not_found"] += 1
        continue

    # Новое имя файла
    new_name = f"{idx:02d} - {artists} - {title}.m4a"
    # Очистка имени от недопустимых символов
    new_name = new_name.replace("/", "_").replace(":", " -")

    target_file = TARGET_DIR / new_name

    # Копирование файла
    try:
        shutil.copy2(found_file, target_file)
        file_size = target_file.stat().st_size / (1024 * 1024)  # MB
        logger.info(
            f"✅ [{idx:02d}/{len(playlist.tracks)}] {artists} - {title} ({file_size:.1f} MB)"
        )
        stats["success"] += 1
    except Exception as e:
        logger.error(f"❌ [{idx:02d}/{len(playlist.tracks)}] Ошибка копирования: {e}")
        stats["errors"] += 1

# Итоговая статистика
logger.info("")
logger.info("=" * 60)
logger.info("📊 СТАТИСТИКА")
logger.info("=" * 60)
logger.info(f"✅ Успешно:     {stats['success']}/{len(playlist.tracks)}")
logger.info(f"⚠️  Не найдено:  {stats['not_found']}/{len(playlist.tracks)}")
logger.info(f"❌ Ошибки:      {stats['errors']}/{len(playlist.tracks)}")
logger.info(f"📁 Директория:  {TARGET_DIR}")
logger.info("=" * 60)
