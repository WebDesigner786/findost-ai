"""Reports, Evidence, Credit Readiness & Preliminary Tax Router"""

from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.workspace import Workspace
from app.models.recommendation import Recommendation
from app.schemas.report import (
    ReportsResponse,
    RecommendationOut,
    CreditReadinessOut,
    CreditReadinessFactor,
    TaxPreviewOut,
    TaxDeductibleCategory,
)
from app.schemas.common import Money

router = APIRouter(prefix="/api/workspaces", tags=["Reports"])


@router.get("/{workspace_id}/reports", response_model=ReportsResponse)
def get_workspace_reports(workspace_id: str, db: Session = Depends(get_db)):
    """Returns evidence-grounded recommendations, credit assessment, and preliminary tax preview."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found.",
        )

    # Fetch Recommendations from database
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.workspace_id == workspace_id)
        .all()
    )

    rec_outs = [
        RecommendationOut(
            id=r.id,
            workspaceId=r.workspace_id,
            title=r.title,
            plainReason=r.plain_reason,
            estimatedImpact=Money.from_decimal(Decimal(str(r.estimated_impact))),
            timeHorizon=r.time_horizon,
            category=r.category,
            evidenceTransactionIds=r.evidence_transaction_ids or [],
            evidenceSourceRefs=r.evidence_source_refs or [],
            assumptions=r.assumptions or [],
        )
        for r in recs
    ]

    # Persona-specific Credit Readiness & Tax Preview Profiles
    if ws.kind == "sme":
        credit_readiness = CreditReadinessOut(
            workspaceId=workspace_id,
            overallScore=78,
            factors=[
                CreditReadinessFactor(
                    name="Cash Buffer & Reserve Coverage",
                    score=82,
                    weight=35,
                    status="good",
                    details="Current working balance provides 97 days runway against fixed supplier expenses.",
                ),
                CreditReadinessFactor(
                    name="Supplier Invoice Settlement Consistency",
                    score=85,
                    weight=25,
                    status="good",
                    details="All distributor invoices paid within 14-day trade credit window.",
                ),
                CreditReadinessFactor(
                    name="Receivable Collection Turnaround",
                    score=62,
                    weight=25,
                    status="moderate",
                    details="Average debtor aging is 48 days (recommended benchmark is under 30 days).",
                ),
                CreditReadinessFactor(
                    name="Commercial Meter & Tax Record",
                    score=75,
                    weight=15,
                    status="good",
                    details="Commercial LESCO meter on-time payment track record across 12 cycles.",
                ),
            ],
            isShariahCompliantWording=True,
            disclaimer="Illustrative readiness score for SME financing programs. Does not constitute formal underwriting.",
        )

        tax_preview = TaxPreviewOut(
            workspaceId=workspace_id,
            taxYear="TY 2026-2027",
            estimatedGrossInflow=Money.from_decimal(Decimal("17400000.00")),
            totalExpenses=Money.from_decimal(Decimal("15840000.00")),
            deductibleExpenses=Money.from_decimal(Decimal("14600000.00")),
            estimatedTaxableIncome=Money.from_decimal(Decimal("2800000.00")),
            illustrativeEstimatedTax=Money.from_decimal(Decimal("325000.00")),
            deductibleCategories=[
                TaxDeductibleCategory(
                    category="Cost of Goods Sold (Verified Supplier Invoices)",
                    spent=Money.from_decimal(Decimal("13200000.00")),
                    deductiblePercentage=100,
                    deductibleAmount=Money.from_decimal(Decimal("13200000.00")),
                    note="Allowable under Section 20 of Income Tax Ordinance with documented invoices.",
                ),
                TaxDeductibleCategory(
                    category="Commercial Shop Rent & Municipal Charges",
                    spent=Money.from_decimal(Decimal("900000.00")),
                    deductiblePercentage=100,
                    deductibleAmount=Money.from_decimal(Decimal("900000.00")),
                    note="Rent paid via banking channel with withholding challan.",
                ),
            ],
            disclaimer="Preliminary Estimate — FBR Validation Required. Not certified tax advice.",
        )
    elif ws.kind == "enterprise":
        credit_readiness = CreditReadinessOut(
            workspaceId=workspace_id,
            overallScore=84,
            factors=[
                CreditReadinessFactor(
                    name="Debt Service Coverage Ratio (DSCR)",
                    score=88,
                    weight=35,
                    status="good",
                    details="Operating EBITDA covers corporate facilities 2.4x.",
                ),
                CreditReadinessFactor(
                    name="Export LC Turnover & State Bank Compliance",
                    score=92,
                    weight=25,
                    status="good",
                    details="Full E-Form tracking and transparent FX proceeds repatriation.",
                ),
            ],
            isShariahCompliantWording=False,
            disclaimer="Corporate credit health indicator for bank consortium financing.",
        )
        tax_preview = TaxPreviewOut(
            workspaceId=workspace_id,
            taxYear="TY 2026-2027",
            estimatedGrossInflow=Money.from_decimal(Decimal("580000000.00")),
            totalExpenses=Money.from_decimal(Decimal("506000000.00")),
            deductibleExpenses=Money.from_decimal(Decimal("478000000.00")),
            estimatedTaxableIncome=Money.from_decimal(Decimal("74000000.00")),
            illustrativeEstimatedTax=Money.from_decimal(Decimal("21460000.00")),
            deductibleCategories=[],
            disclaimer="Preliminary Estimate — FBR Validation Required. Subject to Corporate Tax Return audit.",
        )
    else:
        # Student / Household
        credit_readiness = CreditReadinessOut(
            workspaceId=workspace_id,
            overallScore=74 if ws.kind == "household" else 65,
            factors=[
                CreditReadinessFactor(
                    name="Inflow Regularity & Budget Buffer",
                    score=80 if ws.kind == "household" else 68,
                    weight=50,
                    status="good" if ws.kind == "household" else "moderate",
                    details="Consistent month-over-month inflow deposits.",
                ),
            ],
            isShariahCompliantWording=True,
            disclaimer="Personal Financial Health Indicator. Not a formal credit rating.",
        )
        tax_preview = TaxPreviewOut(
            workspaceId=workspace_id,
            taxYear="TY 2026-2027",
            estimatedGrossInflow=Money.from_decimal(Decimal("4200000.00") if ws.kind == "household" else Decimal("540000.00")),
            totalExpenses=Money.from_decimal(Decimal("3540000.00") if ws.kind == "household" else Decimal("458400.00")),
            deductibleExpenses=Money.from_decimal(Decimal("888000.00") if ws.kind == "household" else Decimal("0.00")),
            estimatedTaxableIncome=Money.from_decimal(Decimal("3312000.00") if ws.kind == "household" else Decimal("0.00")),
            illustrativeEstimatedTax=Money.from_decimal(Decimal("342000.00") if ws.kind == "household" else Decimal("0.00")),
            deductibleCategories=[],
            disclaimer="Preliminary Estimate — FBR Validation Required.",
        )

    return ReportsResponse(
        recommendations=rec_outs,
        creditReadiness=credit_readiness,
        taxPreview=tax_preview,
    )
