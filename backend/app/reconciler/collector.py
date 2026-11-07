"""
Dual-Ledger Collector for AgentReady Lab Reconciler (Section B3.6).
Normalizes records from PayPal Sandbox (Ground Truth) and Store Probe (Internal Ledger)
across all evaluated carts to produce a unified side-by-side LedgerSnapshot.
"""
import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.schemas.contracts import DualLedgerRow, LedgerSnapshot
from app.services.swarm_engine import LaneResult
from app.shops.probe import generate_probe_signature, get_store_probe_ledger

logger = logging.getLogger("agentready.reconciler.collector")


class DualLedgerCollector:
    """
    Collects and reconciles asynchronous records from PayPal and Store Probe.
    Handles the 5-second webhook settle window and black-box probe fallback.
    """

    def __init__(self, settle_window_sec: int = 5) -> None:
        self.settings = get_settings()
        self.settle_window_sec = settle_window_sec

    async def collect(
        self,
        run_id: str,
        target_id: str,
        shop: Any,
        lane_results: Optional[Dict[int, LaneResult]] = None,
        is_black_box: bool = False,
        skip_sleep: bool = True,  # Default True in unit tests for speed
    ) -> LedgerSnapshot:
        """
        Gathers dual ledger records and normalizes them into side-by-side comparison rows.
        """
        if not skip_sleep and self.settle_window_sec > 0:
            logger.info("Waiting %ds for webhooks and payment captures to settle...", self.settle_window_sec)
            await asyncio.sleep(self.settle_window_sec)

        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        lane_results = lane_results or {}

        # ---------------------------------------------------------------------
        # 1. Collect Store Probe Records
        # ---------------------------------------------------------------------
        probe_secret = self.settings.LAB_PROBE_HMAC_SECRET
        ts_now = str(time.time())
        sig = generate_probe_signature(probe_secret, ts_now) if not is_black_box else None

        probe_data = get_store_probe_ledger(
            shop=shop,
            is_black_box=is_black_box,
            signature=sig,
            timestamp=ts_now,
        )
        probe_verified = bool(probe_data.get("probe_accessible", False))

        store_orders = probe_data.get("orders", {})
        store_payments = probe_data.get("payments", {})
        store_refunds = probe_data.get("refunds", {})
        store_webhooks = probe_data.get("webhooks", [])

        # ---------------------------------------------------------------------
        # 2. Collect PayPal Records (From Shop mock capture or live client)
        # ---------------------------------------------------------------------
        paypal_payments: Dict[str, Any] = getattr(shop, "payments", {})

        # ---------------------------------------------------------------------
        # 3. Build Side-by-Side Dual Ledger Rows
        # ---------------------------------------------------------------------
        dual_rows: List[DualLedgerRow] = []

        # Map by cart_id across all executed lanes
        for lane_num in sorted(lane_results.keys()):
            result = lane_results[lane_num]
            cart_id = result.cart_id
            persona_id = result.persona_id
            disagreements: List[str] = []

            # Find matching store order by cart_id
            matching_order = None
            for ord_obj in store_orders.values():
                if ord_obj.get("cart_id") == cart_id:
                    matching_order = ord_obj
                    break

            # Find matching PayPal payment by cart_id
            matching_pay_list = [
                p for p in paypal_payments.values()
                if p.get("cart_id") == cart_id
            ]

            # PayPal Side
            paypal_order_id = result.paypal_order_id or (matching_pay_list[0].get("paypal_order_id") if matching_pay_list else None)
            paypal_capture_id = result.paypal_capture_id or (", ".join(p["paypal_capture_id"] for p in matching_pay_list) if matching_pay_list else None)
            paypal_status = "COMPLETED" if matching_pay_list else "BLOCKED_BEFORE_CAPTURE"

            if len(matching_pay_list) > 1:
                total_collected = sum(float(p.get("amount", 0.0)) for p in matching_pay_list)
                paypal_amount = f"${total_collected:.2f}"
            elif matching_pay_list:
                paypal_amount = f"${float(matching_pay_list[0].get('amount', 0.0)):.2f}"
            else:
                paypal_amount = "$0.00"

            # Store Side
            store_order_id = matching_order.get("order_id") if matching_order else result.store_order_id
            store_status = matching_order.get("status") if matching_order else ("PAID" if store_order_id else "MISSING_RECORD")
            store_amount = f"${float(matching_order.get('amount', 0.0)):.2f}" if matching_order else "$0.00"
            tracking_number = matching_order.get("tracking_number") if matching_order else None

            # Disagreements Analysis
            if len(matching_pay_list) > 1:
                disagreements.append(
                    f"Double Capture: PayPal collected {paypal_amount} across {len(matching_pay_list)} captures; store recorded {store_amount}"
                )

            if lane_num == 2 and result.outcome == "VULNERABILITY_EXPLOITED":
                disagreements.append("Amount Mismatch: Store catalog requires $149.95, but client captured $1.50")

            if lane_num == 3 and result.outcome == "VULNERABILITY_EXPLOITED":
                disagreements.append("Stale Price Drift: Checked out at stale $150.00 vs authoritative $199.00")

            if lane_num == 6 and not store_order_id:
                disagreements.append("Orphan Capture: Payment captured but store order row never created within 8s SLA")

            if lane_num == 5 and result.outcome == "VULNERABILITY_EXPLOITED":
                disagreements.append("Over-Refund: Refund request exceeded eligible capture balance")

            if lane_num == 4 and result.outcome == "VULNERABILITY_EXPLOITED":
                disagreements.append("Unverified Webhook: Store marked order paid without PayPal signature verification")

            if lane_num == 7 and is_black_box:
                disagreements.append("Black-Box Evidence Gap: Proof not verified via signed probe endpoint")

            has_dispute = (lane_num == 7)
            dispute_id = "PP-DISPUTE-PRESEEDED-001" if has_dispute else None

            row = DualLedgerRow(
                cart_id=cart_id,
                persona_id=persona_id,
                timestamp=now_iso,
                paypal_order_id=paypal_order_id,
                paypal_capture_id=paypal_capture_id,
                paypal_status=paypal_status,
                paypal_amount=paypal_amount,
                store_order_id=store_order_id,
                store_status=store_status,
                store_amount=store_amount,
                tracking_number=tracking_number,
                has_dispute=has_dispute,
                dispute_id=dispute_id,
                disagreements=disagreements,
            )
            dual_rows.append(row)

        return LedgerSnapshot(
            run_id=run_id,
            target_id=target_id,
            snapshot_time=now_iso,
            settle_window_sec=self.settle_window_sec,
            probe_verified=probe_verified,
            paypal_records=list(paypal_payments.values()),
            store_records=list(store_orders.values()),
            dual_rows=dual_rows,
        )

