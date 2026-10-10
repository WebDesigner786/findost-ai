"""Udhaar (Receivables) Router"""

import time
from datetime import date
from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.udhaar import UdhaarRecord
from app.models.workspace import Workspace
from app.models.transaction import Transaction
from app.schemas.udhaar import UdhaarRecordOut, SettlementPayload, SettlementResponse
from app.schemas.common import Money, paisa_string_to_decimal, decimal_to_paisa_string
from app.services.calculator import compute_monthly_run_rate

router = APIRouter(tags=["Udhaar"])


@router.get("/api/workspaces/{workspace_id}/udhaar", response_model=List[UdhaarRecordOut])
def get_workspace_udhaar(workspace_id: str, db: Session = Depends(get_db)):
    """Retrieves all customer Udhaar (khata) records for a workspace."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found.",
        )

    records = (
        db.query(UdhaarRecord)
        .filter(UdhaarRecord.workspace_id == workspace_id)
        .order_by(UdhaarRecord.outstanding.desc())
        .all()
    )

    return [
        UdhaarRecordOut(
            id=r.id,
            workspaceId=r.workspace_id,
            customerName=r.customer_name,
            phone=r.phone,
            issuedAt=r.issued_at.isoformat(),
            dueAt=r.due_at.isoformat() if r.due_at else None,
            outstanding=Money.from_decimal(Decimal(str(r.outstanding))),
            status=r.status,
            ageBucket=r.age_bucket,
            sourceRef=r.source_ref,
            notes=r.notes,
        )
        for r in records
    ]


@router.post("/api/udhaar/{udhaar_id}/settlements", response_model=SettlementResponse)
def settle_udhaar_record(
    udhaar_id: str, payload: SettlementPayload, db: Session = Depends(get_db)
):
    """Executes partial or full FIFO settlement on a customer Udhaar record.
    
    1. Reduces the debtor's outstanding balance.
    2. Updates status to 'settled' if remaining balance hits zero.
    3. Injects an offsetting cash inflow Transaction into the workspace.
    4. Recomputes and returns updated net cash balance.
    """
    rec = db.query(UdhaarRecord).filter(UdhaarRecord.id == udhaar_id).first()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Udhaar record '{udhaar_id}' not found.",
        )

    settle_amount_dec = paisa_string_to_decimal(payload.amountPaisa)
    current_outstanding_dec = Decimal(str(rec.outstanding))

    if settle_amount_dec <= Decimal("0.00"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Settlement amount must be positive.",
        )

    # Cap settlement to current outstanding balance
    actual_settle_dec = min(settle_amount_dec, current_outstanding_dec)
    remaining_dec = current_outstanding_dec - actual_settle_dec

    rec.outstanding = remaining_dec
    if remaining_dec == Decimal("0.00"):
        rec.status = "settled"

    if payload.notes:
        existing_notes = rec.notes or ""
        rec.notes = f"{existing_notes} | Settled Rs. {actual_settle_dec:,.2f}: {payload.notes}".strip(" |")

    # Inject an offsetting cash inflow transaction
    ts = int(time.time() * 1000)
    inflow_tx = Transaction(
        id=f"tx-settle-{ts}",
        workspace_id=rec.workspace_id,
        occurred_at=date.today(),
        merchant=f"Udhaar Recovery: {rec.customer_name}",
        amount=actual_settle_dec,
        direction="inflow",
        category="Debt Recovery",
        confidence=Decimal("1.000"),
        review_status="confirmed",
        source_ref=f"REC-{rec.source_ref or 'UDHAAR'}",
    )
    db.add(inflow_tx)
    db.commit()
    db.refresh(rec)

    # Compute updated net working balance
    ws = db.query(Workspace).filter(Workspace.id == rec.workspace_id).first()
    all_txs = db.query(Transaction).filter(Transaction.workspace_id == rec.workspace_id).all()
    inflow_tot, outflow_tot = compute_monthly_run_rate(all_txs)
    updated_net_balance = Decimal(str(ws.starting_balance)) + inflow_tot - outflow_tot

    record_out = UdhaarRecordOut(
        id=rec.id,
        workspaceId=rec.workspace_id,
        customerName=rec.customer_name,
        phone=rec.phone,
        issuedAt=rec.issued_at.isoformat(),
        dueAt=rec.due_at.isoformat() if rec.due_at else None,
        outstanding=Money.from_decimal(Decimal(str(rec.outstanding))),
        status=rec.status,
        ageBucket=rec.age_bucket,
        sourceRef=rec.source_ref,
        notes=rec.notes,
    )

    return SettlementResponse(
        record=record_out,
        updatedBalancePaisa=decimal_to_paisa_string(updated_net_balance),
    )
