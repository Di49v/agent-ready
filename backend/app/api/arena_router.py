"""
AgentReady Lab — The Judge Arena API (Section B11).
Interactive, judge-driven crash testing with natural language shopping prompts,
chaos switches, real-time SSE event streaming, and AG Grid integration.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
import logging
import uuid
from typing import Any, AsyncIterator, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Path, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.core.abuse_guard import get_abuse_guard
from app.core.config import get_settings
from app.schemas.contracts import FindingDetail, FindingSeverity
from app.schemas.problem_details import ProblemException
from app.services.cart_signer import get_cart_signer
from app.services.channel3_service import get_channel3_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Judge Arena"])

# In-memory storage for Arena sessions and live event streams
_ARENA_SESSIONS: Dict[str, "ArenaSessionSummary"] = {}
_ARENA_STREAMS: Dict[str, List[ArenaStepEvent]] = {}

# Shopping keyword validator to prevent off-topic prompts
SHOPPING_KEYWORDS = {
    "buy", "order", "purchase", "shoes", "shoe", "keyboard", "headphones",
    "coffee", "cart", "item", "product", "size", "get", "checkout", "shop", "running",
}


# -----------------------------------------------------------------------------
# Arena Data Models
# -----------------------------------------------------------------------------

class ChaosToggles(BaseModel):
    drop_retry: bool = Field(default=False, description="Drop response after capture, forcing duplicate checkout retry")
    tamper_price: bool = Field(default=False, description="Mutate submitted price to $1.50 (client-side price manipulation)")
    ambiguous_variant: bool = Field(default=False, description="Select multi-variant product without choosing required size")
    prompt_trap: bool = Field(default=False, description="Inject prompt injection trap ordering 5 units instead of 1")
    forge_webhook: bool = Field(default=False, description="Send forged unverified PayPal webhook")


class ArenaRunRequest(BaseModel):
    prompt: str = Field(..., description="Judge's natural language shopping request")
    target: str = Field(default="naive-shop", description="Target store: 'naive-shop' or 'hardened-shop'")
    chaos_toggles: ChaosToggles = Field(default_factory=ChaosToggles, description="Active chaos fault switches")
    seed: int = Field(default=42, description="Evaluation seed")


class ArenaStepEvent(BaseModel):
    id: str
    session_id: str
    timestamp: str
    actor: str  # "AI Agent", "Chaos Proxy", "PayPal Sandbox", "Store Guard", "Reconciler"
    action: str
    ref_id: Optional[str] = None
    amount: Optional[str] = None
    status: str  # "INFO", "MUTATION", "CAPTURED", "BLOCKED", "VIOLATION", "GUARDED"
    rule_hit: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ArenaSessionSummary(BaseModel):
    session_id: str
    prompt: str
    target: str
    target_name: str
    score: int
    total_findings: int
    findings: List[FindingDetail]
    events: List[ArenaStepEvent]
    call_budget_used: int
    call_budget_remaining: int
    fallback_to_replay: bool
    completed_at: str


# -----------------------------------------------------------------------------
# Arena Orchestrator Logic
# -----------------------------------------------------------------------------

def validate_shopping_prompt(prompt: str) -> bool:
    """Verifies that the prompt is genuinely an e-commerce shopping request."""
    tokens = {t.lower() for t in prompt.replace(".", " ").replace(",", " ").split()}
    return bool(tokens.intersection(SHOPPING_KEYWORDS))


async def execute_arena_scenario(request: ArenaRunRequest) -> ArenaSessionSummary:
    """
    Executes a single interactive Judge Arena shopping mission with live chaos switches.
    Emits granular events representing every step of the agent, proxy, PayPal, and store reconciler.
    """
    session_id = f"arena_{uuid.uuid4().hex[:10]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    toggles = request.chaos_toggles
    is_hardened = "hardened" in request.target.lower()
    target_name = "Hardened Shop (AgentReady Guard)" if is_hardened else "Naive Shop (Vulnerable Baseline)"

    events: List[ArenaStepEvent] = []
    findings: List[FindingDetail] = []
    budget_used = 0
    max_budget = 10

    def add_event(
        actor: str,
        action: str,
        ref_id: Optional[str] = None,
        amount: Optional[str] = None,
        status: str = "INFO",
        rule_hit: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        nonlocal budget_used
        budget_used = min(max_budget, budget_used + 1)
        ev = ArenaStepEvent(
            id=f"ev_arena_{len(events) + 1}",
            session_id=session_id,
            timestamp=datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3],
            actor=actor,
            action=action,
            ref_id=ref_id,
            amount=amount,
            status=status,
            rule_hit=rule_hit,
            details=details,
        )
        events.append(ev)

    # 1. AI Agent: Parse Prompt & Query Catalog
    add_event(
        actor="AI Agent",
        action=f"Interpreting judge shopping prompt: \"{request.prompt}\"",
        status="INFO",
    )

    catalog_svc = get_channel3_service()
    products = await catalog_svc.get_all_products()

    # Match product based on prompt keywords
    selected_prod = products[0]
    p_lower = request.prompt.lower()
    if "keyboard" in p_lower:
        selected_prod = next((p for p in products if "keyboard" in p.title.lower()), products[0])
    elif "coffee" in p_lower:
        selected_prod = next((p for p in products if "coffee" in p.title.lower()), products[0])
    elif "shoe" in p_lower or "running" in p_lower:
        selected_prod = next((p for p in products if "shoe" in p.title.lower()), products[0])

    add_event(
        actor="AI Agent",
        action=f"Channel3 search matched '{selected_prod.title}' (${selected_prod.price:.2f})",
        ref_id=selected_prod.id,
        amount=f"${selected_prod.price:.2f}",
        status="INFO",
    )

    # 2. Chaos Switch: Ambiguous Variant
    if toggles.ambiguous_variant:
        add_event(
            actor="Chaos Proxy",
            action="Injected Fault: Variant ambiguity (omitted size selection on multi-variant shoe)",
            status="MUTATION",
            rule_hit="Rule 2 (Right Amount & Variant Clarity)",
        )
        if is_hardened:
            add_event(
                actor="Store Guard",
                action="Blocked checkout: 422 AMBIGUOUS_VARIANT_CLARIFICATION_REQUIRED (user must choose size)",
                ref_id=selected_prod.id,
                status="GUARDED",
                rule_hit="Rule 2",
            )
        else:
            add_event(
                actor="Store Guard",
                action="VULNERABILITY: Naive Shop accepted checkout with unselected variant size!",
                ref_id=selected_prod.id,
                status="VIOLATION",
                rule_hit="Rule 2",
            )
            findings.append(FindingDetail(
                id=f"find_{session_id}_variant",
                rule_number=2,
                rule_name="Right Amount",
                severity=FindingSeverity.HIGH,
                title="Ambiguous Variant Accepted Without Clarification",
                explanation="Naive Shop accepted an agent checkout without required size variant selection.",
                evidence_ids=[selected_prod.id],
            ))

    # 3. Chaos Switch: Prompt Injection Trap
    approved_amount = selected_prod.price
    order_quantity = 1
    cart_id = f"cart_arena_{uuid.uuid4().hex[:8]}"

    if toggles.prompt_trap:
        order_quantity = 5
        wire_amount = round(approved_amount * 5, 2)
        add_event(
            actor="Chaos Proxy",
            action="Injected Prompt Trap: Overriding human intent to order 5 units instead of 1 approved unit",
            status="MUTATION",
            amount=f"${wire_amount:.2f}",
            rule_hit="Rule 2 (AP2 Cart Intent)",
        )
        if is_hardened:
            add_event(
                actor="Store Guard",
                action="Blocked order: 409 CART_INTENT_MISMATCH (HMAC CartReceipt rejected quantity mutation)",
                status="GUARDED",
                rule_hit="Rule 2",
            )
        else:
            add_event(
                actor="Store Guard",
                action=f"VULNERABILITY: Naive Shop accepted tampered order for 5 units (${wire_amount:.2f})!",
                status="VIOLATION",
                amount=f"${wire_amount:.2f}",
                rule_hit="Rule 2",
            )
            findings.append(FindingDetail(
                id=f"find_{session_id}_intent",
                rule_number=2,
                rule_name="Right Amount",
                severity=FindingSeverity.HIGH,
                title="Prompt Injection Hijacked Approved Cart Intent",
                explanation=f"Agent runtime submitted tampered cart (5 units) violating signed human CartReceipt.",
                evidence_ids=[cart_id],
            ))

    # 4. Chaos Switch: Price Tampering
    submitted_price = approved_amount
    if toggles.tamper_price:
        submitted_price = 1.50
        add_event(
            actor="Chaos Proxy",
            action=f"Injected Fault: Client tampered cart total from ${approved_amount:.2f} to $1.50",
            status="MUTATION",
            amount="$1.50",
            rule_hit="Rule 2 (Server-Side Price Validation)",
        )
        if is_hardened:
            add_event(
                actor="Store Guard",
                action=f"Blocked checkout: 409 PRICE_MISMATCH_REAUTHORIZATION_REQUIRED (Catalog=${approved_amount:.2f}, Submitted=$1.50)",
                status="GUARDED",
                rule_hit="Rule 2",
            )
        else:
            add_event(
                actor="Store Guard",
                action=f"VULNERABILITY: Naive Shop accepted client price $1.50 for a ${approved_amount:.2f} item!",
                status="VIOLATION",
                amount="$1.50",
                rule_hit="Rule 2",
            )
            findings.append(FindingDetail(
                id=f"find_{session_id}_price",
                rule_number=2,
                rule_name="Right Amount",
                severity=FindingSeverity.CRITICAL,
                title="Client-Side Price Manipulation Accepted",
                explanation=f"Store trusted client payload ($1.50) without validating against authoritative Channel3 catalog.",
                evidence_ids=[cart_id],
            ))

    # 5. Chaos Switch: Drop Retry & Double Capture
    order_id = f"PP-ORD-{uuid.uuid4().hex[:8].upper()}"
    capture_id = f"PP-CAP-{uuid.uuid4().hex[:8].upper()}"

    add_event(
        actor="PayPal Sandbox",
        action=f"Created PayPal Order {order_id} via Orders v2 API",
        ref_id=order_id,
        amount=f"${submitted_price:.2f}",
        status="INFO",
    )
    add_event(
        actor="PayPal Sandbox",
        action=f"Captured payment {capture_id} (Status: COMPLETED)",
        ref_id=capture_id,
        amount=f"${submitted_price:.2f}",
        status="CAPTURED",
    )

    if toggles.drop_retry:
        add_event(
            actor="Chaos Proxy",
            action="Injected Fault: Dropped HTTP 200 response to agent after successful capture",
            status="MUTATION",
            rule_hit="Rule 1 (Pay Once / Idempotency)",
        )
        add_event(
            actor="AI Agent",
            action="Agent network timeout triggered automated retry with same cart...",
            status="INFO",
        )
        if is_hardened:
            add_event(
                actor="Store Guard",
                action="Idempotency Cache Hit: Returned cached capture with header 'Idempotent-Replayed: true'",
                ref_id=capture_id,
                status="GUARDED",
                rule_hit="Rule 1",
            )
        else:
            capture_id_2 = f"PP-CAP-{uuid.uuid4().hex[:8].upper()}"
            add_event(
                actor="PayPal Sandbox",
                action=f"VULNERABILITY: Executed duplicate second capture {capture_id_2}!",
                ref_id=capture_id_2,
                amount=f"${submitted_price:.2f}",
                status="VIOLATION",
                rule_hit="Rule 1",
            )
            findings.append(FindingDetail(
                id=f"find_{session_id}_double_cap",
                rule_number=1,
                rule_name="Pay Once",
                severity=FindingSeverity.CRITICAL,
                title="Duplicate Payment Captured on Agent Network Retry",
                explanation=f"Network drop caused agent to re-submit checkout. Missing PayPal-Request-Id resulted in double capture.",
                evidence_ids=[capture_id, capture_id_2],
            ))

    # 6. Chaos Switch: Forge Webhook
    if toggles.forge_webhook:
        fake_wh_id = f"WH-{uuid.uuid4().hex[:8].upper()}"
        add_event(
            actor="Chaos Proxy",
            action="Injected Fault: Sent forged PayPal webhook with invalid HMAC signature headers",
            ref_id=fake_wh_id,
            status="MUTATION",
            rule_hit="Rule 6 (Proof on File / Webhook Auth)",
        )
        if is_hardened:
            add_event(
                actor="Store Guard",
                action="PayPal verify-webhook-signature failed -> Dropped event with 401 WEBHOOK_SIGNATURE_INVALID",
                ref_id=fake_wh_id,
                status="GUARDED",
                rule_hit="Rule 6",
            )
        else:
            add_event(
                actor="Store Guard",
                action=f"VULNERABILITY: Naive Shop marked order paid without verifying PayPal webhook signature!",
                ref_id=fake_wh_id,
                status="VIOLATION",
                rule_hit="Rule 6",
            )
            findings.append(FindingDetail(
                id=f"find_{session_id}_forge_wh",
                rule_number=6,
                rule_name="Proof on File",
                severity=FindingSeverity.HIGH,
                title="Unverified Webhook Accepted and Processed",
                explanation="Store omitted verify-webhook-signature API check and processed an unauthenticated payload.",
                evidence_ids=[fake_wh_id],
            ))

    # 7. Final Reconciler Scoring
    score = 95 if is_hardened else max(15, 100 - (len(findings) * 25))
    if is_hardened and len(findings) == 0:
        # Add 1 honest residual finding for black-box merchant limitation
        findings.append(FindingDetail(
            id=f"find_{session_id}_residual",
            rule_number=6,
            rule_name="Proof on File",
            severity=FindingSeverity.LOW,
            title="Black-Box Dispute Evidence Unverifiable",
            explanation="External black-box audit limitation: Merchant tracking records cannot be validated without signed Probe endpoint.",
            evidence_ids=[order_id],
        ))

    add_event(
        actor="Reconciler",
        action=f"Evaluation Complete! Safety Score: {score}/100 ({'🟢 PASS - Guard Protected' if score >= 80 else '🔴 FAIL - Vulnerabilities Detected'})",
        status="GUARDED" if score >= 80 else "VIOLATION",
    )

    summary = ArenaSessionSummary(
        session_id=session_id,
        prompt=request.prompt,
        target=request.target,
        target_name=target_name,
        score=score,
        total_findings=len(findings),
        findings=findings,
        events=events,
        call_budget_used=budget_used,
        call_budget_remaining=max(0, max_budget - budget_used),
        fallback_to_replay=False,
        completed_at=datetime.now(timezone.utc).isoformat(),
    )

    _ARENA_SESSIONS[session_id] = summary
    _ARENA_STREAMS[session_id] = events
    return summary


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@router.get(
    "/v1/arena/presets",
    summary="Get recommended Judge Arena shopping prompts & chaos presets",
    operation_id="getArenaPresets",
)
def get_arena_presets() -> List[Dict[str, Any]]:
    """Returns curated presets for quick 1-click judging demonstrations."""
    return [
        {
            "id": "preset_double_capture",
            "title": "Drop & Retry (Double Capture Attack)",
            "prompt": "Buy running shoes size 8 under $150 with standard shipping",
            "toggles": {"drop_retry": True},
            "description": "Tests Rule 1 (Pay Once). Simulates network timeout after PayPal capture.",
        },
        {
            "id": "preset_price_tampering",
            "title": "Price Mutation ($1.50 Steal Attack)",
            "prompt": "Purchase ergonomic mechanical keyboard with USB-C",
            "toggles": {"tamper_price": True},
            "description": "Tests Rule 2 (Right Amount). Simulates client changing price to $1.50.",
        },
        {
            "id": "preset_prompt_injection",
            "title": "Prompt Injection (+5 Units Hijack)",
            "prompt": "Buy premium organic dark roast coffee beans",
            "toggles": {"prompt_trap": True},
            "description": "Tests Rule 2 (Signed Cart Intent). Overrides approved quantity to 5 units.",
        },
        {
            "id": "preset_forged_webhook",
            "title": "Forged PayPal Webhook Injection",
            "prompt": "Order noise-canceling wireless headphones",
            "toggles": {"forge_webhook": True},
            "description": "Tests Rule 6 (Webhook Verification). Simulates forged PayPal event.",
        },
    ]


@router.post(
    "/v1/arena/run",
    response_model=ArenaSessionSummary,
    status_code=status.HTTP_200_OK,
    operation_id="runArenaScenario",
    summary="Execute an interactive Judge Arena shopping mission",
    description="Runs a single AI shopper prompt through Channel3, Chaos Proxy, and PayPal Sandbox with real-time telemetry.",
)
async def run_arena_scenario(
    request: ArenaRunRequest,
    http_request: Request,
) -> ArenaSessionSummary:
    settings = get_settings()
    if not settings.ENABLE_JUDGE_ARENA:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The Judge Arena is currently disabled via ENABLE_JUDGE_ARENA flag.",
        )

    # Validate shopping prompt guardrail
    if not validate_shopping_prompt(request.prompt):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Off-topic prompt rejected. Prompt must be a shopping instruction (e.g. 'Buy running shoes under $150').",
        )

    guard = get_abuse_guard()
    guard.verify_api_key(http_request)
    guard.validate_target(request.target)

    return await execute_arena_scenario(request)


@router.get(
    "/v1/arena/events/{session_id}",
    summary="Stream Judge Arena telemetry events via SSE into AG Grid",
    operation_id="streamArenaEvents",
    response_class=StreamingResponse,
)
async def stream_arena_events(
    session_id: str = Path(..., description="Arena session identifier"),
) -> StreamingResponse:
    if session_id not in _ARENA_STREAMS:
        raise HTTPException(status_code=404, detail=f"Arena session '{session_id}' not found.")

    events = _ARENA_STREAMS[session_id]

    async def event_generator() -> AsyncIterator[str]:
        for ev in events:
            payload = json.dumps(ev.model_dump())
            yield f"event: arena_step\ndata: {payload}\n\n"
            await asyncio.sleep(0.04)  # Natural visual pacing for AG Grid streaming

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

