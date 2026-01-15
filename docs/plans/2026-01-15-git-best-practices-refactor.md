# Git Repository Best Practices Refactor

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Рефакторинг проекта yandex-music-downloader для соответствия лучшим практикам Git-репозиториев.

**Architecture:** Реорганизация структуры проекта по стандарту Python (flat layout с отдельными директориями для docs, tests, scripts). Добавление CI/CD, линтинга, и стандартных файлов сообщества.

**Tech Stack:** Python 3.9+, pyproject.toml, ruff, pytest, GitHub Actions, pre-commit

---

## Текущие проблемы

| Проблема | Описание |
|----------|----------|
| Отсутствие тестов | Нет директории `tests/`, нет unit-тестов |
| Документация в корне | 5 markdown-файлов в корне вместо `docs/` |
| DJ-скрипты в корне | 13 Python-скриптов для DJ-анализа в корне |
| Неполный pyproject.toml | Нет конфигурации для ruff, pytest, mypy |
| Нет CI/CD | Отсутствует GitHub Actions workflow |
| Нет pre-commit | Отсутствует автоматическая проверка стиля |
| .egg-info в репо | Артефакты сборки не в .gitignore |

## Целевая структура

```text
yandex-music-downloader/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   ├── dj/
│   │   ├── DJAY_PRO_AI_GUIDE.md
│   │   ├── DJ_SETUP_README.md
│   │   ├── DJ_TOOLS_README.md
│   │   ├── HARMONIC_MIXING_GUIDE.md
│   │   └── PLAYLIST_VALIDATION_README.md
│   └── plans/
│       └── ...
├── scripts/
│   └── dj/
│       ├── analyze_audio.py
│       ├── calculate_energy.py
│       ├── generate_transition_guide.py
│       ├── inspect_track_metadata.py
│       ├── key_detector.py
│       ├── optimize_playlist.py
│       ├── prepare_dj_set.py
│       ├── recommend_tracks.py
│       ├── reorder_by_camelot.py
│       ├── reorder_playlist.py
│       ├── run_full_analysis.sh
│       ├── update_m3u8_extended.py
│       ├── validate_playlist.py
│       └── write_id3_tags.py
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── test_api.py
├── ymd/
│   ├── __init__.py
│   ├── __main__.py
│   ├── api.py
│   ├── cli.py
│   ├── core.py
│   └── mime_utils.py
├── .gitignore
├── .pre-commit-config.yaml
├── CONTRIBUTING.md
├── LICENSE
├── MIGRATION.md
├── pyproject.toml
├── README.md
└── uv.lock
```

---

## Task 1: Обновить .gitignore

**Files:**
- Modify: `.gitignore`

**Step 1: Прочитать текущий .gitignore**

Текущий файл уже хороший, нужно добавить несколько паттернов.

**Step 2: Добавить дополнительные паттерны**

```gitignore
# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
*.egg-info/
.ruff_cache/
```

**Step 3: Удалить закомментированные опциональные паттерны**

Убрать неиспользуемые секции (poetry.lock, pdm.lock комментарии).

**Step 4: Commit**

```bash
git add .gitignore
git commit -m "chore: update .gitignore with IDE and modern Python patterns

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Удалить .egg-info из репозитория

**Files:**
- Delete: `yandex_music_downloader.egg-info/`

**Step 1: Удалить директорию из git**

```bash
git rm -r yandex_music_downloader.egg-info/
```

**Step 2: Проверить что .gitignore игнорирует *.egg-info**

```bash
grep "egg-info" .gitignore
```
Expected: `*.egg-info/`

**Step 3: Commit**

```bash
git commit -m "chore: remove egg-info build artifacts from repository

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Создать структуру docs/

**Files:**
- Create: `docs/dj/`
- Move: `DJAY_PRO_AI_GUIDE.md` → `docs/dj/`
- Move: `DJ_SETUP_README.md` → `docs/dj/`
- Move: `DJ_TOOLS_README.md` → `docs/dj/`
- Move: `HARMONIC_MIXING_GUIDE.md` → `docs/dj/`
- Move: `PLAYLIST_VALIDATION_README.md` → `docs/dj/`

**Step 1: Создать директорию**

```bash
mkdir -p docs/dj
```

**Step 2: Переместить файлы**

```bash
git mv DJAY_PRO_AI_GUIDE.md docs/dj/
git mv DJ_SETUP_README.md docs/dj/
git mv DJ_TOOLS_README.md docs/dj/
git mv HARMONIC_MIXING_GUIDE.md docs/dj/
git mv PLAYLIST_VALIDATION_README.md docs/dj/
```

