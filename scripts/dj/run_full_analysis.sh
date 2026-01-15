#!/bin/bash
# Полный анализ DJ-сета: от аудио до transition guide
#
# Использование:
#   ./run_full_analysis.sh

# Активация виртуального окружения
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Виртуальное окружение активировано"
else
    echo "⚠️  Виртуальное окружение не найдено, используется системный Python"
fi

echo "════════════════════════════════════════════════════════════════"
echo "🎛️  FULL DJ SET ANALYSIS PIPELINE"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Проверка наличия metadata
if [ ! -f "dj_set_techno_2025/tracklist_metadata.json" ]; then
    echo "❌ Метаданные не найдены!"
    echo "   Сначала запустите: python prepare_dj_set.py <TOKEN>"
    exit 1
fi

echo "📋 Найдены метаданные треков"
echo ""

# 1. Анализ аудио (BPM + Key)
echo "─────────────────────────────────────────────────────────────────"
echo "ШАГ 1/5: Анализ BPM и Key (это займет ~5-10 минут)"
echo "─────────────────────────────────────────────────────────────────"
python analyze_audio.py
if [ $? -ne 0 ]; then
    echo "❌ Ошибка при анализе аудио"
    exit 1
fi
echo ""

# 2. Расчет Energy Level
echo "─────────────────────────────────────────────────────────────────"
echo "ШАГ 2/5: Расчет Energy Level"
echo "─────────────────────────────────────────────────────────────────"
python calculate_energy.py
if [ $? -ne 0 ]; then
    echo "❌ Ошибка при расчете энергии"
    exit 1
fi
echo ""

# 3. Генерация Camelot-сортированных вариаций
echo "─────────────────────────────────────────────────────────────────"
echo "ШАГ 3/5: Генерация гармонических вариаций"
echo "─────────────────────────────────────────────────────────────────"
python reorder_by_camelot.py
if [ $? -ne 0 ]; then
    echo "❌ Ошибка при создании Camelot sets"
    exit 1
fi
echo ""

# 4. Генерация Transition Guide
echo "─────────────────────────────────────────────────────────────────"
echo "ШАГ 4/5: Генерация Transition Guide"
echo "─────────────────────────────────────────────────────────────────"
python generate_transition_guide.py
if [ $? -ne 0 ]; then
    echo "❌ Ошибка при генерации гайда"
    exit 1
fi
echo ""

# 5. Обновление M3U8
echo "─────────────────────────────────────────────────────────────────"
echo "ШАГ 5/5: Обновление M3U8 с расширенными метаданными"
echo "─────────────────────────────────────────────────────────────────"
python update_m3u8_extended.py
if [ $? -ne 0 ]; then
    echo "❌ Ошибка при обновлении M3U8"
    exit 1
fi
echo ""

# Финальный отчет
echo "════════════════════════════════════════════════════════════════"
echo "✨ АНАЛИЗ ЗАВЕРШЕН!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📂 Результаты в директории: dj_set_techno_2025/"
echo ""
echo "Созданные файлы:"
echo "  📝 tracklist_metadata.json       - Полные метаданные"
echo "  🎵 techno_2025_extended.m3u8     - Плейлист для DJ софта"
echo "  📊 energy_flow_visualization.txt - Визуализация энергии"
echo "  📖 transition_guide.txt          - Детальный гайд по переходам"
echo "  📁 harmonic_sets/                - 3 вариации сета по Camelot"
echo "     ├── progressive/              - Progressive journey"
echo "     ├── plateau/                  - Plateau mixing"
echo "     └── journey/                  - Harmonic journey"
echo ""
echo "🎛️  Готово к импорту в:"
echo "  • djay Pro (Algoriddim)"
echo "  • Rekordbox (Pioneer DJ)"
echo "  • Traktor Pro (Native Instruments)"
echo "  • Serato DJ Pro"
echo ""
echo "════════════════════════════════════════════════════════════════"
