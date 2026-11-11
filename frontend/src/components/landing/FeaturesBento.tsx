"use client";

import React from "react";
import Link from "next/link";
import { PLAYGROUND_URL, PERSONAS_LIST } from "@/lib/constants";
import {
  Zap,
  ShieldCheck,
  Cpu,
  FileCode,
  ArrowRight,
  Split,
  Binary,
  Radio,
  Terminal,
} from "lucide-react";

export const FeaturesBento: React.FC = () => {
  return (
    <section id="features" className="py-16 md:py-24 border-b border-[var(--border)] bg-[var(--surface-sunken)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="flex flex-col text-left max-w-2xl mb-12">
          <span className="text-xs font-mono uppercase tracking-wider text-[var(--text-muted)] mb-2 font-medium">
            Enterprise Deliverables
          </span>
          <h2 className="font-heading font-semibold text-2xl sm:text-4xl text-[var(--accent)] tracking-tight">
            Everything You Need to Certify Agentic Checkouts
          </h2>
          <p className="mt-3 text-[15px] sm:text-base text-[var(--text-muted)] leading-relaxed">
            High-density telemetry, deterministic dual-ledger reconciliation, and grounded APIMatic fixes built with developer-tool discipline.
          </p>
        </div>

        {/* Bento Grid: Hairline Flat Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Bento Item 1: 9-Persona Swarm (Span 2 cols) */}
          <div className="group lg:col-span-2 bg-[var(--surface)] border border-[var(--border)] p-6 sm:p-7 flex flex-col justify-between h-full rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:border-[var(--accent)]/30 dark:hover:shadow-[0_8px_30px_rgba(255,255,255,0.03)] cursor-default">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center transition-colors group-hover:text-[var(--accent)] group-hover:border-[var(--accent)]/30">
                  <Cpu className="w-4 h-4 stroke-[1.5]" />
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[var(--surface-sunken)] text-[var(--text-muted)] border border-[var(--border)]">
                  Batched Concurrency: 5 Buyers
                </span>
              </div>
              <h3 className="font-heading font-semibold text-xl text-[var(--text)] group-hover:text-[var(--accent)] transition-colors">
                9 Specialized Adversarial Personas
              </h3>
              <p className="mt-2 text-sm text-[var(--text-muted)] leading-relaxed font-sans">
                Executes in 2 fast waves (Wave 1: 5 buyers, Wave 2: 4 buyers) in ~12 seconds. From network drops to Gemini 3.8 Flash prompt injections, each bot stress-tests an exact edge case without triggering PayPal 429 rate limits.
              </p>

              {/* Persona Tags */}
              <div className="mt-4 flex flex-wrap gap-1.5">
                {PERSONAS_LIST.map((p) => (
                  <span
                    key={p.name}
                    className="text-[11px] font-mono px-2 py-0.5 rounded bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text)] transition-colors group-hover:border-[var(--border-strong)]"
                  >
                    {p.name}
                  </span>
                ))}
              </div>
            </div>

            <div className="mt-6 pt-3 border-t border-[var(--border)] flex items-center justify-between text-xs font-mono text-[var(--text-dim)]">
              <span>Deterministic State Machines + Gemini LLMs</span>
              <span className="text-[var(--text-muted)]">Wave 1 &amp; 2</span>
            </div>
          </div>

          {/* Bento Item 2: Dual-Ledger Reconciler */}
          <div className="group bg-[var(--surface)] border border-[var(--border)] p-6 sm:p-7 flex flex-col justify-between rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:border-[var(--accent)]/30 dark:hover:shadow-[0_8px_30px_rgba(255,255,255,0.03)] cursor-default">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center mb-4 transition-colors group-hover:text-[var(--accent)] group-hover:border-[var(--accent)]/30">
                <Split className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="font-heading font-semibold text-lg text-[var(--text)] group-hover:text-[var(--accent)] transition-colors">
                Dual-Ledger Reconciler
              </h3>
              <p className="mt-2 text-xs text-[var(--text-muted)] leading-relaxed font-sans">
                Waits a 5-second webhook settle window, then cross-examines PayPal API ground truth vs store probe ledgers joined on <code className="text-[var(--text-muted)] font-mono">custom_id == cart_id</code>.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[var(--border)] text-xs font-mono text-[var(--text-muted)]">
              Evaluates 6 Invariants
            </div>
          </div>

          {/* Bento Item 3: Seeded Chaos Proxy */}
          <div className="group bg-[var(--surface)] border border-[var(--border)] p-6 sm:p-7 flex flex-col justify-between rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:border-[var(--warn)]/50 dark:hover:shadow-[0_8px_30px_rgba(255,255,255,0.03)] cursor-default">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--warn)] flex items-center justify-center mb-4 transition-colors group-hover:bg-[var(--warn)]/10 group-hover:border-[var(--warn)]/30">
                <Binary className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="font-heading font-semibold text-lg text-[var(--text)] group-hover:text-[var(--warn)] transition-colors">
                Seeded Chaos Proxy
              </h3>
              <p className="mt-2 text-xs text-[var(--text-muted)] leading-relaxed font-sans">
                100% reproducible fault injection using <code className="text-[var(--warn)] font-mono">seed=42</code>. Drops HTTP acks, strips idempotency headers, mutates prices, and sends forged webhooks.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[var(--border)] text-xs font-mono text-[var(--warn)]">
              Zero-Flakiness Guarantee
            </div>
          </div>

          {/* Bento Item 4: APIMatic-Grounded Fix Engine */}
          <div className="group lg:col-span-2 bg-[var(--surface)] border border-[var(--border)] p-6 sm:p-7 flex flex-col justify-between rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:border-[var(--accent)]/30 dark:hover:shadow-[0_8px_30px_rgba(255,255,255,0.03)] cursor-default">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center mb-4 transition-colors group-hover:text-[var(--accent)] group-hover:border-[var(--accent)]/30">
                <FileCode className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="font-heading font-semibold text-lg text-[var(--text)] group-hover:text-[var(--accent)] transition-colors">
                APIMatic Fix Engine
              </h3>
              <p className="mt-2 text-xs text-[var(--text-muted)] leading-relaxed font-sans">
                Generates 10-line unified Git patches grounded in the APIMatic Context Plugin for PayPal. Explains root cause with exact PayPal Order/Capture IDs.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[var(--border)] text-xs font-mono text-[var(--text-muted)]">
              Score: 18 &rarr; 95/100 (Pass)
            </div>
          </div>

          {/* Bento Item 5: Reference Testing Envs */}
          <div className="group bg-[var(--surface)] border border-[var(--border)] p-6 sm:p-7 flex flex-col justify-between rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:border-[var(--fail)]/40 dark:hover:shadow-[0_8px_30px_rgba(255,255,255,0.03)] cursor-default">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--fail)] flex items-center justify-center mb-4 transition-colors group-hover:bg-[var(--fail)]/10 group-hover:border-[var(--fail)]/30">
                <ShieldCheck className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="font-heading font-semibold text-lg text-[var(--text)] group-hover:text-[var(--fail)] transition-colors">
                Dual Reference Shops
              </h3>
              <p className="mt-2 text-xs text-[var(--text-muted)] leading-relaxed font-sans">
                Includes <strong className="text-[var(--fail)] font-medium">Naive Shop</strong> with 12 toggleable vulnerability flags, and <strong className="text-[var(--pass)] font-medium">Hardened Shop</strong> with RFC 9457 Guard middleware.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[var(--border)] text-xs font-mono text-[var(--fail)]">
              12/12 True Positives Matrix
            </div>
          </div>

          {/* Bento Item 6: stdio MCP Server & SDK */}
          <div className="group bg-[var(--surface)] border border-[var(--border)] p-6 sm:p-7 flex flex-col justify-between rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:border-[var(--accent)]/30 dark:hover:shadow-[0_8px_30px_rgba(255,255,255,0.03)] cursor-default">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center mb-4 transition-colors group-hover:text-[var(--accent)] group-hover:border-[var(--accent)]/30">
                <Terminal className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="font-heading font-semibold text-lg text-[var(--text)] group-hover:text-[var(--accent)] transition-colors">
                MCP Server &amp; SDK
              </h3>
              <p className="mt-2 text-xs text-[var(--text-muted)] leading-relaxed font-sans">
                Exposes 5 MCP tools on stdio transport for Antigravity IDE and Claude Desktop, plus typed TypeScript SDK generated from OpenAPI 3.1.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[var(--border)] text-xs font-mono text-[var(--text-muted)]">
              @agent-ready/sdk v1.0.0
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};