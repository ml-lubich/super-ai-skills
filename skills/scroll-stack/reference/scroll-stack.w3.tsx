"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { motion, useScroll, useTransform, type MotionValue } from "framer-motion";
import {
  resolveScrollStackVariant,
  shouldUseCompactScrollStackViewport,
} from "@/lib/scroll-stack-layout";
import { useHydrationSafeReducedMotion } from "@/lib/use-hydration-safe-reduced-motion";

/**
 * ScrollStack — cards that pin under the header and stack as the visitor
 * scrolls, each settling back a touch as the next arrives. Scroll is the only
 * input. Only wide, mouse-driven, motion-ok desktops get it; every other
 * viewport keeps the caller's existing layout (see `useScrollStackCompactViewport`).
 *
 * SSR and first paint never render the stack: the variant is measured after
 * mount, so hydration is identical to the compact path. Place below the fold.
 *
 * Same device as eria.co's homepage case studies; routing rules live in
 * `src/lib/scroll-stack-layout.ts` with their tests.
 */

export type ScrollStackItem = { key: string; node: ReactNode };

type ScrollStackProps = {
  items: ScrollStackItem[];
  /** Stack root classes. */
  className?: string;
  /** Per-card shell classes — the caller's cards usually bring their own chrome. */
  cardClassName?: string;
  /** Distance from the viewport top where cards pin (px). Clears the fixed header. */
  stickyTop?: number;
  /** Extra offset per card so the stack peeks (px). */
  stackOffset?: number;
  /** Scroll runway allocated per card (vh). */
  scrollPerCard?: number;
};

const HEADER_CLEARANCE_PX = 104;

/** `null` until measured on the client — treat as compact. */
export function useScrollStackCompactViewport(): boolean | null {
  const reduced = useHydrationSafeReducedMotion();
  const [compact, setCompact] = useState<boolean | null>(null);

  useEffect(() => {
    const mq = (query: string) =>
      typeof window.matchMedia === "function" && window.matchMedia(query).matches;
    const compute = () =>
      setCompact(
        shouldUseCompactScrollStackViewport({
          innerWidth: window.innerWidth,
          pointerCoarse: mq("(pointer: coarse)"),
          hoverNone: mq("(hover: none)"),
          maxTouchPoints: navigator.maxTouchPoints ?? 0,
          prefersReducedMotion: reduced,
          hardwareConcurrency: navigator.hardwareConcurrency,
        })
      );
    compute();
    window.addEventListener("resize", compute, { passive: true });
    return () => window.removeEventListener("resize", compute);
  }, [reduced]);

  return compact;
}

export function ScrollStack({
  items,
  className,
  cardClassName = "mx-auto max-w-3xl",
  stickyTop = HEADER_CLEARANCE_PX,
  stackOffset = 18,
  scrollPerCard = 62,
}: ScrollStackProps) {
  // The root owns the scroll ref so `useScroll` only ever runs with a mounted
  // target — calling it on a path that never attaches the ref throws framer's
  // "target ref is defined but not hydrated" invariant.
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"],
  });
  const variant = resolveScrollStackVariant(undefined, false);

  return (
    <div ref={containerRef} data-variant={variant} className={className}>
      {items.map((item, i) => (
        <StackCard
          key={item.key}
          index={i}
          count={items.length}
          progress={scrollYProgress}
          stickyTop={stickyTop + i * stackOffset}
          runwayVh={scrollPerCard}
          className={cardClassName}
        >
          {item.node}
        </StackCard>
      ))}
    </div>
  );
}

type StackCardProps = {
  index: number;
  count: number;
  progress: MotionValue<number>;
  stickyTop: number;
  runwayVh: number;
  className: string;
  children: ReactNode;
};

function StackCard({ index, count, progress, stickyTop, runwayVh, className, children }: StackCardProps) {
  // Card i is "covered" while card i+1 travels in: that slice of the runway.
  const coverStart = (index + 1) / count;
  const coverEnd = Math.min(1, (index + 2) / count);
  const isLast = index === count - 1;
  const scale = useTransform(progress, [coverStart, coverEnd], isLast ? [1, 1] : [1, 0.94]);
  const opacity = useTransform(progress, [coverStart, coverEnd], isLast ? [1, 1] : [1, 0.72]);

  return (
    <div
      data-scroll-stack-card
      className="sticky"
      style={{ top: stickyTop, minHeight: `${runwayVh}vh` }}
    >
      <motion.div style={{ scale, opacity, transformOrigin: "50% 0%" }} className={className}>
        {children}
      </motion.div>
    </div>
  );
}
