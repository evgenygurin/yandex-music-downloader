"""MCP Server for DJ AI Studio.

Provides tools and resources for Claude Code to interact with
the DJ AI Studio library - searching tracks, analyzing audio,
building sets, and more.
"""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dj_ai_studio.db import get_session, init_db
from dj_ai_studio.db.models import SetORM, TrackORM
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, Tool
from pydantic import AnyUrl
from sqlalchemy import select

# Initialize server
server = Server("dj-ai-studio")

# Database URL from environment or default
DATABASE_URL = os.getenv(
    "DJ_AI_DATABASE_URL",
    f"sqlite+aiosqlite:///{Path.home()}/.dj-ai-studio/library.db",
)


@asynccontextmanager
async def get_db():
    """Get database session."""
    await init_db(DATABASE_URL)
    async for session in get_session():
        yield session


# =============================================================================
# TOOLS
# =============================================================================


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_tracks",
            description="Search tracks in the library by title, artist, BPM range, key, or energy level",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for title or artist",
                    },
                    "bpm_min": {
                        "type": "number",
                        "description": "Minimum BPM",
                    },
                    "bpm_max": {
                        "type": "number",
                        "description": "Maximum BPM",
                    },
                    "key": {
                        "type": "string",
                        "description": "Musical key (e.g., Am, C, F#m)",
                    },
                    "camelot": {
                        "type": "string",
                        "description": "Camelot notation (e.g., 8A, 5B)",
                    },
                    "energy_min": {
                        "type": "integer",
                        "description": "Minimum energy (1-10)",
                    },
                    "energy_max": {
                        "type": "integer",
                        "description": "Maximum energy (1-10)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default 20)",
                    },
                },
            },
        ),
        Tool(
            name="get_track",
            description="Get detailed information about a specific track by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_id": {
                        "type": "string",
                        "description": "Track UUID",
                    },
                },
                "required": ["track_id"],
            },
        ),
        Tool(
            name="find_compatible_tracks",
            description="Find tracks compatible for mixing with a given track (based on Camelot wheel)",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_id": {
                        "type": "string",
                        "description": "Source track UUID",
                    },
                    "bpm_tolerance": {
                        "type": "number",
                        "description": "BPM tolerance percentage (default 5%)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default 10)",
                    },
                },
                "required": ["track_id"],
            },
        ),
        Tool(
            name="analyze_track",
            description="Analyze a track to detect BPM, key, and energy (requires audio file)",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to audio file",
                    },
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="create_set",
            description="Create a new DJ set",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Set name",
                    },
                    "description": {
                        "type": "string",
                        "description": "Set description",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="add_track_to_set",
            description="Add a track to a DJ set",
            inputSchema={
                "type": "object",
                "properties": {
                    "set_id": {
                        "type": "string",
                        "description": "Set UUID",
                    },
                    "track_id": {
                        "type": "string",
                        "description": "Track UUID",
                    },
                    "position": {
                        "type": "integer",
                        "description": "Position in set (optional, appends if not specified)",
                    },
                },
                "required": ["set_id", "track_id"],
            },
        ),
        Tool(
            name="get_set",
            description="Get a DJ set with all its tracks",
            inputSchema={
                "type": "object",
                "properties": {
                    "set_id": {
                        "type": "string",
                        "description": "Set UUID",
                    },
                },
                "required": ["set_id"],
            },
        ),
        Tool(
            name="suggest_next_track",
            description="Suggest the next track for a set based on the last track's key and energy",
            inputSchema={
                "type": "object",
                "properties": {
                    "set_id": {
                        "type": "string",
                        "description": "Set UUID",
                    },
                    "energy_direction": {
                        "type": "string",
                        "enum": ["up", "down", "maintain"],
                        "description": "Desired energy direction",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of suggestions (default 5)",
                    },
                },
                "required": ["set_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "search_tracks":
            result = await search_tracks(**arguments)
        elif name == "get_track":
            result = await get_track(**arguments)
        elif name == "find_compatible_tracks":
            result = await find_compatible_tracks(**arguments)
        elif name == "analyze_track":
            result = await analyze_track(**arguments)
        elif name == "create_set":
            result = await create_set(**arguments)
        elif name == "add_track_to_set":
            result = await add_track_to_set(**arguments)
        elif name == "get_set":
            result = await get_set(**arguments)
        elif name == "suggest_next_track":
            result = await suggest_next_track(**arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


# =============================================================================
# TOOL IMPLEMENTATIONS
# =============================================================================


async def search_tracks(
    query: str | None = None,
    bpm_min: float | None = None,
    bpm_max: float | None = None,
    key: str | None = None,
    camelot: str | None = None,
    energy_min: int | None = None,
    energy_max: int | None = None,
    limit: int = 20,
) -> dict:
    """Search tracks with filters."""
    async with get_db() as session:
        stmt = select(TrackORM)

        if query:
            stmt = stmt.where(
                TrackORM.title.ilike(f"%{query}%")
                | TrackORM.artists.ilike(f"%{query}%")
            )
        if bpm_min is not None:
            stmt = stmt.where(TrackORM.bpm >= bpm_min)
        if bpm_max is not None:
            stmt = stmt.where(TrackORM.bpm <= bpm_max)
        if key is not None:
            stmt = stmt.where(TrackORM.key == key)
        if camelot is not None:
            stmt = stmt.where(TrackORM.camelot == camelot)
        if energy_min is not None:
            stmt = stmt.where(TrackORM.energy >= energy_min)
        if energy_max is not None:
            stmt = stmt.where(TrackORM.energy <= energy_max)

        stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        tracks = result.scalars().all()

        return {
            "count": len(tracks),
            "tracks": [_track_to_dict(t) for t in tracks],
        }


async def get_track(track_id: str) -> dict:
    """Get track by ID."""
    async with get_db() as session:
        result = await session.execute(
            select(TrackORM).where(TrackORM.id == track_id)
        )
        track = result.scalar_one_or_none()

        if track is None:
            return {"error": "Track not found"}

        return _track_to_dict(track)


async def find_compatible_tracks(
    track_id: str,
    bpm_tolerance: float = 5.0,
    limit: int = 10,
) -> dict:
    """Find tracks compatible for mixing."""
    async with get_db() as session:
        # Get source track
        result = await session.execute(
            select(TrackORM).where(TrackORM.id == track_id)
        )
        source = result.scalar_one_or_none()

        if source is None:
            return {"error": "Source track not found"}

        # Calculate BPM range
        bpm_min = source.bpm * (1 - bpm_tolerance / 100)
        bpm_max = source.bpm * (1 + bpm_tolerance / 100)

        # Get compatible Camelot codes
        compatible = _get_compatible_camelot(source.camelot)

        # Search for compatible tracks
        stmt = (
            select(TrackORM)
            .where(TrackORM.id != track_id)
            .where(TrackORM.bpm >= bpm_min)
            .where(TrackORM.bpm <= bpm_max)
            .where(TrackORM.camelot.in_(compatible))
            .limit(limit)
        )
        result = await session.execute(stmt)
        tracks = result.scalars().all()

        return {
            "source_track": _track_to_dict(source),
            "compatible_camelot": compatible,
            "bpm_range": [round(bpm_min, 1), round(bpm_max, 1)],
            "tracks": [_track_to_dict(t) for t in tracks],
        }


async def analyze_track(file_path: str) -> dict:
    """Analyze audio file."""
    from dj_ai_studio.analysis import AudioAnalyzer

    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    analyzer = AudioAnalyzer()
    result = await analyzer.analyze_file_async(str(path))

    return {
        "file": str(path),
        "bpm": result.bpm.bpm,
        "bpm_confidence": result.bpm.confidence,
        "key": result.key.key,
        "camelot": result.key.camelot,
        "is_minor": result.key.is_minor,
        "key_confidence": result.key.confidence,
        "energy": result.energy.energy,
        "duration_seconds": result.duration_seconds,
    }


async def create_set(name: str, description: str | None = None) -> dict:
    """Create a new DJ set."""
    from uuid import uuid4

    async with get_db() as session:
        set_orm = SetORM(
            id=str(uuid4()),
            name=name,
            description=description,
        )
        session.add(set_orm)
        await session.commit()

        return {
            "id": set_orm.id,
            "name": set_orm.name,
            "description": set_orm.description,
        }


async def add_track_to_set(
    set_id: str,
    track_id: str,
    position: int | None = None,
) -> dict:
    """Add track to a set."""
    from dj_ai_studio.db.models import SetTrackORM

    async with get_db() as session:
        # Verify set exists
        result = await session.execute(select(SetORM).where(SetORM.id == set_id))
        set_orm = result.scalar_one_or_none()
        if set_orm is None:
            return {"error": "Set not found"}

        # Verify track exists
        result = await session.execute(
            select(TrackORM).where(TrackORM.id == track_id)
        )
        track = result.scalar_one_or_none()
        if track is None:
            return {"error": "Track not found"}

        # Get current max position
        result = await session.execute(
            select(SetTrackORM)
            .where(SetTrackORM.set_id == set_id)
            .order_by(SetTrackORM.position.desc())
        )
        last = result.scalar_one_or_none()
        next_pos = (last.position + 1) if last else 1

        if position is None:
            position = next_pos

        # Add track to set
        set_track = SetTrackORM(
            set_id=set_id,
            track_id=track_id,
            position=position,
        )
        session.add(set_track)
        await session.commit()

        return {
            "set_id": set_id,
            "track_id": track_id,
            "position": position,
            "track": _track_to_dict(track),
        }


async def get_set(set_id: str) -> dict:
    """Get set with tracks."""
    from dj_ai_studio.db.models import SetTrackORM

    async with get_db() as session:
        result = await session.execute(select(SetORM).where(SetORM.id == set_id))
        set_orm = result.scalar_one_or_none()

        if set_orm is None:
            return {"error": "Set not found"}

        # Get tracks in order
        result = await session.execute(
            select(SetTrackORM, TrackORM)
            .join(TrackORM, SetTrackORM.track_id == TrackORM.id)
            .where(SetTrackORM.set_id == set_id)
            .order_by(SetTrackORM.position)
        )
        rows = result.all()

        tracks = []
        for set_track, track in rows:
            track_dict = _track_to_dict(track)
            track_dict["position"] = set_track.position
            tracks.append(track_dict)

        return {
            "id": set_orm.id,
            "name": set_orm.name,
            "description": set_orm.description,
            "track_count": len(tracks),
            "tracks": tracks,
        }


async def suggest_next_track(
    set_id: str,
    energy_direction: str = "maintain",
    limit: int = 5,
) -> dict:
    """Suggest next track for a set."""
    from dj_ai_studio.db.models import SetTrackORM

    async with get_db() as session:
        # Get last track in set
        result = await session.execute(
            select(SetTrackORM, TrackORM)
            .join(TrackORM, SetTrackORM.track_id == TrackORM.id)
            .where(SetTrackORM.set_id == set_id)
            .order_by(SetTrackORM.position.desc())
        )
        row = result.first()

        if row is None:
            return {"error": "Set is empty"}

        _, last_track = row

        # Get compatible camelot codes
        compatible = _get_compatible_camelot(last_track.camelot)

        # Build energy filter
        energy_min = None
        energy_max = None
        if energy_direction == "up":
            energy_min = last_track.energy
        elif energy_direction == "down":
            energy_max = last_track.energy
        else:  # maintain
            energy_min = max(1, last_track.energy - 1)
            energy_max = min(10, last_track.energy + 1)

        # Get existing track IDs in set
        result = await session.execute(
            select(SetTrackORM.track_id).where(SetTrackORM.set_id == set_id)
        )
        existing_ids = [r[0] for r in result.all()]

        # Search for suggestions
        stmt = (
            select(TrackORM)
            .where(TrackORM.id.notin_(existing_ids))
            .where(TrackORM.camelot.in_(compatible))
        )
        if energy_min is not None:
            stmt = stmt.where(TrackORM.energy >= energy_min)
        if energy_max is not None:
            stmt = stmt.where(TrackORM.energy <= energy_max)

        stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        tracks = result.scalars().all()

        return {
            "last_track": _track_to_dict(last_track),
            "energy_direction": energy_direction,
            "compatible_camelot": compatible,
            "suggestions": [_track_to_dict(t) for t in tracks],
        }


# =============================================================================
# RESOURCES
# =============================================================================


@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available resources."""
    return [
        Resource(
            uri=AnyUrl("dj://library/stats"),
            name="Library Statistics",
            description="Overview of tracks and sets in the library",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("dj://library/tracks"),
            name="All Tracks",
            description="List of all tracks in the library",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("dj://library/sets"),
            name="All Sets",
            description="List of all DJ sets",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read a resource."""
    if uri == "dj://library/stats":
        return await _get_library_stats()
    elif uri == "dj://library/tracks":
        return await _get_all_tracks()
    elif uri == "dj://library/sets":
        return await _get_all_sets()
    else:
        return json.dumps({"error": f"Unknown resource: {uri}"})


async def _get_library_stats() -> str:
    """Get library statistics."""
    async with get_db() as session:
        track_count = await session.execute(select(TrackORM))
        tracks = track_count.scalars().all()

        set_count = await session.execute(select(SetORM))
        sets = set_count.scalars().all()

        # Calculate stats
        bpms = [t.bpm for t in tracks if t.bpm]
        energies = [t.energy for t in tracks if t.energy]

        stats = {
            "total_tracks": len(tracks),
            "total_sets": len(sets),
            "analyzed_tracks": sum(1 for t in tracks if t.analyzed_at),
            "bpm_range": [min(bpms), max(bpms)] if bpms else None,
            "avg_energy": round(sum(energies) / len(energies), 1) if energies else None,
        }

        return json.dumps(stats, indent=2)


async def _get_all_tracks() -> str:
    """Get all tracks."""
    async with get_db() as session:
        result = await session.execute(select(TrackORM).limit(100))
        tracks = result.scalars().all()

        return json.dumps(
            {"count": len(tracks), "tracks": [_track_to_dict(t) for t in tracks]},
            indent=2,
        )


async def _get_all_sets() -> str:
    """Get all sets."""
    async with get_db() as session:
        result = await session.execute(select(SetORM))
        sets = result.scalars().all()

        return json.dumps(
            {
                "count": len(sets),
                "sets": [
                    {"id": s.id, "name": s.name, "description": s.description}
                    for s in sets
                ],
            },
            indent=2,
        )


# =============================================================================
# HELPERS
# =============================================================================


def _track_to_dict(track: TrackORM) -> dict:
    """Convert track ORM to dict."""
    return {
        "id": track.id,
        "title": track.title,
        "artists": track.artists,
        "album": track.album,
        "bpm": track.bpm,
        "key": track.key,
        "camelot": track.camelot,
        "energy": track.energy,
        "duration_ms": track.duration_ms,
        "source": track.source,
        "analyzed": track.analyzed_at is not None,
    }


def _get_compatible_camelot(camelot: str) -> list[str]:
    """Get compatible Camelot codes for harmonic mixing.

    Compatible keys:
    - Same key (e.g., 8A -> 8A)
    - +1 on wheel (e.g., 8A -> 9A)
    - -1 on wheel (e.g., 8A -> 7A)
    - Relative major/minor (e.g., 8A -> 8B)
    """
    if not camelot or len(camelot) < 2:
        return []

    num = int(camelot[:-1])
    letter = camelot[-1]

    compatible = [camelot]  # Same key

    # +1 and -1 on wheel
    next_num = num % 12 + 1
    prev_num = (num - 2) % 12 + 1
    compatible.append(f"{next_num}{letter}")
    compatible.append(f"{prev_num}{letter}")

    # Relative major/minor
    other_letter = "B" if letter == "A" else "A"
    compatible.append(f"{num}{other_letter}")

    return compatible


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Run the MCP server."""
    asyncio.run(run_server())


async def run_server():
    """Run the MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    main()
