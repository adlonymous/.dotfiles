---
title: Emergence
slug: emergence
status: published
description: "Resonance and tiers: content that unfolds as attention grows. Switched off on the live site (EMERGENCE = false); every published page shows."
chips:
  - Motion
  - Emergence
  - Resonance
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:02:22Z
---

**Status on the live site: off.** `js/emergence.js` has `export const EMERGENCE = false` ("OFF for now (Ahmed, Nov 9): every published page shows from the first visit"). With it off, `OPEN` is true. `tick()` returns early, so no score accrues from reading, nothing is queued, no orbs appear and the wordmark's life stays at its stored level, which is 0 for a new visitor. Rebuild it switched off. The spec below is for turning it back on.

## Resonance

A hidden score that grows with attention, in `RESONANCE` (`js/tokens.js`):

| Source | Score |
|---|---|
| each second of active reading (body on screen, tab focused, input in the last 30s) | +.25 |
| idle (no input for 30s) | −.05 a second, never below the floor of the tier reached |
| scrolling a piece | +8 × the new depth reached (0 to 1) |
| opening a piece for the first time | +6 |
| finishing a piece (depth ≥ .98 and read time ≥ 40% of words / 5 wps) | +15 |
| a return visit on another day (Toronto) | +30 |
| a slow hover (600ms) on a new target | +1.5 |
| a secret found | +10 |

Tiers: `TIERS = [0, 25, 60, 150, 260, 400]` (tier 0 to 5). Each tier warms the sound bed (×(1 + .22·tier)).

## Reveals

Each content node can carry `reveal: { tier: n }` or `reveal: { secret: 'id' }`, or both. One reveal at a time: at least `EMERGE.cooldownMs` 4000ms apart, never within `quietAfterNavMs` 1400ms of a route change, and never while the tab is hidden. A reveal emits `emerge` (sound: the rising arpeggio and shimmer; haptics [12, 40, 8, 40, 20]). It re-renders through `transition(..., { kind: 'emerge' })` (816ms, amplitude ×1.35), announces "New: title" to screen readers, and places the orbs after `orbDelay` .75 of the duration.

- **Storage:** `sd.resonance` (score, days, depth, reading, finished, secrets), `sd.revealed`, `sd.opened`, `sd.badges`.
- **Query parameters:** `?reset` clears it; `?tier=n` jumps to tier n; `?open` (locally) shows everything.
- **Life:** `life()` = progress through the tiers (0 to 1) plus `LIFE.perSecret` .08 per secret. It drives the wordmark's stages ([webgl](webgl.md)).

Source: `site/js/emergence.js`, whole file

