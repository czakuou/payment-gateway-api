from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import status

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

    from src.core.config import AppConfig


def test_health(client: TestClient, app_config: AppConfig) -> None:
    # when
    response = client.get("/api/health")

    # then
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"version": app_config.version}
