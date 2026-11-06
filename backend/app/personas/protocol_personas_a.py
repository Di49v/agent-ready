"""
Protocol Attack Personas (Batch A: Personas 1 to 4).
Deterministic scripted state machines executing Section A6 protocol-level chaos attacks:
  - Lane 1: The Retrier (Rule 1: Pay Once — Network Drop & Idempotent Capture Replay)
  - Lane 2: The Tamperer (Rule 2: Right Amount — Client-Side Price Tampering)
  - Lane 3: The Stale Cart (Rule 2: Right Amount — Stale Inventory / Price Drift Race)
  - Lane 4: The Webhook Skeptic (Rule 5: Records Agree — Forged / Unsigned Webhook Injection)
"""
import asyncio
import random
import time
import uuid
from typing import Any, Callable, Dict, List, Optional

from app.personas.base import BasePersona
from app.schemas.contracts import RunEvent
from app.schemas.problem_details import ProblemException
from app.services.swarm_engine import LaneResult


class RetrierPersona(BasePersona):
    """
    Lane 1: The Retrier.
    Tests Invariant Rule 1 (Pay Once).
    Simulates a network timeout/drop immediately after capture submission and
    issues a rapid duplicate capture with the same idempotency key.
    """
    persona_id = "the_retrier"
    name = "The Retrier"
    lane = 1
    rule_number = 1
    rule_name = "Pay Once"
    wave = 1
    driven_by = "fixed_script"
    attack_vector = "Rapid duplicate capture request without idempotency handling"

    async def execute(
        self,
        shop: Any,
        run_id: str,
        events: List[RunEvent],
        event_callback: Optional[Callable[[RunEvent], None]] = None,
    ) -> LaneResult:
        t0 = time.perf_counter()
        cart_id = f"cart_lane1_{uuid.uuid4().hex[:6]}"
        idemp_key = f"idemp_{cart_id}"

        # State 1: Preparing Cart
        self.set_state("PREPARING_CART")
        await self.emit_event(
            events, event_callback, run_id, "agent_step", self.name,
            "CREATE_CART", "STARTED", "$399.00", rule_hit=1
        )
        await shop.create_cart(cart_id, [{"id": "prod_headphones_001", "quantity": 1}], client_price=399.00)

        # State 2: Dispatching Initial Capture
        self.set_state("DISPATCHING_INITIAL_CAPTURE")
        await self.emit_event(
            events, event_callback, run_id, "agent_step", self.name,
            "POST /v2/checkout/orders", "CAPTURING", "$399.00", rule_hit=1
        )
        res1 = await shop.checkout_order(cart_id=cart_id, idempotency_key=idemp_key)

        # State 3: Simulating Network Drop / Client Jitter
        self.set_state("SIMULATING_NETWORK_DROP")
        await asyncio.sleep(random.uniform(0.02, 0.05))

        # State 4: Dispatching Rapid Retry with same key
        self.set_state("DISPATCHING_RETRY_CAPTURE")
        await self.emit_event(
            events, event_callback, run_id, "agent_step", self.name,
            "RETRY_POST /v2/checkout/orders", "RETRYING", "$399.00", rule_hit=1
        )
        res2 = await shop.checkout_order(cart_id=cart_id, idempotency_key=idemp_key)

        # State 5: Evaluating Idempotency
        self.set_state("EVALUATING_IDEMPOTENCY")
        is_replayed = res2.get("idempotent_replayed", False)
        outcome = "BLOCKED_BY_GUARD" if is_replayed else "VULNERABILITY_EXPLOITED"
        status_label = "IDEMPOTENT_CACHE_HIT" if is_replayed else "DOUBLE_CHARGE_DETECTED"
        amount = "$399.00" if is_replayed else "$798.00"

        await self.emit_event(
            events, event_callback, run_id, "paypal_event", "PayPal Sandbox",
            "CAPTURE_RESULT", status_label, amount,
            paypal_id=res1.get("paypal_capture_id"), rule_hit=1
        )

        self.set_state("COMPLETED")
        return LaneResult(
            lane=self.lane,
            persona_id=self.persona_id,
            persona_name=self.name,
            rule_number=self.rule_number,
            cart_id=cart_id,
            attack_vector=self.attack_vector,
            outcome=outcome,
            amount=amount,
            paypal_order_id=res1.get("paypal_order_id"),
            paypal_capture_id=res1.get("paypal_capture_id"),
            store_order_id=res1.get("order_id"),
            duration_ms=(time.perf_counter() - t0) * 1000,
        )


