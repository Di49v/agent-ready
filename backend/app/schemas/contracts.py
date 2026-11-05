"""
Canonical Pydantic v2 schemas and JSON contracts for AgentReady Lab.
Used across the FastAPI backend, Next.js frontend, and APIMatic SDK generation.
"""
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Enums & Scoring Invariants
# -----------------------------------------------------------------------------

class FindingSeverity(str, Enum):
    """Deterministic severity ranking matching Section B3.6 / Roadmap Invariants."""
    CRITICAL = "CRITICAL"  # money_lost (e.g., double capture, under-collected capture, over-refund)
    HIGH = "HIGH"          # money_at_risk (e.g., forged webhook accepted, cart-intent mismatch)
    MEDIUM = "MEDIUM"      # records_drift (e.g., store vs paypal status disagree after settle)
    LOW = "LOW"            # evidence_gap (e.g., missing dispute evidence link or probe limitation)


class RunStatus(str, Enum):
    """Lifecycle statuses for a crash-test run."""
    QUEUED = "queued"
    RUNNING = "running"
    GRADING = "grading"
    COMPLETE = "complete"
    FAILED = "failed"


class AutoReversalPolicy(str, Enum):
    """Reconciler auto-reversal modes from Section A8."""
    OBSERVE = "observe"  # Alert merchant only
    ASSIST = "assist"    # Recommend void or refund for 1-click merchant approval
    AUTO = "auto"        # Automatically void or refund sandbox violations within limits


# -----------------------------------------------------------------------------
# Target Store & Persona Contracts
# -----------------------------------------------------------------------------

class TargetStore(BaseModel):
    """Target e-commerce store under test."""
    id: str = Field(..., description="Unique target identifier (e.g. 'naive-shop', 'hardened-shop')")
    name: str = Field(..., description="Human-readable name of the target store")
    base_url: str = Field(..., description="Root URL of the target store")
    mode: Literal["probe", "black_box"] = Field(
        default="probe",
        description="'probe' has access to signed /_lab/ledger; 'black_box' evaluates externally",
    )
    probe_url: Optional[str] = Field(
        default=None,
        description="Signed internal ledger endpoint (e.g. http://localhost:8000/demo/naive/_lab/ledger)",
    )
    ledger_secret: Optional[str] = Field(
        default=None,
        description="Shared HMAC-SHA256 secret for verifying the store's signed probe ledger",
    )
    description: Optional[str] = Field(default=None, description="Description of the target configuration")
    is_demo: bool = Field(default=True, description="Whether this is a pre-registered built-in demo target")
    created_at: Optional[str] = Field(default=None, description="ISO timestamp of target creation")


class PersonaSpec(BaseModel):
    """Specification of an adversarial AI buyer persona from Section A6."""
    id: str = Field(..., description="Slug identifier (e.g. 'the_retrier')")
    name: str = Field(..., description="Display title (e.g. 'The Retrier')")
    plain_words: str = Field(..., description="Plain-English explanation of the persona's action")
    rule_number: int = Field(..., ge=1, le=6, description="Primary rule tested (1 to 6)")
    rule_name: str = Field(..., description="Canonical rule name ('Pay Once', etc.)")
    driven_by: Literal["fixed_script", "live_llm"] = Field(
        ...,
        description="Execution engine: 'fixed_script' for deterministic replay or 'live_llm'",
    )
    fault_description: str = Field(..., description="Exact network or data fault applied by the Chaos Proxy")
    expected_behavior: str = Field(..., description="What a hardened store must do to pass")
    wave: int = Field(default=1, ge=1, le=2, description="Concurrency wave (Wave 1: 1-5, Wave 2: 6-9)")


# -----------------------------------------------------------------------------
# Cart Receipt (AP2-Inspired Intent Lock)
# -----------------------------------------------------------------------------

class CartItem(BaseModel):
    """An individual item inside a cart."""
    item_id: str = Field(..., description="Product SKU or catalog identifier")
    title: str = Field(..., description="Product title")
    unit_price: str = Field(..., description="Unit price formatted as string decimal (e.g. '120.00')")
    quantity: int = Field(..., ge=1, description="Quantity of items")
    selected_options: Dict[str, str] = Field(
        default_factory=dict,
        description="Selected options such as size or color (e.g. {'size': 'M'})",
    )


class CartReceipt(BaseModel):
    """
    AP2-inspired signed cart receipt produced by the buyer runtime.
    Guarantees that what the store captures matches what the human authorized.
    """
    receipt_id: str = Field(..., description="Unique receipt identifier (e.g. 'rcpt_7f3a9e2b')")
    cart_id: str = Field(
        ...,
        description="Join key across Store and PayPal (matches purchase_units[0].custom_id)",
    )
    items: List[CartItem] = Field(default_factory=list, description="Items approved by the human")
    currency: str = Field(default="USD", description="Three-letter ISO currency code")
    total_amount: str = Field(..., description="Total authorized amount formatted as string decimal")
    client_timestamp: str = Field(..., description="ISO 8601 timestamp of human approval")
    cart_hash: str = Field(..., description="SHA-256 hash of the canonical cart JSON payload")
    signature: Optional[str] = Field(
        default=None,
        description="HMAC-SHA256 signature generated with CART_RECEIPT_HMAC_SECRET",
    )


