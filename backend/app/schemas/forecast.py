"""Forecast Pydantic Schemas"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.common import Money


class ForecastPointOut(BaseModel):
    date: str
    baseline: Money
    p10: Optional[Money] = None
    p50: Optional[Money] = None
    p90: Optional[Money] = None
    simulated: Optional[Money] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class ForecastOut(BaseModel):
    workspaceId: str = Field(..., validation_alias="workspace_id")
    generatedAt: str = Field(..., validation_alias="generated_at")
    horizonDays: int = Field(default=90, validation_alias="horizon_days")
    points: List[ForecastPointOut]
    assumptions: List[str]
    source: str = "api"

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
