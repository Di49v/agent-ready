"""
FastAPI Public v1 Routers for AgentReady Lab (Section B3.9).
"""
from typing import List, Optional
from fastapi import APIRouter, Body, Path, Response, status
from pydantic import BaseModel, Field
from app.api.events_sse import router as events_router
from app.schemas.contracts import (
    FindingDetail,
    LedgerSnapshot,
    PersonaSpec,
    RunCreateRequest,
    RunReportResponse,
    RunSummary,
    TargetStore,
)
from app.services.run_orchestrator import get_run_orchestrator

router = APIRouter()
# Mount SSE event stream router
router.include_router(events_router)


class RerunRequest(BaseModel):
    """Optional payload for re-running a seed against an alternative target."""
    target_override: Optional[str] = Field(
        default=None,
        description="Target ID override (e.g. 'hardened-shop' to verify fix remediation)",
    )


# -----------------------------------------------------------------------------
# Target Stores
# -----------------------------------------------------------------------------

@router.get(
    "/v1/targets",
    response_model=List[TargetStore],
    summary="List registered targets",
    description="Returns pre-registered demo targets (Naive Shop, Hardened Shop) and user-registered stores.",
)
def list_targets() -> List[TargetStore]:
    orchestrator = get_run_orchestrator()
    return orchestrator.list_targets()


@router.post(
    "/v1/targets",
    response_model=TargetStore,
    status_code=status.HTTP_201_CREATED,
    summary="Register a target store",
    description="Registers an external or custom target sandbox store.",
)
def create_target(target: TargetStore) -> TargetStore:
    orchestrator = get_run_orchestrator()
    return orchestrator.create_target(target)


# -----------------------------------------------------------------------------
# Personas
# -----------------------------------------------------------------------------

@router.get(
    "/v1/personas",
    response_model=List[PersonaSpec],
    summary="List adversarial buyer personas",
    description="Returns metadata for the 9 adversarial AI buyer personas in the test pack.",
)
def list_personas() -> List[PersonaSpec]:
    orchestrator = get_run_orchestrator()
    return orchestrator.list_personas()


# -----------------------------------------------------------------------------
# Runs & Evaluation
# -----------------------------------------------------------------------------

@router.post(
    "/v1/runs",
    response_model=RunSummary,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start a crash-test run",
    description="Triggers a crash test run with the specified target, pack, and seed.",
)
async def create_run(request: RunCreateRequest) -> RunSummary:
    orchestrator = get_run_orchestrator()
    return await orchestrator.create_run(request)


@router.get(
    "/v1/runs/{id}",
    response_model=RunSummary,
    summary="Get run status and score",
    description="Retrieves the current status, Agent-Readiness Score, and summary breakdown.",
)
def get_run(id: str = Path(..., description="Run ID")) -> RunSummary:
    orchestrator = get_run_orchestrator()
    return orchestrator.get_run(id)


@router.get(
    "/v1/runs/{id}/findings",
    response_model=List[FindingDetail],
    summary="List findings with PayPal evidence IDs",
    description="Returns all invariant rule violations detected by the Reconciler.",
)
def get_run_findings(id: str = Path(..., description="Run ID")) -> List[FindingDetail]:
    orchestrator = get_run_orchestrator()
    return orchestrator.get_run_findings(id)


@router.get(
    "/v1/runs/{id}/ledger",
    response_model=LedgerSnapshot,
    summary="Get side-by-side dual-ledger snapshot",
    description="Returns normalized side-by-side rows comparing PayPal Sandbox records vs Store Probe rows.",
)
def get_run_ledger(id: str = Path(..., description="Run ID")) -> LedgerSnapshot:
    orchestrator = get_run_orchestrator()
    return orchestrator.get_ledger_snapshot(id)


@router.get(
    "/v1/runs/{id}/report",
    response_model=RunReportResponse,
    summary="Get comprehensive audit report",
    description="Returns Markdown and JSON audit report for merchant export.",
)
def get_run_report(id: str = Path(..., description="Run ID")) -> RunReportResponse:
    orchestrator = get_run_orchestrator()
    return orchestrator.get_run_report(id)


@router.post(
    "/v1/runs/{id}/rerun",
    response_model=RunSummary,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Re-run same seed against target",
    description="Re-runs the exact same seed against the target store or an alternative patched target.",
)
async def rerun_run(
    id: str = Path(..., description="Base run ID to replay"),
    body: Optional[RerunRequest] = Body(default=None),
) -> RunSummary:
    orchestrator = get_run_orchestrator()
    target_override = body.target_override if body else None
    return await orchestrator.rerun_run(base_run_id=id, target_override=target_override)


# -----------------------------------------------------------------------------
# Badge & Webhooks
# -----------------------------------------------------------------------------

@router.get(
    "/v1/badge/{target}.svg",
    summary="Get Agent-Readiness SVG badge",
    description="Generates an SVG score badge for README or merchant site.",
    responses={
        200: {
            "content": {"image/svg+xml": {}},
            "description": "SVG score badge image",
        }
    },
)
def get_badge(target: str = Path(..., description="Target store ID")) -> Response:
    orchestrator = get_run_orchestrator()
    svg = orchestrator.get_badge_svg(target)
    return Response(content=svg, media_type="image/svg+xml")


