"""
AgentReady Lab — Automated Smoke Test & Fresh-Browser External Judge Dry Run.

Asserts:
1. /healthz returns 200 with Sandbox lock confirmed.
2. Naive Shop crash test executes and returns score < 25/100 with Rule 1/2 violations.
3. Hardened Shop re-run executes and returns score >= 90/100 (95/100).
4. Replay Last Run returns in < 2.0s.
5. Sensitive data redaction filter active (no 16-digit PANs, client secrets, or bearer tokens in logs).
"""
import argparse
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.core.config import SensitiveDataFilter, get_settings
from app.main import app


class SmokeTestRunner:
    """Automated validation runner for AgentReady Lab."""

    def __init__(self, base_url: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.client = TestClient(app)
        self.results: List[Tuple[str, bool, str, float]] = []

    def _record(self, name: str, passed: bool, detail: str, duration_ms: float) -> None:
        self.results.append((name, passed, detail, duration_ms))
        status = "\033[92m[PASS]\033[0m" if passed else "\033[91m[FAIL]\033[0m"
        print(f"  {status} {name:<42} ({duration_ms:>6.1f} ms) — {detail}")

    def run_all(self) -> bool:
        print("\n" + "=" * 78)
        print(" AGENTREADY LAB — AUTOMATED SMOKE TEST & JUDGE DRY RUN")
        print("=" * 78)

        # 1. Health & Sandbox Lock
        self.test_healthz_and_sandbox_lock()

        # 2. Naive Shop Crash Test (Red Baseline)
        naive_run_id = self.test_naive_shop_crash_test()

        # 3. Hardened Shop Re-Run (Green Resolution)
        if naive_run_id:
            self.test_hardened_shop_rerun(naive_run_id)

        # 4. Instant Replay Speed (< 2.0s)
        self.test_replay_speed()

        # 5. Sensitive Data Redaction
        self.test_sensitive_data_redaction()

        # 6. Postman Collection Export
        if naive_run_id:
            self.test_postman_collection_export(naive_run_id)

        # Summary
        print("-" * 78)
        passed_count = sum(1 for _, p, _, _ in self.results if p)
        total_count = len(self.results)
        print(f" Total Checks: {passed_count}/{total_count} Passed")

        if passed_count == total_count:
            print("\033[92m >>> ALL SMOKE TEST ASSERTIONS SUCCEEDED — SYSTEM JUDGE-READY <<<\033[0m\n")
            return True
        else:
            print("\033[91m >>> SOME SMOKE TEST CHECKS FAILED <<<\033[0m\n")
            return False

    def test_healthz_and_sandbox_lock(self) -> None:
        t0 = time.perf_counter()
        res = self.client.get("/healthz")
        elapsed = (time.perf_counter() - t0) * 1000

        if res.status_code != 200:
            self._record("1. Service Vitality (/healthz)", False, f"HTTP {res.status_code}", elapsed)
            return

        data = res.json()
        base_url = data.get("paypal_base_url", "")
        is_sandbox = "sandbox.paypal.com" in base_url

        self._record(
            "1. Vitality & Sandbox Lock",
            is_sandbox and data.get("status") == "ok",
            f"status={data.get('status')}, base_url={base_url}",
            elapsed,
        )

    def test_naive_shop_crash_test(self) -> str:
        t0 = time.perf_counter()
        res = self.client.post(
            "/v1/runs",
            json={"target": "naive-shop", "seed": 42, "policy": "auto", "replay": False},
        )
        elapsed = (time.perf_counter() - t0) * 1000

        if res.status_code != 202:
            self._record("2. Naive Shop Crash Test Execution", False, f"HTTP {res.status_code}", elapsed)
            return ""

        summary = res.json()
        score = summary.get("score", 100)
        run_id = summary.get("id", "")

        score_valid = score < 25
        self._record(
            "2. Naive Shop Vulnerable Score (< 25)",
            score_valid,
            f"Run ID: {run_id}, Score: {score}/100 (FAIL)",
            elapsed,
        )

        # Check findings
        t_f0 = time.perf_counter()
        f_res = self.client.get(f"/v1/runs/{run_id}/findings")
        f_elapsed = (time.perf_counter() - t_f0) * 1000

        if f_res.status_code == 200:
            findings = f_res.json()
            has_double_capture = any("Double Capture" in f.get("title", "") for f in findings)
            has_evidence = all(len(f.get("evidence_ids", [])) > 0 for f in findings)
            self._record(
                "   -> Dual-Ledger Findings & Evidence",
                has_double_capture and has_evidence,
                f"{len(findings)} findings detected with PayPal IDs",
                f_elapsed,
            )
        else:
            self._record("   -> Dual-Ledger Findings", False, f"HTTP {f_res.status_code}", f_elapsed)

        return run_id

    def test_hardened_shop_rerun(self, naive_run_id: str) -> None:
        t0 = time.perf_counter()
        res = self.client.post(
            f"/v1/runs/{naive_run_id}/rerun",
            json={"target_override": "hardened-shop"},
        )
        elapsed = (time.perf_counter() - t0) * 1000

        if res.status_code != 202:
            self._record("3. Hardened Shop Re-Run", False, f"HTTP {res.status_code}", elapsed)
            return

        rerun_summary = res.json()
        score = rerun_summary.get("score", 0)
        findings_count = rerun_summary.get("total_findings", 99)

        # Hardened shop achieves score >= 90 (typically 95/100) with 1 honest residual limitation
        score_ok = score >= 90
        findings_ok = findings_count <= 1

        self._record(
            "3. Hardened Shop Resolution (>= 90)",
            score_ok and findings_ok,
            f"Score: {score}/100 (PASS), Residual Findings: {findings_count}",
            elapsed,
        )

    def test_replay_speed(self) -> None:
        t0 = time.perf_counter()
        res = self.client.post(
            "/v1/runs",
            json={"target": "naive-shop", "seed": 42, "policy": "auto", "replay": True},
        )
        elapsed_sec = time.perf_counter() - t0
        elapsed_ms = elapsed_sec * 1000

        under_2s = elapsed_sec < 2.0 and res.status_code == 202
        self._record(
            "4. Instant Replay Speed (< 2.0s SLA)",
            under_2s,
            f"Replay completed in {elapsed_ms:.2f} ms (< 2000 ms limit)",
            elapsed_ms,
        )

    def test_sensitive_data_redaction(self) -> None:
        t0 = time.perf_counter()

        test_card = "4032033950884192"
        test_bearer = "Bearer A21AAL_mock_access_token_super_secret"
        test_secret = "client_secret='secret_production_key_123456'"
        test_standalone = "sb_secret_abcdef998877665544332211"

        raw_payload = f"Auth failed with {test_bearer} using {test_secret} and card {test_card} key {test_standalone}"
        masked = SensitiveDataFilter.mask_text(raw_payload)

        card_redacted = test_card not in masked and "[REDACTED_PAN_CARD]" in masked
        bearer_redacted = test_bearer not in masked and "[REDACTED_BEARER_TOKEN]" in masked
        secret_redacted = "secret_production_key_123456" not in masked and "[REDACTED_SECRET]" in masked
        standalone_redacted = test_standalone not in masked and "[REDACTED_API_KEY]" in masked

        all_redacted = card_redacted and bearer_redacted and secret_redacted and standalone_redacted
        elapsed = (time.perf_counter() - t0) * 1000

        self._record(
            "5. Secret & PAN Redaction Active",
            all_redacted,
            "16-digit PANs, Bearer tokens & client secrets redacted",
            elapsed,
        )

    def test_postman_collection_export(self, run_id: str) -> None:
        t0 = time.perf_counter()
        res = self.client.get(f"/v1/runs/{run_id}/postman")
        elapsed = (time.perf_counter() - t0) * 1000

        if res.status_code != 200:
            self._record("6. Postman Collection Export", False, f"HTTP {res.status_code}", elapsed)
            return

        data = res.json()
        has_schema = "schema.getpostman.com" in data.get("info", {}).get("schema", "")
        has_items = len(data.get("item", [])) >= 3
        self._record(
            "6. Postman Collection (v2.1.0)",
            has_schema and has_items,
            f"{len(data.get('item', []))} requests exported with tests & vars",
            elapsed,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgentReady Lab Smoke Test")
    parser.add_argument("--url", default="", help="Optional base URL for live remote testing")
    args = parser.parse_args()

    runner = SmokeTestRunner(base_url=args.url)
    success = runner.run_all()
    sys.exit(0 if success else 1)

