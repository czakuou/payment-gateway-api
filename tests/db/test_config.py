import string

from pydantic import SecretStr

from src.db.config import PostgresConfig


def test_special_characters_in_password() -> None:
    # given
    config = PostgresConfig(user="user", password=SecretStr(string.punctuation), host="host", db="db")

    # then
    assert str(config.dsn) == (
        "postgresql+psycopg://user:%21%22%23%24%25%26%27%28%29%2A%2B%2C-.%2F%3A%3B%3C%3D%3E%3F%40%5B%5C%5D%5E_%60%7B%7C%7D~@host:5432/db?connect_timeout=10"
    )
