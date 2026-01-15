#!/usr/bin/env python3
"""
Запись BPM и Key метаданных в ID3 tags аудиофайлов
Для совместимости с djay Pro AI, Rekordbox, Traktor, Serato
"""

import json
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent
DJ_SET_DIR = PROJECT_DIR / "dj_set_techno_2025"
METADATA_FILE = DJ_SET_DIR / "tracklist_metadata.json"

# Проверка зависимостей
try:
    from mutagen.id3 import COMM, ID3, TBPM, TKEY
    from mutagen.mp4 import MP4

    logger.info("✓ mutagen доступен")
    HAS_MUTAGEN = True
except ImportError:
    logger.error("❌ mutagen не установлен")
    logger.info("Установите: pip install mutagen")
    HAS_MUTAGEN = False
    import sys

    sys.exit(1)


# OpenKey (Camelot) mapping для djay Pro
CAMELOT_TO_OPENKEY = {
    "1A": "6m",
    "1B": "6d",
    "2A": "7m",
    "2B": "7d",
    "3A": "8m",
    "3B": "8d",
    "4A": "9m",
    "4B": "9d",
    "5A": "10m",
    "5B": "10d",
    "6A": "11m",
    "6B": "11d",
    "7A": "12m",
    "7B": "12d",
    "8A": "1m",
    "8B": "1d",
    "9A": "2m",
    "9B": "2d",
    "10A": "3m",
    "10B": "3d",
    "11A": "4m",
    "11B": "4d",
    "12A": "5m",
    "12B": "5d",
}


def write_m4a_tags(file_path, bpm=None, key=None, camelot=None, energy=None):
    """Запись тегов в M4A файл (iTunes/Apple format)"""
    try:
        audio = MP4(str(file_path))

        # BPM
        if bpm:
            audio["\xa9BPM"] = [str(int(round(bpm)))]  # Apple BPM tag
            audio["tmpo"] = [int(round(bpm))]  # Alternative BPM tag

        # Key (Musical Key format для djay Pro)
        if key:
            audio["\xa9key"] = [key]  # Apple key tag

        # OpenKey (Camelot для djay Pro)
        if camelot:
            openkey = CAMELOT_TO_OPENKEY.get(camelot, camelot)
            audio["----:com.apple.iTunes:KEY"] = openkey.encode("utf-8")

        # Energy (custom tag)
        if energy:
            audio["----:com.apple.iTunes:ENERGY"] = str(energy).encode("utf-8")

        audio.save()
        return True
    except Exception as e:
        logger.debug(f"Ошибка записи M4A тегов: {e}")
        return False


def write_mp3_tags(file_path, bpm=None, key=None, camelot=None, energy=None):
    """Запись ID3 тегов в MP3 файл"""
    try:
        audio = ID3(str(file_path))

        # BPM
        if bpm:
            audio.add(TBPM(encoding=3, text=str(int(round(bpm)))))

        # Key
        if key:
            audio.add(TKEY(encoding=3, text=key))

        # OpenKey/Camelot в комментариях
        if camelot:
            openkey = CAMELOT_TO_OPENKEY.get(camelot, camelot)
            audio.add(COMM(encoding=3, lang="eng", desc="Camelot", text=f"{camelot} ({openkey})"))

        # Energy
        if energy:
            audio.add(COMM(encoding=3, lang="eng", desc="Energy", text=str(energy)))

        audio.save()
        return True
    except Exception as e:
        logger.debug(f"Ошибка записи MP3 тегов: {e}")
        return False


def write_audio_tags(file_path, track):
    """Универсальная запись тегов в аудиофайл"""
    bpm = track.get("bpm")
    key = track.get("key")
    camelot = track.get("camelot")
    energy = track.get("energy")

    file_path = Path(file_path)

    if file_path.suffix.lower() in [".m4a", ".mp4", ".m4p"]:
        return write_m4a_tags(file_path, bpm, key, camelot, energy)
    elif file_path.suffix.lower() == ".mp3":
        return write_mp3_tags(file_path, bpm, key, camelot, energy)
    else:
        logger.warning(f"Неподдерживаемый формат: {file_path.suffix}")
        return False


# ============================================================================
# MAIN
# ============================================================================

logger.info("=" * 70)
logger.info("💾 ЗАПИСЬ МЕТАДАННЫХ В АУДИОФАЙЛЫ")
logger.info("=" * 70)

# Загрузка метаданных
logger.info(f"\n📋 Загрузка метаданных из {METADATA_FILE}...")
with open(METADATA_FILE, encoding="utf-8") as f:
    data = json.load(f)
    tracks = data["tracks"]

logger.info(f"✓ Загружено {len(tracks)} треков\n")

# Запись тегов
logger.info("🎵 Запись BPM, Key, Camelot в аудиофайлы...\n")
stats = {"success": 0, "error": 0, "missing": 0}

for idx, track in enumerate(tracks, 1):
    file_path = Path(track["file_path"])

    if not file_path.exists():
        logger.warning(f"⚠️  [{idx:02d}/50] Файл не найден: {file_path.name}")
        stats["missing"] += 1
        continue

    logger.info(f"🔧 [{idx:02d}/50] {track['artist'][:30]:30}")

    success = write_audio_tags(file_path, track)

    if success:
        bpm = track.get("bpm", "N/A")
        key = track.get("key", "N/A")
        camelot = track.get("camelot", "N/A")
        openkey = CAMELOT_TO_OPENKEY.get(camelot, "N/A") if camelot != "N/A" else "N/A"

        logger.info(f"    ✓ BPM: {bpm}, Key: {key} ({camelot} / OpenKey: {openkey})")
        stats["success"] += 1
    else:
        stats["error"] += 1

# Статистика
logger.info("\n" + "=" * 70)
logger.info("📊 СТАТИСТИКА")
logger.info("=" * 70)
logger.info(f"✅ Успешно обновлено: {stats['success']}/{len(tracks)}")
logger.info(f"❌ Ошибки:            {stats['error']}/{len(tracks)}")
logger.info(f"⚠️  Файлы не найдены:  {stats['missing']}/{len(tracks)}")
logger.info("=" * 70)

logger.info("\n✨ Готово!")
logger.info("\n📖 Следующие шаги:")
logger.info("   1. Импортируйте M3U8 в djay Pro AI:")
logger.info("      File → Import → M3U8 Playlist")
logger.info("   2. djay Pro автоматически прочитает BPM и Key из файлов")
logger.info("   3. Используйте Color Coding для harmonic mixing")
