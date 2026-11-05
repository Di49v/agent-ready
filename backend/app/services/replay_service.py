"""
Replay and Blueprint Service Layer.
Dispatches requests to isolated mock fixtures in development/replay mode,
and serves as the clean provider interface for live Stage 2-4 engines.
"""
import asyncio
from typing import AsyncIterator, Dict, List, Optional
from app.core.config import get_settings
from app.mocks.replay_fixtures import (
    get_mock_ledger_snapshot,
    get_mock_personas,
    get_mock_report_markdown,
    get_mock_run_events,
    get_mock_run_findings,
    get_mock_run_summary,
    get_mock_target,
    get_mock_targets,
)
from app.schemas.contracts import (
    FindingDetail,
    LedgerSnapshot,
    PersonaSpec,
    RunCreateRequest,
    RunEvent,
    RunReportResponse,
    RunSummary,
    TargetStore,
)
from app.schemas.problem_details import ProblemException

# In-memory registry for dynamically created targets and runs in blueprint mode
_DYNAMIC_TARGETS: Dict[str, TargetStore] = {}
_ACTIVE_RUNS: Dict[str, RunSummary] = {}


class ReplayService:
    """Service handling crash-test run orchestration in mock blueprint and replay mode."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def list_targets(self) -> List[TargetStore]:
        """Returns pre-registered demo targets plus any user-registered targets."""
        builtin = get_mock_targets()
        return list(builtin) + list(_DYNAMIC_TARGETS.values())

    def get_target(self, target_id: str) -> Optional[TargetStore]:
        """Retrieves target by ID."""
        if target_id in _DYNAMIC_TARGETS:
            return _DYNAMIC_TARGETS[target_id]
        return get_mock_target(target_id)

    def create_target(self, target: TargetStore) -> TargetStore:
        """Registers a new target store."""
        _DYNAMIC_TARGETS[target.id] = target
        return target

    def list_personas(self) -> List[PersonaSpec]:
        """Returns the 9-persona test pack."""
        return get_mock_personas()

    def create_run(self, req: RunCreateRequest) -> RunSummary:
        """
        Creates and queues a new crash test run.
        In blueprint mode (or with replay=True), immediately returns the realistic fixture summary.
        """
        target = self.get_target(req.target)
        if not target:
            raise ProblemException.not_found("TargetStore", req.target)

        run_summary = get_mock_run_summary(target_id=req.target, seed=req.seed)
        _ACTIVE_RUNS[run_summary.id] = run_summary
        return run_summary

    def get_run(self, run_id: str) -> RunSummary:
        """Retrieves a run by ID."""
        if run_id in _ACTIVE_RUNS:
            return _ACTIVE_RUNS[run_id]

        # Check if it matches mock run naming pattern (e.g. run_42_naive_shop or run_42_hardened_shop)
        if "hardened" in run_id.lower():
            summary = get_mock_run_summary("hardened-shop", seed=42)
            summary.id = run_id
            _ACTIVE_RUNS[run_id] = summary
            return summary
        elif "naive" in run_id.lower():
            summary = get_mock_run_summary("naive-shop", seed=42)
            summary.id = run_id
            _ACTIVE_RUNS[run_id] = summary
            return summary

        raise ProblemException.not_found("Run", run_id)

    def get_run_findings(self, run_id: str) -> List[FindingDetail]:
        """Retrieves findings for a run."""
        # Ensure run exists
        self.get_run(run_id)
        return get_mock_run_findings(run_id)

    def get_ledger_snapshot(self, run_id: str) -> LedgerSnapshot:
        """Retrieves the dual-ledger comparison snapshot."""
        self.get_run(run_id)
        return get_mock_ledger_snapshot(run_id)

    def get_run_report(self, run_id: str) -> RunReportResponse:
        """Generates a complete JSON + Markdown audit report."""
        summary = self.get_run(run_id)
        md = get_mock_report_markdown(run_id)
        return RunReportResponse(
            run_id=run_id,
            summary=summary,
            markdown=md,
            generated_at=summary.completed_at or summary.created_at,
        )

    def rerun_run(self, base_run_id: str, target_override: Optional[str] = None) -> RunSummary:
        """
        Re-runs the same seed against either the original target or a patched target (e.g. hardened-shop).
        Powers the Red-to-Green judge demo flow.
        """
        base_run = self.get_run(base_run_id)
        target_to_run = target_override or base_run.target
        new_summary = get_mock_run_summary(target_id=target_to_run, seed=base_run.seed)
        new_summary.id = f"rerun_{base_run.seed}_{target_to_run.replace('-', '_')}"
        _ACTIVE_RUNS[new_summary.id] = new_summary
        return new_summary

    def get_badge_svg(self, target_id: str) -> str:
        """Generates an Agent-Readiness SVG badge based on target's latest score."""
        target = self.get_target(target_id)
        if not target:
            score = 0
            label = "unknown"
            bg_color = "#6B7280"
        elif "hardened" in target_id.lower():
            score = 95
            label = "agent-ready"
            bg_color = "#10B981"  # Emerald
        else:
            score = 18
            label = "vulnerable"
            bg_color = "#F43F5E"  # Rose

        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="190" height="28" role="img" aria-label="AgentReady: {score}/100">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="a">
    <rect width="190" height="28" rx="4" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#a)">
    <rect width="110" height="28" fill="#11131A"/>
    <rect x="110" width="80" height="28" fill="{bg_color}"/>
    <rect width="190" height="28" fill="url(#b)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="JetBrains Mono,DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="55" y="18" fill="#000" fill-opacity=".3">AgentReady</text>
    <text x="55" y="17" fill="#E2E8F0">AgentReady</text>
    <text x="150" y="18" fill="#000" fill-opacity=".3">{score}/100</text>
    <text x="150" y="17" fill="#fff" font-weight="bold">{score}/100</text>
  </g>
</svg>"""

    async def stream_run_events(
        self,
        run_id: str,
        delay_seconds: float = 0.02,
    ) -> AsyncIterator[str]:
        """
        Yields Server-Sent Events (SSE) telemetry frames for the live dashboard.
        Format: event: <type>\\ndata: <json>\\n\\n
        """
        # Validate that the run is recognized
        summary = self.get_run(run_id)
        events: List[RunEvent] = get_mock_run_events(target_id=summary.target, seed=summary.seed)

        for event in events:
            # Update run_id on the event frame
            event.run_id = run_id
            payload = event.model_dump_json()
            yield f"event: {event.event}\ndata: {payload}\n\n"
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)


_service_instance: Optional[ReplayService] = None


def get_replay_service() -> ReplayService:
    """Singleton getter for ReplayService."""
    global _service_instance
    if _service_instance is None:
        _service_instance = ReplayService()
    return _service_instance

