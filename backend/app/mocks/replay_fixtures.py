"""
Deterministic Mock and Replay Data Provider for AgentReady Lab.
Supplies realistic pre-recorded fixtures for Naive Shop (Score: 18/100) and
Hardened Shop (Score: 95/100) to power the full-stack Blueprint and the
production 'Replay Last Run' fallback mechanism (Sections A9, B3.7, B11).
"""
from typing import Any, Dict, List, Optional
from app.schemas.contracts import (
    AutoReversalPolicy,
    DualLedgerRow,
    FindingDetail,
    FindingSeverity,
    LedgerSnapshot,
    PersonaSpec,
    RuleScore,
    RunEvent,
    RunStatus,
    RunSummary,
    TargetStore,
)

# -----------------------------------------------------------------------------
# 1. Built-in Targets
# -----------------------------------------------------------------------------

MOCK_TARGETS: List[TargetStore] = [
    TargetStore(
        id="naive-shop",
        name="Naive Shop (Vulnerable Baseline)",
        base_url="http://localhost:8000/demo/naive",
        mode="probe",
        probe_url="http://localhost:8000/demo/naive/_lab/ledger",
        ledger_secret="mock_naive_probe_secret_32bytes_hex",
        description="Reference e-commerce store with common AI commerce flaws: missing idempotency, unverified webhooks, client price trust.",
        is_demo=True,
        created_at="2026-11-05T00:00:00Z",
    ),
    TargetStore(
        id="hardened-shop",
        name="Hardened Shop (Guard Protected)",
        base_url="http://localhost:8000/demo/hardened",
        mode="probe",
        probe_url="http://localhost:8000/demo/hardened/_lab/ledger",
        ledger_secret="mock_hardened_probe_secret_32bytes_hex",
        description="Hardened store protected by AgentReady Guard middleware: idempotency cache, server price recomputation, RFC 9457 structured errors.",
        is_demo=True,
        created_at="2026-11-05T00:00:00Z",
    ),
]


def get_mock_targets() -> List[TargetStore]:
    """Returns all pre-registered target stores."""
    return MOCK_TARGETS


def get_mock_target(target_id: str) -> Optional[TargetStore]:
    """Finds a target store by ID."""
    for t in MOCK_TARGETS:
        if t.id == target_id:
            return t
    return None


# -----------------------------------------------------------------------------
# 2. The 9 Adversarial Personas (Section A6)
# -----------------------------------------------------------------------------

MOCK_PERSONAS: List[PersonaSpec] = [
    PersonaSpec(
        id="the_retrier",
        name="The Retrier",
        plain_words="Connection drops after paying, then it tries again",
        rule_number=1,
        rule_name="Pay Once",
        driven_by="fixed_script",
        fault_description="Drops HTTP response after successful capture and replays identical request",
        expected_behavior="Store must reuse PayPal-Request-Id and return original capture with Idempotent-Replayed: true",
        wave=1,
    ),
    PersonaSpec(
        id="the_tamperer",
        name="The Tamperer",
        plain_words="Edits the amount, currency or quantity",
        rule_number=2,
        rule_name="Right Amount",
        driven_by="fixed_script",
        fault_description="Alters unit price in client JSON from $150.00 to $1.50 before order submission",
        expected_behavior="Store must reject tampered price with 409 PRICE_MISMATCH_REAUTHORIZATION_REQUIRED",
        wave=1,
    ),
    PersonaSpec(
        id="the_stale_cart",
        name="The Stale Cart",
        plain_words="Price or stock changes between cart and payment",
        rule_number=2,
        rule_name="Right Amount",
        driven_by="fixed_script",
        fault_description="Simulates 10-minute cart inactivity during which catalog price increases by $10.00",
        expected_behavior="Store recalculates total at checkout and requests fresh consent via RFC 9457 error",
        wave=1,
    ),
    PersonaSpec(
        id="the_webhook_skeptic",
        name="The Webhook Skeptic",
        plain_words="Replays, forges and reorders PayPal notifications",
        rule_number=5,
        rule_name="Records Agree",
        driven_by="fixed_script",
        fault_description="Sends forged CHECKOUT.ORDER.APPROVED webhook with invalid signature",
        expected_behavior="Store calls verify-webhook-signature, drops event, and returns 401 WEBHOOK_SIGNATURE_INVALID",
        wave=1,
    ),
    PersonaSpec(
        id="the_refunder",
        name="The Refunder",
        plain_words="Asks for a partial refund twice",
        rule_number=4,
        rule_name="Safe Refunds",
        driven_by="fixed_script",
        fault_description="Requests two parallel $70.00 partial refunds against a single $100.00 capture",
        expected_behavior="Store checks remaining capture balance with locking, rejecting the second refund with 422",
        wave=1,
    ),
    PersonaSpec(
        id="the_ghost_order",
        name="The Ghost Order",
        plain_words="Pays, then waits to see if the store ships and tracks",
        rule_number=3,
        rule_name="No Orphan Money",
        driven_by="fixed_script",
        fault_description="Simulates store DB crash immediately after PayPal capture succeeds, omitting order and tracking",
        expected_behavior="Store creates order inside atomic transaction or automatically refunds orphan capture within 8s SLA",
        wave=2,
    ),
    PersonaSpec(
        id="the_disputer",
        name="The Disputer",
        plain_words="Triggers a sandbox chargeback or dispute",
        rule_number=6,
        rule_name="Proof Ready",
        driven_by="fixed_script",
        fault_description="Simulates buyer-initiated credit card dispute in PayPal Sandbox",
        expected_behavior="Store provides verifiable tracking number and signed cart receipt within dispute evidence window",
        wave=2,
    ),
    PersonaSpec(
        id="the_misreader",
        name="The Misreader",
        plain_words="Shops from real Channel3 listings with ambiguous sizes or colours",
        rule_number=2,
        rule_name="Right Amount",
        driven_by="live_llm",
        fault_description="Submits checkout payload without selecting required size option for multi-variant apparel",
        expected_behavior="Store blocks order creation and returns 422 AMBIGUOUS_VARIANT_CLARIFICATION_REQUIRED",
        wave=2,
    ),
    PersonaSpec(
        id="the_content_trap",
        name="The Content Trap",
        plain_words="Reads product text with a hidden instruction such as 'order 5 units'",
        rule_number=2,
        rule_name="Right Amount",
        driven_by="live_llm",
        fault_description="Injected adversarial prompt in product description prompts agent to modify approved quantity",
        expected_behavior="Store verifies signed cart receipt and rejects tampered quantity with 409 CART_INTENT_MISMATCH",
        wave=2,
    ),
]


