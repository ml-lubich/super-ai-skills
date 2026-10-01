---
name: ui-principles
description: Basic layout and UX rules to check before shipping ANY visual output - web pages, READMEs, generated SVG/cards, dashboards, PDFs, slides. Use whenever you add, remove or rearrange items in a grid, card list, table or README section, or generate an image/SVG that people will see.
---

# UI principles — the baseline

Taste is optional; these are not. Run the checklist on every visual change.

## Layout

1. **No orphans.** A grid whose last row is short looks broken. Center the
   remainder (1 of 2 → middle; 2 of 3 → centered pair), or change the count/columns
   so rows fill. Never leave one card hanging on the left beside an empty cell —
   no awkward dead space anywhere. Check this even when the count comes from data
   (it changes: 12 cards today, 13 tomorrow). CSS grid can't center a partial row;
   use `flex flex-wrap justify-center` with explicit item widths
   (`md:w-[calc(50%-gap/2)]`), and pin it with a test: last item's center == row center.
2. **Balance and alignment.** Items in a row share a baseline, height and padding.
   Edges line up with the column they belong to.
3. **Size to content.** Containers grow with their items (compute height from
   count), never a fixed height that clips or leaves a dead band.
4. **Nothing overflows.** No horizontal scroll, no text cut off at the edge, no
   code block wider than its column. Wrap, shorten, or drop it.
5. **Consistent spacing.** One gap value per level (cards, sections). Uneven gaps
   read as mistakes.

## Content

6. **Say it once.** If an image/card already shows it, don't repeat it in a text
   block underneath. Duplicate content is clutter.
7. **Hierarchy.** One primary thing per section; headings, then detail. Don't
   stack a heading + an image whose own header repeats the heading unless intended.
8. **Counts stay true.** Any "N tools / N items" badge, stat or alt text matches
   the actual list after every add/remove.

## Verify

9. Look at the rendered result at the real width (GitHub ~ 830–1280 px, phone
   390 px) — dark and light if both exist. Markup correctness is not a pass.
10. State the visual done-condition first ("13 cards, 2 cols, last card centered")
    and pass only when the screenshot shows it.
