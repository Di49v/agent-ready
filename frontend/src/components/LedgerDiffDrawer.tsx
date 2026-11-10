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
    <div className="fixed inset-0 z-50 overflow-hidden bg-[var(--bg)]/80 backdrop-blur-sm flex justify-end transition-opacity animate-in fade-in">
      {/* Slide-over panel */}
      <div className="audit-drawer-enter w-full max-w-3xl bg-[var(--surface)] border-l border-[var(--border)] h-full flex flex-col shadow-none overflow-y-auto">
        {/* Drawer Header */}
        <div className="p-5 border-b border-[var(--border)] bg-[var(--surface-sunken)] sticky top-0 z-10 flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span
                className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase border ${severity === "CRITICAL"
                  ? "bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--text-muted)]"
                    : severity === "HIGH"
                    ? "bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--text-muted)]"
                    : "bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--text-muted)]"
                  }`}
              >
                <span className={`h-1.5 w-1.5 rounded-full ${severity === "CRITICAL" ? "bg-[var(--fail)]" : severity === "HIGH" ? "bg-[var(--warn)]" : "bg-[var(--text-dim)]"}`} />
                {severity}
              </span>
              <span className="text-xs font-mono text-[var(--text-muted)]">
                Rule {ruleNumber}: {ruleName}
              </span>
            </div>
            <h2 className="text-lg font-bold text-[var(--accent)] tracking-tight">
              {title}
            </h2>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-md hover:bg-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text)] transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Body */}
        <div className="p-6 flex-1 flex flex-col gap-6">
          {/* Mismatch Alert Callout */}
          <div className="p-4 rounded-lg bg-[var(--surface-sunken)] border border-[var(--border)] flex items-start gap-3">
            <AlertOctagon className="w-5 h-5 text-[var(--fail)] flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-bold font-mono uppercase text-[var(--fail)] tracking-wide">
                Dual-Ledger Discrepancy Detected by Reconciler
              </h4>
              <p className="text-xs text-[var(--text)] mt-1 leading-relaxed">
                {explanation}
              </p>
            </div>
          </div>

          {/* Evidence IDs Pill Bar */}
          {finding?.evidence_ids && finding.evidence_ids.length > 0 && (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-mono text-[var(--text-dim)]">PayPal Evidence:</span>
              {finding.evidence_ids.map((id, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded bg-[var(--surface-sunken)] border border-[var(--border)] font-mono text-[11px] text-[var(--text-muted)] flex items-center gap-1"
                >
                  {id}
                </span>
              ))}
            </div>
          )}

          {/* Side-by-Side Dual-Ledger Inspector */}
          <div className="flex flex-col gap-2">
            <h3 className="text-xs font-bold font-mono uppercase text-[var(--text-muted)] tracking-wider flex items-center gap-2">
              <Database className="w-3.5 h-3.5 text-[var(--text-muted)]" />
              Side-by-Side Dual Ledger Records
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {/* Left: PayPal Ground Truth */}
              <div className="rounded-lg bg-[var(--surface)] border border-[var(--border)] p-4 flex flex-col">
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-[var(--border)]">
                  <span className="flex items-center gap-1.5 font-mono text-xs font-bold text-[var(--ledger-paypal)]">
                    <CreditCard className="w-3.5 h-3.5" />
                    PayPal Ground Truth (Sandbox)
                  </span>
                  <span className="inline-flex items-center gap-1.5 text-[10px] font-mono text-[var(--text-muted)] bg-[var(--surface-sunken)] px-1.5 py-0.5 rounded border border-[var(--border)]">
                    <span className="h-1.5 w-1.5 rounded-full bg-[var(--pass)]" />
                    AUTHORITATIVE
                  </span>
                </div>
                <pre className="font-mono text-[11px] text-[var(--text-muted)] overflow-x-auto leading-relaxed whitespace-pre-wrap">
                  {JSON.stringify(paypalRecord, null, 2)}
                </pre>
              </div>

              {/* Right: Store Internal Ledger */}
              <div className="rounded-lg bg-[var(--surface)] border border-[var(--border)] p-4 flex flex-col">
                <div className="flex items-center justify-between pb-2 mb-2 border-b border-[var(--border)]">
                  <span className="flex items-center gap-1.5 font-mono text-xs font-bold text-[var(--ledger-store)]">
                    <Database className="w-3.5 h-3.5" />
                    Store Internal Ledger (Probe)
                  </span>
                  <span className="inline-flex items-center gap-1.5 text-[10px] font-mono text-[var(--text-muted)] bg-[var(--surface-sunken)] px-1.5 py-0.5 rounded border border-[var(--border)]">
                    <span className="h-1.5 w-1.5 rounded-full bg-[var(--fail)]" />
                    DISCREPANT
                  </span>
                </div>
                <pre className="font-mono text-[11px] text-[var(--text-muted)] overflow-x-auto leading-relaxed whitespace-pre-wrap">
                  {JSON.stringify(storeRecord, null, 2)}
                </pre>
              </div>
            </div>
          </div>

          {/* Remediation Patch Diff */}
          {patchDiff && (
            <div className="flex flex-col gap-2">
              <h3 className="text-xs font-bold font-mono uppercase text-[var(--text-muted)] tracking-wider flex items-center gap-2">
                <FileDiff className="w-3.5 h-3.5 text-[var(--pass)]" />
                Root Cause Remediation (10-Line Fix)
              </h3>
              <PatchViewer patchDiff={patchDiff} />
            </div>
          )}
        </div>

        {/* Drawer Action Footer */}
        <div className="p-5 border-t border-[var(--border)] bg-[var(--surface-sunken)] sticky bottom-0 z-10 flex items-center justify-between gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-md bg-[var(--surface-sunken)] hover:bg-[var(--border)] border border-[var(--border)] text-sm text-[var(--text-muted)] hover:text-[var(--text)] transition cursor-pointer"
          >
            Close
          </button>

          <button
            onClick={onApplyPatchAndRerun}
            disabled={isRerunning}
            className="flex items-center gap-2 px-5 py-2.5 rounded-md font-semibold text-sm bg-[var(--surface)] hover:bg-[var(--surface-hover)] text-[var(--text)] border border-[var(--border-strong)] shadow-none transition cursor-pointer disabled:opacity-50"
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
