---
title: Media reveal
slug: media-reveal
status: published
description: "Images revealed on attention: rest ~250ms on a record with media and its image resolves into the empty 4th column (blur 8px to 0 through a dot dissolve), cycling every 2.5s."
chips:
  - Pattern
  - Media
  - Attention
created: 2026-11-11T16:08:52Z
updated: 2026-11-11T16:08:52Z
---

Text stays first: at rest the site shows **no images**. Resting about 250ms on something that has one, or focusing it, resolves its image into the empty 4th column. That covers a record with an `img:` field, and a sub-nav page with frontmatter media. The image is top-aligned with the item and sticky in the viewport. It arrives as a focus pull (blur 8px → 0) through a dot-matrix dissolve, under the ink filter and the grain. Several images cycle every 2.5s while attention stays, with a small `1/9` counter. When attention leaves, the image holds a moment, then fades. A record that has media wears a quiet dot after its title (`.record.has-media`).

Under 900px there is no 4th column: tapping a record opens its image inline below it, and a second tap (or a tap elsewhere) closes it. Nothing loads until there is intent: the first image is fetched on the first hover (or touch), and the next one while the current one shows.

The image corners follow the [16px image corners](../../intelligence/memories/16px-image-corners.md) memory.

Source: `site/js/media.js`, whole file

