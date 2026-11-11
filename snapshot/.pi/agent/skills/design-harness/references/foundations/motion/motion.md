---
title: Motion
slug: motion
status: published
description: "One curve, called think, and every duration on the site, derived from --fnd-energy (0.5)."
chips:
  - Think ease
  - Resolve 320ms
  - Focus 360ms
  - Stream 9ms a word
order: 1
created: 2026-11-09T14:21:21Z
updated: 2026-11-11T16:01:22Z
---

Motion on saleh.digital is quiet and short. There is one expressive curve, `think`, and one landing curve, `land`. Every duration derives from one energy value, `--fnd-energy` (0.5 by default).

## The two curves

- **think** (JS, `js/tokens.js`): quick off the mark, lingering through the middle, gentle to land.
  `think(t) = 0.15·t + 0.85·(0.5 + 0.5·sign(u)·|u|^2.4)`, where `u = 2t − 1`. The CSS stand-in is `--ease-think: cubic-bezier(0.1, 0.72, 0.9, 0.28)`.
- **land**: `--ease-land: cubic-bezier(0.2, 0, 0, 1)`. Every Web Animations call on the site uses this curve (`easing: 'cubic-bezier(0.2, 0, 0, 1)'`).

```css
:root {
  --fnd-energy: 0.5;
  --motion-resolve: calc(600ms - 180ms * var(--fnd-energy));  /* 510ms: the CSS-side resolve */
  --motion-stagger: 12ms;
  --ease-think: cubic-bezier(0.1, 0.72, 0.9, 0.28);
  --ease-land: cubic-bezier(0.2, 0, 0, 1);
  --blur-rest: calc(4px * (0.4 + var(--fnd-focus)));          /* 4px at focus .6 */
  --op-rest: calc(0.85 - 0.766 * var(--fnd-focus));           /* 0.3904 */
  --blur-peek: calc(var(--blur-rest) * 0.375);                /* 1.5px */
  --op-peek: calc((var(--op-rest) + 1) / 2);                  /* 0.6952 */
}
```

## Every duration (values at energy 0.5)

| What | Duration | Curve / detail | Source |
|---|---|---|---|
| Field resolve (a state change, the page change) | `(380 − 120E)` = **320ms** | `think` in the shader | `MOTION.resolveMs` |
| Hover morph (nav item peek, warm word, mark) | `(340 − 80E)` = **300ms**, noise × .35 | `think` | `MOTION.hoverMs` |
| Emergence resolve | `(600 − 180E) × 1.6` = **816ms**, noise × 1.35 | `think` | `MOTION.emergeMs` |
| Clock micro-resolve (each minute) | resolveMs, noise × .4 | silent | app.js |
| Morph noise amplitude | `0.6 + 2.6E` = **1.9px** mid-flight | fbm | `MOTION.noisePx` |
| Body line stagger | **12ms** a line | top to bottom | `MOTION.staggerMs` |
| Streaming: between words | `min(9 × (1.3 − .6E), 650 × (9/14) / wordsOnScreen)` = at most **9ms** | | [streaming](streaming.md) |
| Streaming: each word inks in | `220 × 9/14` = **141ms** | blur 5 → 1.4 → 0px, opacity 0 → .55 → 1, land | resolve.js `streamIn` |
| Streaming: words below the fold | 200ms opacity only | | |
| Caret fade at the end | 360ms after a 160ms delay | | |
| Focus pull (whole post) | **360ms** (×1.4 for emergence) | blur 6 → 1.2 → 0, opacity .25 → .9 → 1 | `MOTION.focusMs` |
| Gallery / settings glide-in on a page change | **240ms**, stagger **22ms** (max 8 steps, first 14 children) | opacity 0, translateY 6px, blur 4px → none, land | app.js `flowIn` |
| Actions row stepping out / back | out **90ms**; back opacity/filter 260ms, transform 320ms | land | site.css `.post-meta` |
| Icon toggle (copy → copied, sound on/off) | **380ms**, dot-matrix style (dots 1, pitch 1.75, blur 1.6) | field | app.js `ICON_MS` |
| Icon hover | **260ms**, light halftone (dots .45, pitch 1.75, blur .8) | field | |
| "Copied" hold | 380 + **1600ms** | then back to copy | |
| Warm word: hover before it lights | **700ms** | then a hover morph | |
| Slow hover counted for resonance | **600ms** | | app.js |
| Hold the wordmark (secret) | **2000ms** hold, then morphs to Arabic over 1100ms, holds 3600ms, back over 1100ms, locked until 4800ms | | [hidden extras](hidden-extras.md) |
| Theme change crossfade | `--vt-ms` = `260 − 80E` = **220ms** | land | [themes](../themes.md) |
| MCP chat controls rising in | **220ms**, 50ms apart | translateY 4px → 0 | settings.js |
| Orb bloom / melt / flare | bloom 720ms easeOutBack (overshoot 2.2), melt 650ms, flare 900ms | | [orbs](orbs.md) |
| Grain | jumps at 15 fps | | [texture](../materials/texture.md) |
| GL idle loop | 15 fps idle, 30 fps with an orb on screen | | `MOTION.idleFps`, `orbFps` |
| Reduced-motion swap | **120ms** linear opacity | | `MOTION.reducedMs` |

