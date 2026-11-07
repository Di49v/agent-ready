"""
Unit tests for Fix Engine & Re-Run Verification Loop (Task 5.2).
Verifies APIMatic-grounded code diff templates, root-cause explanation enrichment,
and the Red-to-Green judge demo re-run verification loop.
"""
import pytest
from app.core.config import get_settings
from app.fix_engine.explainer import FixExplainer, get_fix_explainer
from app.fix_engine.templates import (
    BugClass,
    TEMPLATES,
    get_patch_diff,
    get_template_for_rule,
)
from app.schemas.contracts import (
    AutoReversalPolicy,
    FindingDetail,
    FindingSeverity,
    RunCreateRequest,
)
from app.services.run_orchestrator import RunOrchestrator


def test_fix_engine_templates_grounded() -> None:
    """Verifies that all 6 bug-class patch templates exist and contain valid unified git diffs."""
    expected_classes = [
        BugClass.IDEMPOTENCY_PERSISTENCE,
        BugClass.SERVER_PRICE_AUTHORITY,
        BugClass.FULFILLMENT_TRACKING_HOOK,
        BugClass.REFUND_BALANCE_GUARD,
        BugClass.WEBHOOK_SIGNATURE_VERIFICATION,
        BugClass.CART_INTENT_VERIFICATION,
        BugClass.PROBE_SECRET_CONFIG,
    ]

    for bug in expected_classes:
        assert bug in TEMPLATES
        tmpl = TEMPLATES[bug]
        assert "patch" in tmpl
        assert "--- a/" in tmpl["patch"]
        assert "+++ b/" in tmpl["patch"]
        assert "@@" in tmpl["patch"]
        assert "grounded_api" in tmpl

    # Test template lookup by rule number
    assert get_template_for_rule(1)["file"] == "checkout.py"
    assert get_template_for_rule(2, "the_content_trap")["file"] == "acp_sessions.py"
    assert get_template_for_rule(3)["file"] == "fulfillment.py"
    assert get_template_for_rule(4)["file"] == "refund.py"
    assert get_template_for_rule(5)["file"] == "webhooks.py"
    assert get_template_for_rule(6, "the_disputer")["file"] == "hardened_config.py"


@pytest.mark.asyncio
async def test_fix_explainer_fallback_and_enrichment() -> None:
    """Verifies that FixExplainer enriches findings with evidence IDs and unified diffs."""
    explainer = get_fix_explainer()

    raw_finding = FindingDetail(
        id="find_r1_double_capture",
        rule_number=1,
        rule_name="Pay Once",
        severity=FindingSeverity.CRITICAL,
        persona_id="the_retrier",
        title="Double Capture from Idempotency Failure",
        evidence_ids=["PP-CAP-RETRIER-9988"],
        explanation="Short ungrounded description",
    )

    enriched = await explainer.explain_finding(raw_finding)

    assert enriched.patch_diff is not None
    assert "--- a/checkout.py" in enriched.patch_diff
    assert "Idempotency-Key" in enriched.patch_diff or "PayPal-Request-Id" in enriched.patch_diff
    assert "PP-CAP-RETRIER-9988" in enriched.explanation or "Idempotency" in enriched.explanation


@pytest.mark.asyncio
async def test_rerun_verification_loop_red_to_green() -> None:
    """
    Verifies that running Naive Shop produces low compliance score with fix patches,
    and re-running the same seed on Hardened Shop raises score to 95/100 (Red to Green).
    """
    settings = get_settings()
    settings.USE_MOCK_BLUEPRINT = False

    orchestrator = RunOrchestrator()

    # 1. Initial run against Naive Shop (Red)
    naive_req = RunCreateRequest(
        target="naive-shop",
        pack="nine_test_dummies",
        seed=42,
        policy=AutoReversalPolicy.AUTO,
    )
    naive_run = await orchestrator.create_run(naive_req)

    assert naive_run.score is not None
    assert naive_run.score < 25  # High failure rate on vulnerable NaiveShop
    assert len(naive_run.findings) >= 3

    # Every finding on Naive Shop should have a patch diff attached by the Fix Engine
    for finding in naive_run.findings:
        assert finding.patch_diff is not None
        assert "--- a/" in finding.patch_diff

    # 2. Re-run same seed against Hardened Shop (Green!)
    rerun_summary = await orchestrator.rerun_run(
        base_run_id=naive_run.id,
        target_override="hardened-shop",
    )

    assert rerun_summary.target == "hardened-shop"
    assert rerun_summary.score in (95, 100)  # Red turns Green!
    assert rerun_summary.critical_findings == 0
    assert rerun_summary.high_findings == 0

    # Reset setting
    settings.USE_MOCK_BLUEPRINT = True

