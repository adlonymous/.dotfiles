---
title: Navigation
slug: navigation
status: published
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Two lists on the left of every page: the rooms (column 1) and the pages of the current room (column 2). Plain words, no icons, no underlines, no blur. The current item is full ink; everything else recedes to about 39% opacity.

## Markup (desktop and phone are the same DOM)

```html
<nav class="col col-nav" aria-label="Sections">
  <button type="button" class="nav-btn" aria-label="Menu" aria-expanded="false" aria-controls="nav-sheet">
    <span class="nav-btn-l" aria-hidden="true"></span><span class="nav-btn-l" aria-hidden="true"></span>
  </button>
  <ul id="nav">
    <li><a class="item is-active" href="#/welcome" aria-current="page" data-morph="nav-welcome" data-node="room:welcome">Welcome</a></li>
    <li><a class="item" href="#/articles" data-morph="nav-articles" data-node="room:articles">Articles</a></li>
    <li><a class="item" href="#/lectures" data-morph="nav-lectures" data-node="room:lectures">Lectures</a></li>
    <li><a class="item" href="#/talks" data-morph="nav-talks" data-node="room:talks">Speaking</a></li>
    <li><a class="item" href="#/experiments" data-morph="nav-experiments" data-node="room:experiments">Experiments</a></li>
    <li><a class="item" href="#/library" data-morph="nav-library" data-node="room:library">Library</a></li>
    <li><a class="item" href="#/coffee-table" data-morph="nav-coffee-table" data-node="room:coffee-table">Coffee table</a></li>
    <li class="nav-step"><a class="item" href="#/theme" data-morph="nav-theme" data-node="page-theme">Theme</a></li>
    <li><a class="item" href="#/sound" data-morph="nav-sound" data-node="page-sound">Sound</a></li>
    <li><a class="item" href="#/mcp" data-morph="nav-mcp" data-node="page-mcp">MCP</a></li>
  </ul>
</nav>
<nav class="col col-sub" aria-label="In this section">
  <ul id="sub" aria-label="Welcome">
    <li><a class="item" href="mailto:…" data-morph="sub-connect-email" data-node="connect/email">Email</a></li>
    <li><a class="item" href="https://cal.com/ahmed-saleh/30min" target="_blank" rel="noopener" aria-label="Book a meeting (opens in a new tab)">Book a meeting</a></li>
    <li><a class="item" href="https://x.com/saleh_digital" target="_blank" rel="noopener" aria-label="X/Twitter (opens in a new tab)">X/Twitter</a></li>
    <li><a class="item" href="https://www.linkedin.com/in/saleh-ahmed/" target="_blank" rel="noopener" aria-label="LinkedIn (opens in a new tab)">LinkedIn</a></li>
  </ul>
</nav>
```

