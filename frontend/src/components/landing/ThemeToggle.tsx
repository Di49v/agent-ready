"use client";

import React, { useEffect, useState } from "react";
import { useTheme } from "@/lib/theme-context";
import { Sun, Moon } from "lucide-react";

export const ThemeToggle: React.FC<{ className?: string }> = ({ className = "" }) => {
  const { theme, toggleTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className={`w-8 h-8 rounded-md bg-[var(--surface-sunken)] border border-[var(--border)] ${className}`} />
    );
  }

  return (
    <button
      onClick={toggleTheme}
      type="button"
      title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
      className={`inline-flex items-center justify-center w-8 h-8 rounded-md border border-[var(--border)] bg-[var(--surface)] text-[var(--text-muted)] hover:text-[var(--text)] hover:border-[var(--border-strong)] transition-colors cursor-pointer ${className}`}
    >
      {theme === "dark" ? (
        <Sun className="w-4 h-4 text-[var(--highlight)] stroke-[1.5]" />
      ) : (
        <Moon className="w-4 h-4 text-[var(--text-muted)] stroke-[1.5]" />
      )}
    </button>
  );
};
