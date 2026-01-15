# 🎛️ Professional DJ Tools для Techno/House - Полный обзор

Комплексный набор инструментов для создания профессиональных DJ-сетов с harmonic mixing, energy flow analysis и AI-powered transitions.

---

## 📊 Результаты анализа

### ✅ 100% Coverage достигнут!

| Метрика | Значение | Статус |
|---------|----------|--------|
| **BPM Detection** | 50/50 (100%) | ✅ |
| **Key Detection** | 50/50 (100%) | ✅ |
| **Energy Level** | 50/50 (100%) | ✅ |
| **ID3 Tags** | 50/50 (100%) | ✅ |
| **Harmonic Sets** | 50 треков | ✅ |
| **Transition Guide** | 49 переходов | ✅ |
| **Playlist Quality** | 100% Pass Rate | ✅ |
| **Camelot Coverage** | 16/24 ключей (66.7%) | ⚠️ |

---

## 🔧 Созданные инструменты

### 1. **key_detector.py** - Pure Python Key Detection
```bash
python key_detector.py "audio_file.m4a"
```

**Возможности:**
- ✅ Работает БЕЗ C-компиляции (чистый Python + librosa)
- ✅ Алгоритм Krumhansl-Schmuckler
- ✅ Автоматический Camelot Wheel mapping
- ✅ Confidence scoring (0-1)

**Output:**
```text
Key: Fm (4A) - Confidence: 0.35
```

---

### 2. **analyze_audio.py** - BPM + Key Analysis
```bash
source venv/bin/activate
python analyze_audio.py
```

**Возможности:**
- ✅ Optimized BPM detection для techno (120-140 BPM)
- ✅ Key detection для всех треков (100% coverage)
- ✅ Confidence threshold warnings
- ✅ Запись в tracklist_metadata.json

**Технические детали:**
- librosa beat tracking: start_bpm=125, tightness=200
- Duration анализа: 3 минуты (180 sec)
- Chroma-based key detection

---

### 3. **calculate_energy.py** - Energy Level System
```bash
python calculate_energy.py
```

**Возможности:**
- ✅ Energy calculation (1-10 scale)
- ✅ Факторы: BPM (40%), Loudness (30%), Genre (20%), Key (10%)
- ✅ Категории: Warm-up, Building, Peak Time, Climax, Hard Peak
- ✅ ASCII visualization
- ✅ Set structure analysis

**Output:**
```text
01. Christian Craken | 6.3/10 ▅ (Peak Time)
    ███████████████████████████████████████
    Peak Time | 123 BPM | Fm | house
```

---

### 4. **reorder_by_camelot.py** - Harmonic Reordering
```bash
python reorder_by_camelot.py
```

**Возможности:**
- ✅ 3 стратегии микширования:
  - **Progressive**: постепенное нарастание энергии
  - **Plateau**: длинные блоки в одном ключе
  - **Journey**: разнообразие с гармонией
- ✅ Compatibility scoring (0-100)
- ✅ Camelot Wheel transitions
- ✅ Генерация M3U8 + TXT tracklists

**Output:**
```text
harmonic_sets/
├── progressive/
│   ├── progressive.m3u8
│   └── progressive_tracklist.txt
├── plateau/
└── journey/
```

---

### 5. **generate_transition_guide.py** - Transition Recommendations
```bash
python generate_transition_guide.py
```

**Возможности:**
- ✅ 49 детальных рекомендаций по переходам
- ✅ BPM/Key compatibility analysis
- ✅ Техники микширования:
  - Bass Swap Mixing (perfect matches)
  - EQ Mixing (good matches)
  - Echo Out / Hard Cut (challenging)
- ✅ Рекомендуемая длительность (16-96 бар)

**Output:**
```text
ПЕРЕХОД #7: Track 07 → Track 08
────────────────────────────────

TRACK A: Clap Codex - Overlord
  BPM: 123.0 | Key: Dm (7A)

TRACK B: APHE - Tempo
  BPM: 129.2 | Key: D (10B)

🔴 Большая BPM разница (Δ6.2)
🎚️ Рекомендация: QUICK CUT или ECHO OUT
⏱️ Длительность: 16 бар
```

---

### 6. **update_m3u8_extended.py** - Extended M3U8
```bash
python update_m3u8_extended.py
```

