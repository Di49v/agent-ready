"use client";

import React from "react";
import {
  X,
  ShieldCheck,
  AlertOctagon,
  ArrowRight,
  Database,
  CreditCard,
  FileDiff,
  RefreshCw,
  Copy,
} from "lucide-react";
import { FindingDetail, DualLedgerRow } from "@/lib/api";
import { PatchViewer } from "./PatchViewer";

interface LedgerDiffDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  finding: FindingDetail | null;
  dualRow: DualLedgerRow | null;
  onApplyPatchAndRerun: () => void;
  isRerunning: boolean;
}

export const LedgerDiffDrawer: React.FC<LedgerDiffDrawerProps> = ({
  isOpen,
  onClose,
  finding,
  dualRow,
  onApplyPatchAndRerun,
  isRerunning,
}) => {
  if (!isOpen || (!finding && !dualRow)) return null;

  const title = finding?.title || `Ledger Discrepancy — ${dualRow?.cart_id}`;
  const ruleName = finding?.rule_name || "Rule Violation";
  const ruleNumber = finding?.rule_number || 1;
  const severity = finding?.severity || "CRITICAL";
  const explanation = finding?.explanation || dualRow?.disagreements?.join(". ");
  const patchDiff = finding?.patch_diff;

  const paypalRecord = finding?.paypal_record || {
    order_id: dualRow?.paypal_order_id,
    capture_id: dualRow?.paypal_capture_id,
    status: dualRow?.paypal_status,
    amount: dualRow?.paypal_amount,
  };

  const storeRecord = finding?.store_record || {
    order_id: dualRow?.store_order_id,
    status: dualRow?.store_status,
    amount: dualRow?.store_amount,
    dispute_id: dualRow?.dispute_id,
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end transition-opacity animate-in fade-in">
      {/* Slide-over panel */}
      <div className="w-full max-w-3xl bg-[#11131A] border-l border-[#242838] h-full flex flex-col shadow-2xl overflow-y-auto">
        {/* Drawer Header */}
        <div className="p-5 border-b border-[#242838] bg-[#161922] sticky top-0 z-10 flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase border ${
                  severity === "CRITICAL"
                    ? "bg-rose-950/80 border-rose-700/80 text-rose-300"
                    : severity === "HIGH"
                    ? "bg-amber-950/80 border-amber-700/80 text-amber-300"
                    : "bg-slate-900 border-slate-700 text-slate-300"
                }`}
              >
                {severity}
              </span>
              <span className="text-xs font-mono text-[#94A3B8]">
                Rule {ruleNumber}: {ruleName}
              </span>
            </div>
            <h2 className="text-lg font-bold text-white tracking-tight">
              {title}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-md hover:bg-[#242838] text-[#94A3B8] hover:text-white transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Body */}
        <div className="p-6 flex-1 flex flex-col gap-6">
          {/* Mismatch Alert Callout */}
          <div className="p-4 rounded-lg bg-rose-950/30 border border-rose-800/60 flex items-start gap-3">
            <AlertOctagon className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-bold font-mono uppercase text-rose-300 tracking-wide">
                Dual-Ledger Discrepancy Detected by Reconciler
              </h4>
              <p className="text-xs text-[#E2E8F0] mt-1 leading-relaxed">
                {explanation}
              </p>
            </div>
          </div>

          {/* Evidence IDs Pill Bar */}
          {finding?.evidence_ids && finding.evidence_ids.length > 0 && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-mono text-[#64748B]">PayPal Evidence:</span>
              {finding.evidence_ids.map((id, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded bg-[#181B26] border border-[#242838] font-mono text-[11px] text-[#06B6D4] flex items-center gap-1"
                >
                  {id}
                </span>
              ))}
            </div>
          )}

          {/* Side-by-Side Dual-Ledger Inspector */}
          <div className="flex flex-col gap-2">
            <h3 className="text-xs font-bold font-mono uppercase text-[#94A3B8] tracking-wider flex items-center gap-2">
              <Database className="w-3.5 h-3.5 text-[#06B6D4]" />
              Side-by-Side Dual Ledger Records
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {/* Left: PayPal Ground Truth */}
              <div className="rounded-lg bg-[#0E1017] border border-[#242838] p-4 flex flex-col">
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#242838]">
                  <span className="flex items-center gap-1.5 font-mono text-xs font-bold text-[#06B6D4]">
                    <CreditCard className="w-3.5 h-3.5" />
                    PayPal Ground Truth (Sandbox)
                  </span>
                  <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-800/60">
                    AUTHORITATIVE
                  </span>
                </div>
                <pre className="font-mono text-[11px] text-[#94A3B8] overflow-x-auto leading-relaxed whitespace-pre-wrap">
                  {JSON.stringify(paypalRecord, null, 2)}
                </pre>
              </div>

              {/* Right: Store Internal Ledger */}
              <div className="rounded-lg bg-[#0E1017] border border-[#242838] p-4 flex flex-col">
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-[#242838]">
                  <span className="flex items-center gap-1.5 font-mono text-xs font-bold text-[#F59E0B]">
                    <Database className="w-3.5 h-3.5" />
                    Store Internal Ledger (Probe)
                  </span>
                  <span className="text-[10px] font-mono text-rose-400 bg-rose-950/60 px-1.5 py-0.5 rounded border border-rose-800/60">
                    DISCREPANT
                  </span>
                </div>
                <pre className="font-mono text-[11px] text-[#94A3B8] overflow-x-auto leading-relaxed whitespace-pre-wrap">
                  {JSON.stringify(storeRecord, null, 2)}
                </pre>
              </div>
            </div>
          </div>

          {/* Remediation Patch Diff */}
          {patchDiff && (
            <div className="flex flex-col gap-2">
              <h3 className="text-xs font-bold font-mono uppercase text-[#94A3B8] tracking-wider flex items-center gap-2">
                <FileDiff className="w-3.5 h-3.5 text-emerald-400" />
                Root Cause Remediation (10-Line Fix)
              </h3>
              <PatchViewer patchDiff={patchDiff} />
            </div>
          )}
        </div>

        {/* Drawer Action Footer */}
        <div className="p-5 border-t border-[#242838] bg-[#161922] sticky bottom-0 z-10 flex items-center justify-between gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-md bg-[#181B26] hover:bg-[#242838] border border-[#242838] text-sm text-[#94A3B8] hover:text-white transition cursor-pointer"
          >
            Close
          </button>

          <button
            onClick={onApplyPatchAndRerun}
            disabled={isRerunning}
            className="flex items-center gap-2 px-5 py-2.5 rounded-md font-semibold text-sm bg-gradient-to-r from-emerald-600 to-teal-500 hover:brightness-110 text-white shadow-lg shadow-emerald-950/60 transition cursor-pointer disabled:opacity-50"
          >
            {isRerunning ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Re-running Hardened Shop...</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-4 h-4" />
                <span>Apply Patch &amp; Re-Run on Hardened Shop</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
