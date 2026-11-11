---
title: Dot-matrix button
slug: dot-matrix-button
status: published
description: "The viewer and card buttons (prev, next, close): a 7x7 field of dots sized by their SDF distance to the glyph, breathing slowly, blooming on hover."
chips:
  - Component
  - Button
  - SDF
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:07:17Z
---

Used for the full-screen viewer's and the book card's **prev / next / close** buttons (`.viewer-btn`, 40 × 40px, 10px radius). The glyph is a 7 × 7 field of `<circle r="1.6">` on a 4px pitch in a 28 × 28 viewBox. Each dot is sized by its distance `d` to the glyph's line segments (an SDF):

- `--k`: on the glyph, quantised to 1, .4 or 0.
- `--h`: the halo, `1 − d/1.9`.
- `--o`: ripple order, the distance from the centre.
- `--r`: a per-dot random.

At rest a dot is `scale(.3 + .62k)` at opacity `.16 + .7k`. On hover the halo blooms out from the centre, 14ms per ring over 280ms. A slow breathing wave runs at all times (2.8 to 3.6s a cycle, quicker on hover: 1.1 to 1.4s). A press scales the svg to .9. In Marathon the dots take the accent on hover. Under reduced motion there are no transitions and no animation.

Source: `site/js/gallery.js`, lines 179 to 201

```js
// ---------- dot-matrix icons: a 7x7 field of dots, each sized by its distance to the glyph (an SDF) ----------
const SEGS = {
  prev: [[[1, -3], [-2, 0]], [[-2, 0], [1, 3]]],
  next: [[[-1, -3], [2, 0]], [[2, 0], [-1, 3]]],
  close: [[[-2, -2], [2, 2]], [[2, -2], [-2, 2]]],
};
const segDist = (px, py, [[ax, ay], [bx, by]]) => {
  const dx = bx - ax, dy = by - ay;
  const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)));
  return Math.hypot(px - ax - t * dx, py - ay - t * dy);
};
export function dotIcon(kind) {
  let dots = '';
  for (let y = -3; y <= 3; y++) for (let x = -3; x <= 3; x++) {
    const d = Math.min(...SEGS[kind].map(s => segDist(x, y, s)));
    const k0 = 1 - (d - 0.45) / 0.5, k = k0 >= 0.75 ? 1 : k0 >= 0.25 ? 0.4 : 0; // on the glyph, quantised to on / half / off
    const h = Math.max(0, Math.min(1, 1 - d / 1.9));                // the halo around it
    const o = Math.round(Math.hypot(x, y) * 10) / 10;               // ripple order from the centre
    dots += `<circle cx="${14 + x * 4}" cy="${14 + y * 4}" r="1.6" style="--k:${k.toFixed(2)};--h:${h.toFixed(2)};--o:${o};--r:${Math.random().toFixed(2)}"/>`;
  }
  return `<svg class="dm" viewBox="0 0 28 28" aria-hidden="true">${dots}</svg>`;
}
```


Source: `site/css/site.css`, lines 569 to 582

```css
/* dot-matrix buttons: each dot scaled by its SDF distance to the glyph; hover blooms the halo out from the centre */
.viewer-btn { width: 40px; height: 40px; border-radius: 10px; color: var(--ink); }
.viewer-btn svg.dm { width: 28px; height: 28px; overflow: visible; transition: transform 160ms var(--ease-land); }
.viewer-btn .dm circle { fill: currentColor; transform-box: fill-box; transform-origin: center;
  transform: scale(calc(.3 + .62 * var(--k))); opacity: calc(.16 + .7 * var(--k));
  transition: transform 280ms var(--ease-land) calc(var(--o) * 14ms), opacity 280ms var(--ease-land) calc(var(--o) * 14ms); }
.viewer-btn:hover, .viewer-btn:focus-visible { background: none; }
.viewer-btn:hover .dm circle, .viewer-btn:focus-visible .dm circle { transform: scale(calc(.34 + .7 * var(--k) + .16 * var(--h))); opacity: calc(.22 + .8 * var(--k) + .2 * var(--h)); }
.viewer-btn:active svg.dm { transform: scale(.9); }
.viewer-btn:focus-visible { outline: 1px dotted var(--ring); outline-offset: 2px; }
/* Marathon: the dots take the accent on hover */
[data-theme^="marathon"] .viewer-btn:hover, [data-theme^="marathon"] .viewer-btn:focus-visible { color: var(--accent-mark); }
@media (prefers-reduced-motion: reduce) { .viewer-btn .dm circle, .viewer-btn svg.dm { transition: none; } }
```


Source: `site/css/site.css`, lines 748 to 753

```css
/* the dot-matrix icons are alive: a slow wave breathes out from the centre through the field, each dot a little off-beat, and the halo shimmers. Hover quickens it. */
@keyframes dm-breathe { 0%, 100% { scale: 1; } 50% { scale: calc(1 + .22 * var(--k) + .9 * var(--h) * (1 - var(--k)) + .35 * (1 - var(--h))); } }
.viewer-btn .dm circle { animation: dm-breathe calc(2.8s + var(--r) * .8s) ease-in-out infinite; animation-delay: calc(var(--o) * -260ms - var(--r) * 400ms); }
.viewer-btn:hover .dm circle, .viewer-btn:focus-visible .dm circle { animation-duration: calc(1.1s + var(--r) * .3s); }
.info-chips:empty { display: none; }
@media (prefers-reduced-motion: reduce) { .viewer-btn .dm circle { animation: none; } }
```
