"""Transactions Router"""

import time
from datetime import date
from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.transaction import Transaction
from app.models.workspace import Workspace
from app.schemas.transaction import (
    TransactionOut,
    ImportTransactionsPayload,
    UpdateTransactionPayload,
)
from app.schemas.common import Money, paisa_string_to_decimal

router = APIRouter(tags=["Transactions"])


@router.get("/api/workspaces/{workspace_id}/transactions", response_model=List[TransactionOut])
def get_workspace_transactions(workspace_id: str, db: Session = Depends(get_db)):
    """Returns all transactions recorded for a given workspace."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found.",
        )

    txs = (
        db.query(Transaction)
        .filter(Transaction.workspace_id == workspace_id)
        .order_by(Transaction.occurred_at.desc())
        .all()
    )

    return [
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
        for t in txs
    ]


@router.post("/api/workspaces/{workspace_id}/transactions/import", response_model=List[TransactionOut])
def import_transactions(
    workspace_id: str, payload: ImportTransactionsPayload, db: Session = Depends(get_db)
):
    """Batch imports transactions into a workspace."""
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found.",
        )

    created_txs: List[Transaction] = []
    ts = int(time.time() * 1000)

    for idx, item in enumerate(payload.transactions):
        tx_id = f"tx-imp-{ts}-{idx}"
        occurred_date = date.fromisoformat(item.occurredAt)
        amount_dec = item.amount.to_decimal()

        new_tx = Transaction(
            id=tx_id,
            workspace_id=workspace_id,
            occurred_at=occurred_date,
            merchant=item.merchant,
            amount=amount_dec,
            direction=item.direction,
            category=item.category,
            confidence=Decimal(str(round(item.confidence or 1.0, 3))),
            review_status=item.reviewStatus,
            source_ref=item.sourceRef or "IMPORT-BATCH",
        )
        db.add(new_tx)
        created_txs.append(new_tx)

    db.commit()

    return [
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
        for t in created_txs
    ]


@router.patch("/api/transactions/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: str, payload: UpdateTransactionPayload, db: Session = Depends(get_db)
):
    """Updates a transaction with audit trail tracking."""
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction '{transaction_id}' not found.",
        )

    # Capture original state before edits if this is the first edit
    if not tx.is_edited:
        tx.original_merchant = tx.merchant
        tx.original_category = tx.category
        tx.original_amount = tx.amount

    if payload.merchant is not None:
        tx.merchant = payload.merchant

    if payload.category is not None:
        tx.category = payload.category

    if payload.amountPaisa is not None:
        tx.amount = paisa_string_to_decimal(payload.amountPaisa)

    if payload.reviewStatus is not None:
        tx.review_status = payload.reviewStatus

    if payload.correctionNote is not None:
        tx.correction_note = payload.correctionNote

    tx.is_edited = True
    tx.confidence = Decimal("1.000")  # Human verified

    db.commit()
    db.refresh(tx)

    return TransactionOut(
        id=tx.id,
        workspaceId=tx.workspace_id,
        occurredAt=tx.occurred_at.isoformat(),
        merchant=tx.merchant,
        amount=Money.from_decimal(Decimal(str(tx.amount))),
        direction=tx.direction,
        category=tx.category,
        confidence=float(tx.confidence),
        reviewStatus=tx.review_status,
        sourceRef=tx.source_ref,
        isEdited=tx.is_edited,
        originalMerchant=tx.original_merchant,
        originalCategory=tx.original_category,
        originalAmount=Money.from_decimal(Decimal(str(tx.original_amount))) if tx.original_amount else None,
        correctionNote=tx.correction_note,
    )
