"""
Integration tests for Task 1.0B: FastAPI /v1/* Blueprint Routers and SSE Telemetry.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_healthz_endpoint():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["mock_blueprint"] is True
    assert "sandbox.paypal.com" in data["paypal_base_url"]


def test_list_and_create_targets():
    # List pre-registered targets
    response = client.get("/v1/targets")
    assert response.status_code == 200
    targets = response.json()
    target_ids = [t["id"] for t in targets]
    assert "naive-shop" in target_ids
    assert "hardened-shop" in target_ids

    # Create a dynamic custom target
    new_target = {
        "id": "custom-partner-shop",
        "name": "Custom Partner Shop",
        "base_url": "https://partner.example.com",
        "mode": "probe",
        "is_demo": False,
    }
    create_res = client.post("/v1/targets", json=new_target)
    assert create_res.status_code == 201
    assert create_res.json()["id"] == "custom-partner-shop"

    # Verify target appears in list
    list_after = client.get("/v1/targets").json()
    assert any(t["id"] == "custom-partner-shop" for t in list_after)


def test_list_personas():
    response = client.get("/v1/personas")
    assert response.status_code == 200
    personas = response.json()
    assert len(personas) == 9
    persona_names = [p["name"] for p in personas]
    assert "The Retrier" in persona_names
    assert "The Disputer" in persona_names
    assert "The Content Trap" in persona_names


def test_run_creation_and_retrieval_flow():
    # 1. Start a crash test on Naive Shop
    run_req = {
        "target": "naive-shop",
        "pack": "full",
        "seed": 42,
        "policy": "auto",
        "replay": False,
    }
    create_res = client.post("/v1/runs", json=run_req)
    assert create_res.status_code == 202
    summary = create_res.json()
    run_id = summary["id"]
    assert summary["score"] == 18
    assert summary["target"] == "naive-shop"

    # 2. Retrieve run status
    get_res = client.get(f"/v1/runs/{run_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == run_id

    # 3. Retrieve findings
    findings_res = client.get(f"/v1/runs/{run_id}/findings")
    assert findings_res.status_code == 200
    findings = findings_res.json()
    assert len(findings) == 5
    assert any("Double Capture" in f["title"] for f in findings)
    assert all(len(f["evidence_ids"]) > 0 for f in findings)

    # 4. Retrieve dual-ledger snapshot
    ledger_res = client.get(f"/v1/runs/{run_id}/ledger")
    assert ledger_res.status_code == 200
    ledger = ledger_res.json()
    assert len(ledger["dual_rows"]) == 9

    # 5. Retrieve markdown audit report
    report_res = client.get(f"/v1/runs/{run_id}/report")
    assert report_res.status_code == 200
    report = report_res.json()
    assert "18 / 100" in report["markdown"]


def test_rerun_flow_red_to_green():
    # 1. Baseline run on Naive Shop (Red: 18/100)
    baseline_res = client.post(
        "/v1/runs",
        json={"target": "naive-shop", "seed": 42, "policy": "auto"},
    )
    base_id = baseline_res.json()["id"]
    assert baseline_res.json()["score"] == 18

    # 2. Re-run same seed with hardened-shop target override (Green: 95/100)
    rerun_res = client.post(
        f"/v1/runs/{base_id}/rerun",
        json={"target_override": "hardened-shop"},
    )
    assert rerun_res.status_code == 202
    rerun_summary = rerun_res.json()
    assert rerun_summary["score"] == 95
    assert rerun_summary["target"] == "hardened-shop"
    assert rerun_summary["total_findings"] == 1


def test_svg_badge_generation():
    # Naive shop badge (18/100, vulnerable)
    naive_badge = client.get("/v1/badge/naive-shop.svg")
    assert naive_badge.status_code == 200
    assert naive_badge.headers["content-type"] == "image/svg+xml"
    assert "18/100" in naive_badge.text
    assert "#F43F5E" in naive_badge.text

    # Hardened shop badge (95/100, agent-ready)
    hardened_badge = client.get("/v1/badge/hardened-shop.svg")
    assert hardened_badge.status_code == 200
    assert "95/100" in hardened_badge.text
    assert "#10B981" in hardened_badge.text


def test_sse_telemetry_stream():
    # Test streaming endpoint yields text/event-stream
    with client.stream("GET", "/v1/runs/run_42_naive_shop/events") as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        chunks = []
        for line in response.iter_lines():
            if line:
                chunks.append(line)
            if len(chunks) >= 4:
                break
        assert any("event: agent_step" in c or "event:" in c for c in chunks)


def test_rfc9457_not_found_handling():
    # Query non-existent run ID
    res = client.get("/v1/runs/nonexistent-run-id-999")
    assert res.status_code == 404
    assert res.headers["content-type"] == "application/problem+json"
    problem = res.json()
    assert problem["status"] == 404
    assert problem["code"] == "RUN_NOT_FOUND"


def test_rfc9457_validation_error_handling():
    # Post invalid payload (e.g. invalid type for seed)
    res = client.post("/v1/runs", json={"seed": "not-an-integer"})
    assert res.status_code == 422
    assert res.headers["content-type"] == "application/problem+json"
    problem = res.json()
    assert problem["status"] == 422
    assert problem["code"] == "INVALID_PAYLOAD"


def test_paypal_webhook_stub():
    res = client.post(
        "/webhooks/paypal",
        json={"event_type": "CHECKOUT.ORDER.APPROVED", "resource": {"id": "5O190127TN364715T"}},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["received"] is True
    assert data["status"] == "queued_for_reconciliation"

