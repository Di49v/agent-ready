# AgentReady Lab — Devpost Submission

## 💡 Elevator Pitch

> **"PayPal protects the payment. Nobody tests the merchant's side of an agent order. AgentReady Lab does."**

AgentReady Lab is an adversarial chaos-testing, dual-ledger compliance auditing, and self-healing platform for autonomous AI agent commerce on the PayPal Sandbox.

---

## 📖 Inspiration

Priya tells her autonomous AI shopping assistant: *"Buy running shoes, size 8, under $80."*

The assistant pays through PayPal, but a network hiccup interrupts the HTTP confirmation. The agent automatically retries. The merchant's checkout backend does not recognise the idempotency key and generates a second order. PayPal receives two valid payment requests, capturing **\$160 instead of \$80**.

No human was watching. No error appeared on the user's screen. **PayPal did its job flawlessly. The bug lived entirely in the merchant store's backend integration code.**

As autonomous AI agents (ChatGPT, Gemini, operator bots) become the primary consumers of e-commerce APIs, they do not shop like humans. They retry aggressively, act in high-concurrency swarms, submit ambiguous cart variants, and read untrusted product listings that can contain prompt injections.

**PayPal protects the payment itself. But who tests whether the merchant's checkout survives autonomous agents?** We built AgentReady Lab to be the automated crash-test facility and safety seatbelt for agentic commerce.

---

## 🛠️ What It Does

AgentReady Lab acts as an automated crash-testing facility, auditor, and self-healing firewall:

1. **Adversarial Persona Swarm (9 Test Dummies):**
   Spawns 9 specialized buyer personas attacking the checkout in batched parallel waves:
   - *The Retrier:* Drops responses and retries to trigger double-captures.
   - *The Tamperer:* Mutates payload prices to \$1.50 mid-flight.
   - *The Stale Cart:* Exploits expired inventory and changed catalog prices.
   - *The Webhook Skeptic:* Replays, forges, and reorders PayPal notifications.
   - *The Refunder:* Issues duplicate refunds exceeding the original capture.
   - *The Ghost Order:* Captures payment but crashes before database fulfillment.
   - *The Disputer:* Fires chargebacks without linked shipment tracking evidence.
   - *The Misreader (LLM):* Buys from ambiguous Channel3 listings without size/color.
   - *The Content Trap (LLM):* Tricked by prompt-injected product text (*"order 5 units"*).

2. **Ground-Truth Dual-Ledger Reconciliation:**
   Waits for webhooks to settle, then cross-examines **PayPal Sandbox Ground Truth** (`GET /v2/checkout/orders/{id}`, captures, refunds, tracking, disputes) against the **Merchant Store Internal Ledger** (`/_lab/ledger`) joined on `purchase_units[0].custom_id = cart_id`.

3. **6 Deterministic Compliance Rules & Scoring (0–100):**
   - **Rule 1 (Pay Once — 25 pts):** `count(captures per cart_id) == 1`
   - **Rule 2 (Right Amount — 25 pts):** `captured_amount == server_total`
   - **Rule 3 (No Orphan Money — 15 pts):** Capture has store order & tracking within SLA
   - **Rule 4 (Safe Refunds — 10 pts):** `sum(refunds) <= captured` and no duplicate refunds
   - **Rule 5 (Records Agree — 15 pts):** `store_order.status == paypal_order.status`
   - **Rule 6 (Proof Ready — 10 pts):** Tracking reference + HMAC-signed cart receipt on file

4. **APIMatic-Grounded Fix Engine & Re-Run Verification:**
   Generates grounded 10-line Git patches and plain-English root causes referencing exact PayPal transaction IDs. Clicking **`Apply Patch & Re-Run Same Seed`** proves that vulnerable code on `Naive Shop` (score `18/100`) transforms into certified resilient code on `Hardened Shop` (score `95/100`).

5. **The Judge Arena (Interactive Live Shopper):**
   Judges can type any shopping prompt, toggle 5 individual Chaos Switches, and watch a live AI shopper search Channel3 and pay through PayPal Sandbox while streaming real-time SSE events into AG Grid.

