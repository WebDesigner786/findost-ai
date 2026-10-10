"""Scenario Pydantic Schemas"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.common import Money


class ScenarioShock(BaseModel):
    id: str
    kind: str
    label: str
    description: str
    percent: Optional[float] = None
    delayDays: Optional[int] = None
    amount: Optional[Money] = None
    active: bool

    model_config = ConfigDict(populate_by_name=True)


class RecoveryAction(BaseModel):
    id: str
    label: str
    description: str
    estimatedImpact: Money
    active: bool

    model_config = ConfigDict(populate_by_name=True)


class Scenario(BaseModel):
    id: str
    workspaceId: str
    title: str
    description: str
    shocks: List[ScenarioShock]
    recoveryActions: List[RecoveryAction]
    assumptions: List[str]
    simulatedShortageDate: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)
