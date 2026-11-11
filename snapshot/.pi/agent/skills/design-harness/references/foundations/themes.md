---
title: Themes
slug: themes
status: published
description: "Four themes and twelve named palettes, picked in Settings, stored in sd.theme, Ember (marathon-dark, amber) by default for everyone."
chips:
  - Foundation
  - Theme
group: Foundations
order: 2
discuss: 0
created: 2026-11-09T19:23:22Z
updated: 2026-11-11T15:59:05Z
---

Four themes, twelve named palettes. The colours live in `css/tokens.css`, keyed by `html[data-theme]` and, for the two Marathon themes, `html[data-accent]`. Nothing else in the CSS hard-codes a colour: every rule reads the semantic tokens below, so a theme is only a token block.

## The palettes (what the visitor picks)

Settings › Theme shows one card per palette (`PALETTE` in `js/theme.js`). Each card is a live miniature of the site in that palette's tokens.

| Name | data-theme | data-accent |
|---|---|---|
| Paper | light | (none) |
| Night | dark | (none) |
| Acid | marathon-dark | lime |
| Static | marathon-dark | cyan |
| Siren | marathon-dark | red |
| Ember | marathon-dark | amber |
| Reactor | marathon-dark | green |
| Sulphur | marathon-light | lime |
| Glacier | marathon-light | cyan |
| Flare | marathon-light | red |
| Honey | marathon-light | amber |
| Moss | marathon-light | green |

Records: [light](light.md), [dark](dark.md), [marathon-dark](marathon-dark.md), [marathon-light](marathon-light.md), [marathon-accents](marathon-accents.md).

## Choosing a theme (priority)

1. `?theme=…&accent=…` in the URL. This is a preview only and is never stored.
2. The stored choice: `localStorage['sd.theme']` = JSON `{"theme": "...", "accent": "..."}`. A stored accent `orange` is read as `amber`.
3. The default: **Ember**, `marathon-dark` with accent `amber`, for everyone (Ahmed, Nov 11). It no longer follows `prefers-color-scheme`.

A valid stored theme with no or an unknown accent gets `lime`. `data-accent` is set only for the Marathon themes and is removed for light and dark.

## Before first paint

An inline script, placed directly after `<meta name="theme-color">` in `<head>`, applies the same rules before the CSS paints, so there is no flash. It also writes the theme-color meta. Verbatim from the live `index.html`:

```html
<meta name="theme-color" content="#ffffff">
<script>/* the theme before first paint (js/theme.js has the same rules): ?theme=&accent= > stored > Ember (marathon-dark, amber) */
(function(){var d=document.documentElement,q=new URLSearchParams(location.search),T=['light','dark','marathon-dark','marathon-light'],A=['lime','cyan','red','amber','green'],t=q.get('theme'),a=q.get('accent'),s=null;
if(T.indexOf(t)<0){try{s=JSON.parse(localStorage.getItem('sd.theme')||'null')}catch(e){}t=s&&T.indexOf(s.theme)>=0?s.theme:'marathon-dark';a=s&&T.indexOf(s.theme)>=0?(s.accent==='orange'?'amber':s.accent):'amber'}
d.setAttribute('data-theme',t);if(t.indexOf('marathon')===0)d.setAttribute('data-accent',A.indexOf(a)>=0?a:'lime');
var P={light:'#ffffff',dark:'#0b0b0c','marathon-dark':'#0b0b0c','marathon-light':'#f1f3f7'};document.currentScript.previousElementSibling.setAttribute('content',P[t]);})();</script>
```

The inline map gives each theme's paper for the meta (`marathon-dark` `#0b0b0c`, the token value). `js/theme.js` `announce()` then rewrites the meta to the computed `--paper` hex once the module runs.

## Changing it live (`js/theme.js`)

- `setTheme(theme, accent, { store = true })` sets the attributes, stores `{theme, accent}`, and announces. Passing `null` as the theme removes the stored choice and goes back to the default (Ember).
- Nothing listens to `prefers-color-scheme` any more: the default does not follow the system.
- A `storage` event on `sd.theme` (another tab) re-applies it, so tabs stay in sync.
- `announce()` sets `meta[name=theme-color]` to the computed `--paper` hex and dispatches `window` `theme:change` with `readColors()`: the tokens paper, ink, dot, glow, ok, accent, accent-mark, accent-wash, signal, tint, swell, shade, shadow and foot as sRGB triples from 0 to 1, plus `grainK`. The WebGL layers (wordmark, orbs, grids), the grain, and the Settings sound scores re-tint from this event without a reload.

