"""Tests for Track CRUD endpoints."""

from uuid import uuid4

import pytest
from httpx import AsyncClient


class TestTracksAPI:
    """Tests for /api/v1/tracks endpoints."""

    @pytest.fixture
    def sample_track(self) -> dict:
        """Create a sample track payload."""
        return {
            "title": "Test Track",
            "artists": ["Test Artist"],
            "duration_ms": 180000,
            "bpm": 128.0,
            "key": "Am",
            "camelot": "8A",
            "energy": 7,
            "source": "yandex",
            "source_id": "test123",
        }

    async def test_list_tracks_empty(self, client: AsyncClient):
        """List tracks returns empty list initially."""
        response = await client.get("/api/v1/tracks")
        assert response.status_code == 200
        assert response.json() == []

    async def test_create_track(self, client: AsyncClient, sample_track: dict):
        """Create a new track."""
        response = await client.post("/api/v1/tracks", json=sample_track)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == sample_track["title"]
        assert data["bpm"] == sample_track["bpm"]
        assert "id" in data

    async def test_get_track(self, client: AsyncClient, sample_track: dict):
        """Get a track by ID."""
        # Create track first
        create_response = await client.post("/api/v1/tracks", json=sample_track)
        track_id = create_response.json()["id"]

        # Get track
        response = await client.get(f"/api/v1/tracks/{track_id}")
        assert response.status_code == 200
        assert response.json()["id"] == track_id

    async def test_get_track_not_found(self, client: AsyncClient):
        """Get non-existent track returns 404."""
        fake_id = str(uuid4())
        response = await client.get(f"/api/v1/tracks/{fake_id}")
        assert response.status_code == 404

    async def test_update_track(self, client: AsyncClient, sample_track: dict):
        """Update a track."""
        # Create track first
        create_response = await client.post("/api/v1/tracks", json=sample_track)
        track_id = create_response.json()["id"]

        # Update track
        response = await client.patch(
            f"/api/v1/tracks/{track_id}",
            json={"rating": 5, "notes": "Great track!"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["rating"] == 5
        assert data["notes"] == "Great track!"

    async def test_delete_track(self, client: AsyncClient, sample_track: dict):
        """Delete a track."""
        # Create track first
        create_response = await client.post("/api/v1/tracks", json=sample_track)
        track_id = create_response.json()["id"]

        # Delete track
        response = await client.delete(f"/api/v1/tracks/{track_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = await client.get(f"/api/v1/tracks/{track_id}")
        assert get_response.status_code == 404

    async def test_list_tracks_with_filters(self, client: AsyncClient):
        """List tracks with BPM filter."""
        # Create tracks with different BPMs
        track1 = {
            "title": "Slow Track",
            "artists": ["Artist"],
            "duration_ms": 180000,
            "bpm": 100.0,
            "key": "Am",
            "camelot": "8A",
            "energy": 5,
            "source": "local",
            "source_id": "1",
        }
        track2 = {
            "title": "Fast Track",
            "artists": ["Artist"],
            "duration_ms": 180000,
            "bpm": 140.0,
            "key": "Cm",
            "camelot": "5A",
            "energy": 9,
            "source": "local",
            "source_id": "2",
        }

        await client.post("/api/v1/tracks", json=track1)
        await client.post("/api/v1/tracks", json=track2)

        # Filter by BPM range
        response = await client.get("/api/v1/tracks?bpm_min=120&bpm_max=150")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Fast Track"
