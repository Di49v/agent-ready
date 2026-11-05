"""
Server-Sent Events (SSE) telemetry router for live swarm lanes and Judge Arena (Section B11).
"""
from fastapi import APIRouter, Path
from fastapi.responses import StreamingResponse
from app.services.replay_service import get_replay_service

router = APIRouter()


@router.get(
    "/v1/runs/{id}/events",
    summary="Stream live run telemetry frames via SSE",
    description="Streams real-time agent_step, paypal_event, store_ledger_row, finding, and run_completed events.",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "SSE telemetry stream",
            "content": {"text/event-stream": {}},
        },
        404: {"description": "Run not found"},
    },
)
async def stream_run_events(
    id: str = Path(..., description="Run identifier"),
):
    service = get_replay_service()
    # Eagerly validate run existence; raises 404 ProblemException if not found
    service.get_run(id)

    return StreamingResponse(
        service.stream_run_events(id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

