# 🎛️ Профессиональный DJ Setup для Techno/House

Полный набор инструментов для создания гармоничных DJ-сетов с использованием Camelot Wheel, Energy Level системы и продвинутых техник микширования.

## 📚 Что включено

### 1. **Анализ аудио** (analyze_audio.py)
- ✅ BPM detection (optimized for techno: 120-140 BPM)
- ✅ Key detection с Camelot Wheel маппингом
- ✅ Confidence threshold (предупреждение при уверенности < 0.7)
- ✅ Улучшенные алгоритмы (3 минуты анализа, start_bpm=125)

### 2. **Energy Level система** (calculate_energy.py)
- ✅ Расчет энергии треков (1-10 шкала)
- ✅ Учет BPM, loudness, genre, key (major/minor)
- ✅ Категоризация: Warm-up → Building → Peak Time → Climax
- ✅ ASCII визуализация energy flow
- ✅ Set structure analysis по фазам

### 3. **Harmonic Reordering** (reorder_by_camelot.py)
- ✅ 3 варианта сета:
  - **Progressive Journey** - постепенное нарастание энергии
  - **Plateau Mix** - длинные блоки в одном ключе
  - **Harmonic Journey** - разнообразие с гармонией
- ✅ Автоматический расчет compatibility score
- ✅ Оптимизация переходов по Camelot Wheel

### 4. **Transition Guide** (generate_transition_guide.py)
- ✅ Детальные рекомендации для каждого перехода
- ✅ Анализ BPM/Key совместимости
- ✅ Предложения техник микширования:
  - Bass Swap Mixing
  - EQ Mixing
  - Echo Out / Hard Cut
- ✅ Рекомендуемая длительность переходов (16-96 бар)

### 5. **Extended M3U8** (update_m3u8_extended.py)
- ✅ Совместимость с djay Pro, Rekordbox, Traktor, Serato
- ✅ Расширенные теги:
  - `#EXTBPM`, `#EXTKEY`, `#EXTCAMELOT`
  - `#EXTENERGY`, `#EXTENERGYCATEGORY`
  - `#EXTLOUDNESS`, `#EXTLABEL`, `#EXTKEYCONFIDENCE`

---

## 🚀 Быстрый старт

### Шаг 1: Подготовка треков

```bash
# 1. Скачайте плейлист (если еще не сделали)
yandex-music-downloader \
  --token "YOUR_TOKEN" \
  --playlist-id "250905515/1113" \
  --quality 2 \
  --dir ./music_download

# 2. Переименуйте в порядке плейлиста
python reorder_playlist.py "YOUR_TOKEN"

# 3. Соберите метаданные из Yandex Music API
python prepare_dj_set.py "YOUR_TOKEN"
```

### Шаг 2: Полный анализ (один скрипт)

```bash
# Запуск всего pipeline (5-10 минут)
./run_full_analysis.sh
```

Или пошагово:

```bash
# 2.1. Анализ BPM + Key (5-10 минут)
python analyze_audio.py

# 2.2. Расчет Energy Level
python calculate_energy.py

# 2.3. Генерация harmonic вариаций
python reorder_by_camelot.py

# 2.4. Transition guide
python generate_transition_guide.py

# 2.5. Обновление M3U8
python update_m3u8_extended.py
```

### Шаг 3: Импорт в DJ софт

**djay Pro (Algoriddim):**
1. File → Import Playlist → `techno_2025_extended.m3u8`
2. Включите Neural Mix™ для stem separation
3. Camelot коды отобразятся автоматически

**Rekordbox (Pioneer DJ):**
1. File → Import → Playlist
2. Выберите `techno_2025_extended.m3u8`
3. BPM/Key будут импортированы

**Traktor Pro / Serato:**
1. Drag & Drop M3U8 в плейлист
2. Метаданные подхватятся автоматически

---

## 📊 Результаты

После полного анализа вы получите:

