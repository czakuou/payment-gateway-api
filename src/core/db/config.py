from urllib.parse import quote, urlencode

from pydantic import PostgresDsn, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="postgres_",
        extra="ignore",
        frozen=True,
    )

    scheme: str = "postgresql+psycopg"
    user: str
    password: SecretStr
    host: str
    port: int = 5432
    db: str
    connect_timeout: int = 10

    @computed_field  # type: ignore[misc]
    @property
    def dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme=self.scheme,
            username=self.user,
            password=quote(self.password.get_secret_value(), safe=[]),
            host=self.host,
            port=self.port,
            path=self.db,
            query=urlencode({"connect_timeout": self.connect_timeout}),
        )
