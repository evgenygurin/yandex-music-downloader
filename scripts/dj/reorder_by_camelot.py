#!/usr/bin/env python3
"""
Сортировка треков по Camelot Wheel для гармоничных DJ миксов
Создает оптимальные последовательности для minimal/deep tech/progressive techno
"""

import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent
DJ_SET_DIR = PROJECT_DIR / "dj_set_techno_2025"
METADATA_FILE = DJ_SET_DIR / "tracklist_metadata.json"

# Camelot Wheel: совместимые переходы
CAMELOT_TRANSITIONS = {
    # Format: camelot_code -> [perfect_match, energy_boost, mood_change]
    "1A": ["1A", "2A", "12A", "1B"],
    "2A": ["2A", "3A", "1A", "2B"],
    "3A": ["3A", "4A", "2A", "3B"],
    "4A": ["4A", "5A", "3A", "4B"],
    "5A": ["5A", "6A", "4A", "5B"],
    "6A": ["6A", "7A", "5A", "6B"],
    "7A": ["7A", "8A", "6A", "7B"],
    "8A": ["8A", "9A", "7A", "8B"],
    "9A": ["9A", "10A", "8A", "9B"],
    "10A": ["10A", "11A", "9A", "10B"],
    "11A": ["11A", "12A", "10A", "11B"],
    "12A": ["12A", "1A", "11A", "12B"],
    "1B": ["1B", "2B", "12B", "1A"],
    "2B": ["2B", "3B", "1B", "2A"],
    "3B": ["3B", "4B", "2B", "3A"],
    "4B": ["4B", "5B", "3B", "4A"],
    "5B": ["5B", "6B", "4B", "5A"],
    "6B": ["6B", "7B", "5B", "6A"],
    "7B": ["7B", "8B", "6B", "7A"],
    "8B": ["8B", "9B", "7B", "8A"],
    "9B": ["9B", "10B", "8B", "9A"],
    "10B": ["10B", "11B", "9B", "10A"],
    "11B": ["11B", "12B", "10B", "11A"],
    "12B": ["12B", "1B", "11B", "12A"],
}


def calculate_compatibility_score(current_camelot, next_camelot, current_bpm, next_bpm):
    """
    Расчет совместимости двух треков
    Returns: score (0-100)
    """
    score = 0

    # Key compatibility (0-60 points)
    if current_camelot and next_camelot:
        transitions = CAMELOT_TRANSITIONS.get(current_camelot, [])
        if next_camelot == current_camelot:
            score += 60  # Perfect match
        elif next_camelot in transitions[:2]:  # ±1 на wheel
            score += 50  # Energy boost
        elif next_camelot in transitions[2:3]:  # ±1 обратно
            score += 40  # Energy decrease
        elif next_camelot == transitions[3]:  # Major/minor switch
            score += 45  # Mood change
        else:
            score += 10  # Плохая совместимость

    # BPM compatibility (0-40 points)
    if current_bpm and next_bpm:
        bpm_diff = abs(next_bpm - current_bpm)
        if bpm_diff == 0:
            score += 40
        elif bpm_diff <= 2:
            score += 35
        elif bpm_diff <= 4:
            score += 25
        elif bpm_diff <= 6:
            score += 15
        else:
            score += 5

    return score


def build_harmonic_chain(tracks, start_key=None, strategy="progressive"):
    """
    Построение гармонической цепочки треков

    Strategies:
    - 'progressive': постепенное нарастание энергии
    - 'plateau': длинные блоки в одном ключе
    - 'journey': разнообразие с гармоничными переходами
    """
    if not tracks:
        return []

    # Группировка треков по Camelot
    by_camelot = defaultdict(list)
    for track in tracks:
        camelot = track.get("camelot")
        if camelot:
            by_camelot[camelot].append(track)

    # Выбор стартового трека
    if start_key and start_key in by_camelot:
        current = by_camelot[start_key].pop(0)
    else:
        # Начать с самого популярного ключа
        popular_key = max(by_camelot.keys(), key=lambda k: len(by_camelot[k]))
        current = by_camelot[popular_key].pop(0)

    chain = [current]
    used_tracks = {current["position"]}

    # Построение цепочки
    while len(chain) < len(tracks):
        best_score = -1
        best_track = None
        best_camelot = None

        current_camelot = current.get("camelot")
        current_bpm = current.get("bpm")

        # Найти лучший следующий трек
        for camelot, candidates in by_camelot.items():
            if not candidates:
                continue

            for track in candidates:
                if track["position"] in used_tracks:
                    continue

                score = calculate_compatibility_score(
                    current_camelot, camelot, current_bpm, track.get("bpm")
                )

                # Бонус за progressive стратегию (нарастание BPM)
                if strategy == "progressive" and track.get("bpm", 0) > current_bpm:
                    score += 10

                # Бонус за plateau (те же BPM+key)
                if (
                    strategy == "plateau"
                    and track.get("bpm") == current_bpm
                    and camelot == current_camelot
                ):
                    score += 15

                if score > best_score:
                    best_score = score
                    best_track = track
                    best_camelot = camelot

        if best_track:
            chain.append(best_track)
            used_tracks.add(best_track["position"])
            by_camelot[best_camelot].remove(best_track)
            current = best_track
        else:
            # Не нашли совместимый - берем любой оставшийся
            for camelot, candidates in by_camelot.items():
                remaining = [t for t in candidates if t["position"] not in used_tracks]
                if remaining:
                    track = remaining[0]
                    chain.append(track)
                    used_tracks.add(track["position"])
                    by_camelot[camelot].remove(track)
                    current = track
                    break

    return chain


