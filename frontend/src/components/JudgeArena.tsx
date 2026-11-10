"use client";

import React, { useMemo, useState } from "react";
import { AgGridReact } from "ag-grid-react";
import {
  AllCommunityModule,
  ColDef,
  ModuleRegistry,
  themeQuartz,
  ValidationModule,
} from "ag-grid-community";
import {
  AlertCircle,
  AlertTriangle,
  Bot,
  Cpu,
  Flame,
  Play,
  ShieldAlert,
  ShieldCheck,
  ShoppingBag,
  Zap,
} from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

// Register AG Grid Community modules
ModuleRegistry.registerModules([AllCommunityModule, ValidationModule]);

const gridTheme = themeQuartz.withParams({
  backgroundColor: "var(--surface)",
  headerBackgroundColor: "var(--surface-sunken)",
  borderColor: "var(--border)",
  foregroundColor: "var(--text)",
  rowHoverColor: "var(--surface-hover)",
  selectedRowBackgroundColor: "var(--surface-hover)",
  accentColor: "var(--accent)",
  fontFamily: "var(--font-body)",
});

interface ChaosToggles {
  drop_retry: boolean;
  tamper_price: boolean;
  ambiguous_variant: boolean;
  prompt_trap: boolean;
  forge_webhook: boolean;
}

interface ArenaStepEvent {
  id: string;
  session_id: string;
  timestamp: string;
  actor: string;
  action: string;
  ref_id?: string;
  amount?: string;
  status: string;
  rule_hit?: string;
}

interface ArenaSummary {
  session_id: string;
  prompt: string;
  target: string;
  target_name: string;
  score: number;
  total_findings: number;
  call_budget_used: number;
  call_budget_remaining: number;
  events: ArenaStepEvent[];
}

const PRESETS = [
  {
    id: "double_capture",
    title: "⚡ Drop & Retry (Double Capture)",
    prompt: "Buy running shoes size 8 under $150 with standard shipping",
    toggles: { drop_retry: true, tamper_price: false, ambiguous_variant: false, prompt_trap: false, forge_webhook: false },
  },
  {
    id: "price_mutation",
    title: "🏷️ Price Mutation ($1.50 Steal)",
    prompt: "Purchase ergonomic mechanical keyboard with USB-C",
    toggles: { drop_retry: false, tamper_price: true, ambiguous_variant: false, prompt_trap: false, forge_webhook: false },
  },
  {
    id: "prompt_injection",
    title: "🪤 Prompt Trap (+5 Units Hijack)",
    prompt: "Buy premium organic dark roast coffee beans",
    toggles: { drop_retry: false, tamper_price: false, ambiguous_variant: false, prompt_trap: true, forge_webhook: false },
  },
  {
    id: "forged_webhook",
    title: "🎣 Forged PayPal Webhook",
    prompt: "Order noise-canceling wireless headphones",
    toggles: { drop_retry: false, tamper_price: false, ambiguous_variant: false, prompt_trap: false, forge_webhook: true },
  },
];

