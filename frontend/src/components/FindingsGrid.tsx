"use client";

import React, { useMemo, useState } from "react";
import { AgGridReact } from "ag-grid-react";
import {
  AllCommunityModule,
  ColDef,
  ModuleRegistry,
  themeQuartz,
  colorSchemeDark,
  ValidationModule,
} from "ag-grid-community";
import {
  AlertTriangle,
  Database,
  ExternalLink,
  Layers,
  Sparkles,
} from "lucide-react";
import { FindingDetail, DualLedgerRow } from "@/lib/api";

// Register AG Grid Community modules
ModuleRegistry.registerModules([AllCommunityModule, ValidationModule]);

// AG Grid v36 Dark Quartz Theme
const darkGridTheme = themeQuartz.withPart(colorSchemeDark).withParams({
  backgroundColor: "#11131A",
  headerBackgroundColor: "#181B26",
  borderColor: "#242838",
  foregroundColor: "#F1F5F9",
  rowHoverColor: "#1E2230",
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
          let badgeColor = "bg-rose-950/80 border-rose-700/80 text-rose-300";
          if (sev === "HIGH")
            badgeColor = "bg-amber-950/80 border-amber-700/80 text-amber-300";
          else if (sev === "LOW")
            badgeColor = "bg-slate-900 border-slate-700 text-slate-300";

          return (
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider uppercase border ${badgeColor}`}
            >
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
            <span className="font-mono text-xs text-[#06B6D4]">
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
          <span className="font-medium text-white">{params.value}</span>
        ),
      },
      {
        field: "evidence_ids",
        headerName: "PayPal Evidence",
        width: 220,
        cellRenderer: (params: any) => {
          const ids: string[] = params.value || [];
          return (
            <div className="flex items-center gap-1 overflow-hidden">
              {ids.slice(0, 2).map((id, i) => (
                <span
                  key={i}
                  className="px-1.5 py-0.5 rounded bg-[#181B26] border border-[#242838] font-mono text-[10px] text-[#06B6D4] truncate"
                >
                  {id}
                </span>
              ))}
              {ids.length > 2 && (
                <span className="text-[10px] text-[#64748B]">
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
            className="flex items-center gap-1 px-2.5 py-1 rounded bg-[#181B26] hover:bg-[#242838] border border-[#33394D] text-[11px] font-medium text-[#06B6D4] hover:text-white transition cursor-pointer"
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
          <span className="font-mono text-xs text-[#94A3B8]">{p.value}</span>
        ),
      },
      {
        field: "persona_id",
        headerName: "Persona",
        width: 150,
        cellRenderer: (p: any) => (
          <span className="font-medium text-xs text-white capitalize">
            {p.value?.replace(/_/g, " ")}
          </span>
        ),
      },
      {
        field: "paypal_amount",
        headerName: "PayPal Capture",
        width: 140,
        cellRenderer: (p: any) => (
          <span className="font-mono font-bold text-xs text-emerald-400 tabular-nums">
            {p.value || "—"}
          </span>
        ),
      },
      {
        field: "store_amount",
        headerName: "Store Ledger",
        width: 140,
        cellRenderer: (p: any) => (
          <span className="font-mono font-bold text-xs text-[#F1F5F9] tabular-nums">
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
              className={`px-2 py-0.5 rounded text-[10px] font-mono border ${isError
                ? "bg-rose-950/60 border-rose-800/60 text-rose-300"
                : "bg-slate-900 border-slate-700 text-slate-300"
                }`}
            >
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
        cellRenderer: (p: any) => {
          const list: string[] = p.value || [];
          if (list.length === 0) {
            return (
              <span className="text-emerald-400 text-xs font-mono">
                ✓ Records In Agreement
              </span>
            );
          }
          return (
            <span className="text-rose-400 text-xs font-medium truncate">
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
            className="flex items-center gap-1 px-2.5 py-1 rounded bg-[#181B26] hover:bg-[#242838] border border-[#33394D] text-[11px] font-medium text-[#06B6D4] hover:text-white transition cursor-pointer"
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
    <section className="w-full bg-[#11131A] border border-[#242838] rounded-xl p-5 shadow-xl flex flex-col gap-4">
      {/* Table Navigation Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-[#242838]">
        <div className="flex items-center gap-2">
          {/* Findings Tab */}
          <button
            onClick={() => setActiveTab("findings")}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-bold transition font-mono cursor-pointer ${activeTab === "findings"
              ? "bg-[#181B26] text-[#06B6D4] border border-[#06B6D4]/50 shadow-md"
              : "text-[#94A3B8] hover:text-white hover:bg-[#181B26]/50"
              }`}
          >
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            <span>Invariant Violations</span>
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-rose-950/80 text-rose-300 border border-rose-800/80">
              {findings.length}
            </span>
          </button>

          {/* Dual Ledger Matrix Tab */}
          <button
            onClick={() => setActiveTab("dual_ledger")}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-bold transition font-mono cursor-pointer ${activeTab === "dual_ledger"
              ? "bg-[#181B26] text-[#06B6D4] border border-[#06B6D4]/50 shadow-md"
              : "text-[#94A3B8] hover:text-white hover:bg-[#181B26]/50"
              }`}
          >
            <Database className="w-4 h-4 text-[#06B6D4]" />
            <span>Dual-Ledger Matrix (9 Carts)</span>
            <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-slate-900 text-slate-300 border border-slate-700">
              {dualRows.length || 9}
            </span>
          </button>
        </div>

        <div className="text-xs font-mono text-[#64748B]">
          Powered by AG Grid Community • Quartz Dark
        </div>
      </div>

      {/* Grid Container */}
      <div className="w-full h-[360px] rounded-lg overflow-hidden border border-[#242838]">
        {activeTab === "findings" ? (
          <AgGridReact<FindingDetail>
            theme={darkGridTheme}
            rowData={findings}
            columnDefs={findingColDefs}
            onRowClicked={(e) => e.data && onSelectFinding(e.data)}
            pagination={false}
            rowHeight={46}
            headerHeight={40}
            suppressCellFocus={true}
          />
        ) : (
          <AgGridReact<DualLedgerRow>
            theme={darkGridTheme}
            rowData={dualRows}
            columnDefs={dualLedgerColDefs}
            onRowClicked={(e) => e.data && onSelectDualRow(e.data)}
            pagination={false}
            rowHeight={46}
            headerHeight={40}
            suppressCellFocus={true}
          />
        )}
      </div>
    </section>
  );
};