## Reduced motion

`prefers-reduced-motion: reduce` (read once into `reducedMotion` in `js/state.js`, and live by CSS):

- No field morphs. `transition()` takes the fast path: what changed fades in over 120ms linear, and an emergence fades over 360ms.
- Streaming becomes one 160ms opacity fade of the whole post. There is no caret.
- `flowIn` and the MCP rise-ins are skipped.
- The theme crossfade is 120ms linear.
- The audio pitch wobble is off. The Library shelf, Coffee table and Experiments grids draw their static DOM versions.
- The harness-flow dots are drawn by the SVG, with no shader.
- Every CSS transition listed in site.css and the embed CSS has a `@media (prefers-reduced-motion: reduce)` override, either `transition: none` or a 120ms linear opacity.

The `?lite` query also turns off the GL footer and the wordmark traces.

## Review aid (slow motion)

`?slow=8` multiplies `resolveMs`, `hoverMs`, `staggerMs` and `emergeMs` by 8. The backquote key toggles ×40. While slow, the keys 1 to 9 freeze a morph at 10% to 90% and 0 unfreezes. The keys `u n r c s` dispatch `sd:review` (u next tier, n pretend night, r reset, c copy toggle, s sound toggle).

## Every motion token

Source: `site/js/tokens.js`, whole file

```js
// Motion and sound tokens. Defined once; the shaders, the audio and the
// orchestration all read from here.

// "think" ease: quick off the mark, lingers through the middle (the thinking
// beat), then lands fast. f(t) = 0.15t + 0.85 * (0.5 + 0.5 * sign(u) * |u|^2.4), u = 2t - 1
export const THINK_POW = 2.4;
export const THINK_LINEAR = 0.15;
export function think(t) {
  t = Math.min(1, Math.max(0, t));
  const u = 2 * t - 1;
  const s = 0.5 + 0.5 * Math.sign(u) * Math.pow(Math.abs(u), THINK_POW);
  return THINK_LINEAR * t + (1 - THINK_LINEAR) * s;
}

// Review aid: ?slow=8, or the backquote key, stretches every morph so a resolve can be seen mid-flight
let SLOW = Math.max(1, Number(new URLSearchParams(location.search).get('slow')) || 1);
// With slow motion on, keys 1 to 9 freeze every running morph at 10% to 90%; 0 lets go.
export const REVIEW = { freeze: null };
export const setSlow = (on) => { SLOW = on ? 40 : 1; if (!on) REVIEW.freeze = null; };
export const isSlow = () => SLOW > 1;
window.addEventListener('keydown', (e) => {
  if (e.metaKey || e.ctrlKey || e.altKey || e.target.closest?.('input, textarea, select')) return;
  if (e.key === '`') { SLOW = SLOW > 1 ? 1 : 40; REVIEW.freeze = null; console.info('[resolve] slow motion', SLOW > 1 ? 'on' : 'off'); }
  else if (SLOW > 1 && /^[0-9]$/.test(e.key)) REVIEW.freeze = e.key === '0' ? null : Number(e.key) / 10;
  else if (SLOW > 1 && 'unrcs'.includes(e.key)) window.dispatchEvent(new CustomEvent('sd:review', { detail: e.key }));
});

