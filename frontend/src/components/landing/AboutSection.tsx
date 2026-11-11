"use client";

import React from "react";
import {
  Layers,
  Cpu,
  Target,
  Users,
} from "lucide-react";

export const AboutSection: React.FC = () => {
  return (
    <section id="about" className="py-16 md:py-24 border-b border-[var(--border)] bg-[var(--surface-sunken)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="flex flex-col text-left max-w-2xl mb-12">
          <span className="text-xs font-mono uppercase tracking-wider text-[var(--text-muted)] mb-2 font-medium">
            Architecture &amp; Core Motivation
          </span>
          <h2 className="font-heading font-semibold text-2xl sm:text-4xl text-[var(--accent)] tracking-tight">
            What is AgentReady Lab?
          </h2>
          <p className="mt-3 text-[15px] sm:text-base text-[var(--text-muted)] leading-relaxed">
            The developer documentation breakdown of why autonomous AI agents break merchant checkout code, and how our 4-stage deterministic pipeline evaluates and cures integration flaws.
          </p>
        </div>

        {/* 4 Technical Questions & Answers (Flat Grid) */}
        <div className="hairline-grid grid-cols-1 md:grid-cols-2 mb-12 bg-[var(--border)] border border-[var(--border)] rounded-md">
          {/* Card 1: What is it */}
          <div className="bg-[var(--surface)] p-6 sm:p-7 flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center mb-4">
                <Cpu className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="text-lg font-heading font-semibold text-[var(--text)]">
                1. What is AgentReady Lab?
              </h3>
              <p className="mt-2.5 text-sm text-[var(--text-muted)] leading-relaxed font-sans">
                AgentReady Lab is an adversarial crash-testing facility, dual-ledger compliance auditor, and self-healing engine purpose-built for AI agent commerce on the PayPal Sandbox. It treats the merchant store as a test subject, subjecting it to scripted and generative buyer bots that aggressively exploit real-world edge cases.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[var(--border)] flex items-center gap-2 text-xs font-mono text-[var(--text-muted)]">
              <span>Stack: FastAPI + Next.js + AG Grid + Supabase</span>
            </div>
          </div>

          {/* Card 2: Why was it developed */}
          <div className="bg-[var(--surface)] p-6 sm:p-7 flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center mb-4">
                <Target className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="text-lg font-heading font-semibold text-[var(--text)]">
                2. Why was it developed?
              </h3>
              <p className="mt-2.5 text-sm text-[var(--text-muted)] leading-relaxed font-sans">
                Autonomous AI shopping agents (ChatGPT Operator, Gemini agents, automated checkout bots) do not behave like humans. They retry within milliseconds on network drops, transact in high-concurrency swarms, parse ambiguous catalog variants without human confirmation, and ingest untrusted product descriptions containing prompt injections.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[var(--border)] flex items-center gap-2 text-xs font-mono text-[var(--text-muted)]">
              <span>Risk: Unattended Silent Financial Desync</span>
            </div>
          </div>

          {/* Card 3: What problem does it address */}
          <div className="bg-[var(--surface)] p-6 sm:p-7 flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--fail)] flex items-center justify-center mb-4">
                <Layers className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="text-lg font-heading font-semibold text-[var(--text)]">
                3. What problem does it address?
              </h3>
              <p className="mt-2.5 text-sm text-[var(--text-muted)] leading-relaxed font-sans">
                <strong className="text-[var(--text)] font-medium">The Merchant-Side Security Vacuum:</strong> PayPal protects payment credentials, authorizations, and chargebacks. But PayPal cannot stop a merchant backend from double-capturing orders, accepting forged webhooks, or dropping database records while PayPal holds the captured funds (orphan captures).
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[var(--border)] flex items-center gap-2 text-xs font-mono text-[var(--fail)]">
              <span>Invariants: 6 Deterministic Financial Rules</span>
            </div>
          </div>

          {/* Card 4: Who should use it */}
          <div className="bg-[var(--surface)] p-6 sm:p-7 flex flex-col justify-between">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center mb-4">
                <Users className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="text-lg font-heading font-semibold text-[var(--text)]">
                4. Who should use it and why?
              </h3>
              <p className="mt-2.5 text-sm text-[var(--text-muted)] leading-relaxed font-sans">
                Backend software engineers, payment integration architects, and agentic commerce developers. It provides instant, deterministic grading (0–100), reproducible seed traces (`seed=42`), RFC 9457 structured Problem Details errors, and 10-line grounded Git patches before autonomous checkout bots touch production revenue.
              </p>
            </div>
            <div className="mt-6 pt-3 border-t border-[var(--border)] flex items-center gap-2 text-xs font-mono text-[var(--text-muted)]">
              <span>Audience: Enterprise Engineers &amp; DevOps Leads</span>
            </div>
          </div>
        </div>

        {/* The 4-Stage Operational Pipeline */}
        <div className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-6 sm:p-7">
          <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[var(--border)] pb-4">
            <div>
              <span className="text-xs font-mono uppercase tracking-wider text-[var(--text-muted)]">
                Core Execution Pipeline
              </span>
              <h3 className="font-heading font-semibold text-xl text-[var(--text)] mt-0.5">
                How AgentReady Lab Works (Swarm &rarr; Chaos &rarr; Recon &rarr; Fix)
              </h3>
            </div>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-mono bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)]">
              End-to-End Latency: ~12s
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Stage 1 */}
            <div className="rounded-md border border-[var(--border)] bg-[var(--surface-sunken)] p-4 flex flex-col justify-between">
              <div>
                <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[var(--surface-sunken)] text-[var(--text-muted)] border border-[var(--border)]">
                  STAGE 01
                </span>
                <h4 className="font-heading font-semibold text-base text-[var(--text)] mt-2.5">
                  Adversarial Swarm
                </h4>
                <p className="text-xs text-[var(--text-muted)] mt-1.5 leading-relaxed font-sans">
                  9 specialized buyer personas execute in 2 batched waves (`asyncio.Semaphore(5)`) to stress-test the store without triggering PayPal 429 rate limits.
                </p>
              </div>
              <div className="mt-4 pt-2.5 border-t border-[var(--border)] text-[11px] font-mono text-[var(--text-dim)]">
                Input: Target Store URL + Seed
              </div>
            </div>

            {/* Stage 2 */}
            <div className="rounded-md border border-[var(--border)] bg-[var(--surface-sunken)] p-4 flex flex-col justify-between">
              <div>
                <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[var(--surface-sunken)] text-[var(--text-muted)] border border-[var(--border)]">
                  STAGE 02
                </span>
                <h4 className="font-heading font-semibold text-base text-[var(--text)] mt-2.5">
                  Seeded Chaos Proxy
                </h4>
                <p className="text-xs text-[var(--text-muted)] mt-1.5 leading-relaxed font-sans">
                  Deterministic faults: drops payment response, strips idempotency keys, mutates prices to $1.50, and forges unverified webhook payloads.
                </p>
              </div>
              <div className="mt-4 pt-2.5 border-t border-[var(--border)] text-[11px] font-mono text-[var(--text-dim)]">
                Reproducible: `seed=42`
              </div>
            </div>

            {/* Stage 3 */}
            <div className="rounded-md border border-[var(--border)] bg-[var(--surface-sunken)] p-4 flex flex-col justify-between">
              <div>
                <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[var(--surface-sunken)] text-[var(--text-muted)] border border-[var(--border)]">
                  STAGE 03
                </span>
                <h4 className="font-heading font-semibold text-base text-[var(--text)] mt-2.5">
                  Dual-Ledger Reconciler
                </h4>
                <p className="text-xs text-[var(--text-muted)] mt-1.5 leading-relaxed font-sans">
                  Cross-examines PayPal Sandbox API ground truth against merchant internal ledger (`/_lab/ledger`) joined on `custom_id == cart_id`.
                </p>
              </div>
              <div className="mt-4 pt-2.5 border-t border-[var(--border)] text-[11px] font-mono text-[var(--text-dim)]">
                Evaluates: 6 Invariant Rules
              </div>
            </div>

            {/* Stage 4 */}
            <div className="rounded-md border border-[var(--border)] bg-[var(--surface-sunken)] p-4 flex flex-col justify-between">
              <div>
                <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[var(--surface-sunken)] text-[var(--text-muted)] border border-[var(--border)]">
                  STAGE 04
                </span>
                <h4 className="font-heading font-semibold text-base text-[var(--text)] mt-2.5">
                  Grounded Fix Engine
                </h4>
                <p className="text-xs text-[var(--text-muted)] mt-1.5 leading-relaxed font-sans">
                  Synthesizes plain-English root causes with exact PayPal IDs, generates verified 10-line Git patches, and triggers 1-click re-run verification.
                </p>
              </div>
              <div className="mt-4 pt-2.5 border-t border-[var(--border)] text-[11px] font-mono text-[var(--text-dim)]">
                Output: Score Recovery (18 &rarr; 95)
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
