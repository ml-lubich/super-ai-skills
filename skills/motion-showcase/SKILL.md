---
name: motion-showcase
description: Techniques for making a React/Next.js + Tailwind site feel alive - hero product-demo video, staggered fade-up-blur reveals, ambient breathing glow, grain/noise texture, glass floating UI callouts, gradient mesh blobs. Distilled from studying natively.software (originals only - no copied assets, copy, or code). Use for "animated section", "demo video", "make the site feel alive", "natively-style", "hero video", "product showcase", "landing page feels flat".
---

# motion-showcase

Six small, composable effects that make a marketing/portfolio hero feel
crafted instead of templated. None need a heavy animation library - CSS
transitions/keyframes + one `IntersectionObserver` hook cover all of them.
Reach for `scroll-stack` (`~/.claude/skills/scroll-stack/SKILL.md`) instead
when the ask is specifically pinning/stacking cards on scroll - that's a
different, already-solved device. Don't combine more than 2-3 of these on
one page; stacking all six is how a page starts looking like a demo reel.

## Principles

- **CSS does the animating, JS only flips a class/state.** Cheaper, survives
  React re-renders, and degrades to "just visible" if JS fails.
  `prefers-reduced-motion` kills every effect below to opacity:1/no transform,
  no exceptions.
- **Everything decorative is `pointer-events-none` and `aria-hidden`.** Glow
  blobs, noise overlays, floating chips over a video - none of it is content.
  Real text/CTAs never live inside a decorative-only layer.
  Verify with `mcp__*chrome-devtools*__take_snapshot` (or Playwright's a11y
  tree) that content order matches visual order and decorative divs don't
  appear as focusable/labelled nodes.
- **One offset table per section, not one for the whole page.** Vary the
  translateY/scale/delay per element (see below) so a stagger reads as
  choreography, not a single global fade class copy-pasted five times.

## 1. Hero background/demo video

What you see: a full-bleed video sits behind the hero copy, fading to the
page background at the edges instead of hard-cutting.

Recipe:
```tsx
// muted MUST be set as a DOM property, not just the JSX prop, for autoplay
// to be reliable across Safari/iOS - React's attribute reflection alone
// isn't always enough on first paint.
const ref = useRef<HTMLVideoElement>(null);
useEffect(() => { if (ref.current) ref.current.muted = true; }, []);

<div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
  <video
    ref={ref}
    src="/hero.mp4" poster="/hero-poster.jpg"
    autoPlay muted loop playsInline preload="auto"
    className="h-full w-full object-cover object-top"
  />
  {/* fade-to-background mask, NOT a hard edge */}
  <div className="absolute inset-0 bg-[radial-gradient(60%_100%_at_50%_0%,transparent_30%,var(--background)_100%)]" />
</div>
```
- `preload="auto"` only for the one above-the-fold hero video; any
  secondary/mobile duplicate gets `preload="metadata"` to save bandwidth.
- `autoplay + muted + playsinline + loop`, no controls, is the whole
  cross-browser contract. Missing any one of the four silently breaks
  autoplay on some browser.
- Reduced-motion / `prefers-reduced-motion`: skip the `<video>` entirely and
  render the poster `<img>` - don't just pause it, avoid the network fetch.
- Mobile: swap to a shorter/lower-res source via `<picture>`-style
  breakpoint branching or `matchMedia`, not the same asset scaled down.

## 2. Staggered fade-up(-blur) reveal on scroll

What you see: each hero element - badge, headline, subhead, CTA - arrives
on its own delay and its own travel distance (4px for a small badge, 80px
for a big visual), not a uniform "everything fades in together."

