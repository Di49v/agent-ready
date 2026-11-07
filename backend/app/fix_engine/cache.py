"""
Pre-Generated Explanation Cache for the 12 Bug Classes (Section B3.8 / Task 5.3).
Provides sub-5ms instant retrieval of grounded explanations, APIMatic API notes,
and unified git diff patches, interpolating live order, capture, and cart IDs at runtime.
"""
import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger("agentready.fix_engine.cache")

CACHE_FILE_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "data", "explanation_cache.json")
)

# Mapping from canonical finding IDs to BugFlag identifiers
FINDING_ID_TO_BUG_FLAG: Dict[str, str] = {
    "find_r1_double_capture": "BUG_NO_IDEMPOTENCY",
    "find_r2_price_tampered": "BUG_TRUST_CLIENT_PRICE",
    "find_r2_stale_price_drift": "BUG_STALE_CART",
    "find_r2_cart_intent_mismatch": "BUG_NO_CART_INTENT_CHECK",
    "find_r2_ambiguous_variant": "BUG_ALLOW_AMBIGUOUS_VARIANT",
    "find_r3_orphan_capture": "BUG_NO_FULFILLMENT_RECORD",
    "find_r3_missing_tracking": "BUG_NO_SHIPMENT_TRACKING",
    "find_r4_over_refund": "BUG_OVER_REFUND",
    "find_r4_duplicate_refund": "BUG_DOUBLE_REFUND",
    "find_r5_forged_webhook_accepted": "BUG_NO_WEBHOOK_VERIFY",
    "find_r5_replayed_webhook": "BUG_WEBHOOK_REPLAY_VULN",
    "find_r6_missing_tracking_proof": "BUG_MISSING_DISPUTE_PROOF",
}

# Mapping from (rule_number, persona_id) to BugFlag identifiers
RULE_PERSONA_TO_BUG_FLAG: Dict[tuple[int, str], str] = {
    (1, "the_retrier"): "BUG_NO_IDEMPOTENCY",
    (2, "the_tamperer"): "BUG_TRUST_CLIENT_PRICE",
    (2, "the_stale_cart"): "BUG_STALE_CART",
    (2, "the_misreader"): "BUG_ALLOW_AMBIGUOUS_VARIANT",
    (2, "the_content_trap"): "BUG_NO_CART_INTENT_CHECK",
    (3, "the_ghost_order"): "BUG_NO_FULFILLMENT_RECORD",
    (4, "the_refunder"): "BUG_OVER_REFUND",
    (5, "the_webhook_skeptic"): "BUG_NO_WEBHOOK_VERIFY",
    (6, "the_disputer"): "BUG_MISSING_DISPUTE_PROOF",
}


class ExplanationCache:
    """
    In-memory cache for pre-generated explanations and diffs covering all 12 bug flags.
    Guarantees sub-5ms lookup without network dependency on external LLM services.
    """

    def __init__(self, file_path: str = CACHE_FILE_PATH) -> None:
        self.file_path = file_path
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.load_cache()

    def load_cache(self) -> None:
        """Loads cached explanations from JSON file."""
        if not os.path.exists(self.file_path):
            logger.warning("Explanation cache file not found at %s", self.file_path)
            return
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self._cache = json.load(f)
            logger.info("Loaded %d pre-generated bug explanations from cache.", len(self._cache))
        except Exception as exc:
            logger.error("Failed to load explanation cache: %s", exc)

    def _interpolate(
        self,
        template_str: str,
        order_id: Optional[str] = None,
        capture_id: Optional[str] = None,
        cart_id: Optional[str] = None,
        amount: Optional[str] = None,
    ) -> str:
        """Replaces template variables with live runtime evidence IDs."""
        res = template_str
        res = res.replace("{order_id}", order_id or "PP-ORD-EVIDENCE")
        res = res.replace("{capture_id}", capture_id or "PP-CAP-EVIDENCE")
        res = res.replace("{cart_id}", cart_id or "cart_active")
        res = res.replace("{amount}", amount or "$100.00")
        return res

    def get_by_bug_flag(
        self,
        bug_flag: str,
        order_id: Optional[str] = None,
        capture_id: Optional[str] = None,
        cart_id: Optional[str] = None,
        amount: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves explanation and patch diff for a given BugFlag,
        interpolating live order and capture evidence IDs.
        """
        item = self._cache.get(bug_flag)
        if not item:
            return None

        interpolated_explanation = self._interpolate(
            item.get("template_explanation", ""),
            order_id=order_id,
            capture_id=capture_id,
            cart_id=cart_id,
            amount=amount,
        )

        return {
            "bug_flag": bug_flag,
            "rule_number": item.get("rule_number", 1),
            "rule_name": item.get("rule_name", "Compliance Rule"),
            "title": item.get("title", ""),
            "severity": item.get("severity", "HIGH"),
            "explanation": interpolated_explanation,
            "grounded_api_note": item.get("grounded_api_note", ""),
            "patch_diff": item.get("patch_diff", ""),
            "remediation_action": item.get("remediation_action", ""),
        }

    def get_by_finding_id(
        self,
        finding_id: str,
        order_id: Optional[str] = None,
        capture_id: Optional[str] = None,
        cart_id: Optional[str] = None,
        amount: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieves cached explanation by finding ID."""
        bug_flag = FINDING_ID_TO_BUG_FLAG.get(finding_id)
        if bug_flag:
            return self.get_by_bug_flag(
                bug_flag,
                order_id=order_id,
                capture_id=capture_id,
                cart_id=cart_id,
                amount=amount,
            )
        return None

    def get_by_rule_and_persona(
        self,
        rule_number: int,
        persona_id: str,
        order_id: Optional[str] = None,
        capture_id: Optional[str] = None,
        cart_id: Optional[str] = None,
        amount: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieves cached explanation by rule number and persona ID."""
        bug_flag = RULE_PERSONA_TO_BUG_FLAG.get((rule_number, persona_id))
        if bug_flag:
            return self.get_by_bug_flag(
                bug_flag,
                order_id=order_id,
                capture_id=capture_id,
                cart_id=cart_id,
                amount=amount,
            )
        return None

    def list_all_bug_flags(self) -> List[str]:
        """Returns list of all cached bug flags."""
        return list(self._cache.keys())


_global_cache: Optional[ExplanationCache] = None


def get_explanation_cache() -> ExplanationCache:
    """Returns singleton instance of ExplanationCache."""
    global _global_cache
    if _global_cache is None:
        _global_cache = ExplanationCache()
    return _global_cache

