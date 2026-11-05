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
    <div className="w-full rounded-lg bg-[#0D0E15] border border-[#242838] overflow-hidden font-mono text-xs shadow-inner">
      {/* Header bar */}
      <div className="px-3.5 py-2 bg-[#161922] border-b border-[#242838] flex items-center justify-between text-[#94A3B8]">
        <div className="flex items-center gap-2">
          <FileCode className="w-3.5 h-3.5 text-[#06B6D4]" />
          <span className="font-semibold text-[11px] text-white tracking-wide">
            {title}
          </span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2 py-1 rounded bg-[#11131A] hover:bg-[#1E2230] text-[#94A3B8] hover:text-white border border-[#242838] transition cursor-pointer text-[10px]"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-emerald-400" />
              <span className="text-emerald-400">Copied</span>
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
          let lineStyle = "text-[#94A3B8]";
          let bgStyle = "";

          if (line.startsWith("+") && !line.startsWith("+++")) {
            lineStyle = "text-emerald-300 font-semibold";
            bgStyle = "bg-emerald-950/40 -mx-3 px-3";
          } else if (line.startsWith("-") && !line.startsWith("---")) {
            lineStyle = "text-rose-300 font-semibold line-through decoration-rose-500/50";
            bgStyle = "bg-rose-950/40 -mx-3 px-3";
          } else if (line.startsWith("@@")) {
            lineStyle = "text-cyan-400 font-medium";
            bgStyle = "bg-cyan-950/20 -mx-3 px-3";
          } else if (line.startsWith("---") || line.startsWith("+++")) {
            lineStyle = "text-[#64748B] font-bold";
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