Recipe (zero-dependency hook + CSS, no Framer Motion required):
```tsx
function useRevealed<T extends HTMLElement>() {
  const ref = useRef<T>(null);
  const [shown, setShown] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => e.isIntersecting && (setShown(true), io.disconnect()), { threshold: 0.2 });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return { ref, shown };
}

// per element: pick a small distance table, not one global value
<div style={{
  opacity: shown ? 1 : 0,
  transform: shown ? "none" : "translateY(24px)",
  filter: shown ? "none" : "blur(2px)",
  transition: "opacity .6s cubic-bezier(.4,0,.2,1), transform .6s cubic-bezier(.4,0,.2,1), filter .6s",
  transitionDelay: shown ? "120ms" : "0ms", // stagger children by index * 80-120ms
}} />
```
- CSS-only fallback (no JS at all) for a single fixed-position element:
  `@keyframes fade-in-up { from { opacity:0; transform: translateY(30px) } to { opacity:1; transform: translateY(0) } } .reveal { animation: fade-in-up .6s ease-out forwards; }`
- If the project already has Framer Motion / `motion` installed, this maps
  directly to `initial={{opacity:0,y:24,filter:"blur(2px)"}} whileInView={{opacity:1,y:0,filter:"none"}} viewport={{once:true}}` -
  don't add the dependency just for this one effect.
- Distances that read well: badges/pills 4-16px, body copy 14-24px, big
  hero visuals 40-80px with an added `scale(0.96-0.98)`.

## 3. Ambient breathing glow

What you see: a decorative glow or card border pulses very slowly in the
background - alive, not distracting.

```css
@keyframes breathe { 0%, 100% { opacity: .1 } 50% { opacity: .3 } }
.ambient-glow { animation: breathe 4s ease-in-out infinite; }

@keyframes glow-breathe {
  0%, 100% { border-color: rgb(255 255 255 / .1); box-shadow: 0 0 0 transparent; }
  50%      { border-color: rgb(255 255 255 / .5); box-shadow: 0 0 20px rgb(255 255 255 / .1); }
}
```
4s for a large soft blob, 3s for a tighter border glow - slower reads as
ambient, anything under ~2s reads as an alert/notification. Always
`animation: none` under `prefers-reduced-motion: reduce`.

## 4. Grain/noise texture overlay

What you see: flat gradient sections get a faint film-grain texture instead
of looking like a solid color fill.

```tsx
const noiseSvg = `data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E`;

<div
  aria-hidden
  className="pointer-events-none absolute inset-0 opacity-[0.02] mix-blend-multiply"
  style={{ backgroundImage: `url("${noiseSvg}")`, backgroundSize: "200px 200px" }}
/>
```
This is a generic `feTurbulence` recipe (standard SVG filter primitive, not
proprietary) - write your own `baseFrequency`/opacity rather than reusing
someone else's data URI verbatim. Keep opacity in the 0.015-0.04 range;
above ~0.06 it reads as dirty rather than textured. `mix-blend-multiply` on
light backgrounds, plain overlay on dark ones.

## 5. Glass floating UI callout over a demo video/screenshot

What you see: a product demo is framed inside faux window chrome (colored
traffic-light dots), with a translucent glassmorphism card floating on top
showing a fake interaction (a question pill + streamed answer text) - it
demonstrates the feature without needing real narration.

```tsx
<div className="relative rounded-2xl overflow-hidden shadow-2xl ring-1 ring-white/10">
  {/* fake window chrome */}
  <div className="flex gap-2 p-3 bg-neutral-900">
    <span className="h-3 w-3 rounded-full bg-red-500" />
    <span className="h-3 w-3 rounded-full bg-yellow-500" />
    <span className="h-3 w-3 rounded-full bg-green-500" />
  </div>
  <video ... />
  {/* floating glass callout, positioned absolute, own reveal delay */}
  <div className="absolute bottom-6 left-1/2 -translate-x-1/2 rounded-xl bg-black/60 backdrop-blur-xl border border-white/10 px-4 py-3 text-white">
    <span className="inline-block rounded-full bg-blue-500/90 px-3 py-1 text-sm">Example question?</span>
    <p className="mt-2 text-sm text-white/90">Streamed-in answer copy…</p>
  </div>
</div>
```
Write your own copy/question for the callout - it's the mechanism (glass
card floating over faux chrome) you're reusing, not their product's text.
For a "streamed" answer, type the text with a `setInterval`/`requestAnimationFrame`
character reveal (20-35ms/char) rather than a canned typewriter library.

