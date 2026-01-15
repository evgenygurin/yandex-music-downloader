#!/usr/bin/env python3
"""
Рекомендации треков для улучшения плейлиста
Находит треки которые заполнят пробелы в Camelot Wheel и BPM диапазоне
"""

import json
import logging
from collections import Counter
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent
DJ_SET_DIR = PROJECT_DIR / "dj_set_techno_2025"
METADATA_FILE = DJ_SET_DIR / "tracklist_metadata.json"

# Camelot Wheel mapping
CAMELOT_TO_KEY = {
    "1A": "Am",
    "1B": "C",
    "2A": "Em",
    "2B": "G",
    "3A": "Bm",
    "3B": "D",
    "4A": "F#m",
    "4B": "A",
    "5A": "C#m",
    "5B": "E",
    "6A": "G#m",
    "6B": "B",
    "7A": "D#m",
    "7B": "F#",
    "8A": "A#m",
    "8B": "C#",
    "9A": "Fm",
    "9B": "G#",
    "10A": "Cm",
    "10B": "D#",
    "11A": "Gm",
    "11B": "A#",
    "12A": "Dm",
    "12B": "F",
}

CAMELOT_TRANSITIONS = {
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


# ============================================================================
# АНАЛИЗ ПЛЕЙЛИСТА
# ============================================================================


def analyze_playlist_gaps(tracks):
    """Анализ пробелов в плейлисте"""
    # BPM распределение
    bpm_values = [t["bpm"] for t in tracks if t.get("bpm")]
    bpm_min = min(bpm_values) if bpm_values else 120
    bpm_max = max(bpm_values) if bpm_values else 135

    # Key распределение
    key_distribution = Counter(t.get("camelot") for t in tracks if t.get("camelot"))
    present_keys = set(key_distribution.keys())
    all_keys = set(CAMELOT_TRANSITIONS.keys())
    missing_keys = all_keys - present_keys

    # BPM gaps (диапазоны где мало треков)
    bpm_ranges = {
        "115-120": sum(1 for bpm in bpm_values if 115 <= bpm < 120),
        "120-125": sum(1 for bpm in bpm_values if 120 <= bpm < 125),
        "125-130": sum(1 for bpm in bpm_values if 125 <= bpm < 130),
        "130-135": sum(1 for bpm in bpm_values if 130 <= bpm < 135),
        "135-140": sum(1 for bpm in bpm_values if 135 <= bpm < 140),
    }

    # Находим underpopulated ranges
    avg_per_range = sum(bpm_ranges.values()) / len(bpm_ranges) if bpm_ranges else 0
    sparse_ranges = {k: v for k, v in bpm_ranges.items() if v < avg_per_range * 0.7}

    return {
        "bpm_range": (bpm_min, bpm_max),
        "bpm_distribution": bpm_ranges,
        "sparse_bpm_ranges": sparse_ranges,
        "missing_keys": sorted(missing_keys),
        "key_distribution": dict(key_distribution),
        "total_tracks": len(tracks),
    }


def recommend_track_criteria(gaps, priority="balance"):
    """Генерация критериев для рекомендуемых треков"""
    recommendations = []

    # Приоритет 1: Заполнение пробелов в Camelot Wheel
    if gaps["missing_keys"]:
        for missing_key in gaps["missing_keys"][:8]:
            # Находим совместимые ключи которые уже есть
            compatible = CAMELOT_TRANSITIONS.get(missing_key, [])
            present_compatible = [k for k in compatible if k in gaps["key_distribution"].keys()]

            musical_key = CAMELOT_TO_KEY.get(missing_key, missing_key)

            recommendations.append(
                {
                    "priority": "high",
                    "type": "missing_key",
                    "camelot": missing_key,
                    "musical_key": musical_key,
                    "bpm_range": gaps["bpm_range"],
                    "compatible_with": present_compatible,
                    "reason": f"Отсутствующий ключ {missing_key} ({musical_key})",
                    "search_query": f"techno house {musical_key} {gaps['bpm_range'][0]}-{gaps['bpm_range'][1]} BPM",
                }
            )

    # Приоритет 2: Заполнение sparse BPM ranges
    if gaps["sparse_bpm_ranges"]:
        for bpm_range, count in gaps["sparse_bpm_ranges"].items():
            # Находим какие ключи популярны в плейлисте
            popular_keys = sorted(
                gaps["key_distribution"].items(), key=lambda x: x[1], reverse=True
            )[:5]

            for camelot, _ in popular_keys:
                musical_key = CAMELOT_TO_KEY.get(camelot, camelot)

                recommendations.append(
                    {
                        "priority": "medium",
                        "type": "sparse_bpm",
                        "camelot": camelot,
                        "musical_key": musical_key,
                        "bpm_range": tuple(map(int, bpm_range.split("-"))),
                        "reason": f"Мало треков в {bpm_range} BPM, ключ {camelot}",
                        "search_query": f"techno house {musical_key} {bpm_range} BPM",
                    }
                )

    # Приоритет 3: Усиление популярных ключей для plateau mixing
    if priority == "plateau":
        popular_keys = sorted(gaps["key_distribution"].items(), key=lambda x: x[1], reverse=True)[
            :3
        ]

        for camelot, count in popular_keys:
            if count >= 3:  # Уже есть минимум для plateau
                musical_key = CAMELOT_TO_KEY.get(camelot, camelot)

                recommendations.append(
                    {
                        "priority": "low",
                        "type": "plateau_reinforcement",
                        "camelot": camelot,
                        "musical_key": musical_key,
                        "bpm_range": gaps["bpm_range"],
                        "reason": f"Усиление ключа {camelot} для plateau mixing (сейчас {count} треков)",
                        "search_query": f"techno house {musical_key} {gaps['bpm_range'][0]}-{gaps['bpm_range'][1]} BPM",
                    }
                )

    return recommendations


# ============================================================================
# SCORING СИСТЕМЫ ДЛЯ КАНДИДАТОВ
# ============================================================================


def score_candidate_track(candidate, current_playlist, gaps):
    """Оценка кандидата на добавление в плейлист"""
    score = 0
    reasons = []

    camelot = candidate.get("camelot")
    bpm = candidate.get("bpm")
    key_confidence = candidate.get("key_confidence", 0)

    # 1. Missing key bonus (+50 points)
    if camelot in gaps["missing_keys"]:
        score += 50
        reasons.append(f"+50: Заполняет пробел в Camelot Wheel ({camelot})")

    # 2. Sparse BPM range bonus (+30 points)
    if bpm:
        for bpm_range, count in gaps["sparse_bpm_ranges"].items():
            range_min, range_max = map(int, bpm_range.split("-"))
            if range_min <= bpm < range_max:
                score += 30
                reasons.append(f"+30: BPM в sparse range ({bpm_range})")
                break

    # 3. Harmonic connectivity (+20 points)
    if camelot:
        compatible = CAMELOT_TRANSITIONS.get(camelot, [])
        connectivity = sum(1 for k in compatible if k in gaps["key_distribution"].keys())
        connectivity_score = min(20, connectivity * 5)
        score += connectivity_score
        reasons.append(f"+{connectivity_score}: Совместим с {connectivity} ключами")

    # 4. Key confidence bonus (+15 points)
    if key_confidence >= 0.35:
        score += 15
        reasons.append(f"+15: Высокая key confidence ({key_confidence:.2f})")
    elif key_confidence >= 0.25:
        score += 10
        reasons.append(f"+10: Хорошая key confidence ({key_confidence:.2f})")

    # 5. BPM in optimal range (+10 points)
    if bpm and 120 <= bpm <= 135:
        score += 10
        reasons.append(f"+10: BPM в оптимальном диапазоне ({bpm})")

    # Penalties
    # -20: Duplicate key with many existing tracks
    if camelot and gaps["key_distribution"].get(camelot, 0) >= 5:
        score -= 20
        reasons.append(f"-20: Много треков в этом ключе ({gaps['key_distribution'][camelot]})")

    # -15: Very low key confidence
    if key_confidence < 0.25:
        score -= 15
        reasons.append(f"-15: Низкая key confidence ({key_confidence:.2f})")

    return {
        "score": score,
        "reasons": reasons,
        "recommendation": "add" if score >= 40 else "maybe" if score >= 20 else "skip",
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("💡 РЕКОМЕНДАЦИИ ТРЕКОВ ДЛЯ ПЛЕЙЛИСТА")
    logger.info("=" * 70)

    # Загрузка метаданных
    logger.info(f"\n📋 Загрузка метаданных из {METADATA_FILE}...")
    with open(METADATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
        tracks = data["tracks"]

    logger.info(f"✓ Загружено {len(tracks)} треков\n")

    # Анализ пробелов
    logger.info("=" * 70)
    logger.info("🔍 АНАЛИЗ ПРОБЕЛОВ В ПЛЕЙЛИСТЕ")
    logger.info("=" * 70)

    gaps = analyze_playlist_gaps(tracks)

    logger.info(f"\nBPM диапазон: {gaps['bpm_range'][0]:.1f} - {gaps['bpm_range'][1]:.1f}")
    logger.info("\nРаспределение по BPM:")
    for bpm_range, count in gaps["bpm_distribution"].items():
        bar = "█" * min(count, 30)
        sparse_marker = " ⚠️  (sparse)" if bpm_range in gaps["sparse_bpm_ranges"] else ""
        logger.info(f"  {bpm_range}: {count:2d} треков | {bar}{sparse_marker}")

    logger.info(f"\nОтсутствующие ключи ({len(gaps['missing_keys'])}):")
    if gaps["missing_keys"]:
        for i in range(0, len(gaps["missing_keys"]), 12):
            chunk = gaps["missing_keys"][i : i + 12]
            logger.info(f"  {', '.join(chunk)}")
    else:
        logger.info("  ✅ Все 24 ключа представлены")

    # Генерация рекомендаций
    logger.info("\n" + "=" * 70)
    logger.info("🎯 РЕКОМЕНДАЦИИ ПО ДОБАВЛЕНИЮ ТРЕКОВ")
    logger.info("=" * 70)

    recommendations = recommend_track_criteria(gaps, priority="balance")

    # Группировка по приоритету
    high_priority = [r for r in recommendations if r["priority"] == "high"]
    medium_priority = [r for r in recommendations if r["priority"] == "medium"]
    low_priority = [r for r in recommendations if r["priority"] == "low"]

    if high_priority:
        logger.info(f"\n🔴 ВЫСОКИЙ ПРИОРИТЕТ ({len(high_priority)}):\n")
        for i, rec in enumerate(high_priority[:10], 1):
            logger.info(f"  {i}. {rec['reason']}")
            logger.info(f"     Camelot: {rec['camelot']} | Musical Key: {rec['musical_key']}")
            logger.info(f"     BPM: {rec['bpm_range'][0]}-{rec['bpm_range'][1]}")
            if rec.get("compatible_with"):
                logger.info(f"     Совместим с: {', '.join(rec['compatible_with'])}")
            logger.info(f'     🔍 Поиск: "{rec["search_query"]}"')
            logger.info("")

    if medium_priority:
        logger.info(f"🟡 СРЕДНИЙ ПРИОРИТЕТ ({len(medium_priority)}):\n")
        for i, rec in enumerate(medium_priority[:5], 1):
            logger.info(f"  {i}. {rec['reason']}")
            logger.info(f'     🔍 Поиск: "{rec["search_query"]}"')
            logger.info("")

    if low_priority:
        logger.info(f"🟢 НИЗКИЙ ПРИОРИТЕТ ({len(low_priority)}):")
        logger.info(f"   {len(low_priority)} рекомендаций для plateau mixing усиления\n")

    # Сохранение рекомендаций
    output_file = DJ_SET_DIR / "track_recommendations.json"
    recommendations_data = {
        "gaps_analysis": gaps,
        "recommendations": recommendations,
        "summary": {
            "high_priority": len(high_priority),
            "medium_priority": len(medium_priority),
            "low_priority": len(low_priority),
            "total": len(recommendations),
        },
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(recommendations_data, f, ensure_ascii=False, indent=2)

    logger.info(f"✓ Сохранены рекомендации: {output_file}\n")

    # Итоговые советы
    logger.info("=" * 70)
    logger.info("📝 СЛЕДУЮЩИЕ ШАГИ")
    logger.info("=" * 70)

    logger.info("\n1. Найти треки по рекомендациям выше")
    logger.info("2. Скачать в dj_set_techno_2025/")
    logger.info("3. Запустить анализ:")
    logger.info("   ./run_full_analysis.sh")
    logger.info("4. Проверить качество:")
    logger.info("   python validate_playlist.py")

    logger.info("\n" + "=" * 70)
    logger.info("✨ Готово!")
    logger.info("=" * 70)
