---
title: Viewer
slug: viewer
status: published
description: "The full-screen viewer: a strip of frames on one spring (k 450, c 50), drag, flick, trackpad and keys; vertical drag dismisses; opens out of the thumbnail."
chips:
  - Pattern
  - Viewer
  - Spring
created: 2026-11-11T16:08:52Z
updated: 2026-11-11T16:08:52Z
---

Pictures (gallery frames, talk slides, work-grid images, experiments sketches) open in one full-screen viewer (`js/viewer.js`). There is no carousel anywhere on the site.

- **One spring for everything.** A strip of frames moves on one spring. Dragging, flicking, the trackpad, the arrows and the keys all push the same spring, so a step always lands the same way however it was asked for. The model follows the paging physics of mikematas.com (re-written).
- **Drag.** The strip follows the finger 1:1. Past the first or last frame it gives half as much (`rubber` .5).
- **Paging.** Letting go pages if the drag went a third of the width, or if it was moving faster than .1 px/ms (and not moving back): one frame per flick, with the release speed handed to the spring.
- **Trackpad.** A horizontal swipe pages once and its momentum is spent (`wheelFlick` 2 px/ms).
- **Dismiss.** A vertical drag lifts the frame off and fades the backdrop by distance. Past 30% of the screen height, or on a flick, it closes.
- **Open and close.** The frame grows out of the thumbnail that was clicked, and closing puts it back when that thumbnail is still on screen. Otherwise it fades and scales (.93 to 1).
- **Reduced motion.** No springs: steps are instant and open/close fades.
- **Chrome.** The backdrop is a real blurred layer, so it can fade with open, close and drag-to-dismiss. Prev / next / close are [dot-matrix buttons](../components/dot-matrix-button.md). A counter `n / N` sits in `.viewer-count`. Below 900px the close button is at top 8px / right 8px and the stage has 48px of top padding.
- **Sound.** `.viewer-stage` is a drag zone for the press/drag/release palette ([sound](../../foundations/sound/sound.md)).

Source: `site/js/viewer.js`, whole file

