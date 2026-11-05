"""
Unit tests for SQLAlchemy 2.0 Database Models and Session Configuration.
Verifies all 10 schema entities (targets, runs, attempts, paypal_records, store_records,
findings, patches, run_event_logs, store_orders, idempotency_records) and dialect normalization.
"""
from datetime import datetime, timezone
import pytest
from app.db.models import (
    Attempt,
    Finding,
    IdempotencyRecord,
    Patch,
    PayPalRecord,
    Run,
    RunEventLog,
    StoreOrder,
    StoreRecord,
    Target,
)
from app.db.session import Base, get_db_url


def test_table_metadata_registration() -> None:
    """Verifies that all 10 models are registered on Base metadata."""
    expected_tables = {
        "targets",
        "runs",
        "attempts",
        "paypal_records",
        "store_records",
        "findings",
        "patches",
        "run_event_logs",
        "store_orders",
        "idempotency_records",
    }
    actual_tables = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(actual_tables), f"Missing tables: {expected_tables - actual_tables}"


def test_target_and_run_model_instantiation() -> None:
    """Verifies model creation and relationship attributes."""
    target = Target(
        id="demo-shop-1",
        name="Demo Shop",
        base_url="http://localhost:8000/demo",
        mode="probe",
        is_demo=True,
    )
    assert target.id == "demo-shop-1"
    assert target.is_demo is True

    run = Run(
        run_id="run_test_001",
        target_id="demo-shop-1",
        target_name="Demo Shop",
        status="COMPLETED",
        score=95,
        passed=True,
        duration_sec=12.4,
        seed=42,
        policy_id="balanced",
        total_findings=1,
    )
    assert run.score == 95
    assert run.passed is True


def test_finding_and_idempotency_instantiation() -> None:
    """Verifies Finding and IdempotencyRecord models."""
    finding = Finding(
        id="find_001",
        run_id="run_test_001",
        rule_number=1,
        rule_name="Pay Once",
        severity="CRITICAL",
        category="double_charge",
        persona_id="the_retrier",
        title="Double Charge Detected on Retry",
        evidence_ids=["2GG279541U471931P", "7K8830129L554122X"],
        explanation="Second capture accepted without checking idempotency key.",
        fixed=False,
    )
    assert finding.rule_number == 1
    assert len(finding.evidence_ids) == 2

    idem = IdempotencyRecord(
        idempotency_key="idemp_key_12345",
        target_id="demo-shop-1",
        request_hash="sha256_mock_hash",
        status_code=200,
        response_headers={"content-type": "application/json"},
        response_body={"status": "ORDER_CREATED"},
        locked=False,
    )
    assert idem.status_code == 200
    assert idem.locked is False


def test_db_url_normalization(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies that postgres:// and postgresql:// prefixes are converted to asyncpg."""
    from app.core import config
    
    # Test postgres:// rewrite
    test_settings = config.Settings(DATABASE_URL="postgres://user:pass@host:5432/db")
    monkeypatch.setattr(config, "get_settings", lambda: test_settings)
    assert get_db_url() == "postgresql+asyncpg://user:pass@host:5432/db"

    # Test postgresql:// rewrite
    test_settings2 = config.Settings(DATABASE_URL="postgresql://user:pass@host:5432/db")
    monkeypatch.setattr(config, "get_settings", lambda: test_settings2)
    assert get_db_url() == "postgresql+asyncpg://user:pass@host:5432/db"