## 6. Gradient mesh blobs

What you see: 2-3 large, heavily blurred color blobs behind a hero visual
give it depth without a real image.

```tsx
<div className="absolute inset-0 -z-10 pointer-events-none">
  <div className="absolute left-1/4 top-1/3 h-64 w-64 rounded-full bg-gradient-to-tr from-orange-400 via-fuchsia-500 to-blue-500 blur-[60px] opacity-40" />
</div>
```
2-3 blobs max, `blur-[40px]` to `blur-[80px]`, opacity 0.3-0.5. More than
that and Safari's blur compositing gets visibly janky on scroll - test on
an actual Safari/iOS device, not just Chrome DevTools' CPU throttle.

## Recording and encoding your own demo video

1. Record the real screen/product interaction (QuickTime `Cmd+Shift+5`,
   or `agent-browser`/Playwright screen-record for a web demo) at native
   resolution, 30fps is enough - 60fps roughly doubles file size for no
   visible gain in a background loop.
2. Trim to a tight, seamlessly-loopable clip (first and last frame close
   enough that the loop cut isn't jarring) - 6-15s is plenty for a hero
   loop.
3. Encode two formats, both silent (strip audio, autoplay requires muted
   anyway so don't ship an audio track):
   ```bash
   ffmpeg -i raw.mov -an -c:v libx264 -crf 23 -preset slow -pix_fmt yuv420p -movflags +faststart hero.mp4
   ffmpeg -i raw.mov -an -c:v libvpx-vp9 -crf 32 -b:v 0 -row-mt 1 hero.webm
   ```
   `-movflags +faststart` moves the moov atom to the front so the video can
   start playing before it's fully downloaded - skip it and mobile Safari
   stalls on a multi-second video.
4. Generate the poster frame (shown before the video paints, and to
   reduced-motion visitors) from the first real frame, not a black frame:
   ```bash
   ffmpeg -i hero.mp4 -vf "select=eq(n\,0)" -vframes 1 hero-poster.jpg
   ```
5. Budget: a 10s 1080p hero loop should land under ~1.5MB mp4 / ~1MB webm
   at these settings. If it's bigger, drop resolution before dropping
   quality further - a crisp 1280px-wide loop reads better than a blurry
   1920px one.
6. Lazy-load anything below the fold: `preload="metadata"` and don't set
   `autoplay` until an `IntersectionObserver` confirms the video is near
   the viewport, then call `.play()` from the ref.

## Testing

- **Unit** (Vitest/Jest): the pure logic only - the reveal-offset lookup
  table, the streamed-text character-reveal timer, any viewport/media-query
  routing function (mirror `shouldUseCompactScrollStackViewport`'s pattern
  from `scroll-stack` if you add one here).
- **Playwright visual check**: load the page, wait for the hero video's
  `loadeddata` event, screenshot before-and-after the reveal trigger point,
  confirm `prefers-reduced-motion: reduce` (Playwright
  `page.emulateMedia({ reducedMotion: 'reduce' })`) renders final state with
  zero animated properties.
- Confirm autoplay actually fires in a real Chromium/WebKit context, not
  just "the attribute is present" - some of these break silently only on
  real Safari.

## Originality note

Everything above is a *technique* (a named CSS pattern, an ffmpeg encode
recipe, a hook shape) - reimplement each one from scratch with your own
copy, your own color choices, your own footage/screen recordings, and your
own code. Do not fetch, download, or embed natively.software's actual video
files, images, logos, or on-page copy, and do not copy their minified
bundle's markup/class names verbatim - the snippets above are original,
rewritten for a generic React/Tailwind stack, not lifted source.