# -----------------------------------------------------------------------------
# Dual Ledger & Snapshots
# -----------------------------------------------------------------------------

class DualLedgerRow(BaseModel):
    """Unified side-by-side row comparing PayPal Sandbox records vs. Store Probe records."""
    cart_id: str = Field(..., description="Cart join key (custom_id)")
    persona_id: str = Field(..., description="Persona that executed the lane")
    timestamp: str = Field(..., description="ISO timestamp of the event")
    paypal_order_id: Optional[str] = Field(default=None, description="PayPal Order ID (e.g. 5O190127TN364715T)")
    paypal_capture_id: Optional[str] = Field(default=None, description="PayPal Capture ID (e.g. 2GG279541U471931P)")
    paypal_status: Optional[str] = Field(default=None, description="Status in PayPal Sandbox")
    paypal_amount: Optional[str] = Field(default=None, description="Amount collected by PayPal")
    store_order_id: Optional[str] = Field(default=None, description="Store internal order ID")
    store_status: Optional[str] = Field(default=None, description="Order status in Store database")
    store_amount: Optional[str] = Field(default=None, description="Amount recorded by Store")
    tracking_number: Optional[str] = Field(default=None, description="PayPal shipment tracking number")
    has_dispute: bool = Field(default=False, description="Whether a dispute was raised for this cart")
    dispute_id: Optional[str] = Field(default=None, description="Pre-seeded or active PayPal dispute ID")
    disagreements: List[str] = Field(default_factory=list, description="List of detected ledger discrepancies")


class LedgerSnapshot(BaseModel):
    """Full snapshot of dual-ledger data captured at the end of a crash-test run."""
    run_id: str = Field(..., description="Run identifier")
    target_id: str = Field(..., description="Target store identifier")
    snapshot_time: str = Field(..., description="ISO 8601 timestamp of snapshot creation")
    settle_window_sec: int = Field(default=5, description="Webhook settle window applied before grading")
    probe_verified: bool = Field(default=True, description="Whether store probe signature was verified")
    paypal_records: List[Dict[str, Any]] = Field(default_factory=list, description="Raw PayPal record snapshots")
    store_records: List[Dict[str, Any]] = Field(default_factory=list, description="Raw Store ledger snapshots")
    dual_rows: List[DualLedgerRow] = Field(default_factory=list, description="Reconciled side-by-side comparison rows")


# -----------------------------------------------------------------------------
# Findings & Patch Contracts
# -----------------------------------------------------------------------------

class FindingDetail(BaseModel):
    """
    Detailed audit finding generated by the Reconciler when an invariant rule is violated.
    Powers the AG Grid rows and the side-by-side Dual-Ledger Inspector drawer.
    """
    id: str = Field(..., description="Unique finding ID (e.g. 'find_rule1_double_capture')")
    run_id: Optional[str] = Field(default=None, description="ID of the run that generated this finding")
    rule_number: int = Field(..., ge=1, le=6, description="Rule number violated (1 to 6)")
    rule_name: str = Field(..., description="Canonical rule name ('Pay Once', 'Right Amount', etc.)")
    severity: FindingSeverity = Field(..., description="CRITICAL, HIGH, MEDIUM, or LOW")
    persona_id: Optional[str] = Field(default=None, description="Adversarial persona that triggered the bug")
    title: str = Field(..., description="Short finding headline")
    evidence_ids: List[str] = Field(
        default_factory=list,
        description="PayPal Sandbox Order IDs, Capture IDs, or Refund IDs that prove the finding",
    )
    paypal_record: Optional[Dict[str, Any]] = Field(
        default=None,
        description="PayPal ground-truth record displayed on the left side of the drawer",
    )
    store_record: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Store internal order/ledger record displayed on the right side of the drawer",
    )
    explanation: str = Field(
        ...,
        description="Plain-English explanation of why this bug occurred and how it harms merchant/buyer",
    )
    patch_diff: Optional[str] = Field(
        default=None,
        description="Targeted 10-line unified git diff fixing the root cause in the store checkout code",
    )
    fixed: bool = Field(default=False, description="Whether this finding was resolved upon re-run")
    remediation_action: Optional[str] = Field(
        default=None,
        description="Suggested automatic or manual reversal action (e.g. 'refund_excess_charge')",
    )


# -----------------------------------------------------------------------------
# Run Management & Summary Contracts
# -----------------------------------------------------------------------------

