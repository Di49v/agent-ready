"use client";

import React, { useState } from "react";
import {
  BookOpen,
  Terminal,
  Layers,
  ShieldCheck,
  Cpu,
  FileCode,
  Binary,
  Split,
  ChevronRight,
} from "lucide-react";
import { PERSONAS_LIST, INVARIANTS_LIST } from "@/lib/constants";

export const DocumentationHub: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>("getting-started");

  const tabs = [
    { id: "getting-started", label: "1. Getting Started", icon: BookOpen },
    { id: "architecture", label: "2. Architecture", icon: Layers },
    { id: "personas", label: "3. 9 AI Personas", icon: Cpu },
    { id: "invariants", label: "4. 6 Invariant Rules", icon: ShieldCheck },
    { id: "merchant-guard", label: "5. Merchant Guard", icon: FileCode },
    { id: "reconciliation", label: "6. Reconciliation", icon: Split },
    { id: "mcp-sdk", label: "7. MCP & SDK", icon: Terminal },
    { id: "testing", label: "8. Test Suite", icon: Binary },
  ];

  return (
    <section id="docs" className="py-20 border-t border-[var(--border)] bg-[var(--bg)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="flex flex-col items-center text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] mb-3">
            <BookOpen className="w-3.5 h-3.5" />
            <span>Developer Documentation Platform</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-semibold tracking-tight text-[var(--accent)]">
            Complete Technical Documentation
          </h2>
          <p className="mt-3 text-sm sm:text-base text-[var(--text-muted)] leading-relaxed">
            In-depth guides, mathematical formulations, RFC 9457 specifications, and code integration references inspired by enterprise developer platforms.
          </p>
        </div>

        {/* Tabbed Documentation Reader */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 rounded border border-[var(--border)] bg-[var(--surface)] p-6 sm:p-8">
          {/* Left: Tab Sidebar (Cols 3) */}
          <div className="lg:col-span-3 lg:sticky lg:top-24 self-start flex flex-col gap-1.5 border-b lg:border-b-0 lg:border-r border-[var(--border)] pb-6 lg:pb-0 lg:pr-6 transition-all duration-300">
            <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--text-dim)] px-2 mb-2">
              Documentation Index
            </span>
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`text-left px-3.5 py-2.5 rounded-lg text-xs font-mono transition-all flex items-center justify-between cursor-pointer ${
                    isActive
                      ? "bg-[var(--surface-sunken)] text-[var(--accent)] font-semibold border border-[var(--accent)]"
                      : "text-[var(--text-muted)] hover:text-[var(--text)] hover:bg-[var(--surface-hover)]"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Icon className="w-3.5 h-3.5" />
                    <span>{tab.label}</span>
                  </div>
                  {isActive && <ChevronRight className="w-3.5 h-3.5 text-[var(--accent)]" />}
                </button>
              );
            })}
          </div>

          {/* Right: Tab Content Area (Cols 9) */}
          <div className="lg:col-span-9 font-sans text-sm leading-relaxed text-[var(--text-muted)]">
            {/* TAB 1: GETTING STARTED */}
            {activeTab === "getting-started" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold font-heading text-[var(--text)] mb-1">
                    Getting Started with AgentReady Lab
                  </h3>
                  <p className="text-xs font-mono text-[var(--text-muted)]">
                    Quickstart · Environment Setup · 12-Second Verification Loop
                  </p>
                </div>
                <p>
                  AgentReady Lab operates as a unified monorepo containing a high-throughput async Python backend (FastAPI) and a Next.js telemetry workbench.
                </p>

                <div className="rounded-md border border-[var(--code-border)] bg-[var(--code-bg)] p-4 font-mono text-xs text-[var(--text-muted)]">
                  <div className="text-[var(--text-dim)] mb-2">// Quickest start command sequence</div>
                  <code>git clone https://github.com/LOQ/agent-ready.git<br/>cd agent-ready/backend &amp;&amp; uv sync<br/>uv run python scripts/smoke_test.py</code>
                </div>

                <h4 className="text-base font-semibold font-heading text-[var(--text)] pt-2">
                  Zero-Friction Replay Mode
                </h4>
                <p>
                  By default, <code className="text-[var(--text-muted)] font-mono">USE_MOCK_BLUEPRINT=true</code> is pre-configured. You can execute full crash-tests and observe 9-lane animations, AG Grid matrix updates, and Red-to-Green code fixes without requiring active PayPal Sandbox credentials or internet access.
                </p>
              </div>
            )}

            {/* TAB 2: ARCHITECTURE */}
            {activeTab === "architecture" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold font-heading text-[var(--text)] mb-1">
                    System Architecture &amp; Data Pipeline
                  </h3>
                  <p className="text-xs font-mono text-[var(--text-muted)]">
                    FastAPI · Next.js 16 · Supabase Postgres · RFC 9457 Problem Details
                  </p>
                </div>

                <div className="p-4 rounded-md border border-[var(--border)] bg-[var(--surface)] font-mono text-xs text-[var(--text)] space-y-2">
                  <div className="font-bold text-[var(--text-dim)]">// Invariant Join Key</div>
                  <p className="text-[var(--text-muted)]">
                    All PayPal Orders v2 transactions set:
                    <br />
                    <code className="text-[var(--warn)]">purchase_units[0].custom_id = cart_id</code>
                    <br />
                    This serves as the immutable join key between the merchant&rsquo;s internal database orders and PayPal&rsquo;s authoritative capture ledger.
                  </p>
                </div>

                <h4 className="text-base font-semibold font-heading text-[var(--text)]">
                  RFC 9457 Problem Details Standard
                </h4>
                <p>
                  All errors emitted by the platform conform strictly to RFC 9457 (<code className="text-[var(--text-muted)] font-mono">application/problem+json</code>). This provides machine-readable failure keys that autonomous agents can parse to self-correct:
                </p>
                <ul className="list-disc list-inside space-y-1 font-mono text-xs">
                  <li><code className="text-[var(--fail)]">409 PRICE_MISMATCH_REAUTHORIZATION_REQUIRED</code></li>
                  <li><code className="text-[var(--fail)]">409 CART_INTENT_MISMATCH</code> (Prompt Injection detected)</li>
                  <li><code className="text-[var(--warn)]">422 AMBIGUOUS_VARIANT_CLARIFICATION_REQUIRED</code></li>
                  <li><code className="text-[var(--fail)]">422 REFUND_EXCEEDS_CAPTURE</code></li>
                  <li><code className="text-[var(--fail)]">401 WEBHOOK_SIGNATURE_INVALID</code></li>
                </ul>
              </div>
            )}

            {/* TAB 3: 9 AI PERSONAS */}
            {activeTab === "personas" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold font-heading text-[var(--text)] mb-1">
                    The 9 Adversarial Buyer Personas
                  </h3>
                  <p className="text-xs font-mono text-[var(--text-muted)]">
                    7 Scripted State Machines · 2 Gemini 3.8 Flash Generative Agents
                  </p>
                </div>

                <div className="space-y-4">
                  {PERSONAS_LIST.map((p) => (
                    <div
                      key={p.id}
                      className="p-4 rounded border border-[var(--border)] bg-[var(--surface-sunken)] text-xs font-mono"
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="font-bold text-[var(--text)] text-sm">
                          Lane {p.lane}: {p.name}
                        </span>
                        <span className="px-2 py-0.5 rounded bg-[var(--surface-sunken)] text-[var(--text-muted)] border border-[var(--border)]">
                          {p.ruleTested} ({p.ruleWeight} pts)
                        </span>
                      </div>
                      <p className="text-[var(--text-muted)] font-sans mb-2">
                        {p.attackVector}
                      </p>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-[var(--border)] text-[11px]">
                        <div className="text-[var(--fail)]">
                          <strong>Naive:</strong> {p.naiveBehavior}
                        </div>
                        <div className="text-[var(--pass)]">
                          <strong>Hardened:</strong> {p.hardenedBehavior}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB 4: 6 INVARIANT RULES */}
            {activeTab === "invariants" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold font-heading text-[var(--text)] mb-1">
                    The 6 Commerce Invariants &amp; Scoring Formula
                  </h3>
                  <p className="text-xs font-mono text-[var(--text-muted)]">
                    Deterministic Grading · Heuristic Weights (Sum = 100)
                  </p>
                </div>

                {/* Mathematical Formula Box */}
                <div className="p-4 rounded-md border border-[var(--border)] bg-[var(--surface)] font-mono text-xs text-[var(--text)]">
                  <div className="text-[var(--text-dim)] mb-1">// Scoring Formula (Section B3.7)</div>
                  <div>failure_share[r] = failed_carts[r] / total_evaluated_carts[r]</div>
                  <div className="text-[var(--text-muted)] font-bold mt-1">
                    Agent_Readiness_Score = round(100 - sum(weight[r] * failure_share[r]))
                  </div>
                </div>

                <div className="space-y-3">
                  {INVARIANTS_LIST.map((inv) => (
                    <div
                      key={inv.rule}
                      className="p-3.5 rounded-md border border-[var(--border)] bg-[var(--surface)] text-xs font-mono"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-bold text-[var(--text)]">
                          Rule {inv.rule}: {inv.name} (Weight: {inv.weight} pts)
                        </span>
                        <span className="text-[var(--text-muted)]">{inv.formula}</span>
                      </div>
                      <p className="text-[var(--text-muted)] font-sans mt-1">
                        {inv.description}
                      </p>
                    </div>
                  ))}
                </div>

                <p className="text-xs italic text-[var(--text-dim)] border-t border-[var(--border)] pt-3">
                  Disclaimer: Score weights are AgentReady Lab&rsquo;s heuristic design, not an official PayPal standard or certification.
                </p>
              </div>
            )}

            {/* TAB 5: MERCHANT GUARD */}
            {activeTab === "merchant-guard" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold font-heading text-[var(--text)] mb-1">
                    Merchant Guard Middleware &amp; Signed Probe
                  </h3>
                  <p className="text-xs font-mono text-[var(--text-muted)]">
                    Drop-In Protection · Signed HMAC Probe (/_lab/ledger)
                  </p>
                </div>

                <p>
                  The <code className="text-[var(--text-muted)] font-mono">AgentReady Guard</code> middleware intercepts agent requests before they hit PayPal orders creation. It verifies idempotency keys, recalculates authoritative catalog prices, verifies buyer HMAC cart signatures, and rejects invalid webhook signatures.
                </p>

                <div className="rounded-md border border-[var(--code-border)] bg-[var(--code-bg)] p-4 font-mono text-xs text-[var(--text)] overflow-x-auto leading-relaxed">
                  <div className="text-[var(--text-dim)]">
                    {"// Example: Guarding POST /checkout_sessions/{id}/complete"}
                  </div>
                  <code>{`from app.shops.guard import AgentReadyGuard

