"use client";

import React, { useEffect, useState, useCallback } from "react";
import { Header } from "@/components/Header";
import { SwarmLanes, LaneTelemetryState } from "@/components/SwarmLanes";
import {
  createRun,
  fetchPersonas,
  getRun,
  PersonaSpec,
  RunEvent,
  RunSummary,
  subscribeRunEvents,
} from "@/lib/api";
import { ShieldCheck, Zap, AlertCircle } from "lucide-react";

export default function Home() {
  const [selectedTarget, setSelectedTarget] = useState<string>("naive-shop");
  const [selectedPolicy, setSelectedPolicy] = useState<"observe" | "assist" | "auto">("auto");
  const [personas, setPersonas] = useState<PersonaSpec[]>([]);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [currentRun, setCurrentRun] = useState<RunSummary | null>(null);
  const [laneStates, setLaneStates] = useState<Record<number, LaneTelemetryState>>({});
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  // Load initial 9 personas on component mount
  useEffect(() => {
    async function loadInitialData() {
      try {
        const p = await fetchPersonas();
        setPersonas(p);
      } catch (err: any) {
        console.warn("Could not load personas from API (server may be offline):", err);
      }
    }
    loadInitialData();
  }, []);

  // Handler for starting a crash test or replay
  const handleStartRun = useCallback(
    async (isReplay: boolean = false) => {
      setErrorBanner(null);
      setIsRunning(true);

      // Initialize lane states to ready/dispatched
      const initialLanes: Record<number, LaneTelemetryState> = {};
      personas.forEach((p, idx) => {
        initialLanes[idx + 1] = {
          lane: idx + 1,
          persona: p,
          status: "IDLE",
          lastAction: "Queued in swarm...",
        };
      });
      setLaneStates(initialLanes);

      try {
        const run = await createRun({
          target: selectedTarget,
          policy: selectedPolicy,
          seed: 42,
          replay: isReplay,
        });

        setCurrentRun(run);

        // Subscribe to real-time SSE telemetry frames
        const unsubscribe = subscribeRunEvents(
          run.id,
          (event: RunEvent) => {
            if (event.lane) {
              setLaneStates((prev) => {
                const existing = prev[event.lane!] || {
                  lane: event.lane!,
                  persona: personas[event.lane! - 1] || ({} as any),
                  status: "IDLE",
                };

                let newStatus = existing.status;
                if (event.event === "agent_step") {
                  newStatus = "DISPATCHED";
                } else if (event.event === "finding") {
                  newStatus = "FAILED";
                } else if (event.event === "paypal_event") {
                  newStatus = event.status === "COMPLETED" ? "COMPLETED" : "BLOCKED";
                } else if (event.event === "store_ledger_row") {
                  newStatus = event.status?.includes("PASS") ? "COMPLETED" : "BLOCKED";
                }

                return {
                  ...prev,
                  [event.lane!]: {
                    ...existing,
                    status: newStatus,
                    lastAction: event.action || existing.lastAction,
                    actor: event.actor || existing.actor,
                    paypalId: event.paypal_id || existing.paypalId,
                    amount: event.amount || existing.amount,
                    ruleHit: event.rule_hit || existing.ruleHit,
                  },
                };
              });
            }

            if (event.event === "run_completed") {
              setIsRunning(false);
              // Refresh completed summary with score
              getRun(run.id).then(setCurrentRun).catch(console.error);
            }
          },
          () => {
            setIsRunning(false);
          },
          (err) => {
            console.warn("SSE stream ended or disconnected:", err);
            setIsRunning(false);
          }
        );

        return () => unsubscribe();
      } catch (err: any) {
        console.error("Failed to initiate run:", err);
        setErrorBanner(
          err?.problem?.detail || err?.message || "Failed to start crash test. Is the FastAPI backend running?"
        );
        setIsRunning(false);
      }
    },
    [selectedTarget, selectedPolicy, personas]
  );

  return (
    <div className="min-h-screen bg-[#090A0F] text-[#F1F5F9] flex flex-col font-sans">
      {/* Telemetry Header */}
      <Header
        selectedTarget={selectedTarget}
        onSelectTarget={setSelectedTarget}
        selectedPolicy={selectedPolicy}
        onSelectPolicy={setSelectedPolicy}
        isRunning={isRunning}
        onRunCrashTest={() => handleStartRun(false)}
        onReplayLastRun={() => handleStartRun(true)}
        currentScore={currentRun?.score}
        targetName={currentRun?.target_name}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-6 flex flex-col gap-6">
        {/* Error notification banner if backend is unreachable */}
        {errorBanner && (
          <div className="p-4 rounded-lg bg-rose-950/60 border border-rose-800/80 text-rose-300 text-sm flex items-center gap-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-400" />
            <div>
              <p className="font-semibold">Backend Connection Alert</p>
              <p className="text-xs text-rose-300/80 mt-0.5">{errorBanner}</p>
            </div>
          </div>
        )}

        {/* Live Swarm Telemetry Lanes */}
        <SwarmLanes
          personas={personas}
          laneStates={laneStates}
          isRunning={isRunning}
        />

        {/* Milestone Indicator Banner */}
        <div className="rounded-xl border border-[#242838] bg-[#11131A] p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-950/80 border border-emerald-700/60 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">
                Task 1.0C Complete — Connected 9-Lane Swarm Telemetry
              </h3>
              <p className="text-xs text-[#94A3B8]">
                Click <strong>Run Crash Test</strong> or <strong>Replay</strong> to animate all 9 persona lanes via FastAPI SSE.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 font-mono text-xs text-[#64748B]">
            <Zap className="w-3.5 h-3.5 text-[#06B6D4]" />
            <span>Next Task 1.0D: AG Grid Results Matrix &amp; Dual-Ledger Inspector</span>
          </div>
        </div>
      </main>
    </div>
  );
}