def generate_set_variations(tracks):
    """Генерация нескольких вариантов сета"""
    variations = {}

    # 1. Progressive Journey (120 → 130+ BPM)
    logger.info("\n🎚️  Генерация Progressive Journey...")
    progressive = build_harmonic_chain(tracks.copy(), strategy="progressive")
    variations["progressive"] = progressive

    # 2. Plateau Mix (long blocks in same key)
    logger.info("🎵 Генерация Plateau Mix...")
    plateau = build_harmonic_chain(tracks.copy(), strategy="plateau")
    variations["plateau"] = plateau

    # 3. Harmonic Journey (разнообразие)
    logger.info("🌊 Генерация Harmonic Journey...")
    journey = build_harmonic_chain(tracks.copy(), strategy="journey")
    variations["journey"] = journey

    return variations


def save_variation(tracks, name, output_dir):
    """Сохранение вариации в отдельную директорию"""
    var_dir = output_dir / name
    var_dir.mkdir(exist_ok=True)

    # M3U8
    m3u_file = var_dir / f"{name}.m3u8"
    with open(m3u_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for idx, track in enumerate(tracks, 1):
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

    # Tracklist TXT
    txt_file = var_dir / f"{name}_tracklist.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("═══════════════════════════════════════════\n")
        f.write(f"  {name.upper().replace('_', ' ')}\n")
        f.write("═══════════════════════════════════════════\n\n")

        for idx, track in enumerate(tracks, 1):
            bpm = track.get("bpm", "???")
            key = track.get("key", "???")
            camelot = track.get("camelot", "???")
            f.write(f"{idx:02d}. {track['artist']} - {track['title']}\n")
            f.write(f"    {bpm} BPM | {key} ({camelot}) | {track['genre']}\n\n")

    logger.info(f"✓ Сохранено: {var_dir}")


# ============================================================================
# MAIN
# ============================================================================

logger.info("=" * 70)
logger.info("🎛️  CAMELOT WHEEL - HARMONIC REORDERING")
logger.info("=" * 70)

# Загрузка метаданных
logger.info(f"\n📋 Загрузка метаданных из {METADATA_FILE}...")
with open(METADATA_FILE, encoding="utf-8") as f:
    data = json.load(f)
    tracks = data["tracks"]

logger.info(f"✓ Загружено {len(tracks)} треков")

# Фильтр: только треки с Camelot + BPM
tracks_with_key = [t for t in tracks if t.get("camelot") and t.get("bpm")]
logger.info(f"✓ Треков с Key+BPM: {len(tracks_with_key)}")

if len(tracks_with_key) < 10:
    logger.error("❌ Недостаточно треков с определенным ключом!")
    logger.info("   Запустите analyze_audio.py для анализа ключей")
    sys.exit(1)

# Генерация вариаций
logger.info("\n" + "=" * 70)
logger.info("🔄 ГЕНЕРАЦИЯ ВАРИАЦИЙ СЕТА")
logger.info("=" * 70)

variations = generate_set_variations(tracks_with_key)

# Сохранение вариаций
output_dir = DJ_SET_DIR / "harmonic_sets"
output_dir.mkdir(exist_ok=True)

for name, track_list in variations.items():
    save_variation(track_list, name, output_dir)

# Статистика
logger.info("\n" + "=" * 70)
logger.info("📊 СТАТИСТИКА ВАРИАЦИЙ")
logger.info("=" * 70)

for name, track_list in variations.items():
    bpms = [t["bpm"] for t in track_list if t.get("bpm")]
    keys = [t["camelot"] for t in track_list if t.get("camelot")]

    logger.info(f"\n{name.upper()}:")
    logger.info(f"  Треков: {len(track_list)}")
    logger.info(f"  BPM: {min(bpms):.1f} → {max(bpms):.1f}")
    logger.info(f"  Keys: {len(set(keys))} unique")
    logger.info(f"  Start: {keys[0]} @ {bpms[0]} BPM")
    logger.info(f"  End:   {keys[-1]} @ {bpms[-1]} BPM")

logger.info("\n" + "=" * 70)
logger.info("✨ Готово! Harmonic sets сохранены в:")
logger.info(f"   {output_dir}")
logger.info("=" * 70)
