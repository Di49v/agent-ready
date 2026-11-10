"use client";

import React, { useState } from "react";
import { WORKFLOW_STEPS } from "@/lib/constants";
import {
  Terminal,
  Check,
  Copy,
  ArrowRight,
} from "lucide-react";

export const WorkflowSteps: React.FC = () => {
  const [activeStep, setActiveStep] = useState<number>(0);
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  }

  return (
    <section id="workflow" className="py-16 md:py-24 border-b border-[var(--border)] bg-[var(--surface-sunken)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="flex flex-col text-left max-w-2xl mb-12">
          <span className="text-xs font-mono uppercase tracking-wider text-[var(--text-muted)] mb-2 font-medium">
            Developer Getting Started
          </span>
          <h2 className="font-heading font-semibold text-2xl sm:text-4xl text-[var(--accent)] tracking-tight">
            How to Use AgentReady Lab
          </h2>
          <p className="mt-3 text-[15px] sm:text-base text-[var(--text-muted)] leading-relaxed">
            From zero to running your first adversarial simulation and generating grounded APIMatic patches in 8 developer-friendly steps.
          </p>
        </div>

        {/* Step Selector & Terminal Display */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left: Step Pipeline List (Cols 5) */}
          <div className="lg:col-span-5 flex flex-col gap-1.5">
            {WORKFLOW_STEPS.map((step, idx) => {
              const isSelected = activeStep === idx;
              return (
                <button
                  key={step.step}
                  onClick={() => setActiveStep(idx)}
                  className={`text-left p-3 rounded-md border transition-colors cursor-pointer flex items-center justify-between ${
                    isSelected
                      ? "bg-[var(--surface)] border-[var(--border-strong)] text-[var(--text)] shadow-none"
                      : "bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text)]"
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <span
                      className={`w-5 h-5 rounded flex items-center justify-center font-mono text-[11px] font-semibold ${
                        isSelected
                          ? "bg-[var(--accent)] text-[var(--accent-foreground)]"
                          : "bg-[var(--border)] text-[var(--text-dim)]"
                      }`}
                    >
                      {step.step}
                    </span>
                    <span className="text-xs font-mono font-medium text-[var(--text)]">
                      {step.title}
                    </span>
                  </div>
                  <ArrowRight
                    className={`w-3.5 h-3.5 transition-transform stroke-[1.5] ${
                      isSelected ? "text-[var(--accent)] translate-x-0.5" : "text-transparent"
                    }`}
                  />
                </button>
              );
            })}
          </div>

          {/* Right: Active Step Terminal & Guide (Cols 7) */}
          <div className="lg:col-span-7 rounded-md border border-[var(--border)] bg-[var(--surface)] p-6 sm:p-7 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[var(--surface-sunken)] text-[var(--text-muted)] border border-[var(--border)]">
                  STEP {WORKFLOW_STEPS[activeStep].step} OF 8
                </span>
                <span className="text-[11px] font-mono text-[var(--text-dim)]">
                  Developer Workstation
                </span>
              </div>

              <h3 className="font-heading font-semibold text-xl text-[var(--text)]">
                {WORKFLOW_STEPS[activeStep].title}
              </h3>

              <p className="mt-2.5 text-sm text-[var(--text-muted)] leading-relaxed font-sans">
                {WORKFLOW_STEPS[activeStep].description}
              </p>

              {/* Terminal Snippet Box */}
              <div className="mt-5 rounded-md border border-[var(--code-border)] bg-[var(--code-bg)] text-[var(--code-text)] overflow-hidden">
                <div className="bg-[var(--surface-sunken)] px-3.5 py-1.5 border-b border-[var(--code-border)] flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center gap-1.5 text-[var(--text-muted)]">
                    <Terminal className="w-3.5 h-3.5 text-[var(--text-muted)] stroke-[1.5]" />
                    <span>bash / powershell</span>
                  </div>
                  <button
                    onClick={() =>
                      handleCopy(WORKFLOW_STEPS[activeStep].cli, activeStep)
                    }
                    className="inline-flex items-center gap-1 text-[11px] text-[var(--text-muted)] hover:text-[var(--text)] transition-colors cursor-pointer"
                  >
                    {copiedIdx === activeStep ? (
                      <>
                        <Check className="w-3 h-3 text-[var(--pass)] stroke-[1.5]" />
                        <span className="text-[var(--pass)]">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3 stroke-[1.5]" />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                </div>
                <pre className="p-3.5 text-xs font-mono overflow-x-auto leading-relaxed">
                  <code>{WORKFLOW_STEPS[activeStep].cli}</code>
                </pre>
              </div>
            </div>

            {/* Navigation between steps */}
            <div className="mt-6 pt-3 border-t border-[var(--border)] flex items-center justify-between text-xs font-mono">
              <button
                disabled={activeStep === 0}
                onClick={() => setActiveStep(activeStep - 1)}
                className="text-[var(--text-dim)] hover:text-[var(--text)] disabled:opacity-30 cursor-pointer disabled:cursor-not-allowed"
              >
                &larr; Previous Step
              </button>

              <button
                disabled={activeStep === WORKFLOW_STEPS.length - 1}
                onClick={() => setActiveStep(activeStep + 1)}
                className="inline-flex items-center gap-1 text-[var(--text-muted)] hover:text-[var(--text)] disabled:opacity-30 cursor-pointer disabled:cursor-not-allowed font-medium"
              >
                <span>Next Step</span>
                <ArrowRight className="w-3.5 h-3.5 stroke-[1.5]" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
