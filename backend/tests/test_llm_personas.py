"""
Unit tests for Live LLM Adversarial Personas (Batch C: Personas 8 and 9).
Verifies state machine transitions, telemetry RunEvent emissions,
and vulnerability exploitation vs RFC 9457 Guard protection on Naive and Hardened stores.
"""
import pytest
from app.personas.llm_personas import (
    MisreaderPersona,
    ContentTrapPersona,
)
from app.schemas.contracts import RunEvent
from app.services.swarm_engine import SwarmEngine
from app.shops.hardened_shop import HardenedShop
from app.shops.naive_shop import NaiveShop


@pytest.mark.asyncio
async def test_misreader_persona_state_machine() -> None:
    """Tests Lane 8 (The Misreader) against NaiveShop (exploited) and HardenedShop (422 blocked)."""
    naive_shop = NaiveShop()
    hardened_shop = HardenedShop()
    run_id = "run_test_misreader_008"

    # 1. Execute on NaiveShop -> Ambiguous variant order accepted
    p8_naive = MisreaderPersona()
    assert p8_naive.lane == 8
    assert p8_naive.driven_by == "live_llm"
    assert p8_naive.wave == 2

    events_naive: list[RunEvent] = []
    res_naive = await p8_naive.execute(
        shop=naive_shop,
        run_id=run_id,
        events=events_naive,
    )
    assert res_naive.lane == 8
    assert res_naive.outcome == "VULNERABILITY_EXPLOITED"
    assert res_naive.amount == "$130.00"
    assert "QUERYING_PRODUCT_CATALOG" in p8_naive.state_history
    assert "INVOKING_LLM_AGENT" in p8_naive.state_history
    assert "DISPATCHING_CHECKOUT_ATTEMPT" in p8_naive.state_history
    assert p8_naive.current_state == "COMPLETED"

    # 2. Execute on HardenedShop -> 422 AMBIGUOUS_VARIANT_CLARIFICATION_REQUIRED
    p8_hardened = MisreaderPersona()
    events_hardened: list[RunEvent] = []
    res_hardened = await p8_hardened.execute(
        shop=hardened_shop,
        run_id=run_id,
        events=events_hardened,
    )
    assert res_hardened.lane == 8
    assert res_hardened.outcome == "BLOCKED_BY_GUARD"
    assert res_hardened.error_code == "AMBIGUOUS_VARIANT_CLARIFICATION_REQUIRED"
    assert "BLOCKED_BY_GUARD" in p8_hardened.state_history
    assert p8_hardened.current_state == "COMPLETED"


@pytest.mark.asyncio
async def test_content_trap_persona_state_machine() -> None:
    """Tests Lane 9 (The Content Trap) against NaiveShop (injected) and HardenedShop (409 blocked)."""
    naive_shop = NaiveShop()
    hardened_shop = HardenedShop()
    run_id = "run_test_trap_009"

    # 1. Execute on NaiveShop -> Injected order accepted (5 units instead of signed 1 unit)
    p9_naive = ContentTrapPersona()
    assert p9_naive.lane == 9
    assert p9_naive.driven_by == "live_llm"
    assert p9_naive.wave == 2

    events_naive: list[RunEvent] = []
    res_naive = await p9_naive.execute(
        shop=naive_shop,
        run_id=run_id,
        events=events_naive,
    )
    assert res_naive.lane == 9
    assert res_naive.outcome == "VULNERABILITY_EXPLOITED"
    assert "SIGNING_HUMAN_INTENT_RECEIPT" in p9_naive.state_history
    assert "INVOKING_LLM_AGENT_WITH_INJECTION" in p9_naive.state_history
    assert "DISPATCHING_TAMPERED_CART" in p9_naive.state_history
    assert p9_naive.current_state == "COMPLETED"

    # 2. Execute on HardenedShop -> 409 CART_INTENT_MISMATCH
    p9_hardened = ContentTrapPersona()
    events_hardened: list[RunEvent] = []
    res_hardened = await p9_hardened.execute(
        shop=hardened_shop,
        run_id=run_id,
        events=events_hardened,
    )
    assert res_hardened.lane == 9
    assert res_hardened.outcome == "BLOCKED_BY_GUARD"
    assert res_hardened.error_code in ("CART_INTENT_MISMATCH", "PRICE_MISMATCH_REAUTHORIZATION_REQUIRED")
    assert "BLOCKED_BY_GUARD" in p9_hardened.state_history
    assert p9_hardened.current_state == "COMPLETED"


@pytest.mark.asyncio
async def test_llm_personas_event_emission_contract() -> None:
    """Verifies that LLM personas emit valid RunEvent frames with expected metadata."""
    shop = HardenedShop()
    captured_events: list[RunEvent] = []

    def on_event(event: RunEvent) -> None:
        captured_events.append(event)

    p8 = MisreaderPersona()
    await p8.execute(shop=shop, run_id="run_test_stream_008", events=[], event_callback=on_event)

    assert len(captured_events) >= 2
    for ev in captured_events:
        assert ev.run_id == "run_test_stream_008"
        assert ev.lane == 8
        assert ev.persona_id == "the_misreader"
        assert ev.timestamp is not None
        assert ev.action is not None


@pytest.mark.asyncio
async def test_full_9_persona_swarm_execution_with_llm_lanes() -> None:
    """Verifies full 9-persona swarm runs end to end across both waves including LLM lanes 8 and 9."""
    engine = SwarmEngine()
    result = await engine.execute_swarm(target_id="naive-shop", seed=42)

    assert result.total_lanes == 9
    assert len(result.lane_results) == 9
    assert 8 in result.lane_results
    assert 9 in result.lane_results
    assert result.lane_results[8].persona_id == "the_misreader"
    assert result.lane_results[9].persona_id == "the_content_trap"
    assert result.duration_sec > 0.0

