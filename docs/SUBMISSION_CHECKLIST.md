# AgentReady Lab — Final Hackathon Submission Checklist

> **Deadline:** Wednesday, November 12, 2026 at 12:00 PM PT (1:30 AM IST, Nov 13, 2026).  
> **Recommended Submission Target:** Submit at least 4 hours before deadline to allow for network or processing buffers.

---

## 📋 1. Devpost Submission Form Fields

| Field | Value / Content |
|---|---|
| **Project Title** | `AgentReady Lab` |
| **Elevator Pitch / Tagline** | *PayPal protects the payment. Nobody tests the merchant's side of an agent order. AgentReady Lab does.* |
| **Track & Categories** | - Grand Prize ($12,000 / $8,000 / $5,000)<br>- Best Use of Agentic Commerce ($5,000)<br>- Best Use of PayPal + AI ($5,000)<br>- Best Use of APIMatic ($1,000)<br>- Best Demo Delivery ($5,000)<br>- AG Grid Sponsor Prize ($5,000)<br>- Channel3 Sponsor Prize ($1,500) |
| **Primary Project Link (GitHub)** | `https://github.com/LOQ/agent-ready` |
| **Working Demo URL** | `https://agent-ready.onrender.com` (Ensure no login / zero-friction judge path) |
| **Video Link** | YouTube public link (Max 2:45 duration, see [`docs/DEMO_VIDEO_SCRIPT.md`](DEMO_VIDEO_SCRIPT.md)) |
| **Built With (Tags)** | `paypal`, `apimatic`, `ag-grid`, `channel3`, `fastapi`, `next.js`, `typescript`, `python`, `supabase`, `postgresql`, `gemini`, `mcp`, `model-context-protocol`, `render`, `tailwind-css` |

---

## 🎥 2. YouTube Video Upload Specifications

1. **Duration:** Must be strictly **under 3:00** (Target: `2:40`).
2. **Title:** `AgentReady Lab — Crash-Testing & Dual-Ledger Self-Healing for Agentic Commerce (PayPal Hackathon 2026)`
3. **Visibility:** **Public** or **Unlisted** (Never Private). Set category to *Science & Technology*.
4. **Description:**
   ```text
   AgentReady Lab is an adversarial crash-testing, dual-ledger compliance auditing, and self-healing platform for autonomous AI agent commerce on the PayPal Sandbox.

   "PayPal protects the payment. Nobody tests the merchant's side of an agent order. AgentReady Lab does."

   GitHub Repository: https://github.com/LOQ/agent-ready
   Live Demo: https://agent-ready.onrender.com
   Built with: PayPal Sandbox v2, APIMatic SDK, AG Grid Quartz, Channel3, FastAPI, Next.js, and Render.
   ```
5. **Quality:** Export in `1080p (1920x1080) 60fps`, H.264 MP4.

---

## 🏆 3. Sponsor Requirements & Proof

### A. APIMatic ($1,000 Category)
- [x] Integrate official APIMatic PayPal Python SDK (`paypal==2.29` in `pyproject.toml`).
- [x] Ground fix engine with APIMatic context (`backend/app/fix_engine/templates.py`).
- [x] Clean OpenAPI 3.1 schema exported via `backend/scripts/export_openapi.py`.
- [x] Typed TypeScript SDK generated in `sdk/` (`@agent-ready/sdk`).
- [ ] **Form Action:** If APIMatic provides a Free Subscription / Repo Proof form on the Devpost resources page, submit your public GitHub repository URL before deadline.

### B. PayPal ($5,000 Best Use of PayPal + AI & Agentic Commerce)
- [x] Hard-pinned Sandbox endpoint (`https://api-m.sandbox.paypal.com`).
- [x] Orders v2 (`/v2/checkout/orders`), Payments v2 (`/v2/payments/captures`), Webhooks, Shipment Tracking, and Disputes.
- [x] Reconciler evaluates ground truth directly from PayPal's authoritative API.
- [x] Sandbox buyer test credentials listed in `README.md`.

### C. AG Grid ($5,000 / $2,000 / $1,000)
- [x] AG Grid Quartz dark theme implemented with exposed 1px hairline grid.
- [x] Cell change flashing (`defaultColDef={{ enableCellChangeFlash: true }}`).
- [x] Real-time async transactions via `applyTransactionAsync` during live Judge Arena SSE streams.
- [x] Custom status pill micro-renderers for findings and ledger discrepancies.

### D. Channel3 ($1,500)
- [x] Real e-commerce product catalog integration (`backend/app/services/channel3_service.py`).
- [x] Real-time ambiguous variant resolution (`prod_running_shoes_002`) requiring size/color selection.
- [x] Channel3 Product Card displayed side-by-side with wire payloads in `LiveStoreCartInspector.tsx`.

### E. Render
- [x] `render.yaml` zero-downtime blueprint configuration committed.
- [x] `/healthz` warmup endpoint implemented to prevent cold starts.

---

## 🧪 4. Final Workstation Pre-Flight Verification

Run the following commands in order to confirm everything is green before submission:

```powershell
cd d:\agent-ready\backend

# 1. Run all 117 automated unit and integration tests
uv run pytest tests/ -v

# 2. Run the automated smoke test dry run (vitality, naive, hardened, replay, secrets, postman)
uv run python scripts/smoke_test.py

# 3. Run the 12-Bug Benchmark Matrix (12/12 true positives, 0 false alarms)
uv run python scripts/run_self_test_matrix.py

# 4. Verify OpenAPI export
uv run python scripts/export_openapi.py
```

---

## 🏷️ 5. Final Git Tag & Release

Once all tests pass and documentation is verified:

```powershell
cd d:\agent-ready
git add .
git commit -m "chore(release): prepare final hackathon submission package v1.0.0"
git tag -a v1.0.0-hackathon -m "AgentReady Lab — PayPal & AI Commerce Hackathon 2026 Final Release"
git push origin main --tags
```