export const MOTION = {
  focusMs: 360,   // the post's focus pull: blur clears to sharp (no line-by-line field resolve)
  // the post streams in word by word, like it is being written as you arrive
  streamWordMs: 9,       // between words (faster when Lively). Faster and more fluid (Ahmed, Nov 9): was 14
  streamMaxMs: 650,      // the words on screen all start within this (was 1500)
  streamInkMs: 220,      // each word: blur to sharp (was 280)
  // a resolve lasts 380ms when Still, 260ms when Lively (320ms at energy .5); was 600 to 420
  resolveMs: (energy) => (380 - 120 * energy) * SLOW,
  hoverMs: (energy) => (340 - 80 * energy) * SLOW,
  staggerMs: 12 * SLOW,   // per body line, top to bottom
  bodyInDelay: 0.2,       // incoming body starts after 20% of a resolve
  reducedMs: 120,         // prefers-reduced-motion: plain opacity swap
  // noise amplitude in CSS px at the middle of a morph
  noisePx: (energy) => 0.6 + 2.6 * energy, // calmer mid-morph so short resolves stay fluid (was 1 + 5E)
  hoverNoise: 0.35,       // hover morphs carry this fraction of the noise
  // wordmark breathing, CSS px
  breathPx: (energy) => 0.3 + 1.2 * energy,
  grainFps: 15,
  idleFps: 15,
  orbFps: 30,
  emergeMs: (energy) => (600 - 180 * energy) * SLOW * 1.6
};

// ---------- emergence ----------
// Resonance: a hidden score that grows with attention. One tunable table.
export const RESONANCE = {
  readSecond: 0.25,      // per second of active reading (body on screen, tab focused, active in the last 30s)
  idleAfter: 30,         // seconds without input before reading stops counting
  idleDecay: 0.05,       // per idle second, never below the floor of the tier already reached
  scrollDepth: 8,        // per piece, times the deepest fraction reached
  pieceOpened: 6,        // each distinct piece, first time
  finishPiece: 15,       // reached the end having read at least 40% of skim time
  skimWordsPerSecond: 5,
  returnVisit: 30,       // first visit on a new (Toronto) day
  slowHover: 1.5,        // hover held over 600ms, once per element per visit
  slowHoverMs: 600,
  secretFound: 10
};
// Score needed for each tier. A curious first visit (~5 min, 2 to 3 pieces) lands near tier 2.
export const TIERS = [0, 25, 60, 150, 260, 400];

export const EMERGE = {
  cooldownMs: 4000,      // one thing at a time, at least 4s apart
  quietAfterNavMs: 1400, // wait for a route resolve to land first
  durScale: 1.6,         // an emergence resolve is 1.6x a normal one
  ampScale: 1.35,
  think: 1.8,            // wordmark swell (a normal resolve is 1)
  orbDelay: 0.75         // orb blooms at 75% of the emergence resolve
};

