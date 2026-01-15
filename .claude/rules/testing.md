# Testing Guidelines

## Test Structure

```
packages/core/tests/
├── test_models.py       # Pydantic model validation
├── test_analysis.py     # Audio analysis functions
└── test_yandex_converter.py

apps/api/tests/
├── conftest.py          # Fixtures
├── test_tracks.py       # Track CRUD endpoints
└── test_yandex.py       # Yandex integration
```

## Running Tests

```bash
# All tests
uv run pytest -v

# Core package only
uv run pytest packages/core/tests/ -v

# API package only
uv run pytest apps/api/tests/ -v

# Single test file
uv run pytest packages/core/tests/test_models.py -v

# Single test function
uv run pytest -v -k "test_track_creation"

# With coverage
uv run pytest --cov=dj_ai_studio --cov-report=html
```

## Async Testing

```python
import pytest
from httpx import AsyncClient, ASGITransport

# pytest-asyncio auto mode is enabled
# No need for @pytest.mark.asyncio decorator

async def test_create_track(client: AsyncClient):
    response = await client.post("/api/v1/tracks", json={
        "title": "Test Track",
        "bpm": 128.0
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Track"
```

## Fixtures

### Database Fixture (In-Memory SQLite)
```python
# conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

@pytest.fixture
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()
```

### API Client Fixture
```python
@pytest.fixture
async def client(test_session):
    def override_session():
        yield test_session

    app.dependency_overrides[get_session] = override_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
```

## Test Patterns

### Model Validation Tests
```python
def test_track_energy_range():
    """Energy must be 1-10."""
    with pytest.raises(ValidationError):
        Track(title="Test", energy=0)
    with pytest.raises(ValidationError):
        Track(title="Test", energy=11)

    track = Track(title="Test", energy=5)
    assert track.energy == 5

def test_key_pattern():
    """Key must match pattern like Am, C#m, Gb."""
    track = Track(title="Test", key="Am")
    assert track.key == "Am"

    with pytest.raises(ValidationError):
        Track(title="Test", key="invalid")
```

### CRUD Endpoint Tests
```python
async def test_list_tracks_with_filters(client: AsyncClient):
    # Create test data
    await client.post("/api/v1/tracks", json={"title": "Track 1", "bpm": 120})
    await client.post("/api/v1/tracks", json={"title": "Track 2", "bpm": 140})

    # Test filter
    response = await client.get("/api/v1/tracks", params={"bpm_min": 130})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["bpm"] == 140

async def test_delete_track_not_found(client: AsyncClient):
    response = await client.delete("/api/v1/tracks/nonexistent-id")
    assert response.status_code == 404
```

### Error Handling Tests
```python
async def test_duplicate_track_returns_409(client: AsyncClient):
    track_data = {"title": "Unique", "source": "yandex", "source_id": "123"}

    response1 = await client.post("/api/v1/tracks", json=track_data)
    assert response1.status_code == 201

    response2 = await client.post("/api/v1/tracks", json=track_data)
    assert response2.status_code == 409
```

## Test Data Conventions

```python
# Use descriptive test data
SAMPLE_TRACK = {
    "title": "Test Track - House",
    "artists": ["DJ Test"],
    "bpm": 128.0,
    "key": "Am",
    "camelot": "8A",
    "energy": 7
}

# Use factories for complex objects
def make_track(**overrides) -> dict:
    return {**SAMPLE_TRACK, **overrides}

# Test edge cases explicitly
@pytest.mark.parametrize("bpm", [20, 150, 300])  # min, mid, max
def test_valid_bpm_range(bpm: int):
    track = Track(title="Test", bpm=bpm)
    assert track.bpm == bpm
```

## Assertions

```python
# Status codes
assert response.status_code == 200  # OK
assert response.status_code == 201  # Created
assert response.status_code == 204  # No Content (DELETE)
assert response.status_code == 404  # Not Found
assert response.status_code == 409  # Conflict (duplicate)
assert response.status_code == 422  # Validation Error

# JSON response
data = response.json()
assert data["id"] is not None
assert data["title"] == expected_title
assert "error" not in data

# Lists
assert len(data) == expected_count
assert any(t["bpm"] == 128 for t in data)
```
