"use client";

import React from "react";
import Link from "next/link";
import { PLAYGROUND_URL, METRICS } from "@/lib/constants";
import {
  Zap,
  Terminal,
  ArrowRight,
  BookOpen,
  Play,
  AlertCircle,
} from "lucide-react";

export const HeroSection: React.FC = () => {
  return (
    <section className="pt-10 pb-16 md:pt-16 md:pb-20 border-b border-[var(--border)] bg-[var(--bg)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Two-Column Hero Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center text-left">
          
          {/* Left Column: Copy & CTAs */}
          <div className="lg:col-span-6 flex flex-col">
            {/* Storytelling Quotation Callout */}
            <div className="mb-6 p-4 rounded-md border border-[var(--border)] bg-[var(--surface)] text-left shadow-none">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-4 h-4 text-[var(--highlight)] mt-0.5 flex-shrink-0 stroke-[1.5]" />
                <div className="space-y-1.5 text-xs sm:text-[13px] leading-relaxed text-[var(--text)]">
                  <p className="italic">
                    &ldquo;Priya tells her autonomous AI assistant: <span className="font-semibold text-[var(--text)]">&lsquo;Buy running shoes, size 8, under $80.&rsquo;</span> The assistant pays through PayPal, but a network hiccup interrupts HTTP confirmation. The agent retries automatically. The merchant store omits idempotency keys and creates two orders. PayPal processes both valid authorizations, charging <span className="font-semibold text-[var(--fail)]">$160 instead of $80</span>. PayPal did its job. The flaw lived entirely in the merchant&rsquo;s integration code.&rdquo;
                  </p>
                  <div className="flex items-center justify-between text-[11px] font-mono text-[var(--text-muted)] pt-1 border-t border-[var(--border)]">
                    <span>Threat Vector: Autonomous Double-Capture</span>
                    <span className="text-[var(--text-muted)]">Silent Financial Leakage</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Sponsor & Standard Tags */}
            <div className="flex flex-wrap items-center gap-2 mb-4 text-[11px] font-mono text-[var(--text-muted)]">
              <span className="px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--surface-sunken)]">
                PayPal Sandbox v2
              </span>
              <span className="px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--surface-sunken)]">
                APIMatic SDK v2.29
              </span>
              <span className="px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--surface-sunken)]">
                Channel3 Catalog
              </span>
            </div>

            {/* Main Heading in Fraunces */}
            <h1 className="font-heading font-semibold text-3xl sm:text-5xl text-[var(--text)] leading-[1.15] tracking-tight">
              PayPal protects the payment.{" "}
              <span className="text-[var(--accent)]">
                Nobody tests the merchant&rsquo;s side
              </span>{" "}
              of an agent order.{" "}
              <span className="underline decoration-[var(--highlight)] decoration-1 underline-offset-4">
                AgentReady Lab does.
              </span>
            </h1>

            {/* Technical Subtitle */}
            <p className="mt-4 text-[15px] sm:text-base text-[var(--text-muted)] leading-relaxed font-sans">
              An adversarial crash-testing, dual-ledger compliance auditing, and self-healing platform for autonomous AI agent commerce. Swarm 9 specialized buyer test dummies, inject deterministic chaos faults, reconcile against PayPal Sandbox ground truth, and generate grounded 10-line code patches.
            </p>

            {/* Primary CTAs Bar */}
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <Link
                href={PLAYGROUND_URL}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-md font-sans text-sm font-semibold bg-[var(--accent)] text-[var(--accent-foreground)] hover:bg-[var(--accent-hover)] transition-colors cursor-pointer group"
              >
                <Zap className="w-4 h-4 fill-current stroke-[1.5]" />
                <span>Let&apos;s Simulate</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform stroke-[1.5]" />
              </Link>

              <a
                href="#preview"
                className="inline-flex items-center gap-2 px-3.5 py-2 rounded-md font-sans text-xs font-medium border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] hover:bg-[var(--surface-hover)] transition-colors"
              >
                <Play className="w-3 h-3 text-[var(--text-muted)] fill-[var(--text-muted)] stroke-[1.5]" />
                <span>Try Live Demo</span>
              </a>

              <a
                href="#docs"
                className="inline-flex items-center gap-1.5 px-3 py-2 rounded-md font-sans text-xs text-[var(--text-muted)] hover:text-[var(--text)] transition-colors"
              >
                <BookOpen className="w-3.5 h-3.5 text-[var(--text-muted)] stroke-[1.5]" />
                <span>Documentation</span>
              </a>
            </div>
          </div>

          {/* Right Column: Theme-Compliant Terminal */}
          <div className="lg:col-span-6 w-full">
            <div className="w-full rounded-xl border border-[var(--code-border)] bg-[var(--code-bg)] text-[var(--code-text)] text-[13px] font-mono shadow-2xl overflow-hidden relative transition-colors">
              {/* Subtle top glow */}
              <div className="absolute top-0 left-1/4 right-1/4 h-[1px] bg-gradient-to-r from-transparent via-[var(--accent)]/50 to-transparent"></div>
              
              {/* Terminal Window Header */}
              <div className="bg-[var(--surface-sunken)] px-4 py-3 border-b border-[var(--code-border)] flex items-center justify-between transition-colors">
                <div className="flex items-center gap-4">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-[var(--fail)] opacity-80" />
                    <div className="w-3 h-3 rounded-full bg-[var(--warn)] opacity-80" />
                    <div className="w-3 h-3 rounded-full bg-[var(--pass)] opacity-80" />
                  </div>
                  <div className="flex items-center gap-2 text-[11px] text-[var(--text-muted)]">
                    <Terminal className="w-3.5 h-3.5" />
                    <span>telemetry_stream // reconciliation_plane.py</span>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 px-2 py-1 rounded bg-[var(--pass)]/10 border border-[var(--pass)]/20">
                  <span className="w-2 h-2 rounded-full bg-[var(--pass)] animate-pulse" />
                  <span className="text-[10px] text-[var(--pass)] font-semibold tracking-wider">ACTIVE SSE</span>
                </div>
              </div>

              {/* Terminal Body with Exact Theme Variables */}
              <div className="p-5 space-y-5 leading-relaxed overflow-x-auto text-[12px] sm:text-[13px]">
                
                {/* Stage 1: Chaos */}
                <div>
                  <div className="text-[var(--text-dim)] mb-1.5">// 1. Chaos Fault Injected: Dropped ack on payment confirmation</div>
                  <div className="flex items-start gap-2">
                    <span className="px-1.5 py-0.5 rounded bg-[var(--warn)]/10 text-[var(--warn)] font-bold text-[11px] mt-0.5 border border-[var(--warn)]/20">[CHAOS]</span>
                    <span className="text-[var(--code-text)]">
                      Persona 'The Retrier' dropped connection after PayPal capture <span className="text-[var(--accent)]">PP-CAP-5O190127TN364715T</span>
                    </span>
                  </div>
                </div>

                {/* Stage 2: Recon */}
                <div>
                  <div className="text-[var(--text-dim)] mb-1.5">// 2. Deterministic Dual-Ledger Cross-Examination</div>
                  
                  <div className="flex flex-col gap-1.5 pl-1 border-l-2 border-[var(--border)] ml-2 mb-3">
                    <div className="flex items-center gap-3">
                      <span className="text-[var(--text-muted)] w-[170px]">[RECON] PayPal Ground Truth:</span>
                      <span className="text-[var(--fail)] font-bold bg-[var(--fail)]/10 border border-[var(--fail)]/20 px-2 py-0.5 rounded">2 CAPTURES ($240.00)</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-[var(--text-muted)] w-[170px]">[RECON] Store DB Internal:</span>
                      <span className="text-[var(--pass)] font-bold bg-[var(--pass)]/10 border border-[var(--pass)]/20 px-2 py-0.5 rounded">1 ORDER ($120.00)</span>
                    </div>
                  </div>
                  
                  <div className="p-3 rounded bg-[var(--fail-soft)] border border-[var(--fail-border)] flex flex-col gap-1">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-[var(--fail)]" />
                      <strong className="text-[var(--fail)] tracking-wide">RULE_1_VIOLATION: DOUBLE_CAPTURE_DETECTED</strong>
                    </div>
                    <div className="text-[var(--fail)]/90 pl-6">Unrecorded leakage: $120.00 across same cart_id</div>
                  </div>
                </div>

                {/* Stage 3: Patch */}
                <div>
                  <div className="text-[var(--text-dim)] mb-1.5">// 3. APIMatic-Grounded Patch Synthesis</div>
                  <div className="flex items-start gap-2">
                    <span className="px-1.5 py-0.5 rounded bg-[var(--pass)]/10 text-[var(--pass)] font-bold text-[11px] mt-0.5 border border-[var(--pass)]/20">[FIX_ENGINE]</span>
                    <span className="text-[var(--code-text)]">
                      Synthesized 10-line unified diff mapping <span className="text-[var(--highlight)]">Idempotency-Key</span> &rarr; <span className="text-[var(--highlight)]">PayPal-Request-Id</span>.
                    </span>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>

        {/* Top Metrics Bar: Flat 4-Column Hairline Grid */}
        <div className="mt-12 hairline-grid grid-cols-2 md:grid-cols-4 bg-[var(--border)] border border-[var(--border)] rounded-md">
          <div className="bg-[var(--surface)] p-4 flex flex-col items-center justify-center text-center">
            <span className="text-2xl font-mono font-semibold text-[var(--text)] tabular-nums">0 – 100</span>
            <span className="text-[11px] font-mono uppercase tracking-wider text-[var(--text-dim)] mt-0.5">Readiness Score</span>
            <span className="text-[11px] text-[var(--text-muted)]">Weighted Deterministic</span>
          </div>
          <div className="bg-[var(--surface)] p-4 flex flex-col items-center justify-center text-center">
            <span className="text-2xl font-mono font-semibold text-[var(--text)] tabular-nums">{METRICS.invariantsCount} / {METRICS.invariantsCount}</span>
            <span className="text-[11px] font-mono uppercase tracking-wider text-[var(--text-dim)] mt-0.5">Commerce Invariants</span>
            <span className="text-[11px] text-[var(--text-muted)]">Audited Deterministically</span>
          </div>
          <div className="bg-[var(--surface)] p-4 flex flex-col items-center justify-center text-center">
            <span className="text-2xl font-mono font-semibold text-[var(--text)] tabular-nums">12 / 12</span>
            <span className="text-[11px] font-mono uppercase tracking-wider text-[var(--text-dim)] mt-0.5">Benchmark Matrix</span>
            <span className="text-[11px] text-[var(--text-muted)]">0 False Alarms (100%)</span>
          </div>
          <div className="bg-[var(--surface)] p-4 flex flex-col items-center justify-center text-center">
            <span className="text-2xl font-mono font-semibold text-[var(--text)] tabular-nums">{METRICS.preventedFinancialLeakage}</span>
            <span className="text-[11px] font-mono uppercase tracking-wider text-[var(--text-dim)] mt-0.5">Undetected Leakage</span>
            <span className="text-[11px] text-[var(--text-muted)]">Dual-Ledger Verified</span>
          </div>
        </div>
      </div>
    </section>
  );
};