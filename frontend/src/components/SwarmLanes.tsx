"use client";

import React from "react";
import {
  Activity,
  Layers,
  MousePointerClick,
  Sparkles,
} from "lucide-react";
import { PersonaSpec } from "@/lib/api";

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
  selectedLane?: number;
  onSelectLane?: (lane: number) => void;
}

export const SwarmLanes: React.FC<SwarmLanesProps> = ({
  personas,
  laneStates,
  isRunning,
  selectedLane = 2,
  onSelectLane,
}) => {
  // Sort personas by lane (1 to 9) across 2 waves
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
    return (
      laneStates[laneNumber] || {
        lane: laneNumber,
        persona,
        status: "IDLE" as const,
      }
    );
  });

  return (
    <section className="w-full bg-[var(--surface)] border border-[var(--border)] rounded-lg p-5 specular-highlight">
      {/* Strip Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-4 mb-4 border-b border-[var(--border)]">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)]">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="font-mono text-[11px] uppercase tracking-[0.08em] text-[var(--accent)] flex items-center gap-2">
                Swarm Telemetry Matrix
                <span className="text-[var(--text-dim)]">/</span>
                <span className="text-[var(--text)]">9 Adversarial Personas</span>
              </h2>
              {isRunning && (
                <span className="flex h-1.5 w-1.5 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--accent)] opacity-75" />
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-[var(--accent)]" />
                </span>
              )}
            </div>
            <p className="text-xs text-[var(--text-muted)] mt-0.5">
              Two-wave batched execution respecting PayPal Sandbox rate limits (max 5 concurrent)
            </p>
          </div>
        </div>

        {/* Wave Batching Info Badges & Lane Click Tip */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="px-2 py-0.5 text-[11px] font-mono rounded border bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--text-muted)] flex items-center gap-1.5">
            <Layers className="w-3 h-3 text-[var(--text-muted)]" />
            Wave 1: Lanes 1–5
          </span>
          <span className="px-2 py-0.5 text-[11px] font-mono rounded border bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--text-muted)] flex items-center gap-1.5">
            <Layers className="w-3 h-3 text-[var(--text-muted)]" />
            Wave 2: Lanes 6–9
          </span>
          <span className="hidden lg:flex items-center gap-1 text-[11px] font-mono text-[var(--text-dim)] ml-1">
            <MousePointerClick className="w-3 h-3 text-[var(--text-muted)]" />
            Select lane to inspect wire
          </span>
        </div>
      </div>

      {/* Exposed 1px Structural Grid (Swiss Precision Hairline Grid) */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-[var(--surface-sunken)] border border-[var(--border)] rounded-lg overflow-hidden">
        {sortedLanes.map((lane) => {
          const isWave1 = lane.lane <= 5;
          const status = lane.status;
          const isSelected = selectedLane === lane.lane;

          // Status indicators
          let dotColor = "bg-[var(--surface)]";
          let badgeClass = "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)]";

          if (status === "DISPATCHED") {
            dotColor = "bg-[var(--accent)]";
            badgeClass = "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)]";
          } else if (status === "FAILED") {
            dotColor = "bg-[var(--fail)]";
            badgeClass = "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)]";
          } else if (status === "COMPLETED") {
            dotColor = "bg-[var(--pass)]";
            badgeClass = "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)]";
          } else if (status === "BLOCKED") {
            dotColor = "bg-[var(--warn)]";
            badgeClass = "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)]";
          }

          return (
            <div
              key={lane.lane}
              onClick={() => onSelectLane?.(lane.lane)}
              className={`relative p-3.5 transition-all duration-150 ease-[cubic-bezier(0.22,1,0.36,1)] cursor-pointer flex flex-col justify-between ${isSelected
                  ? "bg-[var(--surface-sunken)] ring-1 ring-[var(--accent)]"
                  : "bg-[var(--surface)] hover:bg-[var(--surface-hover)]"
                }`}
            >
              {/* 2px Active Progress Bar at cell top */}
              {status === "DISPATCHED" && (
                <div className="audit-progress-draw absolute top-0 left-0 right-0 h-[2px] bg-[var(--accent)]" />
              )}
              {isSelected && status !== "DISPATCHED" && (
                <div className="absolute top-0 left-0 right-0 h-[2px] bg-[var(--accent)]" />
              )}

              {/* Top Row: Lane Number, Name & Wave */}
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="w-5 h-5 rounded flex items-center justify-center bg-[var(--bg)] border border-[var(--border)] font-mono text-[11px] tabular-nums font-medium text-[var(--text)] flex-shrink-0">
                      {lane.lane}
                    </span>
                    <span className="font-medium text-xs text-[var(--text)] truncate tracking-tight">
                      {lane.persona.name}
                    </span>
                    {lane.persona.driven_by === "live_llm" && (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] flex items-center gap-0.5 flex-shrink-0">
                        <Sparkles className="w-2.5 h-2.5" />
                        LLM
                      </span>
                    )}
                  </div>

                  <span
                    className={`inline-flex items-center gap-1.5 px-2 py-0.5 text-[11px] font-mono rounded border ${badgeClass} flex-shrink-0`}
                  >
                    <span className={`h-1.5 w-1.5 rounded-full ${dotColor}`} />
                    {status}
                  </span>
                </div>

                {/* Plain Words Rule Explanation */}
                <p className="text-[11px] text-[var(--text-muted)] line-clamp-1 mb-3">
                  {lane.persona.plain_words || "Evaluating rule compliance..."}
                </p>
              </div>

              {/* Bottom Telemetry Meta Strip */}
              <div className="pt-2.5 border-t border-[var(--border)] flex flex-col gap-1.5 font-mono text-[11px]">
                {/* Action & Wave / Rule info */}
                <div className="flex items-center justify-between text-[var(--text-dim)] text-[10px]">
                  <span className="truncate max-w-[155px] text-[var(--text)]">
                    {lane.lastAction || (isRunning ? "Queued in wave..." : "Standby")}
                  </span>
                  <span className="px-1.5 py-0.5 rounded bg-[var(--bg)] text-[9px] text-[var(--text-muted)] border border-[var(--border)]">
                    {isWave1 ? "W1" : "W2"} • Rule {lane.persona.rule_number}
                  </span>
                </div>

                {/* PayPal ID & Amount */}
                {(lane.paypalId || lane.amount) && (
                  <div className="flex items-center justify-between pt-1">
                    {lane.paypalId ? (
                      <span className="px-1.5 py-0.5 rounded bg-[var(--bg)] border border-[var(--border)] text-[10px] text-[var(--text-muted)] font-mono tabular-nums truncate max-w-[140px]">
                        {lane.paypalId}
                      </span>
                    ) : (
                      <span className="text-[10px] text-[var(--text-dim)]">—</span>
                    )}

                    {lane.amount && (
                      <span
                        className={`text-[11px] font-mono tabular-nums font-semibold ${status === "FAILED"
                            ? "text-[var(--fail)]"
                            : "text-[var(--pass)]"
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
