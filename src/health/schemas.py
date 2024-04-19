from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    version: str = Field(description="version (commit short SHA)")
