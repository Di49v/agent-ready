"use client";

import React, { useState } from "react";
import Link from "next/link";
import { PLAYGROUND_URL, GITHUB_REPO_URL } from "@/lib/constants";
import { ThemeToggle } from "./ThemeToggle";
import {
  Zap,
  Menu,
  X,
  Lock,
  ArrowRight,
  ExternalLink,
} from "lucide-react";

const GithubIcon: React.FC<{ className?: string }> = ({ className = "w-4 h-4" }) => (
  <svg className={className} fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
  </svg>
);

export const Navbar: React.FC = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { label: "Overview", href: "#about" },
    { label: "Threats", href: "#threats" },
    { label: "Features", href: "#features" },
    { label: "Interactive Demo", href: "#preview" },
    { label: "Workflow", href: "#workflow" },
    { label: "Docs", href: "#docs" },
    { label: "Postman Hub", href: "#postman" },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-[var(--border)] bg-[var(--surface)]/95 backdrop-blur-sm transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between gap-4">
        {/* Logo & Product Identity */}
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2 group">
            <span className="audit-status-led w-2 h-2 rounded-full bg-[var(--accent)]" />
            <div className="flex items-center gap-2">
              <span className="font-heading font-semibold text-base tracking-tight text-[var(--text)]">
                AgentReady<span className="text-[var(--text)]">.Lab</span>
              </span>
              <span className="hidden sm:inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[11px] font-mono bg-[var(--surface-sunken)] text-[var(--text-muted)] border border-[var(--border)]">
                <Lock className="w-2.5 h-2.5 stroke-[1.5]" />
                Sandbox Locked
              </span>
            </div>
          </Link>
        </div>

        {/* Desktop Navigation Links */}
        <nav className="hidden lg:flex items-center gap-1 text-[13px] font-sans">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="px-2.5 py-1 rounded text-[var(--text-muted)] hover:text-[var(--text)] hover:bg-[var(--surface-hover)] transition-colors"
            >
              {link.label}
            </a>
          ))}
        </nav>

        {/* Action Controls & Primary CTA */}
        <div className="flex items-center gap-2">
          {/* Theme Toggle */}
          <ThemeToggle />

          {/* GitHub Repo */}
          <a
            href={GITHUB_REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            title="View Source on GitHub"
            className="hidden sm:inline-flex items-center justify-center w-8 h-8 rounded-md border border-[var(--border)] bg-[var(--surface)] text-[var(--text-muted)] hover:text-[var(--text)] hover:border-[var(--border-strong)] transition-colors"
          >
            <GithubIcon className="w-4 h-4" />
          </a>

          {/* Primary CTA: Let's Simulate */}
          <Link
            href={PLAYGROUND_URL}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md font-sans text-xs font-medium bg-[var(--accent)] text-[var(--accent-foreground)] hover:bg-[var(--accent-hover)] transition-colors cursor-pointer group"
          >
            <Zap className="w-3.5 h-3.5 fill-current stroke-[1.5]" />
            <span>Let&apos;s Simulate</span>
            <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform stroke-[1.5]" />
          </Link>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden inline-flex items-center justify-center p-1.5 rounded-md border border-[var(--border)] bg-[var(--surface)] text-[var(--text-muted)] hover:text-[var(--text)]"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-4 h-4 stroke-[1.5]" /> : <Menu className="w-4 h-4 stroke-[1.5]" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-t border-[var(--border)] bg-[var(--surface)] px-4 pt-3 pb-5 flex flex-col gap-1.5">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className="px-2.5 py-1.5 rounded text-sm text-[var(--text-muted)] hover:text-[var(--text)] hover:bg-[var(--surface-hover)] transition-colors"
            >
              {link.label}
            </a>
          ))}
          <div className="pt-3 mt-1 border-t border-[var(--border)] flex items-center justify-between">
            <a
              href={GITHUB_REPO_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-[var(--text-muted)] hover:text-[var(--text)]"
            >
              <GithubIcon className="w-3.5 h-3.5" />
              <span>GitHub</span>
              <ExternalLink className="w-3 h-3" />
            </a>
            <Link
              href={PLAYGROUND_URL}
              onClick={() => setMobileMenuOpen(false)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-[var(--accent)] text-[var(--accent-foreground)]"
            >
              <Zap className="w-3.5 h-3.5 fill-current" />
              <span>Let&apos;s Simulate</span>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};
