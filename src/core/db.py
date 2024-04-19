from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, AsyncSession, create_async_engine

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from src.core.config import PostgresConfig


@cache
def get_db_engine(config: PostgresConfig) -> AsyncEngine:
    return create_async_engine(url=str(config.dsn))


async def get_db_session(engine: AsyncEngine | AsyncConnection, **kw: Any) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(bind=engine, autoflush=True, expire_on_commit=True, **kw) as session:
        yield session
