# agent-ready — Compact AI Context & Micro-ADR Ledger

> **Instructions for AI Agent:**
> 1. Overwrite Section 1 (Current State Snapshot) at the end of every turn.
> 2. Whenever you implement a task that introduces a key architectural mechanism, append **1 new row** (`ADR-03`, `ADR-04`, etc., max 20 words per cell) to Section 3 (Micro-ADR Log). Do NOT create separate ADR files.

## 1. Current State Snapshot (Overwrite on every task completion)
- **Active Branch:** `main`
- **Completed Tasks:** `Task 1.1` (Config, Redaction, Gemini Sharder), `Task 0.2` (Contracts, Problem Details, OpenAPI), `Task 1.0A` (Mock & Replay Fixture Layer), `Task 1.0B` (FastAPI /v1/* Routers, SSE Stream), `Task 1.0C` (Next.js Frontend, Carbon Theme, 9-Lane Swarm Strip), `Task 1.0D` (AG Grid Matrix, Dual-Ledger Drawer & Red-to-Green Demo Flow), `Task 1.2` (Day-1 PayPal Sandbox Spikes & PayPalSandboxClient), `Task 1.3` (Database Models & Supabase Persistence Layer), `Task 1.4` (Render Skeleton Deployment & Live Webhook Receiver)
- **Milestone Completed:** Stage 1 complete! Tasks 1.2, 1.3, & 1.4 complete!
- **Next Roadmap Task:** `Task 2.1 — Channel3 Product Service (With TTL Cache) & Variant Ambiguity Fixtures`
- **Existing Backend Files:** `backend/app/core/config.py`, `backend/app/core/key_shard.py`, `backend/app/core/__init__.py`, `backend/app/schemas/problem_details.py`, `backend/app/schemas/contracts.py`, `backend/app/schemas/__init__.py`, `backend/app/mocks/__init__.py`, `backend/app/mocks/replay_fixtures.py`, `backend/app/services/replay_service.py`, `backend/app/services/paypal_client.py`, `backend/app/db/__init__.py`, `backend/app/db/session.py`, `backend/app/db/models.py`, `backend/app/db/schema.sql`, `backend/app/api/events_sse.py`, `backend/app/api/webhooks.py`, `backend/app/api/v1_router.py`, `backend/app/main.py`, `backend/scripts/day1_spike.py`, `render.yaml`, `paypal-plan.md`, `openapi/openapi.yaml`, `backend/tests/test_contracts.py`, `backend/tests/test_config_and_contracts.py`, `backend/tests/test_api.py`, `backend/tests/test_db_models.py`, `backend/tests/test_webhooks.py`.
- **Existing Stack Files:** `backend/app/main.py`, `backend/app/api/v1_router.py`, `backend/app/api/webhooks.py`, `backend/app/api/events_sse.py`, `backend/app/services/replay_service.py`, `backend/app/services/paypal_client.py`, `backend/app/db/models.py`, `backend/app/db/session.py`, `backend/app/mocks/replay_fixtures.py`, `render.yaml`, `frontend/src/app/globals.css`, `frontend/src/lib/api.ts`, `frontend/src/components/Header.tsx`, `frontend/src/components/SwarmLanes.tsx`, `frontend/src/components/FindingsGrid.tsx`, `frontend/src/components/LedgerDiffDrawer.tsx`, `frontend/src/components/PatchViewer.tsx`, `frontend/src/app/page.tsx`.

## 2. Locked Stack & Invariants (Do Not Deviate)
- **Project Name:** `agent-ready` (Monorepo: `backend/` FastAPI + `uv` + `uvicorn` + Supabase Postgres `asyncpg`, `frontend/` Next.js App Router + TS + Tailwind + AG Grid Community v32+).
- **Blueprint-First Pattern:** Build the full-stack connected Blueprint first (Stage 1: `Tasks 0.2 -> 1.0A -> 1.0B -> 1.0C -> 1.0D`). Keep mock/replay fixtures strictly isolated inside `backend/app/mocks/` controlled by `settings.use_mock_blueprint`. Never hardcode fake data inside FastAPI routers or React components.
- **LLM Runtime:** `gemini-3.8-flash` via `GeminiKeySharder` (`GEMINI_API_KEYS`).
- **PayPal Sandbox Pin:** `https://api-m.sandbox.paypal.com` only. Join key: `purchase_units[0].custom_id = cart_id`.
- **Error Format:** RFC 9457 (`application/problem+json`).

## 3. Micro-ADR Log (Agent appends 1 row per architectural task completed)
| ID | Date | Status | Decision | Rationale | Files Touched |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ADR-01 | 2026-11-05 | Active | FastAPI (`uv`) backend + Next.js (`AG Grid`) frontend monorepo | Auto-exports OpenAPI 3.1 `/openapi.json` for APIMatic SDK generation; fast async Python | `backend/app/core/config.py`, `backend/app/core/key_shard.py` |
| ADR-02 | 2026-11-05 | Active | Contract-first vertical blueprint with isolated `backend/app/mocks/` | Connects frontend & backend on Day 1; mock provider doubles as instant Replay mode | `docs/ROADMAP.md` |
| ADR-03 | 2026-11-05 | Active | RFC 9457 Problem Details + Canonical Pydantic v2 Contracts & OpenAPI 3.1 | Standardizes machine-actionable errors, dual-ledger snapshots, SSE telemetry, and API contract | `backend/app/schemas/problem_details.py`, `backend/app/schemas/contracts.py`, `openapi/openapi.yaml` |
| ADR-04 | 2026-11-05 | Active | Isolated Mock & Replay Layer in `backend/app/mocks/` | Powers Day 1 Blueprint & production Replay Last Run fallback with identical service signatures | `backend/app/mocks/__init__.py`, `backend/app/mocks/replay_fixtures.py` |
| ADR-05 | 2026-11-05 | Active | FastAPI `/v1/*` Routers + ReplayService + SSE Streaming | Unifies public API, Red-to-Green rerun, and live Judge Arena telemetry with RFC 9457 errors | `backend/app/api/v1_router.py`, `backend/app/api/events_sse.py`, `backend/app/main.py` |
| ADR-06 | 2026-11-05 | Active | Carbon & Telemetry Signal Theme + EventSource SSE 9-Lane Swarm Strip | Delivers real-time animated telemetry across 2 waves with batched concurrency for PayPal Sandbox | `frontend/src/app/globals.css`, `frontend/src/lib/api.ts`, `frontend/src/components/SwarmLanes.tsx` |
| ADR-07 | 2026-11-05 | Active | AG Grid Results Matrix + Side-by-Side Dual-Ledger Inspector Drawer | Implements master findings ranking and side-by-side PayPal vs Store JSON diff with 1-click re-run | `frontend/src/components/FindingsGrid.tsx`, `frontend/src/components/LedgerDiffDrawer.tsx` |
| ADR-08 | 2026-11-06 | Active | APIMatic `paypal==2.29` SDK integration via `PayPalSandboxClient` | Unattended card capture, join key custom_id, refund, and batched concurrency (5 buyers) | `backend/app/services/paypal_client.py`, `backend/scripts/day1_spike.py`, `paypal-plan.md` |
| ADR-09 | 2026-11-06 | Active | SQLAlchemy 2.0 Asyncpg Models with Supabase PgBouncer statement_cache_size=0 | Implements all 10 core entities (targets, runs, attempts, records, findings, idempotency) | `backend/app/db/models.py`, `backend/app/db/session.py`, `backend/tests/test_db_models.py` |
| ADR-10 | 2026-11-06 | Active | Live PayPal Webhook Receiver with Replay Deduplication & Render Blueprint | Real-time webhook ingestion with verify-webhook-signature, duplicate protection, and render.yaml | `backend/app/api/webhooks.py`, `render.yaml`, `backend/tests/test_webhooks.py` |

## 4. Verified Sandbox & Sponsor Quirks Log (Append 1 line per discovery)
- PayPal Sandbox OAuth tokens expire every 3–8 hours; always refresh via `POST /v1/oauth2/token`.
- `POST /v2/customer-support/process-chargeback` is Sandbox-only and requires a `COMPLETED` card-funded capture.
- Supabase pooler on `asyncpg` requires `connect_args={"statement_cache_size": 0}` in SQLAlchemy `create_async_engine`.