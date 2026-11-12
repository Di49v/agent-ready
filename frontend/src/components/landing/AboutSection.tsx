"use client";

import React from "react";
import {
  Layers,
  Cpu,
  Target,
  Users,
} from "lucide-react";
import AccordionGallery from "./AccordionGallery";
import { SwarmDiagram, ChaosDiagram, ReconDiagram, FixDiagram } from "./PipelineDiagrams";

const PIPELINE_STAGES = [
  {
    stage: "STAGE 01",
    title: "Adversarial Swarm",
    description: "9 specialized buyer personas execute in 2 batched waves (`asyncio.Semaphore(5)`) to stress-test the store without triggering PayPal 429 rate limits.",
    footer: "Input: Target Store URL + Seed",
    accentText: "text-[var(--text)]",
    accentBorder: "border-[var(--text-muted)]/50",
    visual: <SwarmDiagram />
  },
  {
    stage: "STAGE 02",
    title: "Seeded Chaos Proxy",
    description: "Deterministic faults: drops payment response, strips idempotency keys, mutates prices to $1.50, and forges unverified webhook payloads.",
    footer: "Reproducible: `seed=42`",
    accentText: "text-[var(--warn)]",
    accentBorder: "border-[var(--warn)]/50",
    visual: <ChaosDiagram />
  },
  {
    stage: "STAGE 03",
    title: "Dual-Ledger Reconciler",
    description: "Cross-examines PayPal Sandbox API ground truth against merchant internal ledger (`/_lab/ledger`) joined on `custom_id == cart_id`.",
    footer: "Evaluates: 6 Invariant Rules",
    accentText: "text-[var(--accent)]",
    accentBorder: "border-[var(--accent)]/50",
    visual: <ReconDiagram />
  },
  {
    stage: "STAGE 04",
    title: "Grounded Fix Engine",
    description: "Synthesizes plain-English root causes with exact PayPal IDs, generates verified 10-line Git patches, and triggers 1-click re-run verification.",
    footer: "Output: Score Recovery (18 → 95)",
    accentText: "text-[var(--pass)]",
    accentBorder: "border-[var(--pass)]/50",
    visual: <FixDiagram />
  }
];

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

        {/* 4 Technical Questions & Answers (Theme-Compliant Bento Cards) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-16">
          {/* Card 1: What is it */}
          <div className="group bg-[var(--surface)] border border-[var(--border)] p-6 sm:p-7 flex flex-col justify-between rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:border-[var(--accent)]/30 dark:hover:shadow-[0_8px_30px_rgba(255,255,255,0.03)] cursor-default">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center mb-4 transition-colors group-hover:text-[var(--accent)] group-hover:border-[var(--accent)]/30">
                <Cpu className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="text-lg font-heading font-semibold text-[var(--text)] group-hover:text-[var(--accent)] transition-colors">
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
          <div className="group bg-[var(--surface)] border border-[var(--border)] p-6 sm:p-7 flex flex-col justify-between rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:border-[var(--accent)]/30 dark:hover:shadow-[0_8px_30px_rgba(255,255,255,0.03)] cursor-default">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center mb-4 transition-colors group-hover:text-[var(--accent)] group-hover:border-[var(--accent)]/30">
                <Target className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="text-lg font-heading font-semibold text-[var(--text)] group-hover:text-[var(--accent)] transition-colors">
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
          <div className="group bg-[var(--surface)] border border-[var(--border)] p-6 sm:p-7 flex flex-col justify-between rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:border-[var(--fail)]/40 dark:hover:shadow-[0_8px_30px_rgba(255,255,255,0.03)] cursor-default">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--fail)] flex items-center justify-center mb-4 transition-colors group-hover:bg-[var(--fail)]/10 group-hover:border-[var(--fail)]/30">
                <Layers className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="text-lg font-heading font-semibold text-[var(--text)] group-hover:text-[var(--fail)] transition-colors">
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
          <div className="group bg-[var(--surface)] border border-[var(--border)] p-6 sm:p-7 flex flex-col justify-between rounded-xl transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:border-[var(--accent)]/30 dark:hover:shadow-[0_8px_30px_rgba(255,255,255,0.03)] cursor-default">
            <div>
              <div className="w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] flex items-center justify-center mb-4 transition-colors group-hover:text-[var(--accent)] group-hover:border-[var(--accent)]/30">
                <Users className="w-4 h-4 stroke-[1.5]" />
              </div>
              <h3 className="text-lg font-heading font-semibold text-[var(--text)] group-hover:text-[var(--accent)] transition-colors">
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

        {/* The 4-Stage Operational Pipeline (Using Accordion Gallery) */}
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-6 sm:p-8 shadow-sm">
          <div className="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[var(--border)] pb-5">
            <div>
              <span className="text-xs font-mono uppercase tracking-wider text-[var(--text-muted)]">
                Core Execution Pipeline
              </span>
              <h3 className="font-heading font-semibold text-xl text-[var(--text)] mt-1">
                How AgentReady Lab Works (Swarm &rarr; Chaos &rarr; Recon &rarr; Fix)
              </h3>
            </div>
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-mono bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)]">
              End-to-End Latency: ~12s
            </span>
          </div>

          <AccordionGallery items={PIPELINE_STAGES} />
        </div>
      </div>
    </section>
  );
};