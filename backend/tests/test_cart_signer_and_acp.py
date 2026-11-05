"""
Unit tests for CartReceiptSigner & ACP Checkout Sessions.
Verifies cryptographic HMAC signature generation, prompt injection defense,
and 409 CART_INTENT_MISMATCH enforcement when cart quantities or prices are tampered.
"""
import pytest
from app.schemas.problem_details import ProblemErrorCode, ProblemException
from app.services.cart_signer import CartReceiptSigner, get_cart_signer
from app.shops.acp_sessions import (
    ACPSessionManager,
    CompleteSessionRequest,
    CreateSessionRequest,
)


def test_cart_signer_mint_and_verify() -> None:
    """Verifies that CartReceiptSigner generates valid HMAC signatures."""
    signer = get_cart_signer()

    # Human approves 1 unit of smart mug for up to $150.00
    receipt = signer.sign_receipt(
        cart_id="cart_intent_001",
        sku="prod_smart_mug_003",
        quantity=1,
        max_amount=150.00,
        variant=None,
        currency="USD",
    )

    assert receipt.signature != ""
    assert signer.verify_receipt_signature(receipt) is True

    # Valid checkout: 1 unit at $149.95
    valid_items = [{"id": "prod_smart_mug_003", "quantity": 1, "price": 149.95}]
    assert signer.verify_cart_intent(receipt, valid_items, 149.95) is True


def test_cart_signer_detects_prompt_injection_quantity_tampering() -> None:
    """
    Verifies that altering quantity (e.g. from 1 to 5 units per prompt injection)
    is detected and rejected by the signer.
    """
    signer = get_cart_signer()

    receipt = signer.sign_receipt(
        cart_id="cart_intent_002",
        sku="prod_smart_mug_003",
        quantity=1,
        max_amount=150.00,
    )

    # Agent follows prompt injection: alters quantity to 5
    tampered_items = [{"id": "prod_smart_mug_003", "quantity": 5, "price": 149.95}]
    assert signer.verify_cart_intent(receipt, tampered_items, 149.95) is False


def test_cart_signer_detects_amount_exceeded() -> None:
    """Verifies that total amount exceeding max_amount is rejected."""
    signer = get_cart_signer()

    receipt = signer.sign_receipt(
        cart_id="cart_intent_003",
        sku="prod_smart_mug_003",
        quantity=1,
        max_amount=150.00,
    )

    valid_items = [{"id": "prod_smart_mug_003", "quantity": 1, "price": 175.00}]
    # Price is $175.00 > authorized $150.00
    assert signer.verify_cart_intent(receipt, valid_items, 175.00) is False


@pytest.mark.asyncio
async def test_acp_session_tampering_triggers_409_on_hardened_shop() -> None:
    """
    Verifies that ACP checkout session on Hardened Shop raises 409 CART_INTENT_MISMATCH
    when quantity is tampered after signing.
    """
    manager = ACPSessionManager()
    signer = manager.signer

    # 1. Human signs receipt for 1 unit of smart mug ($149.95)
    receipt = signer.sign_receipt(
        cart_id="cart_acp_001",
        sku="prod_smart_mug_003",
        quantity=1,
        max_amount=150.00,
    )

    # 2. Agent creates checkout session
    session = await manager.create_session(
        CreateSessionRequest(
            target_id="hardened-shop",
            cart_id="cart_acp_001",
            items=[{"id": "prod_smart_mug_003", "quantity": 1, "price": 149.95}],
            receipt=receipt,
        )
    )
    assert session.status == "CREATED"

    # 3. Agent attempts to complete session with tampered quantity = 5 (Prompt Injection)
    with pytest.raises(ProblemException) as exc_info:
        await manager.complete_session(
            session_id=session.session_id,
            req=CompleteSessionRequest(
                idempotency_key="idemp_acp_001",
                items=[{"id": "prod_smart_mug_003", "quantity": 5, "price": 149.95}],
                submitted_amount=149.95,
            ),
        )

    assert exc_info.value.status == 409
    assert exc_info.value.problem.code == ProblemErrorCode.CART_INTENT_MISMATCH
    assert "Order does not match what the human approved" in exc_info.value.problem.title


@pytest.mark.asyncio
async def test_acp_session_successful_on_valid_intent() -> None:
    """Verifies that an authorized ACP session completes successfully on Hardened Shop."""
    manager = ACPSessionManager()
    signer = manager.signer

    receipt = signer.sign_receipt(
        cart_id="cart_acp_002",
        sku="prod_headphones_001",
        quantity=1,
        max_amount=400.00,
    )

    session = await manager.create_session(
        CreateSessionRequest(
            target_id="hardened-shop",
            cart_id="cart_acp_002",
            items=[{"id": "prod_headphones_001", "quantity": 1}],
            receipt=receipt,
        )
    )

    # Complete session with matching 1 unit
    result = await manager.complete_session(
        session_id=session.session_id,
        req=CompleteSessionRequest(idempotency_key="idemp_acp_002"),
    )
    assert result["status"] == "COMPLETED"
    assert result["order"]["status"] == "PAID"
    assert result["order"]["tracking_number"] == "1Z9999999999999999"

