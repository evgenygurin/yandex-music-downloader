#!/usr/bin/env python3
"""
Анализ аудиофайлов для определения BPM и Key
Использует librosa для BPM и essentia для Key detection
"""

import json
import logging
import sys
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Проверка зависимостей
try:
    import librosa
    import numpy as np

    logger.info("✓ librosa доступна")
except ImportError:
    logger.error("❌ librosa не установлена")
    logger.info("Установите: pip install librosa")
    sys.exit(1)

# Импорт key detector (librosa-based, без C dependencies)
try:
    from key_detector import detect_key

    logger.info("✓ Key detector доступен (librosa chroma + Krumhansl-Schmuckler)")
    HAS_KEY_DETECTOR = True
except ImportError as e:
    logger.warning(f"⚠️  Key detector не найден: {e}")
    HAS_KEY_DETECTOR = False

PROJECT_DIR = Path(__file__).parent
DJ_SET_DIR = PROJECT_DIR / "dj_set_techno_2025"
METADATA_FILE = DJ_SET_DIR / "tracklist_metadata.json"

# Загрузка метаданных
logger.info(f"📋 Загрузка метаданных из {METADATA_FILE}...")
with open(METADATA_FILE, encoding="utf-8") as f:
    data = json.load(f)
    tracks = data["tracks"]

logger.info(f"✓ Загружено {len(tracks)} треков\n")

# Camelot Wheel mapping для DJ
CAMELOT_WHEEL = {
    "C": "8B",
    "C#": "3B",
    "D": "10B",
    "D#": "5B",
    "E": "12B",
    "F": "7B",
    "F#": "2B",
    "G": "9B",
    "G#": "4B",
    "A": "11B",
    "A#": "6B",
    "B": "1B",
    "Cm": "5A",
    "C#m": "12A",
    "Dm": "7A",
    "D#m": "2A",
    "Em": "9A",
    "Fm": "4A",
    "F#m": "11A",
    "Gm": "6A",
    "G#m": "1A",
    "Am": "8A",
    "A#m": "3A",
    "Bm": "10A",
    # Essentia формат (полное название)
    "Cmajor": "8B",
    "C#major": "3B",
    "Dmajor": "10B",
    "D#major": "5B",
    "Emajor": "12B",
    "Fmajor": "7B",
    "F#major": "2B",
    "Gmajor": "9B",
    "G#major": "4B",
    "Amajor": "11B",
    "A#major": "6B",
    "Bmajor": "1B",
    "Cminor": "5A",
    "C#minor": "12A",
    "Dminor": "7A",
    "D#minor": "2A",
    "Eminor": "9A",
    "Fminor": "4A",
    "F#minor": "11A",
    "Gminor": "6A",
    "G#minor": "1A",
    "Aminor": "8A",
    "A#minor": "3A",
    "Bminor": "10A",
}


def analyze_bpm(audio_path):
    """Определение BPM с помощью librosa (оптимизировано для techno)"""
    try:
        # 3 минуты для более точного определения в techno
        y, sr = librosa.load(audio_path, duration=180)

        # Настройки для techno/house (120-140 BPM)
        tempo, beats = librosa.beat.beat_track(
            y=y,
            sr=sr,
            start_bpm=125.0,  # Стартовая точка для techno
            tightness=200,  # Увеличенная точность
        )

        bpm = round(float(tempo), 1)
        logger.debug(f"    BPM detected: {bpm} (beats: {len(beats)})")
        return bpm
    except Exception as e:
        logger.error(f"Ошибка BPM анализа: {e}")
        return None


