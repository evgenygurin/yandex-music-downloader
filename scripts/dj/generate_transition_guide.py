#!/usr/bin/env python3
"""
Генерация детального гайда по переходам между треками
Анализирует каждую пару треков и предлагает технику микширования
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

# Camelot Wheel transitions
CAMELOT_QUALITY = {
    'perfect': ['same'],
    'excellent': ['plus_one', 'minus_one'],
    'good': ['major_minor_switch'],
    'moderate': ['plus_two', 'minus_two'],
    'challenging': ['other']
}


def get_camelot_relationship(from_key, to_key):
    """Определение типа Camelot перехода"""
    if not from_key or not to_key:
        return 'unknown', 'Неизвестно'

    # Извлекаем номер и букву
    from_num = int(''.join(filter(str.isdigit, from_key)))
    to_num = int(''.join(filter(str.isdigit, to_key)))
    from_letter = from_key[-1]
    to_letter = to_key[-1]

    if from_key == to_key:
        return 'perfect', 'Идеальный матч (тот же ключ)'

    if from_letter == to_letter:
        # Та же буква (major/minor)
        diff = (to_num - from_num) % 12
        if diff == 1 or diff == 11:
            if diff == 1:
                return 'excellent', 'Energy boost (+1 на Camelot Wheel)'
            else:
                return 'excellent', 'Energy decrease (-1 на Camelot Wheel)'
        elif diff == 2 or diff == 10:
            return 'moderate', 'Драматический переход (±2)'
    else:
        # Переход A ↔ B
        if from_num == to_num:
            return 'good', 'Major/Minor switch (смена настроения)'

    return 'challenging', 'Сложный переход - требует осторожности'


def recommend_transition_technique(track_a, track_b):
    """Рекомендация техники перехода"""
    bpm_a = track_a.get('bpm', 0)
    bpm_b = track_b.get('bpm', 0)
    key_a = track_a.get('camelot')
    key_b = track_b.get('camelot')
    energy_a = track_a.get('energy', 5.0)
    energy_b = track_b.get('energy', 5.0)

    bpm_diff = abs(bpm_b - bpm_a) if bpm_a and bpm_b else 0
    energy_diff = energy_b - energy_a

    key_quality, key_desc = get_camelot_relationship(key_a, key_b)

    # Выбор техники на основе параметров
    technique = []

    # 1. BPM совместимость
    if bpm_diff == 0:
        technique.append("⚡ **Perfect BPM Match** - используйте длинный переход (64+ бар)")
    elif bpm_diff <= 2:
        technique.append(f"⚡ **BPM близки** (Δ{bpm_diff:.1f}) - стандартный переход (32 бара)")
    elif bpm_diff <= 4:
        technique.append(f"⚠️  **BPM разница** (Δ{bpm_diff:.1f}) - короткий переход (16 бар) или pitch adjust")
    else:
        technique.append(f"🔴 **Большая BPM разница** (Δ{bpm_diff:.1f}) - требуется pitch shift или hard cut")

    # 2. Key совместимость
    if key_quality == 'perfect':
        technique.append("🎹 **Идеальный ключ** - можно делать длинный overlay")
    elif key_quality == 'excellent':
        technique.append(f"🎹 **Отличная совместимость** - {key_desc}")
    elif key_quality == 'good':
        technique.append(f"🎹 **Хороший переход** - {key_desc}")
    elif key_quality == 'moderate':
        technique.append(f"⚠️  **Умеренный переход** - {key_desc}")
    else:
        technique.append(f"🔴 **Сложный переход** - используйте EQ swap или короткий cut")

    # 3. Energy flow
    if energy_diff > 1.5:
        technique.append(f"📈 **Energy boost** (+{energy_diff:.1f}) - постепенно поднимайте highs/mids на Track B")
    elif energy_diff < -1.5:
        technique.append(f"📉 **Energy drop** ({energy_diff:.1f}) - используйте breakdown или EQ cut")
    else:
        technique.append(f"➡️  **Стабильная энергия** (Δ{energy_diff:.1f}) - плавный переход")

    # 4. Рекомендуемая техника
    if key_quality in ['perfect', 'excellent'] and bpm_diff <= 2:
        mixing_style = "**BASS SWAP MIXING** - идеально для этого перехода"
        bars = "64-96 бар"
    elif bpm_diff <= 4:
        mixing_style = "**EQ MIXING** - стандартный подход"
        bars = "32-48 бар"
    else:
        mixing_style = "**QUICK CUT или ECHO OUT** - сложный переход"
        bars = "16 бар или меньше"

    technique.append(f"\n🎚️  **Рекомендация:** {mixing_style}")
    technique.append(f"⏱️  **Длительность перехода:** {bars}")

    return "\n".join(technique)


def generate_transition_guide(tracks):
    """Генерация полного гайда по переходам"""
    guide = []
    guide.append("=" * 100)
    guide.append("🎛️  DETAILED TRANSITION GUIDE")
    guide.append("=" * 100)
    guide.append("")
    guide.append("Этот гайд содержит детальные рекомендации по переходам между каждой парой треков.")
    guide.append("Используйте его для планирования и практики вашего DJ сета.")
    guide.append("")
    guide.append("=" * 100)
    guide.append("")

    for i in range(len(tracks) - 1):
        track_a = tracks[i]
        track_b = tracks[i + 1]

        guide.append(f"\n{'─' * 100}")
        guide.append(f"ПЕРЕХОД #{i+1}: Track {track_a['position']:02d} → Track {track_b['position']:02d}")
        guide.append(f"{'─' * 100}")
        guide.append("")

        # Track A info
        guide.append(f"🎵 TRACK A (OUTGOING):")
        guide.append(f"   {track_a['artist']} - {track_a['title']}")
        guide.append(f"   BPM: {track_a.get('bpm', 'N/A')} | Key: {track_a.get('key', 'N/A')} ({track_a.get('camelot', 'N/A')})")
        guide.append(f"   Energy: {track_a.get('energy', 'N/A')}/10 ({track_a.get('energy_category', 'N/A')})")
        guide.append(f"   Genre: {track_a.get('genre', 'N/A')}")
        guide.append("")

        # Track B info
        guide.append(f"🎵 TRACK B (INCOMING):")
        guide.append(f"   {track_b['artist']} - {track_b['title']}")
        guide.append(f"   BPM: {track_b.get('bpm', 'N/A')} | Key: {track_b.get('key', 'N/A')} ({track_b.get('camelot', 'N/A')})")
        guide.append(f"   Energy: {track_b.get('energy', 'N/A')}/10 ({track_b.get('energy_category', 'N/A')})")
        guide.append(f"   Genre: {track_b.get('genre', 'N/A')}")
        guide.append("")

        # Transition technique
        guide.append("🎚️  РЕКОМЕНДАЦИИ ПО МИКШИРОВАНИЮ:")
        guide.append("")
        technique = recommend_transition_technique(track_a, track_b)
        guide.append(technique)
        guide.append("")

    guide.append("\n" + "=" * 100)
    guide.append("📝 LEGEND")
    guide.append("=" * 100)
    guide.append("")
    guide.append("**BPM Match Quality:**")
    guide.append("  ⚡ Perfect (0 BPM diff) - длинный плавный переход")
    guide.append("  ⚡ Good (1-2 BPM diff) - стандартный переход")
    guide.append("  ⚠️  Moderate (3-4 BPM diff) - требует внимания")
    guide.append("  🔴 Challenging (5+ BPM diff) - сложный переход")
    guide.append("")
    guide.append("**Key Match Quality:**")
    guide.append("  🎹 Perfect - тот же ключ")
    guide.append("  🎹 Excellent - ±1 на Camelot Wheel")
    guide.append("  🎹 Good - Major/Minor switch")
    guide.append("  ⚠️  Moderate - ±2 или другие комбинации")
    guide.append("  🔴 Challenging - требует осторожности")
    guide.append("")
    guide.append("**Mixing Techniques:**")
    guide.append("  • Bass Swap - обмен басами между треками")
    guide.append("  • EQ Mixing - постепенная замена частот")
    guide.append("  • Echo Out - fade out с эхо/reverb")
    guide.append("  • Hard Cut - резкий переход (на downbeat)")
    guide.append("")
    guide.append("=" * 100)

    return "\n".join(guide)


# ============================================================================
# MAIN
# ============================================================================

logger.info("=" * 70)
logger.info("📖 TRANSITION GUIDE GENERATION")
logger.info("=" * 70)

# Загрузка метаданных
logger.info(f"\n📋 Загрузка метаданных из {METADATA_FILE}...")
with open(METADATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)
    tracks = data['tracks']

logger.info(f"✓ Загружено {len(tracks)} треков\n")

# Генерация гайда
logger.info("📝 Генерация transition guide...")
guide_content = generate_transition_guide(tracks)

# Сохранение
guide_file = DJ_SET_DIR / "transition_guide.txt"
with open(guide_file, 'w', encoding='utf-8') as f:
    f.write(guide_content)

logger.info(f"✓ Transition guide сохранен: {guide_file}")
logger.info(f"   Размер: {len(guide_content)} символов")
logger.info(f"   Переходов: {len(tracks) - 1}")

# Preview первого перехода
logger.info("\n" + "=" * 70)
logger.info("PREVIEW: Первый переход")
logger.info("=" * 70)
if len(tracks) >= 2:
    preview = recommend_transition_technique(tracks[0], tracks[1])
    print(f"\n{tracks[0]['artist']} - {tracks[0]['title']}")
    print("  →")
    print(f"{tracks[1]['artist']} - {tracks[1]['title']}\n")
    print(preview)

logger.info("\n✨ Готово!")
logger.info(f"📖 Откройте {guide_file} для детального изучения всех переходов")