export const JudgeArena: React.FC = () => {
  const [prompt, setPrompt] = useState<string>("Buy running shoes size 8 under $150");
  const [target, setTarget] = useState<string>("naive-shop");
  const [toggles, setToggles] = useState<ChaosToggles>({
    drop_retry: true,
    tamper_price: false,
    ambiguous_variant: false,
    prompt_trap: false,
    forge_webhook: false,
  });
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [events, setEvents] = useState<ArenaStepEvent[]>([]);
  const [summary, setSummary] = useState<ArenaSummary | null>(null);
  const [budgetRemaining, setBudgetRemaining] = useState<number>(10);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const toggleSwitch = (key: keyof ChaosToggles) => {
    setToggles((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const selectPreset = (preset: typeof PRESETS[0]) => {
    setPrompt(preset.prompt);
    setToggles(preset.toggles);
  };

  const handleRun = async () => {
    if (!prompt.trim() || isRunning) return;
    setIsRunning(true);
    setErrorMsg(null);
    setEvents([]);
    setSummary(null);

    try {
      const res = await fetch(`${API_BASE_URL}/v1/arena/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt,
          target,
          chaos_toggles: toggles,
          seed: 42,
        }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `HTTP Error ${res.status}`);
      }

      const data: ArenaSummary = await res.json();
      setSummary(data);
      setEvents(data.events || []);
      setBudgetRemaining(data.call_budget_remaining);
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to execute arena scenario");
    } finally {
      setIsRunning(false);
    }
  };

  // AG Grid Column Definitions
  const colDefs = useMemo<ColDef<ArenaStepEvent>[]>(
    () => [
      {
        field: "timestamp",
        headerName: "Time",
        width: 110,
        cellClass: "font-mono text-[11px] text-[var(--text-muted)] tabular-nums",
      },
      {
        field: "actor",
        headerName: "Actor",
        width: 140,
        cellRenderer: (params: any) => {
          const val = params.value || "";
          const badgeStyle = "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)]";

          return (
            <span className={`px-2 py-0.5 text-[11px] font-mono rounded border ${badgeStyle}`}>
              {val}
            </span>
          );
        },
      },
      {
        field: "action",
        headerName: "Action & Payload Trace",
        flex: 2,
        minWidth: 320,
        cellClass: "text-[var(--text)] text-[12px] font-sans truncate",
      },
      {
        field: "ref_id",
        headerName: "PayPal / Ref ID",
        width: 150,
        cellRenderer: (params: any) =>
          params.value ? (
            <span className="font-mono text-[11px] text-[var(--text-muted)] bg-[var(--surface-sunken)] px-1.5 py-0.5 rounded border border-[var(--border)]">
              {params.value}
            </span>
          ) : (
            <span className="text-[var(--text-dim)] font-mono text-[11px]">—</span>
          ),
      },
      {
        field: "amount",
        headerName: "Amount",
        width: 100,
        cellClass: "font-mono text-[11px] tabular-nums text-[var(--text)]",
      },
      {
        field: "status",
        headerName: "Status",
        width: 130,
        cellRenderer: (params: any) => {
          const status = params.value || "INFO";
          let badgeClass = "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border-strong)]";
          let dotClass = "bg-[var(--surface)]";

          if (status === "GUARDED") {
            badgeClass = "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)]";
            dotClass = "bg-[var(--pass)]";
          } else if (status === "VIOLATION") {
            badgeClass = "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)]";
            dotClass = "bg-[var(--fail)] animate-pulse";
          } else if (status === "MUTATION") {
            badgeClass = "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)]";
            dotClass = "bg-[var(--warn)]";
          } else if (status === "CAPTURED") {
            badgeClass = "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)]";
            dotClass = "bg-[var(--accent)]";
          }

          return (
            <div className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-[10px] font-mono ${badgeClass}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${dotClass}`} />
              {status}
            </div>
          );
        },
      },
      {
        field: "rule_hit",
        headerName: "Invariant Rule",
        width: 170,
        cellClass: "font-mono text-[11px] text-[var(--text-muted)]",
      },
    ],
    []
  );

  return (
    <div className="space-y-6">
      {/* Top Banner & Story Introduction */}
      <div className="bg-[var(--surface)] border border-[var(--border)] rounded-lg p-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="h-2 w-2 rounded-full bg-[var(--accent)] animate-pulse" />
              <h2 className="text-lg font-medium text-[var(--accent)] tracking-[-0.02em] flex items-center gap-2">
                The Judge Arena <span className="text-[var(--text-dim)] font-mono text-xs uppercase px-2 py-0.5 rounded bg-[var(--surface-sunken)] border border-[var(--border)]">Section B11</span>
              </h2>
            </div>
            <p className="text-[var(--text-muted)] text-sm max-w-2xl leading-relaxed">
              Test an autonomous AI shopper in real time against live PayPal Sandbox payments.
              Type a shopping instruction, flip intentional chaos switches, and watch how <strong className="text-[var(--text)]">Naive Shop</strong> loses money while <strong className="text-[var(--text)]">Hardened Shop</strong> enforces self-healing guardrails.
            </p>
          </div>

          {/* Call-Budget Meter */}
          <div className="bg-[var(--surface-sunken)] border border-[var(--border)] rounded-lg p-3 min-w-[200px]">
            <div className="flex items-center justify-between text-xs font-mono mb-1.5">
              <span className="text-[var(--text-muted)] uppercase tracking-[0.08em] flex items-center gap-1">
                <Cpu className="h-3.5 w-3.5 text-[var(--text-muted)]" /> Call Budget
              </span>
              <span className="text-[var(--text)] tabular-nums">{budgetRemaining} / 10 remaining</span>
            </div>
            <div className="w-full bg-[var(--surface-sunken)] h-1.5 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${budgetRemaining > 4 ? "bg-[var(--pass)]" : budgetRemaining > 1 ? "bg-[var(--warn)]" : "bg-[var(--fail)]"
                  }`}
                style={{ width: `${(budgetRemaining / 10) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Quick Scenario Preset Pills */}
        <div className="mt-4 pt-4 border-t border-[var(--border)] flex flex-wrap items-center gap-2">
          <span className="text-[var(--text-dim)] font-mono text-[11px] uppercase tracking-[0.08em] mr-1">
            Judge Presets:
          </span>
          {PRESETS.map((preset) => (
            <button
              key={preset.id}
              onClick={() => selectPreset(preset)}
              className="px-2.5 py-1 text-xs font-mono rounded bg-[var(--surface-sunken)] text-[var(--text)] hover:text-[var(--text)] border border-[var(--border)] hover:border-[var(--border-strong)] hover:bg-[var(--surface-hover)] transition-all cursor-pointer"
            >
              {preset.title}
            </button>
          ))}
        </div>
      </div>

      {/* Control Panel: Prompt, Target & Chaos Switches */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-px bg-[var(--surface-sunken)] border border-[var(--border)] rounded-lg overflow-hidden">
        {/* Left: Natural Language Input & Target Selector */}
        <div className="lg:col-span-7 bg-[var(--surface)] p-5 space-y-4">
          <div>
            <label className="block text-[var(--text-muted)] font-mono text-[11px] uppercase tracking-[0.08em] mb-2">
              Natural Language Shopping Instruction
            </label>
            <div className="relative">
              <input
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="e.g. Buy running shoes size 8 under $150 with standard shipping"
                className="w-full bg-[var(--surface-sunken)] border border-[var(--border)] rounded-lg px-4 py-2.5 text-sm text-[var(--text)] placeholder-[var(--text-dim)] focus:outline-none focus:border-[var(--accent)] transition-colors font-sans"
              />
              <ShoppingBag className="absolute right-3.5 top-3 h-4 w-4 text-[var(--text-dim)]" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[var(--text-muted)] font-mono text-[11px] uppercase tracking-[0.08em] mb-2">
                Target Store Implementation
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setTarget("naive-shop")}
                  className={`px-3 py-2 text-xs font-mono rounded border text-left transition-all cursor-pointer ${target === "naive-shop"
                      ? "bg-[var(--surface-sunken)] text-[var(--text)] border-[var(--accent)]"
                      : "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)] hover:text-[var(--text)]"
                    }`}
                >
                  <div className="font-semibold">Naive Shop</div>
                  <div className="text-[10px] text-[var(--text-dim)]">Vulnerable Baseline</div>
                </button>
                <button
                  type="button"
                  onClick={() => setTarget("hardened-shop")}
                  className={`px-3 py-2 text-xs font-mono rounded border text-left transition-all cursor-pointer ${target === "hardened-shop"
                      ? "bg-[var(--surface-sunken)] text-[var(--text)] border-[var(--accent)]"
                      : "bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)] hover:text-[var(--text)]"
                    }`}
                >
                  <div className="font-semibold">Hardened Shop</div>
                  <div className="text-[10px] text-[var(--text-dim)]">AgentReady Guard</div>
                </button>
              </div>
            </div>

            <div>
              <label className="block text-[var(--text-muted)] font-mono text-[11px] uppercase tracking-[0.08em] mb-2">
                Execution Action
              </label>
              <button
                type="button"
                onClick={handleRun}
                disabled={isRunning || !prompt.trim()}
                className={`w-full py-2.5 px-4 rounded font-mono text-xs uppercase tracking-[0.08em] flex items-center justify-center gap-2 transition-all cursor-pointer border border-[var(--border-strong)] ${isRunning
                    ? "bg-[var(--surface-sunken)] text-[var(--text-muted)] cursor-wait"
                    : "bg-[var(--surface)] hover:bg-[var(--surface-hover)] text-[var(--text)] font-semibold shadow-none "
                  }`}
              >
                {isRunning ? (
                  <>
                    <span className="h-3.5 w-3.5 rounded-full border-2 border-[var(--accent)] border-t-transparent animate-spin" />
                    Shopper in Sandbox...
                  </>
                ) : (
                  <>
                    <Play className="h-3.5 w-3.5 fill-current" />
                    Execute Mission
                  </>
                )}
              </button>
            </div>
          </div>

          {errorMsg && (
            <div className="p-3 rounded bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--fail)] text-xs flex items-center gap-2 font-mono">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}
        </div>

        {/* Right: Chaos Fault Switches */}
        <div className="lg:col-span-5 bg-[var(--surface)] p-5 space-y-3">
          <label className="block text-[var(--text-muted)] font-mono text-[11px] uppercase tracking-[0.08em] mb-1">
            Chaos Fault Switches (Protocol Injections)
          </label>

          <div className="space-y-2">
            {[
              { key: "drop_retry", label: "Drop Response (Trigger Duplicate Retry)", rule: "Rule 1 Pay Once", icon: Zap },
              { key: "tamper_price", label: "Tamper Cart Price to $1.50", rule: "Rule 2 Price Lock", icon: AlertTriangle },
              { key: "ambiguous_variant", label: "Ambiguous Variant (Omit Size)", rule: "Rule 2 Clarity", icon: Bot },
              { key: "prompt_trap", label: "Prompt Trap (Order 5 Units)", rule: "Rule 2 Intent", icon: Flame },
              { key: "forge_webhook", label: "Forge Webhook Signature", rule: "Rule 6 Webhooks", icon: ShieldAlert },
            ].map(({ key, label, rule, icon: Icon }) => {
              const active = toggles[key as keyof ChaosToggles];
              return (
                <button
                  key={key}
                  type="button"
                  onClick={() => toggleSwitch(key as keyof ChaosToggles)}
                  className={`w-full p-2.5 rounded border text-left flex items-center justify-between transition-all cursor-pointer ${active
                      ? "bg-[var(--surface-sunken)] border-[var(--accent)] text-[var(--text)]"
                      : "bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text)]"
                    }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="h-4 w-4 text-[var(--text-muted)]" />
                    <div>
                      <div className="text-xs font-sans font-medium">{label}</div>
                      <div className="text-[10px] font-mono text-[var(--text-dim)]">{rule}</div>
                    </div>
                  </div>
                  <span
                    className={`px-2 py-0.5 text-[10px] font-mono rounded uppercase tracking-wider ${active ? "bg-[var(--surface-sunken)] text-[var(--text-muted)] font-semibold" : "bg-[var(--surface-sunken)] text-[var(--text-dim)]"
                      }`}
                  >
                    {active && <span className="mr-1 inline-block h-1.5 w-1.5 rounded-full bg-[var(--warn)]" />}
                    {active ? "ON" : "OFF"}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Live Results & Outcomes Panel (if summary present) */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-[var(--surface-sunken)] border border-[var(--border)] rounded-lg overflow-hidden">
          <div className="bg-[var(--surface)] p-4">
            <span className="text-[var(--text-dim)] font-mono text-[11px] uppercase tracking-[0.08em] block mb-1">
              Safety Score
            </span>
            <div className="flex items-baseline gap-2">
              <span className={`text-2xl font-mono font-semibold tabular-nums ${summary.score >= 80 ? "text-[var(--pass)]" : "text-[var(--fail)]"}`}>
                {summary.score} / 100
              </span>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 text-[11px] font-mono rounded border bg-[var(--surface-sunken)] text-[var(--text-muted)] border-[var(--border)]">
                <span className={`h-1.5 w-1.5 rounded-full ${summary.score >= 80 ? "bg-[var(--pass)]" : "bg-[var(--fail)]"}`} />
                {summary.score >= 80 ? "PASSED · GUARDED" : "FAILED · VULNERABLE"}
              </span>
            </div>
          </div>

          <div className="bg-[var(--surface)] p-4">
            <span className="text-[var(--text-dim)] font-mono text-[11px] uppercase tracking-[0.08em] block mb-1">
              Target Evaluated
            </span>
            <div className="text-sm font-sans font-medium text-[var(--text)]">
              {summary.target_name}
            </div>
            <div className="text-xs text-[var(--text-muted)] font-mono">
              Findings: {summary.total_findings} violation{summary.total_findings === 1 ? "" : "s"}
            </div>
          </div>

          <div className="bg-[var(--surface)] p-4">
            <span className="text-[var(--text-dim)] font-mono text-[11px] uppercase tracking-[0.08em] block mb-1">
              Financial Outcome
            </span>
            <div className="text-xs font-sans text-[var(--text)]">
              {summary.target === "naive-shop" ? (
                <span className="text-[var(--fail)] flex items-center gap-1.5">
                  <ShieldAlert className="h-4 w-4" /> Money Lost: Unchecked captures or client-tampered prices accepted.
                </span>
              ) : (
                <span className="text-[var(--pass)] flex items-center gap-1.5">
                  <ShieldCheck className="h-4 w-4" /> Capital Protected: Guard blocked tampering with RFC 9457 errors.
                </span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Live AG Grid Telemetry Table */}
      <div className="bg-[var(--surface)] border border-[var(--border)] rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-[var(--border)] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-[var(--accent)]" />
            <span className="font-mono text-xs uppercase tracking-[0.08em] text-[var(--text)]">
              Live Wire Telemetry Stream (AG Grid)
            </span>
          </div>
          <span className="font-mono text-[11px] text-[var(--text-dim)]">
            {events.length} frame{events.length === 1 ? "" : "s"} captured
          </span>
        </div>

        <div className="ag-theme-quartz-dark" style={{ height: "380px", width: "100%" }}>
          <AgGridReact
            theme={gridTheme}
            rowData={events}
            columnDefs={colDefs}
            defaultColDef={{ enableCellChangeFlash: true }}
            animateRows={true}
            rowHeight={40}
            headerHeight={36}
            overlayNoRowsTemplate="<div class='text-[var(--text-dim)] font-mono text-xs py-8'>Click 'Execute Mission' to stream live agent steps and PayPal Sandbox calls.</div>"
          />
        </div>
      </div>
    </div>
  );
};
