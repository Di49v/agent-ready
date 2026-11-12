"use client";

import { useRef, useEffect, useState } from "react";
import { gsap } from "gsap";

export interface AccordionStage {
  stage: string;
  title: string;
  description: string;
  footer: string;
  accentText: string;
  accentBorder: string;
}

interface Props {
  items: AccordionStage[];
  defaultIndex?: number;
}

export default function AccordionGallery({ items, defaultIndex = 0 }: Props) {
  const [active, setActive] = useState(defaultIndex);
  const panelRefs = useRef<(HTMLDivElement | null)[]>([]);
  const titleGroupRefs = useRef<(HTMLDivElement | null)[]>([]);
  const descRefs = useRef<(HTMLParagraphElement | null)[]>([]);
  const footerRefs = useRef<(HTMLDivElement | null)[]>([]);
  
  // Ref to hold our hover delay timer
  const timeoutRef = useRef<number | null>(null);

  const handleEnter = (i: number) => {
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
    // 120ms delay prevents the "sliding under cursor" glitch
    timeoutRef.current = window.setTimeout(() => setActive(i), 120);
  };

  const handleLeave = () => {
    if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
  };

  useEffect(() => {
    const isDesktop = window.matchMedia("(min-width: 768px)").matches;
    
    const ctx = gsap.context(() => {
      panelRefs.current.forEach((panel, i) => {
        if (!panel) return;
        const isActive = i === active;
        
        gsap.to(panel, {
          flexGrow: isActive ? (isDesktop ? 3.5 : 4) : 1,
          duration: 0.7,
          ease: "expo.out",
        });
        
        gsap.to(titleGroupRefs.current[i], {
          opacity: isActive ? 1 : 0.5,
          duration: 0.5,
          ease: "power2.out",
        });

        gsap.to([descRefs.current[i], footerRefs.current[i]], {
          opacity: isActive ? 1 : 0,
          duration: isActive ? 0.6 : 0.2,
          delay: isActive ? 0.15 : 0,
          ease: "power2.out",
        });
      });
    });

    return () => ctx.revert();
  }, [active]);

  return (
    <div className="flex flex-col md:flex-row w-full h-[600px] md:h-[280px] gap-4">
      {items.map((item, i) => (
        <div
          key={i}
          ref={(el) => { panelRefs.current[i] = el; }}
          onMouseEnter={() => handleEnter(i)}
          onMouseLeave={handleLeave}
          onClick={() => {
            if (timeoutRef.current) window.clearTimeout(timeoutRef.current);
            setActive(i);
          }}
          className={`relative flex-[1_1_0] overflow-hidden rounded-xl border bg-[var(--surface-sunken)] transition-colors cursor-pointer will-change-[flex-grow] ${
            i === active 
              ? item.accentBorder 
              : "border-[var(--border)] hover:border-[var(--text-muted)]/30"
          }`}
        >
          <div className="absolute top-0 left-0 w-[300px] md:w-[320px] h-full p-5 md:p-6 flex flex-col justify-between pointer-events-none">
            
            <div ref={(el) => { titleGroupRefs.current[i] = el; }}>
              <span className={`inline-flex px-2 py-0.5 rounded text-[11px] font-mono bg-[var(--surface)] border transition-colors ${
                i === active 
                  ? `${item.accentText} ${item.accentBorder}` 
                  : "border-[var(--border)] text-[var(--text-muted)]"
              }`}>
                {item.stage}
              </span>
              
              <h4 className={`font-heading font-semibold text-base mt-3.5 transition-colors ${
                i === active ? item.accentText : "text-[var(--text)]"
              }`}>
                {item.title}
              </h4>
              
              <p 
                ref={(el) => { descRefs.current[i] = el; }}
                className="text-[13px] text-[var(--text-muted)] mt-2.5 leading-relaxed font-sans"
              >
                {item.description}
              </p>
            </div>

            <div 
              ref={(el) => { footerRefs.current[i] = el; }}
              className="mt-4 pt-3 border-t border-[var(--border)] text-[11px] font-mono text-[var(--text-dim)]"
            >
              {item.footer}
            </div>
            
          </div>
        </div>
      ))}
    </div>
  );
}