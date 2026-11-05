"""
Deterministic Fault Types and Injected Fault Models for AgentReady Lab.
Implements reproducible Section B3.5 fault definitions:
dropping post-capture responses, duplicating checkout requests, stripping idempotency keys,
mutating price/quantity, delaying/reordering webhooks, and forging signatures.
"""
from enum import Enum
import time
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class FaultType(str, Enum):
    """Reproducible fault injection categories for chaos testing."""
    DROP_POST_CAPTURE_RESPONSE = "DROP_POST_CAPTURE_RESPONSE"
    DUPLICATE_CHECKOUT_REQUEST = "DUPLICATE_CHECKOUT_REQUEST"
    STRIP_IDEMPOTENCY_KEY = "STRIP_IDEMPOTENCY_KEY"
    MUTATE_PRICE = "MUTATE_PRICE"
    MUTATE_QUANTITY = "MUTATE_QUANTITY"
    FORGE_WEBHOOK_SIGNATURE = "FORGE_WEBHOOK_SIGNATURE"
    DELAY_WEBHOOK_DELIVERY = "DELAY_WEBHOOK_DELIVERY"
    REORDER_WEBHOOKS = "REORDER_WEBHOOKS"
    AMBIGUOUS_VARIANTS = "AMBIGUOUS_VARIANTS"


class InjectedFault(BaseModel):
    """Structured record of a single chaos fault applied to a lane."""
    fault_id: str
    fault_type: FaultType
    lane: int
    persona_id: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    applied_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))

