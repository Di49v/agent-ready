"""
Unit tests for Deterministic Seeded Chaos Proxy & Fault Injection (Task 3.1).
Verifies that runs with seed=101 produce 100% reproducible fault plans,
validates fault mutation payloads, and checks 5-buyer concurrency semaphore.
"""
import pytest
from app.chaos.faults import FaultType, InjectedFault
from app.chaos.proxy import ChaosProxy


def test_chaos_proxy_deterministic_seed_reproducibility() -> None:
    """Verifies that two runs with seed=101 produce bit-for-bit identical fault plans."""
    proxy1 = ChaosProxy(seed=101)
    plan1 = proxy1.generate_fault_plan()

    proxy2 = ChaosProxy(seed=101)
    plan2 = proxy2.generate_fault_plan()

    assert len(plan1) == len(plan2)
    for f1, f2 in zip(plan1, plan2):
        assert f1.fault_id == f2.fault_id
        assert f1.fault_type == f2.fault_type
        assert f1.lane == f2.lane
        assert f1.parameters == f2.parameters
        assert f1.description == f2.description


def test_chaos_proxy_price_mutation() -> None:
    """Verifies that MUTATE_PRICE alters the payload price deterministically."""
    proxy = ChaosProxy(seed=101)
    payload = {"items": [{"id": "prod_mug", "price": 149.95}], "client_price": 149.95}

    mutated, fault = proxy.inject_fault(
        fault_type=FaultType.MUTATE_PRICE,
        lane=2,
        persona_id="the_tamperer",
        payload=payload,
    )

    assert mutated["client_price"] in [1.50, 0.99, 2.00]
    assert mutated["items"][0]["price"] == mutated["client_price"]
    assert fault.fault_type == FaultType.MUTATE_PRICE
    assert fault.lane == 2
    assert len(proxy.injected_faults) == 1


def test_chaos_proxy_strip_idempotency_key() -> None:
    """Verifies that STRIP_IDEMPOTENCY_KEY removes idempotency headers."""
    proxy = ChaosProxy(seed=101)
    payload = {"idempotency_key": "idemp_12345", "cart_id": "c1", "amount": 100.0}

    mutated, fault = proxy.inject_fault(
        fault_type=FaultType.STRIP_IDEMPOTENCY_KEY,
        lane=1,
        persona_id="the_retrier",
        payload=payload,
    )

    assert "idempotency_key" not in mutated
    assert fault.fault_type == FaultType.STRIP_IDEMPOTENCY_KEY


def test_chaos_proxy_forge_webhook_signature() -> None:
    """Verifies that FORGE_WEBHOOK_SIGNATURE sets forged signature token."""
    proxy = ChaosProxy(seed=101)
    headers = {"PAYPAL-TRANSMISSION-SIG": "valid_authentic_sig"}

    mutated, fault = proxy.inject_fault(
        fault_type=FaultType.FORGE_WEBHOOK_SIGNATURE,
        lane=4,
        persona_id="the_webhook_skeptic",
        payload=headers,
    )

    assert mutated["PAYPAL-TRANSMISSION-SIG"] == "forged_signature_invalid"
    assert fault.fault_type == FaultType.FORGE_WEBHOOK_SIGNATURE


def test_chaos_proxy_semaphore_limit() -> None:
    """Verifies that the ChaosProxy semaphore matches MAX_CONCURRENT_BUYERS = 5."""
    proxy = ChaosProxy(seed=42)
    assert proxy.semaphore._value == 5

