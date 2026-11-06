"""
Unit tests for Protocol Attack Personas (Batch B: Personas 5–7).
Verifies state machine transitions, telemetry RunEvent emissions,
and vulnerability exploitation vs RFC 9457 Guard protection.
"""
import pytest
from app.personas.protocol_personas_b import (
    DisputerPersona,
    GhostOrderPersona,
    RefunderPersona,
)
from app.schemas.contracts import RunEvent
from app.shops.hardened_shop import HardenedShop
from app.shops.naive_shop import NaiveShop


@pytest.mark.asyncio
async def test_refunder_persona_state_machine() -> None:
    """Tests Lane 5 (The Refunder) against NaiveShop (exploited) and HardenedShop (422 blocked)."""
    naive_shop = NaiveShop()
    hardened_shop = HardenedShop()
    run_id = "run_test_refunder_005"

    # 1. Execute on NaiveShop -> Over-refund accepted ($200.00 on $99.99 capture)
    p5_naive = RefunderPersona()
    events_naive = []
    res_naive = await p5_naive.execute(
        shop=naive_shop,
        run_id=run_id,
        events=events_naive,
    )
    assert res_naive.lane == 5
    assert res_naive.outcome == "VULNERABILITY_EXPLOITED"
    assert res_naive.amount == "$200.00"
    assert "DISPATCHING_OVER_REFUND" in p5_naive.state_history
    assert p5_naive.current_state == "COMPLETED"

    # 2. Execute on HardenedShop -> 422 REFUND_EXCEEDS_CAPTURE
    p5_hardened = RefunderPersona()
    events_hardened = []
    res_hardened = await p5_hardened.execute(
        shop=hardened_shop,
        run_id=run_id,
        events=events_hardened,
    )
    assert res_hardened.lane == 5
    assert res_hardened.outcome == "BLOCKED_BY_GUARD"
    assert res_hardened.error_code == "REFUND_EXCEEDS_CAPTURE"
    assert res_hardened.amount == "$99.99"
    assert "BLOCKED_BY_GUARD" in p5_hardened.state_history
    assert p5_hardened.current_state == "COMPLETED"


@pytest.mark.asyncio
async def test_ghost_order_persona_state_machine() -> None:
    """Tests Lane 6 (The Ghost Order) against NaiveShop (orphan capture) and HardenedShop (fulfilled)."""
    naive_shop = NaiveShop()
    hardened_shop = HardenedShop()
    run_id = "run_test_ghost_006"

    # 1. Execute on NaiveShop -> Store order dropped (Orphan Money)
    p6_naive = GhostOrderPersona()
    events_naive = []
    res_naive = await p6_naive.execute(
        shop=naive_shop,
        run_id=run_id,
        events=events_naive,
    )
    assert res_naive.lane == 6
    assert res_naive.outcome == "VULNERABILITY_EXPLOITED"
    assert res_naive.store_order_id is None
    assert p6_naive.current_state == "COMPLETED"

    # 2. Execute on HardenedShop -> Fulfill record created
    p6_hardened = GhostOrderPersona()
    events_hardened = []
    res_hardened = await p6_hardened.execute(
        shop=hardened_shop,
        run_id=run_id,
        events=events_hardened,
    )
    assert res_hardened.lane == 6
    assert res_hardened.outcome == "SUCCESS"
    assert res_hardened.store_order_id is not None
    assert p6_hardened.current_state == "COMPLETED"


@pytest.mark.asyncio
async def test_disputer_persona_state_machine() -> None:
    """Tests Lane 7 (The Disputer) against NaiveShop (missing tracking) and HardenedShop (tracking ready)."""
    naive_shop = NaiveShop()
    hardened_shop = HardenedShop()
    run_id = "run_test_disputer_007"

    # 1. Execute on NaiveShop -> Tracking missing
    p7_naive = DisputerPersona()
    events_naive = []
    res_naive = await p7_naive.execute(
        shop=naive_shop,
        run_id=run_id,
        events=events_naive,
    )
    assert res_naive.lane == 7
    assert res_naive.outcome == "VULNERABILITY_EXPLOITED"
    assert "AUDITING_DISPUTE_EVIDENCE" in p7_naive.state_history
    assert p7_naive.current_state == "COMPLETED"

    # 2. Execute on HardenedShop -> Tracking linked and ready
    p7_hardened = DisputerPersona()
    events_hardened = []
    res_hardened = await p7_hardened.execute(
        shop=hardened_shop,
        run_id=run_id,
        events=events_hardened,
    )
    assert res_hardened.lane == 7
    assert res_hardened.outcome == "SUCCESS"
    assert p7_hardened.current_state == "COMPLETED"


@pytest.mark.asyncio
async def test_personas_b_event_emission_contract() -> None:
    """Verifies that all emitted events for Personas 5, 6, 7 carry valid metadata."""
    hardened_shop = HardenedShop()
    streamed_events = []

    def on_event(ev: RunEvent) -> None:
        streamed_events.append(ev)

    for persona_cls in [RefunderPersona, GhostOrderPersona, DisputerPersona]:
        persona = persona_cls()
        events = []
        await persona.execute(
            shop=hardened_shop,
            run_id="run_test_events_b",
            events=events,
            event_callback=on_event,
        )
        assert len(events) > 0
        for ev in events:
            assert ev.lane in {5, 6, 7}
            assert ev.timestamp is not None
            assert len(ev.action) > 0

