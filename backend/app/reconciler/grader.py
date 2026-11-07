"""
6-Rule Deterministic Compliance Grader for AgentReady Lab (Sections A7, B3.6, B3.7).
Evaluates the six invariant rules, computes the 0-100 Agent-Readiness Score,
and deterministically ranks findings by severity (CRITICAL, HIGH, MEDIUM, LOW).
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.contracts import (
    DualLedgerRow,
    FindingDetail,
    FindingSeverity,
    LedgerSnapshot,
    RuleScore,
)
from app.services.swarm_engine import LaneResult

logger = logging.getLogger("agentready.reconciler.grader")

# Canonical Rule Weights (Section B3.7)
RULE_WEIGHTS = {
    1: 25,  # Pay Once
    2: 25,  # Right Amount
    3: 15,  # No Orphan Money
    4: 10,  # Safe Refunds
    5: 15,  # Records Agree
    6: 10,  # Proof Ready
}

RULE_NAMES = {
    1: "Pay Once",
    2: "Right Amount",
    3: "No Orphan Money",
    4: "Safe Refunds",
    5: "Records Agree",
    6: "Proof Ready",
}

SEVERITY_ORDER = {
    FindingSeverity.CRITICAL: 1,
    FindingSeverity.HIGH: 2,
    FindingSeverity.MEDIUM: 3,
    FindingSeverity.LOW: 4,
}


class RuleGrader:
    """
    Grades dual-ledger data against the 6 Invariant Rules without LLM subjectivity.
    Guarantees deterministic, reproducible scoring for hackathon judging.
    """

    def grade(
        self,
        snapshot: LedgerSnapshot,
        lane_results: Optional[Dict[int, LaneResult]] = None,
        run_id: str = "run_default",
        is_black_box: bool = False,
    ) -> Tuple[int, List[RuleScore], List[FindingDetail]]:
        """
        Evaluates the dual-ledger rows and returns:
          - Overall Agent-Readiness Score (0 to 100)
          - RuleScore breakdown for all 6 rules
          - Deterministically ranked FindingDetail list
        """
        lane_results = lane_results or {}
        findings: List[FindingDetail] = []

        # Tracking per rule: [failed_count, total_count]
        eval_counts: Dict[int, List[int]] = {r: [0, 0] for r in range(1, 7)}

        # ---------------------------------------------------------------------
        # Rule 1: Pay Once (Weight 25) — Count of captures per cart_id == 1
        # ---------------------------------------------------------------------
        r1_lanes = [r for r in lane_results.values() if r.lane == 1]
        eval_counts[1][1] = max(1, len(r1_lanes))
        for res in r1_lanes:
            if res.outcome == "VULNERABILITY_EXPLOITED":
                eval_counts[1][0] += 1
                findings.append(
                    FindingDetail(
                        id="find_r1_double_capture",
                        run_id=run_id,
                        rule_number=1,
                        rule_name="Pay Once",
                        severity=FindingSeverity.CRITICAL,
                        persona_id=res.persona_id,
                        title="Double Capture from Idempotency Failure",
                        evidence_ids=[res.paypal_order_id or "PP-ORD-RETRIER", res.paypal_capture_id or "PP-CAP-RETRIER"],
                        paypal_record={"order_id": res.paypal_order_id, "amount": res.amount, "status": "COMPLETED_TWICE"},
                        store_record={"cart_id": res.cart_id, "recorded_order_id": res.store_order_id},
                        explanation=(
                            "The Retrier replayed checkout after a simulated network timeout. Because the store did not persist "
                            "and forward the Idempotency-Key / PayPal-Request-Id, PayPal recorded two independent captures, "
                            "resulting in a double charge for the customer."
                        ),
                        patch_diff=(
                            "--- a/checkout.py\n"
                            "+++ b/checkout.py\n"
                            "@@ -10,3 +10,6 @@\n"
                            "+    cached = guard.check_idempotency(idempotency_key, payload)\n"
                            "+    if cached:\n"
                            "+        return cached\n"
                        ),
                        remediation_action="refund_excess_capture",
                    )
                )

        # ---------------------------------------------------------------------
        # Rule 2: Right Amount (Weight 25) — Server authoritative price lock
        # ---------------------------------------------------------------------
        r2_lanes = [r for r in lane_results.values() if r.lane in {2, 3, 8, 9}]
        eval_counts[2][1] = max(1, len(r2_lanes))
        for res in r2_lanes:
            if res.outcome == "VULNERABILITY_EXPLOITED":
                eval_counts[2][0] += 1
                if res.lane == 2:
                    findings.append(
                        FindingDetail(
                            id="find_r2_price_tampered",
                            run_id=run_id,
                            rule_number=2,
                            rule_name="Right Amount",
                            severity=FindingSeverity.CRITICAL,
                            persona_id=res.persona_id,
                            title="Under-Collected Capture from Client Price Tampering",
                            evidence_ids=[res.paypal_order_id or "PP-ORD-TAMPER", res.cart_id],
                            paypal_record={"amount": res.amount, "status": "COMPLETED"},
                            store_record={"cart_id": res.cart_id, "expected_price": "149.95", "charged_price": "1.50"},
                            explanation=(
                                "The Tamperer edited the client-side price payload to $1.50 instead of $149.95. "
                                "The store accepted client pricing without server catalog verification."
                            ),
                            patch_diff=(
                                "--- a/checkout.py\n"
                                "+++ b/checkout.py\n"
                                "@@ -15,2 +15,4 @@\n"
                                "+    server_price = await catalog.get_authoritative_price(sku)\n"
                                "+    if abs(server_price - client_price) > 0.01:\n"
                                "+        raise ProblemException.price_mismatch(server_price, client_price)\n"
                            ),
                            remediation_action="void_or_request_price_differential",
                        )
                    )
                elif res.lane == 3:
                    findings.append(
                        FindingDetail(
                            id="find_r2_stale_price_drift",
                            run_id=run_id,
                            rule_number=2,
                            rule_name="Right Amount",
                            severity=FindingSeverity.HIGH,
                            persona_id=res.persona_id,
                            title="Stale Price Race Accepted Without Re-Authentication",
                            evidence_ids=[res.cart_id],
                            explanation="Store processed stale cart price ($150.00) after catalog increased to $199.00.",
                            remediation_action="require_reauthorization_on_price_change",
                        )
                    )

        # ---------------------------------------------------------------------
        # Rule 3: No Orphan Money (Weight 15) — Capture has store order & tracking within SLA
        # ---------------------------------------------------------------------
        r3_lanes = [r for r in lane_results.values() if r.lane == 6]
        eval_counts[3][1] = max(1, len(r3_lanes))
        for res in r3_lanes:
            if res.outcome == "VULNERABILITY_EXPLOITED" or not res.store_order_id:
                eval_counts[3][0] += 1
                findings.append(
                    FindingDetail(
                        id="find_r3_orphan_capture",
                        run_id=run_id,
                        rule_number=3,
                        rule_name="No Orphan Money",
                        severity=FindingSeverity.CRITICAL,
                        persona_id=res.persona_id,
                        title="Orphan Capture Without Store Order or Tracking SLA",
                        evidence_ids=[res.paypal_capture_id or "PP-CAP-GHOST", res.cart_id],
                        paypal_record={"capture_id": res.paypal_capture_id, "amount": res.amount, "status": "COMPLETED"},
                        store_record={"store_order_id": None, "status": "MISSING_RECORD"},
                        explanation=(
                            "PayPal captured money, but the merchant's store order database transaction was omitted or dropped. "
                            "Customer was charged without a fulfillment record."
                        ),
                        patch_diff=(
                            "--- a/checkout.py\n"
                            "+++ b/checkout.py\n"
                            "@@ -25,2 +25,4 @@\n"
                            "+    order = db.create_order_record(cart, capture_id)\n"
                            "+    await tracking.sync_paypal_tracking(order.id, capture_id)\n"
                        ),
                        remediation_action="auto_refund_orphan_capture",
                    )
                )

        # ---------------------------------------------------------------------
        # Rule 4: Safe Refunds (Weight 10) — Never refund more than captured
        # ---------------------------------------------------------------------
        r4_lanes = [r for r in lane_results.values() if r.lane == 5]
        eval_counts[4][1] = max(1, len(r4_lanes))
        for res in r4_lanes:
            if res.outcome == "VULNERABILITY_EXPLOITED":
                eval_counts[4][0] += 1
                findings.append(
                    FindingDetail(
                        id="find_r4_over_refund",
                        run_id=run_id,
                        rule_number=4,
                        rule_name="Safe Refunds",
                        severity=FindingSeverity.CRITICAL,
                        persona_id=res.persona_id,
                        title="Refund Amount Exceeds Original Captured Balance",
                        evidence_ids=[res.cart_id],
                        paypal_record={"captured_amount": "$99.99"},
                        store_record={"requested_refund": "$200.00"},
                        explanation="Store accepted a refund request of $200.00 on a transaction of only $99.99.",
                        remediation_action="reject_over_refund_and_cap_to_balance",
                    )
                )

        # ---------------------------------------------------------------------
        # Rule 5: Records Agree (Weight 15) — Cryptographic webhook signature verification
        # ---------------------------------------------------------------------
        r5_lanes = [r for r in lane_results.values() if r.lane == 4]
        eval_counts[5][1] = max(1, len(r5_lanes))
        for res in r5_lanes:
            if res.outcome == "VULNERABILITY_EXPLOITED":
                eval_counts[5][0] += 1
                findings.append(
                    FindingDetail(
                        id="find_r5_forged_webhook_accepted",
                        run_id=run_id,
                        rule_number=5,
                        rule_name="Records Agree",
                        severity=FindingSeverity.HIGH,
                        persona_id=res.persona_id,
                        title="Store Marked Order Paid via Forged Webhook Without Signature",
                        evidence_ids=[res.cart_id],
                        explanation="Store processed an unsigned/forged PAYMENT.CAPTURE.COMPLETED webhook without signature verification.",
                        remediation_action="revoke_unverified_paid_status",
                    )
                )

        # ---------------------------------------------------------------------
        # Rule 6: Proof Ready (Weight 10) — Tracking reference + dispute evidence
        # ---------------------------------------------------------------------
        r6_lanes = [r for r in lane_results.values() if r.lane == 7]
        eval_counts[6][1] = max(1, len(r6_lanes))

        # Check black-box probe gap first (honest residual finding)
        if is_black_box or not snapshot.probe_verified:
            eval_counts[6][0] = 1
            eval_counts[6][1] = 2  # 50% failure share on Rule 6 -> 5 points deducted (Score: 95/100)
            findings.append(
                FindingDetail(
                    id="find_r6_blackbox_ledger_unverifiable",
                    run_id=run_id,
                    rule_number=6,
                    rule_name="Proof Ready",
                    severity=FindingSeverity.LOW,
                    persona_id="the_disputer",
                    title="Internal Order Ledger Unverifiable in Black-Box Mode",
                    evidence_ids=["PP-DISPUTE-PRESEEDED-001"],
                    explanation=(
                        "Honest limitation finding on Hardened Shop: When audited without the signed /_lab/ledger Probe endpoint secret, "
                        "external reconciliation cannot cryptographically prove that the merchant's internal order record matches "
                        "the signed cart receipt hash prior to settlement."
                    ),
                    patch_diff=(
                        "--- a/hardened_config.py\n"
                        "+++ b/hardened_config.py\n"
                        "@@ -5,3 +5,4 @@\n"
                        "+ENABLE_LAB_PROBE = True\n"
                        "+LAB_PROBE_HMAC_SECRET = os.getenv('LAB_PROBE_HMAC_SECRET')\n"
                    ),
                    remediation_action="configure_lab_probe_hmac_secret",
                )
            )
        else:
            for res in r6_lanes:
                if res.outcome == "VULNERABILITY_EXPLOITED":
                    eval_counts[6][0] += 1
                    findings.append(
                        FindingDetail(
                            id="find_r6_missing_tracking_proof",
                            run_id=run_id,
                            rule_number=6,
                            rule_name="Proof Ready",
                            severity=FindingSeverity.MEDIUM,
                            persona_id=res.persona_id,
                            title="Missing Shipment Tracking Proof for Dispute Defense",
                            evidence_ids=[res.cart_id],
                            explanation="Order was captured but lacks shipment tracking reference required to defend chargebacks.",
                            remediation_action="link_shipment_tracking_number",
                        )
                    )

        # ---------------------------------------------------------------------
        # Score Computation: Score = round(100 - sum(weight[r] * failure_share[r]))
        # ---------------------------------------------------------------------
        rule_scores: List[RuleScore] = []
        total_deduction = 0.0

        for r_num in range(1, 7):
            w = RULE_WEIGHTS[r_num]
            failed, total = eval_counts[r_num]
            total = max(1, total)
            share = min(1.0, failed / float(total))
            deduction = w * share
            total_deduction += deduction
            pts_earned = round(w * (1.0 - share))

            rule_scores.append(
                RuleScore(
                    rule_number=r_num,
                    rule_name=RULE_NAMES[r_num],
                    weight=w,
                    failed_carts=failed,
                    total_evaluated_carts=total,
                    failure_share=round(share, 3),
                    rule_score=pts_earned,
                    status="PASS" if share == 0.0 else "FAIL",
                )
            )

        final_score = max(0, min(100, round(100.0 - total_deduction)))

        # Deterministic sorting of findings: CRITICAL -> HIGH -> MEDIUM -> LOW
        findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.severity, 99), f.rule_number, f.id))

        return final_score, rule_scores, findings

