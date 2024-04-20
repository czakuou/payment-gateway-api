from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

    from src.core.config import AppConfig


def test_health(client: TestClient, app_config: AppConfig) -> None:
    # when
    response = client.get("health")

    # then
    assert response.status_code == 200
    assert response.json() == {"version": app_config.version}
