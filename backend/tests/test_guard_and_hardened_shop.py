"""
Unit tests for AgentReady Guard, Hardened Shop, and Signed Probe (/_lab/ledger).
Verifies RFC 9457 structured error handling on all invariant violations,
idempotent replays, and HMAC probe authentication / black-box mode fallback.
"""
import time
import pytest
from app.core.config import get_settings
from app.schemas.problem_details import ProblemErrorCode, ProblemException
from app.shops.guard import AgentReadyGuard
from app.shops.hardened_shop import HardenedShop
from app.shops.probe import (
    generate_probe_signature,
    get_store_probe_ledger,
    verify_probe_signature,
)


@pytest.mark.asyncio
async def test_guard_price_lock_enforcement() -> None:
    """Verifies that Guard raises 409 PRICE_MISMATCH when client attempts price tampering."""
    guard = AgentReadyGuard()

    # prod_headphones_001 is $399.00
    with pytest.raises(ProblemException) as exc_info:
        await guard.validate_price_lock(
            items=[{"id": "prod_headphones_001", "quantity": 1}],
            submitted_total=1.50,
        )
    assert exc_info.value.status == 409
    assert exc_info.value.problem.code == ProblemErrorCode.PRICE_MISMATCH_REAUTHORIZATION_REQUIRED
    assert "399.00" in exc_info.value.problem.detail


@pytest.mark.asyncio
async def test_guard_variant_clarification_enforcement() -> None:
    """Verifies that Guard raises 422 AMBIGUOUS_VARIANT on unselected options."""
    guard = AgentReadyGuard()

    # prod_running_shoes_002 requires size and color
    with pytest.raises(ProblemException) as exc_info:
        await guard.validate_variant_selection(
            items=[{"id": "prod_running_shoes_002", "quantity": 1}],
            selected_variants={"size": "10"},  # Missing color
        )
    assert exc_info.value.status == 422
    assert exc_info.value.problem.code == ProblemErrorCode.AMBIGUOUS_VARIANT_CLARIFICATION_REQUIRED


@pytest.mark.asyncio
async def test_guard_idempotency_caching() -> None:
    """Verifies that repeated requests with the same idempotency key replay cached response."""
    guard = AgentReadyGuard()
    key = "idemp_test_key_001"
    payload = {"cart_id": "c1", "amount": 120.00}
    response = {"order_id": "ORD-123", "status": "PAID"}

    # First check -> None (not cached yet)
    assert guard.check_idempotency(key, payload) is None

    # Record response
    guard.record_idempotent_response(key, payload, response)

    # Second check -> Replay
    replayed = guard.check_idempotency(key, payload)
    assert replayed is not None
    assert replayed["order_id"] == "ORD-123"
    assert replayed["idempotent_replayed"] is True


@pytest.mark.asyncio
async def test_hardened_shop_checkout_and_tracking() -> None:
    """Verifies that Hardened Shop successfully creates order, tracking number, and idempotent replay."""
    shop = HardenedShop()

    # 1. Create cart with correct variant selection
    cart = await shop.create_cart(
        cart_id="hardened_cart_01",
        items=[{"id": "prod_running_shoes_002", "quantity": 1}],
        selected_variants={"size": "10", "color": "Black/White"},
    )
    assert cart["total_amount"] == 130.00

    # 2. Checkout order
    order = await shop.checkout_order(
        cart_id="hardened_cart_01",
        idempotency_key="idemp_hardened_01",
    )
    assert order["status"] == "PAID"
    assert order["tracking_number"] == "1Z9999999999999999"
    assert order["amount"] == 130.00

    # 3. Retry checkout with same idempotency key -> Replays cleanly
    retry_order = await shop.checkout_order(
        cart_id="hardened_cart_01",
        idempotency_key="idemp_hardened_01",
    )
    assert retry_order["idempotent_replayed"] is True
    assert retry_order["order_id"] == order["order_id"]


@pytest.mark.asyncio
async def test_probe_hmac_authentication_and_blackbox_mode() -> None:
    """Verifies HMAC probe signature verification and black-box fallback mode."""
    settings = get_settings()
    secret = settings.LAB_PROBE_HMAC_SECRET
    shop = HardenedShop()

    # 1. Valid HMAC probe signature -> Full verified access
    ts = str(time.time())
    sig = generate_probe_signature(secret=secret, timestamp=ts)
    assert verify_probe_signature(signature=sig, timestamp=ts, secret=secret) is True

    verified_ledger = get_store_probe_ledger(
        shop=shop,
        is_black_box=False,
        signature=sig,
        timestamp=ts,
    )
    assert verified_ledger["probe_accessible"] is True
    assert verified_ledger["ledger_proof"] == "CRYPTOGRAPHICALLY_VERIFIED"

    # 2. Black-box mode -> Returns honest residual limitation finding (Score: 95/100)
    blackbox_ledger = get_store_probe_ledger(
        shop=shop,
        is_black_box=True,
    )
    assert blackbox_ledger["probe_accessible"] is False
    assert blackbox_ledger["ledger_proof"] == "UNVERIFIABLE_WITHOUT_PROBE_SECRET"
    assert "Honest limitation" in blackbox_ledger["explanation"]