// The "new" marker. style 'glow' is the game pickup (js/glsl.js ORB_GLOW_FRAG);
// 'dots' brings back the first orb, the dot-matrix metaball (ORB_DOTS_FRAG).
// Sizes in CSS px (core and halo are diameters), pitch in device px, times in ms
// unless they say s. The four --fnd sliders (glow, sparkle, orbsize, warmth)
// scale these around their middle; see orbLook() in js/gl.js.
export const ORB = {
  style: 'glow',
  size: 7, sizeSmall: 5, gap: 6,
  // glow
  halo: 26, haloSmall: 16,        // halo diameter: under 28px, it never covers the label (masked at its edge)
  haloI: 0.85, shadeI: 0.08,      // halo strength, and the faint darker falloff past it
  gold:  { hot: '#FFFBE0', core: '#FFDA1F', edge: '#FFB300', halo: '#FFCF26' }, // warmth 0
  amber: { hot: '#FFF0BF', core: '#FFBA12', edge: '#FF8A00', halo: '#FFA526' }, // warmth 1
  shadeCol: '#7A3B00', inkCol: '#000000',
  barS: 2.61,                     // breath period: one bar of the site clock (92 bpm, 4/4)
  pulse: 1, pulseSmall: 0,        // pulse rings per two bars
  motes: 3, motesSmall: 1,
  bob: 0.7,                       // px
  flare: 1, flareMs: 900,         // the "new item!" flare, when it first appears
  hoverMs: 220,                   // hover shimmer eases in and out over this
  burstMs: 760,                   // open: the sparks' flight into the label
  // dots
  pitch: 1.5,
  yellow: '#FFD400', shade: '#F0B400', rim: '#A88300', ink: '#000000',
  bloomMs: 720, bloomOvershoot: 2.2,  // easeOutBack s
  meltMs: 650, leanMax: 0.6, leanEase: 6,
  wobbleSpeed: 0.35
};

// The wordmark as the visible resonance meter. life = tier progress / 5 + 0.08
// per secret (0 to 1). Stage k fades in as life*5 goes from k-1 to k.
export const LIFE = {
  perSecret: 0.08,
  settleMs: 1800,          // the displayed life eases to a new level over this
  swell: 1.4,              // an emergence swells the word before it settles
  boil: 0.7,               // tier 1: edge boil, CSS px
  cursorGain: 2.2,         //         cursor perturbation multiplier at full stage
  dotPitch: 2.4,           // tier 2: halftone pitch inside the strokes, CSS px
  dotDrift: 0.6,           //         fbm drift of the dot grid, CSS px
  rippleSpacing: 9,        // tier 3: iso-line spacing, CSS px
  rippleAlpha: 0.13,       //         faint
  rippleReach: 46,         //         falloff distance, CSS px
  meld: 0.42,              // tier 4: smooth-min radius, as a fraction of cap height / 10
  flow: 6,                 //         dot flow along the strokes, CSS px per second
  traceRadius: 0.32,       // tier 5: yellow trace cluster radius, fraction of cap height
  ghostAlpha: 0.16,        //         أحمد صالح ghost in the halftone
  traceLetters: { warm: 9, hold: 0, harness: 4, night: 7 } // the letter each secret lodges in
};

// The footer (bio + marks) drawn in the wordmark's pass: the same life stages,
// attenuated per region so they read as crisp as the DOM at life 0.
export const FOOT = {
  bio: 0.3,     // the bio gets 30% of the word's stage strength
  marks: 1,     // the marks get the wordmark's full treatment
  scale: 2,     // field texels per CSS px for this region (falls back to fit BUDGET)
  maxWarp: 0.4  // px, the cap on any displacement of the bio (in the shader)
};

// ---------- sound: the Jai Paul pass ----------
// One key centre (D, natural minor). Each section is a chord degree, so moving
// around the site plays a progression; a sub-item inverts the voicing.
export const SOUND = {
  root: 146.83,                          // D3
  chords: {                              // semitones from D3
    articles: [0, 3, 7, 10, 14],         // i    Dm9
    components: [3, 7, 10, 14],          // III  Fmaj7
    harnesses: [5, 8, 12, 15, 19],       // iv   Gm9
    philosophy: [-4, 0, 3, 7],           // VI   Bbmaj7
    library: [7, 10, 14, 17],            // v    Am7
    friends: [-2, 2, 5, 12],             // VII  Cadd9
    experiments: [2, 5, 8, 12]           // ii   Em7b5
  },
  detuneCents: 12,        // fixed per-note mistuning, random within +-
  driftCents: 9,          // random walk on top (tape drift)
  wow: { rate: 0.45, cents: 7 }, flutter: { rate: 5.8, cents: 1.6 },
  chorus: { delays: [0.012, 0.017], depth: 0.003, rates: [0.31, 0.53], mix: 0.5 },
  crush: { bits: 5, down: 6 },
  formantAh: [[800, 1, 11], [1150, 0.5, 12], [2900, 0.22, 14]], // Hz, gain, Q
  levels: { stab: 0.045, sub: 0.03, tick: 0.012, emerge: 0.06, vox: 0.035, pluck: 0.03,
            bedNoise: 0.003, bedDrone: 0.0035, warmthPerTier: 0.22, wet: 0.22 },
  pump: { depth: 0.35, releaseMs: 340, beatMs: 420 },
  stabFilter: [220, 1500], bloomFilter: [250, 2200],
  hz(semi) { return this.root * Math.pow(2, semi / 12); },
  voicing(section, inversion = 0) {
    const c = [...(this.chords[section] || this.chords.articles)];
    for (let k = 0; k < inversion % c.length; k++) c.push(c.shift() + 12);
    return c;
  }
};

