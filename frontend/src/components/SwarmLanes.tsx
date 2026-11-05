"use client";

import React from "react";
import {
  Activity,
  Bot,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Layers,
  Sparkles,
} from "lucide-react";
import { PersonaSpec, RunEvent } from "@/lib/api";

export interface LaneTelemetryState {
  lane: number;
  persona: PersonaSpec;
  status: "IDLE" | "DISPATCHED" | "COMPLETED" | "BLOCKED" | "FAILED";
  lastAction?: string;
  actor?: string;
  paypalId?: string;
  amount?: string;
  ruleHit?: number;
  isDoubleCharge?: boolean;
}

interface SwarmLanesProps {
  personas: PersonaSpec[];
  laneStates: Record<number, LaneTelemetryState>;
  isRunning: boolean;
}

export const SwarmLanes: React.FC<SwarmLanesProps> = ({
  personas,
  laneStates,
  isRunning,
}) => {
  // Sort personas by lane / wave
  const sortedLanes = Array.from({ length: 9 }, (_, i) => {
    const laneNumber = i + 1;
    const persona = personas[i] || {
      id: `lane_${laneNumber}`,
      name: `Lane ${laneNumber}`,
      plain_words: "",
      rule_number: 1,
      rule_name: "Rule",
      driven_by: "fixed_script" as const,
      fault_description: "",
      expected_behavior: "",
      wave: laneNumber <= 5 ? 1 : 2,
    };
    return laneStates[laneNumber] || {
      lane: laneNumber,
      persona,
      status: "IDLE" as const,
    };
  });

  return (
    <section className="w-full bg-[#11131A] border border-[#242838] rounded-xl p-5 shadow-xl">
      {/* Strip Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 mb-4 border-b border-[#242838]">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-md bg-cyan-950/60 border border-cyan-800/60 text-[#06B6D4]">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-wide uppercase font-mono flex items-center gap-2">
              Live Swarm Telemetry Strip (9 Adversarial Lanes)
              {isRunning && (
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              )}
            </h2>
            <p className="text-xs text-[#94A3B8]">
              Parallel execution across 2 waves respecting PayPal Sandbox rate limits (max 5 concurrent)
            </p>
          </div>
        </div>

        {/* Wave Batching Info Badges */}
        <div className="flex items-center gap-2 font-mono text-[11px]">
          <span className="px-2.5 py-1 rounded bg-[#181B26] border border-[#242838] text-[#94A3B8] flex items-center gap-1.5">
            <Layers className="w-3 h-3 text-[#06B6D4]" />
            Wave 1: Lanes 1–5
          </span>
          <span className="px-2.5 py-1 rounded bg-[#181B26] border border-[#242838] text-[#94A3B8] flex items-center gap-1.5">
            <Layers className="w-3 h-3 text-[#F59E0B]" />
            Wave 2: Lanes 6–9
          </span>
        </div>
      </div>

      {/* 9-Lane Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {sortedLanes.map((lane) => {
          const isWave1 = lane.lane <= 5;
          const status = lane.status;

          // Status color styles
          let borderColor = "border-[#242838]";
          let badgeBg = "bg-[#181B26] text-[#94A3B8] border-[#242838]";
          let StatusIcon = Clock;

          if (status === "DISPATCHED") {
            borderColor = "border-[#06B6D4]/60 glow-telemetry";
            badgeBg = "bg-cyan-950/60 text-[#06B6D4] border-cyan-800/60";
            StatusIcon = Activity;
          } else if (status === "FAILED") {
            borderColor = "border-rose-500/80 glow-fail bg-rose-950/10";
            badgeBg = "bg-rose-950/80 text-rose-400 border-rose-800/80";
            StatusIcon = AlertTriangle;
          } else if (status === "COMPLETED") {
            borderColor = "border-emerald-500/60";
            badgeBg = "bg-emerald-950/60 text-emerald-400 border-emerald-800/60";
            StatusIcon = CheckCircle2;
          } else if (status === "BLOCKED") {
            borderColor = "border-amber-500/60";
            badgeBg = "bg-amber-950/60 text-amber-400 border-amber-800/60";
            StatusIcon = CheckCircle2;
          }

          return (
            <div
              key={lane.lane}
              className={`rounded-lg p-3.5 bg-[#161922] border ${borderColor} transition-all duration-200 flex flex-col justify-between`}
            >
              {/* Top Row: Lane Number, Name & Wave */}
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded flex items-center justify-center bg-[#11131A] border border-[#242838] font-mono text-[11px] font-bold text-[#F1F5F9]">
                      {lane.lane}
                    </span>
                    <span className="font-semibold text-xs text-white truncate max-w-[150px]">
                      {lane.persona.name}
                    </span>
                    {lane.persona.driven_by === "live_llm" && (
                      <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-indigo-950/80 border border-indigo-700/60 text-indigo-300 flex items-center gap-0.5">
                        <Sparkles className="w-2.5 h-2.5" />
                        LLM
                      </span>
                    )}
                  </div>
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono font-medium border ${badgeBg}`}
                  >
                    <StatusIcon className="w-3 h-3" />
                    {status}
                  </span>
                </div>

                {/* Plain Words Rule Explanation */}
                <p className="text-[11px] text-[#94A3B8] line-clamp-1 mb-2.5">
                  {lane.persona.plain_words || "Evaluating rule compliance..."}
                </p>
              </div>

              {/* Bottom Telemetry Meta Strip */}
              <div className="pt-2 border-t border-[#242838]/80 flex flex-col gap-1.5 font-mono text-[11px]">
                {/* Action & Actor */}
                <div className="flex items-center justify-between text-[#64748B] text-[10px]">
                  <span className="truncate max-w-[160px] text-[#94A3B8]">
                    {lane.lastAction || (isRunning ? "Waiting in wave queue..." : "Ready")}
                  </span>
                  <span className="px-1.5 py-0.5 rounded bg-[#11131A] text-[9px] text-[#64748B] border border-[#242838]">
                    {isWave1 ? "Wave 1" : "Wave 2"} • Rule {lane.persona.rule_number}
                  </span>
                </div>

                {/* PayPal ID & Amount */}
                {(lane.paypalId || lane.amount) && (
                  <div className="flex items-center justify-between pt-1">
                    {lane.paypalId ? (
                      <span className="px-1.5 py-0.5 rounded bg-[#11131A] border border-[#242838] text-[10px] text-[#06B6D4] truncate max-w-[140px]">
                        {lane.paypalId}
                      </span>
                    ) : (
                      <span className="text-[10px] text-[#64748B]">—</span>
                    )}

                    {lane.amount && (
                      <span
                        className={`text-[11px] font-bold tabular-nums ${status === "FAILED"
                            ? "text-rose-400 font-extrabold"
                            : "text-emerald-400"
                          }`}
                      >
                        {lane.amount}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};