```js
// The emergence engine. A hidden resonance score grows with attention; tiers
// and secrets reveal nodes of the content graph one at a time. Nothing is
// generated: it only unfolds what js/content.js already holds.
//
// Storage: sd.resonance (score, days, depth, reading, finished, secrets),
// sd.revealed, sd.opened, sd.badges. ?reset clears it; ?tier=n jumps there.
import { bus } from './state.js';
import { NODES, BY_ID, revealOf, sectionVisible, itemVisible, wordCount, editorViewOn } from './content.js';
import { RESONANCE as W, TIERS, EMERGE } from './tokens.js';

const K = { res: 'sd.resonance', revealed: 'sd.revealed', opened: 'sd.opened', badges: 'sd.badges' };
const load = (k, d) => { try { const v = JSON.parse(localStorage.getItem(k)); return v ?? d; } catch (e) { return d; } };
const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };

const torontoParts = (d = new Date()) => Object.fromEntries(new Intl.DateTimeFormat('en-CA', {
  timeZone: 'America/Toronto', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', hourCycle: 'h23'
}).formatToParts(d).map(p => [p.type, p.value]));

const qs = new URLSearchParams(location.search);
if (qs.has('reset')) {
  Object.values(K).forEach(k => localStorage.removeItem(k));
  qs.delete('reset');
  history.replaceState(null, '', location.pathname + (qs.toString() ? '?' + qs : '') + location.hash);
}

// ?open, locally (the CMS preview): every page shown, night included, nothing stored
const EDITOR = editorViewOn();
// Emergence (content hidden until a visitor's interest grows, plus the hidden extras) is
// OFF for now (Ahmed, Nov 9): every published page shows from the first visit.
// Set EMERGENCE = true to bring it back; levels, secrets and the wordmark's life still count.
export const EMERGENCE = false;
const OPEN = !EMERGENCE || ((qs.has('open') || EDITOR) && (['localhost', '127.0.0.1', '[::1]'].includes(location.hostname) || location.protocol === 'file:'));

const res = Object.assign({ score: 0, lastDay: null, visits: 0, depth: {}, read: {}, finished: [], secrets: [], by: {} }, load(K.res, {}));
res.by = res.by || {};
const revealed = new Set(load(K.revealed, []));
const opened = new Set(load(K.opened, []));
const badges = new Set(load(K.badges, []));
const secrets = new Set(res.secrets);
const finished = new Set(res.finished);
let nightOverride = null;

function isNight() {
  if (OPEN) return true;
  if (nightOverride != null) return nightOverride;
  const h = Number(torontoParts().hour);
  return h >= 23 || h < 5;
}

// the view the renderer uses
export const vis = {
  has: (id) => OPEN || revealed.has(id),
  get night() { return isNight(); }
};

export function tier() { let t = 0; TIERS.forEach((v, i) => { if (res.score >= v) t = i; }); return t; }
export const isBadged = (id) => badges.has(id);
export const badgeList = () => [...badges];

function persist() {
  if (OPEN) return;
  res.secrets = [...secrets]; res.finished = [...finished];
  save(K.res, res); save(K.revealed, [...revealed]); save(K.opened, [...opened]); save(K.badges, [...badges]);
}

function condMet(node) {
  const r = node.reveal; // own condition only (inheriting nodes are not queued)
  if (!r) return true;
  if (r.tier != null && tier() < r.tier) return false;
  if (r.secret && !secrets.has(r.secret)) return false;
  if (node.night && !isNight()) return false;
  return true;
}
function parentVisible(node) {
  if (node.kind === 'section') return true;
  if (node.kind === 'item') return (node.reveal && node.reveal.secret) ? true : sectionVisible(node.section, vis);
  return itemVisible(node.item, vis);
}
function pending() {
  return NODES.filter(n => !revealed.has(n.id) && condMet(n) && parentVisible(n))
    .sort((a, b) => (b.reveal.secret ? 1 : 0) - (a.reveal.secret ? 1 : 0) || (a.reveal.tier ?? 0) - (b.reveal.tier ?? 0));
}

let onReveal = () => {};
let lastReveal = -1e9, lastNav = -1e9;
let lastTier = tier();

function reveal(node, { silent = false } = {}) {
  revealed.add(node.id);
  if (!silent) {
    badges.add(node.id);
    lastReveal = performance.now();
  }
  persist();
  if (!silent) {
    const title = node.kind === 'para' ? node.item.title : node.title;
    bus.emit('emerge', { node, title, tier: tier() });
    onReveal(node, title);
  }
}

// silently reveal everything that is due (first visit, or a ?tier jump)
function settle(badgeTier = null) {
  for (let pass = 0; pass < 6; pass++) {
    const due = pending();
    if (!due.length) break;
    due.forEach(n => { revealed.add(n.id); if (badgeTier && n.reveal.tier === badgeTier) badges.add(n.id); });
  }
  persist();
}

// src: which kind of attention it came from (the debug panel shows the breakdown)
function addScore(v, floorAtTier = false, src = 'other') {
  const before = tier();
  const was = res.score;
  res.score = Math.max(floorAtTier ? TIERS[before] : 0, res.score + v);
  res.by[src] = (res.by[src] || 0) + (res.score - was);
  const t = tier();
  if (t !== lastTier) { lastTier = t; bus.emit('resonance', { score: res.score, tier: t }); }
}

// ---------- attention ----------
let lastActivity = performance.now();
['pointermove', 'pointerdown', 'scroll', 'keydown', 'touchstart', 'wheel'].forEach(t =>
  window.addEventListener(t, () => { lastActivity = performance.now(); }, { passive: true, capture: true }));

let current = null; // the open item
let articleEl = null;
const hovered = new Set();

export function slowHover(key) {
  if (!key || hovered.has(key)) return;
  hovered.add(key); addScore(W.slowHover, false, 'hovers');
}

export function opened_(item) {
  current = item;
  lastNav = performance.now();
  if (!opened.has(item.id)) { opened.add(item.id); addScore(W.pieceOpened, false, 'pieces'); }
  // opening a piece clears its badges (and its section's once nothing new is left in it)
  const cleared = [];
  [item.id, ...item.paras.map(p => p.id)].forEach(id => { if (badges.delete(id)) cleared.push(id); });
  if (badges.delete(item.section.id)) cleared.push(item.section.id);
  persist();
  return cleared;
}
export { opened_ as openPiece };
// a page that is not a piece (Settings): nothing is being read
export function closePiece() { current = null; }

// secrets: returns the nodes it unlocked (revealed at once, ahead of the queue)
export function unlock(id) {
  if (secrets.has(id)) return [];
  secrets.add(id);
  addScore(W.secretFound, false, 'secrets');
  persist();
  bus.emit('secret', { id });
  const out = [];
  for (let pass = 0; pass < 3; pass++) {
    const due = pending().filter(n => n.reveal.secret === id);
    if (!due.length) break;
    due.forEach(n => { reveal(n); out.push(n); });
  }
  return out;
}
export const hasSecret = (id) => secrets.has(id);
export const nodeFor = (secret) => NODES.find(n => n.reveal && n.reveal.secret === secret && n.kind !== 'para');

// secret (d): being here at night, Toronto time, is the whole of the secret
function checkNight() { if (OPEN) return; if (isNight() && !secrets.has('night') && document.visibilityState === 'visible') unlock('night'); }

function tick() {
  if (OPEN) return;
  checkNight();
  const now = performance.now();
  const visible = document.visibilityState === 'visible' && document.hasFocus();
  const idle = (now - lastActivity) / 1000 > W.idleAfter;
  if (current && articleEl && visible) {
    const r = articleEl.getBoundingClientRect();
    const onScreen = r.bottom > 0 && r.top < innerHeight;
    if (onScreen && !idle) {
      addScore(W.readSecond, false, 'reading');
      res.read[current.id] = (res.read[current.id] || 0) + 1;
    }
    // deepest point reached in this piece
    const depth = Math.max(0, Math.min(1, (innerHeight - r.top) / Math.max(1, r.height)));
    const prev = res.depth[current.id] || 0;
    if (depth > prev) { addScore((depth - prev) * W.scrollDepth, false, 'scroll'); res.depth[current.id] = depth; }
    // finished: reached the end, having read at least 40% of skim time
    if (!finished.has(current.id) && depth >= 0.98 &&
        (res.read[current.id] || 0) >= 0.4 * wordCount(current, vis) / W.skimWordsPerSecond) {
      finished.add(current.id); addScore(W.finishPiece, false, 'finishes');
    }
  }
  if (idle && visible) addScore(-W.idleDecay, true, 'idle');

  // one thing at a time, never on top of a route change, never while nobody can see it
  if (document.visibilityState === 'visible' && now - lastReveal >= EMERGE.cooldownMs && now - lastNav >= EMERGE.quietAfterNavMs) {
    const next = pending()[0];
    if (next) reveal(next);
  }
  if (Math.round(now / 1000) % 5 === 0) persist();
}

export function setArticle(el) { articleEl = el; }

export function init(handler) {
  onReveal = handler;
  // a return visit, on another day in Toronto
  const p = torontoParts();
  const day = `${p.year}-${p.month}-${p.day}`;
  if (res.lastDay && res.lastDay !== day) addScore(W.returnVisit, false, 'returns');
  if (res.lastDay !== day) res.visits++;
  res.lastDay = day;
  // review: ?tier=n
  const qt = qs.get('tier');
  if (qt != null && TIERS[Number(qt)] != null) {
    res.score = Math.max(res.score, TIERS[Number(qt)]);
    settle(Number(qt));
  } else {
    // tier 0 arrives silently; anything else due waits in the queue
    const t0 = NODES.filter(n => revealOf(n) && revealOf(n).tier === 0 && !n.reveal.secret);
    t0.forEach(n => revealed.add(n.id));
    persist();
  }
  lastTier = tier();
  lastReveal = performance.now() - EMERGE.cooldownMs + 2500; // the first emergence waits a moment
  setInterval(tick, 1000);
  window.addEventListener('pagehide', persist);
  // review keys (with the backquote aid on): u = next tier, n = pretend night, r = reset
  window.addEventListener('sd:review', (e) => {
    if (e.detail === 'u') { const t = tier(); if (TIERS[t + 1] != null) addScore(TIERS[t + 1] - res.score, false, 'review'); }
    if (e.detail === 'n') nightOverride = !isNight();
    if (e.detail === 'r') { Object.values(K).forEach(k => localStorage.removeItem(k)); location.reload(); }
  });
  bus.emit('resonance', { score: res.score, tier: tier() });
}

import { LIFE } from './tokens.js';
// continuous: progress through the tiers (0 to 1) plus a little per secret
export function life() {
  const t = tier();
  const frac = TIERS[t + 1] != null ? (res.score - TIERS[t]) / (TIERS[t + 1] - TIERS[t]) : 0;
  return Math.min(1, (t + Math.max(0, Math.min(1, frac))) / (TIERS.length - 1) + LIFE.perSecret * secrets.size);
}
export function state() { return { score: res.score, tier: tier(), revealed: [...revealed], secrets: [...secrets], badges: [...badges] }; }

// ---------- for the local debug panel (js/debug) ----------
export const debug = {
  snapshot: () => ({
    score: res.score, tier: tier(), life: life(), by: { ...res.by }, visits: res.visits,
    queue: pending().map(n => n.id), cooldownMs: Math.max(0, EMERGE.cooldownMs - (performance.now() - lastReveal)),
    revealed: revealed.size, badged: badges.size, opened: opened.size, secrets: [...secrets], night: isNight(), current: current?.id || null
  }),
  status(id) { return opened.has(id) ? 'opened' : badges.has(id) ? 'badged' : revealed.has(id) ? 'revealed' : 'hidden'; },
  setTier(n) { if (TIERS[n] == null) return; const t = tier(); if (n > t) addScore(TIERS[n] - res.score, false, 'review'); else { res.score = TIERS[n]; lastTier = n; bus.emit('resonance', { score: res.score, tier: n }); } persist(); },
  addScore(v) { addScore(v, false, 'review'); persist(); },
  emergeNext() { const n = pending()[0]; if (n) reveal(n); return n?.id || null; },
  unlock: (id) => unlock(id),
  secretIds: () => [...new Set(NODES.filter(n => n.reveal && n.reveal.secret).map(n => n.reveal.secret))],
  resetAll() { Object.values(K).forEach(k => localStorage.removeItem(k)); location.reload(); }
};
export { BY_ID };
```