Source: `site/js/theme.js`, whole file

```js
// Themes. The colours live in css/tokens.css, keyed by html[data-theme] and,
// for Marathon, html[data-accent]. The inline script in index.html sets both
// before first paint (the same rules as pick() below); this module changes
// them live and tells everyone that draws in colour.
//
// Choosing: ?theme=…&accent=… (a preview, not stored) > the stored choice
// (localStorage 'sd.theme', set from the debug panel) > Ember (marathon-dark,
// amber), the default for everyone (Ahmed, Nov 11).
//
// Listening: window 'theme:change' (detail = the colours below), or onTheme(fn),
// which also calls fn once now. Colours come as sRGB triples 0..1, read from the
// tokens with getComputedStyle, so a token edit in CSS reaches the GL as is.

export const THEMES = [
  { id: 'light', label: 'Light' },
  { id: 'dark', label: 'Dark' },
  { id: 'marathon-dark', label: 'Marathon dark', accents: true },
  { id: 'marathon-light', label: 'Marathon light', accents: true },
];
export const ACCENTS = ['lime', 'cyan', 'red', 'amber', 'green'];
// every theme the visitor can pick, each colour its own theme with its own name (Ahmed, Nov 9).
// Stored as before ({ theme, accent }), so the tokens and the debug panel are unchanged.
export const PALETTE = [
  { name: 'Paper', theme: 'light' },
  { name: 'Night', theme: 'dark' },
  { name: 'Acid', theme: 'marathon-dark', accent: 'lime' },
  { name: 'Static', theme: 'marathon-dark', accent: 'cyan' },
  { name: 'Siren', theme: 'marathon-dark', accent: 'red' },
  { name: 'Ember', theme: 'marathon-dark', accent: 'amber' },
  { name: 'Reactor', theme: 'marathon-dark', accent: 'green' },
  { name: 'Sulphur', theme: 'marathon-light', accent: 'lime' },
  { name: 'Glacier', theme: 'marathon-light', accent: 'cyan' },
  { name: 'Flare', theme: 'marathon-light', accent: 'red' },
  { name: 'Honey', theme: 'marathon-light', accent: 'amber' },
  { name: 'Moss', theme: 'marathon-light', accent: 'green' },
];
const KEY = 'sd.theme';
const root = document.documentElement;
const valid = (t) => THEMES.some(x => x.id === t);
const hasAccent = (t) => !!THEMES.find(x => x.id === t)?.accents;

// (orange became amber, Nov 9: a stored orange carries over)
function stored() { try { const s = JSON.parse(localStorage.getItem(KEY) || 'null'); if (s?.accent === 'orange') s.accent = 'amber'; return s; } catch (e) { return null; } }

// what applies now: { theme, accent, source: 'url' | 'stored' | 'default' }
export function pick() {
  const q = new URLSearchParams(location.search);
  if (valid(q.get('theme'))) return { theme: q.get('theme'), accent: ACCENTS.includes(q.get('accent')) ? q.get('accent') : 'lime', source: 'url' };
  const s = stored();
  if (s && valid(s.theme)) return { theme: s.theme, accent: ACCENTS.includes(s.accent) ? s.accent : 'lime', source: 'stored' };
  return { theme: 'marathon-dark', accent: 'amber', source: 'default' }; // Ember for everyone until they pick (Ahmed, Nov 11; was the system's light or dark)
}

// any CSS colour string to [r, g, b] 0..1 (and alpha), through a 1px canvas
const cx = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
export function parseColor(str, fallback = [0, 0, 0]) {
  if (!str) return fallback;
  cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = str.trim();
  cx.fillRect(0, 0, 1, 1);
  const d = cx.getImageData(0, 0, 1, 1).data;
  return [d[0] / 255, d[1] / 255, d[2] / 255];
}
export const toHex = (c) => '#' + c.map(v => Math.round(v * 255).toString(16).padStart(2, '0')).join('');
const lum = (c) => c.map(v => v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)).reduce((s, v, i) => s + v * [0.2126, 0.7152, 0.0722][i], 0);

const TOKENS = ['paper', 'ink', 'dot', 'glow', 'ok', 'accent', 'accent-mark', 'accent-wash', 'signal', 'tint', 'swell', 'shade', 'shadow', 'foot'];
// the colours of an element's theme (the page by default, or a [data-theme] probe)
export function readColors(el = root) {
  const cs = getComputedStyle(el);
  const out = {};
  for (const k of TOKENS) out[k.replace(/-(\w)/g, (_, c) => c.toUpperCase())] = parseColor(cs.getPropertyValue('--' + k));
  out.hex = Object.fromEntries(Object.entries(out).map(([k, v]) => [k, toHex(v)]));
  out.grainK = parseFloat(cs.getPropertyValue('--grain-k')) || 1;
  out.dark = lum(out.paper) < lum(out.ink);
  out.theme = el.getAttribute('data-theme') || 'light';
  out.accentName = el.getAttribute('data-accent') || 'lime';
  out.marathon = out.theme.startsWith('marathon');
  return out;
}

export let colors = readColors();

function applyAttrs({ theme, accent }) {
  root.setAttribute('data-theme', theme);
  if (hasAccent(theme)) root.setAttribute('data-accent', accent); else root.removeAttribute('data-accent');
}

function announce() {
  colors = readColors();
  document.querySelectorAll('meta[name="theme-color"]').forEach(m => m.setAttribute('content', colors.hex.paper));
  window.dispatchEvent(new CustomEvent('theme:change', { detail: colors }));
}

// apply a theme; store = remember it (the debug panel), null theme = follow the system again
export function setTheme(theme, accent = 'lime', { store = true } = {}) {
  if (theme == null) { try { localStorage.removeItem(KEY); } catch (e) {} applyAttrs(pick()); announce(); return; }
  if (!valid(theme)) return;
  if (!ACCENTS.includes(accent)) accent = 'lime';
  if (store) { try { localStorage.setItem(KEY, JSON.stringify({ theme, accent })); } catch (e) {} }
  if (root.getAttribute('data-theme') === theme && (root.getAttribute('data-accent') || 'lime') === accent) return;
  applyAttrs({ theme, accent });
  announce();
}

export function current() { return { ...pick(), theme: root.getAttribute('data-theme') || 'light', accent: root.getAttribute('data-accent') || 'lime' }; }

export function onTheme(fn) {
  const h = (e) => fn(e.detail);
  window.addEventListener('theme:change', h);
  fn(colors);
  return () => window.removeEventListener('theme:change', h);
}

// follow the system while nothing is chosen
// (the default no longer follows the system's light or dark, so nothing listens for it changing)
// another tab chose a theme
window.addEventListener('storage', (e) => { if (e.key === KEY && pick().source !== 'url') { applyAttrs(pick()); announce(); } });

// in case the inline script didn't run (a page without it): apply now
if (!root.hasAttribute('data-theme')) applyAttrs(pick());
colors = readColors();
document.querySelectorAll('meta[name="theme-color"]').forEach(m => m.setAttribute('content', colors.hex.paper));
```