def get_mock_personas() -> List[PersonaSpec]:
    """Returns the full 9-persona test pack."""
    return MOCK_PERSONAS


# -----------------------------------------------------------------------------
# 3. Naive Shop Findings (Score: 18/100, seed=42)
# -----------------------------------------------------------------------------

MOCK_NAIVE_FINDINGS: List[FindingDetail] = [
    FindingDetail(
        id="find_r1_double_capture",
        run_id="run_42_naive_shop",
        rule_number=1,
        rule_name="Pay Once",
        severity=FindingSeverity.CRITICAL,
        persona_id="the_retrier",
        title="Double Capture Detected on Idempotent Replay",
        evidence_ids=["5O190127TN364715T", "2GG279541U471931P", "7K8830129L554122X"],
        paypal_record={
            "order_id": "5O190127TN364715T",
            "custom_id": "cart_lane1_retrier",
            "intent": "CAPTURE",
            "status": "COMPLETED",
            "total_captured": "240.00",
            "captures": [
                {
                    "id": "2GG279541U471931P",
                    "status": "COMPLETED",
                    "amount": {"currency_code": "USD", "value": "120.00"},
                    "create_time": "2026-11-05T12:00:03Z",
                },
                {
                    "id": "7K8830129L554122X",
                    "status": "COMPLETED",
                    "amount": {"currency_code": "USD", "value": "120.00"},
                    "create_time": "2026-11-05T12:00:05Z",
                },
            ],
        },
        store_record={
            "order_id": "ORD-NAIVE-001",
            "cart_id": "cart_lane1_retrier",
            "customer": "buyer_lane1@sandbox.example",
            "recorded_amount": "120.00",
            "currency": "USD",
            "status": "PAID",
            "payment_count": 1,
            "paypal_order_id": "5O190127TN364715T",
        },
        explanation=(
            "When the network connection dropped after payment, The Retrier submitted an identical checkout retry. "
            "Naive Shop did not pass or track PayPal-Request-Id, resulting in two separate $120.00 captures ($240.00 total) "
            "for a single $120.00 order."
        ),
        patch_diff=(
            "--- a/naive_checkout.py\n"
            "+++ b/naive_checkout.py\n"
            "@@ -14,6 +14,10 @@\n"
            "-    order = paypal_client.create_order(cart.total)\n"
            "-    capture = paypal_client.capture_order(order.id)\n"
            "+    idempotency_key = request.headers.get('Idempotency-Key') or cart.id\n"
            "+    existing = db.find_payment_by_key(idempotency_key)\n"
            "+    if existing:\n"
            "+        return Response(existing.payload, headers={'Idempotent-Replayed': 'true'})\n"
            "+    order = paypal_client.create_order(cart.total, paypal_request_id=idempotency_key)\n"
            "+    capture = paypal_client.capture_order(order.id, paypal_request_id=idempotency_key)\n"
            "+    db.save_payment(idempotency_key, capture)\n"
        ),
        fixed=False,
        remediation_action="refund_excess_capture_7K8830129L554122X",
    ),
    FindingDetail(
        id="find_r2_price_tampered",
        run_id="run_42_naive_shop",
        rule_number=2,
        rule_name="Right Amount",
        severity=FindingSeverity.CRITICAL,
        persona_id="the_tamperer",
        title="Under-Collected Capture from Client Price Tampering",
        evidence_ids=["3HH482019A120934M", "9LL192834K092182Q"],
        paypal_record={
            "order_id": "3HH482019A120934M",
            "custom_id": "cart_lane2_tamperer",
            "status": "COMPLETED",
            "amount": {"currency_code": "USD", "value": "1.50"},
            "capture_id": "9LL192834K092182Q",
        },
        store_record={
            "order_id": "ORD-NAIVE-002",
            "cart_id": "cart_lane2_tamperer",
            "item_title": "Velocity Carbon Running Shoes",
            "catalog_price": "150.00",
            "charged_price": "1.50",
            "loss_amount": "148.50",
            "status": "PAID",
        },
        explanation=(
            "The Tamperer modified the submitted client price from $150.00 to $1.50. "
            "Naive Shop accepted the client's submitted amount without recomputing against the authoritative "
            "server catalog, capturing only $1.50 and incurring a $148.50 loss."
        ),
        patch_diff=(
            "--- a/naive_checkout.py\n"
            "+++ b/naive_checkout.py\n"
            "@@ -28,5 +28,8 @@\n"
            "-    submitted_total = request.json.get('amount')\n"
            "-    return paypal_client.create_order(submitted_total)\n"
            "+    server_total = catalog.compute_cart_total(cart.items)\n"
            "+    submitted_total = request.json.get('amount')\n"
            "+    if abs(server_total - float(submitted_total)) > 0.001:\n"
            "+        raise ProblemException.price_mismatch(expected=str(server_total), submitted=str(submitted_total))\n"
            "+    return paypal_client.create_order(server_total)\n"
        ),
        fixed=False,
        remediation_action="void_or_request_price_differential",
    ),
    FindingDetail(
        id="find_r3_orphan_capture",
        run_id="run_42_naive_shop",
        rule_number=3,
        rule_name="No Orphan Money",
        severity=FindingSeverity.CRITICAL,
        persona_id="the_ghost_order",
        title="Orphan Capture Without Store Order or Tracking SLA",
        evidence_ids=["1AA992019B882011Z", "4BB882910C773022Y"],
        paypal_record={
            "order_id": "1AA992019B882011Z",
            "custom_id": "cart_lane6_ghost",
            "capture_id": "4BB882910C773022Y",
            "amount": {"currency_code": "USD", "value": "85.00"},
            "status": "COMPLETED",
            "tracking_number": None,
        },
        store_record={
            "order_id": None,
            "cart_id": "cart_lane6_ghost",
            "status": "UNFULFILLED_DATABASE_CRASH",
            "order_created": False,
        },
        explanation=(
            "Payment capture 4BB882910C773022Y succeeded in PayPal Sandbox, but the store backend crashed before "
            "creating an internal order record. The 8-second SLA expired without shipment tracking or auto-refund."
        ),
        patch_diff=(
            "--- a/naive_fulfillment.py\n"
            "+++ b/naive_fulfillment.py\n"
            "@@ -19,4 +19,7 @@\n"
            "-    capture = paypal_client.capture(order_id)\n"
            "-    store_order = db.create_order(capture)\n"
            "+    with db.transaction():\n"
            "+        capture = paypal_client.capture(order_id)\n"
            "+        store_order = db.create_order_or_rollback(capture)\n"
            "+    if not store_order:\n"
            "+        paypal_client.refund(capture.id, note='Orphan capture auto-reversal')\n"
        ),
        fixed=False,
        remediation_action="auto_refund_orphan_capture_4BB882910C773022Y",
    ),
    FindingDetail(
        id="find_r4_duplicate_refund",
        run_id="run_42_naive_shop",
        rule_number=4,
        rule_name="Safe Refunds",
        severity=FindingSeverity.CRITICAL,
        persona_id="the_refunder",
        title="Duplicate Partial Refund Executed Beyond Captured Total",
        evidence_ids=["6CC773829D664033X", "REF-001-ALPHA", "REF-002-BRAVO"],
        paypal_record={
            "capture_id": "6CC773829D664033X",
            "captured_amount": "100.00",
            "refunds": [
                {"id": "REF-001-ALPHA", "amount": "70.00", "status": "COMPLETED"},
                {"id": "REF-002-BRAVO", "amount": "70.00", "status": "COMPLETED"},
            ],
            "total_refunded": "140.00",
        },
        store_record={
            "order_id": "ORD-NAIVE-004",
            "captured_amount": "100.00",
            "total_refunded": "140.00",
            "net_merchant_balance": "-40.00",
        },
        explanation=(
            "The Refunder initiated two parallel $70.00 refund requests. Lacking row-level locking or refund balance "
            "checks, Naive Shop executed both refunds on PayPal, refunding $140.00 on a $100.00 transaction."
        ),
        patch_diff=(
            "--- a/naive_refund.py\n"
            "+++ b/naive_refund.py\n"
            "@@ -12,4 +12,8 @@\n"
            "-    return paypal_client.create_refund(capture_id, amount)\n"
            "+    with db.lock_order(order_id):\n"
            "+        remaining = db.get_refundable_balance(order_id)\n"
            "+        if requested_amount > remaining:\n"
            "+            raise ProblemException.refund_exceeds_capture(str(captured), str(requested_amount))\n"
            "+        return paypal_client.create_refund(capture_id, requested_amount)\n"
        ),
        fixed=False,
        remediation_action="reconcile_merchant_negative_balance",
    ),
    FindingDetail(
        id="find_r5_forged_webhook",
        run_id="run_42_naive_shop",
        rule_number=5,
        rule_name="Records Agree",
        severity=FindingSeverity.HIGH,
        persona_id="the_webhook_skeptic",
        title="Forged Webhook Accepted Without Signature Verification",
        evidence_ids=["WH-FORGED-998877", "ORD-NAIVE-005"],
        paypal_record={
            "webhook_event_id": "WH-FORGED-998877",
            "event_type": "CHECKOUT.ORDER.APPROVED",
            "paypal_verification_status": "FAILURE",
            "genuine": False,
        },
        store_record={
            "order_id": "ORD-NAIVE-005",
            "status": "PAID_VERIFIED",
            "verification_called": False,
            "security_breach": True,
        },
        explanation=(
            "The Webhook Skeptic delivered a forged CHECKOUT.ORDER.APPROVED payload with an arbitrary signature header. "
            "Naive Shop did not verify the signature via PayPal's /v1/notifications/verify-webhook-signature and "
            "marked the uncaptured order as paid."
        ),
        patch_diff=(
            "--- a/naive_webhooks.py\n"
            "+++ b/naive_webhooks.py\n"
            "@@ -10,3 +10,7 @@\n"
            "-    event = parse_json(request.body)\n"
            "-    db.mark_paid(event['resource']['id'])\n"
            "+    is_valid = paypal_client.verify_webhook_signature(request.headers, request.body)\n"
            "+    if not is_valid:\n"
            "+        raise ProblemException.webhook_signature_invalid()\n"
            "+    db.mark_paid(event['resource']['id'])\n"
        ),
        fixed=False,
        remediation_action="revoke_unverified_paid_status",
    ),
]


