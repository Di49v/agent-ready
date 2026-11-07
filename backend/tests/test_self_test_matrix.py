"""
Unit tests for the 12-Bug Self-Test Benchmark Matrix runner.
Verifies that BenchmarkMatrixRunner tests each of the 12 bug flags,
yielding 12/12 True Positives on NaiveShop and 0 False Alarms on HardenedShop.
"""
import pytest
from scripts.run_self_test_matrix import BenchmarkMatrixRunner
from app.shops.bug_flags import BugFlag


@pytest.mark.asyncio
async def test_benchmark_matrix_runs_all_12_flags() -> None:
    """Verifies that BenchmarkMatrixRunner evaluates all 12 BugFlag members."""
    runner = BenchmarkMatrixRunner()
    results = await runner.run_all()

    assert len(results) == 12
    flag_names = {r.bug_flag for r in results}
    for flag in BugFlag:
        assert flag.value in flag_names


@pytest.mark.asyncio
async def test_benchmark_matrix_true_positives_and_zero_false_alarms() -> None:
    """Verifies 12/12 True Positives on NaiveShop and 0 False Alarms on HardenedShop."""
    runner = BenchmarkMatrixRunner()
    results = await runner.run_all()

    for row in results:
        assert row.naive_detected is True, f"Failed True Positive for {row.bug_flag}: {row.naive_evidence}"
        assert row.hardened_guarded is True, f"Failed 0 False Alarm for {row.bug_flag}: {row.hardened_evidence}"
        assert row.rule_number in (1, 2, 3, 4, 5, 6)
        assert row.duration_ms >= 0.0

    true_positives = sum(1 for r in results if r.naive_detected)
    false_alarms = sum(1 for r in results if not r.hardened_guarded)

    assert true_positives == 12
    assert false_alarms == 0


@pytest.mark.asyncio
async def test_benchmark_matrix_markdown_and_terminal_generation() -> None:
    """Verifies that terminal output and markdown tables format properly."""
    runner = BenchmarkMatrixRunner()
    results = await runner.run_all()

    terminal_out = runner.format_terminal_output(results)
    assert "AGENTREADY LAB - 12-BUG SELF-TEST BENCHMARK MATRIX" in terminal_out
    assert "12/12 True Positives, 0 False Alarms" in terminal_out

    markdown_out = runner.generate_markdown_table(results)
    assert "| # | Bug Flag | Rule | Invariant |" in markdown_out
    assert "🟢 100% True Positive" in markdown_out
    assert "**Benchmark Verdict:** `12/12 True Positives, 0 False Alarms`" in markdown_out

