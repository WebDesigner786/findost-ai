"""Udhaar & Receivables Pydantic Schemas"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.common import Money


class UdhaarRecordOut(BaseModel):
    id: str
    workspaceId: str = Field(..., validation_alias="workspace_id")
    customerName: str = Field(..., validation_alias="customer_name")
    phone: Optional[str] = None
    issuedAt: str = Field(..., validation_alias="issued_at")
    dueAt: Optional[str] = Field(default=None, validation_alias="due_at")
    outstanding: Money
    status: str = Field(..., description="current, overdue, settled")
    ageBucket: str = Field(..., validation_alias="age_bucket")
    sourceRef: Optional[str] = Field(default=None, validation_alias="source_ref")
    notes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class SettlementPayload(BaseModel):
    udhaarId: str
    amountPaisa: str
    notes: Optional[str] = None


class SettlementResponse(BaseModel):
    record: UdhaarRecordOut
    updatedBalancePaisa: str
