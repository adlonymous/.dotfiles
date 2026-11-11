---
title: Book spine
slug: spine
status: published
description: "A Library book standing spine-out: the cover colour, title/names/year fitted along it, a rounded spine shade and hairline edge."
chips:
  - Component
  - Library
  - WebGL
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:07:17Z
---

In the Library's "Spines" grid ([bookshelf](../patterns/bookshelf.md)) every book stands spine-out:

- **Size:** height `round(236 + 82 × (.5f + .5·hash(slug + 'h')))` px, thickness `round(20 + 24 × hash(slug + 't'))` px, depth from the cover's aspect.
- **Colour:** the cover's dominant colour, weighted toward the band beside the spine, sampled on a 48 × 64 canvas. `--fnd-spine-tone` (.85) mixes from plain paper (0) to the cover's own colour (1).
- **Type:** fitted along the spine: the title, then the names (full if they fit, else surnames), then the year. A thick spine gets two lines, balanced at a word. Titles are in the theme's ink or paper, whichever reads on the spine colour, and set in Inter Display, with the year in the mono face (`"ABC Favorit Mono Trial", ui-monospace, Menlo, monospace`).
- **Shading:** a rounded spine, a touch darker toward its two edges and lit a little more as it tips out, plus a hairline at the edge so a paper-coloured book still reads.
- **Leans:** a few books lean on a neighbour (`LEANS = { 6: [-1, .13], 15: [-1, .17], 23: [1, .15] }`: index, direction, amount).

Source: `site/js/grids/spines.js`, lines 1 to 146

