"use client";

import React from "react";
import { ShieldAlert, Play, RotateCcw, Lock, Radio, ShieldCheck } from "lucide-react";
import { ThemeToggle } from "@/components/landing/ThemeToggle";

interface HeaderProps {
  selectedTarget: string;
  onSelectTarget: (target: string) => void;
  selectedPolicy: "observe" | "assist" | "auto";
  onSelectPolicy: (policy: "observe" | "assist" | "auto") => void;
  isRunning: boolean;
  onRunCrashTest: () => void;
  onReplayLastRun: () => void;
  onOpenBenchmark?: () => void;
  currentScore?: number | null;
  targetName?: string;
}

export const Header: React.FC<HeaderProps> = ({
  selectedTarget,
  onSelectTarget,
  selectedPolicy,
  onSelectPolicy,
  isRunning,
  onRunCrashTest,
  onReplayLastRun,
  onOpenBenchmark,
  currentScore,
}) => {
  return (
    <header className="w-full bg-[var(--surface)] border-b border-[var(--border)] sticky top-0 z-50 px-6 py-3.5 backdrop-blur-md">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Branding & Invariants Indicator */}
        <div className="flex items-center gap-3.5">
          <div className="w-8 h-8 rounded bg-[var(--surface-sunken)] border border-[var(--border)] flex items-center justify-center">
            <ShieldAlert className="w-5 h-5 text-[var(--text-muted)]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-base tracking-tight text-[var(--text)] font-heading">
                AgentReady<span className="text-[var(--text)]">.Lab</span>
              </span>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)]">
                <span className="h-1.5 w-1.5 rounded-full bg-[var(--pass)]" />
                <Lock className="w-2.5 h-2.5" />
                SANDBOX LOCKED
              </span>
            </div>
            <p className="text-xs text-[var(--text-muted)] font-sans">
              Crash-Testing &amp; Dual-Ledger Self-Healing for Agentic Commerce
            </p>
          </div>
        </div>

        {/* Target, Policy Controls & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Target Store Selector */}
          <div className="flex flex-col">
            <label className="text-[10px] font-mono uppercase tracking-wider text-[var(--text-dim)] mb-0.5">
              Target Store
            </label>
            <select
              value={selectedTarget}
              onChange={(e) => onSelectTarget(e.target.value)}
              disabled={isRunning}
              className="bg-[var(--surface-sunken)] border border-[var(--border)] text-sm text-[var(--text)] rounded px-3 py-1.5 focus:outline-none focus:border-[var(--accent)] transition disabled:opacity-50 font-sans cursor-pointer"
            >
              <option value="naive-shop">Naive Shop (Vulnerable Baseline)</option>
              <option value="hardened-shop">Hardened Shop (Guard Protected)</option>
            </select>
          </div>

          {/* Reversal Policy Selector */}
          <div className="flex flex-col">
            <label className="text-[10px] font-mono uppercase tracking-wider text-[var(--text-dim)] mb-0.5">
              Reconciler Policy
            </label>
            <select
              value={selectedPolicy}
              onChange={(e) =>
                onSelectPolicy(e.target.value as "observe" | "assist" | "auto")
              }
              disabled={isRunning}
              className="bg-[var(--surface-sunken)] border border-[var(--border)] text-sm text-[var(--text)] rounded px-3 py-1.5 focus:outline-none focus:border-[var(--accent)] transition disabled:opacity-50 font-sans cursor-pointer"
            >
              <option value="auto">Auto (Sandbox Void/Refund)</option>
              <option value="assist">Assist (1-Click Approval)</option>
              <option value="observe">Observe (Alert Only)</option>
            </select>
          </div>

          {/* Current Score Badge */}
          {currentScore !== undefined && currentScore !== null && (
            <div className="flex flex-col items-center">
              <label className="text-[10px] font-mono uppercase tracking-wider text-[var(--text-dim)] mb-0.5">
                Score
              </label>
              <div
                className="px-3 py-1 rounded-md font-mono font-bold text-sm border border-[var(--border)] bg-[var(--surface-sunken)] text-[var(--text-muted)] flex items-center gap-1.5"
              >
                <span className={`h-1.5 w-1.5 rounded-full ${currentScore >= 80 ? "bg-[var(--pass)]" : "bg-[var(--fail)]"}`} />
                <span className={currentScore >= 80 ? "text-[var(--pass)]" : "text-[var(--fail)]"}>{currentScore}/100</span>
                <span className="text-[10px] uppercase font-normal opacity-80">
                  {currentScore >= 80 ? "Pass" : "Fail"}
                </span>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center gap-2 pt-3 sm:pt-0">
            <ThemeToggle />
            {/* Run Crash Test Button */}
            <button
              onClick={onRunCrashTest}
              disabled={isRunning}
              className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium text-sm transition-all shadow-none ${isRunning
                ? "bg-[var(--surface-sunken)] text-[var(--text-dim)] border border-[var(--border)] cursor-not-allowed"
                : "bg-[var(--accent)] text-[var(--accent-foreground)] hover:bg-[var(--accent-hover)] cursor-pointer"
                }`}
            >
              {isRunning ? (
                <>
                  <Radio className="w-4 h-4 animate-spin text-[var(--accent)]" />
                  <span>Swarm Testing...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Run Crash Test</span>
                </>
              )}
            </button>

            {/* Replay Last Run Button */}
            <button
              onClick={onReplayLastRun}
              disabled={isRunning}
              title="Instant playback safety net without sandbox network latency"
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-md font-medium text-sm bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] hover:bg-[var(--surface-hover)] hover:border-[var(--border-strong)] transition disabled:opacity-50 cursor-pointer"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Replay</span>
            </button>

            {/* 12-Bug Benchmark Modal Trigger */}
            {onOpenBenchmark && (
              <button
                onClick={onOpenBenchmark}
                disabled={isRunning}
                title="View 12-Bug Benchmark Matrix (12/12 True Positives, 0 False Alarms)"
                className="flex items-center gap-1.5 px-3 py-2 rounded-md font-medium text-sm bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] hover:bg-[var(--surface-hover)] hover:border-[var(--border-strong)] transition disabled:opacity-50 cursor-pointer"
              >
                <ShieldCheck className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">12-Bug Matrix</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
