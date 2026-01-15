"""Tests for Yandex Music converter functions."""

import pytest
from dj_ai_studio.yandex.converter import (
    camelot_to_key,
    key_to_camelot,
)


class TestKeyToCamelot:
    """Tests for key_to_camelot function."""

    @pytest.mark.parametrize(
        "key,expected",
        [
            # Minor keys
            ("Am", "8A"),
            ("Em", "9A"),
            ("Bm", "10A"),
            ("F#m", "11A"),
            ("C#m", "12A"),
            ("Dm", "7A"),
            ("Gm", "6A"),
            ("Cm", "5A"),
            ("Fm", "4A"),
            # Major keys
            ("C", "8B"),
            ("G", "9B"),
            ("D", "10B"),
            ("A", "11B"),
            ("E", "12B"),
            ("F", "7B"),
            ("Bb", "6B"),
            ("Eb", "5B"),
            # Enharmonic equivalents
            ("Gb", "2B"),
            ("F#", "2B"),
            ("Db", "3B"),
            ("C#", "3B"),
        ],
    )
    def test_known_keys(self, key: str, expected: str):
        """Known keys map correctly to Camelot."""
        assert key_to_camelot(key) == expected

    def test_unknown_key_fallback(self):
        """Unknown keys fall back to 8B."""
        assert key_to_camelot("X") == "8B"


class TestCamelotToKey:
    """Tests for camelot_to_key function."""

    @pytest.mark.parametrize(
        "camelot,expected",
        [
            # A column (minor)
            ("8A", "Am"),
            ("9A", "Em"),
            ("10A", "Bm"),
            ("11A", "F#m"),
            ("12A", "C#m"),
            ("1A", "G#m"),
            ("2A", "D#m"),
            ("3A", "A#m"),
            ("4A", "Fm"),
            ("5A", "Cm"),
            ("6A", "Gm"),
            ("7A", "Dm"),
            # B column (major)
            ("8B", "C"),
            ("9B", "G"),
            ("10B", "D"),
            ("11B", "A"),
            ("12B", "E"),
            ("1B", "B"),
            ("2B", "F#"),
            ("3B", "Db"),
            ("4B", "Ab"),
            ("5B", "Eb"),
            ("6B", "Bb"),
            ("7B", "F"),
        ],
    )
    def test_known_camelot(self, camelot: str, expected: str):
        """Known Camelot values map correctly to keys."""
        assert camelot_to_key(camelot) == expected

    def test_unknown_camelot_fallback(self):
        """Unknown Camelot falls back to C."""
        assert camelot_to_key("13A") == "C"


class TestRoundTrip:
    """Test key <-> camelot conversion round trips."""

    @pytest.mark.parametrize(
        "camelot",
        ["8A", "9B", "12A", "1B", "5A", "6B"],
    )
    def test_camelot_roundtrip(self, camelot: str):
        """Camelot -> key -> camelot preserves value."""
        key = camelot_to_key(camelot)
        result = key_to_camelot(key)
        assert result == camelot