```js
// Images, revealed on attention (Ahmed, Nov 9). Text stays first: at rest the
// site shows no images. Resting on something that has one (a record with an
// "img:" field, or a page in the sub-nav with frontmatter media) for ~250ms, or
// focusing it, resolves its image into the empty 4th column, top-aligned with
// that item and sticky in the viewport: a focus pull (blur 8px to 0) through a
// dot-matrix dissolve, under the ink filter and the site's grain. Several
// images cycle every 2.5s while attention stays, with a small "1/9". When
// attention leaves, it holds a moment, then fades.
// Under 900px there is no 4th column: tapping a record opens its image inline
// below it, and a second tap (or a tap elsewhere) closes it.
// Nothing loads until there is intent: the first image is fetched on the first
// hover (or touch), the next one while the current one shows.
import { BY_ID } from './content.js';

const WIDE = matchMedia('(min-width: 900px)');
const CALM = matchMedia('(prefers-reduced-motion: reduce)');
const DWELL = 250, HOLD = 420, CYCLE = 2500, STICK = 24;

const listOf = (el) => (el?.dataset.media || '').split(',').map(s => s.trim()).filter(Boolean);
const cache = new Map();
function load(src) {
  if (!cache.has(src)) {
    cache.set(src, new Promise((res, rej) => {
      const im = new Image();
      im.decoding = 'async';
      im.onload = () => (im.decode ? im.decode().catch(() => {}) : Promise.resolve()).then(() => res(im));
      im.onerror = () => { cache.delete(src); rej(new Error(`no image at ${src}`)); };
      im.src = src;
    }));
  }
  return cache.get(src);
}

// ---------- one figure: frames that cycle, and a counter ----------
function figure(list, label) {
  // a slot as tall as the column (so the figure in it can stick), one per reveal, so one can leave as the next arrives
  const slot = document.createElement('div'); slot.className = 'media-slot';
  const fig = document.createElement('figure');
  fig.className = 'media-fig';
  slot.append(fig);
  const frame = document.createElement('div'); frame.className = 'media-frame';
  const count = document.createElement('figcaption'); count.className = 'media-count';
  fig.append(frame, count);
  let i = 0, timer = 0, alive = true;
  const total = list.length;
  const setCount = () => { count.textContent = total > 1 ? `${i + 1}/${total}` : ''; };
  async function showFrame(n) {
    const src = list[n];
    let im;
    try { im = await load(src); } catch (e) { return false; }
    if (!alive) return false;
    const img = document.createElement('img');
    img.className = 'media-img';
    img.src = src; img.alt = label ? `${label}, image ${n + 1} of ${total}` : '';
    img.width = im.naturalWidth; img.height = im.naturalHeight;
    frame.append(img);
    i = n; setCount();
    // two frames so the start state is painted before it resolves
    requestAnimationFrame(() => requestAnimationFrame(() => {
      img.classList.add('is-in');
      const old = [...frame.children].filter(x => x !== img);
      old.forEach(o => o.classList.add('is-out'));
      setTimeout(() => old.forEach(o => o.remove()), CALM.matches ? 200 : 620);
      setTimeout(() => img.classList.add('is-settled'), CALM.matches ? 0 : 640);
    }));
    if (total > 1) load(list[(n + 1) % total]).catch(() => {});
    return true;
  }
  const tick = () => { timer = setTimeout(async () => { if (!alive) return; await showFrame((i + 1) % total); tick(); }, CYCLE); };
  return {
    el: slot, fig,
    async start() { const ok = await showFrame(0); if (ok && total > 1) tick(); return ok; },
    stop() { alive = false; clearTimeout(timer); },
  };
}

// ---------- wide: the 4th column ----------
let col = null;
let cur = null;     // { el, fig, list }
let intent = null;  // the element attention is resting on
let dwellT = 0, holdT = 0;

function ensureCol() {
  if (col?.isConnected) return col;
  col = document.querySelector('.col-media');
  if (!col) {
    col = document.createElement('aside');
    col.className = 'col col-media';
    col.setAttribute('aria-hidden', 'true');
    document.querySelector('.cols')?.append(col);
  }
  return col;
}

function place(fig, el) {
  const c = ensureCol();
  fig.style.marginTop = '0px';
  const top = el.getBoundingClientRect().top - c.getBoundingClientRect().top;
  const room = c.clientHeight - fig.offsetHeight;
  fig.style.marginTop = `${Math.max(0, Math.min(top, room))}px`;
}

function hideWide(now = false) {
  if (!cur) return;
  const c = cur; cur = null;
  c.fig.stop();
  c.fig.el.classList.add('is-leaving');
  setTimeout(() => c.fig.el.remove(), now || CALM.matches ? 0 : 300);
}

async function showWide(el) {
  const list = listOf(el);
  if (!list.length || cur?.el === el) return;
  hideWide();
  const label = el.querySelector('.rec-title')?.firstChild?.textContent || el.textContent.trim();
  const f = figure(list, label);
  const c = ensureCol();
  cur = { el, fig: f };
  f.el.style.visibility = 'hidden';
  c.append(f.el);
  const ok = await f.start();
  if (!ok || cur?.fig !== f) { if (cur?.fig === f) cur = null; f.el.remove(); return; }
  // placed once its first frame has a size, so it never sits past the end of the column
  const reposition = () => place(f.fig, el);
  reposition();
  f.el.style.visibility = '';
  f.el.querySelector('img')?.addEventListener('load', reposition, { once: true });
}

function attend(el) {
  clearTimeout(holdT);
  if (cur?.el === el) return;
  clearTimeout(dwellT);
  intent = el;
  load(listOf(el)[0]).catch(() => {}); // preload on first intent
  dwellT = setTimeout(() => { if (intent === el) showWide(el); }, DWELL);
}
function leave(el) {
  if (intent === el) intent = null;
  clearTimeout(dwellT);
  if (cur?.el !== el) return;
  clearTimeout(holdT);
  holdT = setTimeout(() => { if (cur?.el === el && intent !== el) hideWide(); }, HOLD);
}

// ---------- narrow: inline, by tap ----------
let open = null; // { el, fig }
// the page below moved: wake the field (it redraws the footer where it now is)
const relaid = () => { window.dispatchEvent(new Event('scroll')); setTimeout(() => window.dispatchEvent(new Event('scroll')), 320); };
function closeInline() {
  if (!open) return;
  const o = open; open = null;
  o.fig.stop();
  o.el.classList.remove('is-open');
  o.el.setAttribute('aria-expanded', 'false');
  o.fig.el.classList.add('is-leaving');
  setTimeout(() => { o.fig.el.remove(); relaid(); }, CALM.matches ? 0 : 240);
}
async function toggleInline(el) {
  if (open?.el === el) return closeInline();
  closeInline();
  const list = listOf(el);
  if (!list.length) return;
  const f = figure(list, el.querySelector('.rec-title')?.firstChild?.textContent || '');
  open = { el, fig: f };
  el.classList.add('is-open');
  el.setAttribute('aria-expanded', 'true');
  // the first frame is decoded before the figure goes in, so it opens once, at its own size
  try { await load(list[0]); } catch (e) { if (open?.el === el) closeInline(); return; }
  if (open?.fig !== f) return;
  f.el.classList.add('is-inline');
  el.append(f.el);
  await f.start();
  relaid();
}

// ---------- wiring ----------
const target = (e) => e.target?.closest?.('[data-media]');
export function initMedia() {
  ensureCol();
  document.addEventListener('pointerover', (e) => {
    if (e.pointerType === 'touch' || !WIDE.matches) return;
    const el = target(e);
    if (el) attend(el);
  });
  document.addEventListener('pointerout', (e) => {
    if (e.pointerType === 'touch' || !WIDE.matches) return;
    const el = target(e);
    if (el && !el.contains(e.relatedTarget)) leave(el);
  });
  document.addEventListener('focusin', (e) => { const el = target(e); if (el && WIDE.matches) attend(el); });
  document.addEventListener('focusout', (e) => { const el = target(e); if (el && !el.contains(e.relatedTarget)) leave(el); });
  document.addEventListener('pointerdown', (e) => { if (e.pointerType === 'touch') { const el = target(e); if (el && el.classList.contains('record')) load(listOf(el)[0]).catch(() => {}); } }, { passive: true });
  document.addEventListener('click', (e) => {
    if (WIDE.matches) return;
    const el = target(e);
    if (el && el.classList.contains('record') && !e.target.closest('a, button')) { toggleInline(el); return; }
    if (open && !open.el.contains(e.target)) closeInline();
  });
  document.addEventListener('keydown', (e) => {
    if (WIDE.matches || (e.key !== 'Enter' && e.key !== ' ')) return;
    const el = target(e);
    if (el && el === e.target && el.classList.contains('record')) { e.preventDefault(); toggleInline(el); }
  });
  WIDE.addEventListener('change', () => resetMedia());
}

// after every render: pages in the sub-nav that have media take attention too
export function markMedia(root = document) {
  root.querySelectorAll('#sub .item[data-node]').forEach(a => {
    const it = BY_ID.get(a.dataset.node);
    if (it?.media?.length) a.dataset.media = it.media.join(',');
    else delete a.dataset.media;
  });
}
// a new page: whatever was revealed goes at once
export function resetMedia() {
  clearTimeout(dwellT); clearTimeout(holdT); intent = null;
  hideWide(true);
  closeInline();
}
```


