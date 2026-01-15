"""Tests for DJ AI MCP Server."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from dj_ai_mcp.server import (
    _get_compatible_camelot,
    _track_to_dict,
    call_tool,
    list_resources,
    list_tools,
)


class TestCamelotCompatibility:
    """Tests for Camelot wheel compatibility calculation."""

    def test_compatible_camelot_8a(self):
        """8A should be compatible with 7A, 9A, and 8B."""
        result = _get_compatible_camelot("8A")

        assert "8A" in result  # Same key
        assert "7A" in result  # -1 on wheel
        assert "9A" in result  # +1 on wheel
        assert "8B" in result  # Relative major
        assert len(result) == 4

    def test_compatible_camelot_1a(self):
        """1A should wrap around correctly (12A, 2A, 1B)."""
        result = _get_compatible_camelot("1A")

        assert "1A" in result
        assert "12A" in result  # -1 wraps to 12
        assert "2A" in result  # +1
        assert "1B" in result  # Relative major

    def test_compatible_camelot_12b(self):
        """12B should wrap around correctly (11B, 1B, 12A)."""
        result = _get_compatible_camelot("12B")

        assert "12B" in result
        assert "11B" in result  # -1
        assert "1B" in result  # +1 wraps to 1
        assert "12A" in result  # Relative minor

    def test_compatible_camelot_5b(self):
        """5B should return expected compatible keys."""
        result = _get_compatible_camelot("5B")

        assert "5B" in result
        assert "4B" in result
        assert "6B" in result
        assert "5A" in result

    def test_compatible_camelot_empty(self):
        """Empty or invalid input returns empty list."""
        assert _get_compatible_camelot("") == []
        assert _get_compatible_camelot("X") == []


class TestTrackToDict:
    """Tests for track ORM to dict conversion."""

    def test_track_to_dict_full(self):
        """Convert track with all fields."""
        from datetime import datetime

        track = MagicMock()
        track.id = "test-id"
        track.title = "Test Track"
        track.artists = "Test Artist"
        track.album = "Test Album"
        track.bpm = 128.0
        track.key = "Am"
        track.camelot = "8A"
        track.energy = 7
        track.duration_ms = 360000
        track.source = "yandex"
        track.analyzed_at = datetime.now()

        result = _track_to_dict(track)

        assert result["id"] == "test-id"
        assert result["title"] == "Test Track"
        assert result["artists"] == "Test Artist"
        assert result["album"] == "Test Album"
        assert result["bpm"] == 128.0
        assert result["key"] == "Am"
        assert result["camelot"] == "8A"
        assert result["energy"] == 7
        assert result["duration_ms"] == 360000
        assert result["source"] == "yandex"
        assert result["analyzed"] is True

    def test_track_to_dict_not_analyzed(self):
        """Track without analysis shows analyzed=False."""
        track = MagicMock()
        track.id = "test-id"
        track.title = "Test Track"
        track.artists = "Test Artist"
        track.album = None
        track.bpm = None
        track.key = None
        track.camelot = None
        track.energy = None
        track.duration_ms = 180000
        track.source = "local"
        track.analyzed_at = None

        result = _track_to_dict(track)

        assert result["analyzed"] is False
        assert result["bpm"] is None
        assert result["key"] is None


class TestListTools:
    """Tests for list_tools handler."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_all_tools(self):
        """list_tools returns all 8 tools."""
        tools = await list_tools()

        assert len(tools) == 8

        tool_names = {t.name for t in tools}
        assert "search_tracks" in tool_names
        assert "get_track" in tool_names
        assert "find_compatible_tracks" in tool_names
        assert "analyze_track" in tool_names
        assert "create_set" in tool_names
        assert "add_track_to_set" in tool_names
        assert "get_set" in tool_names
        assert "suggest_next_track" in tool_names

    @pytest.mark.asyncio
    async def test_list_tools_have_descriptions(self):
        """All tools have descriptions."""
        tools = await list_tools()

        for tool in tools:
            assert tool.description
            assert len(tool.description) > 10

    @pytest.mark.asyncio
    async def test_list_tools_have_input_schemas(self):
        """All tools have input schemas."""
        tools = await list_tools()

        for tool in tools:
            assert tool.inputSchema
            assert tool.inputSchema.get("type") == "object"
            assert "properties" in tool.inputSchema


