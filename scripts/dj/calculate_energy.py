#!/usr/bin/env python3
"""
Расчет Energy Level для каждого трека (1-10 шкала)
+ генерация визуализации energy flow сета
"""

import sys
import json
import logging
from pathlib import Path

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


def calculate_energy_level(bpm, loudness_lufs, genre, key=None):
    """
    Расчет Energy Level (1-10) на основе параметров трека

    Факторы:
    - BPM (40%)
    - Loudness (30%)
    - Genre (20%)
    - Key (major/minor) (10%)
    """
    energy = 0.0

    # 1. BPM contribution (40% веса)
    if bpm:
        # Techno/House диапазон: 117-136 BPM
        if bpm < 120:
            bpm_score = 2.0  # Deep/slow
        elif 120 <= bpm < 123:
            bpm_score = 4.0  # Warm-up
        elif 123 <= bpm < 126:
            bpm_score = 6.0  # Building
        elif 126 <= bpm < 129:
            bpm_score = 7.5  # Peak time
        elif 129 <= bpm < 132:
            bpm_score = 9.0  # Climax
        else:
            bpm_score = 10.0  # Hard techno

        energy += bpm_score * 0.4

    # 2. Loudness contribution (30% веса)
    if loudness_lufs is not None:
        # LUFS для electronic music: -14 (тихо) до -6 (громко)
        # Нормализуем к шкале 1-10
        if loudness_lufs < -12:
            loudness_score = 3.0  # Тихий, ambient
        elif -12 <= loudness_lufs < -10:
            loudness_score = 5.0  # Средний
        elif -10 <= loudness_lufs < -8:
            loudness_score = 7.0  # Громкий
        else:
            loudness_score = 9.0  # Очень громкий

        energy += loudness_score * 0.3

    # 3. Genre contribution (20% веса)
    genre_scores = {
        'techno': 8.0,
        'house': 6.5,
        'dance': 7.0,
        'electronics': 5.5,
        'ambient': 3.0,
        'deep house': 5.0,
        'minimal': 5.5,
    }

    genre_lower = genre.lower() if genre else ''
    genre_score = 6.0  # Default

    for g, score in genre_scores.items():
        if g in genre_lower:
            genre_score = score
            break

    energy += genre_score * 0.2

    # 4. Key (major/minor) contribution (10% веса)
    if key:
        # Minor keys = темнее, lower energy
        # Major keys = ярче, higher energy
        if 'm' in key or key.endswith('m'):
            key_score = 5.0  # Minor
        else:
            key_score = 7.0  # Major

        energy += key_score * 0.1
    else:
        energy += 6.0 * 0.1  # Default

    # Финальное округление до 1-10
    energy = max(1.0, min(10.0, energy))
    return round(energy, 1)


def categorize_energy(energy):
    """Категоризация энергии для DJ"""
    if energy < 3.5:
        return "Warm-up"
    elif energy < 5.5:
        return "Building"
    elif energy < 7.5:
        return "Peak Time"
    elif energy < 9.0:
        return "Climax"
    else:
        return "Hard Peak"


def generate_ascii_visualization(tracks):
    """ASCII визуализация energy flow"""
    viz = []
    viz.append("\n" + "=" * 80)
    viz.append("📊 ENERGY FLOW VISUALIZATION")
    viz.append("=" * 80)
    viz.append("")

    max_width = 60
    for idx, track in enumerate(tracks, 1):
        energy = track.get('energy', 5.0)
        category = categorize_energy(energy)
        bpm = track.get('bpm', '???')
        key = track.get('key', '???')

        # Energy bar
        bar_length = int((energy / 10.0) * max_width)
        bar = "█" * bar_length

        # Color coding (ASCII safe)
        if energy < 4:
            symbol = "▁"
        elif energy < 6:
            symbol = "▃"
        elif energy < 8:
            symbol = "▅"
        else:
            symbol = "█"

        viz.append(f"{idx:02d}. {track['artist'][:30]:30} | {energy:4.1f}/10 {symbol}")
        viz.append(f"    {bar}")
        key_str = key if key else "N/A"
        viz.append(f"    {category:12} | {bpm} BPM | {key_str:5} | {track['genre']}")
        viz.append("")

    viz.append("=" * 80)
    return "\n".join(viz)


