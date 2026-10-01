"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { motion, useReducedMotion, useScroll, useTransform, type MotionValue } from "framer-motion";
import {
  resolveScrollStackVariant,
  shouldUseCompactScrollStackViewport,
} from "@/lib/scroll-stack-layout";

/**
 * ScrollStack — cards that pin under the navbar and stack as the visitor
 * scrolls, each one settling back and dimming a touch as the next arrives
 * (ERI-22, "movement and immersive effects"). Scroll is the only input.
 *
 * Only wide, mouse-driven, motion-ok desktops get the stack. Phones, tablets,
 * coarse pointers, reduced-motion and low-core devices render `items` inside
 * a plain element with `compactClassName` — pass the pre-existing grid classes
 * and those visitors see exactly what they saw before.
 *
 * ponytail: the variant is measured in an effect, so SSR and first paint are
 * always the compact column and wide desktops swap to the stack after mount.
 * The section sits below the fold, so the swap lands before it is scrolled
 * into view. Upgrade to a CSS-only container query if that ever stops being true.
 */

export type ScrollStackItem = { key: string; node: ReactNode };

type ScrollStackProps = {
  items: ScrollStackItem[];
  /** Classes for the compact/column root — pass the old grid classes for a no-op on phones. */
  compactClassName?: string;
  /** Classes for the stack root. */
  className?: string;
  /** Distance from the viewport top where cards pin (px). Clears the fixed navbar. */
  stickyTop?: number;
  /** Extra offset per card so the stack peeks (px). */
  stackOffset?: number;
  /** Scroll runway allocated per card (vh). */
  scrollPerCard?: number;
};

const NAV_CLEARANCE_PX = 112;

function useCompactViewport(): boolean | null {
  const reduced = useReducedMotion();
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
          prefersReducedMotion: Boolean(reduced),
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
  compactClassName,
  className,
  stickyTop = NAV_CLEARANCE_PX,
  stackOffset = 18,
  scrollPerCard = 62,
}: ScrollStackProps) {
  const compact = useCompactViewport();
  const variant = resolveScrollStackVariant(undefined, compact ?? true);

  if (variant !== "stack") {
    return (
      <div data-variant={variant} className={compactClassName}>
        {items.map((item) => (
          <div key={item.key}>{item.node}</div>
        ))}
      </div>
    );
  }

  return (
    <StackRoot
      items={items}
      className={className}
      stickyTop={stickyTop}
      stackOffset={stackOffset}
      scrollPerCard={scrollPerCard}
    />
  );
}

type StackRootProps = Required<Pick<ScrollStackProps, "items" | "stickyTop" | "stackOffset" | "scrollPerCard">> &
  Pick<ScrollStackProps, "className">;

/** Owns the scroll container ref, so `useScroll` only ever runs with a mounted target. */
function StackRoot({ items, className, stickyTop, stackOffset, scrollPerCard }: StackRootProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"],
  });

  return (
    <div ref={containerRef} data-variant="stack" className={className}>
      {items.map((item, i) => (
        <StackCard
          key={item.key}
          index={i}
          count={items.length}
          progress={scrollYProgress}
          stickyTop={stickyTop + i * stackOffset}
          runwayVh={scrollPerCard}
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
  children: ReactNode;
};

function StackCard({ index, count, progress, stickyTop, runwayVh, children }: StackCardProps) {
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
      <motion.div
        style={{ scale, opacity, transformOrigin: "50% 0%" }}
        className="mx-auto max-w-3xl rounded-lg border border-foreground/10 bg-background/85 p-6 shadow-2xl shadow-black/30 backdrop-blur-md md:p-8"
      >
        {children}
      </motion.div>
    </div>
  );
}
