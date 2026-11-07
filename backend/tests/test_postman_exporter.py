"""
Unit and integration tests for Task 7.1: Postman Collection v2.1.0 Exporter.
"""
import json
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.contracts import FindingDetail, RunStatus, RunSummary
from app.services.postman_exporter import get_postman_exporter

client = TestClient(app)


def test_postman_exporter_collection_generation():
    exporter = get_postman_exporter()

    summary = RunSummary(
        id="run_test_postman_001",
        target="naive-shop",
        pack="full",
        seed=42,
        status=RunStatus.COMPLETED,
        score=18,
        total_findings=3,
        critical_count=2,
        high_count=1,
        medium_count=0,
        low_count=0,
        created_at="2026-11-07T12:00:00Z",
    )

    findings = [
        FindingDetail(
            id="f_rule1_001",
            run_id="run_test_postman_001",
            rule_number=1,
            rule_name="Pay Once",
            severity="CRITICAL",
            title="Double Capture on Retry Without Idempotency",
            description="Two capture payments processed for same cart.",
            evidence_ids=["5O190127TN364715T", "7P280238UO475826U"],
            explanation="The store failed to pass the PayPal-Request-Id header.",
            suggested_patch="Use PayPal-Request-Id from cart_id.",
        ),
        FindingDetail(
            id="f_rule2_002",
            run_id="run_test_postman_001",
            rule_number=2,
            rule_name="Right Amount",
            severity="CRITICAL",
            title="Manipulated Cart Unit Price Accepted",
            description="Store trusted submitted item price of $1.50.",
            evidence_ids=["CAP-TAMPER-001"],
            explanation="The store trusted client price.",
            suggested_patch="Recompute prices from catalog.",
        ),
        FindingDetail(
            id="f_rule5_003",
            run_id="run_test_postman_001",
            rule_number=5,
            rule_name="Records Agree",
            severity="HIGH",
            title="Unverified PayPal Webhook Processed",
            description="Webhook signature was not validated with PayPal.",
            evidence_ids=["WH-FORGED-999"],
            explanation="Store accepted self-signed webhook.",
            suggested_patch="Call verify-webhook-signature.",
        ),
    ]

    collection_dict = exporter.generate_collection(summary, findings)

    # 1. Verify Postman v2.1.0 root metadata
    assert "info" in collection_dict
    assert collection_dict["info"]["schema"] == "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    assert "run_test_postman_001" in collection_dict["info"]["name"]
    assert "naive-shop" in collection_dict["info"]["name"]

    # 2. Verify variables
    variables = {v["key"]: v["value"] for v in collection_dict["variable"]}
    assert "baseUrl" in variables
    assert "paypalSandboxUrl" in variables
    assert variables["paypalSandboxUrl"] == "https://api-m.sandbox.paypal.com"
    assert variables["runId"] == "run_test_postman_001"

    # 3. Verify items: Baseline vitality + 3 findings + Store Ledger Probe = 5 items
    items = collection_dict["item"]
    assert len(items) == 5

    item_names = [it["name"] for it in items]
    assert any("Vitality & Sandbox Lock" in name for name in item_names)
    assert any("Double Capture" in name for name in item_names)
    assert any("Manipulated Cart" in name for name in item_names)
    assert any("Unverified PayPal Webhook" in name for name in item_names)
    assert any("Store Internal Ledger Probe" in name for name in item_names)

    # 4. Verify test script execution blocks exist
    for it in items:
        assert "event" in it
        assert len(it["event"]) >= 1
        assert "exec" in it["event"][0]["script"]


def test_postman_exporter_json_serialization():
    exporter = get_postman_exporter()
    summary = RunSummary(
        id="run_empty_findings",
        target="hardened-shop",
        pack="full",
        seed=101,
        status=RunStatus.COMPLETED,
        score=95,
        total_findings=0,
        critical_count=0,
        high_count=0,
        medium_count=0,
        low_count=0,
        created_at="2026-11-07T12:00:00Z",
    )

    json_str = exporter.generate_collection_json(summary, [])
    parsed = json.loads(json_str)
    assert parsed["info"]["schema"] == "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    assert len(parsed["item"]) == 2  # Health check + Store Probe


def test_api_export_postman_endpoint():
    # 1. Create a baseline run on Naive Shop
    res = client.post("/v1/runs", json={"target": "naive-shop", "seed": 42})
    assert res.status_code == 202
    run_id = res.json()["id"]

    # 2. Download Postman Collection
    postman_res = client.get(f"/v1/runs/{run_id}/postman")
    assert postman_res.status_code == 200
    assert "application/json" in postman_res.headers["content-type"]
    assert "attachment;" in postman_res.headers.get("content-disposition", "")
    assert f"agent-ready-run-{run_id}.postman_collection.json" in postman_res.headers.get("content-disposition", "")

    collection_data = postman_res.json()
    assert collection_data["info"]["schema"] == "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    assert len(collection_data["item"]) >= 3

