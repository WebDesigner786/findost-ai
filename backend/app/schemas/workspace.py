"""Workspace Pydantic Schemas"""

from typing import List
from pydantic import BaseModel, Field, ConfigDict


class WorkspaceBase(BaseModel):
    id: str
    kind: str = Field(..., description="student, household, sme, enterprise")
    name: str
    displayName: str = Field(..., validation_alias="display_name")
    description: str
    currency: str = "PKR"
    timezone: str = "Asia/Karachi"
    features: List[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class WorkspaceOut(WorkspaceBase):
    pass
