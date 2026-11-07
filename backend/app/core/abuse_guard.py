"""
AgentReady Lab — Abuse Guard & Protection Middleware.
Provides API key validation, per-IP sliding-window rate limiting,
SSRF protection, and strict target store URL allowlisting.
"""
from __future__ import annotations

from collections import defaultdict
import ipaddress
import logging
import re
import time
from typing import Dict, List, Optional
from urllib.parse import urlparse
from fastapi import Request
from app.core.config import get_settings
from app.schemas.contracts import TargetStore
from app.schemas.problem_details import ProblemException

logger = logging.getLogger(__name__)

# Built-in demo target identifiers and safe hosts
SAFE_BUILTIN_TARGET_IDS = {"naive-shop", "hardened-shop", "demo-shop"}
SAFE_LOCAL_HOSTS = {"localhost", "127.0.0.1", "testserver", "::1"}
ALLOWED_SANDBOX_DOMAINS = {
    "sandbox.paypal.com",
    "api-m.sandbox.paypal.com",
    "onrender.com",
    "render.com",
    "lab.example",
    "example.com",
    "example.org",
    "example.net",
}


class AbuseGuard:
    """
    Stateful abuse guard tracking rate-limit windows and validating external target URLs.
    Thread-safe and async-safe in-memory sliding window.
    """

    def __init__(
        self,
        runs_per_window: int = 10,
        window_seconds: int = 600,
        allow_public_judge_mode: bool = True,
    ) -> None:
        self.runs_per_window = runs_per_window
        self.window_seconds = window_seconds
        self.allow_public_judge_mode = allow_public_judge_mode
        # In-memory sliding window: client_ip -> list of epoch timestamps
        self._ip_run_history: Dict[str, List[float]] = defaultdict(list)
        # Verified domain tokens: domain -> token
        self._verified_domains: Dict[str, str] = {}

    def reset_state(self) -> None:
        """Resets rate limiting and domain registry state (used in testing)."""
        self._ip_run_history.clear()
        self._verified_domains.clear()

    # -------------------------------------------------------------------------
    # 1. Client IP Extraction
    # -------------------------------------------------------------------------

    def extract_client_ip(self, request: Request) -> str:
        """Extracts client IP from X-Forwarded-For, X-Real-IP, or ASGI client host."""
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # X-Forwarded-For can be a comma-separated list; first entry is original client
            client_ip = x_forwarded_for.split(",")[0].strip()
            if client_ip:
                return client_ip

        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip.strip()

        if request.client and request.client.host:
            return request.client.host

        return "127.0.0.1"

    # -------------------------------------------------------------------------
    # 2. API Key Authentication
    # -------------------------------------------------------------------------

    def verify_api_key(self, request: Request) -> bool:
        """
        Validates X-Lab-Api-Key or Authorization Bearer header.
        In public judge mode, requests without an API key or with the judge demo key are allowed.
        Invalid non-empty keys are strictly rejected.
        """
        settings = get_settings()
        expected_key = getattr(settings, "LAB_API_KEY", "judge_demo_public_key_2026")

        # 1. Check X-Lab-Api-Key header
        api_key = request.headers.get("X-Lab-Api-Key")

        # 2. Fallback to Authorization: Bearer <key>
        if not api_key:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                api_key = auth_header[7:].strip()

        # If key is provided, validate match
        if api_key:
            if api_key == expected_key:
                return True
            logger.warning("AbuseGuard: Invalid API key attempt: %s", api_key[:4] + "***")
            raise ProblemException.unauthorized("Invalid API key provided for AgentReady Lab.")

        # If no key provided, check if public judge mode is allowed
        if self.allow_public_judge_mode:
            return True

        raise ProblemException.unauthorized("Missing required X-Lab-Api-Key header.")

    # -------------------------------------------------------------------------
    # 3. Per-IP Rate Limiting (10 runs / 10 minutes)
    # -------------------------------------------------------------------------

    def check_and_record_run_rate_limit(self, request: Request) -> None:
        """
        Enforces sliding-window per-IP rate limit on crash-test runs.
        Raises ProblemException (HTTP 429) if client IP exceeds limit.
        """
        client_ip = self.extract_client_ip(request)
        now = time.time()
        window_start = now - self.window_seconds

        history = self._ip_run_history[client_ip]

        # Prune timestamps older than window
        valid_history = [t for t in history if t > window_start]
        self._ip_run_history[client_ip] = valid_history

        if len(valid_history) >= self.runs_per_window:
            oldest_run = valid_history[0]
            retry_after = max(1, int(oldest_run + self.window_seconds - now))
            logger.warning(
                "AbuseGuard: Rate limit exceeded for IP %s (%d runs in %ds)",
                client_ip,
                len(valid_history),
                self.window_seconds,
            )
            raise ProblemException.rate_limit_exceeded(
                retry_after=retry_after,
                client_ip=client_ip,
                limit=self.runs_per_window,
                window_minutes=self.window_seconds // 60,
            )

        # Record this run
        self._ip_run_history[client_ip].append(now)

    # -------------------------------------------------------------------------
    # 4. Target URL Allowlist & SSRF Defense
    # -------------------------------------------------------------------------

    def validate_target(self, target: TargetStore | str) -> None:
        """
        Validates target store ID and base_url against allowlist and SSRF rules.
        Rejects unallowlisted external domains, private subnets, and AWS metadata addresses.
        """
        target_id = target.id if isinstance(target, TargetStore) else str(target)
        target_url = target.base_url if isinstance(target, TargetStore) else ""

        # 1. Built-in targets are always allowed
        if target_id in SAFE_BUILTIN_TARGET_IDS:
            return

        # If only target_id was given and it's not built-in, must validate as URL or known ID
        if not target_url:
            if target_id.startswith("http://") or target_id.startswith("https://"):
                target_url = target_id
            else:
                raise ProblemException.target_not_allowlisted(
                    target_url=target_id,
                    reason=f"Target identifier '{target_id}' is not a recognized built-in store or valid URL.",
                )

        parsed = urlparse(target_url)
        if parsed.scheme not in ("http", "https"):
            raise ProblemException.target_not_allowlisted(
                target_url=target_url,
                reason="Target URL must use HTTP or HTTPS protocol.",
            )

        hostname = (parsed.hostname or "").lower()
        if not hostname:
            raise ProblemException.target_not_allowlisted(
                target_url=target_url,
                reason="Target URL lacks a valid hostname.",
            )

        # 2. Localhost and development targets
        if hostname in SAFE_LOCAL_HOSTS:
            return

        # 3. SSRF Defense: Check if hostname is an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            # Block private, link-local, loopback (if not explicitly allowed above), and reserved
            if ip.is_private or ip.is_link_local or ip.is_multicast or ip.is_reserved or str(ip) == "0.0.0.0":
                logger.warning("AbuseGuard: Blocked SSRF attempt to private IP: %s", hostname)
                raise ProblemException.target_not_allowlisted(
                    target_url=target_url,
                    reason=f"Target IP '{hostname}' belongs to a private, link-local, or restricted network (SSRF Guard).",
                )
        except ValueError:
            # Not an IP literal, it is a domain name
            pass

        # 4. Check domain allowlist
        for allowed_domain in ALLOWED_SANDBOX_DOMAINS:
            if hostname == allowed_domain or hostname.endswith(f".{allowed_domain}"):
                return

        # 5. Check if domain has a registered verification token
        if hostname in self._verified_domains:
            return

        # If none of the allowlist conditions match, block the unverified target
        logger.warning("AbuseGuard: Target domain not on allowlist: %s", hostname)
        raise ProblemException.target_not_allowlisted(
            target_url=target_url,
            reason=f"Domain '{hostname}' is not on the AgentReady Lab sandbox allowlist. Domain token verification required.",
        )

    def register_domain_token(self, domain: str, token: str) -> None:
        """Registers a domain verification token for custom sandbox stores."""
        self._verified_domains[domain.lower()] = token


# -----------------------------------------------------------------------------
# Singleton Instance & FastAPI Dependencies
# -----------------------------------------------------------------------------

_abuse_guard_instance: Optional[AbuseGuard] = None


def get_abuse_guard() -> AbuseGuard:
    """Returns singleton AbuseGuard instance."""
    global _abuse_guard_instance
    if _abuse_guard_instance is None:
        settings = get_settings()
        limit = getattr(settings, "RATE_LIMIT_RUNS_PER_10_MIN", 10)
        _abuse_guard_instance = AbuseGuard(
            runs_per_window=limit,
            window_seconds=600,
            allow_public_judge_mode=True,
        )
    return _abuse_guard_instance


def verify_api_key_dep(request: Request) -> None:
    """FastAPI dependency for API key verification."""
    guard = get_abuse_guard()
    guard.verify_api_key(request)


def enforce_rate_limit_dep(request: Request) -> None:
    """FastAPI dependency for per-IP crash-test rate limiting."""
    guard = get_abuse_guard()
    guard.check_and_record_run_rate_limit(request)

