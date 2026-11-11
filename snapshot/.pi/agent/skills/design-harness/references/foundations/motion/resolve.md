---
title: Resolve
slug: resolve
status: published
description: "Every state change resolves: a snapshot before and after, then an SDF field morph in 320ms, or a 120ms fade without WebGL."
chips:
  - Motion
  - Resolve
  - Page transitions
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:02:22Z
---

A **resolve** is how anything on the page changes state. The page snapshots what is on screen, applies the change, and snapshots again. Every element that changed is handed to the WebGL field, which morphs it from its old shape to the new one: noise peaks mid-flight and the blur reads as a widened edge. The DOM text steps aside (`.rz` makes it transparent but keeps it selectable) while the field draws it.

## `transition(mutate, opts)` (`js/resolve.js`)

- `opts.kind` is one of `state` (a page or route change), `hover`, `emerge`, `clock` or `icon`.
- **Duration:** `opts.dur`, else hover → `hoverMs(E)` 300ms, emerge → `emergeMs(E)` 816ms, otherwise `resolveMs(E)` 320ms.
- **Amplitude:** `noisePx(E)` 1.9px × (hover .35, clock .4, emerge 1.35, otherwise 1).
- **Which elements:** every `[data-morph]` on screen (or only `opts.keys`). Elements inside the body (`[data-morph-lines]`) and the `.post-meta` row are left out; they have their own motions.
- **The body** (`opts.body`) streams in. See [streaming](streaming.md).
- **Fast path:** used when there is no GL, a lost context, a hidden tab or reduced motion. What changed fades from opacity 0 over 120ms linear (360ms for an emergence). An icon fades from `blur(2px)` / .25 over 260ms with `cubic-bezier(.2,.7,.2,1)`.
- **GPU budget:** an element over the GPU budget (`BUDGET` in [webgl](webgl.md)) also gets the fallback fade.
- **Events:** emits `resolve:start` `{id, kind, dur, section, item, sectionSlug}`, then `resolve:end`. Sound and haptics listen to these.

Source: `site/js/resolve.js`, lines 1 to 94

