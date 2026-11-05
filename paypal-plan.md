# PayPal Integration Plan & Contract Sheet

**Host Application:** `agent-ready` backend (FastAPI, Python 3.11+, Asyncio)  
**SDK Package:** `paypal==2.29` (APIMatic generated, import root: `paypal`)  
**Sync vs Async Decision:** `AsyncPaypalClient` (`AsyncClient`) — The backend runs purely asynchronous event loops with FastAPI and `asyncpg`.  
**Base URL:** `https://api-m.sandbox.paypal.com` (Hard-pinned Sandbox).

---

## 1. Repo Survey & Toolchain Baseline

- **Framework / Runtime:** FastAPI + Uvicorn, Python 3.11+.
- **Package Manager:** `uv`.
- **Installed Version:** `paypal==2.29` from `git+https://github.com/context-plugins/paypal-python-sdk.git@main`.
- **Client Class to Instantiate:** `paypal.AsyncPaypalClient`.
- **Teardown Obligation:** Must await `client.aclose()` on application shutdown.
- **Authentication:** OAuth 2.0 Client Credentials flow (`ClientCredentials(client_id=..., client_secret=...)`) with automatic bearer caching via SDK internal `AsyncClientCredentialsTokenSource`.
- **Join Key Invariant:** Every order specifies `purchase_units[0].custom_id = cart_id` for deterministic cross-ledger reconciliation with store probe records.
- **Idempotency Header:** All mutation calls provide `pay_pal_request_id` (mapping from client `Idempotency-Key`).
- **Concurrency Guard:** All swarm runs enforce `MAX_CONCURRENT_BUYERS = 5` via `asyncio.Semaphore(5)` to avoid Sandbox rate limits (`429`).

---

## 2. In-Scope Operations & Contract Sheet

### Operation 1: Create Order
- **Resource:** `client.orders.create_order`
- **Method & Path:** `POST /v2/checkout/orders`
- **Signature:**
  ```python
  async def create_order(
      self,
      body: OrderRequest | OrderRequestDict,
      *,
      pay_pal_mock_response: str | None = None,
      pay_pal_request_id: str | None = None,
      pay_pal_partner_attribution_id: str | None = None,
      pay_pal_client_metadata_id: str | None = None,
      prefer: str | None = "return=minimal",
      pay_pal_auth_assertion: str | None = None,
      request_options: RequestOptionsOrDict | None = None,
  ) -> Order
  ```
- **Required Body Fields:** `intent="CAPTURE"`, `purchase_units=[PurchaseUnitRequestDict(...)]`
- **Optional / Unattended Card Funding:** `payment_source=PaymentSourceDict(card=CardRequestDict(number=..., expiry="YYYY-MM", security_code=..., name=...))`
- **Key Header:** `pay_pal_request_id` (stores key up to 72 hours for single-step capture calls).
- **Return Type:** `paypal.models.Order` (with `id`, `status`, `links`).
- **Raises:** `paypal.core.ApiError` (wrapping `CreateOrderErrorBody | RawError`).

### Operation 2: Capture Order
- **Resource:** `client.orders.capture_order`
- **Method & Path:** `POST /v2/checkout/orders/{id}/capture`
- **Signature:**
  ```python
  async def capture_order(
      self,
      id_: str,
      *,
      pay_pal_mock_response: str | None = None,
      pay_pal_request_id: str | None = None,
      prefer: str | None = "return=minimal",
      pay_pal_client_metadata_id: str | None = None,
      pay_pal_auth_assertion: str | None = None,
      body: OrderCaptureRequest | OrderCaptureRequestDict | None = None,
      request_options: RequestOptionsOrDict | None = None,
  ) -> Order
  ```
- **Key Header:** `pay_pal_request_id` (idempotent retry).
- **Return Type:** `paypal.models.Order` (contains `purchase_units[0].payments.captures[0].id`).
- **Raises:** `paypal.core.ApiError` (wrapping `CaptureOrderErrorBody | RawError`).