export const HAPTICS = { hover: [6], resolve: [8, 30, 12], copy: [10, 40, 10], toggle: [6], emerge: [12, 40, 8, 40, 20] };

// "Open in MCP": the site's MCP server, as the apps should connect to it.
// Served at /mcp on this site (Streamable HTTP); see mcp/ in the repo.
export const MCP = { name: 'saleh-digital', url: 'https://saleh.digital/mcp' };
```


## The event bus and live params

Source: `site/js/state.js`, whole file

```js
// One event bus for the whole site, plus the live tuning params.
// Events: 'resolve:start' {id, kind, dur, section, item, pitch}
//         'resolve:progress' {id, t, raw}
//         'resolve:end' {id, kind}
//         'hover' {el}, 'copy' {}, 'params' {energy, texture, focus, density}
// Anything new (a light, a log, a second canvas) subscribes with bus.on(type, fn).
// bus.on('*', (type, detail) => ...) hears everything.

const listeners = new Map();

export const bus = {
  on(type, fn) {
    if (!listeners.has(type)) listeners.set(type, new Set());
    listeners.get(type).add(fn);
    return () => listeners.get(type)?.delete(fn);
  },
  off(type, fn) { listeners.get(type)?.delete(fn); },
  emit(type, detail = {}) {
    listeners.get(type)?.forEach(fn => { try { fn(detail); } catch (e) { console.error(e); } });
    listeners.get('*')?.forEach(fn => { try { fn(type, detail); } catch (e) { console.error(e); } });
  }
};

// Tuning axes, read from :root (--fnd-*). Kept live three ways: a 'fnd:params'
// window event (detail may carry new values), a style observer on <html>,
// and a slow poll as a safety net.
export const params = { energy: 0.5, texture: 0.4, focus: 0.6, density: 0.3, life: 0, glow: 0.5, sparkle: 0.5, orbsize: 0.5, warmth: 0.35 };
const KEYS = Object.keys(params);

function readParams() {
  const cs = getComputedStyle(document.documentElement);
  let changed = false;
  for (const k of KEYS) {
    const v = parseFloat(cs.getPropertyValue('--fnd-' + k));
    if (Number.isFinite(v) && v !== params[k]) { params[k] = Math.min(1, Math.max(0, v)); changed = true; }
  }
  if (changed) bus.emit('params', { ...params });
  return changed;
}

window.addEventListener('fnd:params', (e) => {
  const d = e.detail;
  if (d && typeof d === 'object') {
    for (const k of KEYS) if (d[k] != null) document.documentElement.style.setProperty('--fnd-' + k, String(d[k]));
  }
  readParams();
});
new MutationObserver(readParams).observe(document.documentElement, { attributes: true, attributeFilter: ['style', 'class'] });
setInterval(() => { if (!document.hidden) readParams(); }, 500);
export { readParams };

export const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');

// ?lite: a debug fallback. The wordmark keeps its edge and breathing but none
// of its life stages (halftone, ripples, melt, traces), and there is no grain.
export const LITE = new URLSearchParams(location.search).has('lite');

// One bar clock for the whole site, so the wordmark's ripples and the audio's
// pumping breathe together. 92 bpm, 4/4: a bar is about 2.61s.
export const BAR = { bpm: 92, beats: 4 };
export const barMs = () => (60000 / BAR.bpm) * BAR.beats;
export const barPhase = (t = performance.now()) => (t % barMs()) / barMs();
```