class TampererPersona(BasePersona):
    """
    Lane 2: The Tamperer.
    Tests Invariant Rule 2 (Right Amount).
    Alters client-submitted price on a $149.95 item down to $1.50 to test whether
    the merchant calculates totals from server authority.
    """
    persona_id = "the_tamperer"
    name = "The Tamperer"
    lane = 2
    rule_number = 2
    rule_name = "Right Amount"
    wave = 1
    driven_by = "fixed_script"
    attack_vector = "Client-submitted item price modification ($1.50 vs $149.95)"

    async def execute(
        self,
        shop: Any,
        run_id: str,
        events: List[RunEvent],
        event_callback: Optional[Callable[[RunEvent], None]] = None,
    ) -> LaneResult:
        t0 = time.perf_counter()
        cart_id = f"cart_lane2_{uuid.uuid4().hex[:6]}"

        # State 1: Preparing Tampered Cart
        self.set_state("PREPARING_TAMPERED_CART")
        await self.emit_event(
            events, event_callback, run_id, "agent_step", self.name,
            "TAMPER_PRICE $1.50", "ATTEMPTING", "$1.50", rule_hit=2
        )

        outcome = "VULNERABILITY_EXPLOITED"
        err_code = None
        amount = "$1.50"

        # State 2: Dispatching Capture with Tampered Price
        self.set_state("DISPATCHING_CAPTURE")
        try:
            await shop.create_cart(
                cart_id=cart_id,
                items=[{"id": "prod_smart_mug_003", "quantity": 1}],
                client_price=1.50,  # Authoritative catalog price is $149.95
            )
            await shop.checkout_order(cart_id=cart_id)
            await self.emit_event(
                events, event_callback, run_id, "paypal_event", "PayPal Sandbox",
                "UNDER_COLLECTED_CAPTURE", "ACCEPTED", "$1.50", rule_hit=2
            )
        except ProblemException as exc:
            self.set_state("BLOCKED_BY_GUARD")
            outcome = "BLOCKED_BY_GUARD"
            err_code = exc.problem.code
            amount = "$149.95"
            await self.emit_event(
                events, event_callback, run_id, "store_ledger_row", "Guard Middleware",
                "REAUTHORIZATION_REQUIRED", "409_BLOCKED", "$1.50", rule_hit=2
            )

        self.set_state("COMPLETED")
        return LaneResult(
            lane=self.lane,
            persona_id=self.persona_id,
            persona_name=self.name,
            rule_number=self.rule_number,
            cart_id=cart_id,
            attack_vector=self.attack_vector,
            outcome=outcome,
            amount=amount,
            error_code=err_code,
            duration_ms=(time.perf_counter() - t0) * 1000,
        )


