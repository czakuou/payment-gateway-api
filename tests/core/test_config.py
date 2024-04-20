from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import ANY

from src.core.config import AppConfig, PostgresConfig
from src.core.db import get_db_engine

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


def test_app_config_multiple_allowed_hosts(monkeypatch: MonkeyPatch) -> None:
    # given
    monkeypatch.setenv("ALLOWED_HOSTS", '["example.com","other.com"]')

    # when
    config = AppConfig()

    # then
    assert config.allowed_hosts == ("example.com", "other.com")


async def test_engine_connect_args() -> None:
    # given
    config = PostgresConfig(user="test-user", password="test-password", host="test-host", db="test-db")

    # when
    engine = get_db_engine(config)

    # then
    args, kwargs = engine.dialect.create_connect_args(engine.url)

    assert args == []
    assert kwargs == {
        "connect_timeout": "10",
        "context": ANY,
        "dbname": "test-db",
        "host": "test-host",
        "password": "test-password",
        "port": 5432,
        "user": "test-user",
    }
