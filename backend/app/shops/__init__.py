"""E-commerce Shop implementations, Guard middleware, and Probe endpoints."""
from app.shops.bug_flags import BugConfig, BugFlag
from app.shops.guard import AgentReadyGuard, get_guard
from app.shops.hardened_shop import HardenedShop
from app.shops.naive_shop import NaiveShop
from app.shops.probe import (
    generate_probe_signature,
    get_store_probe_ledger,
    verify_probe_signature,
)

__all__ = [
    "BugConfig",
    "BugFlag",
    "NaiveShop",
    "HardenedShop",
    "AgentReadyGuard",
    "get_guard",
    "generate_probe_signature",
    "verify_probe_signature",
    "get_store_probe_ledger",
]
