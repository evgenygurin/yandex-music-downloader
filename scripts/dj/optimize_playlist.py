#!/usr/bin/env python3
"""
Автоматическая оптимизация плейлиста
Удаляет проблемные треки и создает оптимизированный плейлист
"""

import json
import logging
from pathlib import Path
import shutil
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent
DJ_SET_DIR = PROJECT_DIR / "dj_set_techno_2025"
METADATA_FILE = DJ_SET_DIR / "tracklist_metadata.json"


# ============================================================================
# ВАЛИДАЦИЯ (упрощенная версия из validate_playlist.py)
# ============================================================================

VALIDATION_CRITERIA = {
    'bpm_min': 115,
    'bpm_max': 140,
    'key_confidence_min': 0.25,
    'energy_min': 2.0,
    'energy_max': 10.0,
    'duration_min': 120,
}


def validate_track(track):
    """Упрощенная валидация трека"""
    issues = []
    score = 100.0

    bpm = track.get('bpm')
    if not bpm:
        issues.append("Отсутствует BPM")
        score -= 50
    elif bpm < VALIDATION_CRITERIA['bpm_min'] or bpm > VALIDATION_CRITERIA['bpm_max']:
        issues.append(f"BPM {bpm} вне диапазона")
        score -= 30

    key = track.get('key')
    confidence = track.get('key_confidence', 0)
    if not key:
        issues.append("Отсутствует Key")
        score -= 40
    elif confidence < VALIDATION_CRITERIA['key_confidence_min']:
        issues.append(f"Low key confidence: {confidence:.2f}")
        score -= 25

    return {
        'score': score,
        'issues': issues,
        'pass': len(issues) == 0 and score >= 60
    }


# ============================================================================
# ОПТИМИЗАЦИЯ
# ============================================================================

def create_optimized_playlist(tracks, mode='auto', min_score=60):
    """
    Создание оптимизированного плейлиста

    mode:
        'auto' - автоматическое удаление проблемных треков
        'manual' - только пометка проблемных треков
    """
    accepted = []
    rejected = []

    for track in tracks:
        validation = validate_track(track)

        if validation['pass'] and validation['score'] >= min_score:
            accepted.append(track)
        else:
            rejected.append({
                'track': track,
                'validation': validation
            })

    return accepted, rejected


def create_backup(metadata_file):
    """Создание резервной копии метаданных"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = metadata_file.parent / f"tracklist_metadata_backup_{timestamp}.json"

    shutil.copy2(metadata_file, backup_file)
    logger.info(f"✓ Создана резервная копия: {backup_file.name}")

    return backup_file


def update_playlist_files(accepted_tracks, output_dir):
    """Обновление M3U8 файлов с новым плейлистом"""
    m3u8_file = output_dir / "techno_2025_optimized.m3u8"

    lines = ["#EXTM3U\n"]
    for track in accepted_tracks:
        artist = track.get('artist', 'Unknown')
        title = track.get('title', 'Unknown')
        duration = track.get('duration', 0)
        filename = track.get('filename', '')

        lines.append(f"#EXTINF:{duration},{artist} - {title}\n")
        lines.append(f"{filename}\n")

    with open(m3u8_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    logger.info(f"✓ Создан оптимизированный M3U8: {m3u8_file.name}")
    return m3u8_file


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🔄 АВТОМАТИЧЕСКАЯ ОПТИМИЗАЦИЯ ПЛЕЙЛИСТА")
    logger.info("=" * 70)

    # Загрузка метаданных
    logger.info(f"\n📋 Загрузка метаданных из {METADATA_FILE}...")
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        original_tracks = data['tracks']

    logger.info(f"✓ Загружено {len(original_tracks)} треков\n")

    # Создание резервной копии
    logger.info("💾 Создание резервной копии...")
    backup_file = create_backup(METADATA_FILE)

    # Валидация и фильтрация
    logger.info("\n🔍 Валидация треков...")
    accepted, rejected = create_optimized_playlist(original_tracks, mode='auto', min_score=60)

    logger.info(f"\n📊 Результаты:")
    logger.info(f"  ✅ Приняты:   {len(accepted)}/{len(original_tracks)} ({len(accepted)/len(original_tracks)*100:.1f}%)")
    logger.info(f"  ❌ Отклонены: {len(rejected)}/{len(original_tracks)} ({len(rejected)/len(original_tracks)*100:.1f}%)")

    if rejected:
        logger.info(f"\n⚠️  Отклоненные треки:\n")
        for i, r in enumerate(rejected, 1):
            track = r['track']
            val = r['validation']
            logger.info(f"  {i}. {track['artist'][:40]:40} - {track['title'][:30]:30}")
            logger.info(f"     Score: {val['score']:.1f}/100")
            for issue in val['issues']:
                logger.info(f"     ❌ {issue}")
            logger.info("")

    # Сохранение оптимизированного плейлиста
    if len(accepted) < len(original_tracks):
        logger.info("💾 Сохранение оптимизированного плейлиста...\n")

        # Сохранение JSON метаданных
        optimized_metadata = DJ_SET_DIR / "tracklist_metadata_optimized.json"
        optimized_data = {
            'tracks': accepted,
            'metadata': {
                'original_count': len(original_tracks),
                'optimized_count': len(accepted),
                'removed_count': len(rejected),
                'optimization_date': datetime.now().isoformat(),
                'criteria': VALIDATION_CRITERIA
            }
        }

        with open(optimized_metadata, 'w', encoding='utf-8') as f:
            json.dump(optimized_data, f, ensure_ascii=False, indent=2)

        logger.info(f"✓ Метаданные: {optimized_metadata.name}")

        # Сохранение M3U8
        m3u8_file = update_playlist_files(accepted, DJ_SET_DIR)

        # Сохранение списка отклоненных
        rejected_file = DJ_SET_DIR / "rejected_tracks.json"
        with open(rejected_file, 'w', encoding='utf-8') as f:
            json.dump([r['track'] for r in rejected], f, ensure_ascii=False, indent=2)

        logger.info(f"✓ Список отклоненных: {rejected_file.name}")

        logger.info("\n" + "=" * 70)
        logger.info("📝 СЛЕДУЮЩИЕ ШАГИ")
        logger.info("=" * 70)
        logger.info(f"\n1. Проверьте оптимизированный плейлист:")
        logger.info(f"   {optimized_metadata}")
        logger.info(f"\n2. Импортируйте в djay Pro AI:")
        logger.info(f"   {m3u8_file}")
        logger.info(f"\n3. При необходимости восстановите из backup:")
        logger.info(f"   {backup_file}")

    else:
        logger.info("\n✅ Все треки прошли валидацию! Оптимизация не требуется.")

    logger.info("\n" + "=" * 70)
    logger.info("✨ Готово!")
    logger.info("=" * 70)
