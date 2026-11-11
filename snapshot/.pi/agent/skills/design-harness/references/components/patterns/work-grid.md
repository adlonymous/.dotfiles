---
title: Work grid
slug: work-grid
status: published
description: "::work-grid: a masonry of live work built with design harnesses; live artifacts run in their tiles, videos play in place, pictures open the viewer."
chips:
  - Embed
  - Grid
  - Media
created: 2026-11-11T16:05:20Z
updated: 2026-11-11T16:05:35Z
---

Embeds are placed in a post by a paragraph that is only `::name` (`EMBED = /^::([a-z-]+)\s*$/`). `js/embeds.js` replaces it with `<div class="embed embed-NAME" data-embed="NAME" data-stream-skip>`, lazy-imports `js/embeds/NAME.js` and calls `mount(el, ctx)`. Embeds are skipped by the word stream and by the body ink filter (`.col-body article > :not(.embed) { filter: url(#ink-body) }`), so screenshots and diagrams stay sharp.

**What it is.** Live work built with design harnesses, as a masonry of the real artifacts running in their tiles, plus screenshots and videos. Pictures open in the site's full-screen viewer (`js/viewer.js`, see [record](../../templates/record.md)). Videos play in place. Artifacts are live pages and take the pointer themselves: an artifact module is imported when its tile nears the viewport and unmounted when it is far off it, and if it fails to load its fallback image shows. A tile can be `wide` (spans two columns) or `beside`. Each tile has a caption: a one-line note, plus a link (`site`/`href`, opens in a new tab). A tile with `src: null` is a slot waiting for its file and is not shown. It runs full width to the page's right padding at 900px and wider.

The live tiles are the owner's client work. This record describes the component generically: the entries are not reproduced, so use your own.

Source: `site/css/embeds/work-grid.css`, whole file

