"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Cpu,
  Repeat,
  ShieldAlert,
  ShieldCheck,
  ShoppingBag,
  Zap,
} from "lucide-react";

export const WorkflowHeroBanner: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"without_guard" | "with_guard">("with_guard");

  return (
    <div className="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-6">
      {/* Interactive 3-Card Cart-to-Mini-Simulator */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <span className="font-mono text-[11px] uppercase tracking-[0.08em] text-[var(--text-muted)] flex items-center gap-1.5">
            <Cpu className="h-3.5 w-3.5 text-[var(--text-muted)]" /> Interactive Cart-to-Mini-Simulator:
          </span>

          {/* Guard Toggle Pill */}
          <div className="inline-flex rounded-lg p-0.5 bg-[var(--surface-sunken)] border border-[var(--border)]">
            <button
              onClick={() => setActiveTab("without_guard")}
              className={`px-3 py-1 text-xs font-mono rounded transition-all cursor-pointer ${
                activeTab === "without_guard"
                  ? "bg-[var(--surface-sunken)] text-[var(--text)] border border-[var(--border-strong)]"
                  : "text-[var(--text-muted)] hover:text-[var(--text)]"
              }`}
            >
              <span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-[var(--fail)]" />
              Without Guard (Naive Shop)
            </button>
            <button
              onClick={() => setActiveTab("with_guard")}
              className={`px-3 py-1 text-xs font-mono rounded transition-all cursor-pointer ${
                activeTab === "with_guard"
                  ? "bg-[var(--surface-sunken)] text-[var(--text)] border border-[var(--border-strong)]"
                  : "text-[var(--text-muted)] hover:text-[var(--text)]"
              }`}
            >
              <span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-[var(--pass)]" />
              With Guard (Hardened Shop)
            </button>
          </div>
        </div>

        {/* 3-Card Exposed Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-[var(--surface-sunken)] border border-[var(--border)] rounded-lg overflow-hidden">
          {/* Card 1: Human Approved Intent */}
          <div className="bg-[var(--surface)] p-4 flex flex-col justify-between space-y-3">
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-[var(--text-muted)] mb-1">
                <span className="flex items-center gap-1.5 text-[var(--text)]">
                  <ShoppingBag className="h-3.5 w-3.5 text-[var(--text-muted)]" /> 1. Human Cart Approval
                </span>
                <span className="text-[10px] text-[var(--text-dim)] font-mono">HMAC SHA-256</span>
              </div>
              <div className="text-[var(--text)] font-medium text-sm">
                Brooks Ghost 16 Running Shoes
              </div>
              <div className="text-xs text-[var(--text-muted)] mt-1 font-mono">
                Size 8 · 1 Unit · Server Price: <strong className="text-[var(--text)]">$149.95</strong>
              </div>
            </div>
            <div className="text-[11px] font-mono text-[var(--text-muted)] bg-[var(--surface-sunken)] px-2 py-1 rounded border border-[var(--border)] flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-[var(--pass)]" />
              <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
              <span>Signed Cart Receipt Minted</span>
            </div>
          </div>

          {/* Card 2: Chaos Fault / Adversarial Agent Mutation */}
          <div className="bg-[var(--surface)] p-4 flex flex-col justify-between space-y-3">
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-[var(--text-muted)] mb-1">
                <span className="flex items-center gap-1.5 text-[var(--warn)]">
                  <Zap className="h-3.5 w-3.5" /> 2. Wire Fault Injected
                </span>
                <span className="text-[10px] font-mono text-[var(--warn)]">Chaos Proxy</span>
              </div>
              <div className="text-[var(--text)] font-medium text-sm">
                Dropped HTTP 200 & Automated Retry
              </div>
              <div className="text-xs text-[var(--text-muted)] mt-1 font-mono">
                Capture succeeds, but agent response dropped. Shopper retries with same cart.
              </div>
            </div>
            <div className="text-[11px] font-mono text-[var(--text-muted)] bg-[var(--surface-sunken)] px-2 py-1 rounded border border-[var(--border)] flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-[var(--warn)]" />
              <Repeat className="h-3.5 w-3.5 shrink-0" />
              <span>2x POST /v2/checkout/orders</span>
            </div>
          </div>

          {/* Card 3: Dynamic Outcome (Toggleable) */}
          <div className="bg-[var(--surface)] p-4 flex flex-col justify-between space-y-3">
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-[var(--text-muted)] mb-1">
                <span className="flex items-center gap-1.5 text-[var(--text)]">
                  {activeTab === "without_guard" ? (
                    <ShieldAlert className="h-3.5 w-3.5 text-[var(--fail)]" />
                  ) : (
                    <ShieldCheck className="h-3.5 w-3.5 text-[var(--pass)]" />
                  )}
                  3. Store Ledger Outcome
                </span>
                <span className={`text-[10px] font-mono ${activeTab === "without_guard" ? "text-[var(--fail)]" : "text-[var(--pass)]"}`}>
                  {activeTab === "without_guard" ? "18 / 100 🔴" : "95 / 100 🟢"}
                </span>
              </div>

              {activeTab === "without_guard" ? (
                <div>
                  <div className="text-[var(--fail)] font-medium text-sm">
                    Double Capture: $299.90 Charged
                  </div>
                  <div className="text-xs text-[var(--text-muted)] mt-1">
                    Store lacks <code className="text-[var(--text)]">PayPal-Request-Id</code>. Customer charged twice for a single order.
                  </div>
                </div>
              ) : (
                <div>
                  <div className="text-[var(--pass)] font-medium text-sm">
                    Idempotent Replay: $149.95 Preserved
                  </div>
                  <div className="text-xs text-[var(--text-muted)] mt-1">
                    Guard checks idempotency cache, returns original capture with <code className="text-[var(--text)]">Idempotent-Replayed: true</code>.
                  </div>
                </div>
              )}
            </div>

            <div className={`text-[11px] font-mono text-[var(--text-muted)] px-2 py-1 rounded border flex items-center gap-1.5 ${
              activeTab === "without_guard"
                ? "bg-[var(--surface-sunken)] border-[var(--border)]"
                : "bg-[var(--surface-sunken)] border-[var(--border)]"
            }`}>
              <span className={`h-1.5 w-1.5 rounded-full ${activeTab === "without_guard" ? "bg-[var(--fail)]" : "bg-[var(--pass)]"}`} />
              {activeTab === "without_guard" ? (
                <>
                  <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-[var(--fail)]" />
                  <span>Rule 1 Violation · Capital Lost</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-[var(--pass)]" />
                  <span>Rule 1 Passed · 0 False Alarms</span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};