class RunCreateRequest(BaseModel):
    """Payload to initiate a crash-test run."""
    target: str = Field(
        default="naive-shop",
        description="Target store ID or registered alias ('naive-shop', 'hardened-shop')",
    )
    pack: str = Field(default="full", description="Test pack to execute ('full', 'core', 'smoke')")
    seed: int = Field(default=42, description="Random seed for deterministic fault injection and replay")
    policy: AutoReversalPolicy = Field(
        default=AutoReversalPolicy.AUTO,
        description="Reconciler reversal policy ('observe', 'assist', 'auto')",
    )
    replay: bool = Field(
        default=False,
        description="If true, serve instant recorded replay fixture instead of making live network calls",
    )


class RuleScore(BaseModel):
    """Score breakdown for one of the six rules."""
    rule_number: int = Field(..., ge=1, le=6)
    rule_name: str
    weight: int = Field(..., description="Weight in the 100-point formula (25, 25, 15, 10, 15, 10)")
    failed_carts: int = Field(default=0)
    total_evaluated_carts: int = Field(default=1)
    failure_share: float = Field(default=0.0, ge=0.0, le=1.0)
    rule_score: int = Field(..., description="Weight points earned for this rule")
    status: Literal["PASS", "FAIL"] = "PASS"


class RunSummary(BaseModel):
    """Complete summary of a crash-test run, score, and findings."""
    id: str = Field(..., description="Run ID (e.g. 'run_42_naive_shop')")
    target: str = Field(..., description="Target store ID")
    target_name: str = Field(..., description="Display name of target store")
    status: RunStatus = Field(..., description="Current status of the run")
    score: Optional[int] = Field(default=None, ge=0, le=100, description="Agent-Readiness Score (0 to 100)")
    seed: int = Field(default=42, description="Seed used for this run")
    policy: AutoReversalPolicy = Field(default=AutoReversalPolicy.AUTO)
    pack: str = Field(default="full")
    created_at: str = Field(..., description="ISO 8601 start timestamp")
    completed_at: Optional[str] = Field(default=None, description="ISO 8601 completion timestamp")
    settle_window_sec: int = Field(default=5)
    total_findings: int = Field(default=0)
    critical_findings: int = Field(default=0)
    high_findings: int = Field(default=0)
    medium_findings: int = Field(default=0)
    low_findings: int = Field(default=0)
    findings: List[FindingDetail] = Field(default_factory=list)
    rule_scores: List[RuleScore] = Field(default_factory=list)
    badge_url: Optional[str] = Field(default=None, description="URL to the generated SVG score badge")
    disclaimer: str = Field(
        default="Score weights are AgentReady Lab's heuristic design, not an official PayPal standard or certification.",
        description="Mandatory disclaimer label",
    )


class RunReportResponse(BaseModel):
    """Report payload supporting JSON and Markdown representation."""
    run_id: str
    summary: RunSummary
    markdown: str
    generated_at: str


# -----------------------------------------------------------------------------
# SSE Live Telemetry Stream Contracts (Section B11 & Judge Arena)
# -----------------------------------------------------------------------------

class RunEvent(BaseModel):
    """
    Server-Sent Events (SSE) telemetry frame streamed to the live dashboard.
    Emitted as event types: 'agent_step', 'paypal_event', 'store_ledger_row', 'finding', 'run_completed'.
    """
    event: Literal["agent_step", "paypal_event", "store_ledger_row", "finding", "run_completed"] = Field(
        ...,
        description="SSE event type identifier",
    )
    run_id: str = Field(..., description="ID of the active run")
    timestamp: str = Field(..., description="ISO 8601 timestamp of the event")
    lane: Optional[int] = Field(default=None, ge=1, le=9, description="Swarm lane number (1 to 9)")
    persona_id: Optional[str] = Field(default=None, description="Adversarial persona ID")
    actor: Optional[str] = Field(
        default=None,
        description="Entity performing the step (e.g. 'Buyer Agent', 'PayPal Sandbox', 'Naive Shop', 'Reconciler')",
    )
    action: Optional[str] = Field(
        default=None,
        description="Action performed (e.g. 'POST /v2/checkout/orders', 'CAPTURE $120.00', 'WEBHOOK SIGNATURE VERIFY')",
    )
    paypal_id: Optional[str] = Field(default=None, description="Associated PayPal Order ID, Capture ID, or Dispute ID")
    amount: Optional[str] = Field(default=None, description="Transaction amount (e.g. '$120.00')")
    status: Optional[str] = Field(
        default=None,
        description="Status code or token (e.g. 'COMPLETED', 'FAILED', '409_BLOCKED')",
    )
    rule_hit: Optional[int] = Field(default=None, ge=1, le=6, description="Rule evaluated (1 to 6)")
    data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary structured telemetry payload (finding details, error object, or run summary)",
    )

