"use client";

import React from "react";
import LogoLoop from "./landing/LogoLoop";
import { 
  SiPaypal, 
  SiPostman, 
  SiZapier, 
  SiRender 
} from "react-icons/si";

const sponsors = [
  // Icon-only nodes need the title so the text prints next to them
  { node: <SiPaypal className="text-[#00457C]" />, title: "PayPal" },
  
  // Typography nodes don't need a title, otherwise it prints twice!
  { node: <span className="font-bold tracking-tight text-[var(--text)]">AG Grid</span> },
  { node: <span className="font-bold text-[#14b5cb]">APIMatic</span> },
  { node: <span className="font-black italic text-[#9b51e0]">Astropods</span> },
  { node: <span className="font-bold text-[#21ba45]">Bryntum</span> },
  { node: <span className="font-bold tracking-tighter text-[#f26522]">Channel3</span> },
  { node: <span className="font-bold text-[#005571] dark:text-[#fec514]">Elastic</span> },
  { node: <span className="font-mono font-bold tracking-widest text-[var(--text)]">KERNEL</span> },
  
  { node: <SiPostman className="text-[#FF6C37]" />, title: "Postman" },
  { node: <SiRender className="text-[#46E3B7] dark:text-white" />, title: "Render" },
  { node: <SiZapier className="text-[#FF4A00]" />, title: "Zapier" },
];

export const GlobalSponsorTicker: React.FC = () => {
  return (
    <div className="w-full bg-[var(--surface-sunken)] border-b border-[var(--border)] overflow-hidden flex items-center justify-center h-9 relative z-50">
      <div className="absolute left-0 top-0 bottom-0 w-12 bg-gradient-to-r from-[var(--surface-sunken)] to-transparent z-10 pointer-events-none" />
      
      <LogoLoop
        logos={sponsors}
        speed={40} 
        direction="left"
        logoHeight={14}
        gap={48}
        hoverSpeed={10}
        scaleOnHover={false}
        layout="line"
        labels="inline"
        fadeOut={false} 
        muted={0.4} 
      />

      <div className="absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-[var(--surface-sunken)] to-transparent z-10 pointer-events-none" />
    </div>
  );
};