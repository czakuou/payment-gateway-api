
from fastapi import APIRouter, FastAPI

from src.core.config import AppConfig
from src.core.dependencies import get_app_config
from starlette.types import Lifespan
from src.health.endpoints import router as health_router

from src.core.logging import configure as configure_logging

def get_router() -> APIRouter:
    router = APIRouter()
    
    router.include_router(health_router, tags=["Health"])
    
    return router

def get_application(config: AppConfig, router: APIRouter, lifespan: Lifespan[FastAPI] | None = None) -> FastAPI:
    configure_logging(app_config=config)

    application = FastAPI(
        title=config.project_name,
        version=config.version,
        debug=config.debug,
        openapi_url="/contract/openapi.json" if config.docs else None,
        docs_url="/contract/swagger",
        redoc_url="/contract/redoc",
    )

    application.include_router(router)

    return application

app = get_application(config=get_app_config(), router=get_router())
