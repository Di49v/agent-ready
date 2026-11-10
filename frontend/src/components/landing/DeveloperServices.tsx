"use client";

import React, { useState } from "react";
import {
  Check,
  Copy,
  ChevronDown,
  ChevronRight,
  Server,
  Layers,
  Key,
} from "lucide-react";

export const DeveloperServices: React.FC = () => {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [activeFaq, setActiveFaq] = useState<number | null>(0);

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const envSample = `# Core Server Configuration
APP_ENV=development
USE_MOCK_BLUEPRINT=true
PAYPAL_API_BASE_URL="https://api-m.sandbox.paypal.com"
REDACT_SENSITIVE_LOGS=true

# Concurrency & Settle Windows (Respecting Sandbox Rate Limits)
MAX_CONCURRENT_BUYERS=5
WEBHOOK_SETTLE_WINDOW_SEC=5
RULE3_SLA_SECONDS=8

# PayPal Sandbox Credentials (developer.paypal.com)
PAYPAL_CLIENT_ID="your_us_business_client_id"
PAYPAL_CLIENT_SECRET="your_us_business_client_secret"
PAYPAL_WEBHOOK_ID="your_webhook_id"
PAYPAL_TEST_CARD_NUMBER="4032033950884192"
PAYPAL_TEST_CARD_EXPIRY="2028-02"
PAYPAL_TEST_CARD_CVV="957"

# Gemini LLM Pool (Automatic Cooldown & Sharding)
GEMINI_MODEL="gemini-3.8-flash"
GEMINI_API_KEYS="key_alpha,key_beta,key_gamma"

# Cryptographic Integrity Secrets
LAB_PROBE_HMAC_SECRET="32_byte_hex_signature_secret"
CART_RECEIPT_HMAC_SECRET="32_byte_hex_cart_approval_secret"`;

  const apiEndpoints = [
    { method: "POST", path: "/v1/targets", desc: "Register a merchant store sandbox target" },
    { method: "POST", path: "/v1/runs", desc: "Initiate an adversarial swarm test run" },
    { method: "GET", path: "/v1/runs/{id}", desc: "Fetch live run status and readiness score (0-100)" },
    { method: "GET", path: "/v1/runs/{id}/findings", desc: "List detected violations with PayPal IDs" },
    { method: "GET", path: "/v1/runs/{id}/events", desc: "Real-time SSE event stream (agent_step, etc.)" },
    { method: "POST", path: "/v1/runs/{id}/rerun", desc: "Re-run same random seed against Hardened Shop" },
    { method: "GET", path: "/v1/runs/{id}/report", desc: "Export comprehensive audit report (JSON/MD)" },
    { method: "GET", path: "/v1/runs/{id}/postman", desc: "Export Postman Collection v2.1.0 for the run" },
    { method: "GET", path: "/v1/badge/{target}.svg", desc: "Generate dynamic SVG readiness score badge" },
    { method: "POST", path: "/webhooks/paypal", desc: "Live PayPal Sandbox webhook listener" },
    { method: "GET", path: "/_lab/ledger", desc: "HMAC-signed read-only store probe endpoint" },
  ];

  const installMethods = [
    { id: "npm", label: "npm", command: "npm install ./sdk" },
    { id: "pnpm", label: "pnpm", command: "pnpm add ./sdk" },
    { id: "yarn", label: "yarn", command: "yarn add ./sdk" },
    { id: "bun", label: "bun", command: "bun add ./sdk" },
  ] as const;

  const [activeInstallMethod, setActiveInstallMethod] = useState<(typeof installMethods)[number]["id"]>("npm");

  const sdkQuickstart = `import { AgentReadyClient } from "@agent-ready/sdk";
import type { RunCreateRequest } from "@agent-ready/sdk";

const client = new AgentReadyClient({
  baseUrl: process.env.AGENTREADY_API_URL || "http://localhost:8000",
  timeoutMs: 30000,
});

const request: RunCreateRequest = {
  target: "naive-shop",
  pack: "full",
  seed: 42,
  policy: "auto",
  replay: true,
};

const run = await client.createRun(request);
const findings = await client.getRunFindings(run.id);
const report = await client.getRunReport(run.id);

console.log("run:", run.id, run.score);
console.log("findings:", findings.length);
console.log("badge:", report.summary.badge_url);
`;

  const ciExample = `import { AgentReadyClient } from "@agent-ready/sdk";

const client = new AgentReadyClient({
  baseUrl: process.env.AGENTREADY_API_URL || "http://localhost:8000",
  apiKey: process.env.LAB_API_KEY,
  timeoutMs: 30000,
});

const run = await client.createRun({
  target: "hardened-shop",
  seed: 42,
  policy: "auto",
  replay: true,
});

const findings = await client.getRunFindings(run.id);
if (findings.some((finding) => finding.severity === "CRITICAL")) {
  console.error("Critical safety findings detected");
  process.exitCode = 1;
}
`;

  const mcpConfigJson = `{
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
}`;

  const faqs = [
    {
      q: "How does the system prevent PayPal Sandbox 429 rate limit errors?",
      a: "We enforce MAX_CONCURRENT_BUYERS = 5 using an asyncio.Semaphore(5). The 9 buyer personas run in 2 fast waves (Wave 1: 5 buyers, Wave 2: 4 buyers), finishing all 9 lanes in ~12 seconds with zero Sandbox throttling.",
    },
    {
      q: "What is Blueprint-First Isolation (USE_MOCK_BLUEPRINT=true)?",
      a: "When USE_MOCK_BLUEPRINT=true or mode='replay', data is served from backend/app/mocks/replay_fixtures.py through the exact same service interface as live engines. This guarantees an instant (<20ms) full-stack demo and a zero-latency safety net for hackathon judges.",
    },
    {
      q: "Why does Supabase Postgres require statement_cache_size=0?",
      a: "Supabase transaction pooling (PgBouncer) does not support prepared statements across pooled connections. Setting connect_args={'statement_cache_size': 0} in SQLAlchemy create_async_engine guarantees 100% connection compatibility.",
    },
    {
      q: "How does Gemini Key Sharding work?",
      a: "GeminiKeySharder rotates through a comma-separated pool of GEMINI_API_KEYS with an automatic 60-second cooldown on HTTP 429, falling back to pre-cached 12-bug explanation templates if offline.",
    },
  ];

  return (
    <section className="py-16 md:py-24 border-b border-[var(--border)] bg-[var(--bg)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="flex flex-col text-left max-w-2xl mb-12">
          <span className="text-xs font-mono uppercase tracking-wider text-[var(--text-muted)] mb-2 font-medium">
            Developer Services &amp; Spec
          </span>
          <h2 className="font-heading font-semibold text-2xl sm:text-4xl text-[var(--accent)] tracking-tight">
            Developer Services &amp; Configuration
          </h2>
          <p className="mt-3 text-[15px] sm:text-base text-[var(--text-muted)] leading-relaxed">
            Specification details for environment variables, system requirements, REST endpoints, and architectural troubleshooting.
          </p>
        </div>

        {/* 3-Column Specifications Grid */}
        <div className="hairline-grid grid-cols-1 md:grid-cols-3 mb-10 bg-[var(--border)] border border-[var(--border)] rounded-md">
          {/* Card 1: Requirements */}
          <div className="bg-[var(--surface)] p-6 flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center mb-3">
                <Server className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="text-base font-heading font-semibold text-[var(--text)]">
                System Requirements
              </h3>
              <ul className="mt-3 space-y-1.5 text-xs font-mono text-[var(--text-muted)]">
                <li>• Python: 3.11 or higher</li>
                <li>• Package Manager: uv (Astral)</li>
                <li>• Node.js: 20.x or higher (npm)</li>
                <li>• Database: Supabase PostgreSQL</li>
                <li>• Sandbox: PayPal US Business + Personal</li>
              </ul>
            </div>
            <div className="mt-6 pt-3 border-t border-[var(--border)] text-[11px] font-mono text-[var(--text-muted)]">
              Cross-Platform: Windows, macOS, Linux
            </div>
          </div>

          {/* Card 2: Monorepo Architecture */}
          <div className="bg-[var(--surface)] p-6 flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center mb-3">
                <Layers className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="text-base font-heading font-semibold text-[var(--text)]">
                Monorepo Layout
              </h3>
              <ul className="mt-3 space-y-1.5 text-xs font-mono text-[var(--text-muted)]">
                <li>• backend/ — FastAPI + SQLAlchemy + Chaos</li>
                <li>• frontend/ — Next.js 16 + AG Grid Quartz</li>
                <li>• mcp/ — stdio MCP Server (5 tools)</li>
                <li>• sdk/ — APIMatic Generated TypeScript SDK</li>
                <li>• openapi/ — OpenAPI 3.1 specification</li>
              </ul>
            </div>
            <div className="mt-6 pt-3 border-t border-[var(--border)] text-[11px] font-mono text-[var(--text-muted)]">
              117 Automated Tests Passing
            </div>
          </div>

          {/* Card 3: Cryptographic Bounds */}
          <div className="bg-[var(--surface)] p-6 flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--highlight)] flex items-center justify-center mb-3">
                <Key className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="text-base font-heading font-semibold text-[var(--text)]">
                Integrity &amp; Security
              </h3>
              <ul className="mt-3 space-y-1.5 text-xs font-mono text-[var(--text-muted)]">
                <li>• HMAC-SHA256 Cart Receipts</li>
                <li>• PayPal Webhook Signature Verifier</li>
                <li>• Auto PAN &amp; Bearer Log Redaction</li>
                <li>• Target Allowlist &amp; SSRF Shield</li>
                <li>• Rate Limiting: 10 runs / 10 mins</li>
              </ul>
            </div>
            <div className="mt-6 pt-3 border-t border-[var(--border)] text-[11px] font-mono text-[var(--highlight)]">
              Abuse Guard Active
            </div>
          </div>
        </div>

        {/* Environment Variables Template Box */}
        <div className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6 mb-10">
          <div className="flex items-center justify-between mb-3 border-b border-[var(--border)] pb-3">
            <div>
              <span className="text-xs font-mono text-[var(--text-muted)] font-medium">
                Configuration Template
              </span>
              <h3 className="text-base font-heading font-semibold text-[var(--text)] mt-0.5">
                backend/.env.example
              </h3>
            </div>
            <button
              onClick={() => handleCopy(envSample, "env")}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded border border-[var(--border)] bg-[var(--surface-sunken)] text-xs font-mono text-[var(--text-muted)] hover:text-[var(--text)] hover:border-[var(--border-strong)] transition-colors cursor-pointer"
            >
              {copiedKey === "env" ? (
                <>
                  <Check className="w-3.5 h-3.5 text-[var(--pass)] stroke-[1.5]" />
                  <span className="text-[var(--pass)]">Copied .env</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5 stroke-[1.5]" />
                  <span>Copy Template</span>
                </>
              )}
            </button>
          </div>
          <pre className="p-3.5 rounded-md border border-[var(--code-border)] bg-[var(--code-bg)] text-[var(--code-text)] text-xs font-mono overflow-x-auto leading-relaxed max-h-72">
            <code>{envSample}</code>
          </pre>
        </div>

        {/* Package Installation & Quick Starts */}
        <div className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6 mb-10">
          <div className="mb-4 border-b border-[var(--border)] pb-3">
            <span className="text-xs font-mono text-[var(--text-muted)] font-medium">
              SDK &amp; MCP Integration
            </span>
            <h3 className="text-base font-heading font-semibold text-[var(--text)] mt-0.5">
              Install the SDK and wire in Claude Desktop / Cursor
            </h3>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-[1.2fr_0.8fr] gap-5">
            <div className="space-y-4">
              <div className="flex items-center gap-2 border-b border-[var(--border)] pb-2">
                {installMethods.map((method) => (
                  <button
                    key={method.id}
                    type="button"
                    onClick={() => setActiveInstallMethod(method.id)}
                    className={`px-2.5 py-1.5 text-[11px] font-mono rounded border transition-colors cursor-pointer ${
                      activeInstallMethod === method.id
                        ? "bg-[var(--surface-sunken)] text-[var(--accent)] border-[var(--accent)]"
                        : "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)] hover:text-[var(--text)]"
                    }`}
                  >
                    {method.label}
                  </button>
                ))}
              </div>

              <div className="rounded-md border border-[var(--border)] bg-[var(--code-bg)] p-3">
                <div className="flex items-center justify-between gap-3 mb-2">
                  <span className="text-[10px] uppercase tracking-wide font-mono text-[var(--text-dim)]">
                    Install command
                  </span>
                  <button
                    type="button"
                    onClick={() => handleCopy(installMethods.find((item) => item.id === activeInstallMethod)?.command ?? "", `sdk-install-${activeInstallMethod}`)}
                    className="inline-flex items-center gap-1.5 px-2 py-1 rounded border border-[var(--border)] bg-[var(--surface)] text-[10px] font-mono text-[var(--text-muted)] hover:text-[var(--text)] transition-colors cursor-pointer"
                  >
                    {copiedKey === `sdk-install-${activeInstallMethod}` ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-[var(--pass)] stroke-[1.5]" />
                        <span className="text-[var(--pass)]">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5 stroke-[1.5]" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>
                <pre className="text-xs font-mono text-[var(--code-text)] whitespace-pre-wrap break-words">
                  <code>{installMethods.find((item) => item.id === activeInstallMethod)?.command}</code>
                </pre>
              </div>

              <div className="rounded-md border border-[var(--border)] bg-[var(--surface-sunken)] p-3 text-xs text-[var(--text-muted)] leading-relaxed">
                <span className="font-mono text-[var(--text-muted)]">Note:</span> The SDK is checked into this repo under <span className="font-mono text-[var(--text)]">./sdk</span> and is not yet published to npm. Install from the repository checkout with <span className="font-mono text-[var(--text)]">cd sdk && npm install && npm run build</span>, then add it from the local path in your app: <span className="font-mono text-[var(--text)]">npm install ./sdk</span> or <span className="font-mono text-[var(--text)]">pnpm add ./sdk</span>.
              </div>
            </div>

            <div className="space-y-4">
              <div className="rounded-md border border-[var(--border)] bg-[var(--surface-sunken)] p-3">
                <div className="flex items-center justify-between gap-3 mb-2">
                  <span className="text-[10px] uppercase tracking-wide font-mono text-[var(--text-dim)]">TypeScript quickstart</span>
                  <button
                    type="button"
                    onClick={() => handleCopy(sdkQuickstart, "sdk-quickstart")}
                    className="inline-flex items-center gap-1.5 px-2 py-1 rounded border border-[var(--border)] bg-[var(--surface)] text-[10px] font-mono text-[var(--text-muted)] hover:text-[var(--text)] transition-colors cursor-pointer"
                  >
                    {copiedKey === "sdk-quickstart" ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-[var(--pass)] stroke-[1.5]" />
                        <span className="text-[var(--pass)]">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5 stroke-[1.5]" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>
                <pre className="max-h-64 overflow-auto text-[11px] leading-relaxed font-mono text-[var(--code-text)] whitespace-pre-wrap break-words">
                  <code>{sdkQuickstart}</code>
                </pre>
              </div>

              <div className="rounded-md border border-[var(--border)] bg-[var(--surface-sunken)] p-3">
                <div className="flex items-center justify-between gap-3 mb-2">
                  <span className="text-[10px] uppercase tracking-wide font-mono text-[var(--text-dim)]">CI/CD smoke check</span>
                  <button
                    type="button"
                    onClick={() => handleCopy(ciExample, "sdk-ci")}
                    className="inline-flex items-center gap-1.5 px-2 py-1 rounded border border-[var(--border)] bg-[var(--surface)] text-[10px] font-mono text-[var(--text-muted)] hover:text-[var(--text)] transition-colors cursor-pointer"
                  >
                    {copiedKey === "sdk-ci" ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-[var(--pass)] stroke-[1.5]" />
                        <span className="text-[var(--pass)]">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5 stroke-[1.5]" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>
                <pre className="max-h-40 overflow-auto text-[11px] leading-relaxed font-mono text-[var(--code-text)] whitespace-pre-wrap break-words">
                  <code>{ciExample}</code>
                </pre>
              </div>
            </div>
          </div>

          <div className="mt-5 rounded-md border border-[var(--border)] bg-[var(--surface-sunken)] p-4">
            <div className="flex items-center justify-between gap-3 mb-2">
              <div>
                <span className="text-[10px] uppercase tracking-wide font-mono text-[var(--text-muted)]">MCP config</span>
                <h4 className="text-sm font-heading font-semibold text-[var(--text)] mt-0.5">Claude Desktop / Cursor</h4>
              </div>
              <button
                type="button"
                onClick={() => handleCopy(mcpConfigJson, "mcp-config")}
                className="inline-flex items-center gap-1.5 px-2 py-1 rounded border border-[var(--border)] bg-[var(--surface)] text-[10px] font-mono text-[var(--text-muted)] hover:text-[var(--text)] transition-colors cursor-pointer"
              >
                {copiedKey === "mcp-config" ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-[var(--pass)] stroke-[1.5]" />
                    <span className="text-[var(--pass)]">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5 stroke-[1.5]" />
                    <span>Copy JSON</span>
                  </>
                )}
              </button>
            </div>
            <pre className="text-[11px] leading-relaxed font-mono text-[var(--code-text)] whitespace-pre-wrap break-words overflow-x-auto">
              <code>{mcpConfigJson}</code>
            </pre>
          </div>
        </div>

        {/* API Endpoints Table */}
        <div className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6 mb-10">
          <div className="mb-3 border-b border-[var(--border)] pb-3">
            <span className="text-xs font-mono text-[var(--text-muted)] font-medium">
              OpenAPI 3.1 Surface
            </span>
            <h3 className="text-base font-heading font-semibold text-[var(--text)] mt-0.5">
              Core REST API Endpoints (/v1/*)
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono border-collapse">
              <thead>
                <tr className="border-b border-[var(--border)] text-[var(--text-dim)]">
                  <th className="py-2 px-3 font-medium">METHOD</th>
                  <th className="py-2 px-3 font-medium">ENDPOINT</th>
                  <th className="py-2 px-3 font-medium">FUNCTION &amp; PAYLOAD</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border)] text-[var(--text-muted)]">
                {apiEndpoints.map((ep) => (
                  <tr key={ep.path} className="hover:bg-[var(--surface-hover)] transition-colors">
                    <td className="py-2 px-3">
                      <span
                        className={`px-1.5 py-0.5 rounded font-mono text-[10px] font-semibold ${
                          ep.method === "POST"
                            ? "bg-[var(--surface-sunken)] text-[var(--text-muted)] border border-[var(--border)]"
                            : "bg-[var(--surface-sunken)] text-[var(--text)] border border-[var(--border)]"
                        }`}
                      >
                        {ep.method}
                      </span>
                    </td>
                    <td className="py-2 px-3 font-medium text-[var(--text)]">
                      {ep.path}
                    </td>
                    <td className="py-2 px-3">{ep.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Troubleshooting Accordion */}
        <div className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-5 sm:p-6">
          <div className="mb-3 border-b border-[var(--border)] pb-3">
            <span className="text-xs font-mono text-[var(--highlight)] font-medium">
              DevOps &amp; Sandbox Edge Cases
            </span>
            <h3 className="text-base font-heading font-semibold text-[var(--text)] mt-0.5">
              Installation Troubleshooting &amp; FAQs
            </h3>
          </div>
          <div className="space-y-2">
            {faqs.map((faq, idx) => {
              const isOpen = activeFaq === idx;
              return (
                <div
                  key={faq.q}
                  className="rounded-md border border-[var(--border)] bg-[var(--surface-sunken)] overflow-hidden"
                >
                  <button
                    onClick={() => setActiveFaq(isOpen ? null : idx)}
                    className="w-full text-left px-3.5 py-2.5 flex items-center justify-between text-xs sm:text-sm font-sans font-medium text-[var(--text)] hover:bg-[var(--surface)] transition-colors cursor-pointer"
                  >
                    <span>{faq.q}</span>
                    {isOpen ? (
                      <ChevronDown className="w-4 h-4 text-[var(--text-muted)] flex-shrink-0 stroke-[1.5]" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-[var(--text-dim)] flex-shrink-0 stroke-[1.5]" />
                    )}
                  </button>
                  {isOpen && (
                    <div className="px-3.5 pb-3.5 pt-1 text-xs text-[var(--text-muted)] leading-relaxed font-sans border-t border-[var(--border)]">
                      {faq.a}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};