**Step 3: Commit**

```bash
git commit -m "docs: move DJ documentation to docs/dj/

Organize documentation files into proper directory structure.
- DJAY_PRO_AI_GUIDE.md
- DJ_SETUP_README.md
- DJ_TOOLS_README.md
- HARMONIC_MIXING_GUIDE.md
- PLAYLIST_VALIDATION_README.md

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Создать структуру scripts/dj/

**Files:**
- Create: `scripts/dj/`
- Move: All DJ Python scripts

**Step 1: Создать директорию**

```bash
mkdir -p scripts/dj
```

**Step 2: Переместить Python скрипты**

```bash
git mv analyze_audio.py scripts/dj/
git mv calculate_energy.py scripts/dj/
git mv generate_transition_guide.py scripts/dj/
git mv inspect_track_metadata.py scripts/dj/
git mv key_detector.py scripts/dj/
git mv optimize_playlist.py scripts/dj/
git mv prepare_dj_set.py scripts/dj/
git mv recommend_tracks.py scripts/dj/
git mv reorder_by_camelot.py scripts/dj/
git mv reorder_playlist.py scripts/dj/
git mv update_m3u8_extended.py scripts/dj/
git mv validate_playlist.py scripts/dj/
git mv write_id3_tags.py scripts/dj/
```

**Step 3: Переместить shell скрипт**

```bash
git mv run_full_analysis.sh scripts/dj/
```

**Step 4: Обновить импорты в скриптах (если есть относительные)**

Проверить `analyze_audio.py` - он импортирует `key_detector`:
```python
from key_detector import detect_key
```
Нужно изменить на:
```python
from scripts.dj.key_detector import detect_key
```
Или лучше - сделать относительный импорт в той же директории.

**Step 5: Commit**

```bash
git commit -m "refactor: move DJ scripts to scripts/dj/

Organize DJ-related utilities into dedicated directory:
- Audio analysis scripts (BPM, key detection)
- Playlist management tools
- Track recommendation utilities

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Расширить pyproject.toml

**Files:**
- Modify: `pyproject.toml`

**Step 1: Добавить метаданные проекта**

```toml
[project]
name = "yandex-music-downloader"
version = "3.5.4"
description = "Загрузчик музыки с сервиса Яндекс.Музыка"
requires-python = ">=3.9"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "llistochek"}
]
keywords = ["yandex", "music", "downloader", "audio"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Multimedia :: Sound/Audio",
]
dependencies = [
    "yandex-music @ https://github.com/llistochek/yandex-music-api/archive/9623fbca7704f47766614efe51d66c9fd496714c.zip",
    "mutagen>=1.47.0",
    "StrEnum",
    "pycryptodome"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
    "pre-commit>=3.0",
]

[project.urls]
Homepage = "https://github.com/llistochek/yandex-music-downloader"
Repository = "https://github.com/llistochek/yandex-music-downloader"
Issues = "https://github.com/llistochek/yandex-music-downloader/issues"
```

**Step 2: Добавить конфигурацию ruff**

```toml
[tool.ruff]
target-version = "py39"
line-length = 100
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort
    "B",     # flake8-bugbear
    "C4",    # flake8-comprehensions
    "UP",    # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

**Step 3: Добавить конфигурацию pytest**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

**Step 4: Добавить конфигурацию mypy**

```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_ignores = true
ignore_missing_imports = true
```

**Step 5: Commit**

```bash
git add pyproject.toml
git commit -m "build: extend pyproject.toml with dev tools config

Add configurations for:
- Project metadata and classifiers
- Optional dev dependencies (pytest, ruff, mypy, pre-commit)
- Ruff linting rules
- Pytest settings
- Mypy type checking

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Добавить pre-commit конфигурацию

**Files:**
- Create: `.pre-commit-config.yaml`

**Step 1: Создать файл конфигурации**

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
        args: [--ignore-missing-imports]
```

**Step 2: Commit**

```bash
git add .pre-commit-config.yaml
git commit -m "ci: add pre-commit configuration

Configure pre-commit hooks:
- Basic file checks (trailing whitespace, EOF, YAML, merge conflicts)
- Ruff linting and formatting
- Mypy type checking

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Создать базовую структуру tests/

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_core.py`

**Step 1: Создать директорию и __init__.py**

```bash
mkdir -p tests
touch tests/__init__.py
```

**Step 2: Создать test_core.py с базовыми тестами**

```python
"""Tests for ymd.core module."""