```js
// The full-screen viewer: a strip of frames moved by one spring.
// Dragging, flicking, the trackpad, the arrows and the keys all push the same spring, so a
// step always lands the same way however it was asked for. The model follows the paging
// physics of mikematas.com (re-written here; numbers in PHYS):
//  - the strip follows the finger 1:1, and past the first or last frame it gives half as much
//  - letting go pages if the drag went a third of the width or was moving faster than 0.1 px/ms
//    (and wasn't moving back), one frame per flick, handing the release speed to the spring
//  - a vertical drag lifts the frame off, the backdrop fading by distance; past 30% of the
//    screen height (or a flick) it closes
//  - opening grows the frame out of the thumbnail that was clicked, and closing puts it back
//    when that thumbnail is still on screen; otherwise it fades and scales (0.93 to 1)
// With prefers-reduced-motion there are no springs: steps are instant and open/close fade.
import { dotIcon } from './gallery.js';
import { reducedMotion } from './state.js';

const PHYS = {
  page: { k: 450, c: 50 },          // paging spring, tension / friction (mass 1)
  pagePhone: { k: 800, c: 80 },     // under 600px wide: stiffer, more damped
  fly: { k: 300, c: 35 },           // open, close and dismiss
  rubber: 0.5,                      // past the ends the strip moves half as far as the finger
  pageDist: 0.33,                   // of the width
  flick: 0.1,                       // px/ms
  wheelFlick: 2,                    // px/ms of trackpad travel
  dismissDist: 0.3,                 // of the screen height
  axisLock: 10,                     // px before a drag commits to an axis
  gap: 14,                          // between frames (2 x 7px)
  dim: 0.15,                        // a neighbour's opacity one frame away
  fallbackScale: 0.93,
};

// ---------- a critically-ish damped spring, integrated in 1ms steps ----------
function spring(cfg, x = 0, onFrame, onRest) {
  const s = { x, v: 0, to: x, cfg, raf: 0 };
  let last = 0;
  const tick = (t) => {
    let dt = Math.min(0.064, (t - last) / 1000 || 0.016); last = t;
    const { k, c } = s.cfg;
    while (dt > 0) { const h = Math.min(dt, 0.001); s.v += (-k * (s.x - s.to) - c * s.v) * h; s.x += s.v * h; dt -= h; }
    if (Math.abs(s.v) < 2 && Math.abs(s.x - s.to) < 0.05) { s.x = s.to; s.v = 0; s.raf = 0; onFrame(s.x); onRest?.(); return; }
    onFrame(s.x);
    s.raf = requestAnimationFrame(tick);
  };
  s.start = () => { if (!s.raf) { last = performance.now(); s.raf = requestAnimationFrame(tick); } };
  s.stop = () => { cancelAnimationFrame(s.raf); s.raf = 0; };
  s.set = (to, v) => { s.to = to; if (v != null) s.v = v; s.start(); };
  s.jump = (x) => { s.stop(); s.x = s.to = x; s.v = 0; onFrame(x); };
  return s;
}

let viewer, stage, track, scrim, list = [], at = 0, title = '', origin = null;
let W = 0, P = 0;                   // frame width, pitch (frame + gap)
let pos = 0;                        // strip offset in px (frame i sits at i * P)
let strip;                          // the paging spring
let lift = { x: 0, y: 0 };          // the current frame lifted by a vertical drag
let busy = false;                   // opening or closing
let hidden = null;                  // the thumbnail hidden while its frame is out
const slides = new Map();           // index -> { el, img }

const reduced = () => reducedMotion.matches;
const lo = () => 0, hi = () => (list.length - 1) * P;
const rubber = (x, a, b) => x < a ? a + PHYS.rubber * (x - a) : x > b ? b - PHYS.rubber * (x - b) : x;
const pageCfg = () => innerWidth < 600 ? PHYS.pagePhone : PHYS.page;

function build() {
  viewer = document.createElement('dialog');
  viewer.className = 'viewer';
  viewer.setAttribute('aria-label', 'Frames, full screen');
  viewer.setAttribute('aria-roledescription', 'carousel');
  viewer.innerHTML = `
    <div class="viewer-scrim" data-close></div>
    <button type="button" class="viewer-btn viewer-close" data-close aria-label="Close" autofocus>${dotIcon('close')}</button>
    <div class="viewer-stage"><div class="viewer-track"></div></div>
    <div class="viewer-bar">
      <span class="viewer-ctrls">
        <button type="button" class="viewer-btn" data-go="-1" aria-label="Previous">${dotIcon('prev')}</button>
        <button type="button" class="viewer-btn" data-go="1" aria-label="Next">${dotIcon('next')}</button>
      </span>
    </div>`;
  document.body.append(viewer);
  stage = viewer.querySelector('.viewer-stage');
  track = viewer.querySelector('.viewer-track');
  scrim = viewer.querySelector('.viewer-scrim');
  strip = spring(pageCfg(), 0, (x) => { pos = x; paint(); });

  let dragged = false;
  viewer.addEventListener('click', (e) => {
    if (dragged) { dragged = false; return; }
    const b = e.target.closest('[data-go]');
    if (b) return go(+b.dataset.go);
    if (busy) return;
    if (e.target.closest('[data-close]') || e.target === stage || e.target === track || e.target.classList.contains('viewer-slide')) return close();
    if (e.target.classList.contains('viewer-img')) return go(1);
  });
  viewer.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') { e.preventDefault(); go(1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); go(-1); }
    else if (e.key === 'Home') { e.preventDefault(); goTo(0); }
    else if (e.key === 'End') { e.preventDefault(); goTo(list.length - 1); }
  });
  viewer.addEventListener('cancel', (e) => { e.preventDefault(); close(); });
  addEventListener('resize', () => { if (viewer.open) { measure(); strip.jump(at * P); } });

  // ---------- pointer drag: mouse and touch alike ----------
  let d = null;                     // { id, x0, y0, p0, axis, hist: [[t, x, y]] }
  stage.addEventListener('pointerdown', (e) => {
    if (busy || e.button !== 0 || e.target.closest('button')) return;
    strip.stop();
    d = { a0: at, id: e.pointerId, x0: e.clientX, y0: e.clientY, p0: pos, axis: null, hist: [[e.timeStamp, e.clientX, e.clientY]] };
  });
  stage.addEventListener('pointermove', (e) => {
    if (!d || e.pointerId !== d.id) return;
    const dx = e.clientX - d.x0, dy = e.clientY - d.y0;
    if (!d.axis) {
      if (Math.hypot(dx, dy) < PHYS.axisLock) return;
      d.axis = Math.abs(dx) >= Math.abs(dy) || list.length < 1 ? 'x' : 'y';
      stage.setPointerCapture(e.pointerId);
      viewer.classList.add('is-dragging');
    }
    d.hist.push([e.timeStamp, e.clientX, e.clientY]);
    if (d.hist.length > 6) d.hist.shift();
    if (d.axis === 'x') { pos = rubber(d.p0 - dx, lo(), hi()); strip.x = strip.to = pos; paint(); }
    else { lift = { x: 0, y: dy }; paint(); }
  });
  const up = (e) => {
    if (!d || e.pointerId !== d.id) return;
    const g = d; d = null;
    viewer.classList.remove('is-dragging');
    if (!g.axis) { if (strip.x !== at * P) strip.set(at * P); return; }
    dragged = true; setTimeout(() => { dragged = false; }, 0);
    // release speed, px/ms, over the last ~80ms of the drag
    const [t0, x0, y0] = g.hist.find(h => e.timeStamp - h[0] < 80) || g.hist[0];
    const span = Math.max(1, e.timeStamp - t0);
    const vx = (e.clientX - x0) / span, vy = (e.clientY - y0) / span;
    if (g.axis === 'x') {
      const dx = e.clientX - g.x0, dir = dx < 0 ? 1 : -1;
      const pages = shouldPage(Math.abs(dx), -dir * vx, W * PHYS.pageDist, PHYS.flick);
      settle(pages ? g.a0 + dir : g.a0, -vx * 1000);
    } else {
      const dy = e.clientY - g.y0;
      if (shouldPage(Math.abs(dy), Math.sign(dy || 1) * vy, innerHeight * PHYS.dismissDist, PHYS.flick)) close(vy * 1000);
      else liftBack(vy * 1000);
    }
  };
  stage.addEventListener('pointerup', up);
  stage.addEventListener('pointercancel', up);

  // ---------- trackpad: a horizontal swipe pages once, its momentum is spent ----------
  let w = null;                     // { dx, hist, paged, quiet }
  stage.addEventListener('wheel', (e) => {
    if (busy || Math.abs(e.deltaX) <= Math.abs(e.deltaY)) return;
    e.preventDefault();
    if (!w) { strip.stop(); w = { dx: 0, p0: pos, hist: [], paged: false }; }
    clearTimeout(w.quiet);
    w.quiet = setTimeout(() => { if (!w.paged) settle(at); w = null; }, 140);
    if (w.paged) return;
    w.dx += e.deltaX;
    w.hist.push([e.timeStamp, e.deltaX]); if (w.hist.length > 5) w.hist.shift();
    const span = Math.max(16, e.timeStamp - w.hist[0][0]);
    const v = w.hist.reduce((s, h) => s + h[1], 0) / span;          // px/ms, + is forward
    const dir = w.dx > 0 ? 1 : -1;
    if (shouldPage(Math.abs(w.dx), dir * v, W * PHYS.pageDist, PHYS.wheelFlick) && list[at + dir]) {
      w.paged = true; settle(at + dir, v * 1000);
      return;
    }
    pos = rubber(w.p0 + w.dx, lo(), hi()); strip.x = strip.to = pos; paint();
  }, { passive: false });
}

// far enough, or fast enough, and not moving back the other way
const shouldPage = (dist, v, distMin, vMin) => (dist > distMin || v > vMin) && v > -vMin;

function measure() {
  const r = track.getBoundingClientRect();
  W = r.width; P = W + PHYS.gap;
  strip.cfg = pageCfg();
}

// draw the frames near the strip's position; build them as they come into reach
function paint() {
  if (!P) return;
  const c = pos / P, from = Math.max(0, Math.floor(c) - 1), to = Math.min(list.length - 1, Math.ceil(c) + 1);
  for (const [i, s] of slides) if (i < from || i > to) { s.el.remove(); slides.delete(i); }
  const H = innerHeight;
  for (let i = from; i <= to; i++) {
    const s = slides.get(i) || makeSlide(i);
    const off = i * P - pos, k = Math.min(1, Math.abs(off) / P);
    let tx = off, ty = 0, sc = 1;
    if (i === at && (lift.x || lift.y)) { tx += lift.x; ty = lift.y; sc = 1 - 0.15 * Math.min(1, Math.abs(lift.y) / H); }
    s.el.style.transform = `translate3d(${tx}px, ${ty}px, 0) scale(${sc})`;
    s.el.style.opacity = reduced() ? (i === at ? 1 : 0) : 1 - (1 - PHYS.dim) * k;
  }
  // the backdrop and the buttons fade as the frame is lifted away
  const f = 1 - Math.min(1, Math.abs(lift.y) / (H * 0.6));
  scrim.style.opacity = f; viewer.style.setProperty('--chrome', f);
}

function makeSlide(i) {
  const el = document.createElement('div');
  el.className = 'viewer-slide';
  el.setAttribute('role', 'group');
  el.setAttribute('aria-roledescription', 'slide');
  const img = new Image();
  img.className = 'viewer-img'; img.decoding = 'async'; img.draggable = false;
  img.alt = altOf(i); img.src = list[i];
  el.append(img); track.append(el);
  const s = { el, img }; slides.set(i, s);
  return s;
}
const altOf = (i) => Array.isArray(title) ? title[i] : `${title}, frame ${i + 1} of ${list.length}`;

function setAt(i) {
  const was = at; at = i;
  slides.forEach((s, k) => s.el.setAttribute('aria-hidden', k === at ? 'false' : 'true'));
  viewer.querySelector('[data-go="-1"]').disabled = at === 0;
  viewer.querySelector('[data-go="1"]').disabled = at === list.length - 1;
  // the thumbnail behind follows, so closing lands in the right place
  if (was !== at && hidden) { showThumb(); hideThumb(); }
  [at + 2, at - 2].forEach(k => { if (list[k]) { const p = new Image(); p.src = list[k]; } });
}

// move to a frame through the spring; at the ends, a small bump against the wall
function settle(i, v) {
  i = Math.max(0, Math.min(list.length - 1, i));
  if (reduced()) { strip.jump(i * P); setAt(i); return; }
  setAt(i); strip.cfg = pageCfg(); strip.set(i * P, v);
}
function go(d) {
  if (busy || list.length < 2) return;
  const i = at + d;
  if (!list[i]) { if (!reduced()) strip.set(at * P, d * 1400); return; }
  settle(i);
}
function goTo(i) { if (!busy) settle(i); }

// a lifted frame springs back into place
function liftBack(vy = 0) {
  if (reduced()) { lift = { x: 0, y: 0 }; paint(); return; }
  const s = spring(PHYS.fly, lift.y, (y) => { lift.y = y; paint(); });
  s.v = vy; s.set(0);
}

// ---------- the thumbnail the frame came from ----------
const thumbOf = (i) => {
  const el = origin?.(i);
  if (!el?.isConnected) return null;
  const r = el.getBoundingClientRect();
  return r.width > 0 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth ? { el, r } : null;
};
function hideThumb() { const t = origin?.(at); if (t) { t.style.visibility = 'hidden'; hidden = t; } }
function showThumb() { if (hidden) hidden.style.visibility = ''; hidden = null; }

// the frame's picture as it is laid out, without the transforms on it
function restRect(img) {
  const t = track.getBoundingClientRect();
  const nw = img.naturalWidth || 4, nh = img.naturalHeight || 3;
  const s = Math.min(t.width / nw, t.height / nh, 1);          // as the CSS lays it: fit, never enlarge
  const w = nw * s, h = nh * s;
  return { left: t.left + (t.width - w) / 2, top: t.top + (t.height - h) / 2, width: w, height: h };
}

// spring a frame from one rectangle to another (p runs 0 to 1); fade the backdrop along with it
function fly(img, from, to, { v = 0, scrimFrom, scrimTo, fade, onDone }) {
  const L = restRect(img);
  const lerp = (a, b, p) => a + (b - a) * p;
  const s = spring(PHYS.fly, 0, (p) => {
    const w = lerp(from.width, to.width, p), x = lerp(from.left + from.width / 2, to.left + to.width / 2, p), y = lerp(from.top + from.height / 2, to.top + to.height / 2, p);
    img.style.transform = `translate3d(${x - (L.left + L.width / 2)}px, ${y - (L.top + L.height / 2)}px, 0) scale(${w / L.width})`;
    const q = Math.max(0, Math.min(1, p));
    scrim.style.opacity = lerp(scrimFrom, scrimTo, q);
    viewer.style.setProperty('--chrome', lerp(scrimFrom, scrimTo, q));
    if (fade) img.style.opacity = lerp(fade[0], fade[1], q);
  }, onDone);
  s.v = v; s.set(1);
}

// open: grow out of the thumbnail when we have it, else fade and scale up
export function openViewer(frames, i, t, from) {
  if (!viewer) build();
  list = frames; title = t; origin = typeof from === 'function' ? from : null;
  slides.forEach(s => s.el.remove()); slides.clear();
  lift = { x: 0, y: 0 }; at = i;
  viewer.classList.toggle('is-single', list.length < 2);
  viewer.showModal();
  measure(); strip.jump(i * P); setAt(i);
  const s = slides.get(i); if (!s) return;
  if (reduced()) {
    viewer.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 160, easing: 'linear' });
    return;
  }
  const th = thumbOf(i);
  busy = true;
  scrim.style.opacity = 0; viewer.style.setProperty('--chrome', 0);
  s.img.style.opacity = 0;
  const ready = s.img.decode ? Promise.race([s.img.decode().catch(() => {}), new Promise(r => setTimeout(r, 300))]) : Promise.resolve();
  ready.then(() => {
    if (!viewer.open) return;
    const end = restRect(s.img);
    const done = () => { busy = false; s.img.style.transform = ''; s.img.style.opacity = ''; };
    if (th && s.img.naturalWidth) {
      hideThumb();
      s.img.style.opacity = '';
      fly(s.img, th.r, end, { scrimFrom: 0, scrimTo: 1, onDone: done });
    } else {
      const k = PHYS.fallbackScale, c = { left: end.left + end.width * (1 - k) / 2, top: end.top + end.height * (1 - k) / 2, width: end.width * k, height: end.height * k };
      fly(s.img, c, end, { scrimFrom: 0, scrimTo: 1, fade: [0, 1], onDone: done });
    }
  });
}

// close: back into the thumbnail if it is on screen, else fade and scale down; v carries a flick
function close(v = 0) {
  if (!viewer?.open || busy) return;
  const s = slides.get(at);
  const end = () => { busy = false; showThumb(); lift = { x: 0, y: 0 }; viewer.close(); slides.forEach(x => x.el.remove()); slides.clear(); };
  if (reduced() || !s) {
    if (!s) return end();
    busy = true;
    viewer.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 160, easing: 'linear' }).onfinish = end;
    return;
  }
  busy = true; strip.stop();
  // fold the lift into the picture's own transform, so the flight starts where the finger let go
  const now = s.img.getBoundingClientRect();
  const sf = Number(scrim.style.opacity || 1);
  lift = { x: 0, y: 0 }; paint();
  scrim.style.opacity = sf;
  s.el.style.transform = 'none';
  const th = thumbOf(at);
  if (th) {
    if (!hidden) hideThumb();
    fly(s.img, now, th.r, { scrimFrom: sf, scrimTo: 0, onDone: end });
  } else {
    const k = PHYS.fallbackScale, r = restRect(s.img);
    const to = { left: r.left + r.width * (1 - k) / 2, top: r.top + r.height * (1 - k) / 2 + Math.sign(v) * innerHeight * 0.25 * Math.min(1, Math.abs(v) / 1000), width: r.width * k, height: r.height * k };
    fly(s.img, now, to, { scrimFrom: sf, scrimTo: 0, fade: [1, 0], onDone: end });
  }
}
```


