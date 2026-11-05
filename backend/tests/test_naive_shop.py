"""
Unit tests for the 12 Independent Bug Flags & Naive Shop Implementation.
Verifies all-on (Naive Shop baseline), all-off (Hardened baseline),
and individual vulnerability toggles across pricing, idempotency, variants, and refunds.
"""
import pytest
from app.schemas.problem_details import ProblemErrorCode, ProblemException
from app.shops.bug_flags import BugConfig, BugFlag
from app.shops.naive_shop import NaiveShop


def test_bug_flags_toggle_matrix() -> None:
    """Verifies that all 12 bug flags can be toggled individually, all-on, and all-off."""
    all_on = BugConfig.all_on()
    assert len(all_on.active_flags()) == 12
    assert all_on.is_enabled(BugFlag.BUG_NO_IDEMPOTENCY) is True
    assert all_on.is_enabled(BugFlag.BUG_TRUST_CLIENT_PRICE) is True

    all_off = BugConfig.all_off()
    assert len(all_off.active_flags()) == 0
    assert all_off.is_enabled(BugFlag.BUG_NO_IDEMPOTENCY) is False

    # Individual toggles
    custom = BugConfig.all_off()
    custom.enable(BugFlag.BUG_TRUST_CLIENT_PRICE)
    assert custom.is_enabled(BugFlag.BUG_TRUST_CLIENT_PRICE) is True
    assert custom.is_enabled(BugFlag.BUG_NO_IDEMPOTENCY) is False

    custom.disable(BugFlag.BUG_TRUST_CLIENT_PRICE)
    assert custom.is_enabled(BugFlag.BUG_TRUST_CLIENT_PRICE) is False


@pytest.mark.asyncio
async def test_bug_trust_client_price_vulnerability() -> None:
    """Verifies BUG_TRUST_CLIENT_PRICE behavior when enabled vs disabled."""
    # 1. When enabled (Naive Shop baseline): accepts $1.50 client price on a $399 item
    shop_vulnerable = NaiveShop(BugConfig.all_on())
    cart = await shop_vulnerable.create_cart(
        cart_id="cart_tamper_1",
        items=[{"id": "prod_headphones_001", "quantity": 1}],
        client_price=1.50,
    )
    assert cart["total_amount"] == 1.50

    # 2. When disabled (Hardened check): rejects with 409 PRICE_MISMATCH
    shop_protected = NaiveShop(BugConfig.all_off())
    with pytest.raises(ProblemException) as exc_info:
        await shop_protected.create_cart(
            cart_id="cart_tamper_2",
            items=[{"id": "prod_headphones_001", "quantity": 1}],
            client_price=1.50,
        )
    assert exc_info.value.status == 409
    assert exc_info.value.problem.code == ProblemErrorCode.PRICE_MISMATCH_REAUTHORIZATION_REQUIRED


@pytest.mark.asyncio
async def test_bug_no_idempotency_vulnerability() -> None:
    """Verifies BUG_NO_IDEMPOTENCY behavior on duplicate checkout retries."""
    # 1. When enabled (Naive Shop): creates duplicate orders/payments on retry
    shop_vulnerable = NaiveShop(BugConfig.all_on())
    await shop_vulnerable.create_cart(
        cart_id="cart_retry_1",
        items=[{"id": "prod_headphones_001", "quantity": 1}],
        client_price=399.00,
    )

    res1 = await shop_vulnerable.checkout_order(cart_id="cart_retry_1")
    res2 = await shop_vulnerable.checkout_order(cart_id="cart_retry_1")
    # Vulnerable store accepts both and produces two different orders / captures
    assert len(shop_vulnerable.payments) == 2
    assert res1.get("idempotent_replayed") is None
    assert res2.get("idempotent_replayed") is None

    # 2. When disabled (Hardened): returns idempotent replay
    shop_protected = NaiveShop(BugConfig.all_off())
    await shop_protected.create_cart(
        cart_id="cart_retry_2",
        items=[{"id": "prod_headphones_001", "quantity": 1}],
        client_price=399.00,
    )

    pres1 = await shop_protected.checkout_order(cart_id="cart_retry_2")
    pres2 = await shop_protected.checkout_order(cart_id="cart_retry_2")
    assert pres2.get("idempotent_replayed") is True
    assert pres1["order_id"] == pres2["order_id"]


