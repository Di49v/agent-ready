# AgentReady Lab — System Architecture & Engineering Blueprint

This document details the architectural topology, data flows, invariant state machines, and security boundaries governing **AgentReady Lab**.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Client ["Client Presentation Tier (Next.js / TypeScript)"]
        Dashboard["Next.js App Router (Page.tsx)"]
        StoryHero["Story Hero & 4-Step Guided Tour"]
        SwarmStrip["9-Lane Swarm Visualizer (Swiss Telemetry)"]
        CartInspector["Live Channel3 Store/Cart Wire Inspector"]
        Grid["AG Grid Results Matrix (Community v33 Quartz Dark)"]
        Drawer["Dual-Ledger Diff Drawer & PatchViewer"]
        DeliverablesHub["Deliverables Showcase Hub (SDKs, MCP, Postman)"]
    end

    subgraph API ["Gateway & Orchestration Tier (FastAPI / Uvicorn)"]
        V1Router["/v1/* Public API Endpoints"]
        WebhookReceiver["/webhooks/paypal Ingestion Engine"]
        SSEStream["/v1/runs/{id}/events SSE Broadcast Hub"]
        Orchestrator["Persona Swarm Orchestrator (2 Waves)"]
    end

    subgraph Core ["Engine & Middleware Services"]
        Reconciler["Dual-Ledger Reconciler & Invariant Judge"]
        GuardMiddleware["AgentReady Guard Middleware (RFC 9457)"]
        KeySharder["Gemini 3.8 Flash Key Sharding Pool"]
        CartSigner["HMAC-SHA256 Cart Receipt Signer"]
    end

    subgraph Persistence ["Persistence Tier (Supabase PostgreSQL)"]
        DB[(10 Core Tables / PgBouncer pooler)]
    end

    subgraph External ["External Services (PayPal Sandbox & Channels)"]
        PPSandbox["PayPal Sandbox API (api-m.sandbox.paypal.com)"]
        Channel3["Channel3 Product Catalog (TTL=300s)"]
    end

    Dashboard -->|REST| V1Router
    Dashboard -->|SSE| SSEStream
    V1Router --> Orchestrator
    WebhookReceiver -->|Verify & Ingest| PPSandbox
    Orchestrator -->|Batched Semaphore 5| PPSandbox
    Orchestrator -->|Adversarial Requests| GuardMiddleware
    GuardMiddleware -->|Validated Checkouts| PPSandbox
    Reconciler -->|Compare Capture vs Probe| DB
    Reconciler -->|Root Cause Analysis| KeySharder
    Reconciler --> Grid
```

---

## 2. The 6 Commerce Invariants (Scoring Rules)

AgentReady Lab grades merchants across 6 non-negotiable invariants:

```mermaid
stateDiagram-v2
    [*] --> CartCreated: Buyer Selects Items

    state "Rule 1: Pay Once (Weight: 25)" as R1
    CartCreated --> R1: Capture Requested
    R1 --> IdempotentLocked: First Attempt Succeeds
    R1 --> DuplicateRejected: Concurrent/Retry Blocked (Replay Cached)
    R1 --> DoubleChargeFailed: Both Accepted (CRITICAL VULNERABILITY)

    state "Rule 2: Right Amount (Weight: 25)" as R2
    IdempotentLocked --> R2: Price & Variant Validation
    R2 --> PriceVerified: Server Recalculated = Client Paid
    R2 --> TamperBlocked: 409 PRICE_MISMATCH Reauthorization Required

    state "Rule 3: No Orphan Money (Weight: 15)" as R3
    PriceVerified --> R3: Settlement & Order Creation
    R3 --> OrderCreated: Internal Order & Tracking Synced (<8s SLA)
    R3 --> OrphanCaptured: PayPal Charged but No Store Order (CRITICAL)

    state "Rule 4: Safe Refunds (Weight: 10)" as R4
    OrderCreated --> R4: Refund Requested
    R4 --> RefundApproved: Cumulative <= Original Capture
    R4 --> OverRefundBlocked: 422 REFUND_EXCEEDS_CAPTURE

    state "Rule 5: Records Agree (Weight: 15)" as R5
    RefundApproved --> R5: Webhook Reconciliation
    R5 --> WebhookVerified: PayPal RSA/HMAC Signature Valid
    R5 --> ForgedRejected: 401 WEBHOOK_SIGNATURE_INVALID

    state "Rule 6: Proof Ready (Weight: 10)" as R6
    WebhookVerified --> R6: Dispute & Audit Arbitration
    R6 --> ProofComplete: Signed Cart Receipt + Tracking
    R6 --> ResidualGap: Black-box without Probe Secret (Score: 95/100)

    ProofComplete --> [*]
    ResidualGap --> [*]