class TestListResources:
    """Tests for list_resources handler."""

    @pytest.mark.asyncio
    async def test_list_resources_returns_all(self):
        """list_resources returns all 3 resources."""
        resources = await list_resources()

        assert len(resources) == 3

        uris = {str(r.uri) for r in resources}
        assert "dj://library/stats" in uris
        assert "dj://library/tracks" in uris
        assert "dj://library/sets" in uris

    @pytest.mark.asyncio
    async def test_list_resources_have_metadata(self):
        """All resources have name, description, and mimeType."""
        resources = await list_resources()

        for resource in resources:
            assert resource.name
            assert resource.description
            assert resource.mimeType == "application/json"


class TestCallTool:
    """Tests for call_tool handler."""

    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self):
        """Unknown tool returns error."""
        result = await call_tool("unknown_tool", {})

        assert len(result) == 1
        assert "error" in result[0].text
        assert "Unknown tool" in result[0].text

    @pytest.mark.asyncio
    @patch("dj_ai_mcp.server.search_tracks")
    async def test_call_tool_search_tracks(self, mock_search):
        """call_tool routes to search_tracks."""
        mock_search.return_value = {"count": 0, "tracks": []}

        result = await call_tool("search_tracks", {"query": "test"})

        mock_search.assert_called_once_with(query="test")
        assert len(result) == 1

    @pytest.mark.asyncio
    @patch("dj_ai_mcp.server.get_track")
    async def test_call_tool_get_track(self, mock_get):
        """call_tool routes to get_track."""
        mock_get.return_value = {"id": "track-1", "title": "Test"}

        result = await call_tool("get_track", {"track_id": "track-1"})

        mock_get.assert_called_once_with(track_id="track-1")
        assert "track-1" in result[0].text

    @pytest.mark.asyncio
    @patch("dj_ai_mcp.server.create_set")
    async def test_call_tool_create_set(self, mock_create):
        """call_tool routes to create_set."""
        mock_create.return_value = {"id": "set-1", "name": "New Set"}

        result = await call_tool("create_set", {"name": "New Set"})

        mock_create.assert_called_once_with(name="New Set")
        assert "set-1" in result[0].text

    @pytest.mark.asyncio
    @patch("dj_ai_mcp.server.search_tracks")
    async def test_call_tool_handles_exception(self, mock_search):
        """call_tool handles exceptions gracefully."""
        mock_search.side_effect = Exception("Database error")

        result = await call_tool("search_tracks", {})

        assert len(result) == 1
        assert "error" in result[0].text
        assert "Database error" in result[0].text


class TestSearchTracks:
    """Tests for search_tracks tool implementation."""

    @pytest.mark.asyncio
    @patch("dj_ai_mcp.server.get_db")
    async def test_search_returns_tracks(self, mock_get_db):
        """Search tracks returns results from database."""
        from dj_ai_mcp.server import search_tracks

        # Mock session and query result
        mock_track = MagicMock()
        mock_track.id = "track-1"
        mock_track.title = "Test Track"
        mock_track.artists = "Artist"
        mock_track.album = "Album"
        mock_track.bpm = 128.0
        mock_track.key = "Am"
        mock_track.camelot = "8A"
        mock_track.energy = 7
        mock_track.duration_ms = 300000
        mock_track.source = "yandex"
        mock_track.analyzed_at = None

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_track]
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_get_db.return_value.__aexit__ = AsyncMock()

        result = await search_tracks(query="Test")

        assert result["count"] == 1
        assert result["tracks"][0]["title"] == "Test Track"


