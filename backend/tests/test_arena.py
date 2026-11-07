"""
AgentReady Lab — The Judge Arena Tests (Section B11).
Tests interactive AI shopping agent execution, chaos switches, prompt guardrails,
and Server-Sent Events (SSE) telemetry.
"""
from __future__ import annotations

import json
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_arena_presets_endpoint(client: TestClient) -> None:
    """Verifies that the arena presets endpoint returns curated demo missions."""
    res = client.get("/v1/arena/presets")
    assert res.status_code == 200
    presets = res.json()
    assert len(presets) >= 4
    preset_ids = [p["id"] for p in presets]
    assert "preset_double_capture" in preset_ids
    assert "preset_price_tampering" in preset_ids
    assert "preset_prompt_injection" in preset_ids
    assert "preset_forged_webhook" in preset_ids


def test_arena_off_topic_prompt_rejected(client: TestClient) -> None:
    """Verifies that non-shopping prompt inputs are rejected by the guardrail with 400 Bad Request."""
    payload = {
        "prompt": "Explain the history of the Byzantine Empire.",
        "target": "naive-shop",
        "chaos_toggles": {"drop_retry": True},
    }
    res = client.post("/v1/arena/run", json=payload)
    assert res.status_code == 400
    assert "Off-topic prompt rejected" in res.json()["detail"]


def test_arena_drop_retry_on_naive_vs_hardened(client: TestClient) -> None:
    """
    Demonstrates the core Judge Arena scenario:
    Toggling 'Drop Retry' causes a double-capture on Naive Shop,
    whereas Hardened Shop returns an idempotent replay and preserves safety.
    """
    # 1. Run on Naive Shop
    res_naive = client.post(
        "/v1/arena/run",
        json={
            "prompt": "Buy running shoes size 8 under $150",
            "target": "naive-shop",
            "chaos_toggles": {"drop_retry": True},
        },
    )
    assert res_naive.status_code == 200
    naive_data = res_naive.json()
    assert naive_data["score"] < 80
    assert any("Duplicate Payment" in f["title"] for f in naive_data["findings"])
    assert any(ev["status"] == "VIOLATION" for ev in naive_data["events"])

    # 2. Run identical scenario on Hardened Shop
    res_hardened = client.post(
        "/v1/arena/run",
        json={
            "prompt": "Buy running shoes size 8 under $150",
            "target": "hardened-shop",
            "chaos_toggles": {"drop_retry": True},
        },
    )
    assert res_hardened.status_code == 200
    hardened_data = res_hardened.json()
    assert hardened_data["score"] == 95
    assert not any("Duplicate Payment" in f["title"] for f in hardened_data["findings"])
    assert any("Idempotency Cache Hit" in ev["action"] for ev in hardened_data["events"])


def test_arena_price_tampering_on_naive_vs_hardened(client: TestClient) -> None:
    """Verifies that tampering with cart total to $1.50 is caught on Hardened Shop."""
    # 1. Naive Shop accepts tampered $1.50
    res_naive = client.post(
        "/v1/arena/run",
        json={
            "prompt": "Purchase ergonomic mechanical keyboard",
            "target": "naive-shop",
            "chaos_toggles": {"tamper_price": True},
        },
    )
    assert res_naive.status_code == 200
    naive_data = res_naive.json()
    assert any("Price Manipulation" in f["title"] for f in naive_data["findings"])

    # 2. Hardened Shop blocks with 409 PRICE_MISMATCH
    res_hardened = client.post(
        "/v1/arena/run",
        json={
            "prompt": "Purchase ergonomic mechanical keyboard",
            "target": "hardened-shop",
            "chaos_toggles": {"tamper_price": True},
        },
    )
    assert res_hardened.status_code == 200
    hardened_data = res_hardened.json()
    assert hardened_data["score"] == 95
    assert any("PRICE_MISMATCH" in ev["action"] for ev in hardened_data["events"])


def test_arena_events_sse_stream(client: TestClient) -> None:
    """Verifies that the /v1/arena/events/{id} endpoint streams real-time SSE frames for AG Grid."""
    # Start arena run
    res = client.post(
        "/v1/arena/run",
        json={
            "prompt": "Order dark roast coffee beans",
            "target": "hardened-shop",
            "chaos_toggles": {"prompt_trap": True},
        },
    )
    assert res.status_code == 200
    session_id = res.json()["session_id"]

    # Stream SSE frames
    stream_res = client.get(f"/v1/arena/events/{session_id}")
    assert stream_res.status_code == 200
    assert "text/event-stream" in stream_res.headers["content-type"]

    content = stream_res.text
    assert "event: arena_step" in content
    assert "Channel3 search matched" in content

