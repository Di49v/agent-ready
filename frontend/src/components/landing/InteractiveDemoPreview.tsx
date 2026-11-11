"use client";

import React, { useState } from "react";
import Link from "next/link";
import { PLAYGROUND_URL } from "@/lib/constants";
import {
  Play,
  RotateCcw,
  ArrowRight,
  Terminal,
} from "lucide-react";

export const InteractiveDemoPreview: React.FC = () => {
  const [selectedShop, setSelectedShop] = useState<"naive" | "hardened">("naive");
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [simStep, setSimStep] = useState<number>(0);
  const [hasCompleted, setHasCompleted] = useState<boolean>(false);

  const runSimulation = () => {
    setIsSimulating(true);
    setHasCompleted(false);
    setSimStep(1);

    setTimeout(() => setSimStep(2), 600);
    setTimeout(() => setSimStep(3), 1200);
    setTimeout(() => setSimStep(4), 1800);
    setTimeout(() => {
      setIsSimulating(false);
      setHasCompleted(true);
    }, 2400);
  };

  const resetSimulation = () => {
    setSimStep(0);
    setHasCompleted(false);
    setIsSimulating(false);
  };

  // Determine chart values
  const scoreValue = !hasCompleted && !isSimulating ? 0 : (selectedShop === "naive" ? 18 : 95);
  const displayScore = !hasCompleted && !isSimulating ? "--" : scoreValue.toString();
  const themeColor = !hasCompleted && !isSimulating
    ? "text-[var(--border-strong)]"
    : selectedShop === "naive"
    ? "text-[var(--fail)]"
    : "text-[var(--pass)]";

  return (
    <section id="preview" className="py-16 md:py-24 border-b border-[var(--border)] bg-[var(--bg)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="flex flex-col text-left max-w-2xl mb-12">
          <span className="text-xs font-mono uppercase tracking-wider text-[var(--text-muted)] mb-2 font-medium">
            Interactive Micro-Simulator
          </span>
          <h2 className="font-heading font-semibold text-2xl sm:text-4xl text-[var(--accent)] tracking-tight">
            Test the Red-to-Green Engine in Real Time
          </h2>
          <p className="mt-3 text-[15px] sm:text-base text-[var(--text-muted)] leading-relaxed">
            Toggle between the vulnerable baseline and protected shop, trigger an in-browser micro-run, and observe how AgentReady Lab evaluates dual-ledger compliance.
          </p>
        </div>

        {/* Micro-Simulator Container */}
        <div className="max-w-4xl rounded-md border border-[var(--border)] bg-[var(--surface)] overflow-hidden">
          {/* Top Control Bar */}
          <div className="bg-[var(--surface-sunken)] px-5 py-3 border-b border-[var(--border)] flex flex-wrap items-center justify-between gap-3">
            {/* Shop Toggle */}
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-[var(--text-dim)] uppercase">
                Target Store:
              </span>
              <div className="inline-flex rounded-md bg-[var(--surface)] p-0.5 border border-[var(--border)]">
                <button
                  onClick={() => {
                    setSelectedShop("naive");
                    resetSimulation();
                  }}
                  className={`px-3 py-1 rounded text-xs font-mono transition-colors cursor-pointer ${
                    selectedShop === "naive"
                      ? "bg-[var(--surface-sunken)] text-[var(--text)] font-semibold border border-[var(--border-strong)]"
                      : "text-[var(--text-muted)] hover:text-[var(--text)]"
                  }`}
                >
                  <span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-[var(--fail)]" />
                  Naive Shop (Vulnerable)
                </button>
                <button
                  onClick={() => {
                    setSelectedShop("hardened");
                    resetSimulation();
                  }}
                  className={`px-3 py-1 rounded text-xs font-mono transition-colors cursor-pointer ${
                    selectedShop === "hardened"
                      ? "bg-[var(--surface-sunken)] text-[var(--text)] font-semibold border border-[var(--border-strong)]"
                      : "text-[var(--text-muted)] hover:text-[var(--text)]"
                  }`}
                >
                  <span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-[var(--pass)]" />
                  Hardened Shop (Guard)
                </button>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={runSimulation}
                disabled={isSimulating}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-md font-sans text-xs font-medium bg-[var(--accent)] text-[var(--accent-foreground)] hover:bg-[var(--accent-hover)] disabled:opacity-50 transition-colors cursor-pointer"
              >
                {isSimulating ? (
                  <>
                    <span className="w-3 h-3 border-2 border-[var(--text-muted)] border-t-transparent rounded-full animate-spin" />
                    <span>Executing Swarm...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-3 h-3 fill-current stroke-[1.5]" />
                    <span>Run Micro-Simulation</span>
                  </>
                )}
              </button>

              <button
                onClick={resetSimulation}
                title="Reset simulation"
                className="p-1.5 rounded-md border border-[var(--border)] bg-[var(--surface)] text-[var(--text-muted)] hover:text-[var(--text)] transition-colors cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5 stroke-[1.5]" />
              </button>
            </div>
          </div>

          {/* Simulator Content Area */}
          <div className="p-6 grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
            {/* Left: Score & Radial Chart (Col 4) */}
            <div className="md:col-span-4 flex flex-col items-center justify-center p-6 rounded-md border border-[var(--border)] bg-[var(--surface-sunken)] text-center h-full">
              <span className="text-[11px] font-mono text-[var(--text-dim)] uppercase tracking-wider mb-2">
                Simulated Score
              </span>

              {/* Side-by-Side Pie Chart and Score */}
              <div className="flex items-center justify-center gap-5 my-4">
                {/* SVG Solid Pie Chart */}
                <div className="relative w-[72px] h-[72px] rounded-full overflow-hidden border border-[var(--border-strong)] bg-[var(--surface)]">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 32 32">
                    {/* Progress Fill (Solid Pie Slice) */}
                    <circle
                      cx="16"
                      cy="16"
                      r="8"
                      fill="transparent"
                      stroke="currentColor"
                      strokeWidth="16"
                      strokeDasharray="50.265 50.265"
                      strokeDashoffset={50.265 - (scoreValue / 100) * 50.265}
                      className={`transition-all duration-1000 ease-out ${themeColor}`}
                    />
                  </svg>
                </div>

                {/* Score Number & Status */}
                <div className="flex flex-col items-start text-left">
                  <span className={`text-4xl font-mono font-semibold tabular-nums leading-none ${themeColor}`}>
                    {displayScore}
                  </span>
                  <span className={`text-[10px] mt-1 font-mono uppercase tracking-wider font-bold ${themeColor}`}>
                    {!hasCompleted && !isSimulating
                      ? "IDLE"
                      : selectedShop === "naive"
                      ? "CRITICAL"
                      : "PASSED"}
                  </span>
                </div>
              </div>

              <div className="mt-2 text-xs font-mono">
                {selectedShop === "naive" ? (
                  <span className="text-[var(--fail)] font-medium">
                    3 Invariant Breaches
                  </span>
                ) : (
                  <span className="text-[var(--pass)] font-medium">
                    Guarded + 1 Honest Limit
                  </span>
                )}
              </div>
            </div>

            {/* Right: Live Telemetry Stream Box (Col 8) */}
            <div className="md:col-span-8 flex flex-col justify-between rounded-md border border-[var(--code-border)] bg-[var(--code-bg)] text-[var(--code-text)] p-4 text-xs font-mono">
              <div className="border-b border-[var(--code-border)] pb-2 mb-3 flex items-center justify-between text-[11px] text-[var(--text-muted)]">
                <span className="flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-[var(--text-muted)] stroke-[1.5]" />
                  <span>event_stream // client_side_telemetry</span>
                </span>
                <span className="text-[var(--text-muted)]">Seed: 42 (Reproducible)</span>
              </div>

              <div className="space-y-2 min-h-[160px] leading-relaxed">
                {simStep === 0 && !hasCompleted && (
                  <div className="text-[var(--text-dim)] italic py-8 text-center font-sans">
                    Click &ldquo;Run Micro-Simulation&rdquo; to test the dual-wave adversarial buyer swarm.
                  </div>
                )}

                {simStep >= 1 && (
                  <div className="audit-log-enter">
                    <span className="text-[var(--text-muted)] font-semibold">[0.0s WAVE_1]</span> Dispatched 5 parallel buyers (Retrier, Tamperer, Stale Cart, Webhook Skeptic, Refunder)...
                  </div>
                )}

                {simStep >= 2 && selectedShop === "naive" && (
                  <div className="audit-log-enter text-[var(--fail)]">
                    <span className="font-semibold">[0.6s VULN]</span> The Retrier: Dropped ack triggered duplicate capture <span className="underline">PP-CAP-5O190127TN364715T</span> ($240 on $120 order)!
                  </div>
                )}
                {simStep >= 2 && selectedShop === "hardened" && (
                  <div className="audit-log-enter text-[var(--pass)]">
                    <span className="font-semibold">[0.6s GUARD]</span> The Retrier: Idempotency-Key matched cache; returned 200 OK with <code>Idempotent-Replayed: true</code>!
                  </div>
                )}

                {simStep >= 3 && selectedShop === "naive" && (
                  <div className="audit-log-enter text-[var(--fail)]">
                    <span className="font-semibold">[1.2s VULN]</span> The Tamperer: Client price $1.50 accepted for $150.00 shoe! Store database under-collected $148.50.
                  </div>
                )}
                {simStep >= 3 && selectedShop === "hardened" && (
                  <div className="audit-log-enter text-[var(--pass)]">
                    <span className="font-semibold">[1.2s GUARD]</span> The Tamperer: Recalculated server catalog price; rejected with RFC 9457 <code>409 PRICE_MISMATCH</code>.
                  </div>
                )}

                {simStep >= 4 && selectedShop === "naive" && (
                  <div className="audit-log-enter text-[var(--text-muted)]">
                    <span className="font-semibold">[1.8s FINAL]</span> Dual-Ledger Reconciler: Score <span className="font-semibold underline text-[var(--fail)]">18/100 (FAIL)</span>. APIMatic Fix Engine synthesizes 10-line patch.
                  </div>
                )}
                {simStep >= 4 && selectedShop === "hardened" && (
                  <div className="audit-log-enter text-[var(--text-muted)]">
                    <span className="font-semibold">[1.8s FINAL]</span> Dual-Ledger Reconciler: Score <span className="font-semibold underline text-[var(--pass)]">95/100 (PASS)</span>. Honest residual finding on black-box probe.
                  </div>
                )}
              </div>

              {/* Bottom Micro-CTA */}
              <div className="mt-4 pt-3 border-t border-[var(--code-border)] flex items-center justify-between text-[11px]">
                <span className="text-[var(--text-dim)] font-sans">
                  Simulated preview of core reconcile logic
                </span>
                <Link
                  href={PLAYGROUND_URL}
                  className="inline-flex items-center gap-1 text-[var(--text-muted)] hover:text-[var(--text)] font-medium transition-colors"
                >
                  <span>Open Full 9-Lane Workbench</span>
                  <ArrowRight className="w-3.5 h-3.5 stroke-[1.5]" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};