"""
AgentReady Lab — MCP Server & Typed SDK Integration Tests.
Validates OpenAPI 3.1 schema export, operation ID conventions,
Section B3.10 MCP tool contracts, and TypeScript SDK model parity.
"""
from __future__ import annotations

import json
from pathlib import Path
import pytest
from app.main import app
from scripts.export_openapi import export_openapi


def test_openapi_export_and_validity(tmp_path: Path) -> None:
    """Verifies that export_openapi produces valid OpenAPI 3.1 JSON with complete schemas."""
    exported_file = export_openapi()
    assert exported_file.exists(), f"Expected exported file at {exported_file}"

    with open(exported_file, "r", encoding="utf-8") as f:
        schema = json.load(f)

    assert schema.get("openapi") == "3.1.0"
    assert schema.get("info", {}).get("title") == "AgentReady Lab API"
    assert schema.get("info", {}).get("version") == "1.0.0"

    # Verify critical endpoints exist
    paths = schema.get("paths", {})
    expected_paths = [
        "/healthz",
        "/v1/targets",
        "/v1/runs",
        "/v1/runs/{run_id}",
        "/v1/runs/{run_id}/findings",
        "/v1/runs/{run_id}/report",
        "/v1/runs/{run_id}/rerun",
        "/v1/personas",
        "/v1/badge/{target_id}.svg",
        "/v1/runs/{run_id}/events",
    ]
    for p in expected_paths:
        assert p in paths, f"Missing expected path '{p}' in OpenAPI schema"


def test_openapi_operation_ids_match_apimatic_standards() -> None:
    """Verifies operation IDs adhere to clean camelCase conventions suitable for APIMatic."""
    schema = app.openapi()
    paths = schema.get("paths", {})

    discovered_ops = {}
    for path, path_item in paths.items():
        for method, op in path_item.items():
            if isinstance(op, dict) and "operationId" in op:
                discovered_ops[op["operationId"]] = f"{method.upper()} {path}"

    expected_operation_ids = [
        "healthCheck",
        "listTargets",
        "createTarget",
        "listPersonas",
        "createRun",
        "getRun",
        "getRunFindings",
        "getRunLedger",
        "getRunReport",
        "rerunRun",
        "getScoreBadge",
        "streamRunEvents",
        "receivePaypalWebhook",
    ]

    for op_id in expected_operation_ids:
        assert op_id in discovered_ops, f"Missing expected operationId '{op_id}' in OpenAPI paths: {discovered_ops.keys()}"


def test_mcp_server_tool_definitions_and_templates() -> None:
    """Verifies mcp/server.ts implements all 5 Section B3.10 tools and grounded patch templates."""
    mcp_server_file = Path(__file__).resolve().parent.parent.parent / "mcp" / "server.ts"
    assert mcp_server_file.exists(), f"MCP server file not found at {mcp_server_file}"

    content = mcp_server_file.read_text(encoding="utf-8")

    # 1. Verify 5 required Section B3.10 MCP tools
    required_tools = [
        "start_crash_test",
        "list_findings",
        "explain_finding",
        "suggest_fix",
        "rerun",
    ]
    for tool_name in required_tools:
        assert f'name: "{tool_name}"' in content or f"case \"{tool_name}\":" in content, (
            f"MCP server missing tool implementation for '{tool_name}'"
        )

    # 2. Verify APIMatic grounded unified diff templates
    required_bug_diffs = [
        "BUG_NO_IDEMPOTENCY",
        "BUG_TRUST_CLIENT_PRICE",
        "BUG_NO_CART_INTENT_CHECK",
        "BUG_NO_WEBHOOK_VERIFY",
        "BUG_DOUBLE_REFUND",
        "BUG_NO_SHIPMENT_TRACKING",
    ]
    for bug in required_bug_diffs:
        assert bug in content, f"MCP server missing patch template for '{bug}'"


def test_typescript_sdk_surface_completeness() -> None:
    """Verifies sdk/src/client.ts exposes all API operations and RFC 9457 error handling."""
    sdk_client_file = Path(__file__).resolve().parent.parent.parent / "sdk" / "src" / "client.ts"
    assert sdk_client_file.exists(), f"SDK client file not found at {sdk_client_file}"

    client_content = sdk_client_file.read_text(encoding="utf-8")

    # Assert RFC 9457 error wrapper
    assert "class AgentReadyApiError extends Error" in client_content

    # Assert all client operations are defined
    expected_methods = [
        "healthCheck",
        "listTargets",
        "createTarget",
        "listPersonas",
        "createRun",
        "getRun",
        "getRunFindings",
        "getRunLedger",
        "getRunReport",
        "rerunRun",
        "getScoreBadgeSvg",
    ]
    for method in expected_methods:
        assert f"async {method}(" in client_content, f"SDK client missing method '{method}'"

