"use client";

import React from "react";
import Link from "next/link";
import { PLAYGROUND_URL, GITHUB_REPO_URL } from "@/lib/constants";
import {
  ShieldAlert,
  Zap,
  ArrowRight,
  ExternalLink,
} from "lucide-react";

const GithubIcon: React.FC<{ className?: string }> = ({ className = "w-4 h-4" }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
  </svg>
);

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-[var(--border)] bg-[var(--bg)] text-[var(--text-muted)] text-xs font-mono">
      {/* High-Impact Closing CTA Banner (Requirement J) */}
      <div className="border-b border-[var(--border)] bg-[var(--surface-sunken)] py-16 sm:py-20">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center flex flex-col items-center">
          <div className="w-12 h-12 rounded-md bg-[var(--accent)] flex items-center justify-center text-[var(--accent-foreground)] shadow-none  mb-6">
            <Zap className="w-6 h-6 fill-current" />
          </div>

          <h2 className="text-2xl sm:text-4xl font-semibold text-[var(--accent)] font-heading max-w-2xl leading-tight">
            Stop Guessing If Your Store Survives Autonomous Bots.
          </h2>

          <p className="mt-4 text-sm sm:text-base text-[var(--text-muted)] max-w-xl font-sans leading-relaxed">
            Launch the 9-persona swarm against your sandbox endpoints. Uncover silent double charges, client price mutations, and webhook forgeries before autonomous shopping agents touch production revenue.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            {/* Primary CTA: Let's Simulate */}
            <Link
              href={PLAYGROUND_URL}
              className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-md font-mono text-sm font-bold bg-[var(--accent)] text-[var(--accent-foreground)] hover:bg-[var(--accent-hover)] shadow-none   transition-all cursor-pointer group"
            >
              <Zap className="w-4 h-4 fill-current" />
              <span>Let&apos;s Simulate Now</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>

            <a
              href={GITHUB_REPO_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-5 py-3.5 rounded-md font-mono text-sm font-semibold bg-[var(--surface)] border border-[var(--border-strong)] text-[var(--text)] hover:bg-[var(--surface-hover)] transition cursor-pointer"
            >
              <GithubIcon className="w-4 h-4" />
              <span>Explore Code on GitHub</span>
              <ExternalLink className="w-3.5 h-3.5 text-[var(--text-dim)]" />
            </a>
          </div>
        </div>
      </div>

      {/* Main Footer Links */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* Col 1: Branding */}
          <div className="space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-[var(--accent)] flex items-center justify-center text-[var(--accent-foreground)]">
                <ShieldAlert className="w-4 h-4" />
              </div>
              <span className="font-bold text-base text-[var(--text)]">
                AgentReady<span className="text-[var(--text)]">.Lab</span>
              </span>
            </div>
            <p className="text-xs text-[var(--text-dim)] font-sans leading-relaxed">
              Adversarial crash-testing, dual-ledger compliance auditing, and self-healing for AI agent commerce on the PayPal Sandbox.
            </p>
            <div className="text-[11px] text-[var(--text-muted)] font-mono">
              &ldquo;PayPal protects the payment. Nobody tests the merchant&rsquo;s side of an agent order. AgentReady Lab does.&rdquo;
            </div>
          </div>

          {/* Col 2: Product & Simulation */}
          <div className="space-y-2">
            <span className="font-bold text-[var(--text)] uppercase tracking-wider text-[11px]">
              Platform
            </span>
            <ul className="space-y-1.5 text-xs">
              <li>
                <Link href={PLAYGROUND_URL} className="hover:text-[var(--text)] transition">
                  Simulation Playground
                </Link>
              </li>
              <li>
                <a href="#about" className="hover:text-[var(--text)] transition">
                  Product Overview
                </a>
              </li>
              <li>
                <a href="#threats" className="hover:text-[var(--text)] transition">
                  6 Threat Vectors
                </a>
              </li>
              <li>
                <a href="#features" className="hover:text-[var(--text)] transition">
                  Bento Grid Features
                </a>
              </li>
              <li>
                <a href="#preview" className="hover:text-[var(--text)] transition">
                  Micro-Simulator Demo
                </a>
              </li>
            </ul>
          </div>

          {/* Col 3: Developer & Docs */}
          <div className="space-y-2">
            <span className="font-bold text-[var(--text)] uppercase tracking-wider text-[11px]">
              Documentation
            </span>
            <ul className="space-y-1.5 text-xs">
              <li>
                <a href="#docs" className="hover:text-[var(--text)] transition">
                  Getting Started Guide
                </a>
              </li>
              <li>
                <a href="#workflow" className="hover:text-[var(--text)] transition">
                  8-Step Workflow
                </a>
              </li>
              <li>
                <a href="#postman" className="hover:text-[var(--text)] transition">
                  Postman Collection v2.1
                </a>
              </li>
              <li>
                <a
                  href={`${GITHUB_REPO_URL}/blob/main/docs/ARCHITECTURE.md`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-[var(--text)] transition flex items-center gap-1"
                >
                  <span>System Architecture</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </a>
              </li>
              <li>
                <a
                  href={`${GITHUB_REPO_URL}/blob/main/docs/SPEC.md`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-[var(--text)] transition flex items-center gap-1"
                >
                  <span>Formal Engineering Spec</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </a>
              </li>
            </ul>
          </div>

          {/* Col 4: Sponsors & Ecosystem */}
          <div className="space-y-2">
            <span className="font-bold text-[var(--text)] uppercase tracking-wider text-[11px]">
              Built With &amp; Sponsors
            </span>
            <ul className="space-y-1.5 text-xs">
              <li>PayPal Sandbox Orders v2</li>
              <li>APIMatic Python SDK (paypal==2.29)</li>
              <li>AG Grid Quartz (Community v32+)</li>
              <li>Channel3 Real E-Commerce Catalog</li>
              <li>Google Gemini 3.8 Flash LLMs</li>
              <li>Render Cloud Hosting</li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar & Legal Disclaimers */}
        <div className="pt-8 border-t border-[var(--border)] flex flex-col md:flex-row items-center justify-between gap-4 text-[11px] text-[var(--text-dim)]">
          <div>
            &copy; 2026 AgentReady Lab. Open-source MIT License.
          </div>
          <div className="text-center md:text-right font-sans">
            <em>Disclaimer: Score weights are AgentReady Lab&rsquo;s heuristic design, not an official PayPal standard or certification.</em>
          </div>
        </div>
      </div>
    </footer>
  );
};