class TestFindCompatibleTracks:
    """Tests for find_compatible_tracks tool implementation."""

    @pytest.mark.asyncio
    @patch("dj_ai_mcp.server.get_db")
    async def test_find_compatible_track_not_found(self, mock_get_db):
        """Find compatible tracks returns error for non-existent track."""
        from dj_ai_mcp.server import find_compatible_tracks

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_get_db.return_value.__aexit__ = AsyncMock()

        result = await find_compatible_tracks(track_id="non-existent")

        assert "error" in result
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    @patch("dj_ai_mcp.server.get_db")
    async def test_find_compatible_returns_results(self, mock_get_db):
        """Find compatible tracks returns harmonically compatible tracks."""
        from dj_ai_mcp.server import find_compatible_tracks

        # Source track
        mock_source = MagicMock()
        mock_source.id = "track-1"
        mock_source.title = "Source Track"
        mock_source.artists = "Artist"
        mock_source.album = "Album"
        mock_source.bpm = 128.0
        mock_source.key = "Am"
        mock_source.camelot = "8A"
        mock_source.energy = 7
        mock_source.duration_ms = 300000
        mock_source.source = "yandex"
        mock_source.analyzed_at = None

        mock_session = AsyncMock()

        # First call returns source track, second returns compatible tracks
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = mock_source

        mock_result2 = MagicMock()
        mock_result2.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(side_effect=[mock_result1, mock_result2])

        mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_get_db.return_value.__aexit__ = AsyncMock()

        result = await find_compatible_tracks(track_id="track-1")

        assert "source_track" in result
        assert "compatible_camelot" in result
        assert "8A" in result["compatible_camelot"]
        assert "8B" in result["compatible_camelot"]


class TestAnalyzeTrack:
    """Tests for analyze_track tool implementation."""

    @pytest.mark.asyncio
    async def test_analyze_track_file_not_found(self):
        """Analyze track returns error for non-existent file."""
        from dj_ai_mcp.server import analyze_track

        result = await analyze_track(file_path="/fake/path/song.mp3")

        assert "error" in result
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    @patch("dj_ai_studio.analysis.AudioAnalyzer")
    async def test_analyze_track_success(self, mock_analyzer_class, tmp_path):
        """Analyze track returns analysis results."""
        from dj_ai_mcp.server import analyze_track

        # Create a real temp file
        test_file = tmp_path / "song.mp3"
        test_file.write_bytes(b"fake audio data")

        # Mock analyzer result
        mock_result = MagicMock()
        mock_result.bpm.bpm = 128.0
        mock_result.bpm.confidence = 0.9
        mock_result.key.key = "Am"
        mock_result.key.camelot = "8A"
        mock_result.key.is_minor = True
        mock_result.key.confidence = 0.85
        mock_result.energy.energy = 7
        mock_result.duration_seconds = 300.0

        mock_analyzer = MagicMock()
        mock_analyzer.analyze_file_async = AsyncMock(return_value=mock_result)
        mock_analyzer_class.return_value = mock_analyzer

        result = await analyze_track(file_path=str(test_file))

        assert result["bpm"] == 128.0
        assert result["key"] == "Am"
        assert result["camelot"] == "8A"
        assert result["energy"] == 7


class TestCreateSet:
    """Tests for create_set tool implementation."""

    @pytest.mark.asyncio
    async def test_create_set_basic(self, async_session):
        """Create set returns new set info."""
        from dj_ai_mcp.server import create_set

        with patch("dj_ai_mcp.server.get_db") as mock_db:
            mock_db.return_value.__aenter__ = AsyncMock(return_value=async_session)
            mock_db.return_value.__aexit__ = AsyncMock()

            result = await create_set(name="Test Set")

        assert "id" in result
        assert result["name"] == "Test Set"
        assert result["description"] is None

    @pytest.mark.asyncio
    async def test_create_set_with_description(self, async_session):
        """Create set with description."""
        from dj_ai_mcp.server import create_set

        with patch("dj_ai_mcp.server.get_db") as mock_db:
            mock_db.return_value.__aenter__ = AsyncMock(return_value=async_session)
            mock_db.return_value.__aexit__ = AsyncMock()

            result = await create_set(name="Party Set", description="Saturday night vibes")

        assert result["name"] == "Party Set"
        assert result["description"] == "Saturday night vibes"