Source: `site/css/site.css`, lines 400 to 446

```css
/* ---------- images, revealed on attention (js/media.js) ----------
   No image at rest. The 4th column holds a reveal: sized by the grid row only
   (contain: size), so nothing it does can move the text. */
@property --mask-dot { syntax: "<length>"; inherits: false; initial-value: 0px; }
.col-media { align-self: stretch; position: relative; contain: size layout; pointer-events: none; }
.media-slot { position: absolute; inset: 0; }
.media-fig { position: sticky; top: 24px; margin: 0; width: min(100%, 520px); display: flex; flex-direction: column; gap: 8px; }
/* the ink and the grain: the UI's ink filter on the frame; #grain already lies over everything */
.media-frame { display: grid; justify-items: start; align-items: start; filter: url(#ink-ui); }
.media-img {
  grid-area: 1 / 1; display: block; width: auto; height: auto; max-width: 100%; max-height: calc(100vh - 80px); max-height: calc(100svh - 80px);
  opacity: 0; filter: blur(8px);
  /* the dot-matrix dissolve: a 5px screen whose dots open until they cover */
  -webkit-mask: radial-gradient(circle, #000 var(--mask-dot), transparent calc(var(--mask-dot) + .8px)) 0 0 / 5px 5px;
  mask: radial-gradient(circle, #000 var(--mask-dot), transparent calc(var(--mask-dot) + .8px)) 0 0 / 5px 5px;
  transition: opacity 280ms var(--ease-land), filter 560ms var(--ease-land), --mask-dot 520ms cubic-bezier(.5, 0, .2, 1);
}
.media-img.is-in { opacity: 1; filter: blur(0); --mask-dot: 4px; }
.media-img.is-settled { -webkit-mask: none; mask: none; }
.media-img.is-out { opacity: 0; filter: blur(4px); transition: opacity 360ms var(--ease-land) 120ms, filter 360ms var(--ease-land) 120ms; }
.media-count { font: 400 12px/16px var(--ui); letter-spacing: -0.2px; font-variant-numeric: tabular-nums; color: var(--ink); opacity: var(--op-meta); filter: url(#ink-ui); }
.media-count:empty { display: none; }
.media-slot.is-leaving .media-fig { opacity: 0; filter: blur(3px); transition: opacity 260ms var(--ease-land), filter 260ms var(--ease-land); }

/* something to discover: a dot after the title, barely there */
.rec-title { position: relative; }
.rec-mark { display: inline-block; width: 3px; height: 3px; margin-left: 6px; vertical-align: 4px; border-radius: 50%; background: currentColor; opacity: .32; transition: opacity 200ms var(--ease-land); }
.record.has-media { cursor: default; outline: none; }
.record.has-media:hover .rec-mark, .record.has-media:focus-visible .rec-mark, .record.is-open .rec-mark { opacity: .8; }
.record.has-media:focus-visible .rec-title { text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; }

/* narrow: no 4th column; a tap opens the image inline, below the record */
@media (max-width: 899px) {
  .col-media { display: none; }
  .record.has-media { cursor: pointer; -webkit-tap-highlight-color: transparent; }
  .media-slot.is-inline { position: static; grid-column: 2; margin-top: 10px; }
  .media-slot.is-inline .media-fig { position: static; width: 100%; }
  .media-slot.is-inline .media-img { max-height: 70vh; max-height: 70svh; }
}
@media (prefers-reduced-motion: reduce) {
  .media-img { filter: none; -webkit-mask: none; mask: none; transition: opacity 200ms linear; }
  .media-img.is-in { filter: none; }
  .media-img.is-out { filter: none; transition: opacity 200ms linear; }
  .media-slot.is-leaving .media-fig { filter: none; transition: opacity 200ms linear; }
}
.openin[hidden] { display: none; }
```
