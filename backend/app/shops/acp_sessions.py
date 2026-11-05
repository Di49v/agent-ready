"""
Agentic Commerce Protocol (ACP) Checkout Session Endpoints.
Provides standard session-based checkout flows for external AI shopping agents
and enforces CartReceipt intent verification on Hardened Shop.
"""
import copy
import logging
import time
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.problem_details import ProblemErrorCode, ProblemException
from app.services.cart_signer import CartReceipt, get_cart_signer
from app.shops.hardened_shop import HardenedShop
from app.shops.naive_shop import NaiveShop

logger = logging.getLogger("agentready.acp")


class CreateSessionRequest(BaseModel):
    """Payload to initiate an ACP agent checkout session."""
    target_id: str = Field(default="hardened-shop", description="'naive-shop' or 'hardened-shop'")
    cart_id: str
    items: List[Dict[str, Any]]
    client_price: Optional[float] = None
    receipt: Optional[CartReceipt] = None
    selected_variants: Optional[Dict[str, str]] = None


class CheckoutSession(BaseModel):
    """ACP Checkout Session representation."""
    session_id: str
    target_id: str
    cart_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    currency: str = "USD"
    status: str = "CREATED"  # CREATED, COMPLETED, FAILED
    receipt: Optional[CartReceipt] = None
    order_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: str(time.time()))


class CompleteSessionRequest(BaseModel):
    """Payload to complete an authorized checkout session."""
    idempotency_key: Optional[str] = None
    items: Optional[List[Dict[str, Any]]] = None
    submitted_amount: Optional[float] = None


class ACPSessionManager:
    """
    Manages ACP checkout sessions across Naive Shop and Hardened Shop.
    Enforces CartReceipt validation on Hardened Shop.
    """

    def __init__(self) -> None:
        self.signer = get_cart_signer()
        self.naive_shop = NaiveShop()
        self.hardened_shop = HardenedShop()
        self.sessions: Dict[str, CheckoutSession] = {}

    async def create_session(self, req: CreateSessionRequest) -> CheckoutSession:
        """Initializes a new checkout session on the designated target store."""
        session_id = f"acp_sess_{uuid.uuid4().hex[:12]}"

        # Calculate authoritative total
        shop = self.hardened_shop if req.target_id == "hardened-shop" else self.naive_shop
        cart = await shop.create_cart(
            cart_id=req.cart_id,
            items=req.items,
            client_price=req.client_price,
            selected_variants=req.selected_variants,
            receipt_hash=req.receipt.signature if req.receipt else None,
        )

        session = CheckoutSession(
            session_id=session_id,
            target_id=req.target_id,
            cart_id=req.cart_id,
            items=req.items,
            total_amount=cart["total_amount"],
            currency="USD",
            status="CREATED",
            receipt=req.receipt,
        )
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[CheckoutSession]:
        """Retrieves session by ID."""
        return self.sessions.get(session_id)

    async def complete_session(
        self,
        session_id: str,
        req: CompleteSessionRequest,
    ) -> Dict[str, Any]:
        """
        Completes the agent checkout session.
        On Hardened Shop, verifies human CartReceipt intent against checkout payload.
        Raises 409 CART_INTENT_MISMATCH on tampering (e.g., quantity altered by prompt injection).
        """
        session = self.get_session(session_id)
        if not session:
            raise ProblemException.not_found("CheckoutSession", session_id)

        items_to_checkout = req.items if req.items is not None else session.items
        amount_to_checkout = req.submitted_amount if req.submitted_amount is not None else session.total_amount

        # ---------------------------------------------------------------------
        # Hardened Shop: Enforce CartReceipt Intent Validation
        # ---------------------------------------------------------------------
        if session.target_id == "hardened-shop":
            if session.receipt:
                is_valid = self.signer.verify_cart_intent(
                    receipt=session.receipt,
                    checkout_items=items_to_checkout,
                    checkout_total=amount_to_checkout,
                )
                if not is_valid:
                    logger.warning("ACP: CartReceipt intent verification failed for session %s", session_id)
                    session.status = "FAILED"
                    raise ProblemException.cart_intent_mismatch(
                        expected_hash=session.receipt.signature,
                        received_hash=f"tampered_items_{len(items_to_checkout)}_qty",
                    )

            # Process checkout on Hardened Shop
            order = await self.hardened_shop.checkout_order(
                cart_id=session.cart_id,
                idempotency_key=req.idempotency_key,
                expected_receipt_hash=session.receipt.signature if session.receipt else None,
            )
            session.status = "COMPLETED"
            session.order_id = order.get("order_id")
            return {
                "session_id": session_id,
                "status": "COMPLETED",
                "order": order,
            }

        # ---------------------------------------------------------------------
        # Naive Shop: Vulnerable Checkout (Accepts Altered Quantities / Prices)
        # ---------------------------------------------------------------------
        order = await self.naive_shop.checkout_order(
            cart_id=session.cart_id,
            idempotency_key=req.idempotency_key,
            expected_receipt_hash=None,  # Naive shop skips intent verification
        )
        session.status = "COMPLETED"
        session.order_id = order.get("order_id")
        return {
            "session_id": session_id,
            "status": "COMPLETED",
            "order": order,
            "vulnerable_warning": "Order completed without human intent verification",
        }


_acp_manager: Optional[ACPSessionManager] = None


def get_acp_session_manager() -> ACPSessionManager:
    """Returns singleton ACPSessionManager instance."""
    global _acp_manager
    if _acp_manager is None:
        _acp_manager = ACPSessionManager()
    return _acp_manager

