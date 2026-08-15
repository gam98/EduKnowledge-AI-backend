"""Async database and Redis connectivity primitives."""

from collections.abc import AsyncIterator
from typing import Protocol, cast

from redis.asyncio import Redis, from_url
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings


class DependencyChecker(Protocol):
    async def check(self) -> dict[str, bool]: ...


class InfrastructureChecker:
    """Checks required infrastructure without exposing connection details to callers."""

    def __init__(self, engine: AsyncEngine, redis_client: Redis) -> None:
        self._engine = engine
        self._redis = redis_client
        self.session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def check(self) -> dict[str, bool]:
        database_ready = False
        redis_ready = False
        try:
            async with self._engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            database_ready = True
        except Exception:  # Dependency state is intentionally reported as a boolean.
            database_ready = False
        try:
            redis_ready = bool(await self._redis.ping())
        except Exception:
            redis_ready = False
        return {"database": database_ready, "redis": redis_ready}

    async def close(self) -> None:
        await self._engine.dispose()
        await self._redis.aclose()


def build_infrastructure(settings: Settings) -> InfrastructureChecker:
    """Build dependency clients lazily during app creation, not module import."""
    engine = create_async_engine(str(settings.database_url), pool_pre_ping=True)
    redis_client = cast(Redis, from_url(str(settings.redis_url), decode_responses=True))  # type: ignore[no-untyped-call]
    return InfrastructureChecker(engine, redis_client)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Placeholder session dependency; repositories are added with the persistence slice."""
    raise RuntimeError("Database session dependency is not configured until the persistence slice.")
    yield  # pragma: no cover
