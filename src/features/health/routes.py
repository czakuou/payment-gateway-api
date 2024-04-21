from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import select, text

from src.core.db.dependencies import DBSessionDependency
from src.core.dependencies import AppConfigDependency

router = APIRouter()


class HealthResponse(BaseModel):
    version: str = Field(description="version (commit short SHA)")


@router.get("/health", response_model=HealthResponse)
async def health(config: AppConfigDependency, db: DBSessionDependency) -> dict[str, str]:
    query = select(text("1"))
    await db.execute(query)

    return {"version": config.version}
