from functools import cache
from typing import Annotated

from fastapi import Depends

from src.core.config import AppConfig


@cache
def get_app_config() -> AppConfig:
    return AppConfig()


AppConfigDependency = Annotated[AppConfig, Depends(get_app_config)]