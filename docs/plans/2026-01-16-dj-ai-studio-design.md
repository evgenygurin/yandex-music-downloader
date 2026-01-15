# DJ AI Studio — Design Document

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Full-stack AI-powered DJ platform with multi-service integrations, track analysis, set building, and Claude Code integration via MCP.

**Architecture:** Monorepo with Next.js 15 frontend, FastAPI backend, and MCP Server. SQLite for persistence, JSON cache for API responses. Audio analysis via librosa/essentia.

**Tech Stack:** Next.js 15, shadcn/ui, Tailwind CSS 4, FastAPI, SQLAlchemy 2.0, SQLite, Python 3.11+

---

## 1. Overview & Architecture

### Core Purpose
- **Set Builder** — AI-assisted DJ set creation with harmonic mixing
- **Track Discovery** — Smart search across connected services
- **Mix Assistant** — Transition recommendations and compatibility analysis
- **Library Management** — Unified view of all music sources

### AI Interface
- **MCP Server** — Full Claude Code integration for AI-powered workflows
- **CLI** — Command-line tool for automation and scripting

### Monorepo Structure

```bash
dj-ai-studio/
├── apps/
│   ├── web/                 # Next.js 15 (App Router)
│   ├── api/                 # FastAPI backend
│   └── mcp/                 # MCP Server for Claude Code
├── packages/
│   ├── core/                # Shared Python (models, analysis)
│   └── cli/                 # CLI tool
├── scripts/                 # DJ utilities (migrated)
├── docs/                    # Documentation
└── data/                    # SQLite DB, JSON cache
```

---

## 2. Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 15.x | App Router, Server Components, Server Actions |
| React | 19.x | UI framework |
| shadcn/ui | latest | Component library (Radix + Tailwind) |
| Tailwind CSS | 4.x | Styling |
| Recharts | 2.x | Charts (energy curves) |
| Zustand | 5.x | Client state |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.115+ | Async API |
| SQLAlchemy | 2.0 | ORM |
| Pydantic | 2.x | Validation |
| librosa | 0.10+ | Audio analysis |
| essentia | 2.1+ | Advanced audio features |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| SQLite | Primary database |
| JSON files | API response cache |
| UV | Python package manager |
| pnpm | Node package manager |
| Turborepo | Monorepo orchestration |

---

## 3. Data Model

### Track
```python
class Track:
    id: UUID
    title: str
    artists: list[str]
    album: str | None
    duration_ms: int

    # Core DJ attributes
    bpm: float
    key: str              # "Am", "C", "F#m"
    camelot: str          # "8A", "5B"
    energy: int           # 1-10

    # Extended analysis
    mood: list[str]       # ["dark", "driving", "euphoric"]
    genre: list[str]      # ["techno", "progressive"]
    vocals: str           # "none" | "some" | "heavy"
    structure: dict       # {intro_ms, outro_ms, drop_ms}

    # User data
    rating: int | None    # 1-5 stars
    tags: list[str]       # custom user tags
    notes: str | None

    # Source tracking
    source: str           # "yandex", "spotify", "local"
    source_id: str
    cover_url: str | None

    # Timestamps
    created_at: datetime
    analyzed_at: datetime | None
```

### Set
```python
class Set:
    id: UUID
    name: str
    description: str | None
    target_duration_min: int

    # Metadata
    style: str | None           # "progressive", "peak-time"
    energy_curve: list[int]     # target energy per segment

    # Tracks
    tracks: list[SetTrack]

    # Timestamps
    created_at: datetime
    updated_at: datetime
```

### SetTrack
```python
class SetTrack:
    position: int
    track_id: UUID

    # Transition info
    transition_type: str        # "mix", "cut", "fade"
    mix_in_point_ms: int | None
    mix_out_point_ms: int | None

    # Notes
    notes: str | None
```

### Playlist
```python
class Playlist:
    id: UUID
    name: str
    source: str           # "yandex", "spotify"
    source_id: str

    track_ids: list[UUID]

    synced_at: datetime
```

---

## 4. MCP & AI Integration