**Возможности:**
- ✅ Extended M3U8 tags:
  - #EXTBPM, #EXTKEY, #EXTCAMELOT
  - #EXTENERGY, #EXTENERGYCATEGORY
  - #EXTLOUDNESS, #EXTKEYCONFIDENCE
- ✅ Совместимость: djay Pro, Rekordbox, Traktor, Serato

**Output:**
```text
#EXTINF:339,Christian Craken - Instinct
#EXTGENRE:house
#EXTBPM:123.0
#EXTKEY:Fm
#EXTCAMELOT:4A
#EXTENERGY:6.3
#EXTKEYCONFIDENCE:0.35
01 - Christian Craken - Instinct.m4a
```

---

### 7. **write_id3_tags.py** - ID3 Tags Writer
```bash
python write_id3_tags.py
```

**Возможности:**
- ✅ Запись BPM, Key, OpenKey в аудиофайлы
- ✅ Поддержка M4A (Apple) и MP3 (ID3)
- ✅ Camelot → OpenKey конвертация для djay Pro
- ✅ Custom tags (Energy Level)

**Mapping:**
```text
Camelot 4A → OpenKey 9m (Fm)
Camelot 6A → OpenKey 11m (Gm)
Camelot 10B → OpenKey 3d (D)
```

---

### 8. **run_full_analysis.sh** - Automated Pipeline
```bash
./run_full_analysis.sh
```

**Возможности:**
- ✅ Полный pipeline за один запуск
- ✅ Error checking на каждом шаге
- ✅ Автоматическая активация venv
- ✅ Progress reporting

**Шаги:**
1. Analyze Audio (BPM + Key)
2. Calculate Energy
3. Reorder by Camelot
4. Generate Transition Guide
5. Update M3U8

---

### 9. **validate_playlist.py** - Валидация качества
```bash
python validate_playlist.py
```

**Возможности:**
- ✅ Комплексная валидация треков (BPM, Key, Energy, Duration)
- ✅ Camelot Wheel coverage analysis (16/24 ключей = 66.7%)
- ✅ Energy flow анализ (резкие скачки)
- ✅ Scoring system (0-100 для каждого трека)
- ✅ Автоматическая фильтрация проблемных треков

**Output:**
```text
📊 СТАТИСТИКА
✅ Excellent:  50/50 (100.0%)
Pass Rate: 100.0%

🎹 CAMELOT WHEEL
Покрытие: 16/24 ключей (66.7%)
Отсутствующие: 10A, 1B, 2A, 2B, 3A, 4B, 5A, 6B
```

---

### 10. **recommend_tracks.py** - Рекомендации треков
```bash
python recommend_tracks.py
```

**Возможности:**
- ✅ Анализ пробелов в Camelot Wheel
- ✅ Sparse BPM ranges detection
- ✅ Приоритизация рекомендаций (High/Medium/Low)
- ✅ Готовые поисковые запросы для каждого трека
- ✅ Сохранение в track_recommendations.json

**Output:**
```text
🔴 ВЫСОКИЙ ПРИОРИТЕТ:
  1. Отсутствующий ключ 10A (Cm)
     🔍 Поиск: "techno house Cm 117-136 BPM"

🟡 СРЕДНИЙ ПРИОРИТЕТ:
  1. Мало треков в 115-120 BPM, ключ 6A
```

---

### 11. **optimize_playlist.py** - Автоматическая оптимизация
```bash
python optimize_playlist.py
```

**Возможности:**
- ✅ Автоматическое создание backup
- ✅ Валидация и удаление проблемных треков
- ✅ Генерация оптимизированного M3U8
- ✅ Список отклоненных треков с причинами
- ✅ Готовый плейлист для djay Pro AI

**Output:**
```text
💾 Backup: tracklist_metadata_backup_20260103.json
📊 Приняты:   48/50 (96.0%)
    Отклонены:  2/50 (4.0%)

✓ techno_2025_optimized.m3u8
```

---

## 📁 Структура файлов

