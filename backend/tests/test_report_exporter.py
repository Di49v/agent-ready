"""
Unit tests for ReportExporter, Dynamic SVG Badge, and Signed Outbound Callbacks.
Verifies Section B3.9 Spec: Markdown/JSON report export, dynamic SVG badges,
HMAC-SHA256 signature generation/verification, and clean OpenAPI 3.1 operation IDs.
"""
import json
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.mocks.replay_fixtures import get_mock_run_summary
from app.schemas.contracts import FindingDetail, FindingSeverity, RunStatus
from app.services.report_exporter import ReportExporter, get_report_exporter


def test_markdown_report_generation() -> None:
    """Verifies that generate_markdown_report constructs publication-grade audit documents."""
    exporter = get_report_exporter()
    naive_summary = get_mock_run_summary("naive-shop", seed=42)
    hardened_summary = get_mock_run_summary("hardened-shop", seed=42)

    # Test Naive Shop report (Score 18)
    naive_md = exporter.generate_markdown_report(naive_summary)
    assert "# AgentReady Lab — Commerce Audit Report" in naive_md
    assert "Naive Shop" in naive_md
    assert "18 / 100" in naive_md
    assert "CRITICAL DEFICIT (FAILED)" in naive_md
    assert "Invariant Safety Rules Scorecard" in naive_md
    assert "Discovered Vulnerabilities & Evidence" in naive_md
    assert "Disclaimer:" in naive_md

    # Test Hardened Shop report (Score 95)
    hardened_md = exporter.generate_markdown_report(hardened_summary)
    assert "Hardened Shop" in hardened_md
    assert "95 / 100" in hardened_md
    assert "PASS" in hardened_md
    assert "Disclaimer:" in hardened_md


def test_json_report_generation() -> None:
    """Verifies that generate_json_report returns full structured audit data."""
    exporter = get_report_exporter()
    summary = get_mock_run_summary("naive-shop", seed=42)

    data = exporter.generate_json_report(summary)
    assert data["run_id"] == summary.id
    assert data["target"] == "naive-shop"
    assert data["score"] == 18
    assert "rule_scores" in data
    assert "findings" in data
    assert "badge_url" in data
    assert "/v1/badge/naive-shop.svg" in data["badge_url"]


def test_svg_badge_generation() -> None:
    """Verifies dynamic SVG badge rendering for passing, failing, and pending states."""
    exporter = get_report_exporter()

    # Pass badge (>= 80)
    pass_svg = exporter.generate_svg_badge(score=95, target_name="hardened-shop")
    assert "<svg" in pass_svg
    assert "95/100 PASS" in pass_svg
    assert "#10B981" in pass_svg  # Emerald
    assert "agent-ready" in pass_svg

    # Fail badge (< 50)
    fail_svg = exporter.generate_svg_badge(score=18, target_name="naive-shop")
    assert "<svg" in fail_svg
    assert "18/100 FAIL" in fail_svg
    assert "#F43F5E" in fail_svg  # Rose

    # Warn badge (50 - 79)
    warn_svg = exporter.generate_svg_badge(score=75, target_name="remediated-shop")
    assert "75/100 WARN" in warn_svg
    assert "#F59E0B" in warn_svg  # Amber

    # Pending badge
    pending_svg = exporter.generate_svg_badge(score=None)
    assert "PENDING" in pending_svg
    assert "#6B7280" in pending_svg


def test_callback_hmac_signature_verification() -> None:
    """Verifies HMAC-SHA256 signature generation and validation for outbound callbacks."""
    exporter = get_report_exporter()
    secret = "test_custom_hmac_secret_42"
    payload = b'{"event":"run.completed","score":95,"status":"complete"}'

    # Compute valid signature
    import hashlib, hmac
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    sig_header = f"sha256={sig}"

    # Verify signature passes
    assert exporter.verify_callback_signature(payload, sig_header, secret=secret) is True

    # Verify tampered payload fails
    tampered_payload = b'{"event":"run.completed","score":18,"status":"complete"}'
    assert exporter.verify_callback_signature(tampered_payload, sig_header, secret=secret) is False

    # Verify wrong secret fails
    assert exporter.verify_callback_signature(payload, sig_header, secret="wrong_secret") is False


@pytest.mark.asyncio
async def test_openapi_operation_ids_and_schema_quality() -> None:
    """Verifies that all API routes expose clean, standardized operation IDs for APIMatic."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/openapi.json")
        assert res.status_code == 200
        schema = res.json()

        assert schema["openapi"] == "3.1.0"
        paths = schema["paths"]

        expected_operations = {
            "/healthz": ["healthCheck"],
            "/v1/targets": ["listTargets", "createTarget"],
            "/v1/personas": ["listPersonas"],
            "/v1/runs": ["createRun"],
            "/v1/runs/{id}": ["getRun"],
            "/v1/runs/{id}/findings": ["getRunFindings"],
            "/v1/runs/{id}/ledger": ["getRunLedger"],
            "/v1/runs/{id}/report": ["getRunReport"],
            "/v1/runs/{id}/rerun": ["rerunRun"],
            "/v1/badge/{target}.svg": ["getScoreBadge"],
            "/v1/runs/{id}/events": ["streamRunEvents"],
            "/webhooks/paypal": ["receivePaypalWebhook"],
        }

        for path, op_ids in expected_operations.items():
            assert path in paths, f"Path {path} missing from openapi.json"
            path_item = paths[path]
            for op_id in op_ids:
                found = False
                for method, operation in path_item.items():
                    if operation.get("operationId") == op_id:
                        found = True
                        break
                assert found is True, f"OperationId {op_id} not found under path {path}"


@pytest.mark.asyncio
async def test_get_run_report_markdown_and_json_modes() -> None:
    """Verifies /v1/runs/{id}/report supports both JSON and plain Markdown representations."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. JSON mode (default)
        res_json = await client.get("/v1/runs/run_42_naive_shop/report")
        assert res_json.status_code == 200
        assert res_json.headers["content-type"].startswith("application/json")
        data = res_json.json()
        assert data["run_id"] == "run_42_naive_shop"
        assert "markdown" in data

        # 2. Markdown text mode
        res_md = await client.get("/v1/runs/run_42_naive_shop/report?format=markdown")
        assert res_md.status_code == 200
        assert "text/markdown" in res_md.headers["content-type"]
        assert "# AgentReady Lab — Commerce Audit Report" in res_md.text

