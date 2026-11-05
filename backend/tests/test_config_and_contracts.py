"""
Unit and integration tests for Task 1.0A: Mock & Replay Fixture Layer + Contracts.
Verifies the isolated mock provider that powers the initial Blueprint and production Replay mode.
"""
from app.mocks.replay_fixtures import (
    get_mock_ledger_snapshot,
    get_mock_personas,
    get_mock_report_markdown,
    get_mock_run_events,
    get_mock_run_findings,
    get_mock_run_summary,
    get_mock_target,
    get_mock_targets,
)
from app.schemas.contracts import FindingSeverity, RunStatus


def test_mock_personas_coverage():
    personas = get_mock_personas()
    assert len(personas) == 9

    persona_ids = [p.id for p in personas]
    expected_ids = [
        "the_retrier",
        "the_tamperer",
        "the_stale_cart",
        "the_webhook_skeptic",
        "the_refunder",
        "the_ghost_order",
        "the_disputer",
        "the_misreader",
        "the_content_trap",
    ]
    for expected in expected_ids:
        assert expected in persona_ids

    # Check concurrency waves (Wave 1: lanes 1-5, Wave 2: lanes 6-9)
    wave1 = [p for p in personas if p.wave == 1]
    wave2 = [p for p in personas if p.wave == 2]
    assert len(wave1) == 5
    assert len(wave2) == 4

    # Check 7 fixed_script and 2 live_llm
    scripted = [p for p in personas if p.driven_by == "fixed_script"]
    llm = [p for p in personas if p.driven_by == "live_llm"]
    assert len(scripted) == 7
    assert len(llm) == 2


def test_mock_targets():
    targets = get_mock_targets()
    assert len(targets) >= 2
    assert get_mock_target("naive-shop") is not None
    assert get_mock_target("hardened-shop") is not None
    assert get_mock_target("non-existent-target") is None


def test_naive_shop_run_fixture():
    summary = get_mock_run_summary("naive-shop", seed=42)
    assert summary.status == RunStatus.COMPLETE
    assert summary.score == 18
    assert summary.seed == 42
    assert summary.total_findings == 5
    assert summary.critical_findings == 4
    assert summary.high_findings == 1
    assert "heuristic design" in summary.disclaimer

    # Verify score formula consistency: sum of rule scores == summary.score
    total_rule_points = sum(r.rule_score for r in summary.rule_scores)
    assert total_rule_points == 18

    # Verify specific findings exist with evidence IDs and patch diffs
    findings = get_mock_run_findings(summary.id)
    finding_titles = [f.title for f in findings]
    assert any("Double Capture" in t for t in finding_titles)
    assert any("Price Tampering" in t for t in finding_titles)
    assert any("Orphan Capture" in t for t in finding_titles)
    assert any("Duplicate Partial Refund" in t for t in finding_titles)
    assert any("Forged Webhook" in t for t in finding_titles)

    for f in findings:
        assert len(f.evidence_ids) > 0
        assert f.patch_diff is not None
        assert "@@" in f.patch_diff
        assert f.explanation != ""


def test_hardened_shop_run_fixture():
    summary = get_mock_run_summary("hardened-shop", seed=42)
    assert summary.status == RunStatus.COMPLETE
    assert summary.score == 95
    assert summary.seed == 42
    assert summary.total_findings == 1
    assert summary.low_findings == 1
    assert summary.critical_findings == 0

    # Verify score formula consistency: sum of rule scores == summary.score
    total_rule_points = sum(r.rule_score for r in summary.rule_scores)
    assert total_rule_points == 95

    # Verify honest residual limitation finding
    findings = get_mock_run_findings(summary.id)
    assert len(findings) == 1
    assert findings[0].severity == FindingSeverity.LOW
    assert findings[0].rule_number == 6
    assert "Black-Box Mode" in findings[0].title


def test_dual_ledger_snapshot():
    naive_snap = get_mock_ledger_snapshot("run_42_naive_shop")
    assert naive_snap.run_id == "run_42_naive_shop"
    assert len(naive_snap.dual_rows) == 9
    assert naive_snap.settle_window_sec == 5
    # Naive shop has multiple detected discrepancies
    disagreements = [d for r in naive_snap.dual_rows for d in r.disagreements]
    assert len(disagreements) > 0

    hardened_snap = get_mock_ledger_snapshot("run_42_hardened_shop")
    assert hardened_snap.probe_verified is True
    assert len(hardened_snap.dual_rows) == 9


def test_sse_telemetry_events():
    events = get_mock_run_events("naive-shop", seed=42)
    assert len(events) > 5

    event_types = [e.event for e in events]
    assert "agent_step" in event_types
    assert "paypal_event" in event_types
    assert "finding" in event_types
    assert "run_completed" in event_types

    completion = [e for e in events if e.event == "run_completed"][0]
    assert completion.data["score"] == 18

    hardened_events = get_mock_run_events("hardened-shop", seed=42)
    hardened_completion = [e for e in hardened_events if e.event == "run_completed"][0]
    assert hardened_completion.data["score"] == 95


def test_report_markdown_generation():
    md_naive = get_mock_report_markdown("run_42_naive_shop")
    assert "# AgentReady Lab — Commerce Audit Report" in md_naive
    assert "18 / 100" in md_naive
    assert "Pay Once" in md_naive

    md_hardened = get_mock_report_markdown("run_42_hardened_shop")
    assert "95 / 100" in md_hardened

