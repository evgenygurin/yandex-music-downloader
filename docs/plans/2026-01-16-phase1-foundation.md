# Phase 1: Foundation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Set up monorepo structure with core Python package, data models, and basic FastAPI endpoints.

---

## Task 1: Initialize Monorepo Structure

**Files:**
- Create: `pyproject.toml` (root workspace)
- Create: `pnpm-workspace.yaml`
- Create: `turbo.json`
- Create: `apps/web/.gitkeep`
- Create: `apps/api/.gitkeep`
- Create: `apps/mcp/.gitkeep`
- Create: `packages/core/pyproject.toml`
- Create: `packages/core/src/dj_ai_studio/__init__.py`
- Create: `packages/cli/.gitkeep`

**Steps:**
1. Create directory structure for monorepo
2. Create root pyproject.toml with uv workspace config
3. Create pnpm-workspace.yaml for Node packages
4. Create turbo.json for task orchestration
5. Create packages/core with Python package setup
6. Commit

---

## Task 2: Create Core Data Models

**Files:**
- Create: `packages/core/src/dj_ai_studio/models/__init__.py`
- Create: `packages/core/src/dj_ai_studio/models/track.py`
- Create: `packages/core/src/dj_ai_studio/models/set.py`
- Create: `packages/core/src/dj_ai_studio/models/playlist.py`

**Steps:**
1. Create Pydantic models for Track with all fields from design
2. Create Pydantic models for Set and SetTrack
3. Create Pydantic models for Playlist
4. Add __init__.py with exports
5. Commit

---

## Task 3: Create SQLAlchemy ORM Models

**Files:**
- Create: `packages/core/src/dj_ai_studio/db/__init__.py`
- Create: `packages/core/src/dj_ai_studio/db/base.py`
- Create: `packages/core/src/dj_ai_studio/db/models.py`

**Steps:**
1. Create SQLAlchemy 2.0 base with async engine setup
2. Create ORM models matching Pydantic models
3. Add JSON fields for lists (artists, mood, genre, tags)
4. Create db/__init__.py with exports
5. Commit

---

## Task 4: Create Database Migrations Setup

**Files:**
- Create: `packages/core/alembic.ini`
- Create: `packages/core/alembic/env.py`
- Create: `packages/core/alembic/versions/.gitkeep`

**Steps:**
1. Add alembic to dependencies
2. Create alembic.ini with SQLite config
3. Create env.py with async support
4. Generate initial migration
5. Commit

---

## Task 5: Create FastAPI App Skeleton

**Files:**
- Create: `apps/api/pyproject.toml`
- Create: `apps/api/src/dj_ai_api/__init__.py`
- Create: `apps/api/src/dj_ai_api/main.py`
- Create: `apps/api/src/dj_ai_api/config.py`
- Create: `apps/api/src/dj_ai_api/deps.py`

**Steps:**
1. Create pyproject.toml with FastAPI dependencies
2. Create main.py with FastAPI app, CORS, lifespan
3. Create config.py with Pydantic Settings
4. Create deps.py with database session dependency
5. Commit

---

## Task 6: Create Track CRUD Endpoints

**Files:**
- Create: `apps/api/src/dj_ai_api/routers/__init__.py`
- Create: `apps/api/src/dj_ai_api/routers/tracks.py`

**Steps:**
1. Create tracks router with CRUD endpoints:
   - GET /tracks (list with filters)
   - GET /tracks/{id}
   - POST /tracks
   - PATCH /tracks/{id}
   - DELETE /tracks/{id}
2. Add to main.py router
3. Commit

---

## Task 7: Create Set CRUD Endpoints

**Files:**
- Create: `apps/api/src/dj_ai_api/routers/sets.py`

**Steps:**
1. Create sets router with CRUD endpoints:
   - GET /sets
   - GET /sets/{id}
   - POST /sets
   - PATCH /sets/{id}
   - DELETE /sets/{id}
   - POST /sets/{id}/tracks (add track)
   - DELETE /sets/{id}/tracks/{position} (remove track)
2. Add to main.py router
3. Commit

---

## Task 8: Add Tests for Core Models

**Files:**
- Create: `packages/core/tests/__init__.py`
- Create: `packages/core/tests/test_models.py`

**Steps:**
1. Write tests for Track model validation
2. Write tests for Set model with tracks
3. Write tests for Playlist model
4. Run tests, ensure passing
5. Commit

---

## Task 9: Add Tests for API Endpoints

**Files:**
- Create: `apps/api/tests/__init__.py`
- Create: `apps/api/tests/conftest.py`
- Create: `apps/api/tests/test_tracks.py`
- Create: `apps/api/tests/test_sets.py`

**Steps:**
1. Create conftest.py with test client and test DB
2. Write tests for tracks CRUD
3. Write tests for sets CRUD
4. Run tests, ensure passing
5. Commit

---

## Task 10: Update CI Workflow

**Files:**
- Modify: `.github/workflows/ci.yml`

**Steps:**
1. Add job for packages/core tests
2. Add job for apps/api tests
3. Update paths for monorepo structure
4. Commit
