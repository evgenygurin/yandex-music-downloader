---
paths:
  - "apps/api/**/*.py"
---

# FastAPI Backend Rules

## Project Structure

```
apps/api/
├── src/dj_ai_api/
│   ├── main.py          # App factory, lifespan, CORS
│   ├── config.py        # Pydantic Settings
│   ├── deps.py          # Dependency injection
│   └── routers/
│       ├── tracks.py    # /api/v1/tracks
│       ├── sets.py      # /api/v1/sets
│       ├── analysis.py  # /api/v1/analysis
│       └── yandex.py    # /api/v1/yandex
└── tests/
```

## Endpoint Conventions

### URL Patterns
```
GET    /api/v1/tracks           # List with filters
GET    /api/v1/tracks/{id}      # Get single
POST   /api/v1/tracks           # Create (201)
PATCH  /api/v1/tracks/{id}      # Partial update
DELETE /api/v1/tracks/{id}      # Delete (204)
```

### Router Definition
```python
from fastapi import APIRouter, HTTPException, status
from dj_ai_api.deps import DbSession, AppSettings

router = APIRouter(prefix="/api/v1/tracks", tags=["tracks"])

@router.get("")
async def list_tracks(
    session: DbSession,
    settings: AppSettings,
    bpm_min: float | None = None,
    bpm_max: float | None = None,
    key: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Track]:
    """List tracks with optional filters."""
    query = select(TrackORM)

    if bpm_min is not None:
        query = query.where(TrackORM.bpm >= bpm_min)
    if bpm_max is not None:
        query = query.where(TrackORM.bpm <= bpm_max)
    if key is not None:
        query = query.where(TrackORM.key == key)

    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    return [Track.model_validate(row) for row in result.scalars().all()]
```

### Response Status Codes
```python
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_track(session: DbSession, data: TrackCreate) -> Track:
    ...

@router.delete("/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_track(session: DbSession, track_id: str) -> None:
    ...
```

## Dependency Injection

```python
# deps.py
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dj_ai_studio.db import get_session
from dj_ai_api.config import Settings, get_settings

DbSession = Annotated[AsyncSession, Depends(get_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]
```

Usage in endpoints:
```python
@router.get("/{track_id}")
async def get_track(
    session: DbSession,        # Auto-injected
    settings: AppSettings,     # Auto-injected
    track_id: str,
) -> Track:
    ...
```

## Configuration

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./dj_ai_studio.db"
    cors_origins: list[str] = ["http://localhost:3000"]
    yandex_token: str | None = None

    model_config = {"env_prefix": "DJ_AI_"}

_settings: Settings | None = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

## Error Handling

```python
from fastapi import HTTPException, status

@router.get("/{track_id}")
async def get_track(session: DbSession, track_id: str) -> Track:
    result = await session.execute(
        select(TrackORM).where(TrackORM.id == track_id)
    )
    track = result.scalar_one_or_none()

    if track is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Track {track_id} not found"
        )

    return Track.model_validate(track)

@router.post("")
async def create_track(session: DbSession, data: TrackCreate) -> Track:
    try:
        orm = TrackORM(**data.model_dump())
        session.add(orm)
        await session.commit()
        return Track.model_validate(orm)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Track with this source_id already exists"
        )
```

## Request/Response Models

```python
# Use separate models for create/update/response
class TrackCreate(BaseModel):
    title: str
    artists: list[str] = []
    bpm: float | None = None
    key: str | None = None

class TrackUpdate(BaseModel):
    title: str | None = None
    bpm: float | None = None
    key: str | None = None

class Track(BaseModel):  # Response
    id: str
    title: str
    artists: list[str]
    bpm: float | None
    key: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
```

## App Factory Pattern

```python
# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dj_ai_studio.db import init_db, close_db
from dj_ai_api.config import get_settings
from dj_ai_api.routers import tracks, sets, analysis, yandex

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    await init_db(settings.database_url)
    yield
    await close_db()

def create_app() -> FastAPI:
    app = FastAPI(
        title="DJ AI Studio API",
        version="0.1.0",
        lifespan=lifespan,
    )

    settings = get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(tracks.router)
    app.include_router(sets.router)
    app.include_router(analysis.router)
    app.include_router(yandex.router)

    return app

app = create_app()
```
