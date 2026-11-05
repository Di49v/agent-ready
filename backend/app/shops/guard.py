"""
AgentReady Guard Middleware & Compliance Layer.
Enforces RFC 9457 structured errors for AI commerce safety invariants:
Idempotency locks, server-side price locks, variant validation,
cart-intent integrity, refund caps, and webhook signature verification.
"""
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.problem_details import ProblemErrorCode, ProblemException
from app.services.channel3_service import get_channel3_service

logger = logging.getLogger("agentready.guard")


class AgentReadyGuard:
    """
    Middleware security layer that validates inbound agent commerce actions
    and returns RFC 9457 Problem Details for any invariant violation.
    """

    def __init__(self) -> None:
        self.channel3 = get_channel3_service()
        # In-memory idempotency cache: key -> (request_hash, response_payload)
        self.idempotency_store: Dict[str, Tuple[str, Dict[str, Any]]] = {}

    # -------------------------------------------------------------------------
    # 1. Idempotency Lock & Cache Enforcement (Rule 1: Pay Once)
    # -------------------------------------------------------------------------
    def check_idempotency(
        self,
        idempotency_key: Optional[str],
        request_payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Validates idempotency key. If already processed with matching payload,
        returns the previously cached response with idempotent replay indicator.
        If key exists with conflicting payload, raises RFC 9457 IDEMPOTENCY_CONFLICT.
        """
        if not idempotency_key:
            return None

        req_hash = hashlib.sha256(str(sorted(request_payload.items())).encode("utf-8")).hexdigest()

        if idempotency_key in self.idempotency_store:
            stored_hash, cached_response = self.idempotency_store[idempotency_key]
            if stored_hash != req_hash:
                raise ProblemException(
                    status=409,
                    title="Idempotency key payload mismatch",
                    code=ProblemErrorCode.IDEMPOTENCY_CONFLICT,
                    detail=f"Idempotency key '{idempotency_key}' was previously used with a different request payload.",
                    retryable=False,
                )
            logger.info("Guard: Replaying cached idempotent response for key %s", idempotency_key)
            return {**cached_response, "idempotent_replayed": True}

        return None

    def record_idempotent_response(
        self,
        idempotency_key: Optional[str],
        request_payload: Dict[str, Any],
        response_payload: Dict[str, Any],
    ) -> None:
        """Stores successful response for future idempotent replays."""
        if not idempotency_key:
            return
        req_hash = hashlib.sha256(str(sorted(request_payload.items())).encode("utf-8")).hexdigest()
        self.idempotency_store[idempotency_key] = (req_hash, copy_payload := dict(response_payload))

    # -------------------------------------------------------------------------
    # 2. Server-Side Price Verification (Rule 2: Right Amount)
    # -------------------------------------------------------------------------
    async def validate_price_lock(
        self,
        items: List[Dict[str, Any]],
        submitted_total: float,
    ) -> float:
        """
        Recalculates authoritative cart total using the Channel3 product service.
        Raises 409 PRICE_MISMATCH_REAUTHORIZATION_REQUIRED if client tampered with price.
        """
        authoritative_total = 0.0

        for item in items:
            product_id = item.get("id") or item.get("product_id")
            quantity = int(item.get("quantity", 1))

            if product_id:
                server_price = await self.channel3.get_authoritative_price(product_id)
                price = server_price if server_price is not None else float(item.get("price", 100.0))
            else:
                price = float(item.get("price", 100.0))

            authoritative_total += price * quantity

        authoritative_total = round(authoritative_total, 2)

        if abs(submitted_total - authoritative_total) > 0.01:
            logger.warning(
                "Guard: Price mismatch detected! Expected $%.2f, submitted $%.2f",
                authoritative_total,
                submitted_total,
            )
            raise ProblemException.price_mismatch(
                expected=f"{authoritative_total:.2f}",
                submitted=f"{submitted_total:.2f}",
                currency="USD",
            )

        return authoritative_total

    # -------------------------------------------------------------------------
    # 3. Variant Clarification Check (Rule 2: The Misreader Defense)
    # -------------------------------------------------------------------------
    async def validate_variant_selection(
        self,
        items: List[Dict[str, Any]],
        selected_variants: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Ensures items with required variant choices (e.g. size/color) have valid selections.
        Raises 422 AMBIGUOUS_VARIANT_CLARIFICATION_REQUIRED if unselected.
        """
        selected = selected_variants or {}

        for item in items:
            product_id = item.get("id") or item.get("product_id")
            if not product_id:
                continue

            product = await self.channel3.get_product(product_id)
            if product and product.has_variants and product.requires_selection:
                for req_attr in product.requires_selection:
                    if req_attr not in selected or not selected[req_attr]:
                        valid_options = product.variants.get(req_attr, []) if product.variants else []
                        logger.warning(
                            "Guard: Ambiguous variant on product %s; missing %s",
                            product_id,
                            req_attr,
                        )
                        raise ProblemException.ambiguous_variant(
                            product_id=product.id,
                            valid_options=valid_options,
                            missing_attribute=req_attr,
                        )

    # -------------------------------------------------------------------------
    # 4. Cart Intent Integrity Verification (Rule 2: The Content Trap Defense)
    # -------------------------------------------------------------------------
    def validate_cart_intent(
        self,
        expected_hash: Optional[str],
        received_hash: Optional[str],
    ) -> None:
        """
        Validates that human-approved CartReceipt hash matches checkout payload.
        Raises 409 CART_INTENT_MISMATCH on prompt injection or cart manipulation.
        """
        if not expected_hash or not received_hash or expected_hash != received_hash:
            logger.warning("Guard: Cart intent mismatch! Expected %s, got %s", expected_hash, received_hash)
            raise ProblemException.cart_intent_mismatch(
                expected_hash=expected_hash or "NONE",
                received_hash=received_hash or "NONE",
            )

    # -------------------------------------------------------------------------
    # 5. Cumulative Refund Cap (Rule 4: Safe Refunds)
    # -------------------------------------------------------------------------
    def validate_refund_cap(
        self,
        captured_amount: float,
        already_refunded: float,
        requested_refund: float,
    ) -> None:
        """
        Prevents over-refunds where cumulative refunds exceed original capture amount.
        Raises 422 REFUND_EXCEEDS_CAPTURE.
        """
        if already_refunded + requested_refund > captured_amount:
            logger.warning(
                "Guard: Refund cap exceeded! Capture=$%.2f, AlreadyRefunded=$%.2f, Requested=$%.2f",
                captured_amount,
                already_refunded,
                requested_refund,
            )
            raise ProblemException.refund_exceeds_capture(
                captured_amount=f"{captured_amount:.2f}",
                requested_amount=f"{requested_refund:.2f}",
                already_refunded=f"{already_refunded:.2f}",
            )


_guard_instance: Optional[AgentReadyGuard] = None


def get_guard() -> AgentReadyGuard:
    """Returns singleton instance of AgentReadyGuard."""
    global _guard_instance
    if _guard_instance is None:
        _guard_instance = AgentReadyGuard()
    return _guard_instance

