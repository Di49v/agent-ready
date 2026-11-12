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
  AlertTriangle,
  Database,
  ExternalLink,
} from "lucide-react";
import { FindingDetail, DualLedgerRow } from "@/lib/api";

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

interface FindingsGridProps {
  findings: FindingDetail[];
  dualRows: DualLedgerRow[];
  onSelectFinding: (finding: FindingDetail) => void;
  onSelectDualRow: (row: DualLedgerRow) => void;
}

export const FindingsGrid: React.FC<FindingsGridProps> = ({
  findings,
  dualRows,
  onSelectFinding,
  onSelectDualRow,
}) => {
  const [activeTab, setActiveTab] = useState<"findings" | "dual_ledger">(
    "findings"
  );

  // Column definitions for Invariant Violations (Findings)
  const findingColDefs = useMemo<ColDef<FindingDetail>[]>(
    () => [
      {
        field: "severity",
        headerName: "Severity",
        width: 130,
        sort: "asc",
        comparator: (valA, valB) => {
          const ranks: Record<string, number> = {
            CRITICAL: 1,
            HIGH: 2,
            MEDIUM: 3,
            LOW: 4,
          };
          return (ranks[valA] || 99) - (ranks[valB] || 99);
        },
        cellRenderer: (params: any) => {
          const sev = params.value;
          let badgeColor = "bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--text-muted)]";
          if (sev === "HIGH")
            badgeColor = "bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--text-muted)]";
          else if (sev === "LOW")
            badgeColor = "bg-[var(--surface-sunken)] border-[var(--border-strong)] text-[var(--text)]";

          return (
            <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase border ${badgeColor}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${sev === "LOW" ? "bg-[var(--text-dim)]" : sev === "HIGH" ? "bg-[var(--warn)]" : "bg-[var(--fail)]"}`} />
              {sev}
            </span>
          );
        },
      },
      {
        field: "rule_number",
        headerName: "Rule Violated",
        width: 170,
        cellRenderer: (params: any) => {
          return (
            <span className="font-mono text-xs text-[var(--text-muted)]">
              Rule {params.value}: {params.data?.rule_name}
            </span>
          );
        },
      },
      {
        field: "title",
        headerName: "Finding Headline",
        flex: 1,
        minWidth: 260,
        cellRenderer: (params: any) => (
          <span className="font-medium text-[var(--text)]">{params.value}</span>
        ),
      },
      {
        field: "evidence_ids",
        headerName: "PayPal Evidence",
        width: 220,
        cellDataType: false,
        valueFormatter: (params) =>
          params.value && Array.isArray(params.value)
            ? params.value.join(", ")
            : params.value || "",
        cellRenderer: (params: any) => {
          const ids: string[] = params.value || [];
          return (
            <div className="flex items-center gap-1 overflow-hidden">
              {ids.slice(0, 2).map((id, i) => (
                <span
                  key={i}
                  className="px-1.5 py-0.5 rounded bg-[var(--surface-sunken)] border border-[var(--border)] font-mono text-[10px] text-[var(--text-muted)] truncate"
                >
                  {id}
                </span>
              ))}
              {ids.length > 2 && (
                <span className="text-[10px] text-[var(--text-dim)]">
                  +{ids.length - 2}
                </span>
              )}
            </div>
          );
        },
      },
      {
        headerName: "Action",
        width: 130,
        cellRenderer: (params: any) => (
          <button
            onClick={() => onSelectFinding(params.data)}
            className="flex items-center gap-1 px-2.5 py-1 rounded bg-[var(--surface-sunken)] hover:bg-[var(--surface-hover)] border border-[var(--border-strong)] text-[11px] font-medium text-[var(--text-muted)] hover:text-[var(--text)] transition cursor-pointer"
          >
            <span>Inspect</span>
            <ExternalLink className="w-3 h-3" />
          </button>
        ),
      },
    ],
    [onSelectFinding]
  );

  // Column definitions for Dual-Ledger Matrix
  const dualLedgerColDefs = useMemo<ColDef<DualLedgerRow>[]>(
    () => [
      {
        field: "cart_id",
        headerName: "Cart Join Key",
        width: 170,
        cellRenderer: (p: any) => (
          <span className="font-mono text-xs text-[var(--text-muted)]">{p.value}</span>
        ),
      },
      {
        field: "persona_id",
        headerName: "Persona",
        width: 150,
        cellRenderer: (p: any) => (
          <span className="font-medium text-xs text-[var(--text)] capitalize">
            {p.value?.replace(/_/g, " ")}
          </span>
        ),
      },
      {
        field: "paypal_amount",
        headerName: "PayPal Capture",
        width: 140,
        cellRenderer: (p: any) => (
          <span className="font-mono font-bold text-xs text-[var(--ledger-paypal)] tabular-nums">
            {p.value || "—"}
          </span>
        ),
      },
      {
        field: "store_amount",
        headerName: "Store Ledger",
        width: 140,
        cellRenderer: (p: any) => (
          <span className="font-mono font-bold text-xs text-[var(--ledger-store)] tabular-nums">
            {p.value || "—"}
          </span>
        ),
      },
      {
        field: "store_status",
        headerName: "Store Status",
        width: 160,
        cellRenderer: (p: any) => {
          const status = p.value;
          const isError =
            status?.includes("409") ||
            status?.includes("422") ||
            status?.includes("CRASH");
          return (
            <span
              className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono border ${isError
                ? "bg-[var(--surface-sunken)] border-[var(--border)] text-[var(--text-muted)]"
                : "bg-[var(--surface-sunken)] border-[var(--border-strong)] text-[var(--text)]"
                }`}
            >
              {status && <span className={`h-1.5 w-1.5 rounded-full ${isError ? "bg-[var(--fail)]" : "bg-[var(--pass)]"}`} />}
              {status || "UNKNOWN"}
            </span>
          );
        },
      },
      {
        field: "disagreements",
        headerName: "Ledger Discrepancy",
        flex: 1,
        minWidth: 260,
        cellDataType: false,
        valueFormatter: (p) =>
          p.value && Array.isArray(p.value)
            ? p.value.join(", ")
            : p.value || "",
        cellRenderer: (p: any) => {
          const list: string[] = p.value || [];
          if (list.length === 0) {
            return (
              <span className="text-[var(--pass)] text-xs font-mono">
                ✓ Records In Agreement
              </span>
            );
          }
          return (
            <span className="text-[var(--fail)] text-xs font-medium truncate">
              {list[0]}
            </span>
          );
        },
      },
      {
        headerName: "Action",
        width: 120,
        cellRenderer: (p: any) => (
          <button
            onClick={() => onSelectDualRow(p.data)}
            className="flex items-center gap-1 px-2.5 py-1 rounded bg-[var(--surface-sunken)] hover:bg-[var(--surface-hover)] border border-[var(--border-strong)] text-[11px] font-medium text-[var(--text-muted)] hover:text-[var(--text)] transition cursor-pointer"
          >
            <span>Diff</span>
            <ExternalLink className="w-3 h-3" />
          </button>
        ),
      },
    ],
    [onSelectDualRow]
  );

  return (
    <section className="w-full bg-[var(--surface)] border border-[var(--border)] rounded-md p-5 shadow-none flex flex-col gap-4">
      {/* Table Navigation Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-[var(--border)]">
        <div className="flex items-center gap-2">
          {/* Findings Tab */}
          <button
            onClick={() => setActiveTab("findings")}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-bold transition font-mono cursor-pointer ${activeTab === "findings"
              ? "bg-[var(--surface-sunken)] text-[var(--accent)] border border-[var(--accent)]/50 shadow-none"
              : "text-[var(--text-muted)] hover:text-[var(--text)] hover:bg-[var(--surface-hover)]"
              }`}
          >
            <AlertTriangle className="w-4 h-4 text-[var(--fail)]" />
            <span>Invariant Violations</span>
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-[var(--surface-sunken)] text-[var(--text-muted)] border border-[var(--border)]">
              {findings.length}
            </span>
          </button>

          {/* Dual Ledger Matrix Tab */}
          <button
            onClick={() => setActiveTab("dual_ledger")}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-bold transition font-mono cursor-pointer ${activeTab === "dual_ledger"
              ? "bg-[var(--surface-sunken)] text-[var(--accent)] border border-[var(--accent)]/50 shadow-none"
              : "text-[var(--text-muted)] hover:text-[var(--text)] hover:bg-[var(--surface-hover)]"
              }`}
          >
            <Database className="w-4 h-4 text-[var(--accent)]" />
            <span>Dual-Ledger Matrix (9 Carts)</span>
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-[var(--surface-sunken)] text-[var(--text-muted)] border border-[var(--border)]">
              {dualRows.length || 9}
            </span>
          </button>
        </div>

        <div className="text-xs font-mono text-[var(--text-dim)]">
          Powered by AG Grid Community • Quartz Dark
        </div>
      </div>

      {/* Grid Container */}
      <div
        className="w-full h-[360px] rounded-lg overflow-hidden border border-[var(--border)] bg-[var(--surface)]"
        style={{ width: "100%", height: "360px" }}
      >
        {activeTab === "findings" ? (
          <AgGridReact<FindingDetail>
            theme={gridTheme}
            rowData={findings}
            columnDefs={findingColDefs}
            onRowClicked={(e) => e.data && onSelectFinding(e.data)}
            pagination={false}
            rowHeight={46}
            headerHeight={40}
            domLayout="normal"
            suppressCellFocus={true}
          />
        ) : (
          <AgGridReact<DualLedgerRow>
            theme={gridTheme}
            rowData={dualRows}
            columnDefs={dualLedgerColDefs}
            onRowClicked={(e) => e.data && onSelectDualRow(e.data)}
            pagination={false}
            rowHeight={46}
            headerHeight={40}
            domLayout="normal"
            suppressCellFocus={true}
          />
        )}
      </div>
    </section>
  );
};
