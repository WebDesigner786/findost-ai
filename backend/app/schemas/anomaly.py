"""Anomaly Pydantic Schemas"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.common import Money


class AnomalyOut(BaseModel):
    id: str
    workspaceId: str = Field(..., validation_alias="workspace_id")
    kind: str
    severity: str  # info, warning, critical
    title: str
    explanation: str
    amount: Optional[Money] = None
    period: str
    transactionIds: List[str] = Field(default_factory=list, validation_alias="transaction_ids")
    sourceRefs: List[str] = Field(default_factory=list, validation_alias="source_refs")
    detectedAt: str = Field(..., validation_alias="detected_at")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
