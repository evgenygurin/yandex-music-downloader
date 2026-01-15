#!/usr/bin/env python3
"""
Валидация и фильтрация треков для DJ плейлиста
Проверяет BPM, Key confidence, Energy flow, Harmonic compatibility
"""

import json
import logging
from pathlib import Path
from collections import defaultdict, Counter

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
# КРИТЕРИИ ВАЛИДАЦИИ
# ============================================================================

VALIDATION_CRITERIA = {
    # BPM диапазон для techno/house
    'bpm_min': 115,
    'bpm_max': 140,
    'bpm_optimal_min': 120,
    'bpm_optimal_max': 135,

    # Key detection confidence
    'key_confidence_min': 0.25,  # Минимальная уверенность
    'key_confidence_good': 0.35,  # Хорошая уверенность

    # Energy level
    'energy_min': 2.0,
    'energy_max': 10.0,
    'energy_jump_max': 3.0,  # Максимальный скачок между треками

    # Duration
    'duration_min': 120,  # 2 минуты
    'duration_max': 600,  # 10 минут

    # Camelot Wheel coverage
    'min_keys_diversity': 8,  # Минимум 8 разных ключей
}


# Camelot Wheel transitions для проверки совместимости
CAMELOT_TRANSITIONS = {
    '1A': ['1A', '2A', '12A', '1B'],
    '2A': ['2A', '3A', '1A', '2B'],
    '3A': ['3A', '4A', '2A', '3B'],
    '4A': ['4A', '5A', '3A', '4B'],
    '5A': ['5A', '6A', '4A', '5B'],
    '6A': ['6A', '7A', '5A', '6B'],
    '7A': ['7A', '8A', '6A', '7B'],
    '8A': ['8A', '9A', '7A', '8B'],
    '9A': ['9A', '10A', '8A', '9B'],
    '10A': ['10A', '11A', '9A', '10B'],
    '11A': ['11A', '12A', '10A', '11B'],
    '12A': ['12A', '1A', '11A', '12B'],
    '1B': ['1B', '2B', '12B', '1A'],
    '2B': ['2B', '3B', '1B', '2A'],
    '3B': ['3B', '4B', '2B', '3A'],
    '4B': ['4B', '5B', '3B', '4A'],
    '5B': ['5B', '6B', '4B', '5A'],
    '6B': ['6B', '7B', '5B', '6A'],
    '7B': ['7B', '8B', '6B', '7A'],
    '8B': ['8B', '9B', '7B', '8A'],
    '9B': ['9B', '10B', '8B', '9A'],
    '10B': ['10B', '11B', '9B', '10A'],
    '11B': ['11B', '12B', '10B', '11A'],
    '12B': ['12B', '1B', '11B', '12A'],
}


# ============================================================================
# ВАЛИДАЦИЯ ОТДЕЛЬНОГО ТРЕКА
# ============================================================================

def validate_track(track, criteria=VALIDATION_CRITERIA):
    """Проверка трека по критериям качества"""
    issues = []
    warnings = []
    score = 100.0  # Начальный score

    # 1. BPM проверка
    bpm = track.get('bpm')
    if not bpm:
        issues.append("Отсутствует BPM")
        score -= 50
    elif bpm < criteria['bpm_min'] or bpm > criteria['bpm_max']:
        issues.append(f"BPM {bpm} вне диапазона {criteria['bpm_min']}-{criteria['bpm_max']}")
        score -= 30
    elif bpm < criteria['bpm_optimal_min'] or bpm > criteria['bpm_optimal_max']:
        warnings.append(f"BPM {bpm} не в оптимальном диапазоне {criteria['bpm_optimal_min']}-{criteria['bpm_optimal_max']}")
        score -= 5

    # 2. Key и confidence проверка
    key = track.get('key')
    camelot = track.get('camelot')
    confidence = track.get('key_confidence', 0)

    if not key or not camelot:
        issues.append("Отсутствует Key detection")
        score -= 40
    elif confidence < criteria['key_confidence_min']:
        issues.append(f"Key confidence слишком низкий: {confidence:.2f}")
        score -= 25
    elif confidence < criteria['key_confidence_good']:
        warnings.append(f"Key confidence ниже оптимального: {confidence:.2f}")
        score -= 10

    # 3. Energy level проверка
    energy = track.get('energy')
    if not energy:
        warnings.append("Отсутствует Energy level")
        score -= 5
    elif energy < criteria['energy_min'] or energy > criteria['energy_max']:
        warnings.append(f"Energy {energy} вне диапазона {criteria['energy_min']}-{criteria['energy_max']}")
        score -= 5

    # 4. Duration проверка
    duration = track.get('duration')
    if duration:
        if duration < criteria['duration_min']:
            warnings.append(f"Трек слишком короткий: {duration}s")
            score -= 10
        elif duration > criteria['duration_max']:
            warnings.append(f"Трек слишком длинный: {duration}s")
            score -= 5

    # Определение статуса
    if issues:
        status = 'REJECT'
    elif score >= 90:
        status = 'EXCELLENT'
    elif score >= 75:
        status = 'GOOD'
    elif score >= 60:
        status = 'ACCEPTABLE'
    else:
        status = 'POOR'

    return {
        'status': status,
        'score': score,
        'issues': issues,
        'warnings': warnings
    }


