"""
Unit tests for Task 0.2: Core JSON Contracts, RFC 9457 Problem Details, and Config.
"""
import os
import pytest
from app.core.config import get_settings
from app.schemas.contracts import (
    AutoReversalPolicy,
    CartItem,
    CartReceipt,
    FindingDetail,
    FindingSeverity,
    LedgerSnapshot,
    PersonaSpec,
    RuleScore,
    RunCreateRequest,
    RunEvent,
    RunStatus,
    RunSummary,
    TargetStore,
)
from app.schemas.problem_details import (
    ProblemDetails,
    ProblemErrorCode,
    ProblemException,
)


def test_config_use_mock_blueprint_present():
    settings = get_settings()
    assert hasattr(settings, "USE_MOCK_BLUEPRINT")
    assert hasattr(settings, "use_mock_blueprint")
    assert settings.use_mock_blueprint is True


def test_gemini_key_sharder_import_and_fallback():
    from app.core.key_shard import get_sharded_gemini_key
    idx, key = get_sharded_gemini_key()
    assert isinstance(idx, int)
    assert isinstance(key, str)
    assert len(key) > 0


def test_rfc9457_problem_details_model():
    prob = ProblemDetails(
        type="https://lab.example/errors/price-mismatch",
        title="Submitted amount does not match current price",
        status=409,
        code=ProblemErrorCode.PRICE_MISMATCH_REAUTHORIZATION_REQUIRED,
        retryable=False,
        next_action="ask_user_to_confirm_new_price",
        details={"expected_amount": "48.00", "submitted_amount": "40.00", "currency": "USD"},
    )
    dumped = prob.model_dump(exclude_none=True)
    assert dumped["status"] == 409
    assert dumped["code"] == "PRICE_MISMATCH_REAUTHORIZATION_REQUIRED"
    assert dumped["details"]["expected_amount"] == "48.00"
    assert dumped["retryable"] is False


def test_problem_exception_factories():
    # Price mismatch factory
    exc = ProblemException.price_mismatch(expected="120.00", submitted="1.50", currency="USD")
    assert exc.status == 409
    assert exc.problem.code == ProblemErrorCode.PRICE_MISMATCH_REAUTHORIZATION_REQUIRED
    assert exc.problem.details["submitted_amount"] == "1.50"

    # Ambiguous variant factory
    exc_var = ProblemException.ambiguous_variant(
        product_id="shoe-01", valid_options=["S", "M", "L"], missing_attribute="size"
    )
    assert exc_var.status == 422
    assert exc_var.problem.code == ProblemErrorCode.AMBIGUOUS_VARIANT_CLARIFICATION_REQUIRED

    # Cart intent mismatch factory
    exc_cart = ProblemException.cart_intent_mismatch(
        expected_hash="hash_a", received_hash="hash_b"
    )
    assert exc_cart.status == 409
    assert exc_cart.problem.code == ProblemErrorCode.CART_INTENT_MISMATCH

    # Webhook signature invalid factory
    exc_wh = ProblemException.webhook_signature_invalid()
    assert exc_wh.status == 401
    assert exc_wh.problem.code == ProblemErrorCode.WEBHOOK_SIGNATURE_INVALID

    # Refund exceeds capture factory
    exc_ref = ProblemException.refund_exceeds_capture(
        captured_amount="100.00", requested_amount="120.00"
    )
    assert exc_ref.status == 422
    assert exc_ref.problem.code == ProblemErrorCode.REFUND_EXCEEDS_CAPTURE


def test_target_store_and_persona_spec():
    target = TargetStore(
        id="naive-shop",
        name="Naive Shop",
        base_url="http://localhost:8000/demo/naive",
        mode="probe",
        probe_url="http://localhost:8000/demo/naive/_lab/ledger",
    )
    assert target.id == "naive-shop"
    assert target.mode == "probe"

    persona = PersonaSpec(
        id="the_retrier",
        name="The Retrier",
        plain_words="Connection drops after paying, then it tries again",
        rule_number=1,
        rule_name="Pay Once",
        driven_by="fixed_script",
        fault_description="Drops HTTP response after successful capture and replays identical request",
        expected_behavior="Store must return original result with Idempotent-Replayed true",
        wave=1,
    )
    assert persona.rule_number == 1
    assert persona.wave == 1


def test_cart_receipt_and_ledger_snapshot():
    receipt = CartReceipt(
        receipt_id="rcpt_001",
        cart_id="cart_42",
        items=[
            CartItem(item_id="sku_shoe_1", title="Velocity Shoes", unit_price="120.00", quantity=1)
        ],
        currency="USD",
        total_amount="120.00",
        client_timestamp="2026-11-05T12:00:00Z",
        cart_hash="sha256_dummy_hash",
    )
    assert receipt.cart_id == "cart_42"
    assert receipt.items[0].quantity == 1

    snapshot = LedgerSnapshot(
        run_id="run_001",
        target_id="naive-shop",
        snapshot_time="2026-11-05T12:00:05Z",
        settle_window_sec=5,
        probe_verified=True,
    )
    assert snapshot.settle_window_sec == 5
    assert len(snapshot.dual_rows) == 0


def test_finding_detail_and_run_summary():
    finding = FindingDetail(
        id="find_r1_double_capture",
        rule_number=1,
        rule_name="Pay Once",
        severity=FindingSeverity.CRITICAL,
        persona_id="the_retrier",
        title="Double Capture Detected",
        evidence_ids=["5O190127TN364715T", "2GG279541U471931P"],
        paypal_record={"captured_total": "240.00", "captures_count": 2},
        store_record={"order_id": "ORD-123", "recorded_amount": "120.00"},
        explanation="Store captured payment twice when buyer agent retried.",
        patch_diff="@@ -10,3 +10,6 @@\n+ store_idempotency_key(key)",
    )
    assert finding.severity == FindingSeverity.CRITICAL
    assert len(finding.evidence_ids) == 2

    summary = RunSummary(
        id="run_001",
        target="naive-shop",
        target_name="Naive Shop",
        status=RunStatus.COMPLETE,
        score=18,
        seed=42,
        policy=AutoReversalPolicy.AUTO,
        created_at="2026-11-05T12:00:00Z",
        total_findings=1,
        critical_findings=1,
        findings=[finding],
        rule_scores=[
            RuleScore(
                rule_number=1,
                rule_name="Pay Once",
                weight=25,
                failed_carts=1,
                total_evaluated_carts=1,
                failure_share=1.0,
                rule_score=0,
                status="FAIL",
            )
        ],
    )
    assert summary.score == 18
    assert summary.findings[0].rule_number == 1


def test_run_event_sse_payload():
    event = RunEvent(
        event="agent_step",
        run_id="run_001",
        timestamp="2026-11-05T12:00:01Z",
        lane=1,
        persona_id="the_retrier",
        actor="Buyer Agent (The Retrier)",
        action="POST /v2/checkout/orders",
        paypal_id="5O190127TN364715T",
        amount="$120.00",
        status="COMPLETED",
        rule_hit=1,
        data={"idempotency_replayed": False},
    )
    assert event.event == "agent_step"
    assert event.lane == 1
    assert event.paypal_id == "5O190127TN364715T"


def test_openapi_yaml_exists():
    openapi_path = os.path.join(os.path.dirname(__file__), "..", "..", "openapi", "openapi.yaml")
    assert os.path.exists(openapi_path)
    with open(openapi_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "openapi: 3.1.0" in content
    assert "/v1/runs" in content
    assert "/v1/personas" in content
    assert "/v1/runs/{id}/events" in content
    assert "ProblemDetails" in content

