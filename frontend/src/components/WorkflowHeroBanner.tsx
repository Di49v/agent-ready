"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  Bot,
  CheckCircle2,
  Cpu,
  Layers,
  Repeat,
  Shield,
  ShieldAlert,
  ShieldCheck,
  ShoppingBag,
  Sparkles,
  Zap,
} from "lucide-react";

export const WorkflowHeroBanner: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"without_guard" | "with_guard">("with_guard");

  return (
    <div className="bg-[#0D0F14] border border-white/[0.07] rounded-lg p-6 space-y-6">
      {/* Top Header: The 1-Line Pitch & Sponsor Attributions */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 border-b border-white/[0.07] pb-5">
        <div className="space-y-2 max-w-3xl">
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-mono uppercase tracking-[0.08em] bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Autonomous AI Commerce Security
            </span>
            <span className="text-zinc-500 font-mono text-[11px]">·</span>
            <span className="text-zinc-400 font-mono text-[11px]">PayPal Sandbox & APIMatic Middleware</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-medium text-white tracking-[-0.03em] leading-tight">
            PayPal protects the payment. Nobody tests the merchant's side of an agent order.{" "}
            <span className="text-cyan-400">AgentReady Lab does.</span>
          </h1>

          <p className="text-zinc-400 text-sm leading-relaxed">
            When autonomous AI agents buy on behalf of humans, unhandled network drops trigger duplicate captures ($240 charged for $120 order), client payloads mutate prices ($1.50 steal), and prompt traps hijack cart quantities. Lab crash-tests the store with a 9-persona swarm, reconciles ledgers, and proves self-healing.
          </p>
        </div>

        {/* Sponsor Badges */}
        <div className="flex lg:flex-col flex-wrap gap-2 shrink-0">
          <div className="px-3 py-1.5 rounded bg-[#13161F] border border-white/[0.07] flex items-center gap-2 text-xs font-mono text-zinc-300">
            <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
            <span>PayPal Sandbox v2.29</span>
          </div>
          <div className="px-3 py-1.5 rounded bg-[#13161F] border border-white/[0.07] flex items-center gap-2 text-xs font-mono text-zinc-300">
            <span className="h-1.5 w-1.5 rounded-full bg-purple-400" />
            <span>APIMatic Context Plugin</span>
          </div>
          <div className="px-3 py-1.5 rounded bg-[#13161F] border border-white/[0.07] flex items-center gap-2 text-xs font-mono text-zinc-300">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />
            <span>Channel3 Product Catalog</span>
          </div>
          <div className="px-3 py-1.5 rounded bg-[#13161F] border border-white/[0.07] flex items-center gap-2 text-xs font-mono text-zinc-300">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
            <span>AG Grid Community v32</span>
          </div>
        </div>
      </div>

      {/* Interactive 3-Card Cart-to-Ledger Mini-Simulator */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <span className="font-mono text-[11px] uppercase tracking-[0.08em] text-zinc-400 flex items-center gap-1.5">
            <Cpu className="h-3.5 w-3.5 text-cyan-400" /> Interactive Cart-to-Ledger Mini-Simulator:
          </span>

          {/* Guard Toggle Pill */}
          <div className="inline-flex rounded-lg p-0.5 bg-[#13161F] border border-white/[0.08]">
            <button
              onClick={() => setActiveTab("without_guard")}
              className={`px-3 py-1 text-xs font-mono rounded transition-all cursor-pointer ${
                activeTab === "without_guard"
                  ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              Without Guard (Naive Shop)
            </button>
            <button
              onClick={() => setActiveTab("with_guard")}
              className={`px-3 py-1 text-xs font-mono rounded transition-all cursor-pointer ${
                activeTab === "with_guard"
                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              With Guard (Hardened Shop)
            </button>
          </div>
        </div>

        {/* 3-Card Exposed Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-px bg-white/[0.07] border border-white/[0.07] rounded-lg overflow-hidden">
          {/* Card 1: Human Approved Intent */}
          <div className="bg-[#0D0F14] p-4 flex flex-col justify-between space-y-3">
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-zinc-400 mb-1">
                <span className="flex items-center gap-1.5 text-zinc-300">
                  <ShoppingBag className="h-3.5 w-3.5 text-cyan-400" /> 1. Human Cart Approval
                </span>
                <span className="text-[10px] text-zinc-500 font-mono">HMAC SHA-256</span>
              </div>
              <div className="text-white font-medium text-sm">
                Brooks Ghost 16 Running Shoes
              </div>
              <div className="text-xs text-zinc-400 mt-1 font-mono">
                Size 8 · 1 Unit · Server Price: <strong className="text-white">$149.95</strong>
              </div>
            </div>
            <div className="text-[11px] font-mono text-emerald-400 bg-emerald-950/30 px-2 py-1 rounded border border-emerald-800/30 flex items-center gap-1.5">
              <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
              <span>Signed Cart Receipt Minted</span>
            </div>
          </div>

          {/* Card 2: Chaos Fault / Adversarial Agent Mutation */}
          <div className="bg-[#0D0F14] p-4 flex flex-col justify-between space-y-3">
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-zinc-400 mb-1">
                <span className="flex items-center gap-1.5 text-amber-400">
                  <Zap className="h-3.5 w-3.5" /> 2. Wire Fault Injected
                </span>
                <span className="text-[10px] font-mono text-amber-500">Chaos Proxy</span>
              </div>
              <div className="text-white font-medium text-sm">
                Dropped HTTP 200 & Automated Retry
              </div>
              <div className="text-xs text-zinc-400 mt-1 font-mono">
                Capture succeeds, but agent response dropped. Shopper retries with same cart.
              </div>
            </div>
            <div className="text-[11px] font-mono text-amber-300 bg-amber-950/30 px-2 py-1 rounded border border-amber-800/30 flex items-center gap-1.5">
              <Repeat className="h-3.5 w-3.5 shrink-0" />
              <span>2x POST /v2/checkout/orders</span>
            </div>
          </div>

          {/* Card 3: Dynamic Outcome (Toggleable) */}
          <div className="bg-[#0D0F14] p-4 flex flex-col justify-between space-y-3">
            <div>
              <div className="flex items-center justify-between text-xs font-mono text-zinc-400 mb-1">
                <span className="flex items-center gap-1.5 text-zinc-300">
                  {activeTab === "without_guard" ? (
                    <ShieldAlert className="h-3.5 w-3.5 text-rose-400" />
                  ) : (
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
                  )}
                  3. Store Ledger Outcome
                </span>
                <span className={`text-[10px] font-mono ${activeTab === "without_guard" ? "text-rose-400" : "text-emerald-400"}`}>
                  {activeTab === "without_guard" ? "18 / 100 🔴" : "95 / 100 🟢"}
                </span>
              </div>

              {activeTab === "without_guard" ? (
                <div>
                  <div className="text-rose-400 font-medium text-sm">
                    Double Capture: $299.90 Charged
                  </div>
                  <div className="text-xs text-zinc-400 mt-1">
                    Store lacks <code className="text-zinc-300">PayPal-Request-Id</code>. Customer charged twice for a single order.
                  </div>
                </div>
              ) : (
                <div>
                  <div className="text-emerald-400 font-medium text-sm">
                    Idempotent Replay: $149.95 Preserved
                  </div>
                  <div className="text-xs text-zinc-400 mt-1">
                    Guard checks idempotency cache, returns original capture with <code className="text-zinc-300">Idempotent-Replayed: true</code>.
                  </div>
                </div>
              )}
            </div>

            <div className={`text-[11px] font-mono px-2 py-1 rounded border flex items-center gap-1.5 ${
              activeTab === "without_guard"
                ? "bg-rose-950/30 text-rose-300 border-rose-800/30"
                : "bg-emerald-950/30 text-emerald-300 border-emerald-800/30"
            }`}>
              {activeTab === "without_guard" ? (
                <>
                  <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-rose-400" />
                  <span>Rule 1 Violation · Capital Lost</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-emerald-400" />
                  <span>Rule 1 Passed · 0 False Alarms</span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