class StaleCartPersona(BasePersona):
    """
    Lane 3: The Stale Cart.
    Tests Invariant Rule 2 (Right Amount).
    Simulates a checkout attempt where the cart was prepared at an older price ($150.00)
    while the authoritative catalog price has increased to $199.00.
    """
    persona_id = "the_stale_cart"
    name = "The Stale Cart"
    lane = 3
    rule_number = 2
    rule_name = "Right Amount"
    wave = 1
    driven_by = "fixed_script"
    attack_vector = "Checkout with stale pricing after catalog price increase"

    async def execute(
        self,
        shop: Any,
        run_id: str,
        events: List[RunEvent],
        event_callback: Optional[Callable[[RunEvent], None]] = None,
    ) -> LaneResult:
        t0 = time.perf_counter()
        cart_id = f"cart_lane3_{uuid.uuid4().hex[:6]}"

        # State 1: Preparing Stale Cart
        self.set_state("PREPARING_STALE_CART")
        await self.emit_event(
            events, event_callback, run_id, "agent_step", self.name,
            "CREATE_STALE_CART", "STARTED", "$199.00", rule_hit=2
        )

        outcome = "VULNERABILITY_EXPLOITED"
        err_code = None

        # State 2: Dispatching Capture with Stale Price
        self.set_state("DISPATCHING_CAPTURE")
        try:
            # Cart created at stale price $150.00 while catalog is $199.00
            await shop.create_cart(
                cart_id=cart_id,
                items=[{"id": "prod_keyboard_004", "quantity": 1}],
                client_price=150.00,
                selected_variants={"switch_type": "Red (Linear)", "color": "Carbon Black"},
            )
            await shop.checkout_order(cart_id=cart_id)
        except ProblemException as exc:
            self.set_state("BLOCKED_BY_GUARD")
            outcome = "BLOCKED_BY_GUARD"
            err_code = exc.problem.code

        amount = "$199.00" if outcome == "BLOCKED_BY_GUARD" else "$150.00"

        self.set_state("COMPLETED")
        return LaneResult(
            lane=self.lane,
            persona_id=self.persona_id,
            persona_name=self.name,
            rule_number=self.rule_number,
            cart_id=cart_id,
            attack_vector=self.attack_vector,
            outcome=outcome,
            amount=amount,
            error_code=err_code,
            duration_ms=(time.perf_counter() - t0) * 1000,
        )


class WebhookSkepticPersona(BasePersona):
    """
    Lane 4: The Webhook Skeptic.
    Tests Invariant Rule 5 (Records Agree).
    Directly injects forged and unverified PAYMENT.CAPTURE.COMPLETED notifications
    to test whether the store verifies PayPal transmission signatures before marking paid.
    """
    persona_id = "the_webhook_skeptic"
    name = "The Webhook Skeptic"
    lane = 4
    rule_number = 5
    rule_name = "Records Agree"
    wave = 1
    driven_by = "fixed_script"
    attack_vector = "Injection of forged PAYMENT.CAPTURE.COMPLETED webhook without signature"

    async def execute(
        self,
        shop: Any,
        run_id: str,
        events: List[RunEvent],
        event_callback: Optional[Callable[[RunEvent], None]] = None,
    ) -> LaneResult:
        t0 = time.perf_counter()
        cart_id = f"cart_lane4_{uuid.uuid4().hex[:6]}"
        wh_event_id = f"WH-FORGE-{uuid.uuid4().hex[:6]}"

        # State 1: Forging Webhook Payload
        self.set_state("FORGING_WEBHOOK")
        await self.emit_event(
            events, event_callback, run_id, "agent_step", self.name,
            "FORGE_WEBHOOK", "INJECTING", "$85.00", rule_hit=5
        )

        outcome = "VULNERABILITY_EXPLOITED"
        err_code = None

        # State 2: Dispatching Forged Webhook with Invalid Signature
        self.set_state("DISPATCHING_FORGED_WEBHOOK")
        try:
            await shop.handle_webhook(
                event={"id": wh_event_id, "event_type": "PAYMENT.CAPTURE.COMPLETED"},
                headers={"PAYPAL-TRANSMISSION-SIG": "forged_signature_invalid"},
            )
            await self.emit_event(
                events, event_callback, run_id, "store_ledger_row", "Store Ledger",
                "MARKED_PAID_WITHOUT_VERIFY", "COMPLETED", rule_hit=5
            )
        except ProblemException as exc:
            self.set_state("BLOCKED_BY_GUARD")
            outcome = "BLOCKED_BY_GUARD"
            err_code = exc.problem.code
            await self.emit_event(
                events, event_callback, run_id, "store_ledger_row", "Guard Middleware",
                "UNVERIFIED_WEBHOOK_REJECTED", "401_BLOCKED", rule_hit=5
            )

        self.set_state("COMPLETED")
        return LaneResult(
            lane=self.lane,
            persona_id=self.persona_id,
            persona_name=self.name,
            rule_number=self.rule_number,
            cart_id=cart_id,
            attack_vector=self.attack_vector,
            outcome=outcome,
            amount="$85.00",
            error_code=err_code,
            duration_ms=(time.perf_counter() - t0) * 1000,
        )

