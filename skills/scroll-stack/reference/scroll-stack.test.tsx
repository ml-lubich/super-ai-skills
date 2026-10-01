import { afterEach, beforeEach, describe, expect, it } from "bun:test";
import { render, waitFor } from "@testing-library/react";
import { setReducedMotion } from "./reduced-motion-test-util";
import { ScrollStack } from "./scroll-stack";

const items = [
  { key: "a", node: <article>Card A</article> },
  { key: "b", node: <article>Card B</article> },
  { key: "c", node: <article>Card C</article> },
];

function setViewport(opts: {
  innerWidth: number;
  maxTouchPoints?: number;
  hardwareConcurrency?: number;
  coarse?: boolean;
  hoverNone?: boolean;
}) {
  Object.defineProperty(window, "innerWidth", {
    configurable: true,
    value: opts.innerWidth,
  });
  Object.defineProperty(navigator, "maxTouchPoints", {
    configurable: true,
    value: opts.maxTouchPoints ?? 0,
  });
  Object.defineProperty(navigator, "hardwareConcurrency", {
    configurable: true,
    value: opts.hardwareConcurrency ?? 8,
  });
  window.matchMedia = ((query: string) =>
    ({
      matches:
        (query.includes("pointer: coarse") && !!opts.coarse) ||
        (query.includes("hover: none") && !!opts.hoverNone),
      media: query,
      addEventListener() {},
      removeEventListener() {},
      addListener() {},
      removeListener() {},
      onchange: null,
      dispatchEvent: () => false,
    }) as MediaQueryList) as typeof window.matchMedia;
}

beforeEach(() => {
  setReducedMotion(false);
});

afterEach(() => {
  setReducedMotion(false);
});

describe("ScrollStack", () => {
  it("renders every card in the compact column on a phone-class viewport", async () => {
    setViewport({ innerWidth: 390, maxTouchPoints: 5, coarse: true, hoverNone: true });
    const { container, getByText } = render(<ScrollStack items={items} />);
    await waitFor(() =>
      expect(container.firstElementChild?.getAttribute("data-variant")).toBe("compact")
    );
    expect(getByText("Card A")).toBeInTheDocument();
    expect(getByText("Card C")).toBeInTheDocument();
    expect(container.querySelector(".sticky")).toBeNull();
  });

  it("uses the sticky stack on a wide mouse-driven desktop", async () => {
    setViewport({ innerWidth: 1600 });
    const { container } = render(<ScrollStack items={items} />);
    await waitFor(() =>
      expect(container.firstElementChild?.getAttribute("data-variant")).toBe("stack")
    );
    const cards = container.querySelectorAll("[data-scroll-stack-card]");
    expect(cards.length).toBe(3);
    for (const card of Array.from(cards)) {
      expect(card.className).toMatch(/\bsticky\b/);
    }
  });

  it("falls back to the column when the user prefers reduced motion, even on desktop", async () => {
    setViewport({ innerWidth: 1600 });
    setReducedMotion(true);
    const { container } = render(<ScrollStack items={items} />);
    await waitFor(() =>
      expect(container.firstElementChild?.getAttribute("data-variant")).toBe("compact")
    );
    expect(container.querySelector(".sticky")).toBeNull();
  });

  it("passes the compact grid classes through so the column matches the old layout exactly", async () => {
    setViewport({ innerWidth: 390, maxTouchPoints: 5, coarse: true, hoverNone: true });
    const { container } = render(
      <ScrollStack items={items} compactClassName="grid grid-cols-1 gap-6 md:grid-cols-3" />
    );
    await waitFor(() =>
      expect(container.firstElementChild?.getAttribute("data-variant")).toBe("compact")
    );
    expect(container.firstElementChild?.className).toMatch(/\bmd:grid-cols-3\b/);
  });
});
