---
title: Wordmark
slug: wordmark
status: published
description: salehdigital logotype and dot matrix rendering.
chips:
  - Brand
  - SDF
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

`salehdigital`, all lowercase, one word, set in **Kult Luxury** and fitted to the full width of the window at the very bottom of every page. There is no logo, icon or wordmark anywhere else (the top of the page is just the menu).

> **Licensing.** Kult Luxury is a commercial typeface. It is not in this repository or the npm packages. Buy your own license, or set the word in a fallback serif. Never commit or base64 the font.

## Geometry

- Ink of the word spans `clientWidth - 12px` (6px in from each side).
- Top padding 6px on desktop, 8px below 900px.
- The svg is cropped `max(3px, ascent * 0.088)` under the baseline, so descenders (the g) run off the bottom of the page.
- Fill is `var(--foot)`; the text gets `filter: url(#ink-ui)`.

The exact fitting function and markup are in `components/patterns/footer.md` ("The wordmark fit"). At 1440 wide this gives a word roughly 250px tall; at 390 wide roughly 70px.

## Live rendering

On the live site a WebGL pass (three.js) draws the wordmark into the page canvas `#gl` in the same rectangle, hides the DOM text (`.gl .wordmark text { fill: transparent; }`), and adds a hover where letters resolve one by one; holding it swaps to the Arabic name. A static rebuild uses the DOM svg, which has the same geometry.

## Rules

- Never shrink the wordmark into a centred logo or put it in the header.
- Never letter-space it; `letter-spacing: 0`.
- Lowercase only.
