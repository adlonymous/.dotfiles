---
title: Footer
slug: footer
status: published
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

The footer is one quiet line and one huge word. On desktop the line holds the bio on the left, the basmala in the dead centre and four small marks on the right, with a live dot matrix filling each gap. Under it, the `salehdigital` wordmark runs edge to edge across the whole window.

## Placement

The footer is the last child of `.site` (a `min-height: 100vh` flex column, see foundations/layout-grid.md). On a short page it sits on the bottom edge of the window; on a long post it follows the last block of the post after the page's 48px bottom padding (40px on phones). Never place it inside `.cols`, and never give it a fixed position.

## Markup

```html
<footer class="foot">
  <div class="foot-row">
    <div class="foot-side">
      <p class="bio">Ahmed Saleh <span lang="ar" dir="rtl">أحمد صالح</span> is a designer-founder in pursuit of the infinite.</p>
      <canvas class="foot-dots" aria-hidden="true"></canvas>
    </div>
    <p class="basmala" lang="ar" dir="rtl">بسم الله الرحمن الرحيم</p>
    <div class="foot-side foot-end">
      <canvas class="foot-dots" aria-hidden="true"></canvas>
      <ul class="foot-links" id="foot-links" aria-label="More" hidden></ul>
      <ul class="marks" id="marks" aria-label="Marks">
        <li><span class="mark" role="img" aria-label="Mark 1" style="--w: 22.4px; --src: url(assets/footer/27-45.png)"></span></li>
        <li><span class="mark" role="img" aria-label="Mark 2" style="--w: 18.6px; --src: url(assets/footer/27-48.png); --soft: 0.42px"></span></li>
        <li><span class="mark" role="img" aria-label="Mark 3" style="--w: 20px; --src: url(assets/footer/27-49.png)"></span></li>
        <li><span class="mark" role="img" aria-label="Mark 4" style="--w: 18px; --src: url(assets/footer/27-50.png)"></span></li>
      </ul>
    </div>
  </div>
  <svg class="wordmark" role="img" aria-label="salehdigital" tabindex="0"><text>salehdigital</text></svg>
</footer>
```

The marks are PNG masks from the owner's site repo, `site/assets/footer/`, **not part of this harness** (two of them are national symbols, not original artwork). They are painted in `--foot` through `mask`, so only their alpha matters:

| File | Size | Bytes | `--w` | What it shows (source comment) |
|---|---|---|---|---|
| `27-45.png` | 90 × 80 | 816 | 22.4px | a swoosh with a sparkle: a long tapering diagonal stroke rising to the right, with a small four-point star above its tip |
| `27-48.png` | 78 × 84 | 8068 | 18.6px, `--soft` .42px | an interlocking knot: a rosette of six looped bands woven around a centre |
| `27-49.png` | 80 × 80 | 1594 | 20px | the emblem of Oman: a khanjar dagger over two crossed swords |
| `27-50.png` | 72 × 80 | 1048 | 18px | a maple leaf |

Every mark is 20px tall and 8px apart, 8px in from the side. At rest it is a hair soft (`blur(soft + .55px)` through `#ink-mark`); on hover it resolves sharp through the field, or through the GL footer pass's `markHover`. Their labels are "Mark 1" to "Mark 4" (`role="img"`). They are decorative for now. Without them, leave the `<li>`s empty-masked (a mask that fails to load paints nothing) or drop the list; do not draw substitutes.

## CSS

```css
.foot { padding: 0; color: var(--foot); }            /* --foot is --ink in light and dark */
.foot-row { display: grid; grid-template-columns: minmax(min-content, 1fr) auto minmax(min-content, 1fr); align-items: end; column-gap: 0; row-gap: 10px; }
.foot-side { display: flex; align-items: flex-end; column-gap: 0; min-width: 0; }
.foot-end { display: flex; align-items: flex-end; column-gap: 0; row-gap: 10px; margin-left: 0; }
.bio { margin: 0; padding: 0 0 0 12px; white-space: nowrap; line-height: 19.2px; filter: url(#ink-bio); }
.bio [lang="ar"] { unicode-bidi: isolate; }
.basmala { margin: 0; font: 300 18px/19.2px "Kufigraph", var(--ui); letter-spacing: 0; white-space: nowrap; filter: url(#ink-bas); }
.foot-dots { flex: 1 1 0; width: 0; min-width: 12px; height: 19.2px; align-self: flex-end; display: block; filter: url(#ink-dots); }
.marks { list-style: none; display: flex; align-items: flex-end; gap: 8px; margin: 0; padding: 0 8px; }
.mark { display: block; height: 20px; width: var(--w); background: currentColor;
  -webkit-mask: var(--src) center / contain no-repeat; mask: var(--src) center / contain no-repeat;
  filter: url(#ink-mark) blur(calc(var(--soft, 0px) + .55px)); }
.wordmark { display: block; width: 100%; height: 97px; overflow: hidden; user-select: none; outline: none; }
.wordmark text { font-family: "Kult Luxury"; letter-spacing: 0; fill: var(--foot); filter: url(#ink-ui); }

@media (max-width: 899px) {
  .bio { padding: 0 12px; width: auto; max-width: calc(310px + 12px); white-space: normal; }
  .foot-end { flex: 1 1 100%; justify-content: space-between; padding-left: 12px; }
  .foot-dots { display: none; }
  .foot-row { grid-template-columns: 1fr auto; row-gap: 10px; }
  .foot-row > .foot-side:first-child { grid-column: 1 / -1; }
  .basmala { padding-left: 12px; justify-self: start; }
}
```

