"""Tests for ymd.core module."""

from pathlib import Path

from dj_ai_panel.core import (
    DEFAULT_PATH_PATTERN,
    MAX_COMPATIBILITY_LEVEL,
    MIN_COMPATIBILITY_LEVEL,
    CoreTrackQuality,
    LyricsFormat,
    full_title,
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
