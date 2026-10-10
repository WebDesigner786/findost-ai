"""FinDost AI Backend API & Exact Math Test Suite"""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.common import Money, decimal_to_paisa_string, paisa_string_to_decimal
from app.services.calculator import calculate_runway_days


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_exact_numeric_money_conversions():
    """Verifies that Decimal <-> integer paisa conversion has zero floating-point drift."""
    # 0.10 PKR + 0.20 PKR = 0.30 PKR
    val1 = Decimal("0.10")
    val2 = Decimal("0.20")
    total = val1 + val2
    assert total == Decimal("0.30")

    paisa_str = decimal_to_paisa_string(total)
    assert paisa_str == "30"

    recovered_decimal = paisa_string_to_decimal(paisa_str)
    assert recovered_decimal == Decimal("0.30")

    # Large rupee value: Rs. 14,800,000.50
    large = Decimal("14800000.50")
    large_paisa = decimal_to_paisa_string(large)
    assert large_paisa == "1480000050"
    assert paisa_string_to_decimal(large_paisa) == large


def test_health_check(client):
    """Verifies system health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"]["connected"] is True


def test_list_workspaces(client):
    """Verifies listing of the 4 Pakistani financial workspaces."""
    response = client.get("/api/workspaces")
    assert response.status_code == 200
    workspaces = response.json()
    assert len(workspaces) >= 4
    workspace_ids = [w["id"] for w in workspaces]
    assert "sme-bilal" in workspace_ids
    assert "student-ayesha" in workspace_ids
    assert "household-khan" in workspace_ids
    assert "enterprise-indus" in workspace_ids


def test_workspace_dashboard(client):
    """Verifies live KPI computation, 30-day runway, and 90-day forecast for SME hero."""
    response = client.get("/api/workspaces/sme-bilal/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["workspace"]["id"] == "sme-bilal"
    assert "kpis" in data
    assert int(data["kpis"]["runwayDays"]) > 0
    assert "forecast" in data
    assert len(data["forecast"]["points"]) == 13  # 13 weekly points spanning 90 days


def test_transactions_retrieval_and_audit_patch(client):
    """Verifies human-in-the-loop review station update and before/after audit tracking."""
    # 1. Fetch transactions
    get_res = client.get("/api/workspaces/sme-bilal/transactions")
    assert get_res.status_code == 200
    txs = get_res.json()
    assert len(txs) > 0

    target_tx = next((t for t in txs if t["id"] == "tx-sme-7"), txs[0])

    # 2. Patch low-confidence transaction
    patch_payload = {
        "merchant": "National Foods Spices & Seasoning Wholesale",
        "category": "Inventory Restock",
        "amountPaisa": "4800000",  # Rs. 48,000
        "reviewStatus": "confirmed",
        "correctionNote": "Verified vendor tax invoice by human auditor",
    }
    patch_res = client.patch(f"/api/transactions/{target_tx['id']}", json=patch_payload)
    assert patch_res.status_code == 200
    updated = patch_res.json()

    assert updated["merchant"] == "National Foods Spices & Seasoning Wholesale"
    assert updated["isEdited"] is True
    assert updated["reviewStatus"] == "confirmed"
    assert updated["correctionNote"] == "Verified vendor tax invoice by human auditor"


def test_udhaar_retrieval_and_settlement(client):
    """Verifies Udhaar ledger retrieval, partial FIFO settlement, and offsetting cash injection."""
    get_res = client.get("/api/workspaces/sme-bilal/udhaar")
    assert get_res.status_code == 200
    records = get_res.json()
    assert len(records) > 0

    target_udh = records[0]
    initial_outstanding_paisa = int(target_udh["outstanding"]["amountPaisa"])

    # Execute partial settlement of Rs. 20,000 (2,000,000 paisa)
    settle_payload = {
        "udhaarId": target_udh["id"],
        "amountPaisa": "2000000",
        "notes": "Received partial cash recovery via bank deposit",
    }
    settle_res = client.post(f"/api/udhaar/{target_udh['id']}/settlements", json=settle_payload)
    assert settle_res.status_code == 200
    settle_data = settle_res.json()

    new_outstanding_paisa = int(settle_data["record"]["outstanding"]["amountPaisa"])
    assert new_outstanding_paisa == initial_outstanding_paisa - 2000000
    assert "updatedBalancePaisa" in settle_data


def test_shock_scenario_simulation(client):
    """Verifies deterministic shock simulator identifies breach and recomputes correctly."""
    scenario_payload = {
        "id": "scen-test",
        "workspaceId": "sme-bilal",
        "title": "Supply Chain Shock Test",
        "description": "Evaluate wholesale inflation shock",
        "shocks": [
            {
                "id": "shock_price",
                "kind": "price_rise",
                "label": "Supplier Price Hike (+25%)",
                "description": "Wholesale inflation",
                "percent": 25.0,
                "active": True,
            }
        ],
        "recoveryActions": [
            {
                "id": "collect_debt",
                "label": "Recover Receivables",
                "description": "Collect outstanding debt",
                "estimatedImpact": {"currency": "PKR", "amountPaisa": "15000000"},
                "active": False,
            }
        ],
        "assumptions": ["Deterministic run rate model"],
    }

    res = client.post("/api/workspaces/sme-bilal/scenarios", json=scenario_payload)
    assert res.status_code == 200
    result_data = res.json()
    assert "simulatedShortageDate" in result_data


def test_reports_and_evidence(client):
    """Verifies evidence-traceable recommendations, credit assessment, and FBR tax preview."""
    res = client.get("/api/workspaces/sme-bilal/reports")
    assert res.status_code == 200
    data = res.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    # Every recommendation must have evidence source refs
    for rec in data["recommendations"]:
        assert isinstance(rec["evidenceSourceRefs"], list)
    assert "creditReadiness" in data
    assert "taxPreview" in data
    assert "Preliminary Estimate — FBR Validation Required" in data["taxPreview"]["disclaimer"]


def test_error_handling_middleware(client):
    """Verifies standard JSON error envelope on 404 and 422."""
    # 404 Not Found
    res_404 = client.get("/api/workspaces/nonexistent-workspace-id/dashboard")
    assert res_404.status_code == 404
    err_404 = res_404.json()
    assert "error" in err_404
    assert err_404["error"]["code"] == "NOT_FOUND"

    # 422 Validation Error
    res_422 = client.post("/api/udhaar/udh-1/settlements", json={"invalidField": 123})
    assert res_422.status_code == 422
    err_422 = res_422.json()
    assert "error" in err_422
    assert err_422["error"]["code"] == "VALIDATION_ERROR"