```text
yandex-music-downloader/
│
├── venv/                          # Виртуальное окружение
│
├── key_detector.py                # ⭐ Pure Python key detection
├── analyze_audio.py               # ⭐ BPM + Key analysis
├── calculate_energy.py            # ⭐ Energy Level system
├── reorder_by_camelot.py          # ⭐ Harmonic reordering
├── generate_transition_guide.py   # ⭐ Transition recommendations
├── update_m3u8_extended.py        # ⭐ Extended M3U8 generator
├── write_id3_tags.py              # ⭐ ID3 tags writer
├── run_full_analysis.sh           # ⭐ Automated pipeline
│
├── validate_playlist.py           # 🔍 Валидация качества треков
├── recommend_tracks.py            # 💡 Рекомендации для заполнения пробелов
├── optimize_playlist.py           # 🔄 Автоматическая оптимизация
│
├── HARMONIC_MIXING_GUIDE.md       # 📖 Теория harmonic mixing
├── DJAY_PRO_AI_GUIDE.md           # 📖 Инструкция для djay Pro AI
├── DJ_TOOLS_README.md             # 📖 Этот файл
├── PLAYLIST_VALIDATION_README.md  # 📖 Валидация и оптимизация
│
└── dj_set_techno_2025/
    ├── 01 - Christian Craken - Instinct.m4a    # 50 треков с ID3 tags
    ├── 02 - Pęku - By My Side.m4a
    ├── ...
    │
    ├── tracklist_metadata.json                 # Полные метаданные
    ├── techno_2025.m3u8                        # Стандартный M3U8
    ├── techno_2025_extended.m3u8               # Extended M3U8
    ├── transition_guide.txt                    # 49 переходов (72KB)
    ├── energy_flow_visualization.txt           # ASCII график
    │
    └── harmonic_sets/
        ├── progressive/
        │   ├── progressive.m3u8
        │   └── progressive_tracklist.txt
        ├── plateau/
        └── journey/
```

---

## 🚀 Quick Start

### 1. Первый запуск (Setup)
```bash
# Создание venv и установка зависимостей
python3 -m venv venv
source venv/bin/activate
pip install librosa mutagen
```

### 2. Полный анализ
```bash
# Запуск всего pipeline (5-10 минут)
./run_full_analysis.sh
```

### 3. Применение в djay Pro AI
```bash
# Открыть инструкцию
open DJAY_PRO_AI_GUIDE.md

# Импортировать в djay Pro AI:
# 1. Library → Import M3U8
# 2. Выбрать: dj_set_techno_2025/techno_2025.m3u8
# 3. Настроить: Settings → Key Format → OpenKey
# 4. Включить: Color Coding
```

---

## 🎯 Use Cases

### Use Case 1: Быстрый анализ плейлиста
```bash
source venv/bin/activate
python analyze_audio.py
python calculate_energy.py
python update_m3u8_extended.py
```

### Use Case 2: Создание harmonic сета
```bash
python reorder_by_camelot.py
# → 3 варианта в harmonic_sets/
```

### Use Case 3: Подготовка к live set
```bash
python generate_transition_guide.py
open dj_set_techno_2025/transition_guide.txt
# → Изучай переходы перед выступлением
```

### Use Case 4: Экспорт для DJ software
```bash
python write_id3_tags.py
# → BPM/Key записаны в файлы
# → Импорт в djay Pro / Rekordbox / Traktor
```

---

## 📊 Технические детали

### BPM Detection (librosa)
```python
librosa.beat.beat_track(
    y=audio,
    sr=sample_rate,
    start_bpm=125.0,      # Optimized для techno
    tightness=200         # High accuracy
)
```

### Key Detection (Krumhansl-Schmuckler)
```python
# 1. Extract chroma features
chroma = librosa.feature.chroma_cqt(y, sr)

# 2. Correlate с major/minor profiles
correlation = pearson(chroma_mean, key_profile)

# 3. Best match = detected key
```

### Energy Level Calculation
```python
energy = (
    bpm_score * 0.4 +
    loudness_score * 0.3 +
    genre_score * 0.2 +
    key_score * 0.1
)
```

### Camelot Wheel Transitions
```python
perfect_match = same_key
excellent = ±1 position
good = major_minor_switch
moderate = ±2 positions
challenging = other
```

---

## 🎹 Camelot Wheel Reference

```text
      12A ─── 12B
     /  \     /  \
   11A   1A 11B   1B
    |  X  |   |  X  |
   10A   2A 10B   2B
     \  /  |   \  /
      9A ─┼─ 9B
      |   |   |
      8A ─┼─ 8B
     /  \ |  /  \
    7A   3A 7B   3B
    |  X  |  |  X  |
    6A   4A 6B   4B
     \  /     \  /
      5A ─── 5B

Perfect: Same key
Excellent: ±1 (energy up/down)
Good: A ↔ B (mood change)
```

