"use client";

import React from "react";
import {
  ArrowRight,
  CheckCircle2,
  FileCode,
  Flame,
  Play,
  RotateCcw,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

interface GuidedWalkthroughBarProps {
  currentStep: number;
  onSelectStep: (stepNumber: number) => void;
  isRunning: boolean;
  score?: number;
}

export const GuidedWalkthroughBar: React.FC<GuidedWalkthroughBarProps> = ({
  currentStep,
  onSelectStep,
  isRunning,
  score,
}) => {
  const steps = [
    {
      num: 1,
      title: "1. Run Naive Crash Test",
      badge: "18 / 100 🔴",
      description: "Trigger 9-lane adversarial swarm against unhardened store.",
      icon: Play,
    },
    {
      num: 2,
      title: "2. Inspect Dual-Ledger Diff",
      badge: "PP vs Store",
      description: "Compare PayPal captures vs store ledger and inspect signed cart receipt.",
      icon: Search,
    },
    {
      num: 3,
      title: "3. Review APIMatic Patch",
      badge: "10-Line Diff",
      description: "Inspect APIMatic-grounded unified diff for idempotency & price validation.",
      icon: FileCode,
    },
    {
      num: 4,
      title: "4. Re-Run Hardened Shop",
      badge: "95 / 100 🟢",
      description: "Re-run exact same seed to verify red turns green with 0 code bugs.",
      icon: RotateCcw,
    },
  ];

  return (
    <div className="bg-[#0D0F14] border border-white/[0.07] rounded-lg p-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-cyan-400" />
          <span className="font-mono text-xs uppercase tracking-[0.08em] text-white">
            4-Step Guided Judge Tour
          </span>
          <span className="text-zinc-500 font-mono text-xs">
            (Complete 45-Second Red-to-Green Walkthrough)
          </span>
        </div>

        {score !== undefined && (
          <div className="font-mono text-xs text-zinc-400 flex items-center gap-2">
            <span>Current Benchmark Score:</span>
            <span
              className={`px-2 py-0.5 rounded font-bold ${
                score >= 80
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
              }`}
            >
              {score} / 100
            </span>
          </div>
        )}
      </div>

      {/* Steps Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2">
        {steps.map((s) => {
          const isActive = currentStep === s.num;
          const isCompleted = currentStep > s.num || (s.num === 1 && score !== undefined && score < 80) || (s.num === 4 && score !== undefined && score >= 80);
          const Icon = s.icon;

          return (
            <button
              key={s.num}
              onClick={() => onSelectStep(s.num)}
              disabled={isRunning}
              className={`p-3 rounded-lg border text-left transition-all cursor-pointer flex flex-col justify-between ${
                isActive
                  ? "bg-[#13161F] border-cyan-400/50 shadow-lg shadow-cyan-500/5"
                  : isCompleted
                  ? "bg-[#0D0F14] border-white/[0.08] hover:border-white/20"
                  : "bg-[#08090C] border-white/[0.04] opacity-75 hover:opacity-100 hover:border-white/10"
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-2">
                  <div
                    className={`h-6 w-6 rounded flex items-center justify-center font-mono text-xs ${
                      isActive
                        ? "bg-cyan-500 text-black font-semibold"
                        : isCompleted
                        ? "bg-emerald-500/20 text-emerald-400"
                        : "bg-zinc-800 text-zinc-400"
                    }`}
                  >
                    {isCompleted ? <CheckCircle2 className="h-3.5 w-3.5" /> : s.num}
                  </div>
                  <span className="font-sans text-xs font-medium text-white truncate">
                    {s.title}
                  </span>
                </div>
                <span className="font-mono text-[10px] text-zinc-400 bg-white/5 px-1.5 py-0.5 rounded border border-white/5">
                  {s.badge}
                </span>
              </div>

              <p className="text-[11px] text-zinc-400 leading-tight">
                {s.description}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
};

