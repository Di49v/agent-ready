"use client";

import {
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type CSSProperties,
} from "react";

type IdleMode = "none" | "wave" | "pulse";

interface TextPressureProps {
  text?: string;
  fontFamily?: string;
  fontUrl?: string;
  width?: boolean;
  weight?: boolean;
  italic?: boolean;
  alpha?: boolean;
  flex?: boolean;
  stroke?: boolean;
  scale?: boolean;
  radius?: number;
  smoothing?: number;
  idle?: IdleMode;
  idleSpeed?: number;
  clickRipple?: boolean;
  textColor?: string;
  pressureColor?: string;
  strokeColor?: string;
  strokeWidth?: number;
  className?: string;
  minFontSize?: number;
}

interface Point {
  x: number;
  y: number;
}

const useIsomorphicLayoutEffect =
  typeof window !== "undefined" ? useLayoutEffect : useEffect;

const clamp01 = (value: number) =>
  Math.min(1, Math.max(0, value));

const distance = (a: Point, b: Point) => {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  return Math.sqrt(dx * dx + dy * dy);
};

const TextPressure: React.FC<TextPressureProps> = ({
  text = "Compressa",
  fontFamily = "Roboto Flex",
  fontUrl = "https://fonts.googleapis.com/css2?family=Roboto+Flex:opsz,wdth,wght@8..144,25..151,100..1000&display=swap",
  flex = false,
  stroke = false,
  scale = false,
  radius = 0.9,
  smoothing = 0.85,
  textColor = "currentColor",
  strokeColor = "#FF0000",
  strokeWidth = 3,
  className = "",
  minFontSize = 28,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const titleRef = useRef<HTMLHeadingElement | null>(null);
  const spansRef = useRef<(HTMLSpanElement | null)[]>([]);

  const wakeRef = useRef<(() => void) | null>(null);
  const visibleRef = useRef(true);

  const cursorRef = useRef<Point & { seen: boolean }>({
    x: 0,
    y: 0,
    seen: false,
  });

  const mouseRef = useRef<Point>({ x: 0, y: 0 });

  const [fontSize, setFontSize] = useState(minFontSize);
  const [scaleY, setScaleY] = useState(1);

  const chars = Array.from(text);

  useIsomorphicLayoutEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const resize = () => {
      const containerWidth =
        container.getBoundingClientRect().width;

      const nextFontSize = Math.max(
        chars.length
          ? containerWidth / (chars.length / 2)
          : minFontSize,
        minFontSize
      );

      setFontSize(nextFontSize);

      const containerHeight =
        container.getBoundingClientRect().height;

      setScaleY(
        scale && containerHeight > 0
          ? containerHeight / nextFontSize
          : 1
      );
    };

    resize();

    const observer = new ResizeObserver(resize);
    observer.observe(container);

    return () => observer.disconnect();
  }, [chars.length, minFontSize, scale]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const cursor = cursorRef.current;
    const wake = () => wakeRef.current?.();

    const handleMouseMove = (event: MouseEvent) => {
      cursor.x = event.clientX;
      cursor.y = event.clientY;
      cursor.seen = true;
      wake();
    };

    const handleMouseLeave = () => {
      cursor.seen = false;
      wake();
    };

    const handleTouch = (event: TouchEvent) => {
      const touch = event.touches[0];
      if (!touch) return;
      cursor.x = touch.clientX;
      cursor.y = touch.clientY;
      cursor.seen = true;
      wake();
    };

    container.addEventListener("mousemove", handleMouseMove);
    container.addEventListener("mouseleave", handleMouseLeave);
    container.addEventListener("touchstart", handleTouch, { passive: true });
    container.addEventListener("touchmove", handleTouch, { passive: true });
    container.addEventListener("touchend", handleMouseLeave);

    const observer = new IntersectionObserver(([entry]) => {
      visibleRef.current = entry.isIntersecting;
      if (entry.isIntersecting) wake();
    });

    observer.observe(container);

    return () => {
      container.removeEventListener("mousemove", handleMouseMove);
      container.removeEventListener("mouseleave", handleMouseLeave);
      container.removeEventListener("touchstart", handleTouch);
      container.removeEventListener("touchmove", handleTouch);
      container.removeEventListener("touchend", handleMouseLeave);
      observer.disconnect();
    };
  }, []);

  useEffect(() => {
    const title = titleRef.current;
    const container = containerRef.current;

    if (!title || !container) return;

    const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    if (motionQuery.matches) return;

    let rafId = 0;
    let lastTime = 0;

    const tick = (now: number) => {
      rafId = 0;
      const elapsed = lastTime ? Math.min(now - lastTime, 64) : 16;
      lastTime = now;

      const cursor = cursorRef.current;
      const mouse = mouseRef.current;

      const follow = 1 - Math.exp(-elapsed / Math.max(16, smoothing * 80));
      mouse.x += (cursor.x - mouse.x) * follow;
      mouse.y += (cursor.y - mouse.y) * follow;

      const titleRect = title.getBoundingClientRect();
      const maxDistance = Math.max(titleRect.width * radius, 1);

      let changed = false;

      spansRef.current.forEach((span) => {
        if (!span) return;

        const rect = span.getBoundingClientRect();
        const center = {
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2,
        };

        const pressure = cursor.seen
          ? clamp01(1 - distance(mouse, center) / maxDistance)
          : 0;

        // FIXED WEIGHT: Starts at 700 (bold), scales up to 1000 (black) on hover
        const wght = Math.floor(700 + 300 * pressure); 
        const settings = `'wght' ${wght}, 'wdth' 100, 'ital' 0`;
        
        if (span.style.fontVariationSettings !== settings) {
          span.style.fontVariationSettings = settings;
          changed = true;
        }

        const movement = -(pressure * 1.2);
        const nextTransform = `translate3d(0, ${movement.toFixed(2)}px, 0)`;

        if (span.style.transform !== nextTransform) {
          span.style.transform = nextTransform;
          changed = true;
        }
      });

      const moving = Math.abs(cursor.x - mouse.x) > 0.1 || Math.abs(cursor.y - mouse.y) > 0.1;

      if (moving || changed) {
        rafId = requestAnimationFrame(tick);
      } else {
        lastTime = 0;
      }
    };

    const wake = () => {
      if (!rafId && visibleRef.current && !motionQuery.matches) {
        rafId = requestAnimationFrame(tick);
      }
    };

    wakeRef.current = wake;

    return () => {
      cancelAnimationFrame(rafId);
      wakeRef.current = null;
    };
  }, [radius, smoothing]);

  useEffect(() => {
    spansRef.current.forEach((span) => {
      if (span) span.style.transform = "translate3d(0, 0, 0)";
    });
    wakeRef.current?.();
  }, [text, fontSize]);

  const titleStyle = {
    fontFamily,
    fontSize,
    lineHeight: 1.15,
    transform: `scale(1, ${scaleY})`,
    transformOrigin: "left top",
    fontWeight: 800, // FIXED WEIGHT: Ensures base rendering is very bold
    color: textColor,
    overflowWrap: "normal",
    wordBreak: "normal",
    "--text-pressure-stroke-width": `${strokeWidth}px`,
    "--text-pressure-stroke-color": strokeColor,
  } as CSSProperties;

  let charIndex = 0;
  const words = text.split(/(\s+)/);

  return (
    <div ref={containerRef} className="relative w-full bg-transparent">
      <style>{`
        @import url('${fontUrl}');
        .text-pressure-title { white-space: normal; word-break: normal; overflow-wrap: normal; }
        .text-pressure-word { display: inline-block; white-space: nowrap; }
        .text-pressure-char { display: inline-block; will-change: transform; }
      `}</style>

      <h1
        ref={titleRef}
        aria-label={text}
        className={`text-pressure-title m-0 w-full select-none ${flex ? "flex justify-between" : ""} ${className}`}
        style={titleStyle}
      >
        {words.map((word, wordIndex) => {
          if (/^\s+$/.test(word)) {
            // FIXED SPACING: Hardcodes a precise gap for spaces so they never collapse
            return (
              <span key={`space-${wordIndex}`} className="inline-block w-[0.25em]"></span>
            );
          }

          const wordChars = Array.from(word);
          return (
            <span key={`word-${wordIndex}`} className="text-pressure-word">
              {wordChars.map((char, index) => {
                const currentIndex = charIndex++;
                return (
                  <span
                    key={`${currentIndex}-${index}`}
                    ref={(element) => {
                      spansRef.current[currentIndex] = element;
                    }}
                    data-char={char}
                    aria-hidden="true"
                    className="text-pressure-char"
                  >
                    {char}
                  </span>
                );
              })}
            </span>
          );
        })}
      </h1>
    </div>
  );
};

export default TextPressure;