```text
dj_set_techno_2025/
├── 01 - Christian Craken - Instinct.m4a
├── 02 - Pęku - By My Side.m4a
├── ...
├── 50 - Etapp Kyle - Void.m4a
│
├── tracklist_metadata.json              # Полные метаданные
├── techno_2025_extended.m3u8            # Extended M3U8
├── energy_flow_visualization.txt        # ASCII визуализация
├── transition_guide.txt                 # Детальный гайд
│
└── harmonic_sets/                       # 3 вариации сета
    ├── progressive/
    │   ├── progressive.m3u8
    │   └── progressive_tracklist.txt
    ├── plateau/
    │   ├── plateau.m3u8
    │   └── plateau_tracklist.txt
    └── journey/
        ├── journey.m3u8
        └── journey_tracklist.txt
```

---

## 🎹 Camelot Wheel - Правила

### Основные переходы:

| Переход | Эффект | Качество |
|---------|--------|----------|
| 8A → 8A | Идеальный матч | ⭐⭐⭐⭐⭐ |
| 8A → 9A | Energy boost (+1) | ⭐⭐⭐⭐⭐ |
| 8A → 7A | Energy decrease (-1) | ⭐⭐⭐⭐ |
| 8A → 8B | Major/Minor switch | ⭐⭐⭐⭐ |
| 8A → 10A | Драматический переход | ⭐⭐⭐ |
| 8A → 3A | Сложный переход | ⭐⭐ |

### Стратегии:

**Progressive Journey:**
```text
4A @ 120 BPM (Warm-up)
  ↓
6A @ 123 BPM (Building)
  ↓
8A @ 126 BPM (Peak Time)
  ↓
10A @ 129 BPM (Climax)
```

**Plateau Mix:**
```text
8A @ 123 BPM (Track 1)
  ↓
8A @ 125 BPM (Track 2)
  ↓
8A @ 127 BPM (Track 3)
  ↓
8B @ 129 BPM (Energy boost через major)
```

---

## 🎚️ Техники микширования

### 1. Bass Swap Mixing
**Когда:** Perfect key match + BPM ≤ 2

```text
Track A: Full mix → Bass OUT (EQ Low -∞)
          ↓
Track B: Bass IN (EQ Low +0dB) → Full mix

Длительность: 64-96 бар
```

### 2. EQ Mixing
**Когда:** Good key match + BPM ≤ 4

```text
00:00-16: Track A full, Track B intro (highs only)
16:32:    Gradually swap mids
32:48:    Swap bass
48:64:    Track A out, Track B full

Длительность: 32-48 бар
```

### 3. Echo Out / Hard Cut
**Когда:** Challenging transition + BPM > 4

```text
Track A: Add reverb/delay → Fade out
          ↓
Track B: Hard drop on downbeat (bar 1)

Длительность: 8-16 бар
```

---

## ⚡ Energy Level система

### Категории (1-10):

| Energy | Категория | BPM | Применение |
|--------|-----------|-----|------------|
| 1-3 | Warm-up | 117-122 | Открытие, deep intro |
| 4-5 | Building | 123-125 | Постепенное нарастание |
| 6-7 | Peak Time | 126-128 | Prime time, танцпол |
| 8-9 | Climax | 129-132 | Кульминация |
| 10 | Hard Peak | 133+ | Финал, hard techno |

### Структура 90-минутного сета:

```text
00-20 min: Warm-up (Energy 3-4)
20-40 min: Building (Energy 5-6)
40-60 min: Peak Time (Energy 7-8)
60-75 min: Climax (Energy 9-10)
75-90 min: Cool-down (Energy 6-4)
```

---

## 🔥 Анализ вашего сета "Techno 2025"

### Статистика:

- **Треков:** 50
- **Длительность:** ~4.9 часа
- **BPM range:** 117.5 - 136.0 (средний: 124.7)
- **Жанры:**
  - Techno: 19 треков (38%)
  - House: 13 треков (26%)
  - Dance: 11 треков (22%)
  - Electronics: 7 треков (14%)

