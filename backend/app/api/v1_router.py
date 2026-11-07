"""
FastAPI Public v1 Routers for AgentReady Lab (Section B3.9).
Clean OpenAPI 3.1 operation IDs for typed APIMatic SDK generation.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, Path, Query, Request, Response, status
from pydantic import BaseModel, Field
from app.api.events_sse import router as events_router
from app.core.abuse_guard import get_abuse_guard
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
    operation_id="listTargets",
    tags=["Targets"],
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
    operation_id="createTarget",
    tags=["Targets"],
    summary="Register a target store",
    description="Registers an external or custom target sandbox store.",
)
def create_target(target: TargetStore, http_request: Request) -> TargetStore:
    guard = get_abuse_guard()
    guard.verify_api_key(http_request)
    guard.validate_target(target)
    orchestrator = get_run_orchestrator()
    return orchestrator.create_target(target)


# -----------------------------------------------------------------------------
# Personas
# -----------------------------------------------------------------------------

@router.get(
    "/v1/personas",
    response_model=List[PersonaSpec],
    operation_id="listPersonas",
    tags=["Personas"],
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
    operation_id="createRun",
    tags=["Runs"],
    summary="Start a crash-test run",
    description="Triggers a crash test run with the specified target, pack, seed, and optional callback URL.",
)
async def create_run(request: RunCreateRequest, http_request: Request) -> RunSummary:
    guard = get_abuse_guard()
    guard.verify_api_key(http_request)
    guard.check_and_record_run_rate_limit(http_request)
    guard.validate_target(request.target)
    orchestrator = get_run_orchestrator()
    return await orchestrator.create_run(request)


@router.get(
    "/v1/runs/{id}",
    response_model=RunSummary,
    operation_id="getRun",
    tags=["Runs"],
    summary="Get run status and score",
    description="Retrieves the current status, Agent-Readiness Score, and summary breakdown.",
)
def get_run(id: str = Path(..., description="Run ID")) -> RunSummary:
    orchestrator = get_run_orchestrator()
    return orchestrator.get_run(id)


@router.get(
    "/v1/runs/{id}/findings",
    response_model=List[FindingDetail],
    operation_id="getRunFindings",
    tags=["Runs"],
    summary="List findings with PayPal evidence IDs",
    description="Returns all invariant rule violations detected by the Reconciler.",
)
def get_run_findings(id: str = Path(..., description="Run ID")) -> List[FindingDetail]:
    orchestrator = get_run_orchestrator()
    return orchestrator.get_run_findings(id)


@router.get(
    "/v1/runs/{id}/ledger",
    response_model=LedgerSnapshot,
    operation_id="getRunLedger",
    tags=["Runs"],
    summary="Get side-by-side dual-ledger snapshot",
    description="Returns normalized side-by-side rows comparing PayPal Sandbox records vs Store Probe rows.",
)
def get_run_ledger(id: str = Path(..., description="Run ID")) -> LedgerSnapshot:
    orchestrator = get_run_orchestrator()
    return orchestrator.get_ledger_snapshot(id)


@router.get(
    "/v1/runs/{id}/report",
    operation_id="getRunReport",
    tags=["Runs"],
    summary="Get comprehensive audit report",
    description="Returns Markdown or JSON audit report for merchant export.",
    responses={
        200: {
            "description": "JSON audit report or plain Markdown text",
            "content": {
                "application/json": {"schema": {"$ref": "#/components/schemas/RunReportResponse"}},
                "text/markdown": {"schema": {"type": "string"}},
            },
        }
    },
)
def get_run_report(
    id: str = Path(..., description="Run ID"),
    format: Optional[str] = Query(default="json", description="Report format: 'json' or 'markdown'"),
) -> Response:
    orchestrator = get_run_orchestrator()
    report = orchestrator.get_run_report(id)
    if format and format.lower() in ("markdown", "md"):
        return Response(content=report.markdown, media_type="text/markdown; charset=utf-8")
    return Response(
        content=report.model_dump_json(),
        media_type="application/json",
    )


@router.get(
    "/v1/runs/{id}/postman",
    operation_id="exportRunPostmanCollection",
    tags=["Runs"],
    summary="Export Postman collection for run findings",
    description="Generates a downloadable Postman Collection v2.1.0 with reproduction requests for failed findings.",
    responses={
        200: {
            "content": {"application/json": {}},
            "description": "Postman Collection v2.1.0 JSON",
        }
    },
)
def export_run_postman(
    id: str = Path(..., description="Run ID"),
) -> Response:
    orchestrator = get_run_orchestrator()
    collection_json = orchestrator.export_postman_collection(id)
    return Response(
        content=collection_json,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="agent-ready-run-{id}.postman_collection.json"'},
    )


@router.post(
    "/v1/runs/{id}/rerun",
    response_model=RunSummary,
    status_code=status.HTTP_202_ACCEPTED,
    operation_id="rerunRun",
    tags=["Runs"],
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
# Badge & Benchmark
# -----------------------------------------------------------------------------

@router.get(
    "/v1/badge/{target}.svg",
    operation_id="getScoreBadge",
    tags=["Badges"],
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


@router.get(
    "/v1/benchmark",
    operation_id="getBenchmarkMatrix",
    tags=["Benchmark"],
    summary="Get 12-bug benchmark matrix",
    description="Returns the 12-bug detection matrix with true positive and false alarm verification data.",
)
def get_benchmark_matrix() -> Dict[str, Any]:
    from app.fix_engine.cache import get_explanation_cache
    cache = get_explanation_cache()
    return {"bugs": list(cache._cache.values()), "total": len(cache._cache)}