```css
/* ::work-grid (js/embeds/work-grid.js): live work as a masonry; frames as .masonry-cell */
.embed-work-grid { margin: calc(var(--para) * 0.25) 0; }
/* two columns in the 540px post column, one when a column would drop under 220px (phones) */
.wg { columns: 2 220px; column-gap: 12px; }
.wg-tile { margin: 0 0 calc(var(--para) * 0.75); break-inside: avoid; display: flex; flex-direction: column; gap: 8px; }
.wg-frame {
  position: relative; display: block; width: 100%; padding: 0; border: 0; overflow: hidden;
  border-radius: 16px; background: color-mix(in srgb, var(--ink) 3%, var(--paper));
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 7%, transparent);
  cursor: zoom-in; -webkit-tap-highlight-color: transparent;
  transition: transform 160ms var(--ease-land), box-shadow 160ms var(--ease-land);
}
/* the frame line sits over the picture, so a white page still has an edge */
.wg-frame::after { content: ""; position: absolute; inset: 0; border-radius: inherit; pointer-events: none; box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--ink) 7%, transparent); }
button.wg-frame:hover { box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 12%, transparent), 0 6px 16px -8px color-mix(in srgb, var(--shadow) calc(14% * var(--shadow-k)), transparent); }
button.wg-frame:active { transform: scale(.985); }
.wg-frame:focus-visible { outline: none; box-shadow: 0 0 0 2px var(--paper), 0 0 0 3px var(--ring); }
.wg-img { display: block; width: 100%; height: auto; object-fit: cover; opacity: 0; filter: blur(8px); transition: opacity 420ms var(--ease-land), filter 520ms var(--ease-land); }
.wg-img.is-in { opacity: 1; filter: blur(0); }

/* video: the whole frame is the play/pause button; a small mark shows when paused */
div.wg-frame { cursor: default; }
.wg-play { position: absolute; inset: 0; z-index: 1; padding: 0; border: 0; background: none; cursor: pointer; border-radius: inherit; }
.wg-play:focus-visible { outline: none; box-shadow: inset 0 0 0 2px var(--ring); }
.wg-play::before {
  content: ""; position: absolute; left: 12px; bottom: 12px; width: 28px; height: 28px; border-radius: 50%;
  background: color-mix(in srgb, var(--paper) 86%, transparent); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 10%, transparent);
  transition: opacity 200ms var(--ease-land);
}
.wg-play::after {
  content: ""; position: absolute; left: 23px; bottom: 21px; width: 0; height: 0;
  border-style: solid; border-width: 5px 0 5px 8px; border-color: transparent transparent transparent var(--ink);
  transition: opacity 200ms var(--ease-land);
}
.is-playing .wg-play::before, .is-playing .wg-play::after { opacity: 0; }
.is-playing .wg-play:hover::before, .is-playing .wg-play:focus-visible::before { opacity: 1; }
.is-playing .wg-play:hover::after, .is-playing .wg-play:focus-visible::after { opacity: 1; left: 22px; width: 3px; height: 10px; border: 0; background: var(--ink); box-shadow: 5px 0 0 var(--ink); }

/* caption: the site as a link, one line under it */
.wg-cap { display: flex; flex-direction: column; gap: 1px; padding: 0 2px; font: 400 14px/18px var(--ui); letter-spacing: -0.2px; }
.wg-site { align-self: flex-start; color: var(--ink); text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; text-decoration-color: color-mix(in srgb, var(--ink) 28%, transparent); transition: text-decoration-color 160ms var(--ease-land); }
.wg-site::after { content: "\2197"; display: inline-block; margin-left: 3px; font-size: 11px; opacity: var(--op-faint); text-decoration: none; transition: transform 160ms var(--ease-land), opacity 160ms var(--ease-land); }
.wg-site:hover, .wg-site:focus-visible { text-decoration-color: currentColor; outline: none; }
.wg-site:hover::after { opacity: var(--op-meta); transform: translate(1px, -1px); }
.wg-note { display: none; }
.wg-cap { display: none; } /* no caption under the tiles (Ahmed, Nov 10): the pictures stand alone; alt text keeps the site names */

@media (prefers-reduced-motion: reduce) {
  .wg-img { filter: none; transition: opacity 160ms linear; }
  .wg-frame, .wg-site::after { transition: none; }
}

/* inline at the embeds' 820px on desktop: three columns of tiles */
@media (min-width: 900px) { .col-body .embed-work-grid .wg { columns: 3 200px; } }

/* artifact: a live page in the tile (js/embeds/artifacts/*.js); it brings its own look and pointer */
.wg-frame.is-artifact { cursor: auto; background: #fff; }
.wg-frame.is-artifact::after { z-index: 6; }
.wg-live { position: absolute; inset: 0; overflow: hidden; border-radius: inherit; opacity: 0; transition: opacity 420ms var(--ease-land); }
.wg-frame.is-artifact.is-in .wg-live, .wg-live:has(.wg-img) { opacity: 1; }
@media (prefers-reduced-motion: reduce) { .wg-live { transition: none; } }

/* the [product] app demo runs two columns wide in a feature row spanning the grid (see .wg-feature) */
.wg-feature { column-span: all; -webkit-column-span: all; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); column-gap: 12px; align-items: start; }
.wg-feature .wg-tile { min-width: 0; }
.wg-feature .is-wide { grid-column: span 2; }
/* two columns of three (Ahmed, Nov 10): the demo takes 2 of 3 columns, the beside tile the third */
@media (max-width: 899px) { .wg-feature { grid-template-columns: 1fr; } .wg-feature .is-wide { grid-column: auto; } }
```


Source: `site/js/embeds/work-grid.js` (MEDIA entries replaced by their schema)

