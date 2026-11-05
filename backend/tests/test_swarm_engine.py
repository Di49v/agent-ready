"""
Unit tests for the 9-Persona Adversarial Swarm Engine.
Verifies two-wave batched execution (Semaphore 5), live RunEvent streaming,
vulnerability exploitation on NaiveShop, and RFC 9457 guard protection on HardenedShop.
"""
import pytest
from app.schemas.contracts import RunEvent
from app.services.swarm_engine import SwarmEngine, get_swarm_engine


@pytest.mark.asyncio
async def test_swarm_execution_on_naive_shop() -> None:
    """Verifies that all 9 lanes execute against NaiveShop and detect expected vulnerabilities."""
    engine = SwarmEngine()
    streamed_events = []

    def on_event(ev: RunEvent) -> None:
        streamed_events.append(ev)

    res = await engine.execute_swarm(
        target_id="naive-shop",
        event_callback=on_event,
    )

    assert res.total_lanes == 9
    assert len(res.lane_results) == 9
    assert res.duration_sec < 15.0  # Must finish within 15-second SLA
    assert len(streamed_events) > 10

    # Lane 1 (The Retrier): Double capture exploited
    l1 = res.lane_results[1]
    assert l1.outcome == "VULNERABILITY_EXPLOITED"
    assert l1.amount == "$798.00"

    # Lane 2 (The Tamperer): Client price tamper accepted ($1.50)
    l2 = res.lane_results[2]
    assert l2.outcome == "VULNERABILITY_EXPLOITED"
    assert l2.amount == "$1.50"

    # Lane 6 (The Ghost Order): Orphan capture created (no store order record)
    l6 = res.lane_results[6]
    assert l6.outcome == "VULNERABILITY_EXPLOITED"
    assert l6.store_order_id is None


@pytest.mark.asyncio
async def test_swarm_execution_on_hardened_shop() -> None:
    """Verifies that all 9 lanes execute against HardenedShop and attacks are blocked by Guard."""
    engine = SwarmEngine()
    streamed_events = []

    res = await engine.execute_swarm(
        target_id="hardened-shop",
        event_callback=lambda ev: streamed_events.append(ev),
    )

    assert res.total_lanes == 9
    assert len(res.lane_results) == 9
    assert res.duration_sec < 15.0

    # Lane 1 (The Retrier): Idempotent cache hit
    l1 = res.lane_results[1]
    assert l1.outcome == "BLOCKED_BY_GUARD"
    assert l1.amount == "$399.00"

    # Lane 2 (The Tamperer): Blocked with 409 PRICE_MISMATCH
    l2 = res.lane_results[2]
    assert l2.outcome == "BLOCKED_BY_GUARD"
    assert l2.error_code == "PRICE_MISMATCH_REAUTHORIZATION_REQUIRED"

    # Lane 6 (The Ghost Order): Fulfill record successfully created
    l6 = res.lane_results[6]
    assert l6.outcome == "SUCCESS"
    assert l6.store_order_id is not None

    # Lane 7 (The Disputer): Tracking evidence linked
    l7 = res.lane_results[7]
    assert l7.outcome == "SUCCESS"

    # Lane 8 (The Misreader): Blocked with 422 AMBIGUOUS_VARIANT
    l8 = res.lane_results[8]
    assert l8.outcome == "BLOCKED_BY_GUARD"
    assert l8.error_code == "AMBIGUOUS_VARIANT_CLARIFICATION_REQUIRED"

    # Lane 9 (The Content Trap): Blocked with 409 CART_INTENT_MISMATCH
    l9 = res.lane_results[9]
    assert l9.outcome == "BLOCKED_BY_GUARD"
    assert l9.error_code == "CART_INTENT_MISMATCH"


@pytest.mark.asyncio
async def test_swarm_telemetry_event_stream_structure() -> None:
    """Verifies that RunEvents conform to Section B11 event schemas."""
    engine = SwarmEngine()
    events = []

    res = await engine.execute_swarm(
        target_id="hardened-shop",
        event_callback=lambda ev: events.append(ev),
    )

    # Check for completion event
    completion_events = [ev for ev in events if ev.event == "run_completed"]
    assert len(completion_events) == 1
    assert completion_events[0].data.get("total_lanes") == 9

    # Check lane coverage
    lanes_seen = {ev.lane for ev in events if ev.lane is not None and ev.lane > 0}
    assert lanes_seen == {1, 2, 3, 4, 5, 6, 7, 8, 9}

