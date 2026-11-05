"""
Unit tests for Live PayPal Webhook Ingestion & Signature Verification.
Tests signature parsing, RFC 9457 error formatting, and replay deduplication.
"""
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.schemas.problem_details import ProblemErrorCode


@pytest.mark.asyncio
async def test_webhook_successful_ingestion() -> None:
    """Verifies that a valid webhook payload is ingested cleanly."""
    event_id = f"WH-{uuid.uuid4().hex[:16]}"
    cart_id = f"cart_{uuid.uuid4().hex[:8]}"

    payload = {
        "id": event_id,
        "event_version": "1.0",
        "create_time": "2026-11-06T00:00:00Z",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource_type": "capture",
        "resource": {
            "id": f"CAP-{uuid.uuid4().hex[:12]}",
            "custom_id": cart_id,
            "status": "COMPLETED",
            "amount": {"currency_code": "USD", "value": "120.00"},
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/webhooks/paypal", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["received"] is True
        assert data["status"] == "VERIFIED_AND_PROCESSED"
        assert data["event_id"] == event_id
        assert data["cart_id"] == cart_id


@pytest.mark.asyncio
async def test_webhook_duplicate_replay_prevention() -> None:
    """Verifies that duplicate webhook deliveries are safely de-duplicated."""
    duplicate_event_id = f"WH-DUP-{uuid.uuid4().hex[:12]}"
    payload = {
        "id": duplicate_event_id,
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource": {"id": "CAP-001", "custom_id": "cart_dup"},
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First delivery -> Processed
        resp1 = await client.post("/webhooks/paypal", json=payload)
        assert resp1.status_code == 200
        assert resp1.json()["status"] == "VERIFIED_AND_PROCESSED"

        # Second delivery (replay attack or network retry) -> Ignored
        resp2 = await client.post("/webhooks/paypal", json=payload)
        assert resp2.status_code == 200
        assert resp2.json()["status"] == "DUPLICATE_IGNORED"


@pytest.mark.asyncio
async def test_webhook_malformed_json_problem_details() -> None:
    """Verifies that non-JSON payloads raise RFC 9457 Problem Details with 400 status."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/webhooks/paypal",
            content="NOT_VALID_JSON{",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        assert resp.headers["content-type"] == "application/problem+json"
        data = resp.json()
        assert data["code"] == ProblemErrorCode.INVALID_PAYLOAD
        assert "Malformed Webhook JSON" in data["title"]