```js
// Library, "Spines" (concept by Wren). The books stand spine-out on shelves, in order, each
// shelf filled to the column's width (one shelf that scrolls sideways on a phone). The DOM lays
// out every slot (thickness, height, lean) and keeps focus and hits; one three.js canvas
// under the page draws the books on those slots. Hover or focus tips a spine out; a click
// pulls the book, turns it to its cover and lands it under its slot, its details beside it
// as plain text (fillDetails, no modal). Click it again, its cover, anywhere away, or Escape returns it.
import { root, reduced, loadThree, readFnd, gridCanvas, lifetime, disposeGL } from './common.js';
import { onTheme } from '../theme.js';

// ---------- helpers ----------
const hash = (str) => { let h = 2166136261; for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return ((h >>> 0) % 10000) / 10000; };
const clamp01 = (x) => Math.min(1, Math.max(0, x));
const smooth = (x) => { x = clamp01(x); return x * x * (3 - 2 * x); };
const smoother = (x) => { x = clamp01(x); return x * x * x * (x * (x * 6 - 15) + 10); };
const lerp = (a, b, t) => a + (b - a) * t;
// colours here are sRGB 0..1 triples, as js/theme.js gives them
const lin = (c) => c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
const lum = ([r, g, b]) => 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
const contrast = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
const mixRGB = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
// the spine's type: the theme's ink or paper, whichever reads on it
const typeOn = (bg, th) => contrast(bg, th.ink) >= contrast(bg, th.paper) ? th.ink : th.paper;

function loadImage(src) {
  return new Promise((res) => {
    if (!src) return res(null);
    const im = new Image(); im.decoding = 'async'; im.onload = () => res(im); im.onerror = () => res(null); im.src = src;
  });
}

// the spine's colour: the cover's dominant colour, weighted toward the band beside the spine
function sampleColour(img) {
  const W = 48, H = 64, c = document.createElement('canvas'); c.width = W; c.height = H;
  const x = c.getContext('2d', { willReadFrequently: true }); x.drawImage(img, 0, 0, W, H);
  let d; try { d = x.getImageData(0, 0, W, H).data; } catch { return [0.86, 0.86, 0.86]; }
  const bins = new Map();
  for (let y = 0; y < H; y++) for (let xx = 0; xx < W; xx++) {
    const i = (y * W + xx) * 4, r = d[i], g = d[i + 1], b = d[i + 2];
    const key = (r >> 5) << 6 | (g >> 5) << 3 | (b >> 5);
    const w = xx < W * 0.2 ? 3 : 1;
    const e = bins.get(key) || { n: 0, r: 0, g: 0, b: 0 };
    e.n += w; e.r += r * w; e.g += g * w; e.b += b * w; bins.set(key, e);
  }
  let best = null; for (const e of bins.values()) if (!best || e.n > best.n) best = e;
  return [best.r / best.n / 255, best.g / best.n / 255, best.b / best.n / 255];
}

// the names on a spine: full if they fit, else the surnames
function surnames(desc) {
  const clean = desc.replace(/\s*\(.*?\)\s*/g, ' ').trim();
  return clean.split(/\s+(?:and|with)\s+|,\s*/).map(n => n.trim().split(/\s+/).pop()).join(' and ');
}

// the base leans: a few books rest against their neighbour (-1 tops to the right, +1 to the left)
const LEANS = { 6: [-1, 0.13], 15: [-1, 0.17], 23: [1, 0.15] };

// ---------- the spine's type: fit title, names and year along the spine ----------
const UI = '"Inter Display", "Helvetica Neue", Arial, sans-serif';
const MONO = '"ABC Favorit Mono Trial", ui-monospace, Menlo, monospace';
let mctx = null;
function measure(t, size, fam = UI, ls = -0.3) {
  mctx ||= document.createElement('canvas').getContext('2d');
  mctx.font = `400 ${size}px ${fam}`; mctx.letterSpacing = `${ls}px`; return mctx.measureText(t).width;
}
function layoutSpine(rec, T, H) {
  const year = rec.chips[0] || '';
  const avail = H - 12 - 10 - (year ? measure(year, 9, MONO, 0) + 12 : 0);
  const full = rec.desc.replace(/\s*\(.*?\)\s*/g, ' ').trim(), sur = surnames(rec.desc);
  const main = rec.title.split(':')[0];
  const fits = (title, size, by) => measure(title, size) + (by ? 10 + measure(by, 11, UI, -0.2) : 0) <= avail;
  for (const [title, size, by] of [[rec.title, 13, full], [rec.title, 13, sur], [rec.title, 12, sur], [main, 13, sur], [main, 12, sur], [rec.title, 13, '']]) {
    if (fits(title, size, by)) return { title: [title], size, by };
  }
  // two lines on a thick spine, balanced at a word
  if (T >= 30) {
    const w = rec.title.split(' '); let best = null;
    for (let k = 1; k < w.length; k++) {
      const l = [w.slice(0, k).join(' '), w.slice(k).join(' ')];
      const m = Math.max(measure(l[0], 12), measure(l[1], 12));
      if (!best || m < best.m) best = { l, m };
    }
    if (best && best.m + 10 + measure(sur, 11, UI, -0.2) <= avail) return { title: best.l, size: 12, by: sur };
    if (best && best.m <= avail) return { title: best.l, size: 12, by: '' };
  }
  return { title: [main], size: 12, by: '', clip: true };
}
// the mask the shader colours: white type on clear, its alpha the type's weight
function spineMask(bk, R) {
  const { T, H, spine, year } = bk;
  const c = document.createElement('canvas'); c.width = Math.ceil(T * R); c.height = Math.ceil(H * R);
  const x = c.getContext('2d'); x.scale(R, R);
  x.translate(T, 0); x.rotate(Math.PI / 2);           // local x runs down the spine, glyph tops face right
  const mid = T / 2;
  const lines = spine.title, lh = spine.size + 2;
  x.fillStyle = '#fff';
  x.font = `400 ${spine.size}px ${UI}`; x.letterSpacing = '-0.3px';
  let end = 12;
  lines.forEach((t, k) => {
    const y = mid + (k - (lines.length - 1) / 2) * lh + spine.size * 0.34;
    let s = t;
    if (spine.clip) { const max = H - 34; while (s.length > 3 && x.measureText(s + '…').width > max) s = s.slice(0, -1); if (s !== t) s = s.trimEnd() + '…'; }
    x.fillText(s, 12, y); end = Math.max(end, 12 + x.measureText(s).width);
  });
  if (spine.by) {
    x.globalAlpha = 0.62; x.font = `400 11px ${UI}`; x.letterSpacing = '-0.2px';
    x.fillText(spine.by, end + 10, mid + 11 * 0.34);
  }
  if (year) {
    x.globalAlpha = 0.5; x.font = `400 9px ${MONO}`; x.letterSpacing = '0px';
    x.fillText(year, H - 10 - x.measureText(year).width, mid + 9 * 0.34);
  }
  return c;
}

const SPINE_VERT = /* glsl */`
  varying vec2 vUv;
  void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;
const SPINE_FRAG = /* glsl */`
  uniform sampler2D uMask;
  uniform vec3 uColor, uInk;
  uniform vec2 uSize;
  uniform float uTip, uEdge;
  varying vec2 vUv;
  void main() {
    vec2 p = vUv * uSize;
    // a rounded spine: a touch darker toward its two edges, lit a little more as it tips out
    float u = abs(vUv.x - 0.5) * 2.0;
    vec3 col = uColor * (1.0 - 0.07 * u * u) * (1.0 + 0.04 * uTip);
    // a hairline at the spine's edge, so a book the colour of the paper still reads on it
    float e = min(min(p.x, uSize.x - p.x), min(p.y, uSize.y - p.y));
    col = mix(col, uInk, uEdge * (1.0 - smoothstep(0.0, 1.2, e)));
    float a = texture2D(uMask, vUv).a;
    col = mix(col, uInk, a);
    gl_FragColor = vec4(col, 1.0);
    #include <colorspace_fragment>
  }`;

export async function mount({ col, recs, title, fillDetails, signal }) {
  const life = lifetime(signal);
  const P = { 'spine-order': 0.4, 'spine-depth': 0.45, 'spine-tone': 0.85, energy: 0.5 };
  readFnd(P);
  let S = 1;
  const readScale = () => { S = parseFloat(getComputedStyle(wrap).getPropertyValue('--spine-s')) || 1; };
  let TH = { paper: [1, 1, 1], ink: [0, 0, 0] };
```
