from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, FastAPI

from src.core.dependencies import get_app_config
from src.core.logging import configure as configure_logging
from src.features.health.routes import router as health_router

if TYPE_CHECKING:
    from src.core.config import AppConfig


def get_router() -> APIRouter:
    router = APIRouter()

    router.include_router(health_router, tags=["Health"])

    return router


def get_application(config: AppConfig) -> FastAPI:
    configure_logging(app_config=config)

    application = FastAPI(
        title=config.project_name,
        version=config.version,
        debug=config.debug,
        openapi_url="/contract/openapi.json" if config.docs else None,
        docs_url="/contract/swagger",
        redoc_url="/contract/redoc",
    )

    application.include_router(get_router())

    return application


app = get_application(config=get_app_config())
