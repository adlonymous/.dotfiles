---
title: Term
slug: term
status: published
description: A defined word inside a sentence. Same type as the sentence, a dotted underline, and a small card with the definition on hover or tap.
chips:
  - Dotted underline 1px
  - Offset 3px
  - Ink 45%
  - Card 320 wide
created: 2026-11-11T18:00:00Z
updated: 2026-11-11T18:00:00Z
---

Terms mark the words the article defines ("design harness", "agent-native", "coding harness", "design complete"). They read as part of the sentence: the only signal is a **dotted** underline. Ordinary links use a thin **solid** underline instead (see components/screens/reading.md).

```html
<p>A <button type="button" class="term" data-term="design-harness" aria-haspopup="dialog" aria-expanded="false"
  aria-controls="term-pop" aria-describedby="term-def-design-harness">design harness</button> is an opinionated schema …</p>
<div id="term-defs" hidden><span id="term-def-design-harness">An opinionated schema for an agent-native design system. …</span></div>
```

```css
.term {
  --term-wash: color-mix(in srgb, var(--ink) 8%, transparent);
  all: unset; display: inline; font: inherit; letter-spacing: inherit; color: inherit; cursor: help;
  border-radius: 3px; padding: 0 2px; margin: 0 -2px;           /* the wash breathes past the word; the text does not move */
  -webkit-box-decoration-break: clone; box-decoration-break: clone;
  text-decoration: underline dotted; text-decoration-thickness: 1px; text-underline-offset: 3px;
  text-decoration-color: color-mix(in srgb, var(--ink) 45%, transparent);
  transition: background-color 160ms var(--ease-land), text-decoration-color 160ms var(--ease-land);
}
.term:hover, .term[aria-expanded="true"] { background: var(--term-wash); text-decoration-color: currentColor; }
.term:focus-visible { background: var(--term-wash); text-decoration-color: currentColor; outline: 1.5px solid var(--ring); outline-offset: 1px; }

.term-pop { position: fixed; z-index: 60; width: min(320px, calc(100vw - 24px)); padding: 14px 16px 6px;
  background: var(--paper); color: var(--ink); border-radius: 12px; text-align: left;
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) calc(10% * var(--shadow-k)), transparent),
              0 2px 6px -2px color-mix(in srgb, var(--shadow) calc(10% * var(--shadow-k)), transparent),
              0 24px 64px -24px color-mix(in srgb, var(--shadow) calc(25% * var(--shadow-k)), transparent); }
```

The definitions shipped with the article:

- **design harness**: An opinionated schema for an agent-native design system. It gives an agent an "eye" for design, the way a coding harness gives it "hands".
- **agent-native**: Written for agents to read and act on as well as for people: explicit, structured and complete enough that nothing relies on a designer filling the gaps.
- **coding harness**: The software that translates a model into a system that can affect its environment (Rubric Labs). It lets an agent act: read files, run code, call tools.
- **design complete**: Finished to the standard you would ship: every state, edge and detail resolved, not just a convincing first pass.

## Source (verbatim)

Behaviour (from `js/terms.js`):

- **Mouse:** a 120ms hover opens the popover. It stays while the pointer is on the chip or the card, and closes 200ms after it leaves both. A click pins it open.
- **Keys:** focus opens it (focus stays on the chip). Tab moves into its actions. Escape closes it and returns to the chip.
- **Touch:** a tap toggles it, and a tap elsewhere closes it.
- It also closes on scroll and when focus leaves both the chip and the card.
- It sits below the chip's line, or above when there is no room, and stays inside the viewport sideways.
- Screen readers get the definition as the chip's description, from one hidden node per term in `#term-defs`.

Source: `site/js/terms.js`, whole file