```js
// Orchestrates a change of state: snapshot what is on screen, apply the change,
// snapshot again, and hand every element that changed to the field.
import { bus, params, reducedMotion } from './state.js';
import { MOTION } from './tokens.js';
import { snapshot } from './raster.js';

let gl = null;
let gid = 0;
export function setGL(g) { gl = g; }

function viewportClip(margin = 60) {
  return { top: window.scrollY - margin, bottom: window.scrollY + window.innerHeight + margin };
}
function onScreen(el) {
  const r = el.getBoundingClientRect();
  return r.bottom > -40 && r.top < window.innerHeight + 40 && r.width + r.height > 0;
}
// Morph keys inside the body belong to the body's line resolve, unless asked for by name.
function collect(sel, named) {
  const m = new Map();
  document.querySelectorAll(sel).forEach(el => {
    if (!named && el.closest('[data-morph-lines]')) return;
    if (!named && el.closest('.post-meta')) return; // the actions row steps out and back on its own (app.js), no field morph
    if (onScreen(el)) m.set(el.dataset.morph, snapshot(el, el.dataset.morph));
  });
  return m;
}
function same(a, b) {
  return a.sig === b.sig && Math.abs(a.blur - b.blur) < 0.02 && Math.abs(a.opacity - b.opacity) < 0.01
    && Math.abs(a.rect.x - b.rect.x) < 0.5 && Math.abs(a.rect.y - b.rect.y) < 0.5;
}

// mutate(): applies the new state to the DOM.
// opts: { keys: [data-morph keys] (default all), body: bool, kind: 'state'|'hover'|'copy'|'clock', section, item,
//         dur (ms, overrides the kind's), amp (px), style: { dots, pitch, blur } for the icon dot-matrix toggle }
export function transition(mutate, opts = {}) {
  // returns the resolve's duration in ms
  const { keys = null, body = false, kind = 'state' } = opts;
  const id = ++gid;
  const E = params.energy;
  const dur = opts.dur || (kind === 'hover' ? MOTION.hoverMs(E) : kind === 'emerge' ? MOTION.emergeMs(E) : MOTION.resolveMs(E));
  const sel = keys ? keys.map(k => `[data-morph="${k}"]`).join(',') : '[data-morph]';
  // no field when there is no GL, a lost context, a hidden tab or reduced motion
  const fast = !gl || reducedMotion.matches || !gl.canMorph();

  // A: what is showing now (a running hover morph hands over its current params)
  const A = fast ? null : collect(sel, !!keys);
  if (A) for (const [k, s] of A) {
    const cur = gl.current(k);
    if (cur && cur.sameText) { s.blur = cur.blur; s.opacity = cur.opacity; }
  }
  const bodyEl = body ? document.querySelector('[data-morph-lines]') : null;
  const bodyTextA = bodyEl ? bodyEl.textContent : null;

  mutate();

  bus.emit('resolve:start', { id, kind, dur, section: opts.section, item: opts.item, sectionSlug: opts.sectionSlug });

  if (fast) {
    // reduced motion or no WebGL: a plain 120ms opacity swap on what changed
    const els = [...document.querySelectorAll(sel)].filter(el => keys || !el.closest('[data-morph-lines]'));
    if (bodyEl) els.push(bodyEl);
    if (!document.hidden) els.forEach(el => fade(el, kind));
    setTimeout(() => bus.emit('resolve:end', { id, kind }), MOTION.reducedMs);
    return MOTION.reducedMs;
  }

  const B = collect(sel, !!keys);
  const items = [];
  const hide = (el) => { el.classList.add('rz'); el.dataset.rz = id; };
  const unhider = (el) => () => { if (el && el.dataset.rz == id) { el.classList.remove('rz'); delete el.dataset.rz; } };

  const keysAll = new Set([...A.keys(), ...B.keys()]);
  for (const k of keysAll) {
    const a = A.get(k), b = B.get(k);
    if (a && b && same(a, b) && !gl.isActive(k)) continue;
    const el = b?.el || null;
    if (el) hide(el);
    items.push({ key: k, A: a || null, B: b || null, el, onEnd: unhider(el) });
  }

  // the post itself: a focus pull (soft blur clearing to sharp), not a field morph
  let bodyMs = 0;
  if (bodyEl && bodyEl.textContent !== bodyTextA) bodyMs = streamIn(bodyEl, kind, id);

  const amp = opts.amp ?? MOTION.noisePx(E) * (kind === 'hover' ? MOTION.hoverNoise : kind === 'clock' ? 0.4 : kind === 'emerge' ? 1.35 : 1);
  if (!items.length) { setTimeout(() => bus.emit('resolve:end', { id, kind }), bodyMs); return bodyMs; }
  // past the GPU budget (js/gl.js BUDGET) an element gets the plain crossfade instead
  const over = gl.run({ id, kind, items, body: null, dur, amp, style: opts.style || null }) || [];
  for (const it of over) { it.onEnd?.(); if (it.el) fade(it.el, kind); }
  return dur;
}
```


Source: `site/js/resolve.js`, lines 197 to 220

```js
// focus pull: the whole post comes into focus at once, blur clearing to sharp
function focusPull(el, kind) {
  const ms = kind === 'emerge' ? MOTION.focusMs * 1.4 : MOTION.focusMs;
  el.getAnimations().forEach(a => a.cancel());
  el.animate([
    { filter: 'url(#ink-body) blur(6px)', opacity: 0.25 },
    { filter: 'url(#ink-body) blur(1.2px)', opacity: 0.9, offset: 0.55 },
    { filter: 'url(#ink-body) blur(0px)', opacity: 1 }
  ], { duration: ms, easing: 'cubic-bezier(0.2, 0, 0, 1)' });
}

// the plain opacity swap (reduced motion, no WebGL, or over budget)
function fade(el, kind) {
  // an icon without WebGL (and without reduced motion): a CSS blur and opacity pass
  if (el.dataset.maskSrc && !reducedMotion.matches) {
    const cs = getComputedStyle(el);
    el.animate([{ filter: 'blur(2px)', opacity: 0.25 }, { filter: cs.filter === 'none' ? 'blur(0px)' : cs.filter, opacity: cs.opacity }], { duration: 260, easing: 'cubic-bezier(.2,.7,.2,1)' });
    return;
  }
  const fadeMs = kind === 'emerge' ? MOTION.reducedMs * 3 : MOTION.reducedMs; // an emergence is a slightly longer fade
  el.animate([{ opacity: 0 }, { opacity: getComputedStyle(el).opacity }], { duration: fadeMs, easing: 'linear' });
}
```


