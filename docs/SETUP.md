# AgentReady Lab — Complete Setup & Deployment Guide

This guide covers developer workstation configuration, PayPal Sandbox credential onboarding, Supabase database setup, and production deployment on Render.

---

## 1. Prerequisites

Ensure your development environment meets the following baseline:
- **Operating System:** macOS, Linux, or Windows (WSL2 or native PowerShell).
- **Python:** `3.11` or higher.
- **Python Package Manager:** [`uv`](https://docs.astral.sh/uv/) (v0.5+).
- **Node.js:** `v20.x` or higher with `npm`.
- **Git:** Installed and configured.

---

## 2. Environment Variables Reference

Copy `.env.example` to `backend/.env`. All configuration keys are detailed below:

| Environment Variable | Required | Default / Example | Purpose |
|---|---|---|---|
| `APP_ENV` | Yes | `development` | Environment mode (`development`, `production`). |
| `USE_MOCK_BLUEPRINT` | Yes | `true` | When `true`, runs in mock/replay blueprint mode without live external sandbox calls. |
| `PAYPAL_API_BASE_URL` | Yes | `https://api-m.sandbox.paypal.com` | Hard-pinned Sandbox endpoint. Rejects live production URLs. |
| `REDACT_SENSITIVE_LOGS` | Yes | `true` | Enables automatic regex masking of card PANs, Bearer tokens, and keys in logs. |
| `MAX_CONCURRENT_BUYERS`| Yes | `5` | Semaphore limit to prevent Sandbox `429` rate-limit errors. |
| `WEBHOOK_SETTLE_WINDOW_SEC`| Yes | `5` | Reconciler delay waiting for async PayPal webhooks to land before Rule 5 grading. |
| `RULE3_SLA_SECONDS` | Yes | `8` | Time window within which an order and tracking number must be created. |
| `PAYPAL_CLIENT_ID` | Sandbox | `your_us_business_client_id` | US Business Sandbox App Client ID from developer.paypal.com. |
| `PAYPAL_CLIENT_SECRET` | Sandbox | `your_us_business_client_secret`| US Business Sandbox App Secret from developer.paypal.com. |
| `PAYPAL_WEBHOOK_ID` | Sandbox | `your_webhook_id` | Webhook ID registered for `POST /webhooks/paypal`. |
| `PAYPAL_TEST_CARD_NUMBER`| Sandbox | `4032033950884192` | Sandbox Visa card number for unattended checkouts. |
| `PAYPAL_TEST_CARD_EXPIRY`| Sandbox | `2028-02` | `YYYY-MM` format expiration date. |
| `PAYPAL_TEST_CARD_CVV` | Sandbox | `957` | 3-digit security code. |
| `GEMINI_MODEL` | Yes | `gemini-3.8-flash` | Gemini model for autonomous root cause and patch synthesis. |
| `GEMINI_API_KEYS` | Yes | `key1,key2,key3` | Comma-separated Gemini API key pool for rate-limit sharding. |
| `DATABASE_URL` | Yes | `postgresql+asyncpg://...` | Supabase PostgreSQL connection string with `asyncpg` dialect. |
| `LAB_PROBE_HMAC_SECRET` | Yes | `32-byte-hex` | Secret for signing merchant `/_lab/ledger` probe requests. |
| `CART_RECEIPT_HMAC_SECRET`| Yes | `32-byte-hex` | Secret for cryptographic buyer cart approval verification. |

---

## 3. Database Setup (Supabase PostgreSQL)

AgentReady Lab is designed for Supabase PostgreSQL with transaction pooling (`PgBouncer`).

1. Open your **Supabase Project Dashboard** $\rightarrow$ **SQL Editor**.
2. Open [`backend/app/db/schema.sql`](../backend/app/db/schema.sql) in this repository.
3. Paste the contents into the Supabase SQL Editor and click **Run**.
4. Confirm that all 10 tables are created:
   `targets`, `runs`, `attempts`, `paypal_records`, `store_records`, `findings`, `patches`, `run_event_logs`, `store_orders`, `idempotency_records`.
5. Retrieve your connection string from **Project Settings $\rightarrow$ Database $\rightarrow$ Connection String (URI)**:
   - Use the **Transaction Pooler** (port `5432` or `6543`).
   - Prefix the URI with `postgresql+asyncpg://`.
   - Add it to `backend/.env` as `DATABASE_URL`.

---

## 4. Backend Local Development

```powershell
cd backend

# 1. Install all dependencies using uv
uv sync

# 2. Run the test suite
uv run pytest -v

# 3. Run the Day-1 Sandbox Spike test (Verifies PayPal SDK integration)
uv run python scripts/day1_spike.py

# 4. Start the FastAPI development server
uv run uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger UI: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/healthz`
- OpenAPI Specification: `http://localhost:8000/openapi.json`

---

## 5. Frontend Local Development

```powershell
cd frontend

# 1. Install Next.js dependencies
npm install

# 2. Run Next.js with Turbopack
npm run dev -- --turbopack -p 3000
```
- Main Dashboard: `http://localhost:3000`

---

## 6. Verification Checklist

Run these commands to verify your setup end-to-end:
```powershell
# Verify backend contracts & database models
cd backend
uv run pytest tests/test_config_and_contracts.py -v
uv run pytest tests/test_db_models.py -v
uv run pytest tests/test_webhooks.py -v

# Verify frontend production build
cd ../frontend
npm run build
```