These are the live menu labels at `/`, in this order (checked 2026-11-11 after that day's site sync). Seven rooms, then a step of air, then the three app pages Theme, Sound and MCP (until that sync the menu was Articles … Coffee table, then Contact and Settings). Column 2 lists only the pages of the current room: on Welcome it is the ways to reach Ahmed; on Articles the one article title; on Lectures it is "Philosophy of design" and "Lead UX and Product Design Instructor".

## CSS

```css
.col ul { display: flex; flex-direction: column; gap: var(--stack); }      /* 16px lines, 4px apart */
.item { display: inline-block; white-space: nowrap; opacity: var(--op-rest); filter: url(#ink-ui); outline: none; }
.item.is-peek   { opacity: var(--op-peek); filter: url(#ink-ui); }           /* hover / attention */
.item.is-active { opacity: 1; filter: url(#ink-ui); }
.col-nav .item.is-active { color: var(--accent-text); }
.item:focus-visible { opacity: 1; filter: url(#ink-ui); text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; }
.col-nav .nav-step { margin-top: calc(var(--para) - var(--stack)); }        /* 12px: Theme starts a new group */
.sub-group { opacity: var(--op-meta); filter: url(#ink-ui); white-space: nowrap; cursor: default; user-select: none; }
.sub-group:not(:first-child), .sub-one:not(:first-child) { margin-top: calc(var(--para) - var(--stack)); }
/* a long page title wraps instead of widening the column */
.col-sub .item { white-space: normal; max-width: 100%; text-wrap: balance; }
```

`--op-rest` is `calc(.85 - .766 * var(--fnd-focus))` = 0.3904 at the default focus. Resting items are only faded, never blurred.

Type: the menu inherits `body` (`400 16px/16px var(--ui)`, tracking `-0.64px`).

## Phone (below 900px): the two-line glyph and a bottom sheet

`<html>` carries `class="has-nav-sheet"`. Below 900px the `#nav` list is hidden and the glyph shows at the top left. Column 2 (the current page title) stays visible under it.

```css
.nav-btn { display: none; }
.nav-sheet { display: none; }
@media (max-width: 899px) {
  html.has-nav-sheet .col-nav #nav { display: none; }
  .nav-btn { display: grid; align-content: center; justify-items: start; gap: 6px; width: 44px; height: 44px;
    margin: -12px 0 -12px -12px; padding: 0 12px; border: 0; background: none; color: var(--ink); cursor: pointer;
    -webkit-tap-highlight-color: transparent; filter: url(#ink-ui); }
  .nav-btn-l { display: block; width: 20px; height: 1.5px; border-radius: 1px; background: currentColor;
    transition: transform 240ms var(--ease-land), width 240ms var(--ease-land); }
  .nav-btn-l + .nav-btn-l { width: 13px; }                     /* the short second line */
  .nav-btn:hover .nav-btn-l + .nav-btn-l { width: 20px; }
  .nav-btn[aria-expanded="true"] .nav-btn-l { width: 20px; transform: translateY(3.75px) rotate(45deg); }
  .nav-btn[aria-expanded="true"] .nav-btn-l + .nav-btn-l { transform: translateY(-3.75px) rotate(-45deg); }
}
```

So on a 390px phone: the two lines start at x 12, the first 20px long and the second 13px, centred in a 44px tap target that overhangs the 20px top padding; the page title starts 20px under the glyph row; the post starts 28px under the title.

The glyph opens `<dialog id="nav-sheet" class="nav-sheet">`, a liquid-glass bottom sheet:

```css
@media (max-width: 899px) {
  .nav-sheet[open] { display: block; position: fixed; inset: auto 0 0 0; width: 100%; max-width: none; max-height: 85dvh; margin: 0;
    padding: 0 0 max(24px, env(safe-area-inset-bottom)); overflow: auto; overscroll-behavior: contain;
    border: 0; border-radius: 16px 16px 0 0; color: var(--ink); font: 400 16px/20px var(--ui); letter-spacing: var(--track);
    background: color-mix(in srgb, var(--paper) 68%, transparent);
    -webkit-backdrop-filter: blur(20px) saturate(1.3); backdrop-filter: blur(20px) saturate(1.3);
    box-shadow: inset 0 1px 0 color-mix(in srgb, var(--paper) 62%, transparent),
                inset 0 0 0 1px color-mix(in srgb, var(--ink) 7%, transparent),
                0 -12px 40px color-mix(in srgb, var(--shadow) calc(16% * var(--shadow-k)), transparent); }
  .nav-sheet::backdrop { background: color-mix(in srgb, var(--shadow) 20%, transparent); }
  .nav-sheet-grab { display: grid; place-items: center; height: 28px; }
  .nav-sheet-grab span { width: 36px; height: 4px; border-radius: 2px; background: color-mix(in srgb, var(--ink) 18%, transparent); }
  .nav-sheet nav { padding: 4px 24px 0; }
  .nav-sheet-list li { padding: 9px 0; }
  .nav-sheet-list .item { font: 400 24px/28px var(--ui); letter-spacing: -0.96px; opacity: var(--op-meta); }
  .nav-sheet-list .item.is-active { opacity: 1; color: var(--accent-text); }
}
```

The sheet lists the same eight items as `#nav`, drags down to close, and closes on Escape or a tap on the scrim.

## Rules

- Exactly these labels; do not add Home, Recent, Work or icons.
- No underline at rest, no blur on inactive items.
- On phones, never show the menu as a horizontal row of links.

## Source (verbatim)

The phone menu's behaviour: the sheet copies `#nav` each time it opens. It closes on the scrim, on Escape, on a drag down (past a third of its height, or a flick), or when you go anywhere. A drag that moved is not a tap on the item under it. Column widths: `fitColumns()` sizes the nav and sub-nav columns to their longest label across all content, so the gaps never shift, and caps the sub column at 30% of the window.

Source: `site/js/navsheet.js`, whole file

```js
// The menu on a phone (under 900px): a two-line glyph top left opens a bottom
// sheet with the same items as #nav (copied from it each time it opens, so the
// rooms showing, the paragraph step and the active mark are app.js's own).
// Closes on the scrim, Escape, a drag down, or going anywhere.
import { reducedMotion } from './state.js';

const MQ = matchMedia('(max-width: 899px)');
const IN_MS = 240, OUT_MS = 180, EASE_LAND = 'cubic-bezier(0.2, 0, 0, 1)', EASE_OUT = 'cubic-bezier(0.4, 0, 1, 1)';
const nav = document.getElementById('nav');
const col = nav?.closest('.col-nav');

if (nav && col) {
  const btn = document.createElement('button');
  btn.type = 'button'; btn.className = 'nav-btn';
  btn.setAttribute('aria-label', 'Menu'); btn.setAttribute('aria-expanded', 'false'); btn.setAttribute('aria-controls', 'nav-sheet');
  btn.innerHTML = '<span class="nav-btn-l" aria-hidden="true"></span><span class="nav-btn-l" aria-hidden="true"></span>';
  col.prepend(btn);
  document.documentElement.classList.add('has-nav-sheet');

  const sheet = document.createElement('dialog');
  sheet.id = 'nav-sheet'; sheet.className = 'nav-sheet'; sheet.setAttribute('aria-label', 'Menu');
  sheet.innerHTML = '<div class="nav-sheet-grab" aria-hidden="true"><span></span></div><nav aria-label="Sections"><ul class="nav-sheet-list"></ul></nav>';
  document.body.append(sheet);
  const list = sheet.querySelector('.nav-sheet-list');

  // the items, copied from #nav: no morph keys or orb hooks, so the GL and orbs keep to the page's own
  const fill = () => {
    list.replaceChildren(...[...nav.children].map(li => {
      const c = li.cloneNode(true);
      c.querySelectorAll('[data-morph]').forEach(e => e.removeAttribute('data-morph'));
      c.querySelectorAll('[data-node]').forEach(e => e.removeAttribute('data-node'));
      c.querySelectorAll('.is-peek').forEach(e => e.classList.remove('is-peek'));
      return c;
    }));
  };

  let closing = false;
  const open = () => {
    if (sheet.open) return;
    fill();
    sheet.showModal();
    document.documentElement.classList.add('nav-sheet-open');
    btn.setAttribute('aria-expanded', 'true');
    (list.querySelector('[aria-current]') || list.querySelector('a'))?.focus({ preventScroll: true });
    if (!reducedMotion.matches) {
      sheet.animate([{ transform: 'translateY(100%)' }, { transform: 'none' }], { duration: IN_MS, easing: EASE_LAND });
      sheet.animate([{ '--nav-scrim': 0 }, { '--nav-scrim': 1 }], { duration: IN_MS, easing: EASE_LAND });
    } else sheet.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 120 });
  };
  const close = (from = 0) => {
    if (!sheet.open || closing) return;
    closing = true;
    btn.setAttribute('aria-expanded', 'false');
    const done = () => {
      sheet.close(); closing = false; sheet.style.transform = ''; sheet.style.removeProperty('--nav-scrim');
      document.documentElement.classList.remove('nav-sheet-open');
      if (MQ.matches) btn.focus({ preventScroll: true });
    };
    if (reducedMotion.matches) { sheet.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 120 }).onfinish = done; return; }
    const h = sheet.offsetHeight || 1;
    const k = 1 - Math.min(1, from / h);
    sheet.animate([{ transform: `translateY(${from}px)` }, { transform: 'translateY(100%)' }], { duration: OUT_MS * Math.max(0.4, k), easing: EASE_OUT, fill: 'forwards' }).onfinish = () => { sheet.getAnimations().forEach(a => a.cancel()); done(); };
    sheet.animate([{ '--nav-scrim': k }, { '--nav-scrim': 0 }], { duration: OUT_MS * Math.max(0.4, k), easing: EASE_OUT, fill: 'forwards' });
  };

  btn.addEventListener('click', () => (sheet.open ? close() : open()));
  sheet.addEventListener('cancel', (e) => { e.preventDefault(); close(); }); // Escape
  sheet.addEventListener('click', (e) => {
    if (e.target === sheet) { // the scrim (the dialog's box is the sheet; outside it is the backdrop)
      const r = sheet.getBoundingClientRect();
      if (e.clientY < r.top) close();
      return;
    }
    if (e.target.closest('a')) close(); // the hash changes and the page renders under it
  });
  addEventListener('hashchange', () => close());
  MQ.addEventListener('change', () => { if (!MQ.matches) close(); });

  // drag down on the handle or the sheet; past a third of its height (or a flick) it goes
  let y0 = null, dy = 0, t0 = 0, id = null, moved = false, dragged = false;
  sheet.addEventListener('pointerdown', (e) => {
    if (e.button !== 0 || closing) return;
    const r = sheet.getBoundingClientRect();
    if (e.clientY < r.top) return;
    y0 = e.clientY; dy = 0; t0 = performance.now(); id = e.pointerId; moved = false;
  });
  sheet.addEventListener('pointermove', (e) => {
    if (y0 == null || e.pointerId !== id) return;
    dy = Math.max(0, e.clientY - y0);
    if (!moved && dy > 6) { moved = true; sheet.setPointerCapture(id); sheet.classList.add('is-dragging'); }
    if (moved) { sheet.style.transform = `translateY(${dy}px)`; sheet.style.setProperty('--nav-scrim', String(1 - Math.min(1, dy / sheet.offsetHeight))); }
  });
  const end = (e) => {
    if (y0 == null || e.pointerId !== id) return;
    const wasMoved = moved; y0 = null; moved = false; sheet.classList.remove('is-dragging');
    if (!wasMoved) return;
    dragged = true; setTimeout(() => { dragged = false; }, 0);
    const v = dy / Math.max(1, performance.now() - t0);
    if (dy > sheet.offsetHeight / 3 || v > 0.6) close(dy);
    else {
      sheet.animate([{ transform: `translateY(${dy}px)` }, { transform: 'none' }], { duration: reducedMotion.matches ? 0 : IN_MS, easing: EASE_LAND });
      sheet.style.transform = ''; sheet.style.removeProperty('--nav-scrim');
    }
  };
  sheet.addEventListener('pointerup', end);
  sheet.addEventListener('pointercancel', end);
  // a drag that moved is not a tap on the item under it
  sheet.addEventListener('click', (e) => { if (dragged) { e.preventDefault(); e.stopImmediatePropagation(); } }, true);
}
```


Source: `site/css/site.css`, lines 212 to 268

```css
/* ---------- the phone menu (js/navsheet.js): a two-line glyph top left, a bottom sheet of the nav ---------- */
@property --nav-scrim { syntax: '<number>'; inherits: true; initial-value: 1; }
.nav-btn { display: none; }
.nav-sheet { display: none; }
@media (max-width: 899px) {
  html.has-nav-sheet .col-nav #nav { display: none; }
  .nav-btn { display: grid; align-content: center; justify-items: start; gap: 6px; width: 44px; height: 44px; margin: -12px 0 -12px -12px; padding: 0 12px; border: 0; background: none; color: var(--ink); cursor: pointer; -webkit-tap-highlight-color: transparent; filter: url(#ink-ui); }
  .nav-btn-l { display: block; width: 20px; height: 1.5px; border-radius: 1px; background: currentColor; transition: transform 240ms var(--ease-land), width 240ms var(--ease-land); }
  .nav-btn-l + .nav-btn-l { width: 13px; }
  .nav-btn:hover .nav-btn-l + .nav-btn-l { width: 20px; }
  .nav-btn:active { transform: scale(0.94); }
  .nav-btn:focus-visible { outline: none; }
  .nav-btn:focus-visible .nav-btn-l { box-shadow: 0 0 0 1px var(--paper), 0 0 0 2px var(--ring); }
  .nav-btn[aria-expanded="true"] .nav-btn-l { width: 20px; transform: translateY(3.75px) rotate(45deg); }
  .nav-btn[aria-expanded="true"] .nav-btn-l + .nav-btn-l { transform: translateY(-3.75px) rotate(-45deg); }

  /* liquid glass: one blur on the sheet itself; the scrim stays a plain tint (no second blur) */
  .nav-sheet[open] { display: block; position: fixed; inset: auto 0 0 0; width: 100%; max-width: none; max-height: 85dvh; margin: 0; padding: 0 0 max(24px, env(safe-area-inset-bottom)); overflow: auto; overscroll-behavior: contain; touch-action: none;
    border: 0; border-radius: 16px 16px 0 0; color: var(--ink); font: 400 16px/20px var(--ui); letter-spacing: var(--track);
    background: color-mix(in srgb, var(--paper) 68%, transparent);
    -webkit-backdrop-filter: blur(20px) saturate(1.3);
    backdrop-filter: blur(20px) saturate(1.3);
    box-shadow:
      inset 0 1px 0 color-mix(in srgb, var(--paper) 62%, transparent),
      inset 0 0 0 1px color-mix(in srgb, var(--ink) 7%, transparent),
      0 -12px 40px color-mix(in srgb, var(--shadow) calc(16% * var(--shadow-k)), transparent); }
  /* no backdrop-filter: keep text readable with a denser paper fill */
  @supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
    .nav-sheet[open] { background: color-mix(in srgb, var(--paper) 94%, transparent); -webkit-backdrop-filter: none; backdrop-filter: none; }
  }
  @media (prefers-reduced-transparency: reduce) {
    .nav-sheet[open] { background: color-mix(in srgb, var(--paper) 96%, transparent); -webkit-backdrop-filter: none; backdrop-filter: none; }
  }
  /* scrim tint only — skip --shadow-k so dark themes don't smother the frost */
  .nav-sheet::backdrop { background: color-mix(in srgb, var(--shadow) calc(20% * var(--nav-scrim, 1)), transparent); }
  .nav-sheet.is-dragging { user-select: none; -webkit-user-select: none; }
  .nav-sheet-grab { display: grid; place-items: center; height: 28px; cursor: grab; }
  .nav-sheet-grab span { width: 36px; height: 4px; border-radius: 2px; background: color-mix(in srgb, var(--ink) 18%, transparent); }
  .nav-sheet nav { padding: 4px 24px 0; }
  .nav-sheet-list { display: flex; flex-direction: column; margin: 0; padding: 0; list-style: none; }
  .nav-sheet-list li { padding: 9px 0; }
  .nav-sheet-list .item::before { content: ''; position: absolute; inset: -9px -24px; }
  .nav-sheet-list .item { position: relative; display: inline-block; padding: 0; font: 400 24px/28px var(--ui); letter-spacing: -0.96px; white-space: nowrap; color: var(--ink); text-decoration: none; opacity: var(--op-meta); filter: url(#ink-ui); -webkit-tap-highlight-color: transparent; transition: opacity 160ms var(--ease-land); }
  .nav-sheet-list .item:active { opacity: 1; }
  .nav-sheet-list .item.is-active { opacity: 1; color: var(--accent-text); }
  [data-theme="marathon-light"] .nav-sheet-list .item.is-active { background: linear-gradient(transparent 12%, var(--accent-wash) 12%, var(--accent-wash) 92%, transparent 92%); box-shadow: -3px 0 0 var(--accent-wash), 3px 0 0 var(--accent-wash); }
  .nav-sheet-list .item:focus-visible { opacity: 1; text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 4px; }
  .nav-sheet-list .item.has-orb { padding-right: 0; }
  /* .nav-step keeps the class for JS, but no extra margin/padding/border — same rhythm as every other li */
  html.nav-sheet-open, html.nav-sheet-open body { overflow: hidden; }
}

@media (prefers-reduced-motion: reduce) {
  .dot { transition: none; }
  .warm { text-shadow: 0 0 .6px color-mix(in srgb, var(--warm) 55%, transparent); }
}
```


Source: `site/js/app.js`, lines 1016 to 1054

```js
// even column spacing: the nav and sub-nav columns are exactly as wide as their
// longest label across ALL content (revealed or not), so the gaps between nav,
// sub-nav and post are equal and never shift as new pages emerge
// the sub-nav never grows past this; a longer title wraps onto a second line
const SUB_MAX = 264;
function fitColumns() {
  const c = document.createElement('canvas').getContext('2d');
  c.font = '400 16px "Inter Display", sans-serif';
  try { c.letterSpacing = '-0.64px'; } catch (e) {}
  const w = (t) => Math.ceil(c.measureText(t).width);
  let nav = 0, sub = 0;
  subFit.clear();
  // the menu holds the rooms only; the sub column fits a room's section labels and pages
  // (a section in no room, and the app pages, by their own pages)
  for (const rm of rooms()) nav = Math.max(nav, w(rm.title));
  for (const l of navLinks()) nav = Math.max(nav, w(l.title));
  const pagesW = (s) => (s.items || []).reduce((m, it) => Math.max(m, w(it.title), it.group ? w(it.group) : 0), 0);
  for (const s of [...SECTIONS.map(x => x.slug === 'welcome' ? { ...x, items: [...(x.items || []), ...connectLinks()] } : x), MCP_PAGE, ...SETTING_PAGES]) {
    const rm = roomOf(s.slug);
    const own = rm && rm.sections.length > 1 ? Math.max(w(s.title), pagesW(s)) : pagesW(s);
    const key = rm ? rm.slug : s.slug;
    subFit.set(key, Math.max(subFit.get(key) || 0, own)); sub = Math.max(sub, own);
  }
  subBase = Math.min(sub, SUB_MAX);
  const root = document.documentElement.style;
  if (nav) root.setProperty('--col-nav', nav + 'px');
  applySub();
}
// the sub column keeps the site's width, and grows only for a section whose longest title is wider, so it sits on one line
const subFit = new Map(); let subBase = 0, subSection = '';
const subKey = (section) => roomOf(section.slug)?.slug || section.slug;
addEventListener('resize', () => applySub());
function applySub(slug = subSection) {
  subSection = slug;
  if (!subBase) return;
  const own = subFit.get(slug) || 0;
  const max = Math.max(subBase, Math.floor(innerWidth * 0.3)); // never more than ~30% of the window
  document.documentElement.style.setProperty('--col-sub', Math.min(Math.max(subBase, own), max) + 'px');
}
```
