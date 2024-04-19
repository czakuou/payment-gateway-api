from functools import cache
from logging import getLevelNamesMapping
from typing import Annotated, AsyncGenerator

from fastapi import Depends
import structlog
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.core.config import AppConfig, PostgresConfig
from src.core.db import get_db_engine, get_db_session
from src.core.logging import get_structlog_processors
from structlog.typing import FilteringBoundLogger


@cache
def get_app_config() -> AppConfig:
    return AppConfig()


AppConfigDependency = Annotated[AppConfig, Depends(get_app_config)]

@cache
def get_db_config() -> PostgresConfig:
    return PostgresConfig()


DBConfigDependency = Annotated[PostgresConfig, Depends(get_db_config)]

@cache
def get_logger(config: AppConfigDependency) -> FilteringBoundLogger:
    bound_logger_class = structlog.make_filtering_bound_logger(getLevelNamesMapping()[config.log_level])
    logger = structlog.WriteLogger()
    processors = get_structlog_processors(config)

    bound_logger: FilteringBoundLogger = structlog.wrap_logger(
        logger=logger, processors=processors, wrapper_class=bound_logger_class, context={}
    )
    return bound_logger


LoggerDependency = Annotated[FilteringBoundLogger, Depends(get_logger)]


@cache
def _get_db_engine(config: DBConfigDependency) -> AsyncEngine:
    return get_db_engine(config)


DBEngineDependency = Annotated[AsyncEngine, Depends(_get_db_engine)]


async def _get_db_session(engine: DBEngineDependency) -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session(engine=engine):
        yield session


DBSessionDependency = Annotated[AsyncSession, Depends(_get_db_session)]
