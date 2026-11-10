"use client";

import React, { useState } from "react";
import { Copy, Check, FileCode } from "lucide-react";

interface PatchViewerProps {
  patchDiff: string;
  title?: string;
}

export const PatchViewer: React.FC<PatchViewerProps> = ({
  patchDiff,
  title = "Remediation Git Patch (Unified Diff)",
}) => {
  const [copied, setCopied] = useState<boolean>(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(patchDiff);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = patchDiff.trim().split("\n");

  return (
    <div className="w-full rounded-lg bg-[var(--surface)] border border-[var(--border)] overflow-hidden font-mono text-xs shadow-none">
      {/* Header bar */}
      <div className="px-3.5 py-2 bg-[var(--surface-sunken)] border-b border-[var(--border)] flex items-center justify-between text-[var(--text-muted)]">
        <div className="flex items-center gap-2">
          <FileCode className="w-3.5 h-3.5 text-[var(--text-muted)]" />
          <span className="font-semibold text-[11px] text-[var(--text)] tracking-wide">
            {title}
          </span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2 py-1 rounded bg-[var(--surface)] hover:bg-[var(--surface-hover)] text-[var(--text-muted)] hover:text-[var(--text)] border border-[var(--border)] transition cursor-pointer text-[10px]"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-[var(--pass)]" />
              <span className="text-[var(--pass)]">Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              <span>Copy Patch</span>
            </>
          )}
        </button>
      </div>

      {/* Code diff lines */}
      <div className="p-3 overflow-x-auto max-h-64 leading-5">
        {lines.map((line, idx) => {
          let lineStyle = "text-[var(--text-muted)]";
          let bgStyle = "";

          if (line.startsWith("+") && !line.startsWith("+++")) {
            lineStyle = "text-[var(--code-text)] font-semibold";
            bgStyle = "diff-line-add -mx-3 px-3";
          } else if (line.startsWith("-") && !line.startsWith("---")) {
            lineStyle = "text-[var(--text-dim)]";
            bgStyle = "diff-line-del -mx-3 px-3";
          } else if (line.startsWith("@@")) {
            lineStyle = "text-[var(--text-muted)] font-medium";
          } else if (line.startsWith("---") || line.startsWith("+++")) {
            lineStyle = "text-[var(--text-dim)] font-bold";
          }

          return (
            <div key={idx} className={`whitespace-pre ${bgStyle} ${lineStyle}`}>
              {line || " "}
            </div>
          );
        })}
      </div>
    </div>
  );
};
