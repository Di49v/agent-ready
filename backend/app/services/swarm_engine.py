"""
Live 9-Persona Adversarial Swarm Engine.
Executes the Section B3.3 chaos-engineering persona lanes in two batched waves
(MAX_CONCURRENT_BUYERS = 5) with network jitter, emitting real-time RunEvent frames.
"""
import asyncio
import logging
import random
import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.schemas.contracts import RunEvent
from app.schemas.problem_details import ProblemException
from app.services.cart_signer import get_cart_signer
from app.shops.hardened_shop import HardenedShop
from app.shops.naive_shop import NaiveShop

logger = logging.getLogger("agentready.swarm")


class LaneResult(BaseModel):
    """Result of an individual persona lane attack attempt."""
    lane: int
    persona_id: str
    persona_name: str
    rule_number: int
    cart_id: str
    attack_vector: str
    outcome: str  # "VULNERABILITY_EXPLOITED", "BLOCKED_BY_GUARD", "SUCCESS"
    amount: Optional[str] = None
    paypal_order_id: Optional[str] = None
    paypal_capture_id: Optional[str] = None
    store_order_id: Optional[str] = None
    error_code: Optional[str] = None
    duration_ms: float = 0.0


class SwarmExecutionResult(BaseModel):
    """Comprehensive result of all 9 persona swarm lanes."""
    run_id: str
    target_id: str
    total_lanes: int = 9
    duration_sec: float
    lane_results: Dict[int, LaneResult]
    events: List[RunEvent]