```js
// Inline term chips: a word the article defines, written [Term](term:slug) in the
// content and read from js/glossary.js. termChip(slug, nodes) makes the chip
// (inlineInto in js/app.js calls it for every term: href); one popover, a
// non-modal dialog, is shared by every chip on the page.
//   mouse: hover 120ms opens it, it stays while the pointer is on the chip or the
//          card, and closes 200ms after it leaves both; a click pins it open
//   keys:  focus opens it (focus stays on the chip), Tab moves into its actions,
//          Escape closes it and returns to the chip
//   touch: tap toggles it; a tap elsewhere closes it
// It also closes on scroll and when focus leaves the chip and the card.
// Screen readers get the definition as the chip's description (a hidden node per
// term in #term-defs), so it is read whether or not the card is open.
import { GLOSSARY, LAYERS } from './glossary.js';
import { reducedMotion } from './state.js';

const OPEN_MS = 120, GRACE_MS = 200, GAP = 8, EDGE = 12;
const layerTitle = (s) => LAYERS.find(l => l.slug === s)?.title || '';
const defId = (slug) => `term-def-${slug}`;

// the stylesheet, linked once, next to this module
if (!document.querySelector('link[data-terms]')) {
  const l = document.createElement('link');
  l.rel = 'stylesheet'; l.href = new URL('../css/terms.css', import.meta.url).href; l.dataset.terms = '';
  document.head.append(l);
}

// ---------- the chip ----------
// nodes: what inlineInto built for the run (text, em, strong). Unknown slug: null,
// and the caller keeps the plain text.
export function termChip(slug, nodes = []) {
  const g = GLOSSARY[slug];
  if (!g) return null;
  const b = document.createElement('button');
  b.type = 'button'; b.className = 'term'; b.dataset.term = slug;
  b.setAttribute('aria-haspopup', 'dialog');
  b.setAttribute('aria-expanded', 'false');
  b.setAttribute('aria-controls', 'term-pop');
  b.setAttribute('aria-describedby', describe(slug, g));
  b.append(...nodes);
  return b;
}
// one hidden definition per term, the chip's accessible description
function describe(slug, g) {
  let box = document.getElementById('term-defs');
  if (!box) { box = document.createElement('div'); box.id = 'term-defs'; box.hidden = true; document.body.append(box); }
  if (!document.getElementById(defId(slug))) {
    const d = document.createElement('span'); d.id = defId(slug);
    d.textContent = g.def;
    box.append(d);
  }
  return defId(slug);
}

// ---------- the popover (one for the page) ----------
let pop, elTerm, elLayer, elDef, elSee, elCopy, elStatus;
let chip = null, pinned = false, openT = 0, closeT = 0, copyT = 0, pointerX = null, openedAt = 0, quiet = false;

function build() {
  if (pop) return;
  pop = document.createElement('div');
  pop.id = 'term-pop'; pop.className = 'term-pop'; pop.hidden = true;
  pop.setAttribute('role', 'dialog');
  pop.setAttribute('aria-labelledby', 'term-pop-term');
  pop.innerHTML = `
    <div class="term-pop-head"><span class="term-pop-term" id="term-pop-term"></span></div>
    <p class="term-pop-def"></p>
    <span class="sr-only" role="status" aria-live="polite"></span>`;
  [elTerm, elLayer, elDef, elSee, elCopy, elStatus] = ['.term-pop-term', '.term-pop-layer', '.term-pop-def', '.term-see', '.term-copy', '[role=status]'].map(s => pop.querySelector(s));
  document.body.append(pop);

  pop.addEventListener('pointerenter', () => clearTimeout(closeT));
  pop.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse' && !pinned) closeSoon(); });
  pop.addEventListener('keydown', onPopKey);
  pop.addEventListener('focusout', onFocusOut);
  // the layer label and "See it in the harness" removed from the popover (Ahmed, Nov 11): the term and its definition only
  // Copy definition removed from the popover (Ahmed, Nov 10)
}

function open(c, { pin = false } = {}) {
  build();
  clearTimeout(openT); clearTimeout(closeT);
  if (chip && chip !== c) chip.setAttribute('aria-expanded', 'false');
  const g = GLOSSARY[c.dataset.term];
  if (!g) return;
  const same = chip === c && !pop.hidden;
  chip = c; pinned = pinned && same ? true : pin;
  if (!same) {
    elTerm.textContent = g.term;
    elDef.textContent = g.def;
    elStatus.textContent = '';
    pop.hidden = false; openedAt = performance.now();
    place();
    pop.classList.remove('is-in'); void pop.offsetWidth; pop.classList.add('is-in');
  }
  c.setAttribute('aria-expanded', 'true');
}
function close(refocus = false) {
  clearTimeout(openT); clearTimeout(closeT);
  if (!pop || pop.hidden) { pinned = false; return; }
  const c = chip;
  pop.hidden = true; pop.classList.remove('is-in', 'is-above');
  pinned = false; chip = null;
  c?.setAttribute('aria-expanded', 'false');
  if (refocus && c?.isConnected && document.activeElement !== c) { quiet = true; c.focus({ preventScroll: true }); quiet = false; } // back to the chip without reopening
}
const closeSoon = () => { clearTimeout(closeT); closeT = setTimeout(() => close(false), GRACE_MS); };

// below the line the chip sits on, above when there is no room; inside the
// viewport sideways. A chip that wraps anchors to the line the pointer is on.
function place() {
  const rects = [...chip.getClientRects()];
  let r = rects[0] || chip.getBoundingClientRect();
  if (pointerX != null && rects.length > 1) r = rects.find(q => pointerX >= q.left && pointerX <= q.right) || r;
  const vw = document.documentElement.clientWidth, vh = innerHeight;
  pop.style.left = '0px'; pop.style.top = '0px';
  const w = pop.offsetWidth, h = pop.offsetHeight;
  const above = r.bottom + GAP + h > vh - EDGE && r.top - GAP - h >= EDGE;
  const top = above ? r.top - GAP - h : r.bottom + GAP;
  const left = Math.max(EDGE, Math.min(r.left - 14, vw - w - EDGE));
  pop.style.left = `${Math.round(left)}px`; pop.style.top = `${Math.round(top)}px`;
  pop.classList.toggle('is-above', above);
}

async function copy() {
  const g = chip && GLOSSARY[chip.dataset.term];
  if (!g) return;
  const text = `${g.term}: ${g.def}`;
  let ok = false;
  try { await navigator.clipboard.writeText(text); ok = true; } catch {
    const t = document.createElement('textarea'); t.value = text; t.setAttribute('readonly', ''); t.style.cssText = 'position:fixed;opacity:0';
    document.body.append(t); t.select(); try { ok = document.execCommand('copy'); } catch {} t.remove(); elCopy.focus({ preventScroll: true });
  }
  elCopy.textContent = ok ? 'Copied' : 'Could not copy';
  elStatus.textContent = ok ? 'Definition copied' : 'Could not copy the definition';
  clearTimeout(copyT); copyT = setTimeout(() => { if (elCopy) elCopy.textContent = 'Copy definition'; }, 1600);
}

// ---------- keys and focus ----------
const actions = () => [elSee].filter(a => a && !a.hidden);
const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])';
function after(el, dir = 1) { // the next focusable on the page after el (the card is out of the flow)
  const all = [...document.querySelectorAll(FOCUSABLE)].filter(x => !pop.contains(x) && x.offsetParent !== null);
  return all[all.indexOf(el) + dir] || null;
}
function onChipKey(e) {
  const c = e.currentTarget;
  if (e.key === 'Escape' && chip === c && !pop?.hidden) { e.preventDefault(); e.stopPropagation(); close(true); return; }
  if (e.key === 'Tab' && !e.shiftKey && chip === c && !pop?.hidden) { e.preventDefault(); actions()[0]?.focus({ preventScroll: true }); }
}
function onPopKey(e) {
  if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); close(true); return; }
  if (e.key !== 'Tab') return;
  const a = actions(), i = a.indexOf(document.activeElement);
  if (e.shiftKey && i <= 0) { e.preventDefault(); chip?.focus({ preventScroll: true }); return; }
  if (!e.shiftKey && i === a.length - 1) { e.preventDefault(); const c = chip, next = c && after(c); close(false); (next || c)?.focus(); }
}
function onFocusOut(e) {
  const to = e.relatedTarget;
  if (!pop || pop.hidden) return;
  if (to && (to === chip || pop.contains(to))) return;
  if (!to && (pinned || pop.matches(':hover'))) return; // a click on the card or the page: the outside pointerdown decides
  close(false);
}

// ---------- the chip's events, delegated so a re-rendered or word-wrapped chip still works ----------
const chipOf = (t) => t instanceof Element ? t.closest('button.term[data-term]') : null;
document.addEventListener('pointerover', (e) => {
  const c = chipOf(e.target);
  if (!c || e.pointerType !== 'mouse') return;
  if (chip === c) { clearTimeout(closeT); return; }
  pointerX = e.clientX;
  clearTimeout(openT); openT = setTimeout(() => open(c), OPEN_MS);
});
document.addEventListener('pointerout', (e) => {
  const c = chipOf(e.target);
  if (!c || e.pointerType !== 'mouse' || c.contains(e.relatedTarget)) return;
  clearTimeout(openT);
  if (chip === c && !pinned) closeSoon();
});
document.addEventListener('pointerdown', (e) => {
  if (!pop || pop.hidden) return;
  if (pop.contains(e.target) || chipOf(e.target) === chip) return;
  close(false);
}, true);
document.addEventListener('click', (e) => {
  const c = chipOf(e.target);
  if (!c) return;
  e.preventDefault();
  pointerX = e.clientX || null;
  if (chip === c && !pop.hidden && (pinned || e.detail === 0)) close(false); // keyboard Enter/Space toggles too
  else open(c, { pin: true });
});
document.addEventListener('focusin', (e) => {
  const c = chipOf(e.target);
  if (!c) return;
  if (!c.dataset.keys) { c.dataset.keys = '1'; c.addEventListener('keydown', onChipKey); c.addEventListener('focusout', onFocusOut); }
  if (!quiet && c.matches(':focus-visible') && chip !== c) { pointerX = null; open(c); }
});
// focusing a chip off screen scrolls it into view: that scroll moves the card, it does not close it
addEventListener('scroll', (e) => {
  if (!pop || pop.hidden || pop.contains(e.target)) return;
  if (performance.now() - openedAt < 400) place(); else close(false);
}, { capture: true, passive: true });
addEventListener('resize', () => close(false));
addEventListener('hashchange', () => close(false));
reducedMotion.addEventListener?.('change', () => pop?.classList.remove('is-in'));
```