```js
// ::work-grid, live work built with design harnesses: a masonry of the real artifacts, running
// in their tiles, plus any screenshots and videos. Pictures open in the site's full-screen viewer
// (js/viewer.js); videos play in place; artifacts are live pages and take the pointer themselves.
//
// MEDIA: one entry per tile, in reading order. A tile with src: null (and no module) is a slot
// waiting for its file and is not shown.
//   type     'artifact' | 'image' | 'video'
//   module   artifact only: an ES module exporting mount(el) -> cleanup, path from the site root
//            (js/embeds/artifacts/<name>.js). It is imported when the tile nears the viewport and
//            unmounted when it is far off it. If it fails to load, fallback (an image) shows instead.
//   src      image/video: path from the site root, e.g. 'assets/media/harness/neo-app-tour.mp4'
//   poster   video only: a jpg/webp still
//   w, h     the tile's proportions (an image's pixel size), so the masonry holds while it loads
//   site     the caption's link text; href where it goes (opens in a new tab)
//   note     one line under it
//   alt      what it shows, for screen readers (and the viewer)
// MEDIA: the owner's own project tiles (artifacts, videos, images) are listed here on the live site.
// They are client work and are not reproduced in this harness. Shape of one entry:
const MEDIA = [
  { type: 'image', src: 'assets/media/harness/example.webp', w: 1200, h: 700, site: 'example.com', href: 'https://example.com', note: 'A one-line caption', alt: 'What the picture shows' },
  // { type: 'artifact', module: 'js/embeds/artifacts/<name>.js', fallback: 'assets/…webp', w, h, wide: true, … }
  // { type: 'video', src: 'assets/…mp4', poster: 'assets/…jpg', w, h, beside: true, … }
];

const CSS = new URL('../../css/embeds/work-grid.css', import.meta.url).href;
function css() {
  if (document.querySelector(`link[href="${CSS}"]`)) return;
  const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = CSS; document.head.append(l);
}
const ROOT = new URL('../../', import.meta.url);   // the site root, for MEDIA paths
const reduced = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

export function mount(el) {
  css();
  const items = MEDIA.filter(m => m.src || m.module);
  const pics = items.filter(m => m.type === 'image');
  const grid = document.createElement('div');
  grid.className = 'wg';
  const frames = [];   // the picture tiles' frames, in viewer order
  const videos = [];
  const tiles = [];   // live artifacts

  items.forEach((m, n) => {
    const fig = document.createElement('figure'); fig.className = 'wg-tile'; if (m.wide) fig.classList.add('is-wide'); if (m.beside) fig.classList.add('is-beside');
    if (m.type === 'artifact') { artifact(m, fig); return; }
    const frame = document.createElement(m.type === 'image' ? 'button' : 'div');
    frame.className = 'wg-frame';
    frame.style.aspectRatio = `${m.w} / ${m.h}`;
    if (m.type === 'image') {
      const img = new Image();
      img.className = 'wg-img'; img.decoding = 'async'; img.loading = n < 4 ? 'eager' : 'lazy';
      img.alt = m.alt; img.width = m.w; img.height = m.h;
      img.addEventListener('load', () => img.classList.add('is-in'), { once: true });
      img.addEventListener('error', () => fig.remove(), { once: true });
      img.src = m.src;
      if (img.complete && img.naturalWidth) img.classList.add('is-in');
      const k = frames.length; frames.push(frame);
      frame.type = 'button';
      frame.setAttribute('aria-label', `Open ${m.alt} full screen`);
      frame.addEventListener('click', async () => {
        const { openViewer } = await import('../viewer.js');
        openViewer(pics.map(p => p.src), k, pics.map(p => p.alt), (i) => frames[i]);
      });
      frame.append(img);
    } else {
      const v = document.createElement('video');
      v.className = 'wg-img is-in'; v.muted = true; v.loop = true; v.playsInline = true; v.preload = 'metadata';
      v.setAttribute('muted', ''); v.setAttribute('playsinline', '');
      v.width = m.w; v.height = m.h;
      if (m.poster) v.poster = m.poster;
      v.src = m.src; v.setAttribute('aria-label', m.alt);
      const btn = document.createElement('button');
      btn.type = 'button'; btn.className = 'wg-play';
      const sync = () => { const on = !v.paused; btn.setAttribute('aria-label', on ? `Pause ${m.alt}` : `Play ${m.alt}`); frame.classList.toggle('is-playing', on); };
      v.addEventListener('play', sync); v.addEventListener('pause', sync); sync();
      btn.addEventListener('click', () => { v.dataset.user = v.paused ? 'play' : 'pause'; v.paused ? v.play().catch(() => {}) : v.pause(); });
      frame.append(v, btn);
      videos.push(v);
    }
    const cap = document.createElement('figcaption'); cap.className = 'wg-cap';
    const a = document.createElement('a'); a.className = 'wg-site'; a.href = m.href; a.target = '_blank'; a.rel = 'noopener'; a.textContent = m.site;
    const note = document.createElement('span'); note.className = 'wg-note'; note.textContent = m.note;
    cap.append(a, note);
    fig.append(frame, cap);
    grid.append(fig);
  });
  // the feature row (Ahmed, Nov 10): the Neo demo at two columns wide, with one tile beside it in the third.
  // CSS columns can only span one column or all, so the pair sits in its own row that spans all.
  const wide = grid.querySelector('.wg-tile.is-wide'), beside = grid.querySelector('.wg-tile.is-beside');
  if (wide) { const row = document.createElement('div'); row.className = 'wg-feature'; wide.before(row); row.append(wide); if (beside) row.append(beside); }
  el.replaceChildren(grid);

  // artifacts: imported as they near the screen, unmounted when far off it (each also pauses itself)
  function artifact(m, fig) {
    const frame = document.createElement('div');
    frame.className = 'wg-frame is-artifact';
    frame.style.aspectRatio = `${m.w} / ${m.h}`;
    frame.tabIndex = 0;
    frame.setAttribute('role', 'group');
    frame.setAttribute('aria-label', m.alt);
    const host = document.createElement('div'); host.className = 'wg-live';
    frame.append(host);
    fig.append(frame);
    grid.append(fig);
    tiles.push({ m, frame, host, stop: null, state: 'idle' });
  }
  async function on(t) {
    if (t.state !== 'idle') return;
    t.state = 'loading';
    try {
      const mod = await import(new URL(t.m.module, ROOT).href);
      const mount = mod.mount ?? mod.default;
      if (typeof mount !== 'function') throw new Error('no mount');
      if (t.state !== 'loading') return;
      t.stop = mount(t.host) || null; t.state = 'live';
      t.frame.classList.add('is-in');
    } catch {
      t.state = 'failed';
      const img = new Image(); img.className = 'wg-img is-in'; img.alt = t.m.alt; img.src = t.m.fallback;
      t.host.replaceChildren(img);
    }
  }
  function offscreen(t) {
    if (t.state === 'loading') { t.state = 'idle'; return; }
    if (t.state !== 'live') return;
    try { t.stop?.(); } catch {}
    t.stop = null; t.state = 'idle'; t.host.replaceChildren(); t.frame.classList.remove('is-in');
  }
  let near, far;
  if (tiles.length) {
    if ('IntersectionObserver' in window) {
      near = new IntersectionObserver((es) => es.forEach(e => { if (e.isIntersecting) on(tiles.find(t => t.frame === e.target)); }), { rootMargin: '400px 0px' });
      far = new IntersectionObserver((es) => es.forEach(e => { if (!e.isIntersecting) offscreen(tiles.find(t => t.frame === e.target)); }), { rootMargin: '1600px 0px' });
      tiles.forEach(t => { near.observe(t.frame); far.observe(t.frame); });
    } else tiles.forEach(on);
  }

  // inline in the post again (Ahmed, Nov 10), as wide as the diagram and the viewer

  // videos run only while on screen, never under reduced motion (a tap still plays them)
  let io;
  if (videos.length && 'IntersectionObserver' in window) {
    io = new IntersectionObserver((es) => es.forEach(e => {
      const v = e.target;
      if (e.isIntersecting && !reduced() && v.dataset.user !== 'pause') v.play().catch(() => {});
      else if (!e.isIntersecting) v.pause();
    }), { threshold: 0.35 });
    videos.forEach(v => io.observe(v));
  }
  return () => { near?.disconnect(); far?.disconnect(); tiles.forEach(offscreen); io?.disconnect(); videos.forEach(v => { v.pause(); v.removeAttribute('src'); v.load(); }); };
}
```
