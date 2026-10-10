"""Reports, Credit Readiness & Tax Preview Schemas"""

from typing import List
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.common import Money


class RecommendationOut(BaseModel):
    id: str
    workspaceId: str = Field(..., validation_alias="workspace_id")
    title: str
    plainReason: str = Field(..., validation_alias="plain_reason")
    estimatedImpact: Money
    timeHorizon: str = Field(..., validation_alias="time_horizon")
    category: str
    evidenceTransactionIds: List[str] = Field(default_factory=list, validation_alias="evidence_transaction_ids")
    evidenceSourceRefs: List[str] = Field(default_factory=list, validation_alias="evidence_source_refs")
    assumptions: List[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class CreditReadinessFactor(BaseModel):
    name: str
    score: int
    weight: int
    status: str
    details: str


class CreditReadinessOut(BaseModel):
    workspaceId: str
    overallScore: int
    factors: List[CreditReadinessFactor]
    isShariahCompliantWording: bool
    disclaimer: str


class TaxDeductibleCategory(BaseModel):
    category: str
    spent: Money
    deductiblePercentage: int
    deductibleAmount: Money
    note: str


class TaxPreviewOut(BaseModel):
    workspaceId: str
    taxYear: str
    estimatedGrossInflow: Money
    totalExpenses: Money
    deductibleExpenses: Money
    estimatedTaxableIncome: Money
    illustrativeEstimatedTax: Money
    deductibleCategories: List[TaxDeductibleCategory]
    disclaimer: str


class ReportsResponse(BaseModel):
    recommendations: List[RecommendationOut]
    creditReadiness: CreditReadinessOut
    taxPreview: TaxPreviewOut
