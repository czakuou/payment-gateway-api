from fastapi import APIRouter
from sqlalchemy import select, text

from src.core.dependencies import AppConfigDependency, DBSessionDependency
from src.health.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(config: AppConfigDependency, db: DBSessionDependency) -> dict[str, str]:
    query = select(text("1"))
    await db.execute(query)

    return {"version": config.version}