### MCP Server Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    Claude Code MAX                       │
│                                                          │
│  "Покажи треки с энергией 8+ в тональности Am"          │
│  "Собери сет на 2 часа progressive house"               │
│  "Найди переход от текущего трека"                      │
└─────────────────────┬───────────────────────────────────┘
                      │ MCP Protocol
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  dj-ai-studio MCP Server                 │
│                                                          │
│  Tools:                    Resources:                    │
│  ├─ search_tracks          ├─ track://{id}              │
│  ├─ get_track_analysis     ├─ set://{id}                │
│  ├─ create_set             ├─ library://stats           │
│  ├─ add_to_set             └─ context://current_set     │
│  ├─ suggest_transition                                   │
│  ├─ analyze_compatibility                                │
│  └─ sync_from_source                                     │
└─────────────────────────────────────────────────────────┘
```

### MCP Tools

| Tool | Purpose | Parameters |
|------|---------|------------|
| `search_tracks` | Search by any criteria | bpm_range, key, energy, mood, genre, query |
| `get_track_analysis` | Full track analysis | track_id |
| `create_set` | Create new set | name, target_duration, style |
| `add_to_set` | Add track to set | set_id, track_id, position |
| `suggest_transition` | Suggest transition | from_track_id, to_track_id |
| `analyze_compatibility` | Track compatibility | track_ids[] |
| `sync_from_source` | Sync with service | source, playlist_id |

### MCP Resources

| Resource | Content |
|----------|---------|
| `track://{uuid}` | Full track metadata, analysis, usage history |
| `set://{uuid}` | Track list, transitions, energy curve |
| `library://stats` | Genre distribution, BPM range, key popularity |
| `context://current_set` | Active set, last added track, recommendations |

---

## 5. Web App Features

### Navigation

```text
┌─────────────────────────────────────────────────────────┐
│  dj-ai-studio                    🔍 Search    [Avatar]  │
├─────────────────────────────────────────────────────────┤
│  📚 Library    🎛️ Sets    📥 Import    ⚙️ Settings      │
└─────────────────────────────────────────────────────────┘
```

### Library Page

| Feature | Description |
|---------|-------------|
| Track Grid | Cards with covers, BPM, Key badge |
| Smart Filters | BPM range slider, Camelot wheel, Energy, Mood tags |
| Sort Options | Date added, BPM, energy, rating |
| Bulk Actions | Mass analyze, tag, export |
| Track Detail | Sidebar with full analysis, waveform, cue points |

### Sets Page

| Feature | Description |
|---------|-------------|
| Set Builder | Drag-n-drop tracks, energy curve visualization |
| Transition View | Transition recommendations between tracks |
| Timeline | Set timeline with mix points |
| Export | M3U8, Rekordbox XML, Serato crates |
| AI Assistant | Chat for set work via Claude |

### Import Page

| Feature | Description |
|---------|-------------|
| Service Connect | OAuth for Yandex, Spotify, Apple Music |
| Playlist Import | Paste URL → auto-detect service → import |
| Local Import | Drag-drop audio files |
| Sync Status | Last sync time, pending tracks |

### Custom UI Components

| Component | Technology |
|-----------|------------|
| Camelot Wheel | Custom React + SVG |
| BPM Range Slider | shadcn Slider (dual handle) |
| Energy Curve Chart | Recharts LineChart |
| Waveform Display | Canvas API |
| Track Card | shadcn Card + hover preview |
| Transition Badge | 🟢 perfect / 🟡 ok / 🔴 clash |

---

## 6. First Integration: Yandex Music

### Existing Code to Migrate
- `ymd/` package → `packages/core/yandex/`
- Download functionality
- Authentication (token-based)
- Playlist/album/artist fetching

### New Functionality
- Track metadata → Track model mapping
- Audio file caching for analysis
- Incremental playlist sync

---

## 7. Implementation Phases

### Phase 1: Foundation
- Monorepo setup (Turborepo + pnpm + uv)
- Core package with data models
- SQLite database schema
- Basic FastAPI endpoints

### Phase 2: Yandex Integration
- Migrate ymd code to packages/core
- Playlist sync endpoint
- Track download + cache

### Phase 3: Audio Analysis
- librosa integration
- BPM, key detection
- Energy calculation
- Background analysis queue

### Phase 4: MCP Server
- MCP protocol implementation
- Tools: search, analyze, create_set
- Resources: track, set, library stats

### Phase 5: Web App
- Next.js 15 setup with shadcn/ui
- Library page with filters
- Set builder with drag-n-drop
- Import flow

### Phase 6: AI Features
- Transition suggestions
- Set auto-generation
- Smart recommendations
