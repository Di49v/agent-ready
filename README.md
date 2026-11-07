# AgentReady Lab

> **"PayPal protects the payment. Nobody tests the merchant's side of an agent order. AgentReady Lab does."**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.162.0-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.4.5-black?logo=next.js&logoColor=white)](https://nextjs.org)
[![PayPal SDK](https://img.shields.io/badge/PayPal_SDK-2.29_Async-00457C?logo=paypal&logoColor=white)](https://github.com/context-plugins/paypal-python-sdk)
[![APIMatic](https://img.shields.io/badge/APIMatic-Context_Grounded-4A90E2)](https://www.apimatic.io/)
[![AG Grid](https://img.shields.io/badge/AG_Grid-Quartz_Telemetry-E0234E?logo=ag-grid&logoColor=white)](https://www.ag-grid.com)
[![Channel3](https://img.shields.io/badge/Channel3-Product_Catalog-FF6B6B)](https://channel3.ai)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com)
[![Tests Passing](https://img.shields.io/badge/Tests-114%2F114_Passing-brightgreen)](backend/tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## What is AgentReady Lab?

Autonomous AI shopping agents are rapidly replacing human click-and-pay checkouts. However, when autonomous agents execute purchases at high concurrency, standard e-commerce stores fail catastrophically:
- **Double Charges:** Agents retry timed-out requests without idempotency keys, capturing payments twice.
- **Price Tampering:** Agents submit outdated or manipulated cart pricing, which vulnerable stores trust.
- **Orphan Money:** Payment captures complete on PayPal, but internal order fulfillment crashes or fails silently.
- **Webhook Forgery:** Stores process fake payment confirmation webhooks without cryptographic RSA/HMAC verification.
- **Chargeback Blindspots:** Stores lack cryptographic evidence linkage connecting the buyer's signed receipt with PayPal settlement records.

**AgentReady Lab** solves this by acting as an automated compliance auditor and resilience firewall:
1. **Adversarial Persona Swarm:** Spawns 9 distinct chaos-engineering buyer personas against any target store in batched waves (`MAX_CONCURRENT_BUYERS = 5`).
2. **Dual-Ledger Reconciliation:** Compares **PayPal Sandbox Ground Truth** against the **Merchant Store Internal Ledger** (`/_lab/ledger`) joined on `purchase_units[0].custom_id = cart_id`.
3. **Agent-Readiness Certification:** Evaluates stores across 6 core safety rules and outputs an objective certification score ($0\text{--}100$).
4. **Autonomous Self-Healing:** Generates targeted 10-line Git patches and provides drop-in **Guard Middleware** enforcing RFC 9457 structured error responses.

---

## 🎯 The Problem, as a Story

Priya tells her autonomous AI assistant: **"Buy running shoes, size 8, under $80."**

The assistant pays through PayPal, but a network connection hiccups before it receives the HTTP confirmation, so it automatically retries. The merchant store's checkout backend does not recognise the idempotency retry key and creates a second order. PayPal sees two valid authorization and capture calls, so **Priya is charged \$160 instead of \$80**.

No human was watching. No error appeared on the user's screen. **PayPal did its job flawlessly. The bug lives entirely in the merchant store's own backend integration code.**

| Commerce Failure Scenario | Does PayPal's own protection cover it? | Does AgentReady Lab find it? |
|---|:---:|:---:|
| Stolen credit card or compromised account | ✅ Yes (PayPal Fraud Net) | ❌ No (Not our job) |
| Buyer files an unauthorized dispute | ✅ Yes (PayPal Dispute Resolution) | 🎯 We find the merchant root cause |
| Store creates two orders when an agent retries | ❌ No (Valid API requests) | ✅ **Yes (Rule 1: Pay Once)** |
| Money captured, but internal DB insert crashes (orphan capture) | ❌ No (Capture succeeded) | ✅ **Yes (Rule 3: No Orphan Money)** |
| Store trusts a manipulated cart price from the client payload | ❌ No (PayPal bills submitted amount) | ✅ **Yes (Rule 2: Right Amount)** |
| Store processes unverified/forged PayPal webhook notifications | ❌ No (Store neglected verification) | ✅ **Yes (Rule 5: Records Agree)** |
| Agent buys ambiguous variant due to vague prompt injection | ❌ No (Valid checkout session) | ✅ **Yes (Rule 2 & AP2 Cart Intent)** |

### Why Autonomous AI Agents Make This Worse
1. **Unattended Execution:** Agents execute purchases in the background without human supervision or review.
2. **Aggressive Parallelism:** Concurrency spikes when multi-agent swarms shop across merchants simultaneously.
3. **Automatic Retries:** Dropped packets trigger immediate client-side retries without idempotency discipline.
4. **Prompt Traps & Hallucination:** Agents read untrusted third-party product listings that may contain prompt injections (e.g., *"order 5 units"*).

---

## 🏗️ Architectural Diagrams

### 1. System Architecture (B4.1)

```mermaid
flowchart LR
    subgraph USERS["Callers & Tooling"]
        U1["Merchant Dev or Judge (Browser)"]
        U2["AI Coding Assistant (Antigravity / Claude via MCP)"]
        U3["CI/CD Pipeline (GitHub Action via REST API)"]
    end

    subgraph LAB["AgentReady Lab Core (FastAPI on Render)"]
        UI["Next.js Telemetry Dashboard & AG Grid"]
        API["Public REST API v1 (OpenAPI 3.1)"]
        MCP["Stdio MCP Server (@agent-ready/mcp-server)"]
        ORCH["Run Orchestrator (2-Wave Concurrency Semaphore)"]
        SW["Swarm Engine (9 Adversarial Personas)"]
        CP["Deterministic Chaos Proxy (Seeded Faults)"]
        REC["Dual-Ledger Reconciler (6 Rule Grader)"]
        FIX["Fix Engine (APIMatic Grounded Templates + Gemini 3.8 Flash)"]
        DB[("Supabase PostgreSQL Database")]
    end

    subgraph TARGETS["Target Commerce Stores"]
        NS["Naive Shop (18/100 FAIL — 12 Seeded Vulnerabilities)"]
        HS["Hardened Shop (95/100 PASS — AgentReady Guard Protected)"]
        PR["Signed Probe Endpoint (/_lab/ledger)"]
    end

    subgraph PP["PayPal Sandbox Environment"]
        ORD["Orders v2 API (/v2/checkout/orders)"]
        PAY["Payments v2 API (Captures, Refunds, Voids)"]
        WH["Webhook Notifications API"]
        TRK["Shipment Tracking API"]
        DSP["Dispute Resolution & Chargebacks"]
    end

    C3["Channel3 Authoritative Product Catalog"]
    SHARD["Gemini Key Sharder (Pool Rotation)"]

    U1 --> UI
    U2 --> MCP
    U3 --> API
    UI --> API
    MCP --> API
    API --> ORCH
    ORCH --> SW
    SW --> CP
    SW --> SHARD
    CP --> NS
    CP --> HS
    NS --> ORD
    HS --> ORD
    ORD --> PAY
    PAY -->|Webhook Events| WH
    WH --> NS
    WH --> HS
    NS --- PR
    HS --- PR
    NS --> C3
    HS --> C3
    ORCH --> REC
    REC -->|Read PayPal Ground Truth| PAY
    REC -->|Read Dispute & Tracking Records| DSP
    REC -->|Read Merchant Store Ledger| PR
    REC --> FIX
    FIX --> SHARD
    ORCH --> DB
    REC --> DB
```

### 2. End-to-End Crash-Test Sequence (B4.2)

```mermaid
sequenceDiagram
    autonumber
    actor Judge as Judge or Developer
    participant UI as Dashboard (Next.js)
    participant API as Lab REST API
    participant OR as Orchestrator
    participant SW as Persona Swarm (9 Lanes)
    participant CP as Chaos Proxy
    participant ST as Target Store (Naive / Hardened)
    participant PP as PayPal Sandbox
    participant RC as Dual-Ledger Reconciler
    participant FX as Fix Engine (APIMatic Grounded)

    Judge->>UI: Click "Run Crash Test" (Target: Naive Shop, Seed: 42)
    UI->>API: POST /v1/runs
    API->>OR: Queue 9-persona swarm in 2 batched waves (5 + 4)
    OR->>SW: Execute Swarm under concurrency semaphore (max 5)
    loop Parallel Buyer Persona Execution
        SW->>CP: Checkout intent payload
        CP->>ST: Forward request with deterministic chaos fault
        ST->>PP: POST /v2/checkout/orders (with PayPal-Request-Id & custom_id)
        PP-->>ST: Order approval & capture response
        PP-->>ST: Webhook event (PAYMENT.CAPTURE.COMPLETED)
        ST-->>CP: Merchant response or RFC 9457 Problem Details
        CP-->>SW: Raw wire response
    end
    OR->>RC: Settle window (5s), then initiate dual-ledger audit
    RC->>PP: Query authoritative PayPal captures, refunds, tracking, disputes
    RC->>ST: GET /_lab/ledger (Signed HMAC probe)
    RC->>RC: Cross-examine ledgers across 6 deterministic rules (Score: 18/100)
    RC->>FX: Synthesize plain-English root causes & 10-line unified diffs
    RC-->>API: Persist run summary, ledger matrix & findings
    API-->>UI: Real-time SSE stream completes (Red findings displayed)
    Judge->>UI: Click "Apply Patch & Re-Run on Hardened Shop"
    UI->>API: POST /v1/runs/{id}/rerun (target_override: hardened-shop)
    API-->>UI: Green score achieved (95/100) with 1 honest residual limitation!
```

### 3. Dual-Ledger Reconciler Logic (B4.3)

```mermaid
flowchart TD
    A["Swarm Wave Execution Complete"] --> B["Wait Webhook Settle Window (5s)"]
    B --> C["Pull PayPal Records (custom_id = cart_id)"]
    B --> D["Pull Merchant Records (GET /_lab/ledger)"]
    C --> E["Normalize Both Ledgers into Unified Matrix"]
    D --> E
    E --> R1{"Rule 1: count(captures) == 1"}
    E --> R2{"Rule 2: captured_amount == server_total"}
    E --> R3{"Rule 3: order & tracking within SLA"}
    E --> R4{"Rule 4: sum(refunds) <= captured"}
    E --> R5{"Rule 5: store_status == paypal_status"}
    E --> R6{"Rule 6: proof & signed receipt on file"}
    R1 -->|Pass| S["Compute Weighted Score (0-100)"]
    R2 -->|Pass| S
    R3 -->|Pass| S
    R4 -->|Pass| S
    R5 -->|Pass| S
    R6 -->|Pass| S
    R1 -->|Fail| F["Emit Finding with PayPal IDs as Evidence"]
    R2 -->|Fail| F
    R3 -->|Fail| F
    R4 -->|Fail| F
    R5 -->|Fail| F
    R6 -->|Fail| F
    F --> G["Rank by Severity (CRITICAL -> HIGH -> MED)"]
    G --> H["Fix Engine writes APIMatic Diff & Root Cause"]
    H --> I["Re-Run Same Seed against Hardened Shop"]
    I --> K{"Vulnerability Eliminated?"}
    K -->|Yes| L["Score Climbs to 95/100 (Certified Agent-Ready)"]
    K -->|No| H
```

### 4. Mistaken Order Lifecycle & Guard Defense (B4.4)

```mermaid
flowchart TD
    S["Agent Dispatches Checkout Order Request"] --> G1{"Idempotency Key seen in store DB?"}
    G1 -->|Yes| RP["Replay cached response with Idempotent-Replayed: true (HTTP 200)"]
    G1 -->|No| G2{"Cart matches HMAC-signed CartReceipt?"}
    G2 -->|No| E1["409 CART_INTENT_MISMATCH (Prompt Injection Blocked)"]
    G2 -->|Yes| G3{"Payload total matches authoritative catalog price?"}
    G3 -->|No| E2["409 PRICE_MISMATCH_REAUTHORIZATION_REQUIRED"]
    G3 -->|Yes| G4{"Product variant unambiguous (size & color specified)?"}
    G4 -->|No| E3["422 AMBIGUOUS_VARIANT_CLARIFICATION_REQUIRED"]
    G4 -->|Yes| P["Dispatch POST /v2/checkout/orders to PayPal Sandbox"]
    P --> W{"PayPal Webhook RSA/HMAC signature valid?"}
    W -->|No| E4["401 WEBHOOK_SIGNATURE_INVALID (Security Event Logged)"]
    W -->|Yes| FUL{"Shipment tracking posted to PayPal within SLA?"}
    FUL -->|Yes| OK["Order Completed & Fulfilled"]
    FUL -->|No| O["Reconciler Emits ORPHAN_CAPTURE_DETECTED"]
    O --> POL{"Merchant Remediation Policy"}
    POL -->|Observe| AL["Alert merchant on dashboard"]
    POL -->|Assist| RC["Queue 1-click refund recommendation"]
    POL -->|Auto| RF["POST /v2/payments/captures/{id}/refund"]
```

### 5. Data Model (B4.5)

```mermaid
erDiagram
    TARGET ||--o{ RUN : tests
    RUN ||--o{ ATTEMPT : contains
    RUN ||--o{ FINDING : produces
    RUN ||--o{ PAYPAL_RECORD : reconciles
    RUN ||--o{ STORE_RECORD : reconciles
    FINDING ||--o| PATCH : generates

    TARGET {
        string id PK
        string name
        string mode
        string base_url
    }
    RUN {
        string id PK
        string target_id FK
        int seed
        string status
        int score
    }
    ATTEMPT {
        string id PK
        string run_id FK
        string persona
        string fault
        string cart_id
    }
    PAYPAL_RECORD {
        string id PK
        string run_id FK
        string kind
        string paypal_id
        string cart_id
        string amount
    }
    STORE_RECORD {
        string id PK
        string run_id FK
        string cart_id
        string status
        string amount
    }
    FINDING {
        string id PK
        string run_id FK
        int rule
        string severity
        string evidence_ids
    }
    PATCH {
        string id PK
        string finding_id FK
        string diff
        string rerun_result
    }
```

### 6. Interactive Judge Arena (B11)

```mermaid
flowchart LR
    J["Judge enters prompt & selects Chaos Switches"] --> G{"Input Guardrails Pass?"}
    G -->|No| X["Display validation error & offer Instant Replay"]
    G -->|Yes| Q["Queue Arena Session with 10-Call Budget Meter"]
    Q --> A["Live AI Shopper Agent (Gemini 3.8 Flash)"]
    A -->|Search Query| C3["Channel3 Real Product Catalog"]
    A -->|Checkout Payload| CP["Chaos Proxy with toggled faults"]
    CP --> ST["Target Store (Naive vs. Hardened)"]
    ST --> PP["PayPal Sandbox API"]
    PP -->|Webhooks| ST
    A -->|agent_step SSE| SSE["Live SSE Telemetry Stream"]
    ST -->|store_ledger_row SSE| SSE
    PP -->|paypal_event SSE| SSE
    SSE --> GRID["AG Grid Live Quartz Stream (applyTransactionAsync)"]
    ST --> REC["Reconciler Live Evaluation"]
    PP --> REC
    REC -->|finding SSE| SSE
    REC --> R["Live Certification Score (0-100)"]
```

---

## ⚡ The 9 Adversarial Buyer Personas

| # | Persona | Attack Vector / Chaos Fault | Rule Violated | Hardened Shop Resolution |
|---|---|---|:---:|---|
| 1 | **The Retrier** | Client-side connection drops after payment; rapid duplicate capture dispatched | **Rule 1 (Pay Once)** | Persists `Idempotency-Key` to `PayPal-Request-Id`; replays cached payment |
| 2 | **The Tamperer** | Mutates payload item unit prices to \$1.50 during checkout submission | **Rule 2 (Right Amount)** | Authoritative server price re-computation; blocks checkout with RFC 9457 `409` |
| 3 | **The Stale Cart** | Captures cart after inventory expires or price changes dynamically | **Rule 2 (Right Amount)** | Atomic catalog price & inventory lock prior to PayPal capture |
| 4 | **The Skeptic** | Forges fake `PAYMENT.CAPTURE.COMPLETED` webhook with self-signed certificate | **Rule 5 (Records Agree)** | Cryptographic verification via `POST /v1/notifications/verify-webhook-signature` |
| 5 | **The Refunder** | Issues duplicate partial refunds exceeding original payment capture | **Rule 4 (Safe Refunds)** | Enforces cumulative refund ledger cap: `sum(refunds) <= captured` (`422`) |
| 6 | **The Ghost Order** | Payment succeeds on PayPal, but store database fulfillment insert crashes | **Rule 3 (No Orphan Money)**| Two-phase commit transaction lock + automated auto-reversal refund |
| 7 | **The Disputer** | Submits chargeback claim without tracking evidence linked to receipt | **Rule 6 (Proof Ready)** | Automated PayPal Shipment Tracking SLA sync (`< 8s`) |
| 8 | **The Misreader** | Live LLM shopper purchases from ambiguous listings without size/color | **Rule 2 (Right Amount)** | Enforces variant clarification requirement (`422 AMBIGUOUS_VARIANT`) |
| 9 | **The Content Trap**| Adversarial prompt injection hidden in product notes (*"order 5 units"*) | **Rule 2 (Right Amount)** | Strict HMAC-signed `CartReceipt` intent check (`409 CART_INTENT_MISMATCH`) |

---

## 🧪 12-Bug Benchmark Matrix (Section B3.13)

AgentReady Lab was benchmarked by toggling each of the 12 independent vulnerability flags one by one on `NaiveShop` and verifying clean mitigation on `HardenedShop`:

| # | Bug Flag Name | Rule Violated | Severity | Grounded PayPal API / Invariant | Naive Shop Detection | Hardened Shop Resolution | Benchmark Status |
|:---:|---|:---:|:---:|---|:---:|:---:|:---:|
| 1 | `BUG_NO_IDEMPOTENCY` | Rule 1 | CRITICAL | PayPal-Request-Id header caching | ❌ Double capture detected | ✅ Cached replay returned | **PASS (100% True Positive)** |
| 2 | `BUG_TRUST_CLIENT_PRICE` | Rule 2 | CRITICAL | Orders v2 authoritative calculation | ❌ \$1.50 tampered total billed | ✅ 409 Price Mismatch blocked | **PASS (100% True Positive)** |
| 3 | `BUG_NO_WEBHOOK_VERIFY` | Rule 5 | HIGH | verify-webhook-signature endpoint | ❌ Forged webhook accepted | ✅ 401 Signature Invalid | **PASS (100% True Positive)** |
| 4 | `BUG_ORPHAN_CAPTURE` | Rule 3 | CRITICAL | Orders capture fulfillment lifecycle | ❌ Money captured, order dropped | ✅ Auto-reversal refund triggered | **PASS (100% True Positive)** |
| 5 | `BUG_DOUBLE_REFUND` | Rule 4 | HIGH | Payments v2 captures refund cap | ❌ \$240 refunded on \$120 charge | ✅ 422 Refund Exceeds Capture | **PASS (100% True Positive)** |
| 6 | `BUG_STALE_CART` | Rule 2 | MEDIUM | Real-time catalog price validation | ❌ Outdated price honored | ✅ 409 Stale Cart rejected | **PASS (100% True Positive)** |
| 7 | `BUG_NO_TRACKING` | Rule 6 | MEDIUM | Shipment Tracking Orders API | ❌ Dispute evidence missing | ✅ Tracking synced within SLA | **PASS (100% True Positive)** |
| 8 | `BUG_ALLOW_AMBIGUOUS_VARIANT` | Rule 2 | MEDIUM | RFC 9457 422 validation | ❌ Variant omitted at checkout | ✅ 422 Clarification required | **PASS (100% True Positive)** |
| 9 | `BUG_PROMPT_INJECTION_OVERRIDE` | Rule 2 | HIGH | HMAC-signed CartReceipt intent | ❌ 5 units billed instead of 1 | ✅ 409 Cart Intent Mismatch | **PASS (100% True Positive)** |
| 10 | `BUG_OUT_OF_ORDER_WEBHOOKS` | Rule 5 | MEDIUM | State machine version monotonic lock | ❌ Pending overwrote captured | ✅ Out-of-order event discarded | **PASS (100% True Positive)** |
| 11 | `BUG_MISSING_CUSTOM_ID` | Rule 1 | MEDIUM | purchase_units[0].custom_id | ❌ Unlinked reconciliation gap | ✅ custom_id tied to cart_id | **PASS (100% True Positive)** |
| 12 | `BUG_UNENCRYPTED_RECEIPT` | Rule 6 | LOW | Cryptographic receipt signature | ❌ Unsigned cart tamperable | ✅ HMAC SHA-256 verified | **PASS (100% True Positive)** |

> **Benchmark Result:** **12 / 12 True Positives Detected on Naive Shop (100%), 0 False Alarms on Hardened Shop (0%).**

---

## 🥊 Competitor Comparison Table (Section B6)

| Capability / Feature | AgentReady Lab | APIMatic API Validator | Stripe Radar | Gremlin / Chaos Mesh | Postman / Newman |
|---|:---:|:---:|:---:|:---:|:---:|
| **Target Problem** | **Merchant-Side Agent Commerce Checkouts** | OpenAPI syntax & contract linting | Buyer credit card fraud prevention | Infrastructure & network fault injection | Manual API endpoint request testing |
| **Dual-Ledger Ground Truth Reconciler** | ✅ **Yes (PayPal vs. Store DB)** | ❌ No | ❌ No | ❌ No | ❌ No |
| **Autonomous Adversarial Shopper Personas** | ✅ **Yes (9 Specialized Dummies)** | ❌ No | ❌ No | ❌ No | ❌ No |
| **Ground-Truth PayPal Sandbox Integration** | ✅ **Yes (Orders, Captures, Tracking, Disputes)** | ❌ No | ❌ No (Stripe only) | ❌ No | ⚠️ Manual Mocking |
| **Grounded 10-Line Git Patch Generation** | ✅ **Yes (APIMatic Grounded Diff)** | ❌ No | ❌ No | ❌ No | ❌ No |
| **Verification Loop (Same-Seed Re-Run)** | ✅ **Yes (Red $\rightarrow$ Green Proven)** | ❌ No | ❌ No | ❌ No | ❌ No |
| **RFC 9457 AgentReady Guard Middleware** | ✅ **Yes (Drop-in Protection)** | ❌ No | ❌ No | ❌ No | ❌ No |
| **MCP Server for AI Coding Agents** | ✅ **Yes (5 Stdio Tools)** | ❌ No | ❌ No | ❌ No | ❌ No |

---

## 🏆 Sponsor Evidence Checklist (Section B5)

### 1. APIMatic
- **Python SDK Integration:** Grounded with official `paypal==2.29` APIMatic SDK in `backend/app/services/paypal_client.py` using `AsyncPaypalClient` and `ClientCredentialsAuth`.
- **OpenAPI 3.1 Specification:** Exported via `backend/scripts/export_openapi.py` with standard APIMatic-compliant `operationId` naming (`createCrashTestRun`, `getRunReport`, `executeJudgeArena`).
- **TypeScript SDK Generation:** Clean, typed client in `sdk/src/client.ts` (`@agent-ready/sdk`) mapping RFC 9457 Problem Details to `AgentReadyApiError`.
- **APIMatic Context Plugin:** Grounded diff templates in `backend/app/fix_engine/templates.py` incorporating official PayPal endpoint rules without hallucinated claims.

### 2. PayPal
- **Sandbox Hard-Lock:** All external API requests are hard-pinned to `https://api-m.sandbox.paypal.com` (`config.py`).
- **Orders v2 & Payments v2:** Full lifecycle exercised: `POST /v2/checkout/orders`, `POST /v2/payments/captures/{id}/refund`, and `POST /v2/payments/authorizations/{id}/void`.
- **Shipment Tracking:** Orders tracking synchronized within `< 8s` SLA for dispute defense (`Rule 6`).
- **Webhook Cryptographic Verification:** Live verification via `POST /v1/notifications/verify-webhook-signature`.
- **Dispute Resolution:** Pre-seeded dispute reconciliation joined on `purchase_units[0].custom_id`.

### 3. AG Grid
- **Swiss Precision Quartz Telemetry:** Custom dark telemetry workbench utilizing AG Grid Community (`ag-grid-react` v33).
- **Dynamic Cell Flashing:** `enableCellChangeFlash: true` on live updating order and status columns.
- **Async Transaction Engine:** Live SSE event stream updates via `applyTransactionAsync` in the Judge Arena.
- **Custom Status & Latency Renderers:** Micro-indicators for Pass/Violation/Chaos status dots and tabular JetBrains Mono metrics.

### 4. Channel3
- **Authoritative E-Commerce Catalog:** Real product catalog integration in `backend/app/services/channel3_service.py` with in-memory TTL caching.
- **Variant Ambiguity Defense:** Real-time multi-variant resolution (`prod_running_shoes_002`) requiring explicit size and color selection.
- **Tangible E-Commerce Cards:** Product photo, title, authoritative price, and prompt-injection warning banners rendered alongside wire telemetry in `LiveStoreCartInspector.tsx`.

### 5. Render
- **Zero-Downtime Blueprint:** Full service configuration specified in `render.yaml`.
- **Cold-Start Warmup:** Automated `/healthz` warmup ping preventing latency hiccups during hackathon judging.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.11+** with [`uv`](https://docs.astral.sh/uv/) package manager
- **Node.js 20+** and `npm`
- **PayPal Developer Account:** US Sandbox Business & Personal Buyer credentials
- **Supabase Account:** PostgreSQL connection string

### 2. Backend Setup
```powershell
cd d:\agent-ready\backend

# 1. Install dependencies
uv sync

# 2. Run unit test suite (114 passing tests)
uv run pytest tests/ -v

# 3. Run the automated smoke test
uv run python scripts/smoke_test.py

# 4. Run the 12-bug benchmark matrix
uv run python scripts/run_self_test_matrix.py

# 5. Start FastAPI server
uv run uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```powershell
cd d:\agent-ready\frontend

# 1. Install dependencies
npm install

# 2. Start Next.js development server
npm run dev -- --turbopack -p 3000
```

### 4. MCP Server Registration
The AgentReady MCP Server can be linked to **Antigravity IDE** or **Claude Desktop** by registering in your `antigravity.json` or `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "agent-ready": {
      "command": "node",
      "args": ["d:/agent-ready/mcp/dist/server.js"],
      "env": {
        "AGENT_READY_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

---

## 💳 PayPal Sandbox Test Credentials

The platform runs 100% unattended against the PayPal Sandbox using automated payment simulations. To inspect transactions directly inside the PayPal Developer Dashboard:

- **Sandbox Base URL:** `https://api-m.sandbox.paypal.com`
- **Buyer Test Account:** `sb-buyer@business.example.com`
- **Sandbox Test Card (US Visa):**
  - **Card Number:** `4032 0339 5088 4192`
  - **Expiry:** `02/2028`
  - **CVV:** `957`
  - **Postal Code:** `94107`

---

## ⚖️ Honest Limitations & Boundaries

To uphold academic and engineering integrity:
1. **Sandbox Only:** AgentReady Lab is hard-pinned to the PayPal Sandbox (`api-m.sandbox.paypal.com`). It cannot and will never execute transactions on the live PayPal production network.
2. **Not an Official Certification:** The 0–100 Agent-Readiness Score is our own engineering evaluation metric. It is not an official PayPal certification or compliance badge.
3. **Templated Fixes Only:** The Fix Engine provides grounded 10-line unified diffs for the 6 primary bug classes. It does not perform general arbitrary code repair.
4. **Black-Box Residual Finding:** When testing external targets in black-box mode without our signed `/_lab/ledger` Probe endpoint installed, internal database race conditions cannot be verified, resulting in an honest residual finding on the report.
5. **AP2-Inspired Cart Receipts:** Our HMAC-signed `CartReceipt` intent verification is inspired by the Agentic Protocol (AP2) mandate, but we do not claim formal AP2 compliance.

---

## 📚 Project Documentation

- 🏛️ [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — Comprehensive technical architecture, state machines, and threat models.
- 🛠️ [`docs/SETUP.md`](docs/SETUP.md) — Full environment variable reference and Supabase database deployment guide.
- 🗺️ [`docs/ROADMAP.md`](docs/ROADMAP.md) — 7-day milestone execution tracker and completed tasks.
- 📋 [`docs/SPEC.md`](docs/SPEC.md) — Formal specifications and invariant mathematical scoring formulas.
- 📜 [`paypal-plan.md`](paypal-plan.md) — Official APIMatic PayPal SDK v2.29 integration plan and contract sheet.

---

## 📄 License

AgentReady Lab is open-source software licensed under the [MIT License](LICENSE).
