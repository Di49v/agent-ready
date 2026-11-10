"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function DashboardRedirect() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/simulate");
  }, [router]);

  return (
    <div className="min-h-screen bg-[#08090C] text-[#F1F5F9] flex flex-col items-center justify-center font-mono">
      <div className="flex items-center gap-3">
        <div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-zinc-400">Redirecting to Simulation Workbench...</span>
      </div>
    </div>
  );
}

