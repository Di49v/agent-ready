# agent-ready — Verified PayPal & Sponsor Technical Context (Nov 2026)

## 1. PayPal Agent Toolkit (`@paypal/agent-toolkit` 1.11.0 & `@paypal/mcp`) + REST Gotchas
- **Toolkit Scope Trap:** `@paypal/agent-toolkit` and `@paypal/mcp` expose merchant-scoped tools (`create_order`, `get_order`, `pay_order`, `create_refund`, `get_refund`, `list_disputes`, `get_dispute`, `accept_dispute_claim`, `create_shipment_tracking`, `get_shipment_tracking`, `list_transactions`, `get_merchant_insights`).
- **Why Buyer Checkout Must Use Direct REST (`httpx`):**
  1. The toolkit's `create_order` wrapper does not let you pass a custom `PayPal-Request-Id` HTTP header (needed to test Rule 1 Idempotency) or `payment_source.card` / `payment_source.paypal.vault_id` (needed for unattended headless buyer approval without browser popups).
  2. Always set `purchase_units[0].custom_id = cart_id` in `POST /v2/checkout/orders` so the Reconciler can deterministically join PayPal orders to Store DB rows even when responses drop!
- **Token Expiration Gotcha:** PayPal Sandbox OAuth tokens (`POST /v1/oauth2/token`) expire after 3–8 hours. Never hardcode `PAYPAL_ACCESS_TOKEN`; cache it in memory with an automatic refresh when `expires_in` is within 300 seconds.
- **Disputes & Chargeback Gotcha:**
  - `POST /v2/customer-support/process-chargeback` is Sandbox-only and **fails unless the order was paid with a credit card (`payment_source.card`) and is in `COMPLETED` capture status**.
  - Buyer-initiated `POST /v1/customer/disputes` requires a `PayPal-Auth-Assertion` header (`base64url({"alg":"none"}).base64url({"iss":CLIENT_ID,"payer_id":BUYER_PAYER_ID}).`).
  - Always keep a pre-seeded Sandbox Dispute ID (`PAYPAL_PRE_SEEDED_DISPUTE_ID`) so `The Disputer` finishes in <2 seconds during live judge clicks while firing the new chargeback asynchronously in the background.

## 2. APIMatic ($1,000 x 3 Winners) — "MCP for Builders" Alignment
- **What PayPal & APIMatic Built Together (May 2026):** PayPal and APIMatic launched the **PayPal Context Plugin** under PayPal's "MCP for Builders" initiative (led by Mark Lummus) to stop AI coding assistants from hallucinating deprecated `paypal-rest-sdk` methods and instead ground code fixes in current PayPal Server SDK and Orders/Payments v2 specs.
- **How `agent-ready` Locks In Both Halves of This Prize:**
  1. **Fix Engine Grounding:** Feed authoritative PayPal API/SDK endpoint schemas (via APIMatic Context Plugin / curated spec context) into `gemini-3.8-flash` when generating the 6 bug-class code diffs so it never invents fake PayPal methods.
  2. **SDK Generation from OpenAPI 3.1:** Export FastAPI's `/openapi.json` for all `/v1/*` routes and run APIMatic's generator (CLI/Studio) to output a typed SDK in `sdk/` and import it in the MCP server/README.

## 3. Channel3 API (`trychannel3.com/developers` — $1,500 Prize)
- **Actual Endpoints:** `/search` (natural language query + filters returning ranked products, prices, brands, and merchant offers) and `/lookup` (pass product URL for structured variants, images, and metadata). Free tier includes 20,000 searches.
- **Latency & Stability Safeguard:** Fetch 15–20 real products from Channel3 `/search` (specifically items with size/color options like running shoes and apparel) and cache them in Postgres/JSON seed on startup with a "Live Sync from Channel3" toggle. This guarantees `Naive Shop` and `Hardened Shop` load in <50ms during a 9-persona swarm run.

## 4. AG Grid (`ag-grid-react` — $5,000 / $2,000 / $1,000 Prize)
- **Licensing Trap to Avoid:** `ag-grid-enterprise` prints console watermarks and has commercial repo restrictions without a license key. Use **`ag-grid-community` (`v32+`)** with custom full-width detail panels, custom cell renderers (red/green rule badges, PayPal ID copy pills), client-side filtering/sorting, and `themeQuartz` dark styling, OR check the Hackathon Devpost page for the sponsor trial token.

## 5. Render Hosting & Workflows
- Deploy `backend` (FastAPI web service), `frontend` (Next.js web service), and Render Postgres. Include a `/healthz` warm-up endpoint so judges never hit a cold start.