class TestGetSet:
    """Tests for get_set tool implementation."""

    @pytest.mark.asyncio
    @patch("dj_ai_mcp.server.get_db")
    async def test_get_set_with_tracks(self, mock_get_db):
        """Get set returns set with ordered tracks."""
        from dj_ai_mcp.server import get_set

        # Mock set
        mock_set = MagicMock()
        mock_set.id = "set-1"
        mock_set.name = "Friday Night Mix"
        mock_set.description = "Opening set"

        # Mock track
        mock_track = MagicMock()
        mock_track.id = "track-1"
        mock_track.title = "Test Track"
        mock_track.artists = "Artist"
        mock_track.album = "Album"
        mock_track.bpm = 128.0
        mock_track.key = "Am"
        mock_track.camelot = "8A"
        mock_track.energy = 7
        mock_track.duration_ms = 300000
        mock_track.source = "yandex"
        mock_track.analyzed_at = None

        mock_set_track = MagicMock()
        mock_set_track.position = 1

        mock_session = AsyncMock()

        # First call: get set, second call: get tracks
        mock_result1 = MagicMock()
        mock_result1.scalar_one_or_none.return_value = mock_set

        mock_result2 = MagicMock()
        mock_result2.all.return_value = [(mock_set_track, mock_track)]

        mock_session.execute = AsyncMock(side_effect=[mock_result1, mock_result2])

        mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_get_db.return_value.__aexit__ = AsyncMock()

        result = await get_set(set_id="set-1")

        assert result["id"] == "set-1"
        assert result["name"] == "Friday Night Mix"
        assert result["track_count"] == 1
        assert result["tracks"][0]["position"] == 1

    @pytest.mark.asyncio
    @patch("dj_ai_mcp.server.get_db")
    async def test_get_set_not_found(self, mock_get_db):
        """Get non-existent set returns error."""
        from dj_ai_mcp.server import get_set

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_get_db.return_value.__aexit__ = AsyncMock()

        result = await get_set(set_id="non-existent")

        assert "error" in result
        assert "not found" in result["error"].lower()


class TestSuggestNextTrack:
    """Tests for suggest_next_track tool implementation."""

    @pytest.mark.asyncio
    @patch("dj_ai_mcp.server.get_db")
    async def test_suggest_next_empty_set(self, mock_get_db):
        """Suggest next for empty set returns error."""
        from dj_ai_mcp.server import suggest_next_track

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_get_db.return_value.__aexit__ = AsyncMock()

        result = await suggest_next_track(set_id="empty-set")

        assert "error" in result
        assert "empty" in result["error"].lower()

    @pytest.mark.asyncio
    @patch("dj_ai_mcp.server.get_db")
    async def test_suggest_next_returns_compatible(self, mock_get_db):
        """Suggest next returns harmonically compatible suggestions."""
        from dj_ai_mcp.server import suggest_next_track

        # Mock last track
        mock_track = MagicMock()
        mock_track.id = "track-2"
        mock_track.title = "Last Track"
        mock_track.artists = "Artist"
        mock_track.album = "Album"
        mock_track.bpm = 126.0
        mock_track.key = "Gm"
        mock_track.camelot = "6A"
        mock_track.energy = 7
        mock_track.duration_ms = 300000
        mock_track.source = "yandex"
        mock_track.analyzed_at = None

        mock_set_track = MagicMock()
        mock_set_track.position = 2

        mock_session = AsyncMock()

        # First call: get last track
        mock_result1 = MagicMock()
        mock_result1.first.return_value = (mock_set_track, mock_track)

        # Second call: get existing track ids
        mock_result2 = MagicMock()
        mock_result2.all.return_value = [("track-1",), ("track-2",)]

        # Third call: get suggestions
        mock_result3 = MagicMock()
        mock_result3.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(side_effect=[mock_result1, mock_result2, mock_result3])

        mock_get_db.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_get_db.return_value.__aexit__ = AsyncMock()

        result = await suggest_next_track(set_id="set-1")

        assert "last_track" in result
        assert "compatible_camelot" in result
        assert "suggestions" in result
        # Last track is 6A, so compatible keys should include 5A, 7A, 6B
        assert "6A" in result["compatible_camelot"]
        assert "6B" in result["compatible_camelot"]
