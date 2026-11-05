"""
Naive Shop (Vulnerable Baseline E-Commerce Store).
Simulates realistic e-commerce application flaws governed by the 12 Bug Flags.
Demonstrates financial race conditions, orphan money, price tampering,
and webhook forgery vulnerabilities (Section B3.2 & B3.13 of Spec).
"""
import copy
import logging
import uuid
from typing import Any, Dict, List, Optional

from app.schemas.problem_details import ProblemException
from app.services.channel3_service import get_channel3_service
from app.shops.bug_flags import BugConfig, BugFlag

logger = logging.getLogger("agentready.naive_shop")


class NaiveShop:
    """
    Reference vulnerable e-commerce store.
    By default runs with all 12 bug flags enabled (BugConfig.all_on()).
    Flags can be individually toggled for benchmark self-testing.
    """

    def __init__(self, bug_config: Optional[BugConfig] = None) -> None:
        self.bugs = bug_config or BugConfig.all_on()
        self.channel3 = get_channel3_service()

        # In-memory store database tables
        self.carts: Dict[str, Dict[str, Any]] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.payments: Dict[str, Dict[str, Any]] = {}
        self.refunds: Dict[str, List[Dict[str, Any]]] = {}
        self.webhook_history: List[Dict[str, Any]] = []
        self.processed_webhook_ids: set[str] = set()

    # -------------------------------------------------------------------------
    # 1. Cart Management
    # -------------------------------------------------------------------------
    async def create_cart(
        self,
        cart_id: str,
        items: List[Dict[str, Any]],
        client_price: Optional[float] = None,
        selected_variants: Optional[Dict[str, str]] = None,
        receipt_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Creates or updates a shopping cart.
        Vulnerabilities tested:
          - BUG_TRUST_CLIENT_PRICE (Rule 2)
          - BUG_ALLOW_AMBIGUOUS_VARIANT (Rule 2)
        """
        total_amount = 0.0

        for item in items:
            product_id = item.get("id") or item.get("product_id")
            product = await self.channel3.get_product(product_id) if product_id else None
            authoritative_price = product.price if product else 100.0

            # Price verification check (BUG_TRUST_CLIENT_PRICE)
            if self.bugs.is_enabled(BugFlag.BUG_TRUST_CLIENT_PRICE):
                # Trust client-provided price without checking server catalog
                item_price = float(item.get("price", client_price or authoritative_price))
            else:
                # Server-side authoritative price check
                item_price = authoritative_price
                if client_price is not None and abs(client_price - authoritative_price) > 0.01:
                    raise ProblemException.price_mismatch(
                        expected=f"{authoritative_price:.2f}",
                        submitted=f"{client_price:.2f}",
                        currency="USD",
                    )

            # Variant ambiguity check (BUG_ALLOW_AMBIGUOUS_VARIANT)
            if not self.bugs.is_enabled(BugFlag.BUG_ALLOW_AMBIGUOUS_VARIANT):
                if product and product.has_variants and product.requires_selection:
                    for req in product.requires_selection:
                        if not selected_variants or req not in selected_variants:
                            valid_options = product.variants.get(req, []) if product.variants else []
                            raise ProblemException.ambiguous_variant(
                                product_id=product.id,
                                valid_options=valid_options,
                                missing_attribute=req,
                            )

            total_amount += item_price * int(item.get("quantity", 1))

        cart_data = {
            "cart_id": cart_id,
            "items": copy.deepcopy(items),
            "total_amount": round(total_amount, 2),
            "currency": "USD",
            "selected_variants": selected_variants or {},
            "receipt_hash": receipt_hash or "unverified_receipt_hash",
            "status": "OPEN",
        }
        self.carts[cart_id] = cart_data
        return cart_data

    # -------------------------------------------------------------------------
    # 2. Checkout & Payment Capture
    # -------------------------------------------------------------------------
    async def checkout_order(
        self,
        cart_id: str,
        idempotency_key: Optional[str] = None,
        expected_receipt_hash: Optional[str] = None,
        mock_paypal_order_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes order checkout and records payment.
        Vulnerabilities tested:
          - BUG_NO_IDEMPOTENCY (Rule 1)
          - BUG_NO_CART_INTENT_CHECK (Rule 2)
          - BUG_NO_FULFILLMENT_RECORD (Rule 3)
          - BUG_NO_SHIPMENT_TRACKING (Rule 3)
        """
        cart = self.carts.get(cart_id)
        if not cart:
            raise ProblemException.not_found("Cart", cart_id)

        # Idempotency check (BUG_NO_IDEMPOTENCY)
        if not self.bugs.is_enabled(BugFlag.BUG_NO_IDEMPOTENCY):
            # Check if this cart was already checked out
            for existing_order in self.orders.values():
                if existing_order.get("cart_id") == cart_id:
                    logger.info("Idempotent replay returned for cart %s", cart_id)
                    return {
                        **existing_order,
                        "idempotent_replayed": True,
                    }

        # Cart intent check (BUG_NO_CART_INTENT_CHECK)
        if not self.bugs.is_enabled(BugFlag.BUG_NO_CART_INTENT_CHECK):
            if expected_receipt_hash and cart.get("receipt_hash") != expected_receipt_hash:
                raise ProblemException.cart_intent_mismatch(
                    expected_hash=expected_receipt_hash,
                    received_hash=cart.get("receipt_hash", ""),
                )

        # Generate simulated or real PayPal transaction IDs
        paypal_order_id = mock_paypal_order_id or f"PP-ORD-{uuid.uuid4().hex[:12].upper()}"
        paypal_capture_id = f"PP-CAP-{uuid.uuid4().hex[:12].upper()}"
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        # Record payment transaction in store's payment ledger
        payment_record = {
            "payment_id": f"PAY-{uuid.uuid4().hex[:8]}",
            "cart_id": cart_id,
            "order_id": order_id,
            "paypal_order_id": paypal_order_id,
            "paypal_capture_id": paypal_capture_id,
            "amount": cart["total_amount"],
            "currency": "USD",
            "status": "COMPLETED",
        }
        self.payments[paypal_capture_id] = payment_record

        # Fulfillment record check (BUG_NO_FULFILLMENT_RECORD)
        if self.bugs.is_enabled(BugFlag.BUG_NO_FULFILLMENT_RECORD):
            # Simulates server crash / dropped DB transaction after PayPal capture
            # Store gets the money on PayPal, but internal order record is MISSING (Orphan Capture)
            logger.warning("BUG_NO_FULFILLMENT_RECORD triggered: Payment captured but store order omitted!")
            return {
                "order_id": None,
                "cart_id": cart_id,
                "paypal_order_id": paypal_order_id,
                "paypal_capture_id": paypal_capture_id,
                "amount": cart["total_amount"],
                "status": "ORPHAN_CAPTURE_NO_FULFILLMENT",
            }

        # Shipment tracking check (BUG_NO_SHIPMENT_TRACKING)
        tracking_number = None
        if not self.bugs.is_enabled(BugFlag.BUG_NO_SHIPMENT_TRACKING):
            tracking_number = f"TRACK-{uuid.uuid4().hex[:12].upper()}"

        order_record = {
            "order_id": order_id,
            "cart_id": cart_id,
            "paypal_order_id": paypal_order_id,
            "paypal_capture_id": paypal_capture_id,
            "amount": cart["total_amount"],
            "currency": "USD",
            "status": "PAID",
            "tracking_number": tracking_number,
            "items": cart["items"],
        }
        self.orders[order_id] = order_record
        cart["status"] = "COMPLETED"

        return order_record

    # -------------------------------------------------------------------------
    # 3. Refunds Management
    # -------------------------------------------------------------------------
    async def refund_order(
        self,
        order_id: str,
        refund_amount: float,
        reason: str = "customer_request",
    ) -> Dict[str, Any]:
        """
        Processes a partial or full refund on an order.
        Vulnerabilities tested:
          - BUG_OVER_REFUND (Rule 4)
          - BUG_DOUBLE_REFUND (Rule 4)
        """
        order = self.orders.get(order_id)
        if not order:
            raise ProblemException.not_found("Order", order_id)

        captured_amount = float(order["amount"])
        existing_refunds = self.refunds.get(order_id, [])
        already_refunded = sum(float(r["amount"]) for r in existing_refunds)

        # Over-refund check (BUG_OVER_REFUND)
        if not self.bugs.is_enabled(BugFlag.BUG_OVER_REFUND):
            if already_refunded + refund_amount > captured_amount:
                raise ProblemException.refund_exceeds_capture(
                    captured_amount=f"{captured_amount:.2f}",
                    requested_amount=f"{refund_amount:.2f}",
                    already_refunded=f"{already_refunded:.2f}",
                )

        # Double-refund check (BUG_DOUBLE_REFUND)
        if not self.bugs.is_enabled(BugFlag.BUG_DOUBLE_REFUND):
            if any(r["reason"] == reason and abs(r["amount"] - refund_amount) < 0.01 for r in existing_refunds):
                raise ProblemException(
                    status=409,
                    title="Duplicate refund already processed",
                    code="DUPLICATE_REFUND_REJECTED",
                    detail=f"A refund of ${refund_amount:.2f} for '{reason}' has already been processed.",
                )

        refund_record = {
            "refund_id": f"REF-{uuid.uuid4().hex[:8].upper()}",
            "order_id": order_id,
            "amount": refund_amount,
            "reason": reason,
            "status": "COMPLETED",
        }

        if order_id not in self.refunds:
            self.refunds[order_id] = []
        self.refunds[order_id].append(refund_record)

        return refund_record

    # -------------------------------------------------------------------------
    # 4. Webhook Ingestion
    # -------------------------------------------------------------------------
    async def handle_webhook(
        self,
        event: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Receives webhook notification from payment gateway.
        Vulnerabilities tested:
          - BUG_NO_WEBHOOK_VERIFY (Rule 5)
          - BUG_WEBHOOK_REPLAY_VULN (Rule 5)
        """
        headers = headers or {}
        event_id = event.get("id") or "UNKNOWN_EVENT"
        event_type = event.get("event_type") or "UNKNOWN_TYPE"
        resource = event.get("resource") or {}

        # Webhook signature check (BUG_NO_WEBHOOK_VERIFY)
        if not self.bugs.is_enabled(BugFlag.BUG_NO_WEBHOOK_VERIFY):
            auth_algo = headers.get("paypal-auth-algo") or headers.get("PAYPAL-AUTH-ALGO")
            sig = headers.get("paypal-transmission-sig") or headers.get("PAYPAL-TRANSMISSION-SIG")
            if not auth_algo or not sig or sig == "forged_signature_invalid":
                raise ProblemException.webhook_signature_invalid(
                    detail="Webhook signature verification failed on merchant boundary."
                )

        # Webhook replay vulnerability check (BUG_WEBHOOK_REPLAY_VULN)
        if not self.bugs.is_enabled(BugFlag.BUG_WEBHOOK_REPLAY_VULN):
            if event_id in self.processed_webhook_ids:
                return {"status": "DUPLICATE_IGNORED", "event_id": event_id}

        self.processed_webhook_ids.add(event_id)
        self.webhook_history.append({"event_id": event_id, "type": event_type, "resource": resource})

        # Process status change
        custom_id = resource.get("custom_id")
        if custom_id:
            for order in self.orders.values():
                if order.get("cart_id") == custom_id:
                    order["status"] = "PAID"

        return {"status": "PROCESSED", "event_id": event_id}

    # -------------------------------------------------------------------------
    # 5. Dual-Ledger Internal Probe Snapshot
    # -------------------------------------------------------------------------
    def get_ledger_snapshot(self) -> Dict[str, Any]:
        """
        Returns internal store ledger state as observed through /_lab/ledger Probe endpoint.
        Exposes discrepancy against PayPal Sandbox Ground Truth.
        """
        return {
            "store_name": "Naive Shop",
            "active_bug_flags": [flag.value for flag in self.bugs.active_flags()],
            "orders": copy.deepcopy(self.orders),
            "payments": copy.deepcopy(self.payments),
            "refunds": copy.deepcopy(self.refunds),
            "total_orders": len(self.orders),
            "total_payments": len(self.payments),
        }

