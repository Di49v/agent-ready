"""
SQLAlchemy 2.0 Declarative Models for AgentReady Lab.
Implements Section B3.4 & B4.5 schema entities for Supabase PostgreSQL:
Target, Run, Attempt, PayPalRecord, StoreRecord, Finding, Patch,
RunEventLog, StoreOrder, and IdempotencyRecord.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.session import Base

# Use JSONB on PostgreSQL for efficient indexing, fallback to standard JSON elsewhere
JsonType = JSON().with_variant(JSONB(), "postgresql")


class Target(Base):
    """Registered E-commerce Store Target (Naive Shop, Hardened Shop, or Custom)."""
    __tablename__ = "targets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    mode: Mapped[str] = mapped_column(String(32), default="probe", nullable=False)
    probe_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ledger_secret: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    runs: Mapped[List["Run"]] = relationship("Run", back_populates="target", cascade="all, delete-orphan")


class Run(Base):
    """Crash-Test Run Header and Certification Summary."""
    __tablename__ = "runs"

    run_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    target_id: Mapped[str] = mapped_column(String(64), ForeignKey("targets.id", ondelete="CASCADE"), index=True)
    target_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True, nullable=False)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    duration_sec: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    seed: Mapped[int] = mapped_column(Integer, default=42, nullable=False)
    policy_id: Mapped[str] = mapped_column(String(64), default="balanced", nullable=False)
    total_findings: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    critical_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    high_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    medium_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    low_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    target: Mapped["Target"] = relationship("Target", back_populates="runs")
    attempts: Mapped[List["Attempt"]] = relationship("Attempt", back_populates="run", cascade="all, delete-orphan")
    paypal_records: Mapped[List["PayPalRecord"]] = relationship("PayPalRecord", back_populates="run", cascade="all, delete-orphan")
    store_records: Mapped[List["StoreRecord"]] = relationship("StoreRecord", back_populates="run", cascade="all, delete-orphan")
    findings: Mapped[List["Finding"]] = relationship("Finding", back_populates="run", cascade="all, delete-orphan")
    events: Mapped[List["RunEventLog"]] = relationship("RunEventLog", back_populates="run", cascade="all, delete-orphan")


class Attempt(Base):
    """Individual Persona Lane Attempt Execution."""
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.run_id", ondelete="CASCADE"), index=True)
    persona_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    lane_number: Mapped[int] = mapped_column(Integer, nullable=False)
    cart_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", nullable=False)
    last_action: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    amount: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    paypal_order_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    paypal_capture_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    run: Mapped["Run"] = relationship("Run", back_populates="attempts")


class PayPalRecord(Base):
    """Ground-Truth Capture Snapshot Retrieved from PayPal Sandbox API."""
    __tablename__ = "paypal_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.run_id", ondelete="CASCADE"), index=True)
    cart_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    order_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    capture_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(16), default="USD", nullable=False)
    raw_json: Mapped[Dict[str, Any]] = mapped_column(JsonType, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    run: Mapped["Run"] = relationship("Run", back_populates="paypal_records")


class StoreRecord(Base):
    """Store Ledger State Snapshot Retrieved via /_lab/ledger Probe or Black-box Observer."""
    __tablename__ = "store_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.run_id", ondelete="CASCADE"), index=True)
    cart_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    order_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[str] = mapped_column(String(32), nullable=False)
    probe_accessible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    raw_json: Mapped[Dict[str, Any]] = mapped_column(JsonType, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    run: Mapped["Run"] = relationship("Run", back_populates="store_records")


class Finding(Base):
    """Commerce Invariant Violation Identified by Reconciler & Judge."""
    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.run_id", ondelete="CASCADE"), index=True)
    rule_number: Mapped[int] = mapped_column(Integer, nullable=False)
    rule_name: Mapped[str] = mapped_column(String(128), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    persona_id: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    evidence_ids: Mapped[List[str]] = mapped_column(JsonType, default=list, nullable=False)
    paypal_record: Mapped[Optional[Dict[str, Any]]] = mapped_column(JsonType, nullable=True)
    store_record: Mapped[Optional[Dict[str, Any]]] = mapped_column(JsonType, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    patch_diff: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fixed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    remediation_action: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    run: Mapped["Run"] = relationship("Run", back_populates="findings")


class Patch(Base):
    """Autonomous Git Remediation Patch Generated for Vulnerabilities."""
    __tablename__ = "patches"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    finding_id: Mapped[Optional[str]] = mapped_column(String(64), index=True, nullable=True)
    target_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    diff_content: Mapped[str] = mapped_column(Text, nullable=False)
    applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class RunEventLog(Base):
    """Sequential Telemetry Event Log for Live SSE Streaming and Replay."""
    __tablename__ = "run_event_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.run_id", ondelete="CASCADE"), index=True)
    event_id: Mapped[str] = mapped_column(String(64), nullable=False)
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    lane: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JsonType, nullable=False)

    run: Mapped["Run"] = relationship("Run", back_populates="events")

    __table_args__ = (
        Index("ix_run_event_seq", "run_id", "seq"),
    )


class StoreOrder(Base):
    """Internal Store Order for Demo Stores (Naive Shop / Hardened Shop)."""
    __tablename__ = "store_orders"

    order_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    cart_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="CREATED", nullable=False)
    amount: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(16), default="USD", nullable=False)
    customer_email: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    paypal_order_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    paypal_capture_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class IdempotencyRecord(Base):
    """Idempotency-Key Lock and Cached Response for Guard Middleware."""
    __tablename__ = "idempotency_records"

    idempotency_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    target_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    response_headers: Mapped[Dict[str, Any]] = mapped_column(JsonType, default=dict, nullable=False)
    response_body: Mapped[Dict[str, Any]] = mapped_column(JsonType, default=dict, nullable=False)
    locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