# -----------------------------------------------------------------------------
# 4. Hardened Shop Findings (Score: 95/100, seed=42)
# -----------------------------------------------------------------------------

MOCK_HARDENED_FINDINGS: List[FindingDetail] = [
    FindingDetail(
        id="find_r6_blackbox_ledger_unverifiable",
        run_id="run_42_hardened_shop",
        rule_number=6,
        rule_name="Proof Ready",
        severity=FindingSeverity.LOW,
        persona_id="the_disputer",
        title="Internal Order Ledger Unverifiable in Black-Box Mode",
        evidence_ids=["PP-DISPUTE-PRESEEDED-001", "ORD-HARDENED-007"],
        paypal_record={
            "dispute_id": "PP-DISPUTE-PRESEEDED-001",
            "status": "UNDER_REVIEW",
            "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            "evidence_provided": True,
            "tracking_number": "1Z9999999999999999",
        },
        store_record={
            "order_id": "ORD-HARDENED-007",
            "status": "FULFILLED",
            "probe_accessible": False,
            "ledger_proof": "UNVERIFIABLE_WITHOUT_PROBE_SECRET",
        },
        explanation=(
            "Honest limitation finding on Hardened Shop: When audited without the signed /_lab/ledger Probe endpoint secret, "
            "external reconciliation cannot cryptographically prove that the merchant's internal order record matches "
            "the signed cart receipt hash prior to settlement."
        ),
        patch_diff=(
            "--- a/hardened_config.py\n"
            "+++ b/hardened_config.py\n"
            "@@ -5,3 +5,4 @@\n"
            "+# Enable Lab Probe with shared HMAC secret for 100/100 audit grade\n"
            "+ENABLE_LAB_PROBE = True\n"
            "+LAB_PROBE_HMAC_SECRET = os.getenv('LAB_PROBE_HMAC_SECRET')\n"
        ),
        fixed=False,
        remediation_action="configure_lab_probe_hmac_secret",
    ),
]