## Page transitions (routing, `js/app.js`)

Routing uses hashes: `#/section/item`. Path entry points such as `/articles/slug/` are folded into the hash on boot and kept canonical with `replaceState`. A route change does the following:

1. Marks the piece opened. Its badges clear, so their orbs melt into the label.
2. `transition(() => render(r), { body: true, kind: 'state', section, item, sectionSlug, chord })`. The nav and sub-nav labels whose state changed morph through the field, the post streams in, and the sound pad glides to the section's chord.
3. The actions row steps out (`.post-meta.is-away`: opacity 0, translateY 4px, blur 3px, 90ms) and settles back when the stream ends (260/320ms). There is a safety timeout of dur + 1400ms.
4. `flowIn()`: what the field does not morph (a gallery grid, slides, a Settings page) glides in. That is opacity 0, translateY 6px, blur 4px → none over 240ms, 22ms apart for the first 14 children (delays capped at 8 steps), with land easing.
5. At 900px and wider, if scrolled, the page jumps to the top.

The same item with a different sub-page (a gallery's project) only re-renders the gallery and calls `flowIn`, scrolling smoothly to the top.

Source: `site/js/app.js`, lines 468 to 499

```js
// ---------- routing ----------
function go(initial = false) {
  const r = routeOf(location.hash);
  if (!r) { renderEmpty(); return; }
  if (location.hash !== r.hash) history.replaceState(null, '', r.hash);
  const open = (x) => (x.app ? E.closePiece() : E.openPiece(x.item)); // Settings is not a piece: nothing is read there
  if (initial || !route) { open(r); render(r); document.querySelector('.post-meta')?.classList.add('is-away'); streamIn(article, 'load'); return; }
  if (route.section === r.section && route.item === r.item) {
    if (r.sub !== route.sub) { route = r; renderGallery(r); flowIn(); if (window.scrollY > 0 && innerWidth >= 900) window.scrollTo({ top: 0, behavior: reducedMotion.matches ? 'auto' : 'smooth' }); }
    return;
  }
  open(r); // clears its badges: their orbs melt into the label
  const chord = SOUND.voicing(r.section.slug, r.itemIndex);
  transition(() => render(r), { body: true, kind: 'state', section: r.sectionIndex, item: r.itemIndex, sectionSlug: r.section.slug, chord });
  flowIn(); // the grid and the settings page glide in rather than cut
  syncOrbs();
  if (window.scrollY > 0 && innerWidth >= 900) window.scrollTo({ top: 0 });
}
// what the field doesn't morph (a gallery's grid, the slides, a settings page) glides in:
// a quick rise out of a soft blur, staggered a touch, so a page change reads as one motion
function flowIn() {
  if (reducedMotion.matches) return;
  const els = [...document.querySelectorAll('.col-gallery > *, #article.is-settings > .settings:not(.settings-mcp) > *')].slice(0, 14);
  els.forEach((el, i) => el.animate([
    { opacity: 0, transform: 'translateY(6px)', filter: 'blur(4px)' },
    { opacity: 1, transform: 'none', filter: 'blur(0px)' }
  ], { duration: 240, delay: Math.min(i, 8) * 22, easing: 'cubic-bezier(0.2, 0, 0, 1)', fill: 'backwards' }));
}
window.addEventListener('hashchange', () => go());

// ---------- emergence: something new resolves into place ----------
function onReveal(node, title) {
```


## Hover and focus: the peek

Inactive menu items rest at `opacity: var(--op-rest)` (.39) with the `#ink-ui` filter. Hovering, or focusing with `:focus-visible`, resolves the item partway: `.is-peek` gives `--op-peek` .695, as a hover-kind morph over 300ms with a third of the noise. The active item is sharp at 1. Touch never peeks, but a touch press emits `hover` for the sound and haptics. Focus-visible also underlines the item (1px, offset 3px).

Source: `site/css/site.css`, lines 56 to 71

```css
/* ---------- items: active sharp, the rest recede ---------- */
.item {
  display: inline-block;
  white-space: nowrap;
  opacity: var(--op-rest);
  filter: url(#ink-ui);
  outline: none;
}
.item.is-peek { opacity: var(--op-peek); filter: url(#ink-ui); }
.item.is-active { opacity: 1; filter: url(#ink-ui); }
.col-nav .item.is-active { color: var(--accent-text); }
/* on light Marathon paper the accent is a highlighter behind the ink, never the type */
[data-theme="marathon-light"] .col-nav .item.is-active { background: linear-gradient(transparent 12%, var(--accent-wash) 12%, var(--accent-wash) 92%, transparent 92%); box-shadow: -3px 0 0 var(--accent-wash), 3px 0 0 var(--accent-wash); }
/* room for the yellow orb after a label (6px gap + 7px orb) */
.item.has-orb { padding-right: 13px; }
.item:focus-visible { opacity: 1; filter: url(#ink-ui); text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; }
```


Source: `site/js/app.js`, lines 614 to 628

```js
// ---------- hover and focus partially resolve inactive items ----------
function bindPeek(a) {
  const peek = (on, source) => {
    if (a.classList.contains('is-active')) return;
    if (a.classList.contains('is-peek') === on) return;
    transition(() => a.classList.toggle('is-peek', on), { keys: [a.dataset.morph], kind: 'hover' });
    if (on) bus.emit('hover', { el: a, source });
  };
  a.addEventListener('pointerenter', (e) => { if (e.pointerType !== 'touch') peek(true, e.pointerType); });
  a.addEventListener('pointerleave', (e) => { if (e.pointerType !== 'touch') peek(false); });
  a.addEventListener('focus', () => { if (a.matches(':focus-visible')) peek(true, 'focus'); });
  a.addEventListener('blur', () => peek(false));
  a.addEventListener('pointerdown', (e) => { if (e.pointerType === 'touch') bus.emit('hover', { el: a, source: 'touch' }); });
}
```


## Press and icon toggles (col 4 icons)

Icons are Amicons masks. They are not in this harness: rebuild them as `<span class="ico">` slots. At rest an icon is its line variant at ink .56. Hover is the line variant at 1. Pressed or active is the solid variant. Every change between them runs through the field. Mid-flight the icon dissolves into a halftone (dot pitch 1.75px) and lands crisp. A toggle takes 380ms. A hover takes 260ms with a lighter halftone. "Copied" is a single green check (`--ok`) that holds for 1.6s.

Source: `site/js/app.js`, lines 629 to 674

```js
// ---------- col 4: icons that toggle through an SDF dot matrix ----------
// At rest an icon is its line variant at ink .56; hover is line at 1; pressed
// or active is the solid variant. Every change between them runs through the
// field: mid-flight the icon dissolves into a halftone and lands crisp.
const ICON_STYLE = { dots: 1, pitch: 1.75, blur: 1.6 };   // press and toggles
const ICON_HOVER = { dots: 0.45, pitch: 1.75, blur: 0.8 }; // a light partial pass
const ICON_MS = { toggle: 380, hover: 260, hold: 1600 };
const ICON_AMP = 0.8;                                      // px of fbm warp under the dots
const absSrc = (name) => new URL(iconSrc(name), document.baseURI).href;
const variant = (key, v) => { const k = ICONS[key]; return typeof k === 'string' ? k : k[v]; };

// el: the .ico span. key: an ICONS key. v: 'line' | 'solid'
function setIcon(el, key, v = 'line') {
  const name = variant(key, v);
  const src = absSrc(name);
  el.dataset.icon = key; el.dataset.variant = v; el.dataset.maskSrc = src;
  el.classList.toggle('is-ok', key === 'copied'); // success: a single check, in green
  el.style.setProperty('--src', `url("${src}")`); // absolute: a url() in a custom property resolves against the stylesheet
}
function iconTo(el, key, v, { hot = el.classList.contains('is-hot'), style = ICON_STYLE, dur = ICON_MS.toggle, kind = 'icon' } = {}) {
  return transition(() => { setIcon(el, key, v); el.classList.toggle('is-hot', hot); },
    { keys: [el.dataset.morph], kind, dur: dur * slowFactor(), amp: ICON_AMP, style });
}
// the review aid's slow motion stretches these too
const slowFactor = () => (isSlow() ? 40 : 1);

function bindIcon(btn, el, keyFn) {
  btn.addEventListener('pointerenter', (e) => {
    if (e.pointerType === 'touch') return;
    bus.emit('hover', { el: btn, source: e.pointerType });
    if (!el.classList.contains('is-hot')) iconTo(el, keyFn(), el.dataset.variant, { hot: true, style: ICON_HOVER, dur: ICON_MS.hover, kind: 'hover' });
  });
  btn.addEventListener('pointerleave', () => {
    if (el.dataset.variant === 'solid' && !btn.dataset.holding) iconTo(el, keyFn(), 'line', { hot: false });
    else if (el.classList.contains('is-hot')) iconTo(el, keyFn(), el.dataset.variant, { hot: false, style: ICON_HOVER, dur: ICON_MS.hover, kind: 'hover' });
  });
  btn.addEventListener('pointerdown', (e) => {
    if (e.button !== 0 || btn.dataset.holding) return;
    iconTo(el, keyFn(), 'solid', { hot: true });
    if (e.pointerType === 'touch') bus.emit('hover', { el: btn, source: 'touch' });
  });
  btn.addEventListener('pointerup', () => { if (el.dataset.variant === 'solid' && !btn.dataset.holding) iconTo(el, keyFn(), 'line', { hot: true }); });
  btn.addEventListener('focus', () => { if (btn.matches(':focus-visible') && !el.classList.contains('is-hot')) iconTo(el, keyFn(), el.dataset.variant, { hot: true, style: ICON_HOVER, dur: ICON_MS.hover, kind: 'hover' }); });
  btn.addEventListener('blur', () => { if (el.classList.contains('is-hot') && !btn.matches(':hover')) iconTo(el, keyFn(), el.dataset.variant, { hot: false, style: ICON_HOVER, dur: ICON_MS.hover, kind: 'hover' }); });
}
```


## The actions row (code)

Source: `site/js/app.js`, lines 682 to 700

```js
// the actions row under the post: it follows the text, so while the body changes it
// steps out (fast), and settles back in at its new place once the text has landed
const postMeta = document.querySelector('.post-meta');
let metaSafety = 0, metaResolve = null;
bus.on('resolve:start', (d) => {
  if (!postMeta || !(d.kind === 'state' || d.kind === 'emerge')) return;
  metaResolve = d.id;
  postMeta.classList.add('is-away');
  clearTimeout(metaSafety);
  metaSafety = setTimeout(() => postMeta.classList.remove('is-away'), (d.dur || 600) + 1400); // never stuck hidden
});
bus.on('resolve:end', (d) => {
  if (!postMeta || d.id !== metaResolve || article.dataset.streaming) return;
  clearTimeout(metaSafety);
  requestAnimationFrame(() => postMeta.classList.remove('is-away'));
});
// the actions come back once the post has finished writing itself
bus.on('stream:end', () => { if (!postMeta) return; clearTimeout(metaSafety); requestAnimationFrame(() => postMeta.classList.remove('is-away')); });
```


Source: `site/css/site.css`, lines 302 to 307

```css
/* the actions row steps out while the post changes and settles back once the text lands */
.post-meta { transition: opacity 260ms var(--ease-land), transform 320ms var(--ease-land), filter 260ms var(--ease-land); }
.post-meta.is-away { opacity: 0; transform: translateY(4px); filter: url(#ink-ui) blur(3px); pointer-events: none; transition-duration: 90ms; }
@media (prefers-reduced-motion: reduce) { .post-meta, .post-meta.is-away { transition: opacity 120ms linear; transform: none; filter: url(#ink-ui); } }
.post-meta[hidden] { display: none; }
```


## Clock

A Toronto clock re-resolves once a minute (kind `clock`, silent). It is `hidden` on the live site.