## The switch itself (crossfade)

Picking a card in Settings › Theme runs `setTheme` inside `document.startViewTransition` (when it exists and the page is visible), so the whole page crossfades. There is no mask and no blur. `--vt-ms` is `calc(260ms - 80ms * var(--fnd-energy))`, which is 220ms at the default energy of 0.5. Under reduced motion it becomes 120ms linear. Without View Transitions the theme simply swaps.

Source: `site/css/site.css`, lines 850 to 859

```css
/* the theme change: a quick crossfade of the whole page, no mask, no blur (Ahmed, Nov 9) */
::view-transition-old(root), ::view-transition-new(root) { animation: none; mix-blend-mode: normal; }
::view-transition-old(root) { animation: vt-out var(--vt-ms) var(--ease-land) both; }
::view-transition-new(root) { animation: vt-in var(--vt-ms) var(--ease-land) both; }
@keyframes vt-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes vt-out { from { opacity: 1; } to { opacity: 0; } }
@media (prefers-reduced-motion: reduce) {
  ::view-transition-old(root), ::view-transition-new(root) { animation-duration: 120ms; animation-timing-function: linear; }
  .qs-label, .qs-dots i, .spec-frame, .chip, .mini { transition: none; }
}
```


The Settings page itself is specified in [Settings](../../templates/settings.md).

## The token block (all themes)

The semantic tokens, with the meaning of each one, then every theme block verbatim. This is the whole of the theme system.

Source: `site/css/tokens.css`, lines 51 to 189

