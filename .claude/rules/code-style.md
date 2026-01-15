# Code Style Guidelines

## Python Style (Ruff)

### Formatting
- **Line length:** 100 characters max
- **Indentation:** 4 spaces
- **Quotes:** Double quotes (`"string"`)
- **Trailing commas:** Use in multiline structures

### Imports
```python
# Order: stdlib -> third-party -> local
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from pydantic import BaseModel
from sqlalchemy import select

from dj_ai_studio.models import Track
```

### Type Hints
```python
# Required for all functions
def detect_bpm(audio_path: Path) -> float: ...

async def get_track(track_id: str) -> Track | None: ...

# Use TYPE_CHECKING for import-only types
if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
```

### Naming Conventions
| Type | Convention | Example |
|------|------------|---------|
| Classes | PascalCase | `AudioAnalyzer`, `TrackORM` |
| Functions | snake_case | `detect_bpm`, `get_session` |
| Variables | snake_case | `track_list`, `bpm_value` |
| Constants | UPPER_SNAKE | `CAMELOT_MAJOR`, `MAX_RETRIES` |
| Private | `_prefix` | `_analyze_signal`, `_engine` |
| Modules | snake_case | `audio_analysis.py` |

### Docstrings
```python
def analyze_track(file_path: Path) -> dict[str, float]:
    """Analyze audio file for DJ metadata.

    Args:
        file_path: Path to audio file (wav, mp3, flac)

    Returns:
        Dict with keys: bpm, key, camelot, energy

    Raises:
        FileNotFoundError: If file doesn't exist
        AudioAnalysisError: If analysis fails
    """
```

### Async Patterns
```python
# Use async for I/O operations
async def fetch_track(track_id: str) -> Track:
    async with get_session_context() as session:
        result = await session.execute(
            select(TrackORM).where(TrackORM.id == track_id)
        )
        return result.scalar_one_or_none()

# Use asyncio.to_thread for blocking calls
async def analyze_async(file_path: Path) -> dict:
    return await asyncio.to_thread(self._analyze_sync, file_path)
```

## JavaScript/TypeScript Style

### Formatting
- **Indentation:** 2 spaces
- **Semicolons:** Optional (Prettier decides)
- **Quotes:** Single quotes or double (consistent)

### Component Pattern
```tsx
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"

interface TrackCardProps {
  track: Track
  onSelect?: (id: string) => void
}

export function TrackCard({ track, onSelect }: TrackCardProps) {
  const [isSelected, setIsSelected] = useState(false)

  return (
    <div className="p-4 border rounded-lg">
      <h3>{track.title}</h3>
      <Button onClick={() => onSelect?.(track.id)}>
        Select
      </Button>
    </div>
  )
}
```

### Tailwind CSS
```tsx
// Use utility classes directly
<div className="flex items-center gap-4 p-4 bg-background rounded-lg shadow-sm">

// For complex styles, use cn() helper
import { cn } from "@/lib/utils"
<div className={cn(
  "base-styles",
  isActive && "active-styles",
  className
)}>
```

## Pydantic Models

```python
from pydantic import BaseModel, Field, field_validator

class Track(BaseModel):
    """Music track with DJ metadata."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(min_length=1, max_length=500)
    bpm: float | None = Field(default=None, ge=20, le=300)
    key: str | None = Field(default=None, pattern=r"^[A-G][#b]?[mM]?$")
    energy: int | None = Field(default=None, ge=1, le=10)

    @field_validator("key")
    @classmethod
    def normalize_key(cls, v: str | None) -> str | None:
        if v:
            return v.capitalize()
        return v
```

## SQLAlchemy ORM

```python
from sqlalchemy import String, Float, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

class TrackORM(Base):
    __tablename__ = "tracks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    bpm: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    artists: Mapped[list[str]] = mapped_column(JSON, default=list)
```