---

## 🔥 Pro Tips

### 1. Re-analysis треков
```bash
# Если обновили аудиофайлы:
rm dj_set_techno_2025/tracklist_metadata.json
./run_full_analysis.sh
```

### 2. Custom Energy Levels
```bash
# Отредактируй вручную:
nano dj_set_techno_2025/tracklist_metadata.json
# Измени "energy": 7.5 на нужное значение
python reorder_by_camelot.py  # Regenerate
```

### 3. Экспорт в другие форматы
```bash
# CSV для Excel/Spreadsheets:
python -c "
import json, csv
data = json.load(open('dj_set_techno_2025/tracklist_metadata.json'))
with open('tracklist.csv', 'w') as f:
    w = csv.DictWriter(f, fieldnames=['position', 'artist', 'title', 'bpm', 'key', 'energy'])
    w.writeheader()
    w.writerows(data['tracks'])
"
```

### 4. Filter по энергии
```bash
# Только high energy tracks (8+):
python -c "
import json
data = json.load(open('dj_set_techno_2025/tracklist_metadata.json'))
high_energy = [t for t in data['tracks'] if t.get('energy', 0) >= 8]
print(f'{len(high_energy)} tracks with energy >= 8')
for t in high_energy:
    print(f'{t[\"artist\"]} - {t[\"title\"]} | Energy: {t[\"energy\"]}')
"
```

---

## 🐛 Troubleshooting

### Проблема: librosa не устанавливается
```bash
# macOS:
brew install portaudio
pip install librosa

# Linux:
sudo apt-get install libportaudio2
pip install librosa
```

### Проблема: Key detection низкий confidence
```bash
# Используйте внешние tools:
# - Mixed In Key (commercial)
# - Rekordbox analysis
# Затем обновите metadata вручную
```

### Проблема: M4A не читается
```bash
# Установите audioread backend:
pip install audioread
# Или конвертируйте в WAV:
ffmpeg -i input.m4a output.wav
```

### Проблема: Harmonic sets пустые
```bash
# Проверьте key detection:
python -c "
import json
data = json.load(open('dj_set_techno_2025/tracklist_metadata.json'))
keys = [t for t in data['tracks'] if t.get('key')]
print(f'{len(keys)} tracks with key')
"
# Если < 10, re-run analyze_audio.py
```

---

## 📚 Документация

### Основные гайды:
- **HARMONIC_MIXING_GUIDE.md** - Теория Camelot Wheel, техники микширования
- **DJAY_PRO_AI_GUIDE.md** - Полная инструкция для djay Pro AI
- **DJ_TOOLS_README.md** - Этот файл (overview инструментов)

### Видео tutorials:
- DJ TechTools: https://djtechtools.com/
- Mixed In Key: https://mixedinkey.com/harmonic-mixing-guide/
- djay Pro AI: https://www.youtube.com/c/Algoriddim

---

## 🎉 Итого

**Вы получили:**

✅ **100% coverage** BPM + Key + Energy для всех треков
✅ **Pure Python** key detector (без C dependencies)
✅ **3 harmonic вариации** сета (Progressive, Plateau, Journey)
✅ **49 детальных transition guides** с техниками
✅ **ID3 tags** в аудиофайлах для DJ software
✅ **Energy flow visualization** для планирования сета
✅ **Extended M3U8** с полными метаданными
✅ **Полная совместимость** с djay Pro AI, Rekordbox, Traktor, Serato

**Следующий шаг:**

```bash
# 1. Импортируйте в djay Pro AI
open DJAY_PRO_AI_GUIDE.md

# 2. Изучите переходы
open dj_set_techno_2025/transition_guide.txt

# 3. Практикуйте!
```

---

## 🙏 Credits

**Tools:**
- librosa - BPM detection
- mutagen - ID3 tags
- Python 3.11+ - Core language

**Theory:**
- Krumhansl-Schmuckler algorithm (key detection)
- Camelot Wheel (Mixed In Key)
- Energy Level system (DJ methodology)

**Created with:**
- Yandex Music Downloader
- Professional DJ Tools
- Claude Code + Sonnet 4.5

---

**Happy mixing! 🎧✨**

*For support: check GitHub Issues or open HARMONIC_MIXING_GUIDE.md*
