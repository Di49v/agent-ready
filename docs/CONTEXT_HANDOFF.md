# agent-ready — Compact AI Context & Micro-ADR Ledger

## 1. Current State Snapshot (Overwrite on every task completion)
- **Active Branch:** `main`
- **Last Completed Roadmap Task:** `None (Initial Setup)`
- **Next Roadmap Task:** `Task 1.1 — Day 1 PayPal Sandbox Spikes`
- **Known Blockers / Active Notes:** Verify card-payments capability on US Sandbox Business account.

## 2. Locked Stack & Invariants (Do Not Deviate)
- **Project Name:** `agent-ready` (Monorepo: `backend/` FastAPI + `uv` + `uvicorn` + Postgres, `frontend/` Next.js + TS + AG Grid).
- **LLM Runtime:** `gemini-3.8-flash` via `GeminiKeySharder` (`GEMINI_API_KEYS`).
- **PayPal Sandbox Pin:** `https://api-m.sandbox.paypal.com` only. Join key: `purchase_units[0].custom_id = cart_id`.
- **Error Format:** RFC 9457 (`application/problem+json`).

## 3. Micro-ADR Log (Append 1 row per architectural decision — max 20 words per cell)
| ID | Date | Decision | Rationale | Files Touched |
| :--- | :--- | :--- | :--- | :--- |
| ADR-01 | 2026-11-05 | FastAPI backend + Next.js frontend monorepo | Auto-exports OpenAPI 3.1 `/openapi.json` for APIMatic SDK generation; fast async Python | `backend/`, `frontend/` |
| ADR-02 | 2026-11-05 | Direct REST for buyer checkout; `@paypal/agent-toolkit` for merchant tools | Toolkit is merchant-scoped; buyer card/vault approval + `PayPal-Request-Id` requires REST | `backend/app/services/paypal_client.py` |
| ADR-03 | 2026-11-05 | 7 deterministic PRNG personas + 2 live LLM (`gemini-3.8-flash`) personas | Ensures fast, reproducible protocol fault testing while testing semantic prompt traps | `backend/app/personas/` |

## 4. Verified Sandbox & Sponsor Quirks Log (Append 1 line per discovery)
- PayPal Sandbox tokens expire every 3–8 hours; always refresh via `POST /v1/oauth2/token`.
- `POST /v2/customer-support/process-chargeback` requires a `COMPLETED` card-funded capture.