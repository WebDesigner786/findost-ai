"""Seed Data Module for FinDost AI

Populates PostgreSQL / SQLite with coherent synthetic data for the 4 Pakistani personas:
1. Bilal General Store (SME Kiryana - Hero Demo)
2. Ayesha Noor (FAST Student)
3. Khan Family (Salaried Household)
4. Indus Textiles Ltd. (Enterprise Multi-branch)
"""

from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session
from app.models.workspace import Workspace
from app.models.transaction import Transaction
from app.models.udhaar import UdhaarRecord
from app.models.anomaly import Anomaly
from app.models.recommendation import Recommendation
from app.models.document import Document


def seed_database(db: Session) -> dict:
    """Idempotently seeds the database with the 4 Pakistani personas."""
    # Check if already seeded
    existing_ws = db.query(Workspace).filter(Workspace.id == "sme-bilal").first()
    if existing_ws:
        return {"status": "already_seeded", "message": "Database already contains baseline workspaces"}

    # 1. Bilal General Store (SME Hero Demo)
    sme = Workspace(
        id="sme-bilal",
        kind="sme",
        name="Bilal General Store",
        display_name="Bilal General Store (Kiryana SME)",
        description="Retail grocery & FMCG distribution — Lahore (Hero Demo)",
        currency="PKR",
        timezone="Asia/Karachi",
        starting_balance=Decimal("420000.00"),
        features=["cash_flow", "upload_review", "udhaar_ledger", "simulator", "reports", "credit_readiness", "tax_preview"],
    )
    db.add(sme)

    sme_txs = [
        Transaction(
            id="tx-sme-1",
            workspace_id="sme-bilal",
            occurred_at=date(2026, 10, 8),
            merchant="Engro Foods Distributor",
            amount=Decimal("125000.00"),
            direction="outflow",
            category="Inventory Restock",
            confidence=Decimal("0.960"),
            review_status="confirmed",
            source_ref="INV-ENG-9821.pdf",
        ),
        Transaction(
            id="tx-sme-2",
            workspace_id="sme-bilal",
            occurred_at=date(2026, 10, 7),
            merchant="Daily Retail Counter Cash Inflow",
            amount=Decimal("86500.00"),
            direction="inflow",
            category="Retail Sales",
            confidence=Decimal("0.990"),
            review_status="confirmed",
            source_ref="POS-BATCH-1007",
        ),
        Transaction(
            id="tx-sme-3",
            workspace_id="sme-bilal",
            occurred_at=date(2026, 10, 6),
            merchant="Unilever Pakistan Wholesale",
            amount=Decimal("94000.00"),
            direction="outflow",
            category="Inventory Restock",
            confidence=Decimal("0.940"),
            review_status="confirmed",
            source_ref="INV-UNI-5542.pdf",
        ),
        Transaction(
            id="tx-sme-4",
            workspace_id="sme-bilal",
            occurred_at=date(2026, 10, 5),
            merchant="Shan Foods Distribution Hub",
            amount=Decimal("42500.00"),
            direction="outflow",
            category="Inventory Restock",
            confidence=Decimal("0.910"),
            review_status="confirmed",
            source_ref="INV-SHAN-1109.pdf",
        ),
        Transaction(
            id="tx-sme-5",
            workspace_id="sme-bilal",
            occurred_at=date(2026, 10, 4),
            merchant="LESCO Commercial Electricity Bill",
            amount=Decimal("38600.00"),
            direction="outflow",
            category="Utilities",
            confidence=Decimal("0.980"),
            review_status="confirmed",
            source_ref="BILL-LESCO-OCT26.pdf",
        ),
        Transaction(
            id="tx-sme-6",
            workspace_id="sme-bilal",
            occurred_at=date(2026, 10, 3),
            merchant="Easypaisa Merchant QR Settlement",
            amount=Decimal("54200.00"),
            direction="inflow",
            category="Digital Payments",
            confidence=Decimal("0.970"),
            review_status="confirmed",
            source_ref="EP-SETTLE-883",
        ),
        Transaction(
            id="tx-sme-7",
            workspace_id="sme-bilal",
            occurred_at=date(2026, 10, 2),
            merchant="National Foods Spices & Condiments",
            amount=Decimal("48000.00"),
            direction="outflow",
            category="Inventory Restock",
            confidence=Decimal("0.620"),
            review_status="needs_review",
            source_ref="SCAN-RECEIPT-4029.jpg",
        ),
        Transaction(
            id="tx-sme-8",
            workspace_id="sme-bilal",
            occurred_at=date(2026, 10, 1),
            merchant="Shop Rent - Main Market Johar Town",
            amount=Decimal("75000.00"),
            direction="outflow",
            category="Rent & Facilities",
            confidence=Decimal("0.990"),
            review_status="confirmed",
            source_ref="RENT-RECEIPT-OCT",
        ),
    ]
    for tx in sme_txs:
        db.add(tx)

    sme_udhaar = [
        UdhaarRecord(
            id="udh-1",
            workspace_id="sme-bilal",
            customer_name="Tariq Mahmood (Al-Madina Caterers)",
            phone="0300-8451290",
            issued_at=date(2026, 7, 15),
            due_at=date(2026, 8, 15),
            outstanding=Decimal("85000.00"),
            status="overdue",
            age_bucket="90d+",
            source_ref="KATA-LEAF-041",
            notes="Ordered wedding ghee & basmati bulk; promise date missed twice.",
        ),
        UdhaarRecord(
            id="udh-2",
            workspace_id="sme-bilal",
            customer_name="Imran Butt (Butt Sweets)",
            phone="0321-4458921",
            issued_at=date(2026, 8, 10),
            due_at=date(2026, 9, 10),
            outstanding=Decimal("65000.00"),
            status="overdue",
            age_bucket="60d",
            source_ref="KATA-LEAF-089",
            notes="Dairy restock; agreed to pay in two installments.",
        ),
        UdhaarRecord(
            id="udh-3",
            workspace_id="sme-bilal",
            customer_name="Chaudhry Akram Farm Supplies",
            phone="0333-5120934",
            issued_at=date(2026, 8, 28),
            due_at=date(2026, 9, 28),
            outstanding=Decimal("50000.00"),
            status="overdue",
            age_bucket="30d",
            source_ref="KATA-LEAF-114",
            notes="Monthly ration for farm workers.",
        ),
        UdhaarRecord(
            id="udh-4",
            workspace_id="sme-bilal",
            customer_name="Dr. Farooq Clinic Staff Ration",
            phone="0302-9988112",
            issued_at=date(2026, 9, 25),
            due_at=date(2026, 10, 25),
            outstanding=Decimal("42000.00"),
            status="current",
            age_bucket="30d",
            source_ref="KATA-LEAF-150",
            notes="Regular 30-day corporate settlement account.",
        ),
        UdhaarRecord(
            id="udh-5",
            workspace_id="sme-bilal",
            customer_name="Master Aslam (School Canteen)",
            phone="0314-2201944",
            issued_at=date(2026, 9, 18),
            due_at=date(2026, 10, 18),
            outstanding=Decimal("38000.00"),
            status="current",
            age_bucket="30d",
            source_ref="KATA-LEAF-162",
            notes="Biscuits & juices canteen credit.",
        ),
        UdhaarRecord(
            id="udh-6",
            workspace_id="sme-bilal",
            customer_name="Haji Usman Tea Stall",
            phone="0345-6677881",
            issued_at=date(2026, 7, 20),
            due_at=date(2026, 8, 20),
            outstanding=Decimal("35000.00"),
            status="overdue",
            age_bucket="90d+",
            source_ref="KATA-LEAF-033",
            notes="Milk powder & sugar weekly credit.",
        ),
    ]
    for ud in sme_udhaar:
        db.add(ud)

    sme_anomalies = [
        Anomaly(
            id="anom-sme-1",
            workspace_id="sme-bilal",
            kind="supplier_price",
            severity="warning",
            title="Supplier Price Increase (+18.4%) Detected",
            explanation="Engro Foods invoice unit cost for 16kg Cooking Oil tin increased from Rs. 7,600 to Rs. 9,000 without prior vendor notice.",
            amount=Decimal("22400.00"),
            period="October 2026 vs September 2026",
            transaction_ids=["tx-sme-1"],
            source_refs=["INV-ENG-9821.pdf"],
            detected_at=date(2026, 10, 8),
        ),
        Anomaly(
            id="anom-sme-2",
            workspace_id="sme-bilal",
            kind="overdue_udhaar",
            severity="critical",
            title="Overdue Udhaar Exceeds Working Capital Buffer",
            explanation="Rs. 235,000 of customer Udhaar is overdue past 30 days. Collecting top 3 debtors would extend cash runway by 38 days.",
            amount=Decimal("235000.00"),
            period="Last 90 days aging",
            transaction_ids=[],
            source_refs=["KATA-LEAF-041", "KATA-LEAF-089", "KATA-LEAF-114"],
            detected_at=date(2026, 10, 9),
        ),
    ]
    for anom in sme_anomalies:
        db.add(anom)

    sme_recs = [
        Recommendation(
            id="rec-sme-1",
            workspace_id="sme-bilal",
            title="Initiate structured recovery on Rs. 150,000 overdue Udhaar",
            plain_reason="Tariq Caterers and Butt Sweets have exceeded 60-day terms. Recovering even 60% eliminates the projected Day 42 cash dip.",
            estimated_impact=Decimal("90000.00"),
            time_horizon="Next 14 days",
            category="collections",
            evidence_transaction_ids=[],
            evidence_source_refs=["KATA-LEAF-041", "KATA-LEAF-089"],
            assumptions=["Assumes 60% recovery via WhatsApp reminder and partial installment offer"],
        ),
        Recommendation(
            id="rec-sme-2",
            workspace_id="sme-bilal",
            title="Consolidate Engro Oil & Ghee orders to unlock 3.5% distributor rebate",
            plain_reason="Weekly fragmented orders of 16kg tins miss the 50-tin bulk distributor discount tier.",
            estimated_impact=Decimal("26250.00"),
            time_horizon="Next 30 days",
            category="supplier",
            evidence_transaction_ids=["tx-sme-1"],
            evidence_source_refs=["INV-ENG-9821.pdf"],
            assumptions=["Order 50 tins bi-weekly instead of 15 tins weekly"],
        ),
    ]
    for rec in sme_recs:
        db.add(rec)

    # 2. Student — Ayesha Noor
    student = Workspace(
        id="student-ayesha",
        kind="student",
        name="Ayesha Noor",
        display_name="Ayesha Noor (FAST University)",
        description="Hostel budget, allowance & freelance tutoring",
        currency="PKR",
        timezone="Asia/Karachi",
        starting_balance=Decimal("28500.00"),
        features=["cash_flow", "upload_review", "simulator", "reports"],
    )
    db.add(student)

    # 3. Household — Khan Family
    household = Workspace(
        id="household-khan",
        kind="household",
        name="Khan Family",
        display_name="Khan Family Household",
        description="Salaried household, utility bills & education planning",
        currency="PKR",
        timezone="Asia/Karachi",
        starting_balance=Decimal("185000.00"),
        features=["cash_flow", "upload_review", "simulator", "reports", "tax_preview"],
    )
    db.add(household)

    # 4. Enterprise — Indus Textiles
    enterprise = Workspace(
        id="enterprise-indus",
        kind="enterprise",
        name="Indus Textiles Ltd.",
        display_name="Indus Textiles (Multi-branch)",
        description="Spinning & weaving roll-up across Lahore, Faisalabad, Karachi",
        currency="PKR",
        timezone="Asia/Karachi",
        starting_balance=Decimal("14800000.00"),
        features=["cash_flow", "upload_review", "udhaar_ledger", "simulator", "reports", "credit_readiness", "tax_preview"],
    )
    db.add(enterprise)

    db.commit()
    return {"status": "seeded", "message": "Successfully seeded 4 workspaces and baseline financial fixtures"}