Source: `site/css/terms.css`, whole file

```css
/* Inline term chips and their card (js/terms.js). The chip stays a word in the
   sentence: same face, size and line box, a dotted underline (a definition, not a
   link's solid one), and a faint wash on hover, focus and while its card is open. */
.term {
  --term-wash: color-mix(in srgb, var(--ink) 8%, transparent);
  all: unset;
  display: inline;
  font: inherit; letter-spacing: inherit; color: inherit;
  cursor: help;
  border-radius: 3px;
  padding: 0 2px; margin: 0 -2px;                  /* the wash breathes past the word, the text does not move */
  -webkit-box-decoration-break: clone; box-decoration-break: clone;
  text-decoration: underline dotted;
  text-decoration-thickness: 1px; text-underline-offset: 3px;
  text-decoration-color: color-mix(in srgb, var(--ink) 45%, transparent);
  -webkit-tap-highlight-color: transparent;
  transition: background-color 160ms var(--ease-land), text-decoration-color 160ms var(--ease-land);
}
[data-theme="marathon-light"] .term { --term-wash: color-mix(in srgb, var(--accent-wash) 55%, transparent); }
[data-theme="marathon-dark"] .term { --term-wash: color-mix(in srgb, var(--accent-wash) 26%, transparent); }
.term:hover, .term[aria-expanded="true"] { background: var(--term-wash); text-decoration-color: currentColor; }
.term:focus-visible { background: var(--term-wash); text-decoration-color: currentColor; outline: 1.5px solid var(--ring); outline-offset: 1px; }

/* the card: paper, a hairline, the viewer's soft shadow */
.term-pop {
  position: fixed; z-index: 60; left: 0; top: 0;
  box-sizing: border-box; width: min(320px, calc(100vw - 24px));
  padding: 14px 16px 14px;
  background: var(--paper); color: var(--ink);
  border-radius: 12px;
  box-shadow:
    0 0 0 1px color-mix(in srgb, var(--ink) calc(10% * var(--shadow-k)), transparent),
    0 2px 6px -2px color-mix(in srgb, var(--shadow) calc(10% * var(--shadow-k)), transparent),
    0 24px 64px -24px color-mix(in srgb, var(--shadow) calc(25% * var(--shadow-k)), transparent);
  text-align: left;
}
.term-pop[hidden] { display: none; }
.term-pop.is-in { animation: term-in 160ms var(--ease-land); }
.term-pop.is-in.is-above { animation-name: term-in-above; }
@keyframes term-in { from { opacity: 0; transform: translateY(-4px); } }
@keyframes term-in-above { from { opacity: 0; transform: translateY(4px); } }
@media (prefers-reduced-motion: reduce) {
  .term-pop.is-in, .term-pop.is-in.is-above { animation-name: term-fade; }
  .term { transition: none; }
}
@keyframes term-fade { from { opacity: 0; } }

.term-pop-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; }
.term-pop-term { font: 400 16px/20.8px var(--serif); letter-spacing: var(--track); }
.term-pop-layer { flex: none; font: 400 12px/16px var(--ui); letter-spacing: -0.12px; opacity: var(--op-meta); }
.term-pop-layer[hidden] { display: none; }
.term-pop-def { margin: 6px 0 0; font: 400 15px/20px var(--serif); letter-spacing: var(--track); text-wrap: pretty; color: color-mix(in srgb, var(--ink) 80%, var(--paper)); }

.term-pop-acts { display: flex; flex-wrap: wrap; gap: 0 4px; margin: 0 -8px; padding-top: 2px; } /* no divider (Ahmed, Nov 10) */
.term-pop-act {
  all: unset; box-sizing: border-box;
  display: inline-flex; align-items: center; min-height: 32px; padding: 0 8px; border-radius: 6px;
  font: 400 13px/16px var(--ui); letter-spacing: -0.2px; color: var(--ink);
  cursor: pointer; -webkit-tap-highlight-color: transparent;
  transition: background-color 120ms var(--ease-land);
}
.term-pop-act[hidden] { display: none; }
.term-pop-act:hover { background: color-mix(in srgb, var(--ink) 7%, transparent); }
.term-pop-act:active { background: color-mix(in srgb, var(--ink) 12%, transparent); }
.term-pop-act:focus-visible { outline: 1.5px solid var(--ring); outline-offset: -1.5px; }
@media (pointer: coarse) { .term-pop-act { min-height: 44px; } }
```
