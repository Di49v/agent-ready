"""
Unit tests for RunOrchestrator (Task 4.2).
Verifies live swarm orchestration, dual-ledger grading, SSE streaming,
and Red-to-Green rerun capability.
"""
import pytest
from app.core.config import get_settings
from app.schemas.contracts import AutoReversalPolicy, RunCreateRequest, RunStatus
from app.services.run_orchestrator import RunOrchestrator, get_run_orchestrator


@pytest.mark.asyncio
async def test_orchestrator_live_run_execution() -> None:
    """Verifies that RunOrchestrator executes live Swarm, Reconciler, and Grader end-to-end."""
    settings = get_settings()
    original_mock = settings.use_mock_blueprint
    try:
        # Enable live execution mode
        settings.use_mock_blueprint = False

        orchestrator = RunOrchestrator()
        req = RunCreateRequest(
            target="naive-shop",
            pack="full",
            seed=42,
            policy=AutoReversalPolicy.AUTO,
            replay=False,
        )

        summary = await orchestrator.create_run(req)

        assert summary.id.startswith("run_42_naive_shop")
        assert summary.target == "naive-shop"
        assert summary.status == RunStatus.COMPLETE
        assert summary.score is not None
        assert summary.score <= 30  # NaiveShop vulnerable score
        assert summary.total_findings > 0

        # Retrieve through orchestrator getter methods
        fetched_summary = orchestrator.get_run(summary.id)
        assert fetched_summary.id == summary.id

        findings = orchestrator.get_run_findings(summary.id)
        assert len(findings) == summary.total_findings

        ledger = orchestrator.get_ledger_snapshot(summary.id)
        assert len(ledger.dual_rows) == 9
    finally:
        settings.use_mock_blueprint = original_mock


@pytest.mark.asyncio
async def test_orchestrator_rerun_red_to_green() -> None:
    """Verifies rerun_run on HardenedShop transitions score from red to green (95/100)."""
    settings = get_settings()
    original_mock = settings.use_mock_blueprint
    try:
        settings.use_mock_blueprint = False
        orchestrator = RunOrchestrator()

        # 1. Base run on NaiveShop
        req = RunCreateRequest(target="naive-shop", seed=101, policy=AutoReversalPolicy.AUTO, replay=False)
        base_summary = await orchestrator.create_run(req)
        assert base_summary.score is not None and base_summary.score < 35

        # 2. Re-run on HardenedShop
        rerun_summary = await orchestrator.rerun_run(base_run_id=base_summary.id, target_override="hardened-shop")
        assert rerun_summary.target == "hardened-shop"
        assert rerun_summary.status == RunStatus.COMPLETE
        # HardenedShop achieves 95/100
        assert rerun_summary.score == 95
    finally:
        settings.use_mock_blueprint = original_mock


@pytest.mark.asyncio
async def test_orchestrator_sse_stream() -> None:
    """Verifies that stream_run_events emits live or recorded SSE frames."""
    orchestrator = get_run_orchestrator()
    events = []
    async for frame in orchestrator.stream_run_events("run_42_naive_shop", delay_seconds=0.0):
        events.append(frame)
        if len(events) >= 5:
            break

    assert len(events) >= 5
    for frame in events:
        assert frame.startswith("event: ")
        assert "\ndata: " in frame

