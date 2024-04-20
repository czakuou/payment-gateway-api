from unittest.mock import ANY

from src.core.db import get_db_engine
from src.db.config import PostgresConfig


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