"""
AgentReady Lab — Abuse Guard Tests.
Verifies API key enforcement, per-IP sliding-window rate limiting,
SSRF defense against private IP ranges, and target store allowlisting (Task 6.3).
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from app.core.abuse_guard import AbuseGuard, get_abuse_guard
from app.main import app
from app.schemas.contracts import TargetStore
from app.schemas.problem_details import ProblemErrorCode, ProblemException


@pytest.fixture(autouse=True)
def reset_abuse_guard() -> None:
    """Resets abuse guard state before each test."""
    guard = get_abuse_guard()
    guard.reset_state()


def test_abuse_guard_builtin_and_localhost_targets_pass() -> None:
    """Verifies that built-in demo targets and local dev servers pass allowlist validation."""
    guard = get_abuse_guard()

    # Built-in IDs
    guard.validate_target("naive-shop")
    guard.validate_target("hardened-shop")
    guard.validate_target("demo-shop")

    # Local development hosts
    guard.validate_target(TargetStore(id="local_3000", name="Local", base_url="http://localhost:3000"))
    guard.validate_target(TargetStore(id="local_ip", name="Local IP", base_url="http://127.0.0.1:8000"))
    guard.validate_target("http://localhost:3000")

    # Allowed sandbox cloud domains
    guard.validate_target(TargetStore(id="render_shop", name="Render Shop", base_url="https://demo-store.onrender.com"))
    guard.validate_target(TargetStore(id="paypal_sb", name="PayPal SB", base_url="https://api-m.sandbox.paypal.com"))


def test_abuse_guard_ssrf_private_ips_blocked() -> None:
    """Verifies that attempts to target private subnets, AWS metadata, or loopback are rejected."""
    guard = get_abuse_guard()

    blocked_targets = [
        "http://169.254.169.254/latest/meta-data",  # AWS link-local metadata
        "http://10.0.0.1:8080/checkout",            # Class A private
        "http://192.168.1.1/api",                   # Class C private
        "http://172.16.0.1:5000",                   # Class B private
        "http://0.0.0.0:8000",                      # Unspecified address
    ]

    for blocked_url in blocked_targets:
        with pytest.raises(ProblemException) as exc_info:
            guard.validate_target(TargetStore(id="ssrf_target", name="SSRF", base_url=blocked_url))
        assert exc_info.value.status == 403
        assert exc_info.value.problem.code == ProblemErrorCode.TARGET_NOT_ALLOWLISTED
        assert "SSRF" in exc_info.value.problem.detail or "private" in exc_info.value.problem.detail


def test_abuse_guard_unallowlisted_external_domain_blocked() -> None:
    """Verifies that unverified third-party domains are rejected with 403 TARGET_NOT_ALLOWLISTED."""
    guard = get_abuse_guard()

    with pytest.raises(ProblemException) as exc_info:
        guard.validate_target(TargetStore(
            id="rogue_target",
            name="Rogue Target",
            base_url="https://arbitrary-unverified-store.com/checkout",
        ))

    assert exc_info.value.status == 403
    assert exc_info.value.problem.code == ProblemErrorCode.TARGET_NOT_ALLOWLISTED
    assert "not on the AgentReady Lab sandbox allowlist" in exc_info.value.problem.detail


def test_abuse_guard_domain_token_verification() -> None:
    """Verifies that custom domains pass once a verification token is registered."""
    guard = get_abuse_guard()
    domain = "my-custom-sandbox-store.com"
    target = TargetStore(id="custom", name="Custom", base_url=f"https://{domain}/api")

    # Before token registration: rejected
    with pytest.raises(ProblemException):
        guard.validate_target(target)

    # Register verification token
    guard.register_domain_token(domain, "lab_verify_token_998877")

    # After token registration: allowed
    guard.validate_target(target)


def test_abuse_guard_sliding_window_rate_limiting() -> None:
    """Verifies 10-run limit per 10-minute sliding window, raising HTTP 429 on the 11th run."""
    guard = AbuseGuard(runs_per_window=3, window_seconds=600)  # Low limit for fast test

    class DummyRequest:
        headers = {}
        client = type("Client", (), {"host": "198.51.100.42"})()

    req = DummyRequest()  # type: ignore

    # First 3 runs pass
    guard.check_and_record_run_rate_limit(req)
    guard.check_and_record_run_rate_limit(req)
    guard.check_and_record_run_rate_limit(req)

    # 4th run exceeds limit
    with pytest.raises(ProblemException) as exc_info:
        guard.check_and_record_run_rate_limit(req)

    assert exc_info.value.status == 429
    assert exc_info.value.problem.code == ProblemErrorCode.RATE_LIMIT_EXCEEDED
    assert "Retry-After" in exc_info.value.headers
    assert int(exc_info.value.headers["Retry-After"]) > 0


def test_api_endpoints_abuse_guard_integration() -> None:
    """Verifies AbuseGuard integration directly through FastAPI TestClient."""
    client = TestClient(app)

    # 1. Unallowlisted target registration returns 403
    res = client.post(
        "/v1/targets",
        json={
            "id": "malicious_ext_store",
            "name": "Malicious",
            "base_url": "https://external-ddos-target.com",
            "mode": "probe",
        },
    )
    assert res.status_code == 403
    problem = res.json()
    assert problem["code"] == ProblemErrorCode.TARGET_NOT_ALLOWLISTED

    # 2. Invalid API Key returns 401
    res = client.post(
        "/v1/runs",
        headers={"X-Lab-Api-Key": "invalid_wrong_key_123"},
        json={"target": "naive-shop", "pack": "full", "seed": 42},
    )
    assert res.status_code == 401
    problem = res.json()
    assert problem["code"] == ProblemErrorCode.UNAUTHORIZED_API_KEY

    # 3. Legitimate demo key or default judge request returns 202
    res = client.post(
        "/v1/runs",
        headers={"X-Lab-Api-Key": "judge_demo_public_key_2026"},
        json={"target": "naive-shop", "pack": "full", "seed": 42},
    )
    assert res.status_code == 202
    assert "id" in res.json()