# -----------------------------------------------------------------------------
# 5. Dual Ledger Snapshots
# -----------------------------------------------------------------------------

def get_mock_ledger_snapshot(run_id: str) -> LedgerSnapshot:
    """Returns side-by-side dual ledger snapshot comparing PayPal vs. Store records."""
    is_naive = "naive" in run_id.lower()
    target_id = "naive-shop" if is_naive else "hardened-shop"

    dual_rows = [
        DualLedgerRow(
            cart_id="cart_lane1_retrier",
            persona_id="the_retrier",
            timestamp="2026-11-05T12:00:03Z",
            paypal_order_id="5O190127TN364715T",
            paypal_capture_id="2GG279541U471931P, 7K8830129L554122X" if is_naive else "2GG279541U471931P",
            paypal_status="COMPLETED",
            paypal_amount="$240.00" if is_naive else "$120.00",
            store_order_id="ORD-001",
            store_status="PAID",
            store_amount="$120.00",
            tracking_number="1Z1111111111111111",
            has_dispute=False,
            disagreements=["Double Capture: PayPal collected $240.00 across 2 captures; store recorded $120.00"] if is_naive else [],
        ),
        DualLedgerRow(
            cart_id="cart_lane2_tamperer",
            persona_id="the_tamperer",
            timestamp="2026-11-05T12:00:04Z",
            paypal_order_id="3HH482019A120934M" if is_naive else None,
            paypal_capture_id="9LL192834K092182Q" if is_naive else None,
            paypal_status="COMPLETED" if is_naive else "BLOCKED_BEFORE_CAPTURE",
            paypal_amount="$1.50" if is_naive else "$0.00",
            store_order_id="ORD-002" if is_naive else None,
            store_status="PAID" if is_naive else "409_PRICE_MISMATCH",
            store_amount="$1.50" if is_naive else "$150.00",
            tracking_number=None,
            has_dispute=False,
            disagreements=["Amount Mismatch: Store catalog requires $150.00, but client captured $1.50"] if is_naive else [],
        ),
        DualLedgerRow(
            cart_id="cart_lane3_stale",
            persona_id="the_stale_cart",
            timestamp="2026-11-05T12:00:05Z",
            paypal_order_id="8YY992019C110923L" if is_naive else None,
            paypal_capture_id="5MM882910D221099P" if is_naive else None,
            paypal_status="COMPLETED" if is_naive else "BLOCKED_STALE_CART",
            paypal_amount="$80.00" if is_naive else "$0.00",
            store_order_id="ORD-003" if is_naive else None,
            store_status="PAID" if is_naive else "409_PRICE_MISMATCH",
            store_amount="$80.00" if is_naive else "$90.00",
            tracking_number=None,
            has_dispute=False,
            disagreements=["Stale Price: Expired cart price $80.00 honored instead of current $90.00"] if is_naive else [],
        ),
        DualLedgerRow(
            cart_id="cart_lane4_webhook",
            persona_id="the_webhook_skeptic",
            timestamp="2026-11-05T12:00:06Z",
            paypal_order_id="WH-FORGED-998877",
            paypal_capture_id=None,
            paypal_status="UNVERIFIED_FORGERY",
            paypal_amount="$0.00",
            store_order_id="ORD-004",
            store_status="PAID_VERIFIED" if is_naive else "401_SIGNATURE_INVALID",
            store_amount="$65.00" if is_naive else "$0.00",
            tracking_number=None,
            has_dispute=False,
            disagreements=["Forged Webhook: Store marked order paid on unverified webhook notification"] if is_naive else [],
        ),
        DualLedgerRow(
            cart_id="cart_lane5_refunder",
            persona_id="the_refunder",
            timestamp="2026-11-05T12:00:07Z",
            paypal_order_id="6CC773829D664033X",
            paypal_capture_id="CAP-REFUND-005",
            paypal_status="REFUNDED",
            paypal_amount="-$140.00" if is_naive else "-$70.00",
            store_order_id="ORD-005",
            store_status="REFUNDED",
            store_amount="-$140.00" if is_naive else "-$70.00",
            tracking_number=None,
            has_dispute=False,
            disagreements=["Over-Refund: $140.00 total refunds executed against $100.00 original capture"] if is_naive else [],
        ),
        DualLedgerRow(
            cart_id="cart_lane6_ghost",
            persona_id="the_ghost_order",
            timestamp="2026-11-05T12:00:08Z",
            paypal_order_id="1AA992019B882011Z",
            paypal_capture_id="4BB882910C773022Y",
            paypal_status="COMPLETED",
            paypal_amount="$85.00",
            store_order_id=None if is_naive else "ORD-006",
            store_status="MISSING_RECORD" if is_naive else "AUTO_REFUNDED",
            store_amount="$0.00" if is_naive else "$85.00",
            tracking_number=None,
            has_dispute=False,
            disagreements=["Orphan Capture: Payment captured but store order row never created within 8s SLA"] if is_naive else [],
        ),
        DualLedgerRow(
            cart_id="cart_lane7_disputer",
            persona_id="the_disputer",
            timestamp="2026-11-05T12:00:09Z",
            paypal_order_id="PP-DISPUTE-PRESEEDED-001",
            paypal_capture_id="CAP-DISPUTE-007",
            paypal_status="UNDER_DISPUTE",
            paypal_amount="$110.00",
            store_order_id="ORD-007",
            store_status="DISPUTE_EVIDENCE_SUBMITTED",
            store_amount="$110.00",
            tracking_number="1Z9999999999999999",
            has_dispute=True,
            dispute_id="PP-DISPUTE-PRESEEDED-001",
            disagreements=["Black-Box Evidence Gap: Proof not verified via signed probe endpoint"] if not is_naive else [],
        ),
        DualLedgerRow(
            cart_id="cart_lane8_misreader",
            persona_id="the_misreader",
            timestamp="2026-11-05T12:00:10Z",
            paypal_order_id=None,
            paypal_capture_id=None,
            paypal_status="NO_PAYMENT",
            paypal_amount="$0.00",
            store_order_id="ORD-008" if is_naive else None,
            store_status="CORRUPTED_BLIND_FULFILL" if is_naive else "422_AMBIGUOUS_VARIANT",
            store_amount="$75.00" if is_naive else "$0.00",
            tracking_number=None,
            has_dispute=False,
            disagreements=["Ambiguous Option: Store accepted apparel order without required size selection"] if is_naive else [],
        ),
        DualLedgerRow(
            cart_id="cart_lane9_trap",
            persona_id="the_content_trap",
            timestamp="2026-11-05T12:00:11Z",
            paypal_order_id="9ZZ881029D332011M" if is_naive else None,
            paypal_capture_id="2NN771920E443102P" if is_naive else None,
            paypal_status="COMPLETED" if is_naive else "BLOCKED_INTENT_MISMATCH",
            paypal_amount="$250.00" if is_naive else "$0.00",
            store_order_id="ORD-009" if is_naive else None,
            store_status="PAID_5_UNITS" if is_naive else "409_CART_INTENT_MISMATCH",
            store_amount="$250.00" if is_naive else "$50.00",
            tracking_number=None,
            has_dispute=False,
            disagreements=["Intent Mismatch: Prompt injection caused 5 units to be captured instead of human-approved 1 unit"] if is_naive else [],
        ),
    ]

    return LedgerSnapshot(
        run_id=run_id,
        target_id=target_id,
        snapshot_time="2026-11-05T12:00:12Z",
        settle_window_sec=5,
        probe_verified=not is_naive,
        paypal_records=[r.model_dump() for r in dual_rows],
        store_records=[{"store_order_id": r.store_order_id, "status": r.store_status, "amount": r.store_amount} for r in dual_rows],
        dual_rows=dual_rows,
    )


