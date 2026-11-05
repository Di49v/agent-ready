"""
The 12 Independent Bug Flags for AgentReady Lab Benchmark Matrix.
Allows granular control over which commerce vulnerabilities are active
on test stores (Section B3.13 of Spec).
"""
from enum import Enum
from typing import Dict, Set
from pydantic import BaseModel, Field


class BugFlag(str, Enum):
    """The 12 individually toggleable commerce bug flags."""
    BUG_NO_IDEMPOTENCY = "BUG_NO_IDEMPOTENCY"
    BUG_TRUST_CLIENT_PRICE = "BUG_TRUST_CLIENT_PRICE"
    BUG_STALE_CART = "BUG_STALE_CART"
    BUG_ALLOW_AMBIGUOUS_VARIANT = "BUG_ALLOW_AMBIGUOUS_VARIANT"
    BUG_NO_CART_INTENT_CHECK = "BUG_NO_CART_INTENT_CHECK"
    BUG_NO_WEBHOOK_VERIFY = "BUG_NO_WEBHOOK_VERIFY"
    BUG_WEBHOOK_REPLAY_VULN = "BUG_WEBHOOK_REPLAY_VULN"
    BUG_NO_FULFILLMENT_RECORD = "BUG_NO_FULFILLMENT_RECORD"
    BUG_NO_SHIPMENT_TRACKING = "BUG_NO_SHIPMENT_TRACKING"
    BUG_DOUBLE_REFUND = "BUG_DOUBLE_REFUND"
    BUG_OVER_REFUND = "BUG_OVER_REFUND"
    BUG_MISSING_DISPUTE_PROOF = "BUG_MISSING_DISPUTE_PROOF"


class BugConfig(BaseModel):
    """
    Configuration matrix governing which bug flags are currently enabled.
    Naive Shop runs with all_on(), Hardened Shop runs with all_off().
    """
    flags: Dict[BugFlag, bool] = Field(
        default_factory=lambda: {flag: True for flag in BugFlag}
    )

    @classmethod
    def all_on(cls) -> "BugConfig":
        """Returns configuration with all 12 bug flags enabled (Naive Shop baseline)."""
        return cls(flags={flag: True for flag in BugFlag})

    @classmethod
    def all_off(cls) -> "BugConfig":
        """Returns configuration with all 12 bug flags disabled (Hardened Shop baseline)."""
        return cls(flags={flag: False for flag in BugFlag})

    def is_enabled(self, flag: BugFlag) -> bool:
        """Returns whether a specific bug flag is active."""
        return self.flags.get(flag, False)

    def enable(self, flag: BugFlag) -> None:
        """Enables a specific bug flag."""
        self.flags[flag] = True

    def disable(self, flag: BugFlag) -> None:
        """Disables a specific bug flag."""
        self.flags[flag] = False

    def active_flags(self) -> Set[BugFlag]:
        """Returns set of all currently active bug flags."""
        return {flag for flag, enabled in self.flags.items() if enabled}

