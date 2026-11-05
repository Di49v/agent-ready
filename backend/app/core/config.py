import logging
import re
from functools import lru_cache
from typing import Any, List, Optional
from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LOCKED_SANDBOX_BASE_URL: str = "https://" + "api-m.sandbox.paypal.com"


class SensitiveDataFilter(logging.Filter):
    """
    Python logging filter that redacts bearer tokens, API keys, client secrets,
    and 16-digit PAN (credit card) sequences from log records to prevent secret leakage.
    """

    # Regex patterns for sensitive tokens
    BEARER_PATTERN = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9_\-\.]+\b")
    PAN_16_PATTERN = re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")
    SECRET_KEY_PATTERN = re.compile(
        r"(?i)(client_secret|api_key|secret_key|gemini_api_keys?|sb_secret|paypal_client_secret|supabase_secret_key)[\s:=]+['\"]?([A-Za-z0-9_\-\.]{8,})['\"]?"
    )
    STANDALONE_SECRET_PATTERN = re.compile(
        r"\b(?:AIzaSy[A-Za-z0-9_\-]{33}|sb_secret_[A-Za-z0-9_\-]+|sb_publishable_[A-Za-z0-9_\-]+)\b"
    )

    @classmethod
    def mask_text(cls, text: str) -> str:
        """Mask sensitive sequences in a string."""
        if not text:
            return text
        # Mask 16-digit PAN
        text = cls.PAN_16_PATTERN.sub("[REDACTED_PAN_CARD]", text)
        # Mask Bearer tokens
        text = cls.BEARER_PATTERN.sub("Bearer [REDACTED_BEARER_TOKEN]", text)
        # Mask key-value secrets
        text = cls.SECRET_KEY_PATTERN.sub(r"\1=[REDACTED_SECRET]", text)
        # Mask standalone recognized API keys
        text = cls.STANDALONE_SECRET_PATTERN.sub("[REDACTED_API_KEY]", text)
        return text

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.mask_text(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self.mask_text(v) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(
                    self.mask_text(v) if isinstance(v, str) else v
                    for v in record.args
                )
        return True


class Settings(BaseSettings):
    """
    Application Settings for AgentReady Lab backend.
    Enforces strict PayPal Sandbox endpoint locks and Supabase asyncpg database connections.
    """

    # --- Environment & Hardened Sandbox Lock ---
    APP_ENV: str = Field(default="development", description="Application environment")
    PAYPAL_BASE_URL: str = Field(
        default=LOCKED_SANDBOX_BASE_URL,
        validation_alias=AliasChoices("PAYPAL_BASE_URL", "PAYPAL_API_BASE_URL"),
        description="PayPal API Sandbox Base URL (hard-pinned to sandbox)",
    )
    PAYPAL_API_BASE_URL: str = Field(
        default=LOCKED_SANDBOX_BASE_URL,
        validation_alias=AliasChoices("PAYPAL_API_BASE_URL", "PAYPAL_BASE_URL"),
        description="Alias for PAYPAL_BASE_URL",
    )
    REDACT_SENSITIVE_LOGS: bool = Field(default=True, description="Enable automatic sensitive log filtering")
    ENABLE_JUDGE_ARENA: bool = Field(default=True, description="Enable the interactive Judge Arena")

    # --- Concurrency & Reconciler Timing Windows ---
    MAX_CONCURRENT_BUYERS: int = Field(default=5, description="Max concurrent buyers for Sandbox rate limits")
    WEBHOOK_SETTLE_WINDOW_SEC: int = Field(default=5, description="Reconciler webhook settle window in seconds")
    RULE3_SLA_SECONDS: int = Field(default=8, description="SLA for order and tracking creation in seconds")

    # --- PayPal Sandbox Credentials ---
    PAYPAL_CLIENT_ID: str = Field(default="", description="Sandbox Business Client ID")
    PAYPAL_CLIENT_SECRET: str = Field(default="", description="Sandbox Business Client Secret")
    PAYPAL_WEBHOOK_ID: str = Field(default="", description="Sandbox Webhook ID")
    PAYPAL_SANDBOX_BUYER_PAYER_ID: str = Field(default="", description="US Sandbox Buyer Payer ID")
    PAYPAL_PRE_SEEDED_DISPUTE_ID: str = Field(default="PP-D-XXXXXXX", description="Pre-seeded dispute ID")

    # --- Sandbox Test Card ---
    PAYPAL_TEST_CARD_NUMBER: str = Field(default="4032033950884192", description="Sandbox test credit card")
    PAYPAL_TEST_CARD_EXPIRY: str = Field(default="2028-02", description="Sandbox test card expiry")
    PAYPAL_TEST_CARD_CVV: str = Field(default="957", description="Sandbox test card CVV")

    # --- Gemini Key Sharder & Model ---
    GEMINI_MODEL: str = Field(default="gemini-3.8-flash", description="Gemini model identifier")
    GEMINI_API_KEYS: str = Field(default="", description="Comma-separated Gemini API key pool")

    # --- Hackathon Sponsor APIs ---
    CHANNEL3_API_KEY: str = Field(default="", description="Channel3 API Key")
    CHANNEL3_CACHE_TTL_SEC: int = Field(default=300, description="Channel3 catalog in-memory TTL")
    APIMATIC_API_KEY: str = Field(default="", description="APIMatic API Key")

    # --- Supabase Database & Auth ---
    SUPABASE_URL: str = Field(default="", description="Supabase project URL")
    SUPABASE_PUBLISHABLE_KEY: str = Field(default="", description="Supabase publishable key")
    SUPABASE_SECRET_KEY: str = Field(default="", description="Supabase secret key")
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/postgres",
        description="PostgreSQL connection string with asyncpg dialect",
    )

    # --- Internal HMAC Signers & Abuse Guard ---
    LAB_PROBE_HMAC_SECRET: str = Field(
        default="0123456789abcdef0123456789abcdef",
        description="32-byte secret for signing /_lab/ledger Probe endpoints",
    )
    CART_RECEIPT_HMAC_SECRET: str = Field(
        default="0123456789abcdef0123456789abcdef",
        description="32-byte secret for HMAC signing of human-approved Cart Receipts",
    )
    LAB_API_KEY: str = Field(default="judge_demo_public_key_2026", description="Demo API key for Judge access")
    RATE_LIMIT_RUNS_PER_10_MIN: int = Field(default=10, description="IP rate limit for crash-test runs")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("PAYPAL_BASE_URL", "PAYPAL_API_BASE_URL", mode="after")
    @classmethod
    def validate_paypal_sandbox_url(cls, v: str) -> str:
        """
        Hard-pins the PayPal endpoint strictly to the Sandbox domain.
        Any attempt to use a production endpoint or alternative host raises a ValueError.
        """
        expected = LOCKED_SANDBOX_BASE_URL
        if v != expected:
            raise ValueError(
                f"CRITICAL SAFETY LOCK VIOLATION: PAYPAL_BASE_URL must equal the exact string '{expected}'. "
                f"Received '{v}'. Live production PayPal endpoints are strictly prohibited."
            )
        return v

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def ensure_asyncpg_dialect(cls, v: str) -> str:
        """
        Ensures Supabase or Postgres database URLs use the SQLAlchemy asyncpg dialect.
        Converts 'postgres://' or 'postgresql://' into 'postgresql+asyncpg://'.
        """
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @property
    def gemini_api_keys_list(self) -> List[str]:
        """Returns the parsed non-empty list of Gemini API keys."""
        if not self.GEMINI_API_KEYS:
            return []
        return [k.strip() for k in self.GEMINI_API_KEYS.split(",") if k.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Returns a cached instance of application Settings."""
    return Settings()


def setup_sensitive_log_redaction() -> None:
    """Applies the SensitiveDataFilter to all handlers on the root logger."""
    root = logging.getLogger()
    filt = SensitiveDataFilter()
    for h in root.handlers:
        h.addFilter(filt)

