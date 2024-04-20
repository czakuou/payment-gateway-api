from typing import TYPE_CHECKING

import pytest
from starlette.testclient import TestClient

if TYPE_CHECKING:
    from fastapi import FastAPI


@pytest.fixture
def unauthenticated_client(
    fastapi_app: "FastAPI",
) -> TestClient:
    return TestClient(app=fastapi_app)
