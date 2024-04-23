from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", frozen=True)

    project_name: str = "Payment Gateway APP"
    version: str = "v1"
    environment: str = "local"

    debug: bool = False
    docs: bool = False

    allowed_hosts: tuple[str, ...] = ("*",)

    log_level: str = "INFO"
    log_json: bool = True