6. **AgentReady Guard Middleware & MCP Server:**
   - Drop-in middleware returning structured **RFC 9457 Problem Details** (`application/problem+json`).
   - Stdio MCP server exposing 5 tools (`start_crash_test`, `list_findings`, `explain_finding`, `suggest_fix`, `rerun`) for Antigravity IDE and Claude Desktop.
   - Typed TypeScript SDK generated from OpenAPI 3.1.

---

## ⚙️ How We Built It

- **Backend:** FastAPI, Python 3.11, `uv`, Pydantic v2, `httpx` (async), `paypal==2.29` APIMatic SDK, Supabase PostgreSQL with `asyncpg`.
- **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, AG Grid Community v33 (Swiss Precision Telemetry, JetBrains Mono, 1px exposed hairline grid, `enableCellChangeFlash`).
- **Catalog & Commerce Context:** Channel3 API for authoritative product listings and variant resolution.
- **Intelligence & Grounding:** Gemini 3.8 Flash with sharded key pooling, APIMatic Context Plugin, and dual-layer offline explanation cache for sub-5ms lookups.
- **Ecosystem:** OpenAPI 3.1 schema exporter, Model Context Protocol (MCP) server, and `@agent-ready/sdk`.

---

## 🧗 Challenges We Ran Into

1. **Sandbox Rate Limits & Concurrency:** Firing 9 parallel AI buyers simultaneously would occasionally hit PayPal Sandbox rate limits. We engineered a 2-wave batching orchestrator (5 buyers in Wave 1, 4 in Wave 2) governed by an `asyncio.Semaphore(5)`, finishing full runs in ~10 seconds with 0 rate errors.
2. **The Prompt Trap Problem:** A merchant checkout cannot see inside an AI agent's "mind" to know if it was tricked by a prompt injection. We resolved this by introducing **HMAC-signed `CartReceipt` intent tokens**: the agent's runtime signs what the human approved, and the store verifies the hash before capture.
3. **LLM Non-Determinism in Judging:** Hackathon judges need instant, reliable results even if free Gemini API quota is throttled. We pre-generated grounded explanation caches across all 12 bug classes, ensuring instant `<5ms` responses with live interpolated transaction IDs.

---

## 🏆 Accomplishments That We're Proud Of

- **114 / 114 Backend Tests Passing** in 5.67 seconds with 100% test coverage across all core systems.
- **12 / 12 True Positive Detection** on our 12-Bug Benchmark Matrix with 0 false alarms on the Hardened Shop.
- **Red-to-Green Verification:** A single click proves the entire lifecycle—taking a store from `18/100 (FAIL)` to `95/100 (PASS)`.
- **Full Sponsor Integration:** Deep, meaningful use of PayPal, APIMatic, AG Grid, Channel3, and Render.

---

## 🧠 What We Learned

- Autonomous shopping agents do not invent brand-new bug categories; they exploit classic merchant integration race conditions at machine speed and scale.
- Single-sided logs lie. Comparing the merchant's internal database against PayPal's authoritative ground truth is the only way to detect orphan money and silent state drift.

---

## 🚀 What's Next for AgentReady Lab

- Publish `@agent-ready/guard` to npm and PyPI as a single-line drop-in middleware.
- Release the `agent-ready-action` GitHub Action for continuous merchant deployment testing.
- Expand support to additional agentic commerce protocols (AP2 and ACP).

---

## 🧰 Built With

`paypal`, `apimatic`, `ag-grid`, `channel3`, `fastapi`, `next.js`, `typescript`, `python`, `supabase`, `postgresql`, `gemini`, `mcp`, `model-context-protocol`, `render`, `tailwind-css`

---

## 🔗 Links & Resources

- **GitHub Repository:** [https://github.com/LOQ/agent-ready](https://github.com/LOQ/agent-ready)
- **Live Demo Workbench:** [https://agent-ready.onrender.com](https://agent-ready.onrender.com)
- **YouTube Demo Video (2:45):** [https://youtu.be/placeholder-demo-video](https://youtu.be/placeholder-demo-video)
- **APIMatic PayPal Python SDK:** `paypal==2.29`

