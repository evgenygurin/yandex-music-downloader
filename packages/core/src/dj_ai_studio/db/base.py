"""SQLAlchemy async database setup for DJ AI Studio.

Provides async engine, session factory, and base declarative model
for all ORM models.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

# Global engine and session factory - initialized by init_db()
_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


def get_db_url(db_path: str) -> str:
    """Convert a file path to a SQLite async URL.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        SQLite async connection URL.

    Examples:
        >>> get_db_url("/data/dj_studio.db")
        'sqlite+aiosqlite:////data/dj_studio.db'
        >>> get_db_url("./local.db")
        'sqlite+aiosqlite:///./local.db'
    """
    return f"sqlite+aiosqlite:///{db_path}"


async def init_db(db_url: str) -> None:
    """Initialize the database engine and create all tables.

    This should be called once at application startup.

    Args:
        db_url: Database connection URL (use get_db_url() for SQLite).

    Example:
        >>> import asyncio
        >>> asyncio.run(init_db(get_db_url("./dj_studio.db")))
    """
    global _engine, _async_session_factory

    _engine = create_async_engine(
        db_url,
        echo=False,
        future=True,
    )

    _async_session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    # Create all tables
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close the database engine.

    Should be called at application shutdown.
    """
    global _engine, _async_session_factory

    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session.

    Yields an AsyncSession that is automatically committed on success
    or rolled back on exception.

    Yields:
        AsyncSession: Database session for queries and mutations.

    Raises:
        RuntimeError: If init_db() has not been called.

    Example:
        >>> async for session in get_session():
        ...     result = await session.execute(select(TrackORM))
        ...     tracks = result.scalars().all()
    """
    if _async_session_factory is None:
        raise RuntimeError(
            "Database not initialized. Call init_db() first."
        )

    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager version of get_session().

    Useful when not using dependency injection.

    Yields:
        AsyncSession: Database session for queries and mutations.

    Example:
        >>> async with get_session_context() as session:
        ...     track = TrackORM(title="Test", ...)
        ...     session.add(track)
    """
    if _async_session_factory is None:
        raise RuntimeError(
            "Database not initialized. Call init_db() first."
        )

    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