Source: `site/css/site.css`, lines 476 to 503

```css
/* the full-screen viewer */
.viewer { position: fixed; inset: 0; width: 100vw; height: 100dvh; max-width: none; max-height: none; margin: 0; padding: 0; border: 0; background: transparent; color: var(--ink); display: none; }
.viewer[open] { display: grid; grid-template-rows: minmax(0, 1fr) auto; }
.viewer { overflow: hidden; overflow: clip; }  /* clip: the strip runs past the edges and must never scroll the dialog */
/* the blurred backdrop is a real layer, so it can fade with the open, close and drag-to-dismiss */
.viewer::backdrop { background: transparent; }
.viewer-scrim { position: fixed; inset: 0; background: color-mix(in srgb, var(--paper) 52%, transparent); -webkit-backdrop-filter: blur(28px) saturate(1.15); backdrop-filter: blur(28px) saturate(1.15); }
.viewer-stage { position: relative; display: grid; min-height: 0; padding: 32px 32px 8px; cursor: zoom-out; touch-action: none; user-select: none; -webkit-user-select: none; }
.viewer-track { position: relative; min-width: 0; min-height: 0; }
.viewer-slide { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; will-change: transform; }
.viewer-img { display: block; max-width: 100%; max-height: 100%; width: auto; height: auto; object-fit: contain; cursor: grab; transform-origin: center; -webkit-user-drag: none; border-radius: 16px; box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 8%, transparent), 0 24px 64px -24px color-mix(in srgb, var(--shadow) calc(25% * var(--shadow-k)), transparent); }
.viewer.is-dragging .viewer-stage, .viewer.is-dragging .viewer-img { cursor: grabbing; }
.viewer-bar, .viewer-close { opacity: var(--chrome, 1); }
.viewer-bar { position: relative; }
.viewer.is-single .viewer-ctrls { display: none; }
.viewer-btn:disabled { opacity: .25; cursor: default; }
.viewer-bar { display: flex; align-items: center; justify-content: center; gap: 16px; min-height: 32px; padding: 12px 24px 20px; font: 400 16px/20px var(--ui); letter-spacing: var(--track); }
.viewer-title { flex: 0 1 auto; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.viewer-count { color: color-mix(in srgb, var(--ink) 50%, var(--paper)); font-variant-numeric: tabular-nums; }
.viewer-ctrls { display: flex; gap: 8px; }
.viewer-close { position: absolute; top: 16px; right: 16px; z-index: 1; }
.viewer-stage { padding-inline: 64px; }
.viewer-btn { width: 32px; height: 32px; display: grid; place-items: center; padding: 0; border: 0; border-radius: 8px; background: none; color: color-mix(in srgb, var(--ink) 60%, var(--paper)); cursor: pointer; }
.viewer-btn svg { width: 16px; height: 16px; }
.viewer-btn:hover, .viewer-btn:focus-visible { color: var(--ink); background: color-mix(in srgb, var(--ink) 6%, transparent); outline: none; }
.viewer-btn[hidden] { display: none; }
@media (max-width: 899px) { .viewer-stage { padding: 16px 12px 4px; } .viewer-bar { padding: 10px 12px 16px; } }
```
