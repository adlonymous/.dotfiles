---
title: Texture
slug: texture
status: published
description: Grain, ink, and paper texture effects.
chips:
  - Foundation
  - Materials
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

The page is meant to read like ink on paper, not pixels on glass. Two things make that happen, and a rebuild that skips either one looks flat and wrong next to the live site:

1. **Ink filters**: every piece of type and every diagram passes through an SVG filter that displaces it a hair, bleeds it a little and (for the footer and diagrams) knocks out grain-shaped specks.
2. **Grain**: one fixed noise layer over the whole window, above everything, that jitters 12 times a second.

## 1. Ink filters

Put this `<svg>` first in `<body>`, exactly as shipped:

```html
<svg class="defs" width="0" height="0" aria-hidden="true" focusable="false">
  <filter id="ink-ui" x="-4%" y="-25%" width="108%" height="150%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="0.7" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="0.22" result="b"/>
    <feComponentTransfer in="b"><feFuncA type="linear" slope="1.34" intercept="0"/></feComponentTransfer>
  </filter>
  <filter id="ink-bio" x="-2%" y="-30%" width="104%" height="160%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="1.8" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="0.3" result="b"/>
    <feComponentTransfer in="b" result="i"><feFuncA type="linear" slope="1.8" intercept="0"/></feComponentTransfer>
    <feTurbulence type="fractalNoise" baseFrequency="2.4" numOctaves="1" seed="11" result="g"/>
    <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.4 0 0 0 1.6" result="gm"/>
    <feComposite in="i" in2="gm" operator="in"/>
  </filter>
  <filter id="ink-diagram" x="-1%" y="-2%" width="102%" height="104%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="1.2" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="0.25" result="b"/>
    <feComponentTransfer in="b" result="i"><feFuncA type="linear" slope="1.6" intercept="0"/></feComponentTransfer>
    <feTurbulence type="fractalNoise" baseFrequency="2.4" numOctaves="1" seed="11" result="g"/>
    <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.1 0 0 0 1.5" result="gm"/>
    <feComposite in="i" in2="gm" operator="in"/>
  </filter>
  <!-- ink-bas (basmala), ink-mark (footer marks) and ink-dots (footer dot strips) are byte-for-byte copies of ink-bio
       with ids "ink-bas", "ink-mark", "ink-dots"; ink-bas and ink-dots use x="-2%" y="-40%" width="104%" height="180%",
       ink-mark uses x="-20%" y="-20%" width="140%" height="140%" -->
  <filter id="ink-body" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="1" seed="3" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="0.24" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="0.1" result="b"/>
    <feComponentTransfer in="b"><feFuncA type="linear" slope="1.12" intercept="0"/></feComponentTransfer>
  </filter>
</svg>
```

Where each filter goes:

| Filter | Applied to |
| --- | --- |
| `#ink-ui` | every `.item` (menu and page titles), `.col-meta`, `.nav-btn`, `.foot-links`, the wordmark text |
| `#ink-body` | every direct child of the article except embeds: `.col-body article > :not(.embed) { filter: url(#ink-body); }` |
| `#ink-bio` | `.bio` in the footer |
| `#ink-bas` | `.basmala` |
| `#ink-dots` | `.foot-dots` canvases |
| `#ink-mark` | `.mark` (with a resting `blur(calc(var(--soft, 0px) + .55px))`) |
| `#ink-diagram` | `.hd-canvas, .hf-canvas, .hf-toggle` (the diagrams and the Before/After switch) |

Images and screenshots inside embeds are never filtered; they stay sharp.

## 2. Grain

A 256 x 256 device-pixel noise tile, drawn once on a 2D canvas, repeated on a fixed `<div id="grain">` appended to `<body>`. It sits above everything (`z-index: 11`) and never takes pointer events.

```css
#grain {
  position: fixed; left: 0; top: 0; z-index: 11; pointer-events: none;
  background-repeat: repeat; image-rendering: pixelated; will-change: transform;
  opacity: calc((0.01 + 0.05 * var(--fnd-texture)) * var(--grain-k) / 0.45);  /* --fnd-texture .4, --grain-k 1 (light) => 0.0667 */
}
@media print { #grain { display: none; } }
```

```js
// the shipped recipe (js/grain.js); ink/paper are the theme's colours as 0..1 RGB
const TILE = 256, FPS = 12, GRAIN_K = 0.45;
function makeTile(ink = [0, 0, 0], paper = [1, 1, 1]) {
  const I = ink.map(v => Math.round(v * 255)), P = paper.map(v => Math.round(v * 255));
  const c = document.createElement('canvas'); c.width = c.height = TILE;
  const x = c.getContext('2d'), img = x.createImageData(TILE, TILE), d = img.data;
  const half = TILE / 2, coarse = new Float32Array(half * half);
  for (let i = 0; i < coarse.length; i++) coarse[i] = Math.random();
  for (let y = 0; y < TILE; y++) for (let xx = 0; xx < TILE; xx++) {
    const g = Math.random(), g2 = coarse[(y >> 1) * half + (xx >> 1)];
    const v = g * 0.8 + g2 * 0.2, light = g >= 0.93;
    const a = light ? 2.2 * GRAIN_K : GRAIN_K * Math.pow(v, 1.7);
    const i = (y * TILE + xx) * 4, col = light ? P : I;
    d[i] = col[0]; d[i + 1] = col[1]; d[i + 2] = col[2]; d[i + 3] = Math.round(Math.min(1, a) * 255);
  }
  x.putImageData(img, 0, 0);
  return c;
}
function startGrain() {
  const el = document.createElement('div'); el.id = 'grain'; el.setAttribute('aria-hidden', 'true');
  document.body.append(el);
  makeTile().toBlob(b => { el.style.backgroundImage = `url(${URL.createObjectURL(b)})`; });
  const dpr = window.devicePixelRatio || 1, t = TILE / dpr;
  el.style.backgroundSize = `${t}px ${t}px`;
  el.style.width = `calc(100vw + ${t}px)`; el.style.height = `calc(100vh + ${t}px)`;
  const jump = () => { const ox = Math.floor(Math.random() * TILE) / dpr, oy = Math.floor(Math.random() * TILE) / dpr;
    el.style.transform = `translate3d(${-ox}px, ${-oy}px, 0)`; };
  jump();
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) setInterval(jump, 1000 / FPS);
}
startGrain();
```

