"""Tests for Pydantic data models."""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from dj_ai_studio.models import Playlist, Set, SetTrack, Track, TrackStructure


class TestTrack:
    """Tests for Track model."""

    def test_create_minimal_track(self):
        """Create track with required fields."""
        track = Track(
            title="Test Track",
            artists=["Artist 1"],
            duration_ms=180000,
            bpm=128.0,
            key="Am",
            camelot="8A",
            energy=7,
            source="yandex",
            source_id="123456",
        )
        assert track.title == "Test Track"
        assert track.artists == ["Artist 1"]
        assert track.bpm == 128.0
        assert track.id is not None

    def test_create_full_track(self):
        """Create track with all fields."""
        track = Track(
            title="Full Track",
            artists=["Artist 1", "Artist 2"],
            album="Test Album",
            duration_ms=300000,
            bpm=128.0,
            key="Am",
            camelot="8A",
            energy=7,
            mood=["dark", "driving"],
            genre=["techno"],
            vocals="none",
            structure=TrackStructure(intro_ms=30000, outro_ms=45000),
            rating=5,
            tags=["favorite", "peak-time"],
            notes="Great for drops",
            source="spotify",
            source_id="abc123",
            cover_url="https://example.com/cover.jpg",
        )
        assert track.bpm == 128.0
        assert track.energy == 7
        assert track.structure.intro_ms == 30000

    def test_energy_validation(self):
        """Energy must be between 1 and 10."""
        with pytest.raises(ValidationError):
            Track(
                title="Bad Track",
                artists=["Artist"],
                duration_ms=180000,
                bpm=128.0,
                key="Am",
                camelot="8A",
                energy=11,  # Invalid
                source="local",
                source_id="1",
            )

    def test_rating_validation(self):
        """Rating must be between 1 and 5."""
        with pytest.raises(ValidationError):
            Track(
                title="Bad Track",
                artists=["Artist"],
                duration_ms=180000,
                bpm=128.0,
                key="Am",
                camelot="8A",
                energy=5,
                source="local",
                source_id="1",
                rating=6,  # Invalid
            )

    def test_key_validation(self):
        """Key must be valid musical key."""
        track = Track(
            title="Track",
            artists=["Artist"],
            duration_ms=180000,
            bpm=128.0,
            key="Am",
            camelot="8A",
            energy=5,
            source="local",
            source_id="1",
        )
        assert track.key == "Am"

        # Test sharp key
        track2 = Track(
            title="Track",
            artists=["Artist"],
            duration_ms=180000,
            bpm=128.0,
            key="C#m",
            camelot="5A",
            energy=5,
            source="local",
            source_id="2",
        )
        assert track2.key == "C#m"


class TestSet:
    """Tests for Set model."""

    def test_create_empty_set(self):
        """Create set with no tracks."""
        dj_set = Set(name="My Set")
        assert dj_set.name == "My Set"
        assert dj_set.tracks == []
        assert dj_set.id is not None

    def test_create_set_with_tracks(self):
        """Create set with tracks (1-indexed positions)."""
        track1_id = uuid4()
        track2_id = uuid4()

        dj_set = Set(
            name="Peak Time Set",
            target_duration_min=120,
            style="peak-time",
            energy_curve=[5, 6, 7, 8, 9, 10, 9, 8],
            tracks=[
                SetTrack(position=1, track_id=track1_id),
                SetTrack(position=2, track_id=track2_id, transition_type="mix"),
            ],
        )

        assert len(dj_set.tracks) == 2
        assert dj_set.tracks[0].position == 1
        assert dj_set.tracks[1].transition_type == "mix"

    def test_set_add_track(self):
        """Test add_track helper method."""
        dj_set = Set(name="Test Set")
        track_id = uuid4()

        dj_set.add_track(track_id)
        assert len(dj_set.tracks) == 1
        assert dj_set.tracks[0].track_id == track_id
        assert dj_set.tracks[0].position == 1  # 1-indexed

        # Add another
        track2_id = uuid4()
        dj_set.add_track(track2_id, transition_type="fade")
        assert len(dj_set.tracks) == 2
        assert dj_set.tracks[1].position == 2  # 1-indexed
        assert dj_set.tracks[1].transition_type == "fade"

    def test_set_remove_track(self):
        """Test remove_track helper method."""
        track1_id = uuid4()
        track2_id = uuid4()

        dj_set = Set(
            name="Test",
            tracks=[
                SetTrack(position=1, track_id=track1_id),
                SetTrack(position=2, track_id=track2_id),
            ],
        )

        dj_set.remove_track(1)  # Remove first track
        assert len(dj_set.tracks) == 1
        # Position should be renumbered to 1
        assert dj_set.tracks[0].position == 1
        assert dj_set.tracks[0].track_id == track2_id


class TestSetTrack:
    """Tests for SetTrack model."""

    def test_position_validation(self):
        """Position must be >= 1."""
        with pytest.raises(ValidationError):
            SetTrack(position=0, track_id=uuid4())  # Invalid, must be >= 1

    def test_valid_position(self):
        """Valid position starts from 1."""
        st = SetTrack(position=1, track_id=uuid4())
        assert st.position == 1

    def test_default_transition_type(self):
        """Default transition type is mix."""
        st = SetTrack(position=1, track_id=uuid4())
        assert st.transition_type == "mix"


class TestPlaylist:
    """Tests for Playlist model."""

    def test_create_playlist(self):
        """Create a playlist."""
        playlist = Playlist(
            name="Favorites",
            source="yandex",
            source_id="playlist123",
        )
        assert playlist.name == "Favorites"
        assert playlist.track_ids == []

    def test_playlist_add_track(self):
        """Test add_track helper method (allows duplicates by design)."""
        playlist = Playlist(
            name="Test",
            source="spotify",
            source_id="123",
        )

        track_id = uuid4()
        playlist.add_track(track_id)
        assert track_id in playlist.track_ids

    def test_playlist_remove_track(self):
        """Test remove_track helper method."""
        track_id = uuid4()
        playlist = Playlist(
            name="Test",
            source="spotify",
            source_id="123",
            track_ids=[track_id],
        )

        playlist.remove_track(track_id)
        assert track_id not in playlist.track_ids
