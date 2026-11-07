"""
Fix Engine Code Diff Templates (Grounded with APIMatic Context Plugin for PayPal).
Provides standardized, targeted unified git diff patches for the 6 core bug classes (Section B3.8):
  1. IDEMPOTENCY_PERSISTENCE (Rule 1: Pay Once)
  2. SERVER_PRICE_AUTHORITY (Rule 2: Right Amount)
  3. FULFILLMENT_TRACKING_HOOK (Rule 3: No Orphan Money)
  4. REFUND_BALANCE_GUARD (Rule 4: Safe Refunds)
  5. WEBHOOK_SIGNATURE_VERIFICATION (Rule 5: Records Agree)
  6. CART_INTENT_VERIFICATION (Rule 2 & 6: Proof Ready / Prompt Injection Defense)
"""
from typing import Dict, Optional


class BugClass:
    IDEMPOTENCY_PERSISTENCE = "idempotency_persistence"
    SERVER_PRICE_AUTHORITY = "server_price_authority"
    FULFILLMENT_TRACKING_HOOK = "fulfillment_tracking_hook"
    REFUND_BALANCE_GUARD = "refund_balance_guard"
    WEBHOOK_SIGNATURE_VERIFICATION = "webhook_signature_verification"
    CART_INTENT_VERIFICATION = "cart_intent_verification"
    PROBE_SECRET_CONFIG = "probe_secret_config"


TEMPLATES: Dict[str, Dict[str, str]] = {
    BugClass.IDEMPOTENCY_PERSISTENCE: {
        "file": "checkout.py",
        "title": "Enforce Idempotency Key Mapping and Cache Replay",
        "grounded_api": "PayPal Orders v2 (POST /v2/checkout/orders and capture) with PayPal-Request-Id header",
        "patch": (
            "--- a/checkout.py\n"
            "+++ b/checkout.py\n"
            "@@ -14,6 +14,11 @@\n"
            "-    order = await paypal_client.create_order(cart.total)\n"
            "-    capture = await paypal_client.capture_order(order.id)\n"
            "+    idempotency_key = request.headers.get('Idempotency-Key') or cart_id\n"
            "+    cached_response = guard.check_idempotency(idempotency_key, cart_payload)\n"
            "+    if cached_response is not None:\n"
            "+        return Response(cached_response, headers={'Idempotent-Replayed': 'true'})\n"
            "+    order = await paypal_client.create_order(cart.total, paypal_request_id=idempotency_key)\n"
            "+    capture = await paypal_client.capture_order(order.id, paypal_request_id=idempotency_key)\n"
            "+    guard.save_idempotent_capture(idempotency_key, capture)\n"
        ),
    },
    BugClass.SERVER_PRICE_AUTHORITY: {
        "file": "checkout.py",
        "title": "Recalculate Cart Total from Server Catalog Authority",
        "grounded_api": "PayPal Orders v2 purchase_units[0].amount validated against authoritative server catalog",
        "patch": (
            "--- a/checkout.py\n"
            "+++ b/checkout.py\n"
            "@@ -25,4 +25,7 @@\n"
            "-    order_amount = client_payload.get('amount')\n"
            "-    return await paypal_client.create_order(order_amount)\n"
            "+    server_total = await catalog.calculate_authoritative_total(cart.items)\n"
            "+    if abs(server_total - float(client_payload.get('amount', 0))) > 0.01:\n"
            "+        raise ProblemException.price_mismatch(expected=str(server_total), submitted=str(client_payload.get('amount')))\n"
            "+    return await paypal_client.create_order(server_total)\n"
        ),
    },
    BugClass.FULFILLMENT_TRACKING_HOOK: {
        "file": "fulfillment.py",
        "title": "Atomic Store Order Transaction and Shipment Tracking Sync",
        "grounded_api": "PayPal Orders Tracking API (POST /v2/checkout/orders/{id}/track) within SLA deadline",
        "patch": (
            "--- a/fulfillment.py\n"
            "+++ b/fulfillment.py\n"
            "@@ -19,4 +19,8 @@\n"
            "-    capture = await paypal_client.capture(order_id)\n"
            "-    store_order = db.create_order(capture)\n"
            "+    async with db.transaction():\n"
            "+        capture = await paypal_client.capture(order_id)\n"
            "+        store_order = await db.create_order_or_rollback(cart, capture)\n"
            "+    if not store_order:\n"
            "+        await paypal_client.refund(capture.id, note='Orphan capture auto-reversal')\n"
            "+    await tracking.sync_paypal_tracking(order_id=store_order.id, tracking_number=store_order.tracking_number)\n"
        ),
    },
    BugClass.REFUND_BALANCE_GUARD: {
        "file": "refund.py",
        "title": "Row-Level Mutex Locking and Refund Balance Cap",
        "grounded_api": "PayPal Payments v2 (POST /v2/payments/captures/{id}/refund) balance constraint check",
        "patch": (
            "--- a/refund.py\n"
            "+++ b/refund.py\n"
            "@@ -12,4 +12,9 @@\n"
            "-    return await paypal_client.refund(capture_id, amount)\n"
            "+    async with db.lock_order(order_id):\n"
            "+        remaining_balance = await db.get_refundable_balance(order_id)\n"
            "+        if requested_amount > remaining_balance:\n"
            "+            raise ProblemException.refund_exceeds_capture(captured=str(remaining_balance), requested=str(requested_amount))\n"
            "+        return await paypal_client.refund(capture_id, requested_amount)\n"
        ),
    },
    BugClass.WEBHOOK_SIGNATURE_VERIFICATION: {
        "file": "webhooks.py",
        "title": "Verify PayPal Cryptographic Webhook Signatures",
        "grounded_api": "PayPal Notifications API (POST /v1/notifications/verify-webhook-signature)",
        "patch": (
            "--- a/webhooks.py\n"
            "+++ b/webhooks.py\n"
            "@@ -10,3 +10,7 @@\n"
            "-    event = json.loads(request.body)\n"
            "-    await db.mark_order_paid(event['resource']['custom_id'])\n"
            "+    is_valid = await paypal_client.verify_webhook_signature(headers=request.headers, raw_body=request.body)\n"
            "+    if not is_valid:\n"
            "+        raise ProblemException.webhook_signature_invalid()\n"
            "+    await db.mark_order_paid(event['resource']['custom_id'])\n"
        ),
    },
    BugClass.CART_INTENT_VERIFICATION: {
        "file": "acp_sessions.py",
        "title": "Validate HMAC Cart-Receipt Against Injected Agent Orders",
        "grounded_api": "AP2-Inspired Signed Cart Receipt with HMAC-SHA256 user intent authorization",
        "patch": (
            "--- a/acp_sessions.py\n"
            "+++ b/acp_sessions.py\n"
            "@@ -18,3 +18,7 @@\n"
            "-    order = await paypal_client.create_order(session.cart_total)\n"
            "-    return await paypal_client.capture_order(order.id)\n"
            "+    expected_hash = request.headers.get('X-Cart-Receipt-Hash')\n"
            "+    if not cart_signer.verify_signature(cart_id, expected_hash):\n"
            "+        raise ProblemException.cart_intent_mismatch(expected=expected_hash, received=cart.hash)\n"
            "+    return await paypal_client.create_order(session.cart_total)\n"
        ),
    },
    BugClass.PROBE_SECRET_CONFIG: {
        "file": "hardened_config.py",
        "title": "Configure Signed /_lab/ledger Probe Shared Secret",
        "grounded_api": "AgentReady Lab HMAC-SHA256 Signed Probe Contract",
        "patch": (
            "--- a/hardened_config.py\n"
            "+++ b/hardened_config.py\n"
            "@@ -5,3 +5,5 @@\n"
            "+ENABLE_LAB_PROBE = True\n"
            "+LAB_PROBE_HMAC_SECRET = os.getenv('LAB_PROBE_HMAC_SECRET')\n"
        ),
    },
}


