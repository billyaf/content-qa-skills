---
name: visual-qa
description: Technical and aesthetic QA of social-media designs (PNG/JPG) against a brand file before they are shown to the owner. Checks canvas size, palette share, a single off-brand colour taking over, spacing rhythm between blocks, large dead areas and elements touching the side margins, then guides a visual review. Use after a designer exports PNGs, or when someone asks "is this ready?" or "why does this feel off?".
---

# Visual QA

1. Run `python3 <skill>/scripts/tech_check.py --brand brand.json <png ...>`.
2. Read the result per image:
   - **Size FAIL**: wrong canvas. Re-export it.
   - **Palette FAIL**: one off-palette colour covers ≥ 25 % of the canvas, usually a background copied from the brief. A low palette share alone is fine for photo-led designs.
   - **Rhythm CHECK**: one gap is far larger than the median gap. Check that the space is intentional; on a 9:16 story the bottom is often kept empty for the platform UI.
   - **Dead area CHECK**: a large connected empty area. Balance the layout, or confirm it is breathing room.
   - **Margin CHECK**: text-coloured pixels in the outer 60 px. Something is probably outside the column.
3. Then look at every image yourself: hierarchy (one focal point), contrast of text over photos, logo and footer present, nothing in the platform's UI zones.
4. Write `qa.md` with OK/CHECK/FAIL per image, what to fix, and what was accepted on purpose.

Calibrate `brand.json` (`palette`, `background`, `edgeColors`, `contentColumn`) from approved designs rather than guessing.