@pytest.mark.asyncio
async def test_bug_allow_ambiguous_variant() -> None:
    """Verifies BUG_ALLOW_AMBIGUOUS_VARIANT on multi-variant product."""
    # 1. When enabled (Naive): allows checkout of shoes with no size or color selected
    shop_vulnerable = NaiveShop(BugConfig.all_on())
    cart = await shop_vulnerable.create_cart(
        cart_id="cart_variant_1",
        items=[{"id": "prod_running_shoes_002", "quantity": 1}],
        selected_variants=None,
    )
    assert cart["total_amount"] == 130.00

    # 2. When disabled (Hardened): raises 422 AMBIGUOUS_VARIANT
    shop_protected = NaiveShop(BugConfig.all_off())
    with pytest.raises(ProblemException) as exc_info:
        await shop_protected.create_cart(
            cart_id="cart_variant_2",
            items=[{"id": "prod_running_shoes_002", "quantity": 1}],
            selected_variants=None,
        )
    assert exc_info.value.status == 422
    assert exc_info.value.problem.code == ProblemErrorCode.AMBIGUOUS_VARIANT_CLARIFICATION_REQUIRED


@pytest.mark.asyncio
async def test_bug_over_refund() -> None:
    """Verifies BUG_OVER_REFUND when requesting refund exceeding captured amount."""
    # 1. When enabled (Naive): allows refund of $500 on a $399 purchase
    shop_vulnerable = NaiveShop(BugConfig.all_on())
    await shop_vulnerable.create_cart(
        cart_id="cart_refund_1",
        items=[{"id": "prod_headphones_001", "quantity": 1}],
        client_price=399.00,
    )
    order = await shop_vulnerable.checkout_order(cart_id="cart_refund_1")
    order_id = order["order_id"]
    if order_id:
        refund = await shop_vulnerable.refund_order(order_id=order_id, refund_amount=500.00)
        assert refund["amount"] == 500.00

    # 2. When disabled (Hardened): rejects refund exceeding capture with 422
    shop_protected = NaiveShop(BugConfig.all_off())
    await shop_protected.create_cart(
        cart_id="cart_refund_2",
        items=[{"id": "prod_headphones_001", "quantity": 1}],
        client_price=399.00,
    )
    p_order = await shop_protected.checkout_order(cart_id="cart_refund_2")
    with pytest.raises(ProblemException) as exc_info:
        await shop_protected.refund_order(order_id=p_order["order_id"], refund_amount=500.00)
    assert exc_info.value.status == 422
    assert exc_info.value.problem.code == ProblemErrorCode.REFUND_EXCEEDS_CAPTURE


@pytest.mark.asyncio
async def test_bug_no_webhook_verify() -> None:
    """Verifies BUG_NO_WEBHOOK_VERIFY on unverified/forged webhook signatures."""
    # 1. When enabled (Naive): blindly processes forged webhook
    shop_vulnerable = NaiveShop(BugConfig.all_on())
    resp = await shop_vulnerable.handle_webhook(
        event={"id": "WH-TEST-001", "event_type": "PAYMENT.CAPTURE.COMPLETED"},
        headers={"PAYPAL-TRANSMISSION-SIG": "forged_signature_invalid"},
    )
    assert resp["status"] == "PROCESSED"

    # 2. When disabled (Hardened): rejects with 401 WEBHOOK_SIGNATURE_INVALID
    shop_protected = NaiveShop(BugConfig.all_off())
    with pytest.raises(ProblemException) as exc_info:
        await shop_protected.handle_webhook(
            event={"id": "WH-TEST-002", "event_type": "PAYMENT.CAPTURE.COMPLETED"},
            headers={"PAYPAL-TRANSMISSION-SIG": "forged_signature_invalid"},
        )
    assert exc_info.value.status == 401
    assert exc_info.value.problem.code == ProblemErrorCode.WEBHOOK_SIGNATURE_INVALID

