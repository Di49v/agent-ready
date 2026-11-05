"""
Signed Store Probe Endpoint Helper (/_lab/ledger).
Provides authenticated external read-only access to a merchant's internal order ledger
using HMAC-SHA256 signatures, and implements Black-Box mode for Rule 6 evaluation.
"""
import hashlib
import hmac
import logging
import time
from typing import Any, Dict, Optional

from app.core.config import get_settings

logger = logging.getLogger("agentready.probe")


def generate_probe_signature(
    secret: str,
    timestamp: str,
    path: str = "/_lab/ledger",
) -> str:
    """Generates HMAC-SHA256 signature for authenticating /_lab/ledger probe requests."""
    message = f"{timestamp}:{path}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def verify_probe_signature(
    signature: str,
    timestamp: str,
    secret: str,
    path: str = "/_lab/ledger",
    max_skew_sec: int = 300,
) -> bool:
    """Validates probe signature and ensures timestamp is within the allowable time skew."""
    try:
        ts_float = float(timestamp)
        current_time = time.time()
        if abs(current_time - ts_float) > max_skew_sec:
            logger.warning("Probe signature timestamp outside allowed skew (diff=%.1fs)", abs(current_time - ts_float))
            return False

        expected = generate_probe_signature(secret=secret, timestamp=timestamp, path=path)
        return hmac.compare_digest(signature, expected)
    except Exception as exc:
        logger.warning("Probe signature verification failed: %s", exc)
        return False


def get_store_probe_ledger(
    shop: Any,
    is_black_box: bool = False,
    signature: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieves store ledger snapshot.
    If is_black_box=True or signature is absent/invalid, returns the unverified black-box view
    that triggers Rule 6's honest residual finding (Score: 95/100).
    """
    settings = get_settings()
    secret = settings.LAB_PROBE_HMAC_SECRET

    # Black-box mode or missing credentials
    if is_black_box or not signature or not timestamp:
        return {
            "probe_accessible": False,
            "ledger_proof": "UNVERIFIABLE_WITHOUT_PROBE_SECRET",
            "store_name": getattr(shop, "store_name", "Hardened Shop"),
            "orders": {},
            "payments": {},
            "explanation": (
                "Honest limitation finding on Hardened Shop: When audited without the signed /_lab/ledger "
                "Probe endpoint secret, external reconciliation cannot cryptographically prove that the "
                "merchant's internal order record matches the signed cart receipt hash prior to settlement."
            ),
        }

    # Verify HMAC signature
    is_valid = verify_probe_signature(signature=signature, timestamp=timestamp, secret=secret)
    if not is_valid:
        return {
            "probe_accessible": False,
            "ledger_proof": "INVALID_PROBE_SIGNATURE",
            "orders": {},
            "payments": {},
            "explanation": "Invalid HMAC signature provided for /_lab/ledger probe endpoint.",
        }

    # Verified probe access
    ledger_data = shop.get_ledger_snapshot()
    return {
        **ledger_data,
        "probe_accessible": True,
        "ledger_proof": "CRYPTOGRAPHICALLY_VERIFIED",
    }

