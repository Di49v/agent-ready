"use client";

import React from "react";
import { 
  Users, Server, Zap, Database, CheckCircle2, 
  AlertTriangle, GitMerge, FileCode2, ArrowRight
} from "lucide-react";

export const SwarmDiagram = () => (
  <div className="flex items-center justify-end w-full h-full pr-2">
    <div className="flex items-center gap-3 lg:gap-4 shrink-0 scale-[0.70] lg:scale-[0.85] xl:scale-100 origin-right">
      
      {/* Tight 3x3 Grid of Personas */}
      <div className="grid grid-cols-3 gap-1.5 shrink-0 p-2 rounded-xl bg-[var(--surface-sunken)] border border-[var(--border)]">
        {[...Array(9)].map((_, i) => (
          <div key={i} className="w-7 h-7 rounded-md bg-[var(--surface)] border border-[var(--border)] flex items-center justify-center animate-pulse" style={{ animationDelay: `${i * 100}ms` }}>
            <Users className="w-3.5 h-3.5 text-[var(--text-muted)]" />
          </div>
        ))}
      </div>
      
      {/* Network Traffic */}
      <div className="flex flex-col items-center gap-1 shrink-0">
        <ArrowRight className="w-5 h-5 text-[var(--accent)]" />
        <div className="text-[9px] font-mono text-[var(--accent)] whitespace-nowrap">Batched</div>
      </div>

      {/* Target Store */}
      <div className="w-16 h-16 rounded-xl bg-[var(--surface)] border-2 border-[var(--border-strong)] flex flex-col items-center justify-center gap-1 shrink-0">
        <Server className="w-6 h-6 text-[var(--text)]" />
        <span className="text-[9px] font-mono font-bold text-[var(--text)]">STORE</span>
      </div>

    </div>
  </div>
);

export const ChaosDiagram = () => (
  <div className="flex items-center justify-end w-full h-full pr-2">
    <div className="flex items-center gap-3 shrink-0 scale-[0.70] lg:scale-[0.85] xl:scale-100 origin-right">
      
      <div className="w-12 h-12 rounded-xl bg-[var(--surface-sunken)] border border-[var(--border)] flex items-center justify-center shrink-0">
        <Server className="w-5 h-5 text-[var(--text-muted)]" />
      </div>
      
      {/* Chaos Proxy */}
      <div className="flex flex-col items-center shrink-0 mx-1">
        <div className="flex items-center gap-1.5">
          <div className="h-px w-4 bg-[var(--pass)]"></div>
          <div className="w-10 h-10 rounded-full bg-[var(--warn)]/10 border border-[var(--warn)]/30 flex items-center justify-center relative shrink-0">
            <Zap className="w-5 h-5 text-[var(--warn)]" />
            <div className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-[var(--fail)] animate-ping"></div>
          </div>
          <div className="h-px w-4 bg-[var(--fail)] border-t border-dashed border-[var(--fail)]"></div>
        </div>
        <div className="text-[9px] font-mono text-[var(--warn)] mt-2 bg-[var(--warn)]/10 px-2 py-0.5 rounded whitespace-nowrap">
          ACK DROP
        </div>
      </div>

      <div className="w-12 h-12 rounded-xl bg-[#00457C]/10 border border-[#00457C]/30 flex items-center justify-center shrink-0">
        <span className="font-bold text-[#00457C] text-[10px]">PayPal</span>
      </div>

    </div>
  </div>
);

export const ReconDiagram = () => (
  <div className="flex items-center justify-end w-full h-full pr-2">
    <div className="flex items-center gap-3 shrink-0 scale-[0.70] lg:scale-[0.85] xl:scale-100 origin-right">
      
      <div className="flex flex-col items-center gap-2 shrink-0">
        <div className="w-12 h-12 rounded-xl bg-[var(--fail-soft)] border border-[var(--fail-border)] flex items-center justify-center">
          <Database className="w-5 h-5 text-[var(--fail)]" />
        </div>
        <span className="text-[9px] font-mono text-[var(--fail)] font-bold whitespace-nowrap">2 CAPTURES</span>
      </div>
      
      <div className="flex flex-col items-center gap-1 shrink-0 mx-2">
        <GitMerge className="w-5 h-5 text-[var(--text-muted)]" />
        <AlertTriangle className="w-3.5 h-3.5 text-[var(--fail)] mt-0.5" />
      </div>

      <div className="flex flex-col items-center gap-2 shrink-0">
        <div className="w-12 h-12 rounded-xl bg-[var(--pass)]/10 border border-[var(--pass)]/30 flex items-center justify-center">
          <Database className="w-5 h-5 text-[var(--pass)]" />
        </div>
        <span className="text-[9px] font-mono text-[var(--pass)] font-bold whitespace-nowrap">1 ORDER</span>
      </div>

    </div>
  </div>
);

export const FixDiagram = () => (
  <div className="flex items-center justify-end w-full h-full pr-2">
    <div className="w-[210px] rounded-xl border border-[var(--code-border)] bg-[var(--code-bg)] overflow-hidden shadow-lg shrink-0 scale-[0.75] lg:scale-[0.85] xl:scale-100 origin-right">
      
      <div className="bg-[var(--surface-sunken)] px-2.5 py-1.5 flex items-center gap-1.5 border-b border-[var(--code-border)]">
        <FileCode2 className="w-3.5 h-3.5 text-[var(--text-muted)]" />
        <span className="text-[10px] font-mono text-[var(--text-muted)]">checkout.ts</span>
      </div>
      
      <div className="p-2 text-[10px] font-mono flex flex-col whitespace-nowrap">
        <div className="text-[var(--text-dim)]">{"const order = {"}</div>
        <div className="text-[var(--fail)] bg-[var(--fail)]/10 px-1 border-l-2 border-[var(--fail)]">{"-  intent: 'CAPTURE',"}</div>
        <div className="text-[var(--pass)] bg-[var(--pass)]/10 px-1 border-l-2 border-[var(--pass)]">{"+  intent: 'CAPTURE',"}</div>
        <div className="text-[var(--pass)] bg-[var(--pass)]/10 px-1 border-l-2 border-[var(--pass)]">{"+  PayPal-Request-Id: id,"}</div>
        <div className="text-[var(--text-dim)]">{"};"}</div>
      </div>
      
      <div className="bg-[var(--pass)]/10 border-t border-[var(--pass)]/20 px-2.5 py-1.5 flex items-center justify-between">
        <span className="text-[9px] font-mono text-[var(--pass)] font-bold">Context Synced</span>
        <CheckCircle2 className="w-3.5 h-3.5 text-[var(--pass)]" />
      </div>

    </div>
  </div>
);