from collections.abc import AsyncGenerator
from functools import cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.core.db.config import PostgresConfig
from src.core.db.sql_db import get_db_engine, get_db_session


@cache
def get_db_config() -> PostgresConfig:
    return PostgresConfig()


DBConfigDependency = Annotated[PostgresConfig, Depends(get_db_config)]


@cache
def _get_db_engine(config: DBConfigDependency) -> AsyncEngine:
    return get_db_engine(config)


DBEngineDependency = Annotated[AsyncEngine, Depends(_get_db_engine)]


async def _get_db_session(
    engine: DBEngineDependency,
) -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session(engine=engine):
        yield session


DBSessionDependency = Annotated[AsyncSession, Depends(_get_db_session)]