## In app.js

Source: `site/js/app.js`, lines 497 to 531

```js
// ---------- emergence: something new resolves into place ----------
function onReveal(node, title) {
  announce(`New: ${title}`);
  updateLife();
  if (!route) return;
  const dur = transition(() => render(route), { body: true, kind: 'emerge', section: route.sectionIndex, sectionSlug: (node.section || node.item?.section || node).slug });
  // a new paragraph in the piece being read is seen at once: no orb for it
  if (node.kind === 'para' && node.item === route.item) E.openPiece(route.item);
  setTimeout(syncOrbs, (dur || 0) * EMERGE.orbDelay);
}

// ---------- the wordmark's life: the visible resonance meter ----------
function lifeValue() {
  const forced = params.life;
  if (forced > 0) return forced;
  return E.life();
}
function updateLife() {
  gl?.setLife(lifeValue());
  gl?.setTraces(E.state().secrets);
}
bus.on('resonance', updateLife);
bus.on('secret', updateLife);
bus.on('params', updateLife);

// secrets that open a piece go there once it has emerged
function openSecret(id) {
  const fresh = E.unlock(id);
  const node = E.nodeFor(id);
  if (!node) return;
  const hash = node.kind === 'section' ? `#/${node.slug}` : `#/${node.section.slug}/${node.slug}`;
  if (fresh.length) setTimeout(() => { location.hash = hash; }, 1500);
  else location.hash = hash;
}
```
