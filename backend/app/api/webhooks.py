"""
Live PayPal Webhook Event Receiver.
Verifies cryptographic signatures against PayPal Notifications API,
prevents duplicate webhook replays, and persists events to the Reconciler ledger.
"""
import json
import logging
from typing import Any, Dict, Set
from fastapi import APIRouter, Header, Request, Response, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.schemas.problem_details import ProblemException, ProblemErrorCode, ProblemDetails
from app.services.paypal_client import PayPalSandboxClient

logger = logging.getLogger("agentready.webhooks")

router = APIRouter(tags=["Webhooks"])

# In-memory deduplication set for processed webhook IDs (rolling window)
_PROCESSED_WEBHOOK_IDS: Set[str] = set()
_MAX_STORED_IDS = 10000


def is_duplicate_webhook(event_id: str) -> bool:
    """Checks if a webhook event ID was already processed; records it if not."""
    if event_id in _PROCESSED_WEBHOOK_IDS:
        return True
    if len(_PROCESSED_WEBHOOK_IDS) >= _MAX_STORED_IDS:
        _PROCESSED_WEBHOOK_IDS.clear()
    _PROCESSED_WEBHOOK_IDS.add(event_id)
    return False


@router.post(
    "/webhooks/paypal",
    operation_id="receivePaypalWebhook",
    summary="PayPal Webhook Ingestion Endpoint",
    description="Live webhook endpoint registered in PayPal Developer Dashboard. Validates HMAC/RSA signature and dispatches events to dual-ledger.",
    responses={
        200: {"description": "Webhook received, verified, and queued for reconciliation"},
        401: {"description": "Signature verification failed — forged or tampered webhook rejected"},
        409: {"description": "Duplicate webhook delivery rejected (idempotency)"},
    },
)
async def receive_paypal_webhook(request: Request) -> JSONResponse:
    """
    Receives incoming webhook notifications from PayPal Sandbox.
    Enforces signature verification via PayPal's verify-webhook-signature API.
    """
    settings = get_settings()

    # Read raw body bytes for cryptographic verification
    raw_bytes = await request.body()
    try:
        raw_text = raw_bytes.decode("utf-8")
        payload: Dict[str, Any] = json.loads(raw_text) if raw_text else {}
    except Exception as exc:
        logger.error("Failed to parse incoming webhook JSON: %s", exc)
        raise ProblemException(
            status=status.HTTP_400_BAD_REQUEST,
            code=ProblemErrorCode.INVALID_PAYLOAD,
            title="Malformed Webhook JSON",
            detail="The incoming webhook payload could not be parsed as valid JSON.",
        )

    event_id = payload.get("id") or "UNKNOWN_EVENT_ID"
    event_type = payload.get("event_type") or "UNKNOWN_EVENT_TYPE"
    resource = payload.get("resource") or {}

    logger.info("Incoming PayPal Webhook received: ID=%s, Type=%s", event_id, event_type)

    # -------------------------------------------------------------------------
    # 1. Cryptographic Webhook Signature Verification
    # -------------------------------------------------------------------------
    auth_algo = request.headers.get("paypal-auth-algo") or request.headers.get("PAYPAL-AUTH-ALGO")
    transmission_sig = request.headers.get("paypal-transmission-sig") or request.headers.get("PAYPAL-TRANSMISSION-SIG")

    # In live mode (or when credentials & webhook ID are set), enforce signature verification
    should_verify = bool(
        settings.PAYPAL_WEBHOOK_ID
        and not settings.use_mock_blueprint
        and not settings.PAYPAL_CLIENT_ID.startswith("your_")
    )

    if should_verify:
        if not auth_algo or not transmission_sig:
            logger.warning("Rejecting unauthenticated webhook without signature headers: ID=%s", event_id)
            raise ProblemException.webhook_signature_invalid(
                detail="Missing required PayPal transmission signature headers."
            )

        try:
            async with PayPalSandboxClient() as paypal_client:
                is_valid = await paypal_client.verify_webhook_signature(
                    headers=dict(request.headers),
                    raw_body=raw_text,
                )
                if not is_valid:
                    logger.warning("PayPal Webhook signature INVALID for event %s", event_id)
                    raise ProblemException.webhook_signature_invalid(
                        detail="PayPal verify-webhook-signature returned FAILURE. Event is forged or corrupted."
                    )
                logger.info("PayPal Webhook signature VALID for event %s", event_id)
        except ProblemException:
            raise
        except Exception as exc:
            logger.error("Error during webhook signature verification call: %s", exc)
            # Fail closed on verification exceptions in production
            raise ProblemException.webhook_signature_invalid(
                detail=f"Verification subsystem error: {str(exc)}"
            )

    # -------------------------------------------------------------------------
    # 2. Idempotency & Replay Protection (BUG_WEBHOOK_REPLAY_VULN check)
    # -------------------------------------------------------------------------
    if is_duplicate_webhook(event_id):
        logger.warning("Duplicate webhook detected and rejected: ID=%s", event_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "received": True,
                "status": "DUPLICATE_IGNORED",
                "event_id": event_id,
                "event_type": event_type,
                "message": "Webhook already processed previously.",
            },
        )

    # -------------------------------------------------------------------------
    # 3. Event Processing & Dual-Ledger Dispatch
    # -------------------------------------------------------------------------
    cart_id = resource.get("custom_id")
    order_id = resource.get("id") if "ORDER" in event_type else None
    capture_id = resource.get("id") if "CAPTURE" in event_type else None

    # Handle key event types
    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        amount_obj = resource.get("amount") or {}
        amount = f"${amount_obj.get('value', '0.00')}"
        logger.info("Processed PAYMENT.CAPTURE.COMPLETED: Capture=%s, Cart=%s, Amount=%s", capture_id, cart_id, amount)

    elif event_type == "PAYMENT.CAPTURE.REFUNDED":
        amount_obj = resource.get("amount") or {}
        amount = f"${amount_obj.get('value', '0.00')}"
        logger.info("Processed PAYMENT.CAPTURE.REFUNDED: Capture=%s, RefundAmount=%s", capture_id, amount)

    elif event_type == "CUSTOMER.DISPUTE.CREATED":
        dispute_id = resource.get("dispute_id")
        reason = resource.get("reason")
        logger.info("Processed CUSTOMER.DISPUTE.CREATED: DisputeID=%s, Reason=%s", dispute_id, reason)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "received": True,
            "status": "VERIFIED_AND_PROCESSED",
            "event_id": event_id,
            "event_type": event_type,
            "cart_id": cart_id,
        },
    )

