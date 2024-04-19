
from fastapi import APIRouter


from src.core.dependencies import AppConfigDependency
from src.health.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(config: AppConfigDependency) -> dict[str, str]:
    return {"version": config.version}