```css
/* ---------- themes ----------
   Semantic colour tokens, keyed by html[data-theme] (and html[data-accent] for
   Marathon). The attributes are set before first paint by the inline script in
   index.html and changed live by js/theme.js, which tells the GL layers, grain
   and grids with a 'theme:change' event. A [data-theme] probe element gets the
   same values (the debug panel's swatches read them that way).
   --paper, --ink       the page and its type
   --dot                quiet fills: the dot buttons at rest, slate surfaces
   --glow               the "new" marker and found-secret traces
   --ok                 the success check
   --accent             the theme's colour, as a fill
   --accent-text        the accent where it is type on paper (AA)
   --accent-mark        the accent where it is a small non-text mark on paper (3:1)
   --accent-wash        the accent as a highlight behind ink (ink on it is AA)
   --on-accent          type on an --accent fill
   --ring               focus rings
   --signal             the second colour, used sparingly (Marathon only)
   --tint               what the Library dots and Experiments glyphs lean to at Tone
   --swell              the wordmark's colour at the peak of a "thinking" swell
   --shade, --shadow    a cast shadow on the Coffee table; the colour of UI shadows
   --shadow-k           how much stronger UI shadows are than on white
   --warm, --warm-halo  the warm words' glow
   --muted              secondary type (also --op-meta, --op-faint as opacities)
   --grain-k            the grain's strength against this paper */
:root, [data-theme] {
  color-scheme: light;
  --paper: #fff;
  --ink: #000;
  --dot: #e0e0e0;
  --glow: #FFC81A;
  --ok: #1e9e57;
  --accent: #000;
  --accent-text: var(--ink);
  --accent-mark: var(--ink);
  --accent-wash: transparent;
  --on-accent: var(--paper);
  --ring: var(--ink);
  --signal: var(--ink);
  --tint: var(--ink);
  --swell: var(--ink);
  --shade: #dad8d6;
  --shadow: #000;
  --shadow-k: 1;
  --warm: #d69600;
  --warm-halo: #ffc400;
  --select-bg: var(--ink);
  --select-fg: var(--paper);
  --op-meta: 0.56;
  --op-faint: 0.39;
  --grain-k: 1;
  --foot: var(--ink);
  --muted: color-mix(in srgb, var(--ink) calc(var(--op-meta) * 100%), var(--paper));
}
[data-theme="dark"] {
  color-scheme: dark;
  --paper: #0b0b0c;
  --ink: #ece8e1;
  --dot: #2b2a28;
  --glow: #FFC81A;
  --ok: #3ecf7e;
  --accent: var(--ink);
  --shade: #000;
  --shadow: #000;
  --shadow-k: 2.4;
  --warm: #ffb81a;
  --warm-halo: #ffc400;
  --op-meta: 0.6;
  --op-faint: 0.5;
  --grain-k: 1.5;
  --blend-ink: screen;
}
/* Marathon: the acid graphic look. One accent (data-accent), the others as signals. */
[data-theme="marathon-dark"] {
  color-scheme: dark;
  --paper: #0b0b0c;               /* the dark theme's paper, no navy */
  --ink: #ece8e1;
  --dot: #2b2a28;
  --foot: var(--accent);          /* footer wordmark, marks and bio in the accent */
  --accent: #c2fe0b;
  --accent-text: var(--accent);
  --accent-mark: var(--accent);
  --accent-wash: var(--accent);
  --on-accent: #0b0b0c;
  --signal: #01ffff;
  --glow: var(--accent);
  --ok: var(--accent);
  --ring: var(--accent-mark);
  --tint: var(--signal);
  --swell: var(--signal);
  --shade: #000;
  --shadow: #000;
  --shadow-k: 2.4;
  --warm: var(--accent);
  --warm-halo: var(--accent);
  --select-bg: var(--accent);
  --select-fg: var(--on-accent);
  --op-meta: 0.64;
  --op-faint: 0.52;
  --grain-k: 1.4;
  --blend-ink: screen;
}
[data-theme="marathon-dark"][data-accent="cyan"] { --accent: #01ffff; --signal: #c2fe0b; }
[data-theme="marathon-dark"][data-accent="red"] { --accent: #ff0d1a; --accent-text: #ff4d55; --accent-mark: #ff4d55; --ok: #59b41d; --on-accent: #fff; }
[data-theme="marathon-dark"][data-accent="amber"] { --accent: #ffb000; }
[data-theme="marathon-dark"][data-accent="green"] { --accent: #59b41d; }
[data-theme="marathon-light"] {
  color-scheme: light;
  --foot: var(--accent-mark);     /* the accent, deepened so it reads on light paper */
  --paper: #f1f3f7;
  --ink: #29324f;
  --dot: #d5dae4;
  --accent: #c2fe0b;
  --accent-text: var(--ink);       /* lime is never type on light paper: it sits behind it */
  --accent-mark: #587c00;
  --accent-wash: var(--accent);
  --on-accent: var(--ink);
  --signal: #ff0d1a;
  --glow: var(--accent);
  --ok: #38801a;
  --ring: var(--accent-mark);
  --tint: var(--ink);
  --swell: var(--signal);
  --shade: #c3c9d6;
  --shadow: #29324f;
  --shadow-k: 1.2;
  --warm: #8fbf00;
  --warm-halo: var(--accent);
  --select-bg: var(--accent-wash);
  --select-fg: var(--ink);
  --op-meta: 0.78;
  --op-faint: 0.72;
  --grain-k: 1.1;
}
[data-theme="marathon-light"][data-accent="cyan"] { --accent: #01ffff; --accent-mark: #007f88; --warm: #00b3bf; }
[data-theme="marathon-light"][data-accent="red"] { --accent: #ff0d1a; --accent-wash: #f88088; --accent-mark: #e00012; --signal: #fd6c1d; --warm: #ff0d1a; }
[data-theme="marathon-light"][data-accent="amber"] { --accent: #ffb000; --accent-wash: #ffd47a; --accent-mark: #9a6200; --warm: #e09a00; }
[data-theme="marathon-light"][data-accent="green"] { --accent: #59b41d; --accent-wash: #96cd74; --accent-mark: #38801a; --warm: #59b41d; }
```


