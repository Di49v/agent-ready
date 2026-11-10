"use client";

import React, { useState } from "react";
import {
  Copy,
  Check,
  Send,
} from "lucide-react";

export const PostmanSection: React.FC = () => {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const handleCopy = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const sampleProblemDetails = `{
  "type": "https://agentready.lab/errors/cart-intent-mismatch",
  "title": "Cart Intent Mismatch Detected",
  "status": 409,
  "code": "CART_INTENT_MISMATCH",
  "detail": "Submitted cart quantity (5) exceeds human-approved HMAC cart receipt (1 unit). Potential prompt injection detected.",
  "retryable": false,
  "next_action": "REAUTHORIZE_WITH_HUMAN_BUYER",
  "cart_id": "cart_prompt_trap_009",
  "expected_hash": "a8f3b9c2...",
  "submitted_hash": "e1d4c7f0..."
}`;

  const postmanCollectionSnippet = `{
  "info": {
    "name": "AgentReady Lab API (v1.0.0)",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    { "name": "1. Health & Vitality Check", "request": { "method": "GET", "url": "{{base_url}}/healthz" } },
    { "name": "2. List Personas", "request": { "method": "GET", "url": "{{base_url}}/v1/personas" } },
    { "name": "3. Register Target Store", "request": { "method": "POST", "url": "{{base_url}}/v1/targets" } },
    { "name": "4. Trigger Crash-Test Swarm", "request": { "method": "POST", "url": "{{base_url}}/v1/runs" } },
    { "name": "5. Fetch Dual-Ledger Findings", "request": { "method": "GET", "url": "{{base_url}}/v1/runs/{{run_id}}/findings" } },
    { "name": "6. Re-Run on Hardened Shop", "request": { "method": "POST", "url": "{{base_url}}/v1/runs/{{run_id}}/rerun" } },
    { "name": "7. Export Audit Report", "request": { "method": "GET", "url": "{{base_url}}/v1/runs/{{run_id}}/report" } }
  ]
}`;

  return (
    <section id="postman" className="py-20 border-t border-[var(--border)] bg-[var(--surface-sunken)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="flex flex-col items-center text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono bg-[var(--surface-sunken)] border border-[var(--border)] text-[var(--text-muted)] mb-3">
            <Send className="w-3.5 h-3.5" />
            <span>Developer API Hub</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-[var(--accent)]">
            Postman API Testing Hub
          </h2>
          <p className="mt-3 text-sm sm:text-base text-[var(--text-muted)] leading-relaxed">
            Test the entire AgentReady Lab API lifecycle without writing a single line of code. Includes pre-configured environment variables, test scripts, and RFC 9457 error contracts.
          </p>
        </div>

        {/* 2-Column Postman Showcase */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Collection Structure & Import Guide (Cols 6) */}
          <div className="lg:col-span-6 space-y-6">
            <div className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-6 shadow-none">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-mono uppercase tracking-wider text-[var(--text-muted)]">
                  Collection v2.1.0 Structure
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[var(--surface-sunken)] text-[var(--text-muted)] border border-[var(--border)]">
                  7 Standard Requests
                </span>
              </div>
              <h3 className="text-lg font-semibold font-heading text-[var(--text)] mb-3">
                Full-Lifecycle API Test Suite
              </h3>
              <p className="text-xs text-[var(--text-muted)] leading-relaxed mb-4">
                Our Postman collection automatically passes variables between calls. Triggering <code className="text-[var(--text-muted)] font-mono">POST /v1/runs</code> saves the generated <code className="text-[var(--text-muted)] font-mono">run_id</code> to the active environment, enabling instant downstream checks.
              </p>

              <div className="space-y-2 font-mono text-xs text-[var(--text)]">
                <div className="p-2.5 rounded-lg bg-[var(--surface-sunken)] border border-[var(--border)] flex items-center justify-between">
                  <span>GET /healthz</span>
                  <span className="text-[var(--pass)]">Vitality &amp; Sandbox Lock</span>
                </div>
                <div className="p-2.5 rounded-lg bg-[var(--surface-sunken)] border border-[var(--border)] flex items-center justify-between">
                  <span>POST /v1/runs</span>
                  <span className="text-[var(--text-muted)]">Dispatches Swarm (Seed: 42)</span>
                </div>
                <div className="p-2.5 rounded-lg bg-[var(--surface-sunken)] border border-[var(--border)] flex items-center justify-between">
                  <span>GET /v1/runs/:id/findings</span>
                  <span className="text-[var(--fail)]">Asserts Violations &amp; PayPal IDs</span>
                </div>
                <div className="p-2.5 rounded-lg bg-[var(--surface-sunken)] border border-[var(--border)] flex items-center justify-between">
                  <span>POST /v1/runs/:id/rerun</span>
                  <span className="text-[var(--pass)]">Asserts Hardened Score &gt;= 90</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="mt-6 pt-4 border-t border-[var(--border)] flex flex-wrap items-center gap-3">
                <button
                  onClick={() => handleCopy(postmanCollectionSnippet, "postman_json")}
                  className="inline-flex items-center gap-2 px-4 py-2 rounded-lg font-mono text-xs font-semibold bg-[var(--accent)] text-[var(--accent-foreground)] hover:bg-[var(--accent-hover)] shadow-none transition cursor-pointer"
                >
                  {copiedKey === "postman_json" ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-[var(--text)]" />
                      <span>Copied Collection JSON</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy Postman Collection</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Environment Variables Reference */}
            <div className="rounded-md border border-[var(--border)] bg-[var(--surface)] p-6 shadow-none">
              <h4 className="text-sm font-semibold font-heading text-[var(--text)] mb-2">
                Postman Environment Variables
              </h4>
              <div className="space-y-1.5 font-mono text-xs text-[var(--text-muted)]">
                <div>• <code className="text-[var(--text-muted)]">base_url</code>: http://localhost:8000 or Render URL</div>
                <div>• <code className="text-[var(--text-muted)]">api_key</code>: Optional X-Lab-Api-Key</div>
                <div>• <code className="text-[var(--text-muted)]">target_store</code>: naive-shop or hardened-shop</div>
                <div>• <code className="text-[var(--text-muted)]">run_id</code>: Auto-populated from POST /v1/runs</div>
              </div>
            </div>
          </div>

          {/* Right Column: RFC 9457 Problem Details Sample (Cols 6) */}
          <div className="lg:col-span-6 rounded-md border border-[var(--border)] bg-[var(--surface)] p-6 shadow-none">
            <div className="flex items-center justify-between mb-4">
              <div>
                <span className="text-xs font-mono uppercase tracking-wider text-[var(--text-muted)]">
                  RFC 9457 Response Spec
                </span>
                <h3 className="text-base font-semibold font-heading text-[var(--text)]">
                  Machine-Actionable Error Contract
                </h3>
              </div>
              <button
                onClick={() => handleCopy(sampleProblemDetails, "problem_details")}
                className="inline-flex items-center gap-1.5 text-xs font-mono text-[var(--text-muted)] hover:text-[var(--text)] transition cursor-pointer"
              >
                {copiedKey === "problem_details" ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-[var(--pass)]" />
                    <span className="text-[var(--pass)]">Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy JSON</span>
                  </>
                )}
              </button>
            </div>

            <p className="text-xs text-[var(--text-muted)] leading-relaxed mb-4">
              Every error payload returns Content-Type: <code className="text-[var(--text-muted)] font-mono">application/problem+json</code> with deterministic recovery recommendations for autonomous agents.
            </p>

            <pre className="p-4 rounded-md border border-[var(--code-border)] bg-[var(--code-bg)] text-xs font-mono text-[var(--code-text)] overflow-x-auto leading-relaxed">
              <code>{sampleProblemDetails}</code>
            </pre>
          </div>
        </div>
      </div>
    </section>
  );
};
