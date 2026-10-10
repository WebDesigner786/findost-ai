"""Scenarios & Shock Simulator Router"""

from decimal import Decimal
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.workspace import Workspace
from app.models.transaction import Transaction
from app.schemas.scenario import Scenario
from app.services.calculator import compute_monthly_run_rate

router = APIRouter(prefix="/api/workspaces", tags=["Scenarios"])


@router.post("/{workspace_id}/scenarios", response_model=Scenario)
def run_workspace_scenario(
    workspace_id: str, scenario: Scenario, db: Session = Depends(get_db)
):
    """Executes a deterministic macroeconomic shock and recovery scenario.
    
    Simulates cash balances over 90 days under active price shocks, receivable delays,
    and recovery levers, identifying the exact liquidity shortage date if breached.
    """
    ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not ws:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workspace '{workspace_id}' not found.",
        )

    txs = db.query(Transaction).filter(Transaction.workspace_id == workspace_id).all()
    inflow_dec, outflow_dec = compute_monthly_run_rate(txs)
    starting_balance = Decimal(str(ws.starting_balance))
    current_net = starting_balance + inflow_dec - outflow_dec

    daily_inflow_base = inflow_dec / Decimal("30")
    daily_outflow_base = outflow_dec / Decimal("30")

    # Evaluate active shocks
    daily_outflow_shock = Decimal("0.00")
    delayed_inflow = Decimal("0.00")
    fixed_outflow = Decimal("0.00")

    for shock in scenario.shocks:
        if not shock.active:
            continue
        if shock.kind == "price_rise" and shock.percent:
            daily_outflow_shock += (daily_outflow_base * Decimal(str(shock.percent))) / Decimal("100")
        elif shock.kind == "utility_spike" and shock.amount:
            daily_outflow_shock += shock.amount.to_decimal() / Decimal("30")
        elif shock.kind == "delayed_receivables" and shock.amount:
            delayed_inflow += shock.amount.to_decimal()
        elif shock.amount:
            fixed_outflow += shock.amount.to_decimal()

    # Evaluate active recoveries
    daily_outflow_recovery = Decimal("0.00")
    upfront_recovery_inflow = Decimal("0.00")

    for rec in scenario.recoveryActions:
        if not rec.active:
            continue
        if rec.id == "defer_stock":
            daily_outflow_recovery += (daily_outflow_base * Decimal("20")) / Decimal("100")
        else:
            upfront_recovery_inflow += rec.estimatedImpact.to_decimal()

    effective_daily_outflow = daily_outflow_base + daily_outflow_shock - daily_outflow_recovery
    effective_daily_inflow = daily_inflow_base
    delayed_daily_reduction = delayed_inflow / Decimal("45") if delayed_inflow > Decimal("0.00") else Decimal("0.00")

    simulated_balance = current_net + upfront_recovery_inflow - fixed_outflow
    shortage_date = None
    today = date.today()

    for day in range(0, 91, 5):
        sim_date = today + timedelta(days=day)
        if day > 0:
            inflow_adj = (
                max(effective_daily_inflow - delayed_daily_reduction, Decimal("0.00"))
                if day <= 45
                else effective_daily_inflow + delayed_daily_reduction
            )
            delta = (inflow_adj - effective_daily_outflow) * Decimal("5")
            simulated_balance += delta

        if simulated_balance < Decimal("0.00") and not shortage_date:
            shortage_date = sim_date.isoformat()

    scenario.simulatedShortageDate = shortage_date
    return scenario