# ============================================================================
# АНАЛИЗ ПЛЕЙЛИСТА
# ============================================================================

def analyze_playlist_quality(tracks, criteria=VALIDATION_CRITERIA):
    """Анализ качества всего плейлиста"""
    results = []

    for track in tracks:
        validation = validate_track(track, criteria)
        results.append({
            'track': track,
            'validation': validation
        })

    # Статистика
    stats = {
        'total': len(tracks),
        'excellent': sum(1 for r in results if r['validation']['status'] == 'EXCELLENT'),
        'good': sum(1 for r in results if r['validation']['status'] == 'GOOD'),
        'acceptable': sum(1 for r in results if r['validation']['status'] == 'ACCEPTABLE'),
        'poor': sum(1 for r in results if r['validation']['status'] == 'POOR'),
        'reject': sum(1 for r in results if r['validation']['status'] == 'REJECT'),
    }

    stats['pass_rate'] = ((stats['excellent'] + stats['good'] + stats['acceptable']) / stats['total'] * 100) if stats['total'] > 0 else 0
    stats['avg_score'] = sum(r['validation']['score'] for r in results) / len(results) if results else 0

    return results, stats


def analyze_camelot_coverage(tracks):
    """Анализ покрытия Camelot Wheel"""
    key_distribution = Counter(t.get('camelot') for t in tracks if t.get('camelot'))

    all_keys = set(CAMELOT_TRANSITIONS.keys())
    present_keys = set(key_distribution.keys())
    missing_keys = all_keys - present_keys

    # Проверка гармонической связности
    isolated_keys = []
    for key in present_keys:
        compatible = CAMELOT_TRANSITIONS.get(key, [])
        has_neighbors = any(k in present_keys for k in compatible if k != key)
        if not has_neighbors:
            isolated_keys.append(key)

    return {
        'total_keys': len(present_keys),
        'missing_keys': sorted(missing_keys),
        'isolated_keys': isolated_keys,
        'distribution': dict(key_distribution.most_common()),
        'coverage_percent': (len(present_keys) / len(all_keys) * 100)
    }


def analyze_energy_flow(tracks):
    """Анализ энергетического потока"""
    issues = []

    for i in range(len(tracks) - 1):
        current = tracks[i]
        next_track = tracks[i + 1]

        current_energy = current.get('energy', 5.0)
        next_energy = next_track.get('energy', 5.0)

        energy_jump = abs(next_energy - current_energy)

        if energy_jump > VALIDATION_CRITERIA['energy_jump_max']:
            issues.append({
                'position': i + 1,
                'from': f"{current['artist']} - {current['title']}",
                'to': f"{next_track['artist']} - {next_track['title']}",
                'jump': energy_jump,
                'from_energy': current_energy,
                'to_energy': next_energy
            })

    return issues


# ============================================================================
# ФИЛЬТРАЦИЯ ТРЕКОВ
# ============================================================================

def filter_tracks(tracks, min_score=60, reject_issues=True):
    """Фильтрация треков по критериям качества"""
    filtered = []
    rejected = []

    for track in tracks:
        validation = validate_track(track)

        if reject_issues and validation['issues']:
            rejected.append({'track': track, 'validation': validation})
        elif validation['score'] < min_score:
            rejected.append({'track': track, 'validation': validation})
        else:
            filtered.append(track)

    return filtered, rejected


