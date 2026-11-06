"""
Unit tests for Protocol Attack Personas (Batch A: Personas 1–4).
Verifies state machine transitions, telemetry RunEvent emissions,
and vulnerability exploitation vs RFC 9457 Guard protection.
"""
import pytest
from app.personas.protocol_personas_a import (
    RetrierPersona,
    StaleCartPersona,
    TampererPersona,
    WebhookSkepticPersona,
)
from app.schemas.contracts import RunEvent
from app.shops.hardened_shop import HardenedShop
from app.shops.naive_shop import NaiveShop


@pytest.mark.asyncio
async def test_retrier_persona_state_machine() -> None:
    """Tests Lane 1 (The Retrier) against NaiveShop (exploited) and HardenedShop (blocked)."""
    naive_shop = NaiveShop()
    hardened_shop = HardenedShop()
    run_id = "run_test_retrier_001"

    # 1. Execute on NaiveShop -> double capture
    p1_naive = RetrierPersona()
    events_naive = []
    res_naive = await p1_naive.execute(
        shop=naive_shop,
        run_id=run_id,
        events=events_naive,
    )
    assert res_naive.lane == 1
    assert res_naive.outcome == "VULNERABILITY_EXPLOITED"
    assert res_naive.amount == "$798.00"
    assert "DISPATCHING_RETRY_CAPTURE" in p1_naive.state_history
    assert p1_naive.current_state == "COMPLETED"
    assert len(events_naive) >= 3

    # 2. Execute on HardenedShop -> idempotent replayed
    p1_hardened = RetrierPersona()
    events_hardened = []
    res_hardened = await p1_hardened.execute(
        shop=hardened_shop,
        run_id=run_id,
        events=events_hardened,
    )
    assert res_hardened.lane == 1
    assert res_hardened.outcome == "BLOCKED_BY_GUARD"
    assert res_hardened.amount == "$399.00"
    assert p1_hardened.current_state == "COMPLETED"


@pytest.mark.asyncio
async def test_tamperer_persona_state_machine() -> None:
    """Tests Lane 2 (The Tamperer) against NaiveShop (exploited) and HardenedShop (409 blocked)."""
    naive_shop = NaiveShop()
    hardened_shop = HardenedShop()
    run_id = "run_test_tamperer_002"

    # 1. Execute on NaiveShop -> under-collected capture ($1.50)
    p2_naive = TampererPersona()
    events_naive = []
    res_naive = await p2_naive.execute(
        shop=naive_shop,
        run_id=run_id,
        events=events_naive,
    )
    assert res_naive.lane == 2
    assert res_naive.outcome == "VULNERABILITY_EXPLOITED"
    assert res_naive.amount == "$1.50"
    assert p2_naive.current_state == "COMPLETED"

    # 2. Execute on HardenedShop -> 409 PRICE_MISMATCH
    p2_hardened = TampererPersona()
    events_hardened = []
    res_hardened = await p2_hardened.execute(
        shop=hardened_shop,
        run_id=run_id,
        events=events_hardened,
    )
    assert res_hardened.lane == 2
    assert res_hardened.outcome == "BLOCKED_BY_GUARD"
    assert res_hardened.error_code == "PRICE_MISMATCH_REAUTHORIZATION_REQUIRED"
    assert "BLOCKED_BY_GUARD" in p2_hardened.state_history
    assert p2_hardened.current_state == "COMPLETED"


@pytest.mark.asyncio
async def test_stale_cart_persona_state_machine() -> None:
    """Tests Lane 3 (The Stale Cart) against NaiveShop (exploited) and HardenedShop (409 blocked)."""
    naive_shop = NaiveShop()
    hardened_shop = HardenedShop()
    run_id = "run_test_stale_003"

    # 1. Execute on NaiveShop -> stale price accepted ($150.00)
    p3_naive = StaleCartPersona()
    events_naive = []
    res_naive = await p3_naive.execute(
        shop=naive_shop,
        run_id=run_id,
        events=events_naive,
    )
    assert res_naive.lane == 3
    assert res_naive.outcome == "VULNERABILITY_EXPLOITED"
    assert res_naive.amount == "$150.00"
    assert p3_naive.current_state == "COMPLETED"

    # 2. Execute on HardenedShop -> 409 PRICE_MISMATCH
    p3_hardened = StaleCartPersona()
    events_hardened = []
    res_hardened = await p3_hardened.execute(
        shop=hardened_shop,
        run_id=run_id,
        events=events_hardened,
    )
    assert res_hardened.lane == 3
    assert res_hardened.outcome == "BLOCKED_BY_GUARD"
    assert res_hardened.error_code == "PRICE_MISMATCH_REAUTHORIZATION_REQUIRED"
    assert res_hardened.amount == "$199.00"
    assert p3_hardened.current_state == "COMPLETED"


@pytest.mark.asyncio
async def test_webhook_skeptic_persona_state_machine() -> None:
    """Tests Lane 4 (The Webhook Skeptic) against NaiveShop (exploited) and HardenedShop (401 blocked)."""
    naive_shop = NaiveShop()
    hardened_shop = HardenedShop()
    run_id = "run_test_webhook_004"

    # 1. Execute on NaiveShop -> unverified webhook accepted
    p4_naive = WebhookSkepticPersona()
    events_naive = []
    res_naive = await p4_naive.execute(
        shop=naive_shop,
        run_id=run_id,
        events=events_naive,
    )
    assert res_naive.lane == 4
    assert res_naive.outcome == "VULNERABILITY_EXPLOITED"
    assert p4_naive.current_state == "COMPLETED"

    # 2. Execute on HardenedShop -> 401 WEBHOOK_SIGNATURE_INVALID
    p4_hardened = WebhookSkepticPersona()
    events_hardened = []
    res_hardened = await p4_hardened.execute(
        shop=hardened_shop,
        run_id=run_id,
        events=events_hardened,
    )
    assert res_hardened.lane == 4
    assert res_hardened.outcome == "BLOCKED_BY_GUARD"
    assert res_hardened.error_code == "WEBHOOK_SIGNATURE_INVALID"
    assert "BLOCKED_BY_GUARD" in p4_hardened.state_history
    assert p4_hardened.current_state == "COMPLETED"


@pytest.mark.asyncio
async def test_persona_event_emission_contract() -> None:
    """Verifies that all emitted events contain valid timestamps, lane, and non-empty actions."""
    hardened_shop = HardenedShop()
    streamed_events = []

    def on_event(ev: RunEvent) -> None:
        streamed_events.append(ev)

    persona = RetrierPersona()
    events = []
    await persona.execute(
        shop=hardened_shop,
        run_id="run_test_events_005",
        events=events,
        event_callback=on_event,
    )

    assert len(streamed_events) > 0
    assert len(events) == len(streamed_events)
    for ev in streamed_events:
        assert ev.lane == 1
        assert ev.persona_id == "the_retrier"
        assert ev.timestamp is not None
        assert len(ev.action) > 0

