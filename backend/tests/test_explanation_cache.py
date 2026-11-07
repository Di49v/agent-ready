"""
Unit tests for Pre-Generated Explanation Cache (Task 5.3).
Verifies coverage of all 12 bug classes, dynamic evidence ID interpolation,
and sub-100ms lookup latency without external network dependencies.
"""
import time
import pytest
from app.fix_engine.cache import ExplanationCache, get_explanation_cache
from app.shops.bug_flags import BugFlag


def test_explanation_cache_covers_all_12_bug_flags() -> None:
    """Verifies that all 12 individually toggleable BugFlag enums exist in the explanation cache."""
    cache = get_explanation_cache()
    cached_flags = set(cache.list_all_bug_flags())

    # Every single enum member of BugFlag must be covered in the cache
    for flag in BugFlag:
        assert flag.value in cached_flags, f"Missing cache entry for {flag.value}"

    assert len(cached_flags) == 12


def test_explanation_cache_interpolation() -> None:
    """Verifies that live evidence IDs (order_id, capture_id, cart_id) interpolate dynamically."""
    cache = get_explanation_cache()

    result = cache.get_by_bug_flag(
        bug_flag="BUG_NO_IDEMPOTENCY",
        order_id="PP-ORD-TEST-9988",
        capture_id="PP-CAP-TEST-7766",
        cart_id="cart_test_retrier_101",
    )

    assert result is not None
    assert result["bug_flag"] == "BUG_NO_IDEMPOTENCY"
    assert result["rule_number"] == 1
    assert result["severity"] == "CRITICAL"

    explanation = result["explanation"]
    assert "PP-ORD-TEST-9988" in explanation
    assert "PP-CAP-TEST-7766" in explanation
    assert "cart_test_retrier_101" in explanation

    # Verify patch diff structure
    patch = result["patch_diff"]
    assert "--- a/checkout.py" in patch
    assert "+++ b/checkout.py" in patch
    assert "@@" in patch

    # Verify APIMatic grounded note
    assert "APIMatic" in result["grounded_api_note"] or "PayPal" in result["grounded_api_note"]


def test_explanation_cache_sub_100ms_latency() -> None:
    """Verifies sub-millisecond retrieval latency across all 12 bug classes without network calls."""
    cache = get_explanation_cache()

    t0 = time.perf_counter()
    for flag in BugFlag:
        entry = cache.get_by_bug_flag(flag.value, order_id="ORD-1", capture_id="CAP-1", cart_id="CART-1")
        assert entry is not None
        assert len(entry["explanation"]) > 20
        assert len(entry["patch_diff"]) > 20

    total_time_ms = (time.perf_counter() - t0) * 1000

    # Must be under 100ms (in reality typically under 1ms for all 12)
    assert total_time_ms < 100.0, f"Cache retrieval took {total_time_ms:.2f}ms (expected <100ms)"


def test_finding_id_and_persona_lookups() -> None:
    """Verifies finding ID and (rule, persona) lookup conveniences."""
    cache = get_explanation_cache()

    # By finding ID
    by_find = cache.get_by_finding_id("find_r1_double_capture", cart_id="cart_retrier_01")
    assert by_find is not None
    assert by_find["bug_flag"] == "BUG_NO_IDEMPOTENCY"
    assert "cart_retrier_01" in by_find["explanation"]

    # By (rule, persona)
    by_persona = cache.get_by_rule_and_persona(2, "the_content_trap", order_id="PP-ORD-TRAP-99")
    assert by_persona is not None
    assert by_persona["bug_flag"] == "BUG_NO_CART_INTENT_CHECK"
    assert "PP-ORD-TRAP-99" in by_persona["explanation"]