```

---

## 3. Dual-Ledger Reconciliation Data Flow

The platform's core technical innovation is **Dual-Ledger Reconciliation**:

```mermaid
sequenceDiagram
    autonumber
    actor Swarm as Adversarial Swarm
    participant Target as Target Store
    participant PayPal as PayPal Sandbox API
    participant Recon as Dual-Ledger Reconciler
    participant Judge as Invariant Judge Arena

    Swarm->>Target: Checkout Request (Cart Join Key: cart_id)
    Target->>PayPal: POST /v2/checkout/orders (purchase_units[0].custom_id = cart_id)
    PayPal-->>Target: Order Created (201 Created)
    Target->>PayPal: POST /v2/checkout/orders/{id}/capture
    PayPal-->>Target: Captured (201 Created)
    
    Note over Swarm,Target: Chaos Attack Triggered (e.g. Retry / Price Tamper)
    
    Target-->>Swarm: Response (Success or RFC 9457 Error)
    
    Note over Recon,PayPal: Post-Swarm Settle Window (5s)
    
    Recon->>PayPal: GET /v2/checkout/orders + /v2/payments/captures
    PayPal-->>Recon: PayPal Ground Truth Records
    
    Recon->>Target: GET /_lab/ledger (Signed Probe)
    Target-->>Recon: Internal Store Ledger Snapshot
    
    Recon->>Judge: Reconcile Join (cart_id)
    Note over Judge: Compare PayPal Capture vs Store Fulfillment
    
    alt Invariant Broken
        Judge->>Judge: Calculate Discrepancy (e.g. $240 captured vs $120 order)
        Judge-->>Recon: Generate FindingDetail + 10-line Git Diff Patch
    else Invariant Respected
        Judge-->>Recon: Mark Rule PASS
    end
```

---

## 4. Concurrency & Rate Limit Architecture

PayPal Sandbox imposes strict IP-based rate limiting on rapid payment captures (`429 Too Many Requests`). To prevent test run aborts while evaluating all 9 persona lanes, the engine utilizes a **Two-Wave Batched Semaphore**:

- `MAX_CONCURRENT_BUYERS = 5` via `asyncio.Semaphore(5)`.
- **Wave 1 (5 Buyers):** `The Retrier`, `The Tamperer`, `The Stale Cart`, `The Webhook Skeptic`, `The Refunder`.
- **Wave 2 (4 Buyers):** `The Ghost Order`, `The Disputer`, `The Misreader`, `The Content Trap`.
- Completes the entire 9-lane adversarial stress test in **10–14 seconds** without triggering a single sandbox 429.

---

## 5. Security & Isolation Boundaries

1. **Log Redaction Filter ([`SensitiveDataFilter`](../backend/app/core/config.py)):**
   - Automatically sanitizes 16-digit credit card PAN sequences (`[REDACTED_PAN_CARD]`).
   - Redacts Bearer tokens (`[REDACTED_BEARER_TOKEN]`), client secrets, Supabase service keys, and Gemini API keys from all stdout streams and database snapshots.
2. **Sandbox Hard-Lock:**
   - Base URL is strictly validated against `https://api-m.sandbox.paypal.com`. Any attempt to pass production URLs is rejected at startup.
3. **Gemini Key Sharder ([`GeminiKeySharder`](../backend/app/core/key_shard.py)):**
   - Round-robin key rotation across `GEMINI_API_KEYS` with an automated 60-second cooldown window on HTTP `429` errors.