def suggest_missing_keys(tracks, target_coverage=12):
    """Рекомендации каких ключей не хватает"""
    key_distribution = Counter(t.get('camelot') for t in tracks if t.get('camelot'))
    present_keys = set(key_distribution.keys())
    all_keys = set(CAMELOT_TRANSITIONS.keys())
    missing_keys = all_keys - present_keys

    # Приоритизация: какие ключи важнее добавить
    priority_keys = []
    for missing_key in missing_keys:
        # Считаем сколько присутствующих ключей совместимы с этим
        compatible = CAMELOT_TRANSITIONS.get(missing_key, [])
        compatibility_count = sum(1 for k in compatible if k in present_keys)

        priority_keys.append({
            'key': missing_key,
            'compatibility_count': compatibility_count,
            'compatible_with': [k for k in compatible if k in present_keys]
        })

    # Сортируем по совместимости (чем больше, тем приоритетнее)
    priority_keys.sort(key=lambda x: x['compatibility_count'], reverse=True)

    return priority_keys[:target_coverage - len(present_keys)]


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🔍 ВАЛИДАЦИЯ И ФИЛЬТРАЦИЯ ПЛЕЙЛИСТА")
    logger.info("=" * 70)

    # Загрузка метаданных
    logger.info(f"\n📋 Загрузка метаданных из {METADATA_FILE}...")
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        tracks = data['tracks']

    logger.info(f"✓ Загружено {len(tracks)} треков\n")

    # ========================================================================
    # 1. АНАЛИЗ КАЧЕСТВА ТРЕКОВ
    # ========================================================================

    logger.info("=" * 70)
    logger.info("📊 АНАЛИЗ КАЧЕСТВА ТРЕКОВ")
    logger.info("=" * 70)

    results, stats = analyze_playlist_quality(tracks)

    logger.info(f"\nСтатистика качества:")
    logger.info(f"  ✅ Excellent:  {stats['excellent']:2d}/{stats['total']} ({stats['excellent']/stats['total']*100:.1f}%)")
    logger.info(f"  ✅ Good:       {stats['good']:2d}/{stats['total']} ({stats['good']/stats['total']*100:.1f}%)")
    logger.info(f"  ⚠️  Acceptable: {stats['acceptable']:2d}/{stats['total']} ({stats['acceptable']/stats['total']*100:.1f}%)")
    logger.info(f"  🔴 Poor:       {stats['poor']:2d}/{stats['total']} ({stats['poor']/stats['total']*100:.1f}%)")
    logger.info(f"  ❌ Reject:     {stats['reject']:2d}/{stats['total']} ({stats['reject']/stats['total']*100:.1f}%)")
    logger.info(f"\n  Pass Rate: {stats['pass_rate']:.1f}%")
    logger.info(f"  Avg Score: {stats['avg_score']:.1f}/100")

    # Показать проблемные треки
    problematic = [r for r in results if r['validation']['status'] in ['POOR', 'REJECT']]
    if problematic:
        logger.info(f"\n⚠️  Проблемные треки ({len(problematic)}):\n")
        for r in problematic[:10]:  # Показываем первые 10
            track = r['track']
            val = r['validation']
            logger.info(f"  [{val['status']:10}] {track['artist'][:30]:30} - {track['title'][:30]:30}")
            logger.info(f"              Score: {val['score']:.1f}/100")
            if val['issues']:
                for issue in val['issues']:
                    logger.info(f"              ❌ {issue}")
            if val['warnings']:
                for warning in val['warnings'][:2]:
                    logger.info(f"              ⚠️  {warning}")
            logger.info("")

    # ========================================================================
    # 2. АНАЛИЗ CAMELOT WHEEL COVERAGE
    # ========================================================================

    logger.info("=" * 70)
    logger.info("🎹 АНАЛИЗ CAMELOT WHEEL COVERAGE")
    logger.info("=" * 70)

    camelot_analysis = analyze_camelot_coverage(tracks)

    logger.info(f"\nПокрытие Camelot Wheel:")
    logger.info(f"  Уникальных ключей: {camelot_analysis['total_keys']}/24")
    logger.info(f"  Coverage: {camelot_analysis['coverage_percent']:.1f}%")

    if camelot_analysis['missing_keys']:
        logger.info(f"\n  Отсутствующие ключи ({len(camelot_analysis['missing_keys'])}):")
        logger.info(f"    {', '.join(camelot_analysis['missing_keys'][:12])}")

    if camelot_analysis['isolated_keys']:
        logger.info(f"\n  ⚠️  Изолированные ключи (нет совместимых):")
        logger.info(f"    {', '.join(camelot_analysis['isolated_keys'])}")

    logger.info(f"\n  Распределение по ключам (топ 10):")
    for key, count in list(camelot_analysis['distribution'].items())[:10]:
        bar = "█" * min(count, 30)
        logger.info(f"    {key:4} | {count:2d} треков | {bar}")

    # ========================================================================
    # 3. АНАЛИЗ ENERGY FLOW
    # ========================================================================

    logger.info("\n" + "=" * 70)
    logger.info("⚡ АНАЛИЗ ENERGY FLOW")
    logger.info("=" * 70)

    energy_issues = analyze_energy_flow(tracks)

    if energy_issues:
        logger.info(f"\n⚠️  Резкие скачки энергии (>{VALIDATION_CRITERIA['energy_jump_max']}):\n")
        for issue in energy_issues[:5]:
            logger.info(f"  Позиция {issue['position']:2d}:")
            logger.info(f"    От: {issue['from'][:50]}")
            logger.info(f"        Energy: {issue['from_energy']:.1f}")
            logger.info(f"    К:  {issue['to'][:50]}")
            logger.info(f"        Energy: {issue['to_energy']:.1f}")
            logger.info(f"    Скачок: {issue['jump']:.1f} ⚠️")
            logger.info("")
    else:
        logger.info("\n✅ Energy flow плавный, резких скачков нет")

    # ========================================================================
    # 4. ФИЛЬТРАЦИЯ ТРЕКОВ
    # ========================================================================

    logger.info("=" * 70)
    logger.info("🔧 ФИЛЬТРАЦИЯ ТРЕКОВ")
    logger.info("=" * 70)

    filtered, rejected = filter_tracks(tracks, min_score=60, reject_issues=True)

    logger.info(f"\nРезультаты фильтрации:")
    logger.info(f"  ✅ Приняты:   {len(filtered)}/{len(tracks)} ({len(filtered)/len(tracks)*100:.1f}%)")
    logger.info(f"  ❌ Отклонены: {len(rejected)}/{len(tracks)} ({len(rejected)/len(tracks)*100:.1f}%)")

    if rejected:
        logger.info(f"\n  Причины отклонения:")
        reject_reasons = defaultdict(int)
        for r in rejected:
            for issue in r['validation']['issues']:
                reject_reasons[issue] += 1

        for reason, count in sorted(reject_reasons.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"    {count:2d}x - {reason}")

    # Сохранение отфильтрованного плейлиста
    if len(filtered) < len(tracks):
        output_file = DJ_SET_DIR / "tracklist_metadata_filtered.json"
        data_filtered = {
            'tracks': filtered,
            'metadata': {
                'original_count': len(tracks),
                'filtered_count': len(filtered),
                'rejected_count': len(rejected),
                'filter_criteria': VALIDATION_CRITERIA
            }
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data_filtered, f, ensure_ascii=False, indent=2)

        logger.info(f"\n✓ Сохранен отфильтрованный плейлист: {output_file}")

    # ========================================================================
    # 5. РЕКОМЕНДАЦИИ
    # ========================================================================

    logger.info("\n" + "=" * 70)
    logger.info("💡 РЕКОМЕНДАЦИИ")
    logger.info("=" * 70)

    suggestions = suggest_missing_keys(tracks)

    if suggestions:
        logger.info(f"\nРекомендуемые ключи для добавления:")
        for i, suggestion in enumerate(suggestions[:8], 1):
            logger.info(f"  {i}. {suggestion['key']} - совместим с: {', '.join(suggestion['compatible_with'])}")
    else:
        logger.info("\n✅ Camelot Wheel покрытие достаточное")

    # Итоговые рекомендации
    logger.info(f"\n📝 Итоговые рекомендации:")

    if stats['reject'] > 0:
        logger.info(f"  1. Удалить {stats['reject']} треков с критическими проблемами")

    if stats['poor'] > 0:
        logger.info(f"  2. Пересмотреть {stats['poor']} треков с низким качеством")

    if len(camelot_analysis['isolated_keys']) > 0:
        suggested_keys = [s['key'] for s in suggestions[:3]]
        logger.info(f"  3. Добавить треки в ключах: {', '.join(suggested_keys)} для лучшей связности")

    if len(energy_issues) > 5:
        logger.info(f"  4. Сгладить {len(energy_issues)} резких скачков энергии")

    if stats['pass_rate'] >= 90:
        logger.info(f"\n✅ Плейлист высокого качества! Pass rate: {stats['pass_rate']:.1f}%")
    elif stats['pass_rate'] >= 75:
        logger.info(f"\n✅ Плейлист хорошего качества. Pass rate: {stats['pass_rate']:.1f}%")
    else:
        logger.info(f"\n⚠️  Рекомендуется улучшить качество. Pass rate: {stats['pass_rate']:.1f}%")

    logger.info("\n" + "=" * 70)
    logger.info("✨ Анализ завершен!")
    logger.info("=" * 70)
