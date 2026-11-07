"use client";

import React from "react";
import { ShieldAlert, Play, RotateCcw, Lock, Radio, ShieldCheck } from "lucide-react";

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
    <header className="w-full bg-[#11131A] border-b border-[#242838] sticky top-0 z-50 px-6 py-3.5 backdrop-blur-md">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Branding & Invariants Indicator */}
        <div className="flex items-center gap-3.5">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#06B6D4] to-[#0070BA] flex items-center justify-center shadow-lg shadow-cyan-950/40">
            <ShieldAlert className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight text-white font-mono">
                AgentReady<span className="text-[#06B6D4]">.Lab</span>
              </span>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-emerald-950/60 border border-emerald-800/60 text-emerald-400">
                <Lock className="w-2.5 h-2.5" />
                SANDBOX LOCKED
              </span>
            </div>
            <p className="text-xs text-[#94A3B8] font-sans">
              Crash-Testing &amp; Dual-Ledger Self-Healing for Agentic Commerce
            </p>
          </div>
        </div>

        {/* Target, Policy Controls & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Target Store Selector */}
          <div className="flex flex-col">
            <label className="text-[10px] font-mono uppercase tracking-wider text-[#64748B] mb-0.5">
              Target Store
            </label>
            <select
              value={selectedTarget}
              onChange={(e) => onSelectTarget(e.target.value)}
              disabled={isRunning}
              className="bg-[#181B26] border border-[#242838] text-sm text-[#F1F5F9] rounded-md px-3 py-1.5 focus:outline-none focus:border-[#06B6D4] transition disabled:opacity-50 font-sans cursor-pointer"
            >
              <option value="naive-shop">Naive Shop (Vulnerable Baseline)</option>
              <option value="hardened-shop">Hardened Shop (Guard Protected)</option>
            </select>
          </div>

          {/* Reversal Policy Selector */}
          <div className="flex flex-col">
            <label className="text-[10px] font-mono uppercase tracking-wider text-[#64748B] mb-0.5">
              Reconciler Policy
            </label>
            <select
              value={selectedPolicy}
              onChange={(e) =>
                onSelectPolicy(e.target.value as "observe" | "assist" | "auto")
              }
              disabled={isRunning}
              className="bg-[#181B26] border border-[#242838] text-sm text-[#F1F5F9] rounded-md px-3 py-1.5 focus:outline-none focus:border-[#06B6D4] transition disabled:opacity-50 font-sans cursor-pointer"
            >
              <option value="auto">Auto (Sandbox Void/Refund)</option>
              <option value="assist">Assist (1-Click Approval)</option>
              <option value="observe">Observe (Alert Only)</option>
            </select>
          </div>

          {/* Current Score Badge */}
          {currentScore !== undefined && currentScore !== null && (
            <div className="flex flex-col items-center">
              <label className="text-[10px] font-mono uppercase tracking-wider text-[#64748B] mb-0.5">
                Score
              </label>
              <div
                className={`px-3 py-1 rounded-md font-mono font-bold text-sm border flex items-center gap-1.5 ${currentScore >= 80
                  ? "bg-emerald-950/60 border-emerald-500/50 text-emerald-400"
                  : "bg-rose-950/60 border-rose-500/50 text-rose-400"
                  }`}
              >
                <span>{currentScore}/100</span>
                <span className="text-[10px] uppercase font-normal opacity-80">
                  {currentScore >= 80 ? "Pass" : "Fail"}
                </span>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center gap-2 pt-3 sm:pt-0">
            {/* Run Crash Test Button */}
            <button
              onClick={onRunCrashTest}
              disabled={isRunning}
              className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium text-sm transition-all shadow-md ${isRunning
                ? "bg-[#1E2230] text-[#94A3B8] border border-[#242838] cursor-not-allowed"
                : "bg-gradient-to-r from-[#06B6D4] to-[#0070BA] text-white hover:brightness-110 glow-telemetry cursor-pointer"
                }`}
            >
              {isRunning ? (
                <>
                  <Radio className="w-4 h-4 animate-spin text-[#06B6D4]" />
                  <span>Swarm Testing...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-white text-white" />
                  <span>Run Crash Test</span>
                </>
              )}
            </button>

            {/* Replay Last Run Button */}
            <button
              onClick={onReplayLastRun}
              disabled={isRunning}
              title="Instant playback safety net without sandbox network latency"
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-md font-medium text-sm bg-[#181B26] border border-[#33394D] text-[#F59E0B] hover:bg-[#1E2230] hover:border-[#F59E0B]/50 transition disabled:opacity-50 cursor-pointer"
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
                className="flex items-center gap-1.5 px-3 py-2 rounded-md font-medium text-sm bg-[#181B26] border border-[#242838] text-[#06B6D4] hover:bg-[#1E2230] hover:border-[#06B6D4]/50 transition disabled:opacity-50 cursor-pointer"
              >
                <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                <span className="hidden sm:inline">12-Bug Matrix</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

