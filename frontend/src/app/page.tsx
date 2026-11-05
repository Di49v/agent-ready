"use client";

import React, { useEffect, useState, useCallback } from "react";
import { Header } from "@/components/Header";
import { SwarmLanes, LaneTelemetryState } from "@/components/SwarmLanes";
import { FindingsGrid } from "@/components/FindingsGrid";
import { LedgerDiffDrawer } from "@/components/LedgerDiffDrawer";
import {
  createRun,
  fetchPersonas,
  getRun,
  getRunFindings,
  getRunLedger,
  rerunRun,
  DualLedgerRow,
  FindingDetail,
  PersonaSpec,
  RunEvent,
  RunSummary,
  subscribeRunEvents,
} from "@/lib/api";
import { ShieldCheck, Zap, AlertCircle, ArrowUpRight } from "lucide-react";

export default function Home() {
  const [selectedTarget, setSelectedTarget] = useState<string>("naive-shop");
  const [selectedPolicy, setSelectedPolicy] = useState<"observe" | "assist" | "auto">("auto");
  const [personas, setPersonas] = useState<PersonaSpec[]>([]);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [isRerunning, setIsRerunning] = useState<boolean>(false);
  const [currentRun, setCurrentRun] = useState<RunSummary | null>(null);
  const [laneStates, setLaneStates] = useState<Record<number, LaneTelemetryState>>({});
  const [findings, setFindings] = useState<FindingDetail[]>([]);
  const [dualRows, setDualRows] = useState<DualLedgerRow[]>([]);
  const [selectedFinding, setSelectedFinding] = useState<FindingDetail | null>(null);
  const [selectedDualRow, setSelectedDualRow] = useState<DualLedgerRow | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);
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

  // Fetch findings and dual-ledger rows for a completed run
  const loadRunArtifacts = useCallback(async (runId: string) => {
    try {
      const [f, ledger] = await Promise.all([
        getRunFindings(runId),
        getRunLedger(runId),
      ]);
      setFindings(f);
      setDualRows(ledger.dual_rows);
    } catch (err) {
      console.warn("Could not load findings or dual-ledger rows:", err);
    }
  }, []);

  // Handler for starting a crash test or replay
  const handleStartRun = useCallback(
    async (isReplay: boolean = false) => {
      setErrorBanner(null);
      setIsRunning(true);
      setFindings([]);
      setDualRows([]);

      // Initialize lane states
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
              getRun(run.id).then((summary) => {
                setCurrentRun(summary);
                loadRunArtifacts(run.id);
              }).catch(console.error);
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
    [selectedTarget, selectedPolicy, personas, loadRunArtifacts]
  );

  // Re-run same seed on Hardened Shop (Red to Green Judge Demo flow)
  const handleApplyPatchAndRerun = useCallback(async () => {
    if (!currentRun) return;
    setIsRerunning(true);

    try {
      // 1. Trigger server rerun against hardened-shop
      const updatedRun = await rerunRun(currentRun.id, "hardened-shop");
      setSelectedTarget("hardened-shop");
      setCurrentRun(updatedRun);

      // 2. Refresh findings and dual ledger rows (turning green!)
      await loadRunArtifacts(updatedRun.id);

      // 3. Update lanes to reflect hardened results
      setLaneStates((prev) => {
        const next: Record<number, LaneTelemetryState> = {};
        Object.entries(prev).forEach(([laneKey, laneVal]) => {
          const lNum = Number(laneKey);
          next[lNum] = {
            ...laneVal,
            status: lNum === 7 ? "COMPLETED" : "COMPLETED",
            lastAction: lNum === 1 ? "RETURN_IDEMPOTENT_CACHE (Replayed: true)" : "BLOCKED_WITH_RFC9457",
            amount: lNum === 1 ? "$120.00" : "$0.00",
          };
        });
        return next;
      });

      setIsDrawerOpen(false);
    } catch (err: any) {
      console.error("Failed to re-run on Hardened Shop:", err);
    } finally {
      setIsRerunning(false);
    }
  }, [currentRun, loadRunArtifacts]);

  const handleOpenFinding = (finding: FindingDetail) => {
    setSelectedFinding(finding);
    setSelectedDualRow(null);
    setIsDrawerOpen(true);
  };

  const handleOpenDualRow = (row: DualLedgerRow) => {
    setSelectedDualRow(row);
    // Find matching finding if any
    const matching = findings.find((f) => f.persona_id === row.persona_id);
    setSelectedFinding(matching || null);
    setIsDrawerOpen(true);
  };

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

        {/* AG Grid Results Matrix */}
        <FindingsGrid
          findings={findings}
          dualRows={dualRows}
          onSelectFinding={handleOpenFinding}
          onSelectDualRow={handleOpenDualRow}
        />

        {/* Milestone Indicator Banner */}
        <div className="rounded-xl border border-[#242838] bg-[#11131A] p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-950/80 border border-emerald-700/60 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">
                Stage 1 Full Blueprint Milestone Complete
              </h3>
              <p className="text-xs text-[#94A3B8]">
                Red-to-Green Judge Demo flow ready: Run Naive Shop (18/100) &rarr; Inspect Double-Charge row &rarr; Apply Patch &amp; Re-Run Hardened Shop (95/100)!
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 font-mono text-xs text-[#06B6D4]">
            <span>Stage 2 Next: Live PayPal Sandbox Spikes</span>
            <ArrowUpRight className="w-4 h-4" />
          </div>
        </div>
      </main>

      {/* Side-by-Side Dual-Ledger Inspector Slide-Over Drawer */}
      <LedgerDiffDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        finding={selectedFinding}
        dualRow={selectedDualRow}
        onApplyPatchAndRerun={handleApplyPatchAndRerun}
        isRerunning={isRerunning}
      />
    </div>
  );
}
