from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.core.config import AppConfig
from src.core.dependencies import get_app_config
from src.core.fastapi import get_application

if TYPE_CHECKING:
    from collections.abc import Generator

    from fastapi import FastAPI


pytest_plugins = [
    "tests.fixtures.clients",
]


@pytest.fixture(scope="session")
def app_config() -> AppConfig:
    return AppConfig(error_details=True)


@pytest.fixture(scope="session")
def fastapi_app_session(app_config: AppConfig) -> FastAPI:
    return get_application(config=app_config)


@pytest.fixture
def fastapi_app(fastapi_app_session: FastAPI, app_config: AppConfig) -> Generator[FastAPI, None, None]:
    fastapi_app_session.dependency_overrides[get_app_config] = lambda: app_config

    yield fastapi_app_session

    fastapi_app_session.dependency_overrides.clear()
