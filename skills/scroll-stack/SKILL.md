---
name: scroll-stack
description: Misha's scroll-driven "stacking cards" pattern for React/Next.js sites - cards pin under the navbar and stack as the visitor scrolls, each settling back as the next arrives, with a pure viewport-routing function that keeps phones, tablets, coarse pointers, reduced-motion and low-core devices on a plain column. Use when a client asks for movement, immersive effects, scrollytelling, "make it feel less like a template", or a signature scroll move on a landing page. Pairs with scroll-craft (nateherk) for whole-page grammar; this skill is the one reusable device.
---

# scroll-stack

One device, done properly: cards that **pin and stack** as you scroll. Shipped
first on the portfolio site, then on eria.co's homepage Case Studies (ERI-22), then on
w3sourcing.com's How-it-works steps (`src/components/scroll-stack.tsx` there).
Reference implementation in `reference/` (framer-motion, TypeScript, bun tests).

## The rule that makes it safe

The stack is only for **wide, mouse-driven, motion-ok desktops**. Everything else
gets the caller's existing layout untouched. That decision is a pure function so
it is unit-tested, not eyeballed:

| Signal | Result |
|---|---|
| `innerWidth <= 1366` | column |
| `prefers-reduced-motion` | column |
| `(pointer: coarse)` | column |
| touch points > 0 **and** `(hover: none)` | column |
| touch points > 0 **and** width <= 1920 | column |
| `hardwareConcurrency <= 4` | column |
| otherwise | sticky stack |

`shouldUseCompactScrollStackViewport(signals)` in `reference/scroll-stack-layout.ts`.
Port it verbatim with its test; the thresholds came from real device complaints.

## How the component is shaped

```tsx
<ScrollStack
  compactClassName="mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-3"  // the OLD layout, verbatim
  className="mx-auto max-w-5xl"
  items={things.map((t, i) => ({ key: t.slug, node: <Card ... /> }))}
/>
```

- Two shapes exist. ERIA's takes `compactClassName` and renders the column itself.
  w3sourcing's exposes `useScrollStackCompactViewport()` and lets the caller branch
  (`StepsDesktop`), because its compact layout was already two different DOM trees
  (chevron row + mobile timeline). Pick the second shape whenever the existing
  layout is more than one element; pass `cardClassName` when the caller's cards
  already carry their own chrome (glass panels) so you don't double-wrap.
- `compactClassName` **is the pre-existing layout's classes**. Passing them makes
  the change a no-op for every compact visitor - that is the whole trick, and it
  is what lets you ship a scroll effect to a live client site without a mobile
  regression.
- SSR always paints the compact column; the effect measures the viewport and
  swaps to the stack after mount. Place the section below the fold.
- The stack root owns the `useScroll` ref (`StackRoot`). Calling `useScroll` in
  the branch that never mounts the ref throws framer's "target ref not hydrated"
  invariant - on phones, in production. The test suite catches it.
- Per-card: `sticky`, `top = stickyTop + i * stackOffset`, `minHeight = scrollPerCard vh`
  runway; the covered card animates to `scale 0.94 / opacity 0.72` over the
  slice of progress where the next card travels in. Last card never shrinks.

Defaults that felt right on a 1600x1000 desktop with a 76px fixed nav:
`stickyTop 112`, `stackOffset 18`, `scrollPerCard 62`.

## Verification that counts

1. Unit: the routing table above + component contract (`reference/*.test.*`).
2. Browser, desktop **1600x1000**: `[data-variant="stack"]`, every
   `[data-scroll-stack-card]` has `position: sticky`; after scrolling ~700px into
   the section the covered cards report `transform: scale(0.94)`.
3. Browser, **iPhone 12**: `[data-variant="compact"]`, zero sticky cards, and the
   screenshot matches the pre-change layout.
4. Dev log has no hydration warnings.

Use `agent-browser` for 2-4; the exact eval snippets are in the ERIA session
that shipped it (2026-09-05).

## Don'ts

- Don't apply it to more than one section per page. Five sections behaving
  identically is one section shown five times (scroll-craft's first rule).
- Don't port the portfolio's 900-line drag-physics card engine. The 150-line
  framer version in `reference/` is the whole device.
- Don't skip the pure-function port to "just use a media query" - reduced motion,
  coarse pointer and low cores are not breakpoints.

## Dark pages (learned on the-ascendant, 2026-09-17)

The reference dims a covered card with `opacity 0.72`. On a dark page that lets
the card underneath show through the one on top. Dim with
`filter: brightness(0.6)` via `useTransform(dim, d => \`brightness(${d})\`)`
instead, and make card backgrounds fully opaque. Also: the reference's
`motion.div` carries its own panel chrome; strip it when items bring their own,
or you get a double frame.