def analyze_key(audio_path):
    """Определение тональности с помощью librosa chroma (Krumhansl-Schmuckler algorithm)"""
    if not HAS_KEY_DETECTOR:
        return None, None, None

    try:
        # Используем новый key detector на базе librosa
        key, camelot, confidence = detect_key(str(audio_path), duration=180)

        if not key:
            return None, None, None

        # Предупреждение при низкой уверенности (< 0.6 для chroma-based detection)
        if confidence < 0.6:
            logger.warning(f"    ⚠️  Низкая уверенность key detection: {confidence:.2f}")

        logger.debug(f"    Key detection: {key} (Camelot: {camelot}, confidence: {confidence:.2f})")
        return key, camelot, confidence
    except Exception as e:
        logger.debug(f"    Key анализ ошибка: {str(e)[:50]}")
        return None, None, None


# Анализ треков
logger.info("🎵 Анализ аудиофайлов...\n")
stats = {"analyzed": 0, "errors": 0, "missing": 0}

for idx, track in enumerate(tracks, 1):
    file_path = Path(track["file_path"])

    if not file_path.exists():
        logger.warning(f"⚠️  [{idx:02d}/50] Файл не найден: {file_path.name}")
        stats["missing"] += 1
        continue

    logger.info(f"🔍 [{idx:02d}/50] {track['artist']} - {track['title']}")

    try:
        # BPM анализ
        bpm = analyze_bpm(file_path)
        if bpm:
            track["bpm"] = bpm
            logger.info(f"    BPM: {bpm}")

        # Key анализ
        if HAS_KEY_DETECTOR:
            key, camelot, confidence = analyze_key(file_path)
            if key:
                track["key"] = key
                track["camelot"] = camelot
                track["key_confidence"] = confidence
                conf_emoji = "✓" if confidence and confidence >= 0.6 else "⚠️"
                logger.info(f"    Key: {key} (Camelot: {camelot}) {conf_emoji} {confidence}")

        stats["analyzed"] += 1

    except Exception as e:
        logger.error(f"    ❌ Ошибка: {e}")
        stats["errors"] += 1

# Сохранение обновленных метаданных
logger.info("\n💾 Сохранение обновленных метаданных...")
with open(METADATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
logger.info(f"✓ Сохранено в {METADATA_FILE}")

# Обновление M3U8
m3u_file = DJ_SET_DIR / "techno_2025.m3u8"
with open(m3u_file, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    for track in tracks:
        f.write(
            f"#EXTINF:{int(track['duration_ms'] / 1000)},{track['artist']} - {track['title']}\n"
        )
        f.write(f"#EXTGENRE:{track['genre']}\n")
        if track.get("bpm"):
            f.write(f"#EXTBPM:{track['bpm']}\n")
        if track.get("key"):
            f.write(f"#EXTKEY:{track['key']}\n")
        if track.get("camelot"):
            f.write(f"#EXTCAMELOT:{track['camelot']}\n")
        f.write(f"{track['filename']}\n")
logger.info("✓ M3U8 обновлен")

# Статистика
logger.info("\n" + "=" * 60)
logger.info("📊 СТАТИСТИКА АНАЛИЗА")
logger.info("=" * 60)
logger.info(f"✅ Проанализировано: {stats['analyzed']}/{len(tracks)}")
logger.info(f"⚠️  Не найдено:      {stats['missing']}/{len(tracks)}")
logger.info(f"❌ Ошибки:          {stats['errors']}/{len(tracks)}")

# BPM статистика
bpms = [t["bpm"] for t in tracks if t.get("bpm")]
if bpms:
    logger.info(f"\nBPM диапазон: {min(bpms):.1f} - {max(bpms):.1f}")
    logger.info(f"Средний BPM:  {sum(bpms) / len(bpms):.1f}")

# Key статистика
if HAS_ESSENTIA:
    keys = {}
    for track in tracks:
        if track.get("key"):
            k = track["key"]
            keys[k] = keys.get(k, 0) + 1

    if keys:
        logger.info("\nТональности:")
        for key, count in sorted(keys.items(), key=lambda x: x[1], reverse=True)[:5]:
            logger.info(f"  {key:10} {count:3d} треков")

logger.info("=" * 60)
logger.info("\n✨ Анализ завершен!")
logger.info("📁 Файлы готовы для импорта в DJ Pro AI")