import pytest
from pathlib import Path

from ymd.core import (
    CoreTrackQuality,
    LyricsFormat,
    full_title,
    DEFAULT_PATH_PATTERN,
    MIN_COMPATIBILITY_LEVEL,
    MAX_COMPATIBILITY_LEVEL,
)

class TestCoreTrackQuality:
    """Tests for CoreTrackQuality enum."""

    def test_quality_values(self):
        """Test that quality enum has expected values."""
        assert CoreTrackQuality.LOW == 0
        assert CoreTrackQuality.NORMAL == 1
        assert CoreTrackQuality.LOSSLESS == 2

    def test_quality_ordering(self):
        """Test that qualities are ordered correctly."""
        assert CoreTrackQuality.LOW < CoreTrackQuality.NORMAL
        assert CoreTrackQuality.NORMAL < CoreTrackQuality.LOSSLESS

class TestLyricsFormat:
    """Tests for LyricsFormat enum."""

    def test_lyrics_format_values(self):
        """Test that lyrics format enum has expected string values."""
        assert str(LyricsFormat.NONE) == "none"
        assert str(LyricsFormat.TEXT) == "text"
        assert str(LyricsFormat.LRC) == "lrc"

class TestConstants:
    """Tests for module constants."""

    def test_default_path_pattern(self):
        """Test default path pattern is valid."""
        assert isinstance(DEFAULT_PATH_PATTERN, Path)
        pattern_str = str(DEFAULT_PATH_PATTERN)
        assert "#album-artist" in pattern_str
        assert "#album" in pattern_str
        assert "#title" in pattern_str

    def test_compatibility_levels(self):
        """Test compatibility level bounds."""
        assert MIN_COMPATIBILITY_LEVEL == 0
        assert MAX_COMPATIBILITY_LEVEL == 1
        assert MIN_COMPATIBILITY_LEVEL <= MAX_COMPATIBILITY_LEVEL

class TestFullTitle:
    """Tests for full_title function."""

    def test_full_title_simple(self):
        """Test full_title with simple title."""
        # Mock object with title only
        class MockTrack:
            def __getitem__(self, key):
                if key == "title":
                    return "Song Name"
                return None

        result = full_title(MockTrack())
        assert result == "Song Name"

    def test_full_title_with_version(self):
        """Test full_title with version."""
        class MockTrack:
            def __getitem__(self, key):
                if key == "title":
                    return "Song Name"
                if key == "version":
                    return "Remix"
                return None

        result = full_title(MockTrack())
        assert result == "Song Name (Remix)"

    def test_full_title_none(self):
        """Test full_title with None title."""
        class MockTrack:
            def __getitem__(self, key):
                return None

        result = full_title(MockTrack())
        assert result == ""
```

**Step 3: Run test to verify**

```bash
pytest tests/test_core.py -v
```
Expected: All tests PASS

**Step 4: Commit**

```bash
git add tests/
git commit -m "test: add initial test structure and core module tests

Add tests directory with basic tests for:
- CoreTrackQuality enum values and ordering
- LyricsFormat enum string values
- Module constants (path pattern, compatibility levels)
- full_title function behavior

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Добавить GitHub Actions CI

**Files:**
- Create: `.github/workflows/ci.yml`

**Step 1: Создать директорию**

```bash
mkdir -p .github/workflows
```

**Step 2: Создать CI workflow**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install ruff
        run: pip install ruff

      - name: Run ruff check
        run: ruff check .

      - name: Run ruff format check
        run: ruff format --check .

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests
        run: pytest tests/ -v --tb=short

  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install mypy types-requests
          pip install -e .

      - name: Run mypy
        run: mypy ymd/ --ignore-missing-imports
```

**Step 3: Commit**

```bash
git add .github/
git commit -m "ci: add GitHub Actions workflow

Configure CI pipeline with:
- Lint job (ruff check and format)
- Test job (pytest on Python 3.9-3.12)
- Type check job (mypy)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Добавить CONTRIBUTING.md

**Files:**
- Create: `CONTRIBUTING.md`

**Step 1: Создать файл**

```markdown
# Contributing to yandex-music-downloader

Спасибо за интерес к проекту! Ниже описаны рекомендации для контрибьюторов.

## Разработка

### Установка для разработки

```bash
# Клонировать репозиторий
git clone https://github.com/llistochek/yandex-music-downloader.git
cd yandex-music-downloader

# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или .venv\Scripts\activate  # Windows

# Установить зависимости для разработки
pip install -e ".[dev]"