On phones the bio wraps to two lines (max 310px of text), the basmala goes under it on the left, the marks stay right, and the dot strips are hidden.

## The wordmark fit (js/app.js `fitWordmark`)

The word is fitted so its ink spans the window minus 6px on each side, and the svg is cropped just under the baseline so the descender of the g is cut off by the page edge:

```js
function fitWordmark(svg) {
  const W = document.documentElement.clientWidth, side = 6, top = W < 900 ? 8 : 6;
  const ctx = document.createElement('canvas').getContext('2d');
  ctx.font = '400 100px "Kult Luxury"';
  const m = ctx.measureText('salehdigital');
  const inkW = m.actualBoundingBoxLeft + m.actualBoundingBoxRight;
  const k = (W - side * 2) / inkW, size = 100 * k;
  const asc = m.actualBoundingBoxAscent * k, pad = Math.max(3, asc * 0.088);
  const H = Math.round(top + asc + pad);
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.setAttribute('width', W); svg.setAttribute('height', H); svg.style.height = H + 'px';
  const t = svg.querySelector('text');
  t.setAttribute('x', (side + m.actualBoundingBoxLeft * k).toFixed(2));
  t.setAttribute('y', (top + asc).toFixed(2));
  t.setAttribute('font-size', size.toFixed(3));
}
// run after fonts load and on resize: document.fonts.ready.then(() => fitWordmark(svg)); addEventListener('resize', ...)
```

On the live site a WebGL pass redraws the bio, basmala, dot strips and wordmark in the same place (and lets the wordmark react to hover); the DOM above is the exact fallback and has the same geometry.

## The dot strips (js/footdots.js)

Each `.foot-dots` canvas (index `R` = 0 for the left strip, 1 for the right) draws a grid of dots in the footer colour on a 4.8px pitch. A dot's radius grows from 0.45px to 1.7px inside a few soft blobs defined by a signed distance field; the blobs drift with time and one follows the pointer. One frame, as shipped:

```js
function drawDots(cv, R, time = 0) {
  const rect = cv.getBoundingClientRect(), s = rect.width, h = rect.height, dpr = Math.min(2, devicePixelRatio || 1);
  cv.width = Math.round(s * dpr); cv.height = Math.round(h * dpr);
  const a = cv.getContext('2d'); a.setTransform(dpr, 0, 0, dpr, 0, 0); a.fillStyle = getComputedStyle(cv).color;
  const u = 4.8, big = 1.7, small = .45;
  const smin = (p, q, k) => { const e = Math.max(k - Math.abs(p - q), 0) / k; return Math.min(p, q) - e * e * k * .25; };
  const sdf = (x, y) => { let e = 1e9; const C = Math.max(2, Math.round(s / 140));
    for (let m = 0; m < C; m++) { const l = m * 2.399 + R * 1.3;
      const f = ((m + .5) / C + .06 * Math.sin(time * .21 + l)) * s, M = h * (.5 + .35 * Math.sin(time * .33 + l * 1.7));
      const p = 5 + 4 * (.5 + .5 * Math.sin(time * .27 + l * .9));
      e = smin(e, Math.hypot((x - f) * .55, y - M) - p, 10); }
    return e; };   // the live site also unions a 7px blob at the pointer: smin(e, hypot(x - px, y - py) - 7, 14)
  const n = Math.floor(s / u), rows = Math.floor(h / u), ox = (s - (n - 1) * u) / 2, oy = (h - (rows - 1) * u) / 2;
  a.beginPath();
  for (let j = 0; j < rows; j++) for (let i = 0; i < n; i++) { const X = ox + i * u, Y = oy + j * u;
    const g = 1 - Math.min(1, Math.max(0, (sdf(X, Y) + 2) / 8)), r = small + (big - small) * g * g * (3 - 2 * g);
    a.moveTo(X + r, Y); a.arc(X, Y, r, 0, Math.PI * 2); }
  a.fill();
}
```

Animated, `time` is seconds since load times `0.4 + 1.2 * --fnd-energy`; under reduced motion it stays 0.

## What the live footer looks like today

- **Basmala face.** The CSS names Kufigraph Light with `font-display: optional`, and the WebGL footer snapshots the text with whatever face is ready. In practice visitors see the system Arabic fallback (a Naskh-style face), not the square Kufic of Kufigraph. To match the live look, do not load Kufigraph. Kufigraph's license is not covered by this repo either.
- **Phone wordmark.** Until the 2026-11-11 sync, at 390 wide the live footer read "salehdigi" (Kult Luxury was `font-display: optional`, so the DOM fell back to a wider serif while the canvas measured Kult). Kult is now `font-display: block` and the whole word fits at 390 (font-size 29.702). See [webgl](../../foundations/motion/webgl.md) › Mobile overflow.

## Rules

- Bio copy exactly: "Ahmed Saleh أحمد صالح is a designer-founder in pursuit of the infinite."
- No links, columns of links, social icons or copyright line in the footer.
- The wordmark is always the full window width and always last on the page.
