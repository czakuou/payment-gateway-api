from functools import cache
from logging import getLevelNamesMapping
from typing import Annotated

import structlog
from fastapi import Depends
from structlog.typing import FilteringBoundLogger

from src.core.config import AppConfig, StripeConfig
from src.core.logging import get_structlog_processors


@cache
def get_app_config() -> AppConfig:
    return AppConfig()


AppConfigDependency = Annotated[AppConfig, Depends(get_app_config)]


@cache
def get_stripe_config() -> StripeConfig:
    return StripeConfig()


StripeConfigDependency = Annotated[StripeConfig, Depends(get_stripe_config)]


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