def generate_set_structure_analysis(tracks):
    """Анализ структуры сета"""
    analysis = []
    analysis.append("\n" + "=" * 80)
    analysis.append("🎛️  SET STRUCTURE ANALYSIS")
    analysis.append("=" * 80)
    analysis.append("")

    total_duration = sum(t.get('duration_ms', 0) for t in tracks) / 1000 / 60
    analysis.append(f"Total Duration: {total_duration:.1f} minutes")
    analysis.append("")

    # Energy по фазам
    num_tracks = len(tracks)
    phase_size = num_tracks // 5

    phases = [
        ("WARM-UP", tracks[:phase_size]),
        ("BUILDING", tracks[phase_size:phase_size*2]),
        ("PEAK TIME", tracks[phase_size*2:phase_size*3]),
        ("CLIMAX", tracks[phase_size*3:phase_size*4]),
        ("COOL-DOWN", tracks[phase_size*4:]),
    ]

    for phase_name, phase_tracks in phases:
        if not phase_tracks:
            continue

        energies = [t.get('energy', 5.0) for t in phase_tracks]
        bpms = [t.get('bpm') for t in phase_tracks if t.get('bpm')]

        avg_energy = sum(energies) / len(energies) if energies else 0
        avg_bpm = sum(bpms) / len(bpms) if bpms else 0

        analysis.append(f"{phase_name}:")
        analysis.append(f"  Tracks:      {len(phase_tracks)}")
        analysis.append(f"  Avg Energy:  {avg_energy:.1f}/10")
        analysis.append(f"  Avg BPM:     {avg_bpm:.1f}")
        analysis.append(f"  BPM Range:   {min(bpms):.1f} - {max(bpms):.1f}" if bpms else "  BPM Range:   N/A")
        analysis.append("")

    analysis.append("=" * 80)
    return "\n".join(analysis)


# ============================================================================
# MAIN
# ============================================================================

logger.info("=" * 70)
logger.info("⚡ ENERGY LEVEL CALCULATION")
logger.info("=" * 70)

# Загрузка метаданных
logger.info(f"\n📋 Загрузка метаданных из {METADATA_FILE}...")
with open(METADATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)
    tracks = data['tracks']

logger.info(f"✓ Загружено {len(tracks)} треков\n")

# Расчет Energy Level
logger.info("🔋 Расчет Energy Level для каждого трека...\n")
energy_stats = {"calculated": 0, "missing_data": 0}

for track in tracks:
    bpm = track.get('bpm')
    loudness = track.get('loudness_lufs')
    genre = track.get('genre')
    key = track.get('key')

    if bpm or loudness:
        energy = calculate_energy_level(bpm, loudness, genre, key)
        track['energy'] = energy
        track['energy_category'] = categorize_energy(energy)
        energy_stats["calculated"] += 1

        logger.info(f"✓ [{track['position']:02d}] {track['artist'][:30]:30} | Energy: {energy:.1f}/10 ({track['energy_category']})")
        logger.debug(f"    BPM: {bpm}, Loudness: {loudness} LUFS, Genre: {genre}")
    else:
        energy_stats["missing_data"] += 1
        logger.warning(f"⚠️  [{track['position']:02d}] {track['artist'][:30]:30} | Недостаточно данных для расчета энергии")

# Сохранение обновленных метаданных
logger.info("\n💾 Сохранение обновленных метаданных...")
with open(METADATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
logger.info(f"✓ Сохранено в {METADATA_FILE}")

# Генерация визуализаций
viz_file = DJ_SET_DIR / "energy_flow_visualization.txt"
with open(viz_file, 'w', encoding='utf-8') as f:
    f.write(generate_ascii_visualization(tracks))
    f.write("\n\n")
    f.write(generate_set_structure_analysis(tracks))

logger.info(f"✓ Визуализация сохранена в {viz_file}")

# Вывод визуализации в консоль
print(generate_ascii_visualization(tracks))
print(generate_set_structure_analysis(tracks))

# Статистика
logger.info("\n" + "=" * 70)
logger.info("📊 СТАТИСТИКА")
logger.info("=" * 70)
logger.info(f"✅ Рассчитано Energy Level: {energy_stats['calculated']}/{len(tracks)}")
logger.info(f"⚠️  Недостаточно данных:    {energy_stats['missing_data']}/{len(tracks)}")

energies = [t['energy'] for t in tracks if t.get('energy')]
if energies:
    logger.info(f"\nEnergy диапазон: {min(energies):.1f} - {max(energies):.1f}")
    logger.info(f"Средний Energy:  {sum(energies)/len(energies):.1f}")

logger.info("=" * 70)
logger.info("\n✨ Готово!")
