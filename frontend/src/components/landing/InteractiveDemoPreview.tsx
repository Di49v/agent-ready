"use client";

import React, { useState } from "react";
import Link from "next/link";
import { PLAYGROUND_URL } from "@/lib/constants";
import { 
  AlertCircle, 
  ShieldCheck, 
  Server, 
  Key, 
  FileWarning, 
  CheckCircle,
  Zap
} from "lucide-react";

// Mini helper icon for the vulnerable server
const XIcon = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
  </svg>
);

export const InteractiveDemoPreview: React.FC = () => {
  const [selectedShop, setSelectedShop] = useState<"naive" | "hardened">("naive");

  return (
    <section id="preview" className="py-16 md:py-24 border-b border-[var(--border)] bg-[var(--bg)]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Header */}
        <div className="flex flex-col text-left max-w-3xl mb-10">
          <span className="text-xs font-mono uppercase tracking-wider text-[var(--text-muted)] mb-2 font-medium">
            Architecture Breakdown
          </span>
          <h2 className="font-heading font-semibold text-3xl sm:text-4xl text-[var(--text)] tracking-tight">
            Why Standard Integrations Fail AI Agents
          </h2>
          <p className="mt-3 text-[15px] sm:text-base text-[var(--text-muted)] leading-relaxed">
            Toggle below to understand the critical differences between a standard web integration and a resilient, zero-trust backend designed for autonomous commerce.
          </p>
        </div>

        {/* Main Floating Container */}
        <div className="max-w-5xl mx-auto rounded-xl border border-[var(--border)] bg-[var(--surface)] overflow-hidden shadow-xl hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-1">
          
          {/* Top Control Bar */}
          <div className="bg-[var(--surface-sunken)] px-4 py-3 border-b border-[var(--border)] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            
            {/* Left Side: Tabs */}
            <div className="flex items-center gap-4">
              <span className="hidden sm:inline-block text-[11px] font-mono text-[var(--text-muted)] uppercase tracking-wider">
                Trust Models:
              </span>
              <div className="inline-flex rounded-md bg-[var(--surface)] p-1 border border-[var(--border)] shadow-sm">
                <button
                  onClick={() => setSelectedShop("naive")}
                  className={`px-3.5 py-1.5 rounded text-xs font-mono transition-all cursor-pointer flex items-center gap-2 ${
                    selectedShop === "naive"
                      ? "bg-[var(--fail)]/10 text-[var(--fail)] font-semibold border border-[var(--fail)]/20 shadow-sm"
                      : "text-[var(--text-muted)] hover:text-[var(--text)] border border-transparent"
                  }`}
                >
                  <span className={`inline-block h-1.5 w-1.5 rounded-full ${selectedShop === "naive" ? "bg-[var(--fail)]" : "bg-[var(--text-dim)]"}`} />
                  Legacy/Baseline Store (Vulnerable)
                </button>
                <button
                  onClick={() => setSelectedShop("hardened")}
                  className={`px-3.5 py-1.5 rounded text-xs font-mono transition-all cursor-pointer flex items-center gap-2 ${
                    selectedShop === "hardened"
                      ? "bg-[var(--pass)]/10 text-[var(--pass)] font-semibold border border-[var(--pass)]/20 shadow-sm"
                      : "text-[var(--text-muted)] hover:text-[var(--text)] border border-transparent"
                  }`}
                >
                  <span className={`inline-block h-1.5 w-1.5 rounded-full ${selectedShop === "hardened" ? "bg-[var(--pass)]" : "bg-[var(--text-dim)]"}`} />
                  Zero-Trust/Sheilded Store (Guard)
                </button>
              </div>
            </div>

            {/* Right Side: Direct Simulation Button */}
            <Link 
              href={PLAYGROUND_URL}
              className="inline-flex items-center justify-center gap-1.5 px-4 py-1.5 rounded-md text-xs font-semibold bg-[var(--accent)] text-[var(--accent-foreground)] hover:bg-[var(--accent-hover)] transition-colors shadow-sm cursor-pointer"
            >
              <Zap className="w-3.5 h-3.5 fill-current" />
              <span>Direct Simulation</span>
            </Link>
          </div>

          {/* Content Area */}
          <div className="p-6 md:p-10 bg-[var(--surface)] min-h-[360px]">
            {selectedShop === "naive" ? (
              <div className="grid grid-cols-1 md:grid-cols-12 gap-10 items-center animate-in fade-in zoom-in-95 duration-300">
                
                {/* Left Text */}
                <div className="md:col-span-7 space-y-6">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="w-6 h-6 text-[var(--fail)]" />
                    <h3 className="text-xl sm:text-2xl font-heading font-semibold text-[var(--text)]">The Naive Store</h3>
                  </div>
                  <p className="text-[14px] sm:text-[15px] text-[var(--text-muted)] leading-relaxed">
                    A "Naive Shop" represents a standard web integration. It assumes the buyer is a human clicking buttons in a browser, making it highly vulnerable to autonomous AI agents that act unpredictably and at high speeds.
                  </p>
                  <ul className="space-y-6 border-t border-[var(--border)] pt-6">
                    <li className="flex items-start gap-3.5">
                      <div className="bg-[var(--fail)]/10 p-2 rounded-md mt-0.5 border border-[var(--fail)]/20">
                        <FileWarning className="w-4 h-4 text-[var(--fail)] flex-shrink-0" />
                      </div>
                      <div>
                        <strong className="block text-[14px] text-[var(--text)] mb-1">Missing Idempotency Keys</strong>
                        <span className="text-[13.5px] text-[var(--text-muted)] leading-relaxed block">If a network timeout occurs, AI agents automatically retry the request. Without proper caching, the server processes both requests, double-charging the customer.</span>
                      </div>
                    </li>
                    <li className="flex items-start gap-3.5">
                      <div className="bg-[var(--fail)]/10 p-2 rounded-md mt-0.5 border border-[var(--fail)]/20">
                        <AlertCircle className="w-4 h-4 text-[var(--fail)] flex-shrink-0" />
                      </div>
                      <div>
                        <strong className="block text-[14px] text-[var(--text)] mb-1">Client-Side Price Trust</strong>
                        <span className="text-[13.5px] text-[var(--text-muted)] leading-relaxed block">The server accepts price totals directly from the API payload. A rogue or hallucinating agent can alter the cart total, leading to silent under-collection.</span>
                      </div>
                    </li>
                  </ul>
                </div>

                {/* Right Graphic */}
                <div className="md:col-span-5 flex items-center justify-center bg-[var(--surface-sunken)] rounded-xl border border-[var(--border)] p-8 shadow-inner h-full min-h-[280px]">
                   <div className="text-center space-y-5">
                      <div className="w-24 h-24 mx-auto bg-[var(--fail)]/10 rounded-full flex items-center justify-center border border-[var(--fail)]/20 shadow-sm relative">
                        <Server className="w-10 h-10 text-[var(--fail)]" />
                        <span className="absolute bottom-0 right-0 flex h-7 w-7 items-center justify-center rounded-full bg-[var(--fail)] border-[3px] border-[var(--surface-sunken)]">
                          <XIcon className="w-3.5 h-3.5 text-white" />
                        </span>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-[var(--fail)]">Vulnerable Backend</div>
                        <div className="text-[13px] text-[var(--text-muted)] mt-1.5 leading-relaxed">Susceptible to agent swarms<br/>and dual-ledger leakage.</div>
                      </div>
                   </div>
                </div>

              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-12 gap-10 items-center animate-in fade-in zoom-in-95 duration-300">
                
                {/* Left Text */}
                <div className="md:col-span-7 space-y-6">
                  <div className="flex items-center gap-2 mb-2">
                    <ShieldCheck className="w-6 h-6 text-[var(--pass)]" />
                    <h3 className="text-xl sm:text-2xl font-heading font-semibold text-[var(--text)]">The Hardened Store</h3>
                  </div>
                  <p className="text-[14px] sm:text-[15px] text-[var(--text-muted)] leading-relaxed">
                    A "Hardened Shop" implements strict zero-trust commerce invariants. It assumes every incoming API request could be from a faulty agent, validating every single action against a deterministic source of truth.
                  </p>
                  <ul className="space-y-6 border-t border-[var(--border)] pt-6">
                    <li className="flex items-start gap-3.5">
                      <div className="bg-[var(--pass)]/10 p-2 rounded-md mt-0.5 border border-[var(--pass)]/20">
                        <Key className="w-4 h-4 text-[var(--pass)] flex-shrink-0" />
                      </div>
                      <div>
                        <strong className="block text-[14px] text-[var(--text)] mb-1">Strict Request Idempotency</strong>
                        <span className="text-[13.5px] text-[var(--text-muted)] leading-relaxed block">Enforces `PayPal-Request-Id`. If an agent retries a delayed request, the server returns the cached success response instead of creating a duplicate charge.</span>
                      </div>
                    </li>
                    <li className="flex items-start gap-3.5">
                      <div className="bg-[var(--pass)]/10 p-2 rounded-md mt-0.5 border border-[var(--pass)]/20">
                        <CheckCircle className="w-4 h-4 text-[var(--pass)] flex-shrink-0" />
                      </div>
                      <div>
                        <strong className="block text-[14px] text-[var(--text)] mb-1">Dual-Ledger Reconciliation</strong>
                        <span className="text-[13.5px] text-[var(--text-muted)] leading-relaxed block">Prices are strictly recalculated server-side and continuously cross-referenced with PayPal's actual captured amounts to detect any leakage instantly.</span>
                      </div>
                    </li>
                  </ul>
                </div>

                {/* Right Graphic */}
                <div className="md:col-span-5 flex items-center justify-center bg-[var(--surface-sunken)] rounded-xl border border-[var(--border)] p-8 shadow-inner h-full min-h-[280px]">
                   <div className="text-center space-y-5">
                      <div className="w-24 h-24 mx-auto bg-[var(--pass)]/10 rounded-full flex items-center justify-center border border-[var(--pass)]/20 shadow-sm relative">
                        <ShieldCheck className="w-10 h-10 text-[var(--pass)]" />
                        <span className="absolute bottom-0 right-0 flex h-7 w-7 items-center justify-center rounded-full bg-[var(--pass)] border-[3px] border-[var(--surface-sunken)]">
                          <CheckCircle className="w-3.5 h-3.5 text-[var(--surface)]" />
                        </span>
                      </div>
                      <div>
                        <div className="text-lg font-bold text-[var(--pass)]">Zero-Trust Backend</div>
                        <div className="text-[13px] text-[var(--text-muted)] mt-1.5 leading-relaxed">AgentReady Lab Verified<br/>for autonomous agents.</div>
                      </div>
                   </div>
                </div>

              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};