The live script also pauses the jitter while the tab is hidden or unfocused and rebuilds the tile when the theme changes (dark specks on light paper, light specks on dark paper).

`--grain-k` per theme: light 1, dark 1.5, marathon-dark 1.4, marathon-light 1.1 (see colors and themes).

## Paper

There is no paper image. The paper is the flat `--paper` colour (`#fff` in light) plus the grain above. Do not add a background texture image.

## Source (verbatim)

Source: `site/js/grain.js`, whole file

```js
// The paper and screen grain, out of WebGL. One 256 px noise tile, made once on
// a 2D canvas with the same recipe the old shader used (dark specks on paper, a
// few light ones that only show inside ink), sits on a fixed layer above the
// page, one tile pixel to one device pixel. About 12 times a second the layer
// jumps to a new random whole-device-pixel offset: a compositor-only move, so
// there is no repaint and no shader. Its strength follows --fnd-texture in CSS
// (css/site.css #grain). Still while the window is hidden or unfocused, or for
// reduced motion; absent with ?lite.
import { reducedMotion, LITE } from './state.js';
import { onTheme } from './theme.js';

const TILE = 256;            // device px
const FPS = 12;
export const GRAIN_K = 0.45; // alpha baked into the tile; CSS opacity = amount / GRAIN_K

// The specks are the theme's ink, the few bright ones its paper: dark specks on
// white, light specks on dark paper. Rebuilt when the theme changes.
function makeTile(ink = [0, 0, 0], paper = [1, 1, 1]) {
  const I = ink.map(v => Math.round(v * 255)), P = paper.map(v => Math.round(v * 255));
  const c = document.createElement('canvas'); c.width = c.height = TILE;
  const x = c.getContext('2d');
  const img = x.createImageData(TILE, TILE), d = img.data;
  const half = TILE / 2, coarse = new Float32Array(half * half);
  for (let i = 0; i < coarse.length; i++) coarse[i] = Math.random();
  for (let y = 0; y < TILE; y++) for (let xx = 0; xx < TILE; xx++) {
    const g = Math.random(), g2 = coarse[(y >> 1) * half + (xx >> 1)];
    const v = g * 0.8 + g2 * 0.2;
    const light = g >= 0.93;
    const a = light ? 2.2 * GRAIN_K : GRAIN_K * Math.pow(v, 1.7);
    const i = (y * TILE + xx) * 4;
    const c = light ? P : I;
    d[i] = c[0]; d[i + 1] = c[1]; d[i + 2] = c[2];
    d[i + 3] = Math.round(Math.min(1, a) * 255);
  }
  x.putImageData(img, 0, 0);
  return c;
}

export function startGrain() {
  if (LITE) return null;
  const el = document.createElement('div');
  el.id = 'grain'; el.setAttribute('aria-hidden', 'true');
  document.body.append(el);
  let url = '';
  onTheme((c) => makeTile(c.ink, c.paper).toBlob((b) => {
    if (!b) return;
    const prev = url; url = URL.createObjectURL(b);
    el.style.backgroundImage = `url(${url})`;
    if (prev) URL.revokeObjectURL(prev);
  }));

  let dpr = 1, timer = 0;
  function size() {
    dpr = window.devicePixelRatio || 1;
    const t = TILE / dpr;
    el.style.backgroundSize = `${t}px ${t}px`;
    el.style.width = `calc(100vw + ${t}px)`; el.style.height = `calc(100vh + ${t}px)`;
  }
  function jump() {
    const ox = Math.floor(Math.random() * TILE) / dpr, oy = Math.floor(Math.random() * TILE) / dpr;
    el.style.transform = `translate3d(${-ox}px, ${-oy}px, 0)`;
  }
  function sync() {
    const run = !document.hidden && document.hasFocus() && !reducedMotion.matches;
    if (run && !timer) timer = setInterval(jump, 1000 / FPS);
    if (!run && timer) { clearInterval(timer); timer = 0; }
  }
  size(); jump(); sync();
  window.addEventListener('resize', size);
  ['focus', 'blur'].forEach(t => window.addEventListener(t, sync));
  document.addEventListener('visibilitychange', sync);
  reducedMotion.addEventListener?.('change', sync);
  return el;
}
```


Source: `site/css/site.css`, lines 31 to 41

```css
/* the one canvas: above everything, never in the way */
#gl { position: fixed; inset: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 10; }
/* the grain (js/grain.js): a noise tile at one device pixel per texel, over
   everything; 0.45 is the alpha baked into the tile (GRAIN_K) */
#grain {
  position: fixed; left: 0; top: 0; z-index: 11; pointer-events: none;
  background-repeat: repeat; image-rendering: pixelated; will-change: transform;
  opacity: calc((0.01 + 0.05 * var(--fnd-texture)) * var(--grain-k) / 0.45);
}
@media print { #gl, #grain { display: none; } }
```