guard = AgentReadyGuard(
    catalog_service=channel3,
    hmac_secret=settings.cart_receipt_hmac_secret
)

# Enforces price integrity, variant clarity, and cart intent:
order_result = await guard.process_checkout(
    cart_id=session.cart_id,
    idempotency_key=headers.get("Idempotency-Key"),
    submitted_price=payload.price,
    cart_receipt_signature=payload.receipt_sig
)`}</code>
                </div>
              </div>
            )}

            {/* TAB 6: RECONCILIATION */}
            {activeTab === "reconciliation" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold font-heading text-[var(--text)] mb-1">
                    Dual-Ledger Reconciliation &amp; Remediation Policies
                  </h3>
                  <p className="text-xs font-mono text-[var(--text-muted)]">
                    Webhook Settle Window: 5s · Rule 3 SLA: 8s · Auto Refund
                  </p>
                </div>

                <p>
                  The Reconciler supports 3 automated remediation policies for orphan captures or broken state:
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
                  <div className="p-3.5 rounded-md border border-[var(--border)] bg-[var(--surface)]">
                    <span className="text-[var(--text-muted)] font-bold block mb-1">AUTO (Default)</span>
                    <p className="text-[var(--text-muted)] text-[11px] font-sans">
                      Automatically triggers PayPal Sandbox capture refund when an orphan capture is detected after the 8s SLA.
                    </p>
                  </div>

                  <div className="p-3.5 rounded-md border border-[var(--border)] bg-[var(--surface)]">
                    <span className="text-[var(--warn)] font-bold block mb-1">ASSIST</span>
                    <p className="text-[var(--text-muted)] text-[11px] font-sans">
                      Surfaces a 1-click remediation button in the AG Grid matrix for the engineer to authorize.
                    </p>
                  </div>

                  <div className="p-3.5 rounded-md border border-[var(--border)] bg-[var(--surface)]">
                    <span className="text-[var(--text-muted)] font-bold block mb-1">OBSERVE</span>
                    <p className="text-[var(--text-muted)] text-[11px] font-sans">
                      Audit-only mode; records the violation in the dual ledger without issuing outbound PayPal reversals.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* TAB 7: MCP & SDK */}
            {activeTab === "mcp-sdk" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold font-heading text-[var(--text)] mb-1">
                    stdio MCP Server &amp; Generated TypeScript SDK
                  </h3>
                  <p className="text-xs font-mono text-[var(--text-muted)]">
                    Antigravity IDE · Claude Desktop · @agent-ready/sdk
                  </p>
                </div>

                <p>
                  AgentReady Lab ships with an official Model Context Protocol (MCP) server exposing 5 tools for autonomous coding agents:
                </p>

                <div className="rounded-md border border-[var(--code-border)] bg-[var(--code-bg)] p-4 font-mono text-xs text-[var(--text)] overflow-x-auto leading-relaxed">
                  <div className="text-[var(--text-dim)]">// mcp/server.ts tool definitions</div>
                  <ul className="space-y-1">
                    <li>• <code className="text-[var(--text-muted)]">start_crash_test</code> — Runs adversarial swarm with target &amp; seed</li>
                    <li>• <code className="text-[var(--text-muted)]">list_findings</code> — Returns findings with PayPal transaction IDs</li>
                    <li>• <code className="text-[var(--text-muted)]">explain_finding</code> — Plain-English root cause from Gemini 3.8 Flash</li>
                    <li>• <code className="text-[var(--text-muted)]">suggest_fix</code> — Returns APIMatic-grounded 10-line unified diff</li>
                    <li>• <code className="text-[var(--text-muted)]">rerun</code> — Re-evaluates same seed against Hardened Shop</li>
                  </ul>
                </div>
              </div>
            )}

            {/* TAB 8: TESTING */}
            {activeTab === "testing" && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold font-heading text-[var(--text)] mb-1">
                    Automated Test Suite &amp; Benchmark Matrix
                  </h3>
                  <p className="text-xs font-mono text-[var(--text-muted)]">
                    117 Passing Tests · 7/7 Smoke Test · 12/12 Matrix
                  </p>
                </div>

                <div className="rounded-md border border-[var(--code-border)] bg-[var(--code-bg)] p-4 font-mono text-xs text-[var(--text)] space-y-3">
                  <div>
                    <span className="text-[var(--text-dim)]">// 1. Run all 117 unit and integration tests</span>
                    <br />
                    <code>uv run pytest tests/ -v</code>
                    <div className="text-[var(--pass)] mt-0.5">117 passed in 19.84s</div>
                  </div>

                  <div>
                    <span className="text-[var(--text-dim)]">// 2. Run automated judge dry run</span>
                    <br />
                    <code>uv run python scripts/smoke_test.py</code>
                    <div className="text-[var(--pass)] mt-0.5">Total Checks: 7/7 Passed (Vitality, Naive 18/100, Hardened 95/100, Replay &lt;2s)</div>
                  </div>

                  <div>
                    <span className="text-[var(--text-dim)]">// 3. Run 12-Bug Benchmark Matrix</span>
                    <br />
                    <code>uv run python scripts/run_self_test_matrix.py</code>
                    <div className="text-[var(--pass)] mt-0.5">12/12 True Positives, 0 False Alarms (100% deterministic coverage)</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};