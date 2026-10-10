"""Workspaces & Dashboard Router"""

from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.workspace import Workspace
from app.models.transaction import Transaction
from app.models.udhaar import UdhaarRecord
from app.models.anomaly import Anomaly
from app.schemas.workspace import WorkspaceOut
from app.schemas.dashboard import DashboardData, DashboardKpis
from app.schemas.transaction import TransactionOut
from app.schemas.anomaly import AnomalyOut
from app.schemas.common import Money, decimal_to_paisa_string
from app.services.calculator import (
    compute_monthly_run_rate,
    calculate_runway_days,
    generate_deterministic_forecast,
)

router = APIRouter(prefix="/api/workspaces", tags=["Workspaces"])


@router.get("", response_model=List[WorkspaceOut])
def list_workspaces(db: Session = Depends(get_db)):
    """Retrieves all registered financial workspaces."""
    workspaces = db.query(Workspace).all()
    return [
        WorkspaceOut(
            id=ws.id,
            kind=ws.kind,
            name=ws.name,
            displayName=ws.display_name,
            description=ws.description,
            currency=ws.currency,
            timezone=ws.timezone,
            features=ws.features or [],
        )
        for ws in workspaces
    ]


@router.get("/{workspace_id}/dashboard", response_model=DashboardData)
def get_workspace_dashboard(workspace_id: str, db: Session = Depends(get_db)):
    """Computes live dashboard KPIs, deterministic runway, and 90-day cash forecast."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found.",
        )

    # Fetch recent transactions
    txs = (
        db.query(Transaction)
        .filter(Transaction.workspace_id == workspace_id)
        .order_by(Transaction.occurred_at.desc())
        .all()
    )

    # Compute run rate
    inflow_dec, outflow_dec = compute_monthly_run_rate(txs)
    starting_balance = Decimal(str(ws.starting_balance))
    net_balance = starting_balance + inflow_dec - outflow_dec

    runway_days = calculate_runway_days(net_balance, outflow_dec, inflow_dec)

    # Fetch Udhaar ledger summary
    udhaar_records = (
        db.query(UdhaarRecord)
        .filter(UdhaarRecord.workspace_id == workspace_id)
        .all()
    )
    total_outstanding_dec = Decimal("0.00")
    overdue_count = 0
    for ud in udhaar_records:
        if ud.status != "settled":
            total_outstanding_dec += Decimal(str(ud.outstanding))
            if ud.status == "overdue":
                overdue_count += 1

    # Fetch Anomalies
    anomalies = (
        db.query(Anomaly)
        .filter(Anomaly.workspace_id == workspace_id)
        .order_by(Anomaly.detected_at.desc())
        .all()
    )

    # Generate 90-day deterministic forecast
    forecast = generate_deterministic_forecast(
        workspace_id=workspace_id,
        starting_balance=net_balance,
        transactions=txs,
    )

    # Prepare serialized response
    kpis = DashboardKpis(
        netBalance=decimal_to_paisa_string(net_balance),
        runwayDays=runway_days,
        monthlyOutflow=decimal_to_paisa_string(outflow_dec),
        monthlyInflow=decimal_to_paisa_string(inflow_dec),
        totalOutstandingUdhaar=decimal_to_paisa_string(total_outstanding_dec),
        overdueUdhaarCount=overdue_count,
    )

    recent_tx_outs = [
        TransactionOut(
            id=t.id,
            workspaceId=t.workspace_id,
            occurredAt=t.occurred_at.isoformat(),
            merchant=t.merchant,
            amount=Money.from_decimal(Decimal(str(t.amount))),
            direction=t.direction,
            category=t.category,
            confidence=float(t.confidence),
            reviewStatus=t.review_status,
            sourceRef=t.source_ref,
            isEdited=t.is_edited,
            originalMerchant=t.original_merchant,
            originalCategory=t.original_category,
            originalAmount=Money.from_decimal(Decimal(str(t.original_amount))) if t.original_amount else None,
            correctionNote=t.correction_note,
        )
        for t in txs[:10]
    ]

    anomaly_outs = [
        AnomalyOut(
            id=a.id,
            workspaceId=a.workspace_id,
            kind=a.kind,
            severity=a.severity,
            title=a.title,
            explanation=a.explanation,
            amount=Money.from_decimal(Decimal(str(a.amount))) if a.amount else None,
            period=a.period,
            transactionIds=a.transaction_ids or [],
            sourceRefs=a.source_refs or [],
            detectedAt=a.detected_at.isoformat(),
        )
        for a in anomalies
    ]

    return DashboardData(
        workspace=WorkspaceOut(
            id=ws.id,
            kind=ws.kind,
            name=ws.name,
            displayName=ws.display_name,
            description=ws.description,
            currency=ws.currency,
            timezone=ws.timezone,
            features=ws.features or [],
        ),
        kpis=kpis,
        forecast=forecast,
        anomalies=anomaly_outs,
        recentTransactions=recent_tx_outs,
        freshnessTimestamp="Live from Supabase PostgreSQL engine",
    )
