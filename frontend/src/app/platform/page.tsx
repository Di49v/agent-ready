"use client";

import React from "react";
import Link from "next/link";
import { Navbar } from "@/components/landing/Navbar";
import { Footer } from "@/components/landing/Footer";
import { DeliverablesHub } from "@/components/DeliverablesHub";
import { ArrowLeft } from "lucide-react";

export default function PlatformHubPage() {
  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)] flex flex-col font-sans transition-colors duration-200">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-xs font-mono text-[var(--text-muted)] hover:text-[var(--text)] transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Home</span>
          </Link>
        </div>

        {/* The DeliverablesHub component you removed from the simulation page! */}
        <DeliverablesHub />
      </main>

      <Footer />
    </div>
  );
}