"""Transaction Pydantic Schemas"""

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.common import Money


class TransactionBase(BaseModel):
    merchant: str
    direction: str = Field(..., description="inflow or outflow")
    category: str
    confidence: Optional[float] = 1.0
    reviewStatus: str = Field(default="confirmed", validation_alias="review_status")
    sourceRef: Optional[str] = Field(default=None, validation_alias="source_ref")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class TransactionOut(TransactionBase):
    id: str
    workspaceId: str = Field(..., validation_alias="workspace_id")
    occurredAt: str = Field(..., validation_alias="occurred_at")
    amount: Money
    isEdited: Optional[bool] = Field(default=False, validation_alias="is_edited")
    originalMerchant: Optional[str] = Field(default=None, validation_alias="original_merchant")
    originalCategory: Optional[str] = Field(default=None, validation_alias="original_category")
    originalAmount: Optional[Money] = Field(default=None, validation_alias="original_amount")
    correctionNote: Optional[str] = Field(default=None, validation_alias="correction_note")


class TransactionCreate(TransactionBase):
    occurredAt: str = Field(..., validation_alias="occurred_at")
    amount: Money


class ImportTransactionsPayload(BaseModel):
    transactions: List[TransactionCreate]


class UpdateTransactionPayload(BaseModel):
    merchant: Optional[str] = None
    category: Optional[str] = None
    amountPaisa: Optional[str] = None
    reviewStatus: Optional[str] = None
    correctionNote: Optional[str] = None