# Установить pre-commit hooks
pre-commit install
```

### Запуск тестов

```bash
pytest tests/ -v
```

### Проверка стиля кода

```bash
# Линтинг
ruff check .

# Форматирование
ruff format .

# Проверка типов
mypy ymd/ --ignore-missing-imports
```

## Pull Requests

1. Форкните репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Сделайте изменения
4. Убедитесь что тесты проходят
5. Закоммитьте изменения (`git commit -m 'feat: add amazing feature'`)
6. Запушьте в branch (`git push origin feature/amazing-feature`)
7. Откройте Pull Request

### Формат коммитов

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - новая функциональность
- `fix:` - исправление бага
- `docs:` - изменения документации
- `test:` - добавление/изменение тестов
- `refactor:` - рефакторинг кода
- `chore:` - обслуживание проекта
- `ci:` - изменения CI/CD

## Сообщения об ошибках

При создании issue укажите:
- Версию Python
- Операционную систему
- Команду которую выполняли
- Полный текст ошибки
```text

**Step 2: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs: add CONTRIBUTING.md

Add contributor guidelines with:
- Development setup instructions
- Testing and linting commands
- Pull request workflow
- Commit message format

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Обновить README.md

**Files:**
- Modify: `README.md`

**Step 1: Добавить badges в начало**

После заголовка добавить:

```markdown
[![CI](https://github.com/llistochek/yandex-music-downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/llistochek/yandex-music-downloader/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
```

**Step 2: Добавить секцию разработки**

Перед "Спасибо" добавить:

```markdown
## Разработка

См. [CONTRIBUTING.md](CONTRIBUTING.md) для информации о разработке и контрибуции.
```

**Step 3: Добавить ссылку на DJ-документацию**

```markdown
## DJ Tools

Для использования DJ-утилит (анализ BPM, тональности, создание плейлистов) см. документацию в [docs/dj/](docs/dj/).
```

**Step 4: Commit**

```bash
git add README.md
git commit -m "docs: update README with badges and references

Add:
- CI status badge
- Python version badge
- License badge
- Links to contributing guide and DJ docs

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Финальная очистка и проверка

**Files:**
- Various

**Step 1: Удалить дубликат venv директории**

```bash
rm -rf venv/  # Если .venv уже используется
```

**Step 2: Запустить все проверки**

```bash
# Линтинг
ruff check .

# Форматирование
ruff format --check .

# Тесты
pytest tests/ -v

# Типы
mypy ymd/ --ignore-missing-imports
```

**Step 3: Проверить структуру**

```bash
tree -L 3 -I '__pycache__|*.pyc|.venv|venv|.git|music_download|dj_set_techno_2025'
```

Expected:
```text
.
├── .github
│   └── workflows
│       └── ci.yml
├── .gitignore
├── .pre-commit-config.yaml
├── CONTRIBUTING.md
├── LICENSE
├── MIGRATION.md
├── README.md
├── docs
│   ├── dj
│   │   └── *.md
│   └── plans
│       └── *.md
├── pyproject.toml
├── scripts
│   └── dj
│       └── *.py
├── tests
│   ├── __init__.py
│   └── test_*.py
├── uv.lock
└── ymd
    └── *.py
```

**Step 4: Финальный коммит (если нужны дополнительные изменения)**

```bash
git status
# Если есть изменения:
git add .
git commit -m "chore: final cleanup after restructuring

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Резюме изменений

| До | После |
|----|-------|
| 13 Python скриптов в корне | `scripts/dj/` |
| 5 MD файлов в корне | `docs/dj/` |
| Нет тестов | `tests/` с базовыми тестами |
| Минимальный pyproject.toml | Полная конфигурация с ruff, pytest, mypy |
| Нет CI/CD | GitHub Actions workflow |
| Нет pre-commit | .pre-commit-config.yaml |
| Нет CONTRIBUTING.md | Полное руководство для контрибьюторов |
| .egg-info в репо | Удален, в .gitignore |

## Проверочный чеклист

- [ ] `.gitignore` обновлен
- [ ] `yandex_music_downloader.egg-info/` удален из git
- [ ] DJ документация в `docs/dj/`
- [ ] DJ скрипты в `scripts/dj/`
- [ ] `pyproject.toml` расширен
- [ ] `.pre-commit-config.yaml` создан
- [ ] `tests/` с базовыми тестами
- [ ] `.github/workflows/ci.yml` создан
- [ ] `CONTRIBUTING.md` создан
- [ ] `README.md` обновлен с badges
- [ ] Все проверки проходят (ruff, pytest, mypy)