### BPM кластеры:

- **123 BPM** - 34 трека (идеально для minimal/tech house)
- **129 BPM** - 13 треков (progressive techno)
- **117.5 BPM** - 2 трека (deep intro/outro)
- **136 BPM** - 1 трек (peak moment)

### Рекомендуемая структура:

```text
WARM-UP (0-15 min):
  HilalDeep - Anonim (117.5 BPM, 8A)
  Cable - Cold Lake (117.5 BPM)

BUILDING (15-35 min):
  Christian Craken - Instinct (123 BPM, 4A)
  Kakoon - Skylight (123 BPM)
  Collective States - Resurrection (123 BPM)

PEAK TIME (35-60 min):
  Pęku - By My Side (129 BPM, 6A)
  APHE - Tempo (129 BPM, 10B)
  Alessandro Spaiani - Collision (129 BPM, 9B)

CLIMAX (60-75 min):
  Phoenix Movement - Drift (136 BPM) ← PEAK!
  MARK MICHAEL - Dilation (129 BPM)

COOL-DOWN (75-90 min):
  Bendtsen - Deeper (123 BPM)
  Cable - Cold Lake (117.5 BPM)
```

---

## 📖 Дополнительные ресурсы

### Harmonic Mixing:
- Mixed In Key - официальный софт
- Camelot Wheel interactive trainer
- HowToMix.org - уроки

### Техно/хаус техники:
- DJ TechTools - tutorials
- Point Blank Music School
- Resident Advisor features

### Софт:
- **djay Pro** (Algoriddim) - AI stems, Neural Mix™
- **Rekordbox** (Pioneer DJ) - industry standard
- **Traktor Pro** (Native Instruments) - advanced features
- **Serato DJ Pro** - надежный выбор

---

## ❓ FAQ

**Q: Почему у некоторых треков нет Key?**
A: Формат M4A иногда вызывает проблемы с essentia. Попробуйте конвертировать в WAV для анализа.

**Q: Confidence < 0.7 - это плохо?**
A: Предупреждение. Проверьте key вручную в Mixed In Key или другом софте.

**Q: Как использовать harmonic_sets/?**
A: Это готовые вариации с оптимизированным порядком треков. Импортируйте M3U8 из нужной вариации.

**Q: Можно ли редактировать energy levels вручную?**
A: Да! Откройте `tracklist_metadata.json` и измените поле `"energy"` для любого трека.

**Q: Как добавить stems в микс?**
A: Используйте djay Pro с Neural Mix™ или отдельные инструменты типа Spleeter/Demucs для pre-processing.

---

## 🎉 Итого

Вы получили:

✅ **Профессиональный анализ** - BPM, Key, Energy для всех треков
✅ **3 готовых сета** - Progressive, Plateau, Journey
✅ **Детальный transition guide** - техники для каждого перехода
✅ **Визуализацию энергии** - ASCII graph и set structure analysis
✅ **Extended M3U8** - готов к импорту в любой DJ софт

**Следующие шаги:**
1. Изучите `transition_guide.txt` - практикуйте переходы
2. Импортируйте `harmonic_sets/progressive/progressive.m3u8` в djay Pro
3. Практикуйте bass swaps на парах с perfect key match
4. Экспериментируйте с stems (vocals/drums) для creative transitions
5. Записывайте миксы и анализируйте energy flow

---

## 📞 Поддержка

Вопросы? Проблемы?

- GitHub Issues: `yandex-music-downloader`
- DJ форумы: djforums.com, reddit.com/r/DJs
- YouTube tutorials: DJ TechTools, Crossfader

**Happy mixing! 🎧**

---

*Создано с помощью Yandex Music Downloader + Professional DJ Tools*
*Совместимо с: djay Pro, Rekordbox, Traktor, Serato*
