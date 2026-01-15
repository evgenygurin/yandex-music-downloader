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
