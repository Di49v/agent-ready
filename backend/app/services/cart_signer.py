"""
HMAC Cart-Receipt Signer for AgentReady Lab.
Mints and cryptographically verifies human-approved CartReceipts
to defend against prompt injection and cart manipulation (The Content Trap).
"""
import hashlib
import hmac
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.config import get_settings


class CartReceipt(BaseModel):
    """Human-approved shopping cart intent and price authorization."""
    cart_id: str
    sku: str
    variant: Optional[str] = None
    quantity: int
    max_amount: float
    currency: str = "USD"
    timestamp: str = Field(default_factory=lambda: str(time.time()))
    signature: str = ""


class CartReceiptSigner:
    """
    Utility for signing and validating CartReceipts using HMAC-SHA256.
    Enforces that an autonomous agent cannot order more units or pay a different
    amount than the human buyer explicitly authorized.
    """

    def __init__(self, secret: Optional[str] = None) -> None:
        self.settings = get_settings()
        self.secret = secret or self.settings.CART_RECEIPT_HMAC_SECRET

    def _canonical_payload(
        self,
        cart_id: str,
        sku: str,
        quantity: int,
        max_amount: float,
        variant: Optional[str] = None,
        currency: str = "USD",
        timestamp: Optional[str] = None,
    ) -> str:
        """Constructs canonical string representation for HMAC digest."""
        ts_part = timestamp or ""
        v_part = variant or ""
        return f"{cart_id}:{sku}:{v_part}:{quantity}:{max_amount:.2f}:{currency}:{ts_part}"

    def sign_receipt(
        self,
        cart_id: str,
        sku: str,
        quantity: int,
        max_amount: float,
        variant: Optional[str] = None,
        currency: str = "USD",
    ) -> CartReceipt:
        """Mints a cryptographically signed CartReceipt."""
        ts = str(time.time())
        payload = self._canonical_payload(
            cart_id=cart_id,
            sku=sku,
            quantity=quantity,
            max_amount=max_amount,
            variant=variant,
            currency=currency,
            timestamp=ts,
        )
        sig = hmac.new(self.secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

        return CartReceipt(
            cart_id=cart_id,
            sku=sku,
            variant=variant,
            quantity=quantity,
            max_amount=max_amount,
            currency=currency,
            timestamp=ts,
            signature=sig,
        )

    def verify_receipt_signature(self, receipt: CartReceipt) -> bool:
        """Verifies that the receipt signature was minted with CART_RECEIPT_HMAC_SECRET."""
        payload = self._canonical_payload(
            cart_id=receipt.cart_id,
            sku=receipt.sku,
            quantity=receipt.quantity,
            max_amount=receipt.max_amount,
            variant=receipt.variant,
            currency=receipt.currency,
            timestamp=receipt.timestamp,
        )
        expected_sig = hmac.new(self.secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(receipt.signature, expected_sig)

    def verify_cart_intent(
        self,
        receipt: CartReceipt,
        checkout_items: List[Dict[str, Any]],
        checkout_total: float,
    ) -> bool:
        """
        Validates that the checkout payload matches the human authorization:
          1. Cryptographic HMAC signature must be valid.
          2. Item SKU, quantity, and variant must match.
          3. Total amount must not exceed max_amount.
        """
        if not self.verify_receipt_signature(receipt):
            return False

        if checkout_total > receipt.max_amount + 0.01:
            return False

        # Find matching item in checkout
        matching = [
            item for item in checkout_items
            if (item.get("id") == receipt.sku or item.get("sku") == receipt.sku)
        ]
        if not matching:
            return False

        actual_qty = sum(int(item.get("quantity", 1)) for item in matching)
        if actual_qty != receipt.quantity:
            return False

        return True


_signer_instance: Optional[CartReceiptSigner] = None


def get_cart_signer() -> CartReceiptSigner:
    """Returns singleton CartReceiptSigner instance."""
    global _signer_instance
    if _signer_instance is None:
        _signer_instance = CartReceiptSigner()
    return _signer_instance