### Operation 3: Refund Captured Payment
- **Resource:** `client.payments.refund_captured_payment`
- **Method & Path:** `POST /v2/payments/captures/{capture_id}/refund`
- **Signature:**
  ```python
  async def refund_captured_payment(
      self,
      capture_id: str,
      *,
      pay_pal_mock_response: str | None = None,
      pay_pal_request_id: str | None = None,
      prefer: str | None = "return=minimal",
      pay_pal_auth_assertion: str | None = None,
      body: RefundRequest | RefundRequestDict | None = None,
      request_options: RequestOptionsOrDict | None = None,
  ) -> Refund
  ```
- **Return Type:** `paypal.models.Refund` (`id`, `status="COMPLETED"`, `amount`).
- **Raises:** `paypal.core.ApiError` (wrapping `RefundCapturedPaymentErrorBody | RawError`).

### Operation 4: Void Authorized Payment
- **Resource:** `client.payments.void_payment`
- **Method & Path:** `POST /v2/payments/authorizations/{authorization_id}/void`
- **Signature:**
  ```python
  async def void_payment(
      self,
      authorization_id: str,
      *,
      pay_pal_mock_response: str | None = None,
      pay_pal_auth_assertion: str | None = None,
      pay_pal_request_id: str | None = None,
      prefer: str | None = "return=minimal",
      request_options: RequestOptionsOrDict | None = None,
  ) -> PaymentAuthorization
  ```
- **Return Type:** `paypal.models.PaymentAuthorization` (`id`, `status="VOIDED"`).
- **Raises:** `paypal.core.ApiError` (wrapping `VoidPaymentErrorBody | RawError`).

### Operation 5: Verify Webhook Signature (Notifications API)
- **Direct HTTP Resource:** `POST https://api-m.sandbox.paypal.com/v1/notifications/verify-webhook-signature`
- **Note:** Called via client raw transport or async httpx using OAuth2 bearer token.
- **Request Body:**
  ```json
  {
    "auth_algo": "<PAYPAL-AUTH-ALGO>",
    "cert_url": "<PAYPAL-CERT-URL>",
    "transmission_id": "<PAYPAL-TRANSMISSION-ID>",
    "transmission_sig": "<PAYPAL-TRANSMISSION-SIG>",
    "transmission_time": "<PAYPAL-TRANSMISSION-TIME>",
    "webhook_id": "<PAYPAL-WEBHOOK-ID>",
    "webhook_event": { ... }
  }
  ```
- **Expected Response:** `{"verification_status": "SUCCESS" | "FAILURE"}`.

### Operation 6: Process Sandbox Chargeback (Sandbox-Only Simulation)
- **Direct HTTP Resource:** `POST https://api-m.sandbox.paypal.com/v2/customer-support/process-chargeback`
- **Payload:** `{"dispute_id": "...", "action": "ACCEPT_DISPUTE"}` or card chargeback negative testing.

---

## 3. Duplicate Claims Table

| Write | Where the claim is stored | What rejects the second one | Where that rejection is caught | Where in the code |
| :--- | :--- | :--- | :--- | :--- |
| Create Order (`create_order`) | `IdempotencyRecord` in Store DB / Memory Cache | Duplicate `cart_id` or `Idempotency-Key` active lock | `HTTP 409 Conflict` or return cached Order | `TBD` |
| Capture Order (`capture_order`) | `StoreOrder.capture_status` in DB | Status check (`ALREADY_CAPTURED`) or `PayPal-Request-Id` replay | Invariant check or `ApiError` `ORDER_ALREADY_CAPTURED` | `TBD` |
| Refund Capture (`refund_captured_payment`) | `StoreRefund` ledger | Total refunded sum exceeding original capture amount | `HTTP 422 Unprocessable Entity` (`REFUND_EXCEEDS_CAPTURE`) | `TBD` |

---

## 4. Required Reading Block

- MUST load `python-client-initialization` (Async client factory and lifetime handling)
- MUST load `python-calling-endpoints` (Keyword-only args, response decoding)
- MUST load `python-authentication` (ClientCredentials OAuth token caching)
- MUST load `python-error-handling` (`ApiError` inspection and status code decoding)
- MUST load `python-models` (Pydantic / TypedDict request modeling)
- MUST load `python-configuration-resilience` (Timeout, retries, and rate limits)
- MUST load `python-testing` (Transport isolation for pytest suites)