def get_template_for_rule(rule_number: int, persona_id: Optional[str] = None) -> Dict[str, str]:
    """
    Returns the grounded code-diff patch template corresponding to the violated invariant rule.
    """
    if rule_number == 1:
        return TEMPLATES[BugClass.IDEMPOTENCY_PERSISTENCE]
    elif rule_number == 2:
        if persona_id == "the_content_trap":
            return TEMPLATES[BugClass.CART_INTENT_VERIFICATION]
        return TEMPLATES[BugClass.SERVER_PRICE_AUTHORITY]
    elif rule_number == 3:
        return TEMPLATES[BugClass.FULFILLMENT_TRACKING_HOOK]
    elif rule_number == 4:
        return TEMPLATES[BugClass.REFUND_BALANCE_GUARD]
    elif rule_number == 5:
        return TEMPLATES[BugClass.WEBHOOK_SIGNATURE_VERIFICATION]
    elif rule_number == 6:
        if persona_id == "the_disputer":
            return TEMPLATES[BugClass.PROBE_SECRET_CONFIG]
        return TEMPLATES[BugClass.FULFILLMENT_TRACKING_HOOK]
    return TEMPLATES[BugClass.IDEMPOTENCY_PERSISTENCE]


def get_patch_diff(bug_class: str, file_name: Optional[str] = None) -> str:
    """Retrieves unified git diff patch for a given bug class."""
    template = TEMPLATES.get(bug_class, TEMPLATES[BugClass.IDEMPOTENCY_PERSISTENCE])
    patch = template["patch"]
    if file_name and template["file"] != file_name:
        patch = patch.replace(template["file"], file_name)
    return patch