# -----------------------------------------------------------------------------
# 6. Run Summary Provider
# -----------------------------------------------------------------------------

def get_mock_run_findings(run_id: str) -> List[FindingDetail]:
    """Returns findings for a given run ID."""
    if "hardened" in run_id.lower():
        return MOCK_HARDENED_FINDINGS
    return MOCK_NAIVE_FINDINGS


def get_mock_run_summary(target_id: str = "naive-shop", seed: int = 42) -> RunSummary:
    """
    Returns full run summary for either Naive Shop (18/100) or Hardened Shop (95/100).
    Formula: round(100 - sum(weight[r] * failure_share[r])).
    Weights: R1:25, R2:25, R3:15, R4:10, R5:15, R6:10.
    """
    is_hardened = "hardened" in target_id.lower()

    if is_hardened:
        run_id = f"run_{seed}_hardened_shop"
        target_name = "Hardened Shop (Guard Protected)"
        score = 95
        findings = MOCK_HARDENED_FINDINGS
        crit = 0
        high = 0
        med = 0
        low = 1
        rule_scores = [
            RuleScore(rule_number=1, rule_name="Pay Once", weight=25, failed_carts=0, total_evaluated_carts=1, failure_share=0.0, rule_score=25, status="PASS"),
            RuleScore(rule_number=2, rule_name="Right Amount", weight=25, failed_carts=0, total_evaluated_carts=3, failure_share=0.0, rule_score=25, status="PASS"),
            RuleScore(rule_number=3, rule_name="No Orphan Money", weight=15, failed_carts=0, total_evaluated_carts=1, failure_share=0.0, rule_score=15, status="PASS"),
            RuleScore(rule_number=4, rule_name="Safe Refunds", weight=10, failed_carts=0, total_evaluated_carts=1, failure_share=0.0, rule_score=10, status="PASS"),
            RuleScore(rule_number=5, rule_name="Records Agree", weight=15, failed_carts=0, total_evaluated_carts=1, failure_share=0.0, rule_score=15, status="PASS"),
            RuleScore(rule_number=6, rule_name="Proof Ready", weight=10, failed_carts=1, total_evaluated_carts=2, failure_share=0.5, rule_score=5, status="PASS"),
        ]
    else:
        run_id = f"run_{seed}_naive_shop"
        target_name = "Naive Shop (Vulnerable Baseline)"
        score = 18
        findings = MOCK_NAIVE_FINDINGS
        crit = 4
        high = 1
        med = 0
        low = 0
        rule_scores = [
            RuleScore(rule_number=1, rule_name="Pay Once", weight=25, failed_carts=1, total_evaluated_carts=1, failure_share=1.0, rule_score=0, status="FAIL"),
            RuleScore(rule_number=2, rule_name="Right Amount", weight=25, failed_carts=3, total_evaluated_carts=3, failure_share=1.0, rule_score=0, status="FAIL"),
            RuleScore(rule_number=3, rule_name="No Orphan Money", weight=15, failed_carts=1, total_evaluated_carts=1, failure_share=1.0, rule_score=0, status="FAIL"),
            RuleScore(rule_number=4, rule_name="Safe Refunds", weight=10, failed_carts=1, total_evaluated_carts=5, failure_share=0.2, rule_score=8, status="FAIL"),
            RuleScore(rule_number=5, rule_name="Records Agree", weight=15, failed_carts=1, total_evaluated_carts=1, failure_share=1.0, rule_score=0, status="FAIL"),
            RuleScore(rule_number=6, rule_name="Proof Ready", weight=10, failed_carts=0, total_evaluated_carts=2, failure_share=0.0, rule_score=10, status="PASS"),
        ]

    return RunSummary(
        id=run_id,
        target=target_id,
        target_name=target_name,
        status=RunStatus.COMPLETE,
        score=score,
        seed=seed,
        policy=AutoReversalPolicy.AUTO,
        pack="full",
        created_at="2026-11-05T12:00:00Z",
        completed_at="2026-11-05T12:00:14Z",
        settle_window_sec=5,
        total_findings=len(findings),
        critical_findings=crit,
        high_findings=high,
        medium_findings=med,
        low_findings=low,
        findings=findings,
        rule_scores=rule_scores,
        badge_url=f"/v1/badge/{target_id}.svg",
        disclaimer="Score weights are AgentReady Lab's heuristic design, not an official PayPal standard or certification.",
    )


