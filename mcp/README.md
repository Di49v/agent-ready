# `@agent-ready/mcp-server`

> **Model Context Protocol (MCP) Server for AgentReady Lab**  
> Exposes autonomous e-commerce adversarial testing, dual-ledger reconciliation, and self-healing tools directly into **Google Antigravity IDE**, **Claude Desktop**, and MCP-compliant AI assistants.

---

## ⚡ 1. Overview & Capability Roster

The AgentReady MCP Server implements the **Model Context Protocol (MCP)** specification via `@modelcontextprotocol/sdk` on the standard input/output (`stdio`) transport. It empowers coding assistants to automatically audit e-commerce stores, detect unauthorized mutations across PayPal Sandbox transactions, inspect cryptographic cart receipts, and apply verified APIMatic patches with a single prompt.

### Exposed MCP Tools (Section B3.10)

| Tool Name | Purpose | Key Inputs | Output Format |
| :--- | :--- | :--- | :--- |
| `start_crash_test` | Triggers a 9-lane adversarial crash test against a target store | `target` (`naive-shop` \| `hardened-shop`), `pack` (`full` \| `core`), `seed` (`number`), `policy` (`auto` \| `observe`) | Markdown summary with Run ID, Safety Score `/100`, and finding breakdown. |
| `list_findings` | Lists all invariant violations with real PayPal Sandbox evidence IDs | `run_id` (`string`) | Markdown table detailing Rule #, Severity, Title, and PayPal IDs (`PP-ORD-*`, `PP-CAP-*`, `PP-REF-*`). |
| `explain_finding` | Grounded root-cause analysis referencing APIMatic PayPal SDK v2.29 context | `finding_id` (`string`), `run_id` (`string`) | Plain-English root cause, invariant explanation, and protocol boundary guidance. |
| `suggest_fix` | Generates an APIMatic-grounded unified diff code patch ready for 1-click apply | `finding_id` (`string`), `run_id` (`string`) | Unified diff patch block with standard `--- a/` and `+++ b/` file headers. |
| `rerun` | Replays exact same seed against `hardened-shop` to verify Red-to-Green transition | `run_id` (`string`), `target_override` (`string`, default `hardened-shop`) | Remediated score verification (`18/100` 🔴 $\rightarrow$ `95/100` 🟢). |

---

## 🛠️ 2. IDE Installation & Configuration

### Option A: Google Antigravity IDE (Recommended)

1. Open **Google Antigravity IDE**.
2. Press `Ctrl+,` (or `Cmd+,` on macOS) and navigate to **Settings > Model Context Protocol > Open MCP Config**.
3. Add the `agent-ready` server to your `mcpServers` configuration:

```json
{
  "mcpServers": {
    "agent-ready": {
      "command": "node",
      "args": ["d:/agent-ready/mcp/dist/server.js"],
      "env": {
        "AGENTREADY_API_URL": "http://localhost:8000",
        "LAB_API_KEY": ""
      }
    }
  }
}
```

> **Note:** If testing with a deployed cloud lab instance (e.g. Render), replace `http://localhost:8000` with your public API endpoint (e.g., `https://agent-ready-api.onrender.com`).

---

### Option B: Claude Desktop

Add the server to your Claude Desktop configuration file:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "agent-ready": {
      "command": "node",
      "args": ["d:/agent-ready/mcp/dist/server.js"],
      "env": {
        "AGENTREADY_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

---

## 🏗️ 3. Building from Source

To compile the TypeScript MCP server into runnable JavaScript:

```bash
cd d:\agent-ready\mcp
npm install
npm run build
```

This compiles `server.ts` into `dist/server.js`.

---

## 💬 4. Sample Assistant Dialogue & Walkthrough

Once registered, you can issue natural language prompts in your IDE's assistant chat:

### Step 1 — Audit Naive Shop
> **User Prompt:**  
> *"Run an adversarial crash test on naive-shop to check our PayPal compliance."*

> **MCP Execution:**  
> The agent invokes `start_crash_test({ target: "naive-shop", seed: 42, policy: "auto" })`.  
> Returns score `18/100` with 6 critical findings.

### Step 2 — Inspect Evidence
> **User Prompt:**  
> *"Show me the detected invariant violations and the PayPal evidence IDs."*

> **MCP Execution:**  
> The agent invokes `list_findings({ run_id: "run_42_naive_shop" })`.  
> Returns Markdown table highlighting `PP-CAP-429188` (double capture) and `PP-REF-109281` (duplicate refund).

### Step 3 — Request Grounded Patch
> **User Prompt:**  
> *"Suggest an APIMatic-grounded fix for the double capture vulnerability."*

> **MCP Execution:**  
> The agent invokes `suggest_fix({ finding_id: "BUG_NO_IDEMPOTENCY" })`.  
> Returns unified diff integrating `PayPal-Request-Id` and response caching.

### Step 4 — Verify Red-to-Green Transition
> **User Prompt:**  
> *"Apply the fix and re-run the exact same seed to verify compliance."*

> **MCP Execution:**  
> The agent invokes `rerun({ run_id: "run_42_naive_shop", target_override: "hardened-shop" })`.  
> Returns verification confirmation: Score jumps from **18/100** to **95/100** with 0 active code-bug vulnerabilities!

---

## 📜 License

Apache-2.0 © 2026 AgentReady Lab Team.