---

## 6. Client Presentation Tier & Swiss Precision Telemetry Workbench

The frontend architecture is built with **Next.js (App Router)** and **Tailwind CSS**, adhering strictly to the **Swiss Precision Telemetry** design system (`#08090C` Obsidian Carbon canvas, `#0D0F14` Graphite Slate panels, `gap-px bg-white/[0.07]` hairline structural grid, and `JetBrains Mono` tabular data).

### 6.1 Component Topology & Data Flow

```mermaid
flowchart TD
    Page["app/page.tsx (State Orchestrator)"]
    Page --> StoryHero["StoryHero.tsx (Value Prop & Quick Stats)"]
    Page --> GuidedTour["GuidedTour.tsx (4-Step Interactive Walkthrough)"]
    Page --> SwarmLanes["SwarmLanes.tsx (9 Persona Live Wire visualizer)"]
    Page --> CartInspector["LiveStoreCartInspector.tsx (Channel3 Intent vs Wire Diff)"]
    Page --> ResultsMatrix["AG Grid ResultsMatrix.tsx (Rule Matrix & Replay Drilldown)"]
    Page --> LedgerDrawer["DualLedgerDrawer.tsx (Capture vs Probe Diffs & Auto-Patch)"]
    Page --> DeliverablesHub["DeliverablesHub.tsx (SDKs, MCP Server & Postman)"]

    SwarmLanes -.->|Select Lane ID| CartInspector
    ResultsMatrix -.->|Open Remediation| LedgerDrawer
```

### 6.2 Key Architectural Components

1. **`StoryHero.tsx` (Task 6.5):**
   - Narrative framing explaining the high-stakes risk of autonomous agent commerce (hallucinated amounts, parallel double-charges, prompt injection).
   - High-contrast visual metric badges (0 to 100 Health Score, Invariant Compliance Status, Total Prevented Leakage in USD).

2. **`GuidedTour.tsx` (Task 6.5):**
   - 4-step guided progression across the workbench:
     - **Step 1:** Select target shop (`NaiveShop` vs. `HardenedShop`).
     - **Step 2:** Trigger the 9-Persona Swarm & observe live wire exploits in real time.
     - **Step 3:** Inspect the Dual-Ledger Discrepancy and trace captured USD vs. merchant reality.
     - **Step 4:** Execute One-Click Auto-Remediation and observe Red-to-Green compliance score recovery.

3. **`LiveStoreCartInspector.tsx` (Task 4.3):**
   - Bridges human e-commerce intent with raw agent protocol wire telemetry.
   - Synchronized with `SwarmLanes`: clicking any of the 9 persona lanes instantly updates the inspector to display that persona's exact wire transformation.
   - Displays real Channel3 catalog item (e.g., Ember Travel Mug, Sony WH-1000XM5, Brooks Ghost 16).
   - Features side-by-side **Human-Approved HMAC Cart Receipt** (signed with authoritative prices, SKUs, and maximum allowable totals) vs. **Intercepted Agent Wire Payload** (highlighting tampered prices `$149.95 → $1.50`, parallel duplicate capture calls, prompt-injected cart quantities, or dropped required variant attributes).
   - Displays real-time store outcome comparing `NaiveShop` (vulnerable 200 OK acceptance) against `HardenedShop` + `AgentReadyGuard` (RFC 9457 Problem Details rejection).

4. **`DeliverablesHub.tsx` (Task 6.5):**
   - Complete developer artifact showroom providing instant export and inspection of:
     - **Python SDK (`agentready-sdk`):** Async APIMatic client wrapper with built-in guard hooks.
     - **TypeScript SDK (`@agentready/sdk`):** Browser & Edge-ready client with automated HMAC cart signing.
     - **Model Context Protocol (MCP) Server:** Stdio & SSE tool server exposing `evaluate_shop_readiness`, `inspect_ledger_diff`, and `simulate_persona_swarm`.
     - **Postman Collection v2.1:** Automated regression test suite covering all 6 commerce invariants.


