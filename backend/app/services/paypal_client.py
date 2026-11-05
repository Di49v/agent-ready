"""
Async PayPal Sandbox Client for AgentReady Lab.
Grounded with APIMatic's official `paypal` SDK (version 2.29).
Enforces hard-pinned Sandbox endpoints, idempotency request IDs,
and batched concurrency (MAX_CONCURRENT_BUYERS = 5).
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx
from paypal import AsyncPaypalClient
from paypal.core import ApiError, ClientCredentials
from paypal.models import (
    AmountWithBreakdown,
    CardRequest,
    Order,
    OrderCaptureRequest,
    OrderRequest,
    PaymentAuthorization,
    PaymentSource,
    PurchaseUnitRequest,
    Refund,
    RefundRequest,
)

from app.core.config import get_settings

logger = logging.getLogger("agentready.paypal")


class PayPalSandboxClient:
    """
    High-level async client wrapping the official APIMatic PayPal SDK.
    Pins all operations to https://api-m.sandbox.paypal.com.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.semaphore = asyncio.Semaphore(self.settings.MAX_CONCURRENT_BUYERS)

        # Initialize the official APIMatic AsyncPaypalClient with OAuth 2.0 Client Credentials
        self.sdk = AsyncPaypalClient(
            base_url=self.settings.PAYPAL_BASE_URL,
            oauth2=ClientCredentials(
                client_id=self.settings.PAYPAL_CLIENT_ID,
                client_secret=self.settings.PAYPAL_CLIENT_SECRET,
            ),
        )

    async def aclose(self) -> None:
        """Closes the underlying HTTP transport cleanly."""
        await self.sdk.aclose()

    async def __aenter__(self) -> "PayPalSandboxClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.aclose()

    # -------------------------------------------------------------------------
    # 1. Unattended Order Creation with Card Payment Source
    # -------------------------------------------------------------------------
    async def create_card_order(
        self,
        cart_id: str,
        amount_value: str,
        card_number: Optional[str] = None,
        card_expiry: Optional[str] = None,
        card_cvv: Optional[str] = None,
        currency: str = "USD",
        request_id: Optional[str] = None,
        intent: str = "CAPTURE",
    ) -> Order:
        """
        Creates an unattended PayPal order with card payment source.
        Attaches `purchase_units[0].custom_id = cart_id` as the cross-ledger join key.
        """
        number = card_number or self.settings.PAYPAL_TEST_CARD_NUMBER
        expiry = card_expiry or self.settings.PAYPAL_TEST_CARD_EXPIRY
        cvv = card_cvv or self.settings.PAYPAL_TEST_CARD_CVV

        order_req = OrderRequest(
            intent=intent,
            purchase_units=[
                PurchaseUnitRequest(
                    custom_id=cart_id,
                    amount=AmountWithBreakdown(
                        currency_code=currency,
                        value=amount_value,
                    ),
                    description=f"AgentReady Cart {cart_id}",
                )
            ],
            payment_source=PaymentSource(
                card=CardRequest(
                    number=number,
                    expiry=expiry,
                    security_code=cvv,
                    name="AgentReady Test Buyer",
                )
            ),
        )

        async with self.semaphore:
            logger.info("Creating order for cart %s with request_id %s", cart_id, request_id)
            return await self.sdk.orders.create_order(
                body=order_req,
                pay_pal_request_id=request_id,
            )

    # -------------------------------------------------------------------------
    # 2. Capture Order Payment
    # -------------------------------------------------------------------------
    async def capture_order(
        self,
        order_id: str,
        request_id: Optional[str] = None,
    ) -> Order:
        """
        Captures an approved or card-funded PayPal order.
        """
        async with self.semaphore:
            logger.info("Capturing order %s with request_id %s", order_id, request_id)
            return await self.sdk.orders.capture_order(
                id_=order_id,
                pay_pal_request_id=request_id,
                body=OrderCaptureRequest(),
            )

    # -------------------------------------------------------------------------
    # 3. Refund Captured Payment
    # -------------------------------------------------------------------------
    async def refund_captured_payment(
        self,
        capture_id: str,
        amount_value: Optional[str] = None,
        currency: str = "USD",
        request_id: Optional[str] = None,
    ) -> Refund:
        """
        Refunds a captured payment by ID. If amount_value is None, issues a full refund.
        """
        body: Optional[RefundRequest] = None
        if amount_value:
            body = RefundRequest(
                amount=AmountWithBreakdown(
                    currency_code=currency,
                    value=amount_value,
                )
            )

        async with self.semaphore:
            logger.info("Refunding capture %s with amount %s", capture_id, amount_value)
            return await self.sdk.payments.refund_captured_payment(
                capture_id=capture_id,
                pay_pal_request_id=request_id,
                body=body,
            )

    # -------------------------------------------------------------------------
    # 4. Void Payment Authorization
    # -------------------------------------------------------------------------
    async def void_payment(
        self,
        authorization_id: str,
        request_id: Optional[str] = None,
    ) -> PaymentAuthorization:
        """
        Voids an authorized payment by ID.
        """
        async with self.semaphore:
            logger.info("Voiding authorization %s", authorization_id)
            return await self.sdk.payments.void_payment(
                authorization_id=authorization_id,
                pay_pal_request_id=request_id,
            )

    # -------------------------------------------------------------------------
    # 5. Webhook Signature Verification (Notifications API)
    # -------------------------------------------------------------------------
    async def verify_webhook_signature(
        self,
        headers: Dict[str, str],
        raw_body: str,
        webhook_id: Optional[str] = None,
    ) -> bool:
        """
        Validates the authenticity of an incoming PayPal webhook event
        against PayPal's verify-webhook-signature endpoint.
        """
        target_webhook_id = webhook_id or self.settings.PAYPAL_WEBHOOK_ID
        if not target_webhook_id:
            logger.warning("No webhook_id configured; skipping live signature check")
            return False

        # Extract PayPal verification headers
        auth_algo = headers.get("paypal-auth-algo") or headers.get("PAYPAL-AUTH-ALGO")
        cert_url = headers.get("paypal-cert-url") or headers.get("PAYPAL-CERT-URL")
        transmission_id = headers.get("paypal-transmission-id") or headers.get("PAYPAL-TRANSMISSION-ID")
        transmission_sig = headers.get("paypal-transmission-sig") or headers.get("PAYPAL-TRANSMISSION-SIG")
        transmission_time = headers.get("paypal-transmission-time") or headers.get("PAYPAL-TRANSMISSION-TIME")

        if not all([auth_algo, cert_url, transmission_id, transmission_sig, transmission_time]):
            logger.warning("Missing required PayPal webhook headers for signature verification")
            return False

        payload = {
            "auth_algo": auth_algo,
            "cert_url": cert_url,
            "transmission_id": transmission_id,
            "transmission_sig": transmission_sig,
            "transmission_time": transmission_time,
            "webhook_id": target_webhook_id,
            "webhook_event": raw_body if isinstance(raw_body, dict) else httpx._models.json.loads(raw_body),
        }

        # Request an access token to call the notifications endpoint
        token_url = f"{self.settings.PAYPAL_BASE_URL}/v1/oauth2/token"
        verify_url = f"{self.settings.PAYPAL_BASE_URL}/v1/notifications/verify-webhook-signature"

        async with httpx.AsyncClient(timeout=15.0) as client:
            token_resp = await client.post(
                token_url,
                data={"grant_type": "client_credentials"},
                auth=(self.settings.PAYPAL_CLIENT_ID, self.settings.PAYPAL_CLIENT_SECRET),
            )
            if token_resp.status_code != 200:
                logger.error("Failed to obtain OAuth2 token for webhook verification: %s", token_resp.text)
                return False

            access_token = token_resp.json().get("access_token")
            verify_resp = await client.post(
                verify_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            if verify_resp.status_code == 200:
                status = verify_resp.json().get("verification_status")
                logger.info("Webhook verification result: %s", status)
                return status == "SUCCESS"

            logger.error("Webhook verify call failed: %s", verify_resp.text)
            return False

    # -------------------------------------------------------------------------
    # 6. Negative Testing / Chargeback Simulator (Sandbox Only)
    # -------------------------------------------------------------------------
    async def process_sandbox_chargeback(
        self,
        dispute_id: str,
        action: str = "ACCEPT_DISPUTE",
    ) -> Dict[str, Any]:
        """
        Invokes PayPal Sandbox dispute simulator to simulate chargeback transitions.
        """
        token_url = f"{self.settings.PAYPAL_BASE_URL}/v1/oauth2/token"
        chargeback_url = f"{self.settings.PAYPAL_BASE_URL}/v2/customer-support/process-chargeback"

        async with httpx.AsyncClient(timeout=15.0) as client:
            token_resp = await client.post(
                token_url,
                data={"grant_type": "client_credentials"},
                auth=(self.settings.PAYPAL_CLIENT_ID, self.settings.PAYPAL_CLIENT_SECRET),
            )
            if token_resp.status_code != 200:
                return {"error": "Failed to authenticate", "details": token_resp.text}

            token = token_resp.json().get("access_token")
            resp = await client.post(
                chargeback_url,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={"dispute_id": dispute_id, "action": action},
            )
            return {"status_code": resp.status_code, "body": resp.json() if resp.text else {}}