# -----------------------------------------------------------------------------
# 7. Ordered SSE Telemetry Events (Section B11 & 9-Lane Swarm)
# -----------------------------------------------------------------------------

def get_mock_run_events(target_id: str = "naive-shop", seed: int = 42) -> List[RunEvent]:
    """
    Returns the sequential stream of SSE telemetry frames for the 9-lane swarm.
    Includes agent_step, paypal_event, store_ledger_row, finding, and run_completed.
    """
    is_hardened = "hardened" in target_id.lower()
    run_id = f"run_{seed}_{'hardened_shop' if is_hardened else 'naive_shop'}"
    events: List[RunEvent] = []

    # Wave 1 (Lanes 1 to 5)
    wave1_personas = [
        (1, "the_retrier", "Buyer Agent (The Retrier)", "POST /v2/checkout/orders", "5O190127TN364715T", "$120.00"),
        (2, "the_tamperer", "Buyer Agent (The Tamperer)", "POST /v2/checkout/orders (Tampered)", "3HH482019A120934M", "$1.50" if not is_hardened else "$150.00"),
        (3, "the_stale_cart", "Buyer Agent (The Stale Cart)", "POST /v2/checkout/orders", "8YY992019C110923L", "$80.00"),
        (4, "the_webhook_skeptic", "Adversary (Webhook Skeptic)", "POST /webhooks/paypal (Forged)", "WH-FORGED-998877", "$65.00"),
        (5, "the_refunder", "Buyer Agent (The Refunder)", "POST /v2/payments/captures/refund", "6CC773829D664033X", "$70.00"),
    ]

    for lane, pid, actor, action, pid_ref, amt in wave1_personas:
        events.append(
            RunEvent(
                event="agent_step",
                run_id=run_id,
                timestamp="2026-11-05T12:00:01Z",
                lane=lane,
                persona_id=pid,
                actor=actor,
                action=action,
                paypal_id=pid_ref,
                amount=amt,
                status="DISPATCHED",
                data={"wave": 1},
            )
        )

    # Wave 1 execution results & store responses
    events.append(
        RunEvent(
            event="paypal_event",
            run_id=run_id,
            timestamp="2026-11-05T12:00:03Z",
            lane=1,
            persona_id="the_retrier",
            actor="PayPal Sandbox",
            action="CAPTURE",
            paypal_id="2GG279541U471931P",
            amount="$120.00",
            status="COMPLETED",
            rule_hit=1,
            data={"capture_id": "2GG279541U471931P"},
        )
    )

    if not is_hardened:
        # Naive shop double capture
        events.append(
            RunEvent(
                event="paypal_event",
                run_id=run_id,
                timestamp="2026-11-05T12:00:04Z",
                lane=1,
                persona_id="the_retrier",
                actor="PayPal Sandbox",
                action="REPLAY_CAPTURE (Double Charge)",
                paypal_id="7K8830129L554122X",
                amount="$120.00",
                status="COMPLETED",
                rule_hit=1,
                data={"duplicate_detected": True, "total_captured": "$240.00"},
            )
        )
        events.append(
            RunEvent(
                event="finding",
                run_id=run_id,
                timestamp="2026-11-05T12:00:05Z",
                lane=1,
                persona_id="the_retrier",
                actor="Reconciler",
                action="FLAG_RULE_VIOLATION",
                paypal_id="5O190127TN364715T",
                amount="$240.00",
                status="CRITICAL",
                rule_hit=1,
                data={"rule_name": "Pay Once", "title": "Double Capture Detected on Idempotent Replay"},
            )
        )
    else:
        events.append(
            RunEvent(
                event="store_ledger_row",
                run_id=run_id,
                timestamp="2026-11-05T12:00:04Z",
                lane=1,
                persona_id="the_retrier",
                actor="Hardened Shop",
                action="RETURN_IDEMPOTENT_CACHE",
                paypal_id="2GG279541U471931P",
                amount="$120.00",
                status="IDEMPOTENT_REPLAY_PASS",
                rule_hit=1,
                data={"header": "Idempotent-Replayed: true"},
            )
        )

    # Wave 2 (Lanes 6 to 9)
    wave2_personas = [
        (6, "the_ghost_order", "Buyer Agent (The Ghost Order)", "POST /v2/checkout/orders", "1AA992019B882011Z", "$85.00"),
        (7, "the_disputer", "Buyer Agent (The Disputer)", "POST /v1/customer/disputes", "PP-DISPUTE-PRESEEDED-001", "$110.00"),
        (8, "the_misreader", "LLM Agent (The Misreader)", "POST /v2/checkout/orders (Ambiguous)", None, "$75.00"),
        (9, "the_content_trap", "LLM Agent (The Content Trap)", "POST /v2/checkout/orders (Injected)", "9ZZ881029D332011M", "$250.00" if not is_hardened else "$50.00"),
    ]

    for lane, pid, actor, action, pid_ref, amt in wave2_personas:
        events.append(
            RunEvent(
                event="agent_step",
                run_id=run_id,
                timestamp="2026-11-05T12:00:07Z",
                lane=lane,
                persona_id=pid,
                actor=actor,
                action=action,
                paypal_id=pid_ref,
                amount=amt,
                status="DISPATCHED",
                data={"wave": 2},
            )
        )

    # Completion Event
    events.append(
        RunEvent(
            event="run_completed",
            run_id=run_id,
            timestamp="2026-11-05T12:00:14Z",
            actor="Run Orchestrator",
            action="GRADE_RUN",
            status="COMPLETE",
            amount=None,
            data={
                "score": 95 if is_hardened else 18,
                "target": target_id,
                "total_findings": 1 if is_hardened else 5,
            },
        )
    )

    return events