## Theme-specific rules elsewhere in site.css

- Light Marathon: the active nav item and the miniature's active item get the accent as a highlighter behind the ink (`linear-gradient(transparent 12%, var(--accent-wash) 12% 92%, transparent 92%)` with ±3px box-shadow), never as type colour.
- In dark and Marathon themes, the small grey type (`.rec-val, .viewer-count, .info-foot, .info-source, .mcp-label, .mcp-note, .mcp-lede, .sp-back, .type-tile-desc` and the MCP step numbers) uses `var(--muted)` instead of the 40–50% ink mixes, so it stays above AA.
- Marathon: the dot-matrix buttons take the accent on hover.
- `--blend-ink: screen` (dark themes) is the blend the ink filters use on dark paper.

## The favicon follows the theme

`js/favicon.js` (mounted at the end of `boot()`) draws the tab icon as a 7 × 7 dot matrix holding a circle: each dot's size comes from the circle's signed distance field. It is drawn as an SVG in `--accent-mark` (or `--ink` in the plain themes) on `--paper`, and redrawn on every theme change. Every `link[rel=icon]` takes the live SVG. `assets/favicon.svg` is the same circle in Ember, for the first paint.

Source: `site/js/favicon.js`, whole file

```js
// The favicon (Ahmed, Nov 11): a 7 by 7 dot matrix holding a circle. Each dot's size comes from the circle's signed
// distance field (inside, full; past the edge, a faint speck), the same way the harness card's tile draws its square.
// Drawn as an SVG in the theme's accent (--accent-mark, ink in the plain themes) on its paper, and drawn again
// whenever the theme changes, so the tab follows the site. assets/favicon.svg is the same circle in Ember, for
// the first paint and for anything that reads the file (tools/favicon.py made the old "sd").
import { onTheme } from './theme.js';

const N = 7;
const esc = (c) => c.replace(/#/g, '%23');

export function faviconSvg(ink, paper) {
  const cell = 64 / (N + 1);
  let dots = '';
  for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
    const x = (i - (N - 1) / 2) / ((N - 1) / 2), y = (j - (N - 1) / 2) / ((N - 1) / 2); // -1..1
    const d = Math.hypot(x, y) - 0.86;                                // the circle's distance field
    const fill = Math.min(1, Math.max(0, 0.5 - d / 0.34));
    const r = cell * (0.1 + 0.34 * fill), o = 0.22 + 0.78 * fill;
    dots += `<circle cx="${(cell * (i + 1)).toFixed(2)}" cy="${(cell * (j + 1)).toFixed(2)}" r="${r.toFixed(2)}"${o < 1 ? ` opacity="${o.toFixed(2)}"` : ''}/>`;
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="${paper}"/><g fill="${ink}">${dots}</g></svg>`;
}

export function mountFavicon() {
  const links = [...document.head.querySelectorAll('link[rel="icon"]')];
  const draw = () => {
    const cs = getComputedStyle(document.documentElement);
    const ink = cs.getPropertyValue('--accent-mark').trim() || cs.getPropertyValue('--ink').trim() || '#000';
    const paper = cs.getPropertyValue('--paper').trim() || '#fff';
    const href = 'data:image/svg+xml,' + esc(faviconSvg(ink, paper));
    // the .ico would win in some browsers, so every icon link takes the live SVG
    links.forEach(l => { l.href = href; l.type = 'image/svg+xml'; l.removeAttribute('sizes'); });
  };
  return onTheme(draw);
}
```
