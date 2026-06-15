"""Async database engine and session factory.

Provides:
* A module-level :pydata:`async_engine` bound to the configured
  MySQL DSN (aiomysql driver).
* An :pydata:`async_session_factory` that produces
  :class:`~sqlalchemy.ext.asyncio.AsyncSession` instances.
* A :func:`get_db` async generator suitable for FastAPI's
  ``Depends()`` dependency injection.
"""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.config import settings

# ── Engine ────────────────────────────────────────────────────────────

async_engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=False,
)

# ── Session factory ──────────────────────────────────────────────────

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# ── FastAPI dependency ────────────────────────────────────────────────


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an :class:`AsyncSession` and guarantee cleanup.

    Usage inside a FastAPI route::

        @router.post("/profiles")
        async def create(session: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db() -> None:
    """Initialize database tables."""
    from backend.database.models import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
