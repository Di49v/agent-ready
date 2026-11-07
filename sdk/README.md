# `@agent-ready/sdk`

> Official TypeScript SDK for **AgentReady Lab**, generated from OpenAPI 3.1 specification via **APIMatic**.

Adversarial crash-testing, dual-ledger reconciliation, and self-healing middleware for autonomous AI agent commerce on PayPal Sandbox.

---

## Installation

```bash
npm install @agent-ready/sdk
```

---

## Quickstart

```typescript
import { AgentReadyClient } from "@agent-ready/sdk";

// Initialize client
const client = new AgentReadyClient({
  baseUrl: process.env.AGENTREADY_API_URL || "http://localhost:8000",
  apiKey: process.env.LAB_API_KEY,
});

async function main() {
  // 1. Health check
  const health = await client.healthCheck();
  console.log("Lab Health:", health);

  // 2. Start an adversarial crash test on Naive Shop
  const run = await client.createRun({
    target: "naive-shop",
    pack: "full",
    seed: 42,
    policy: "auto",
  });
  console.log(`Run started: ${run.id} | Initial Score: ${run.score}/100`);

  // 3. Inspect findings with PayPal Sandbox evidence IDs
  const findings = await client.getRunFindings(run.id);
  console.log(`Found ${findings.length} vulnerabilities:`);
  findings.forEach((f) => {
    console.log(`- [${f.severity}] ${f.title} (Evidence: ${f.evidence_ids.join(", ")})`);
  });

  // 4. Re-run same seed on Hardened Shop (Red to Green transition)
  const rerun = await client.rerunRun(run.id, {
    target_override: "hardened-shop",
  });
  console.log(`Remediated Score: ${rerun.score}/100`);
}

main().catch(console.error);
```

---

## API Operations

| Method | Operation ID | Description |
|---|---|---|
| `client.healthCheck()` | `healthCheck` | Checks service health and PayPal Sandbox vitality |
| `client.listTargets()` | `listTargets` | Returns registered targets (`naive-shop`, `hardened-shop`) |
| `client.createTarget(target)` | `createTarget` | Registers a custom sandbox target store |
| `client.listPersonas()` | `listPersonas` | Returns the 9 adversarial AI buyer personas |
| `client.createRun(req)` | `createRun` | Starts a 9-lane adversarial crash test |
| `client.getRun(id)` | `getRun` | Retrieves run status and score |
| `client.getRunFindings(id)` | `getRunFindings` | Returns findings with PayPal order/capture/dispute evidence IDs |
| `client.getRunLedger(id)` | `getRunLedger` | Returns side-by-side PayPal vs. Store ledger comparison |
| `client.getRunReport(id)` | `getRunReport` | Returns structured JSON audit report |
| `client.getRunReportMarkdown(id)` | `getRunReport` | Returns publication-grade Markdown audit document |
| `client.rerunRun(id, req)` | `rerunRun` | Replays exact same seed to verify fix remediation |
| `client.getScoreBadgeSvg(target)` | `getScoreBadge` | Generates dynamic SVG safety score badge |
| `client.getBenchmarkMatrix()` | `getBenchmarkMatrix` | Returns 12-bug benchmark detection verification matrix |

---

## Error Handling

This SDK strictly converts HTTP errors into typed `AgentReadyApiError` instances containing RFC 9457 Problem Details:

```typescript
import { AgentReadyApiError } from "@agent-ready/sdk";

try {
  await client.createRun({ target: "non-existent-store" });
} catch (error) {
  if (error instanceof AgentReadyApiError) {
    console.error("RFC 9457 Code:", error.problem.code);
    console.error("HTTP Status:", error.status);
    console.error("Detail:", error.problem.detail);
  }
}
```

---

## License

Apache-2.0 © AgentReady Lab Team