# -----------------------------------------------------------------------------
# 8. Markdown Report Generator
# -----------------------------------------------------------------------------

def get_mock_report_markdown(run_id: str) -> str:
    """Generates comprehensive markdown report for export."""
    is_hardened = "hardened" in run_id.lower()
    score = 95 if is_hardened else 18
    target_name = "Hardened Shop (Guard Protected)" if is_hardened else "Naive Shop (Vulnerable Baseline)"

    return f"""# AgentReady Lab — Commerce Audit Report

**Run ID:** `{run_id}`
**Target:** {target_name}
**Agent-Readiness Score:** **{score} / 100**
**Audit Mode:** Dual-Ledger Reconciled (PayPal Sandbox + Store Probe)
**Evaluation Seed:** `42`
**Evaluation Date:** 2026-11-05 12:00:14 UTC

---

## Executive Summary
{
"Hardened Shop passed 5 of 6 invariant safety rules. All automated adversarial attacks were mitigated at the checkout boundary with RFC 9457 structured errors."
if is_hardened else
"Naive Shop critically failed 5 of 6 invariant safety rules. The store demonstrated severe financial vulnerability to idempotent retries, client-side price tampering, and forged webhooks."
}

## Rule Breakdown
- **Rule 1 (Pay Once):** {'PASS (25/25 pts)' if is_hardened else 'FAIL (0/25 pts) — Double capture detected'}
- **Rule 2 (Right Amount):** {'PASS (25/25 pts)' if is_hardened else 'FAIL (0/25 pts) — Client price tampering accepted'}
- **Rule 3 (No Orphan Money):** {'PASS (15/15 pts)' if is_hardened else 'FAIL (0/15 pts) — Capture without order row or tracking'}
- **Rule 4 (Safe Refunds):** {'PASS (10/10 pts)' if is_hardened else 'FAIL (8/10 pts) — Duplicate refund exceeded original capture'}
- **Rule 5 (Records Agree):** {'PASS (15/15 pts)' if is_hardened else 'FAIL (0/15 pts) — Unverified webhook updated order to PAID'}
- **Rule 6 (Proof Ready):** {'PASS (5/10 pts) — Honest residual limitation in black-box mode' if is_hardened else 'PASS (10/10 pts)'}

> *Disclaimer: Score weights are AgentReady Lab's heuristic design, not an official PayPal standard or certification.*
"""