class SwarmEngine:
    """
    Orchestrates the 9 adversarial persona lanes against a target store.
    Runs in 2 waves using asyncio.Semaphore(5) to respect PayPal Sandbox rate limits.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.semaphore = asyncio.Semaphore(self.settings.MAX_CONCURRENT_BUYERS)
        self.signer = get_cart_signer()

    def _now(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    async def _emit_event(
        self,
        event_list: List[RunEvent],
        event_callback: Optional[Callable[[RunEvent], None]],
        run_id: str,
        lane: Optional[int],
        persona_id: str,
        event_type: str,
        actor: str,
        action: str,
        status: str,
        amount: Optional[str] = None,
        paypal_id: Optional[str] = None,
        rule_hit: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> RunEvent:
        """Helper to create and broadcast a telemetry event."""
        event_obj = RunEvent(
            event=event_type,  # type: ignore
            run_id=run_id,
            timestamp=self._now(),
            lane=lane,
            persona_id=persona_id,
            actor=actor,
            action=action,
            status=status,
            amount=amount,
            paypal_id=paypal_id,
            rule_hit=rule_hit,
            data=data or {},
        )
        event_list.append(event_obj)
        if event_callback:
            try:
                event_callback(event_obj)
            except Exception as e:
                logger.warning("Event callback failed: %s", e)
        return event_obj

    # -------------------------------------------------------------------------
    # Individual Persona Attack Runners
    # -------------------------------------------------------------------------
    async def _run_lane_1_retrier(self, shop: Any, run_id: str, events: List[RunEvent], cb: Any) -> LaneResult:
        """Lane 1: The Retrier (Rule 1: Pay Once — Idempotency Attack)"""
        t0 = time.perf_counter()
        cart_id = f"cart_lane1_{uuid.uuid4().hex[:6]}"
        pid = "the_retrier"

        await self._emit_event(events, cb, run_id, 1, pid, "agent_step", "The Retrier", "CREATE_CART", "STARTED", "$399.00", rule_hit=1)
        await shop.create_cart(cart_id, [{"id": "prod_headphones_001", "quantity": 1}], client_price=399.00)

        # Trigger rapid retry with same idempotency key
        key = f"idemp_{cart_id}"
        await self._emit_event(events, cb, run_id, 1, pid, "agent_step", "The Retrier", "POST /v2/checkout/orders", "CAPTURING", "$399.00", rule_hit=1)

        res1 = await shop.checkout_order(cart_id=cart_id, idempotency_key=key)

        # Injected jitter simulating network retry
        await asyncio.sleep(random.uniform(0.02, 0.05))

        res2 = await shop.checkout_order(cart_id=cart_id, idempotency_key=key)

        is_replayed = res2.get("idempotent_replayed", False)
        outcome = "BLOCKED_BY_GUARD" if is_replayed else "VULNERABILITY_EXPLOITED"
        status_label = "IDEMPOTENT_CACHE_HIT" if is_replayed else "DOUBLE_CHARGE_DETECTED"

        await self._emit_event(
            events, cb, run_id, 1, pid, "paypal_event", "PayPal Sandbox",
            "CAPTURE_RESULT", status_label, "$399.00" if is_replayed else "$798.00",
            paypal_id=res1.get("paypal_capture_id"), rule_hit=1
        )

        return LaneResult(
            lane=1,
            persona_id=pid,
            persona_name="The Retrier",
            rule_number=1,
            cart_id=cart_id,
            attack_vector="Rapid duplicate capture request without idempotency handling",
            outcome=outcome,
            amount="$399.00" if is_replayed else "$798.00",
            paypal_order_id=res1.get("paypal_order_id"),
            paypal_capture_id=res1.get("paypal_capture_id"),
            store_order_id=res1.get("order_id"),
            duration_ms=(time.perf_counter() - t0) * 1000,
        )

    async def _run_lane_2_tamperer(self, shop: Any, run_id: str, events: List[RunEvent], cb: Any) -> LaneResult:
        """Lane 2: The Tamperer (Rule 2: Right Amount — Price Tampering Attack)"""
        t0 = time.perf_counter()
        cart_id = f"cart_lane2_{uuid.uuid4().hex[:6]}"
        pid = "the_tamperer"

        await self._emit_event(events, cb, run_id, 2, pid, "agent_step", "The Tamperer", "TAMPER_PRICE $1.50", "ATTEMPTING", "$1.50", rule_hit=2)

        outcome = "VULNERABILITY_EXPLOITED"
        err_code = None
        amount = "$1.50"

        try:
            cart = await shop.create_cart(
                cart_id=cart_id,
                items=[{"id": "prod_smart_mug_003", "quantity": 1}],
                client_price=1.50,  # Authoritative catalog price is $149.95
            )
            res = await shop.checkout_order(cart_id=cart_id)
            await self._emit_event(events, cb, run_id, 2, pid, "paypal_event", "PayPal Sandbox", "UNDER_COLLECTED_CAPTURE", "ACCEPTED", "$1.50", rule_hit=2)
        except ProblemException as exc:
            outcome = "BLOCKED_BY_GUARD"
            err_code = exc.problem.code
            amount = "$149.95"
            await self._emit_event(events, cb, run_id, 2, pid, "store_ledger_row", "Guard Middleware", "REAUTHORIZATION_REQUIRED", "409_BLOCKED", "$1.50", rule_hit=2)

        return LaneResult(
            lane=2,
            persona_id=pid,
            persona_name="The Tamperer",
            rule_number=2,
            cart_id=cart_id,
            attack_vector="Client-submitted item price modification ($1.50 vs $149.95)",
            outcome=outcome,
            amount=amount,
            error_code=err_code,
            duration_ms=(time.perf_counter() - t0) * 1000,
        )

    async def _run_lane_3_stale_cart(self, shop: Any, run_id: str, events: List[RunEvent], cb: Any) -> LaneResult:
        """Lane 3: The Stale Cart (Rule 2: Right Amount — Stale Inventory / Price Race)"""
        t0 = time.perf_counter()
        cart_id = f"cart_lane3_{uuid.uuid4().hex[:6]}"
        pid = "the_stale_cart"

        await self._emit_event(events, cb, run_id, 3, pid, "agent_step", "The Stale Cart", "CREATE_STALE_CART", "STARTED", "$199.00", rule_hit=2)
        outcome = "VULNERABILITY_EXPLOITED"
        err_code = None

        try:
            # Cart created at stale price $150.00 while catalog is $199.00
            await shop.create_cart(
                cart_id,
                [{"id": "prod_keyboard_004", "quantity": 1}],
                client_price=150.00,
                selected_variants={"switch_type": "Red (Linear)", "color": "Carbon Black"},
            )
            await shop.checkout_order(cart_id=cart_id)
        except ProblemException as exc:
            outcome = "BLOCKED_BY_GUARD"
            err_code = exc.problem.code

        return LaneResult(
            lane=3,
            persona_id=pid,
            persona_name="The Stale Cart",
            rule_number=2,
            cart_id=cart_id,
            attack_vector="Checkout with stale pricing after catalog price increase",
            outcome=outcome,
            amount="$199.00" if outcome == "BLOCKED_BY_GUARD" else "$150.00",
            error_code=err_code,
            duration_ms=(time.perf_counter() - t0) * 1000,
        )

    async def _run_lane_4_webhook_skeptic(self, shop: Any, run_id: str, events: List[RunEvent], cb: Any) -> LaneResult:
        """Lane 4: The Webhook Skeptic (Rule 5: Records Agree — Forged Webhook Attack)"""
        t0 = time.perf_counter()
        cart_id = f"cart_lane4_{uuid.uuid4().hex[:6]}"
        pid = "the_webhook_skeptic"

        await self._emit_event(events, cb, run_id, 4, pid, "agent_step", "The Webhook Skeptic", "FORGE_WEBHOOK", "INJECTING", "$85.00", rule_hit=5)
        outcome = "VULNERABILITY_EXPLOITED"
        err_code = None

        try:
            await shop.handle_webhook(
                event={"id": f"WH-FORGE-{uuid.uuid4().hex[:6]}", "event_type": "PAYMENT.CAPTURE.COMPLETED"},
                headers={"PAYPAL-TRANSMISSION-SIG": "forged_signature_invalid"},
            )
            await self._emit_event(events, cb, run_id, 4, pid, "store_ledger_row", "Store Ledger", "MARKED_PAID_WITHOUT_VERIFY", "COMPLETED", rule_hit=5)
        except ProblemException as exc:
            outcome = "BLOCKED_BY_GUARD"
            err_code = exc.problem.code
            await self._emit_event(events, cb, run_id, 4, pid, "store_ledger_row", "Guard Middleware", "UNVERIFIED_WEBHOOK_REJECTED", "401_BLOCKED", rule_hit=5)

        return LaneResult(
            lane=4,
            persona_id=pid,
            persona_name="The Webhook Skeptic",
            rule_number=5,
            cart_id=cart_id,
            attack_vector="Injection of forged PAYMENT.CAPTURE.COMPLETED webhook without signature",
            outcome=outcome,
            error_code=err_code,
            duration_ms=(time.perf_counter() - t0) * 1000,
        )

    async def _run_lane_5_refunder(self, shop: Any, run_id: str, events: List[RunEvent], cb: Any) -> LaneResult:
        """Lane 5: The Refunder (Rule 4: Safe Refunds — Over-Refund Attack)"""
        t0 = time.perf_counter()
        cart_id = f"cart_lane5_{uuid.uuid4().hex[:6]}"
        pid = "the_refunder"

        await shop.create_cart(cart_id, [{"id": "prod_mouse_005", "quantity": 1}], client_price=99.99)
        order = await shop.checkout_order(cart_id=cart_id)
        order_id = order.get("order_id")

        await self._emit_event(events, cb, run_id, 5, pid, "agent_step", "The Refunder", "REQUEST_OVER_REFUND $200.00", "ATTEMPTING", "$200.00", rule_hit=4)

        outcome = "VULNERABILITY_EXPLOITED"
        err_code = None

        try:
            if order_id:
                await shop.refund_order(order_id=order_id, refund_amount=200.00)
                await self._emit_event(events, cb, run_id, 5, pid, "store_ledger_row", "Store Ledger", "OVER_REFUND_ACCEPTED", "COMPLETED", "$200.00", rule_hit=4)
        except ProblemException as exc:
            outcome = "BLOCKED_BY_GUARD"
            err_code = exc.problem.code
            await self._emit_event(events, cb, run_id, 5, pid, "store_ledger_row", "Guard Middleware", "REFUND_EXCEEDS_CAPTURE", "422_BLOCKED", rule_hit=4)

        return LaneResult(
            lane=5,
            persona_id=pid,
            persona_name="The Refunder",
            rule_number=4,
            cart_id=cart_id,
            attack_vector="Submitting refund request of $200.00 on a $99.99 captured payment",
            outcome=outcome,
            error_code=err_code,
            duration_ms=(time.perf_counter() - t0) * 1000,
        )

    async def _run_lane_6_ghost_order(self, shop: Any, run_id: str, events: List[RunEvent], cb: Any) -> LaneResult:
        """Lane 6: The Ghost Order (Rule 3: No Orphan Money — Dropped Store Order)"""
        t0 = time.perf_counter()
        cart_id = f"cart_lane6_{uuid.uuid4().hex[:6]}"
        pid = "the_ghost_order"

        await shop.create_cart(cart_id, [{"id": "prod_headphones_001", "quantity": 1}], client_price=399.00)
        res = await shop.checkout_order(cart_id=cart_id)

        has_order = res.get("order_id") is not None
        outcome = "SUCCESS" if has_order else "VULNERABILITY_EXPLOITED"

        status_label = "ORDER_FULFILLED" if has_order else "ORPHAN_CAPTURE_NO_FULFILLMENT"
        await self._emit_event(events, cb, run_id, 6, pid, "store_ledger_row", "Store Ledger", status_label, "COMPLETED" if has_order else "ORPHAN_FOUND", "$399.00", rule_hit=3)

        return LaneResult(
            lane=6,
            persona_id=pid,
            persona_name="The Ghost Order",
            rule_number=3,
            cart_id=cart_id,
            attack_vector="PayPal payment capture succeeds but store database record is dropped",
            outcome=outcome,
            amount="$399.00",
            paypal_capture_id=res.get("paypal_capture_id"),
            store_order_id=res.get("order_id"),
            duration_ms=(time.perf_counter() - t0) * 1000,
        )

    async def _run_lane_7_disputer(self, shop: Any, run_id: str, events: List[RunEvent], cb: Any) -> LaneResult:
        """Lane 7: The Disputer (Rule 6: Proof Ready — Tracking Number Verification)"""
        t0 = time.perf_counter()
        cart_id = f"cart_lane7_{uuid.uuid4().hex[:6]}"
        pid = "the_disputer"

        await shop.create_cart(cart_id, [{"id": "prod_mouse_005", "quantity": 1}], client_price=99.99)
        res = await shop.checkout_order(cart_id=cart_id)

        tracking = res.get("tracking_number")
        has_tracking = bool(tracking and tracking != "None")
        outcome = "SUCCESS" if has_tracking else "VULNERABILITY_EXPLOITED"

        await self._emit_event(events, cb, run_id, 7, pid, "agent_step", "The Disputer", "CHECK_DISPUTE_EVIDENCE", "COMPLETED" if has_tracking else "MISSING_TRACKING", "$99.99", rule_hit=6)

        return LaneResult(
            lane=7,
            persona_id=pid,
            persona_name="The Disputer",
            rule_number=6,
            cart_id=cart_id,
            attack_vector="Chargeback audit check verifying PayPal shipment tracking link",
            outcome=outcome,
            amount="$99.99",
            store_order_id=res.get("order_id"),
            duration_ms=(time.perf_counter() - t0) * 1000,
        )

    async def _run_lane_8_misreader(self, shop: Any, run_id: str, events: List[RunEvent], cb: Any) -> LaneResult:
        """Lane 8: The Misreader (Rule 2: Right Amount — Ambiguous Variant Attack)"""
        t0 = time.perf_counter()
        cart_id = f"cart_lane8_{uuid.uuid4().hex[:6]}"
        pid = "the_misreader"

        await self._emit_event(events, cb, run_id, 8, pid, "agent_step", "The Misreader", "BUY_WITHOUT_SIZE", "ATTEMPTING", "$130.00", rule_hit=2)
        outcome = "VULNERABILITY_EXPLOITED"
        err_code = None

        try:
            # prod_running_shoes_002 has multi-size/color variants; passing None
            await shop.create_cart(cart_id, [{"id": "prod_running_shoes_002", "quantity": 1}], selected_variants=None)
            await shop.checkout_order(cart_id=cart_id)
        except ProblemException as exc:
            outcome = "BLOCKED_BY_GUARD"
            err_code = exc.problem.code
            await self._emit_event(events, cb, run_id, 8, pid, "store_ledger_row", "Guard Middleware", "AMBIGUOUS_VARIANT_CLARIFICATION_REQUIRED", "422_BLOCKED", rule_hit=2)

        return LaneResult(
            lane=8,
            persona_id=pid,
            persona_name="The Misreader",
            rule_number=2,
            cart_id=cart_id,
            attack_vector="Purchasing multi-variant shoes without specifying required size/color",
            outcome=outcome,
            error_code=err_code,
            duration_ms=(time.perf_counter() - t0) * 1000,
        )

    async def _run_lane_9_content_trap(self, shop: Any, run_id: str, events: List[RunEvent], cb: Any) -> LaneResult:
        """Lane 9: The Content Trap (Rule 2: Right Amount — Prompt Injection Defense)"""
        t0 = time.perf_counter()
        cart_id = f"cart_lane9_{uuid.uuid4().hex[:6]}"
        pid = "the_content_trap"

        # Human signed receipt: 1 unit max $150.00
        receipt = self.signer.sign_receipt(
            cart_id=cart_id,
            sku="prod_smart_mug_003",
            quantity=1,
            max_amount=150.00,
        )

        await self._emit_event(events, cb, run_id, 9, pid, "agent_step", "The Content Trap", "PROMPT_INJECTION_ALTER_QTY 5", "ATTEMPTING", "$749.75", rule_hit=2)
        outcome = "VULNERABILITY_EXPLOITED"
        err_code = None

        try:
            # Agent falls for injection in description and alters quantity from 1 to 5
            await shop.create_cart(
                cart_id=cart_id,
                items=[{"id": "prod_smart_mug_003", "quantity": 5}],
                receipt_hash="tampered_hash_after_injection",
            )
            await shop.checkout_order(
                cart_id=cart_id,
                expected_receipt_hash=receipt.signature,
            )
        except ProblemException as exc:
            outcome = "BLOCKED_BY_GUARD"
            err_code = exc.problem.code
            await self._emit_event(events, cb, run_id, 9, pid, "store_ledger_row", "Guard Middleware", "CART_INTENT_MISMATCH", "409_BLOCKED", rule_hit=2)

        return LaneResult(
            lane=9,
            persona_id=pid,
            persona_name="The Content Trap",
            rule_number=2,
            cart_id=cart_id,
            attack_vector="Prompt injection in product description tricks agent into buying 5 units",
            outcome=outcome,
            error_code=err_code,
            duration_ms=(time.perf_counter() - t0) * 1000,
        )

    # -------------------------------------------------------------------------
    # Two-Wave Batch Orchestrator
    # -------------------------------------------------------------------------
    async def execute_swarm(
        self,
        target_id: str,
        run_id: Optional[str] = None,
        event_callback: Optional[Callable[[RunEvent], None]] = None,
    ) -> SwarmExecutionResult:
        """
        Executes all 9 persona lanes against the target store.
        Splits into 2 waves using asyncio.Semaphore(5) with network jitter.
        """
        run_id = run_id or f"run_{uuid.uuid4().hex[:12]}"
        t_start = time.perf_counter()
        events: List[RunEvent] = []

        # Instantiate live shop target
        shop = HardenedShop() if "hardened" in target_id.lower() else NaiveShop()

        lane_results: Dict[int, LaneResult] = {}

        async def run_with_throttle(coro: Any) -> LaneResult:
            async with self.semaphore:
                # Add network jitter
                await asyncio.sleep(random.uniform(0.02, 0.08))
                return await coro

        # ---------------------------------------------------------------------
        # Wave 1: Lanes 1 to 5 (Max 5 concurrent buyers)
        # ---------------------------------------------------------------------
        logger.info("Executing Swarm Wave 1 (Lanes 1-5) for run %s...", run_id)
        wave_1_tasks = [
            run_with_throttle(self._run_lane_1_retrier(shop, run_id, events, event_callback)),
            run_with_throttle(self._run_lane_2_tamperer(shop, run_id, events, event_callback)),
            run_with_throttle(self._run_lane_3_stale_cart(shop, run_id, events, event_callback)),
            run_with_throttle(self._run_lane_4_webhook_skeptic(shop, run_id, events, event_callback)),
            run_with_throttle(self._run_lane_5_refunder(shop, run_id, events, event_callback)),
        ]
        w1_results = await asyncio.gather(*wave_1_tasks)
        for res in w1_results:
            lane_results[res.lane] = res

        # ---------------------------------------------------------------------
        # Wave 2: Lanes 6 to 9 (Remaining 4 buyers)
        # ---------------------------------------------------------------------
        logger.info("Executing Swarm Wave 2 (Lanes 6-9) for run %s...", run_id)
        wave_2_tasks = [
            run_with_throttle(self._run_lane_6_ghost_order(shop, run_id, events, event_callback)),
            run_with_throttle(self._run_lane_7_disputer(shop, run_id, events, event_callback)),
            run_with_throttle(self._run_lane_8_misreader(shop, run_id, events, event_callback)),
            run_with_throttle(self._run_lane_9_content_trap(shop, run_id, events, event_callback)),
        ]
        w2_results = await asyncio.gather(*wave_2_tasks)
        for res in w2_results:
            lane_results[res.lane] = res

        total_duration = time.perf_counter() - t_start

        # Broadcast completion event
        await self._emit_event(
            events, event_callback, run_id, None, "orchestrator", "run_completed",
            "Swarm Orchestrator", "SWARM_BATCH_COMPLETE", "COMPLETED",
            data={"total_lanes": 9, "duration_sec": total_duration}
        )

        return SwarmExecutionResult(
            run_id=run_id,
            target_id=target_id,
            total_lanes=9,
            duration_sec=total_duration,
            lane_results=lane_results,
            events=events,
        )


_swarm_engine: Optional[SwarmEngine] = None


def get_swarm_engine() -> SwarmEngine:
    """Returns singleton instance of SwarmEngine."""
    global _swarm_engine
    if _swarm_engine is None:
        _swarm_engine = SwarmEngine()
    return _swarm_engine

