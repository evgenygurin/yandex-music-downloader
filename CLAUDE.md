# Yandex Music Downloader & DJ AI Studio

AI-powered DJ platform built on top of yandex-music-downloader with audio analysis capabilities.

## Quick Reference

**Build & Test:**
```bash
uv sync --all-packages      # Install Python deps
pnpm install                # Install Node deps
uv run pytest -v            # Run all tests
uv run ruff check .         # Lint
uv run ruff format .        # Format
uv run pyright              # Type check
```

**Run Services:**
```bash
uv run uvicorn dj_ai_api.main:app --reload  # API server
cd apps/web && pnpm dev                      # Web app
uv run dj-ai-mcp                             # MCP server
```

## Architecture Overview

```
yandex-music-downloader/
├── packages/core/              # Core Python library (dj-ai-studio-core)
│   └── src/dj_ai_studio/
│       ├── models/             # Pydantic models (Track, Set, Playlist)
│       ├── db/                 # SQLAlchemy ORM + async (aiosqlite)
│       ├── analysis/           # Audio analysis (BPM, key, energy)
│       └── yandex/             # Yandex Music client
├── apps/
│   ├── api/                    # FastAPI backend (dj-ai-api)
│   ├── mcp/                    # MCP server for Claude Code
│   └── web/                    # Next.js 15 frontend
└── ymd/                        # Legacy CLI (yandex-music-downloader)
```

## Key Technologies

| Component | Stack |
|-----------|-------|
| **Python** | 3.12+, Pydantic 2.0, SQLAlchemy 2.0, FastAPI, librosa |
| **Database** | SQLite + aiosqlite, Alembic migrations |
| **Frontend** | Next.js 15, React 19, Tailwind CSS 4, shadcn/ui |
| **Testing** | pytest, pytest-asyncio, httpx |
| **Quality** | Ruff (lint+format), Pyright (types), pre-commit |

## Code Style

- **Line length:** 100 characters
- **Indentation:** 4 spaces (Python), 2 spaces (JS/TS)
- **Quotes:** Double quotes
- **Type hints:** Required for all functions
- **Async:** Use `async/await` for I/O operations
- **Naming:** PascalCase (classes), snake_case (functions/variables)

See @.claude/rules/code-style.md for detailed guidelines.

## Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - new feature
- `fix:` - bug fix
- `docs:` - documentation
- `test:` - tests
- `refactor:` - refactoring
- `chore:` - maintenance
- `ci:` - CI/CD changes

## Important Patterns

### Database Operations
```python
# Always use async session context
async with get_session_context() as session:
    result = await session.execute(select(TrackORM))
    tracks = result.scalars().all()
```

### API Endpoints
```python
# Use dependency injection
@router.get("/tracks")
async def list_tracks(session: DbSession, settings: AppSettings):
    ...
```

### Audio Analysis
```python
# Use AudioAnalyzer service
analyzer = AudioAnalyzer()
result = await analyzer.analyze_async(file_path)
# Returns: {"bpm": 128.0, "key": "Am", "camelot": "8A", "energy": 7.5}
```

## MCP Server Tools

8 tools for DJ operations:
- `search_tracks` - Search library by criteria
- `get_track` - Get track details
- `find_compatible_tracks` - Harmonic mixing suggestions
- `analyze_track` - Audio analysis
- `create_set` / `get_set` - DJ set management
- `add_track_to_set` - Add track to set
- `suggest_next_track` - AI mixing recommendations

## Testing

```bash
# Core tests (models, analysis)
uv run pytest packages/core/tests/ -v

# API tests (endpoints, CRUD)
uv run pytest apps/api/tests/ -v

# All tests
uv run pytest -v
```

Tests use in-memory SQLite for isolation. See @.claude/rules/testing.md for patterns.

## Related Documentation

- @README.md - Project overview
- @CONTRIBUTING.md - Development guide
- @docs/dj/HARMONIC_MIXING_GUIDE.md - Camelot wheel reference
- @docs/plans/ - Architecture design documents
