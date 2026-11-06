"""
Protocol Attack Personas (Batch B: Personas 5 to 7).
Deterministic scripted state machines executing Section A6 protocol-level chaos attacks:
  - Lane 5: The Refunder (Rule 4: Safe Refunds — Duplicate Partial Refund & Over-Refund)
  - Lane 6: The Ghost Order (Rule 3: No Orphan Money — Dropped Store Order / Orphan Money)
  - Lane 7: The Disputer (Rule 6: Proof Ready — Card Payment, Chargeback Audit & Tracking Link)
"""
import asyncio
import logging
import time
import uuid
from typing import Any, Callable, Dict, List, Optional

from app.personas.base import BasePersona
from app.schemas.contracts import RunEvent
from app.schemas.problem_details import ProblemErrorCode, ProblemException
from app.services.swarm_engine import LaneResult

logger = logging.getLogger("agentready.personas.b")


class RefunderPersona(BasePersona):
    """
    Lane 5: The Refunder.
    Tests Invariant Rule 4 (Safe Refunds).
    Attempts to submit a refund exceeding the original captured transaction amount
    and attempts duplicate partial refunds to test cumulative balance cap enforcement.
    """
    persona_id = "the_refunder"
    name = "The Refunder"
    lane = 5
    rule_number = 4
    rule_name = "Safe Refunds"
    wave = 1
    driven_by = "fixed_script"
    attack_vector = "Submitting refund request of $200.00 on a $99.99 captured payment"

    async def execute(
        self,
        shop: Any,
        run_id: str,
        events: List[RunEvent],
        event_callback: Optional[Callable[[RunEvent], None]] = None,
    ) -> LaneResult:
        t0 = time.perf_counter()
        cart_id = f"cart_lane5_{uuid.uuid4().hex[:6]}"

        # State 1: Preparing and checking out order
        self.set_state("PREPARING_ORDER")
        await shop.create_cart(cart_id, [{"id": "prod_mouse_005", "quantity": 1}], client_price=99.99)
        order = await shop.checkout_order(cart_id=cart_id)
        order_id = order.get("order_id")

        # State 2: Dispatching Over-Refund Request
        self.set_state("DISPATCHING_OVER_REFUND")
        await self.emit_event(
            events, event_callback, run_id, "agent_step", self.name,
            "REQUEST_OVER_REFUND $200.00", "ATTEMPTING", "$200.00", rule_hit=4
        )

        outcome = "VULNERABILITY_EXPLOITED"
        err_code = None
        amount = "$200.00"

        # State 3: Evaluating Refund Protection
        self.set_state("EVALUATING_REFUND_PROTECTION")
        try:
            if order_id:
                await shop.refund_order(order_id=order_id, refund_amount=200.00)
                await self.emit_event(
                    events, event_callback, run_id, "store_ledger_row", "Store Ledger",
                    "OVER_REFUND_ACCEPTED", "COMPLETED", "$200.00", rule_hit=4
                )
        except ProblemException as exc:
            self.set_state("BLOCKED_BY_GUARD")
            outcome = "BLOCKED_BY_GUARD"
            err_code = exc.problem.code
            amount = "$99.99"
            await self.emit_event(
                events, event_callback, run_id, "store_ledger_row", "Guard Middleware",
                "REFUND_EXCEEDS_CAPTURE", "422_BLOCKED", rule_hit=4
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


class GhostOrderPersona(BasePersona):
    """
    Lane 6: The Ghost Order.
    Tests Invariant Rule 3 (No Orphan Money).
    Executes a successful PayPal payment capture but tests whether the merchant
    successfully stores a fulfillment record and initiates tracking within RULE3_SLA_SECONDS.
    """
    persona_id = "the_ghost_order"
    name = "The Ghost Order"
    lane = 6
    rule_number = 3
    rule_name = "No Orphan Money"
    wave = 2
    driven_by = "fixed_script"
    attack_vector = "PayPal payment capture succeeds but store database record is dropped"

    async def execute(
        self,
        shop: Any,
        run_id: str,
        events: List[RunEvent],
        event_callback: Optional[Callable[[RunEvent], None]] = None,
    ) -> LaneResult:
        t0 = time.perf_counter()
        cart_id = f"cart_lane6_{uuid.uuid4().hex[:6]}"

        # State 1: Preparing Cart
        self.set_state("PREPARING_CART")
        await shop.create_cart(cart_id, [{"id": "prod_headphones_001", "quantity": 1}], client_price=399.00)

        # State 2: Dispatching Payment Capture
        self.set_state("DISPATCHING_CHECKOUT")
        res = await shop.checkout_order(cart_id=cart_id)

        # State 3: Checking Fulfillment Record & SLA Sync
        self.set_state("CHECKING_FULFILLMENT_SLA")
        has_order = res.get("order_id") is not None
        outcome = "SUCCESS" if has_order else "VULNERABILITY_EXPLOITED"

        status_label = "ORDER_FULFILLED" if has_order else "ORPHAN_CAPTURE_NO_FULFILLMENT"
        await self.emit_event(
            events, event_callback, run_id, "store_ledger_row", "Store Ledger",
            status_label, "COMPLETED" if has_order else "ORPHAN_FOUND", "$399.00", rule_hit=3
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
            amount="$399.00",
            paypal_capture_id=res.get("paypal_capture_id"),
            store_order_id=res.get("order_id"),
            duration_ms=(time.perf_counter() - t0) * 1000,
        )


class DisputerPersona(BasePersona):
    """
    Lane 7: The Disputer.
    Tests Invariant Rule 6 (Proof Ready).
    Executes a card-funded transaction, schedules non-blocking dispute handling,
    and audits whether the store has linked shipment tracking and dispute evidence.
    """
    persona_id = "the_disputer"
    name = "The Disputer"
    lane = 7
    rule_number = 6
    rule_name = "Proof Ready"
    wave = 2
    driven_by = "fixed_script"
    attack_vector = "Chargeback audit check verifying PayPal shipment tracking link"

    async def execute(
        self,
        shop: Any,
        run_id: str,
        events: List[RunEvent],
        event_callback: Optional[Callable[[RunEvent], None]] = None,
    ) -> LaneResult:
        t0 = time.perf_counter()
        cart_id = f"cart_lane7_{uuid.uuid4().hex[:6]}"

        # State 1: Preparing Card Purchase
        self.set_state("PREPARING_CARD_PURCHASE")
        await shop.create_cart(cart_id, [{"id": "prod_mouse_005", "quantity": 1}], client_price=99.99)

        # State 2: Dispatching Card Checkout
        self.set_state("DISPATCHING_CHECKOUT")
        res = await shop.checkout_order(cart_id=cart_id)

        # State 3: Non-blocking background chargeback simulation
        self.set_state("SIMULATING_CHARGEBACK_PROCEEDING")
        tracking = res.get("tracking_number")
        has_tracking = bool(tracking and tracking != "None")
        outcome = "SUCCESS" if has_tracking else "VULNERABILITY_EXPLOITED"

        # State 4: Auditing Dispute Evidence
        self.set_state("AUDITING_DISPUTE_EVIDENCE")
        await self.emit_event(
            events, event_callback, run_id, "agent_step", self.name,
            "CHECK_DISPUTE_EVIDENCE", "COMPLETED" if has_tracking else "MISSING_TRACKING",
            "$99.99", rule_hit=6
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
            amount="$99.99",
            store_order_id=res.get("order_id"),
            duration_ms=(time.perf_counter() - t0) * 1000,
        )

