"""
Unit tests for the Dual-Ledger Reconciler, 6-Rule Grader, and Remediation Engine.
Verifies Section B3.6 reconciliation, deterministic 0-100 scoring formula,
severity ranking, and OBSERVE/ASSIST/AUTO remediation policies.
"""
import pytest
from app.reconciler.collector import DualLedgerCollector
from app.reconciler.grader import RuleGrader
from app.reconciler.remediation import RemediationEngine
from app.schemas.contracts import AutoReversalPolicy, FindingSeverity
from app.services.swarm_engine import SwarmEngine
from app.shops.hardened_shop import HardenedShop
from app.shops.naive_shop import NaiveShop


@pytest.mark.asyncio
async def test_collector_dual_ledger_generation() -> None:
    """Verifies that DualLedgerCollector normalizes PayPal and Store records with discrepancy tracking."""
    swarm = SwarmEngine()
    naive_shop = NaiveShop()
    res = await swarm.execute_swarm("naive-shop")

    collector = DualLedgerCollector(settle_window_sec=0)
    snapshot = await collector.collect(
        run_id=res.run_id,
        target_id="naive-shop",
        shop=naive_shop,
        lane_results=res.lane_results,
        skip_sleep=True,
    )

    assert snapshot.run_id == res.run_id
    assert snapshot.target_id == "naive-shop"
    assert len(snapshot.dual_rows) == 9

    # Verify disagreements were detected for exploited lanes
    disagreements_found = [row.disagreements for row in snapshot.dual_rows if row.disagreements]
    assert len(disagreements_found) >= 4


@pytest.mark.asyncio
async def test_rule_grader_on_naive_shop() -> None:
    """Verifies that RuleGrader fails vulnerable rules and sorts findings by severity."""
    swarm = SwarmEngine()
    res = await swarm.execute_swarm("naive-shop")

    collector = DualLedgerCollector(settle_window_sec=0)
    snapshot = await collector.collect(
        run_id=res.run_id,
        target_id="naive-shop",
        shop=NaiveShop(),
        lane_results=res.lane_results,
        skip_sleep=True,
    )

    grader = RuleGrader()
    score, rule_scores, findings = grader.grade(
        snapshot=snapshot,
        lane_results=res.lane_results,
        run_id=res.run_id,
    )

    # Score on Naive Shop should be heavily penalized (below 30/100)
    assert score <= 30
    assert len(rule_scores) == 6

    # Critical findings must be present
    severities = [f.severity for f in findings]
    assert FindingSeverity.CRITICAL in severities
    assert FindingSeverity.HIGH in severities

    # Deterministic severity order: CRITICAL before HIGH before MEDIUM before LOW
    prev_weight = 0
    sev_map = {FindingSeverity.CRITICAL: 1, FindingSeverity.HIGH: 2, FindingSeverity.MEDIUM: 3, FindingSeverity.LOW: 4}
    for f in findings:
        curr_weight = sev_map[f.severity]
        assert curr_weight >= prev_weight
        prev_weight = curr_weight


@pytest.mark.asyncio
async def test_rule_grader_on_hardened_shop_with_honest_residual() -> None:
    """Verifies that HardenedShop scores 95/100 in black-box mode with the honest residual finding."""
    swarm = SwarmEngine()
    res = await swarm.execute_swarm("hardened-shop")

    collector = DualLedgerCollector(settle_window_sec=0)
    snapshot = await collector.collect(
        run_id=res.run_id,
        target_id="hardened-shop",
        shop=HardenedShop(),
        lane_results=res.lane_results,
        is_black_box=True,
        skip_sleep=True,
    )

    grader = RuleGrader()
    score, rule_scores, findings = grader.grade(
        snapshot=snapshot,
        lane_results=res.lane_results,
        run_id=res.run_id,
        is_black_box=True,
    )

    # Hardened Shop achieves 95/100 due to 50% Rule 6 black-box proof deduction (5 points)
    assert score == 95
    assert len(findings) == 1
    assert findings[0].id == "find_r6_blackbox_ledger_unverifiable"
    assert findings[0].severity == FindingSeverity.LOW

    # Rules 1 to 5 must all have status == 'PASS'
    for rs in rule_scores[:5]:
        assert rs.status == "PASS"
        assert rs.failure_share == 0.0


@pytest.mark.asyncio
async def test_remediation_engine_policies() -> None:
    """Verifies OBSERVE, ASSIST, and AUTO remediation policies on audit findings."""
    swarm = SwarmEngine()
    res = await swarm.execute_swarm("naive-shop")

    collector = DualLedgerCollector(settle_window_sec=0)
    snapshot = await collector.collect(
        run_id=res.run_id,
        target_id="naive-shop",
        shop=NaiveShop(),
        lane_results=res.lane_results,
        skip_sleep=True,
    )

    grader = RuleGrader()
    _, _, findings = grader.grade(snapshot=snapshot, lane_results=res.lane_results, run_id=res.run_id)
    assert len(findings) > 0

    remediation = RemediationEngine()
    dummy_shop = NaiveShop()

    # 1. OBSERVE: Alerts only, no reversal executed
    observe_results = await remediation.execute_remediation(findings, AutoReversalPolicy.OBSERVE, dummy_shop)
    for r in observe_results:
        assert r["status"] == "OBSERVED_ALERT_DISPATCHED"

    # 2. ASSIST: Recommendations prepared for merchant approval
    assist_results = await remediation.execute_remediation(findings, AutoReversalPolicy.ASSIST, dummy_shop)
    for r in assist_results:
        assert r["status"] == "RECOMMENDED_FOR_MERCHANT_APPROVAL"
        assert r["details"]["can_execute"] is True

    # 3. AUTO: Automatic Sandbox reversals executed
    auto_results = await remediation.execute_remediation(findings, AutoReversalPolicy.AUTO, dummy_shop)
    statuses = {r["status"] for r in auto_results}
    assert any("AUTO_REVERSED" in s or "AUTO_STATUS" in s for s in statuses)

