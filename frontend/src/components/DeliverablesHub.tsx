"use client";

import React, { useState } from "react";
import {
  Check,
  Code2,
  Copy,
  Download,
  ExternalLink,
  FileCheck,
  FileCode,
  Layers,
  Package,
  ShieldCheck,
  Sparkles,
  Terminal,
} from "lucide-react";
import { API_BASE_URL } from "@/lib/api";

export const DeliverablesHub: React.FC = () => {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const mcpConfigJson = JSON.stringify(
    {
      mcpServers: {
        "agent-ready": {
          command: "node",
          args: ["d:/agent-ready/mcp/dist/server.js"],
          env: {
            AGENTREADY_API_URL: "http://localhost:8000",
            LAB_API_KEY: "judge_demo_public_key_2026",
          },
        },
      },
    },
    null,
    2
  );

  const sdkCodeSnippet = `import { AgentReadyClient } from "@agent-ready/sdk";

const client = new AgentReadyClient({
  baseUrl: "http://localhost:8000",
  apiKey: "judge_demo_public_key_2026",
});

// Run adversarial crash-test swarm
const run = await client.createRun({
  target: "naive-shop",
  pack: "full",
  seed: 42,
});
console.log(\`Run: \${run.id} | Score: \${run.score}/100\`);

// Inspect PayPal Sandbox evidence IDs
const findings = await client.getRunFindings(run.id);
findings.forEach((f) => console.log(\`[\${f.severity}] \${f.title} -> \${f.evidence_ids.join(", ")}\`));

// Re-run same seed on Hardened Shop (Red to Green transition)
const rerun = await client.rerunRun(run.id, { target_override: "hardened-shop" });
console.log(\`Remediated Score: \${rerun.score}/100 🟢\`);`;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-[#0D0F14] border border-white/[0.07] rounded-lg p-5">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="h-2 w-2 rounded-full bg-cyan-400" />
          <h2 className="text-lg font-medium text-white tracking-[-0.02em] flex items-center gap-2">
            Platform Deliverables &amp; Sponsor Hub <span className="text-zinc-500 font-mono text-xs uppercase px-2 py-0.5 rounded bg-white/5 border border-white/10">Stage 6</span>
          </h2>
        </div>
        <p className="text-zinc-400 text-sm max-w-2xl leading-relaxed">
          AgentReady Lab is built API-first. Every crash-test run, dual-ledger comparison, and grounded APIMatic patch is exposed through clean OpenAPI 3.1 endpoints, a Model Context Protocol (MCP) server, and dynamic vector safety score badges.
        </p>
      </div>

      {/* Grid: SVG Badges & MCP Config */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-px bg-white/[0.07] border border-white/[0.07] rounded-lg overflow-hidden">
        {/* Dynamic SVG Safety Score Badges */}
        <div className="bg-[#0D0F14] p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <h3 className="text-sm font-medium text-white">Dynamic SVG Safety Score Badges</h3>
            </div>
            <span className="text-zinc-500 font-mono text-[10px] uppercase">GET /v1/badge/&#123;target&#125;.svg</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed">
            Vector safety score badge generated dynamically based on reconciler audit results. Live README badge for e-commerce stores:
          </p>

          {/* Badge Previews */}
          <div className="grid grid-cols-2 gap-3 pt-1">
            <div className="p-3 rounded bg-[#13161F] border border-white/[0.07] space-y-2">
              <span className="text-[10px] font-mono text-zinc-500 uppercase block">Hardened Shop (Guarded)</span>
              <div className="inline-flex rounded overflow-hidden text-xs font-mono font-bold shadow-sm">
                <span className="bg-[#1E293B] text-white px-2.5 py-1 border-r border-black/30">agent-ready</span>
                <span className="bg-[#10B981] text-black px-2.5 py-1 font-bold">95 / 100</span>
              </div>
            </div>

            <div className="p-3 rounded bg-[#13161F] border border-white/[0.07] space-y-2">
              <span className="text-[10px] font-mono text-zinc-500 uppercase block">Naive Shop (Vulnerable)</span>
              <div className="inline-flex rounded overflow-hidden text-xs font-mono font-bold shadow-sm">
                <span className="bg-[#1E293B] text-white px-2.5 py-1 border-r border-black/30">agent-ready</span>
                <span className="bg-[#F43F5E] text-white px-2.5 py-1 font-bold">18 / 100</span>
              </div>
            </div>
          </div>

          {/* Markdown Snippet Copy */}
          <div className="space-y-1.5 pt-2">
            <div className="flex items-center justify-between text-[11px] font-mono text-zinc-400">
              <span>Markdown Embed Code:</span>
              <button
                onClick={() =>
                  copyToClipboard(
                    `[![AgentReady Score](${API_BASE_URL}/v1/badge/hardened-shop.svg)](${API_BASE_URL}/v1/runs/latest/report)`,
                    "badge"
                  )
                }
                className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer"
              >
                {copiedKey === "badge" ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                <span>{copiedKey === "badge" ? "Copied" : "Copy"}</span>
              </button>
            </div>
            <pre className="p-2.5 rounded bg-[#08090C] border border-white/[0.07] text-[11px] font-mono text-zinc-300 overflow-x-auto">
              {`[![AgentReady Score](${API_BASE_URL}/v1/badge/hardened-shop.svg)](${API_BASE_URL}/v1/runs/latest/report)`}
            </pre>
          </div>
        </div>

        {/* Model Context Protocol (MCP) Server */}
        <div className="bg-[#0D0F14] p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Terminal className="h-4 w-4 text-cyan-400" />
              <h3 className="text-sm font-medium text-white">Model Context Protocol (MCP) Server</h3>
            </div>
            <span className="text-zinc-500 font-mono text-[10px] uppercase">Section B3.10</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed">
            Exposes 5 tools directly to <strong>Google Antigravity IDE</strong> (<code className="text-zinc-300">Open MCP Config</code>) and <strong>Claude Desktop</strong> for the 10-second demo video clip:
          </p>

          {/* Tools List */}
          <div className="flex flex-wrap gap-1.5 font-mono text-[11px]">
            <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-cyan-300">start_crash_test</span>
            <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-cyan-300">list_findings</span>
            <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-cyan-300">explain_finding</span>
            <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-cyan-300">suggest_fix</span>
            <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-cyan-300">rerun</span>
          </div>

          {/* MCP JSON Snippet */}
          <div className="space-y-1.5 pt-1">
            <div className="flex items-center justify-between text-[11px] font-mono text-zinc-400">
              <span>IDE Config (Antigravity / Claude Desktop):</span>
              <button
                onClick={() => copyToClipboard(mcpConfigJson, "mcp")}
                className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer"
              >
                {copiedKey === "mcp" ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                <span>{copiedKey === "mcp" ? "Copied" : "Copy"}</span>
              </button>
            </div>
            <pre className="p-2.5 rounded bg-[#08090C] border border-white/[0.07] text-[10px] font-mono text-zinc-300 overflow-x-auto max-h-[140px]">
              {mcpConfigJson}
            </pre>
          </div>
        </div>
      </div>

      {/* Grid: APIMatic SDK & OpenAPI Exporter */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-px bg-white/[0.07] border border-white/[0.07] rounded-lg overflow-hidden">
        {/* APIMatic Generated TypeScript SDK */}
        <div className="bg-[#0D0F14] p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Package className="h-4 w-4 text-purple-400" />
              <h3 className="text-sm font-medium text-white">APIMatic Typed TypeScript SDK</h3>
            </div>
            <span className="text-zinc-500 font-mono text-[10px] uppercase">@agent-ready/sdk</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed">
            Generated directly from <code className="text-zinc-300">openapi.json</code> using APIMatic conventions. Includes RFC 9457 error translation and typed models:
          </p>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px] font-mono text-zinc-400">
              <span>SDK Usage Sample:</span>
              <button
                onClick={() => copyToClipboard(sdkCodeSnippet, "sdk")}
                className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 cursor-pointer"
              >
                {copiedKey === "sdk" ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                <span>{copiedKey === "sdk" ? "Copied" : "Copy"}</span>
              </button>
            </div>
            <pre className="p-2.5 rounded bg-[#08090C] border border-white/[0.07] text-[10px] font-mono text-zinc-300 overflow-x-auto max-h-[160px]">
              {sdkCodeSnippet}
            </pre>
          </div>
        </div>

        {/* Audit Report & Specification Links */}
        <div className="bg-[#0D0F14] p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileCheck className="h-4 w-4 text-amber-400" />
              <h3 className="text-sm font-medium text-white">Audit Reports &amp; OpenAPI Spec</h3>
            </div>
            <span className="text-zinc-500 font-mono text-[10px] uppercase">REST API /v1</span>
          </div>
          <p className="text-xs text-zinc-400 leading-relaxed">
            Download full audit reports with PayPal Sandbox transaction IDs as ground-truth evidence:
          </p>

          <div className="space-y-2 pt-1">
            <a
              href={`${API_BASE_URL}/openapi.json`}
              target="_blank"
              rel="noreferrer"
              className="p-3 rounded bg-[#13161F] border border-white/[0.07] hover:border-cyan-400/40 flex items-center justify-between text-xs font-mono text-zinc-300 hover:text-white transition group"
            >
              <div className="flex items-center gap-2.5">
                <FileCode className="h-4 w-4 text-cyan-400" />
                <div>
                  <div className="font-semibold text-white">OpenAPI 3.1 Specification</div>
                  <div className="text-[10px] text-zinc-500">Ready for APIMatic Studio &amp; Postman</div>
                </div>
              </div>
              <ExternalLink className="h-3.5 w-3.5 text-zinc-500 group-hover:text-cyan-400 transition" />
            </a>

            <a
              href={`${API_BASE_URL}/docs`}
              target="_blank"
              rel="noreferrer"
              className="p-3 rounded bg-[#13161F] border border-white/[0.07] hover:border-cyan-400/40 flex items-center justify-between text-xs font-mono text-zinc-300 hover:text-white transition group"
            >
              <div className="flex items-center gap-2.5">
                <Code2 className="h-4 w-4 text-purple-400" />
                <div>
                  <div className="font-semibold text-white">Interactive Swagger API Docs</div>
                  <div className="text-[10px] text-zinc-500">FastAPI interactive documentation</div>
                </div>
              </div>
              <ExternalLink className="h-3.5 w-3.5 text-zinc-500 group-hover:text-purple-400 transition" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

