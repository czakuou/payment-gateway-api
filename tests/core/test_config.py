from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.config import AppConfig

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


def test_app_config_multiple_allowed_hosts(monkeypatch: MonkeyPatch) -> None:
    # given
    monkeypatch.setenv("ALLOWED_HOSTS", '["example.com","other.com"]')

    # when
    config = AppConfig()

    # then
    assert config.allowed_hosts == ("example.com", "other.com")
