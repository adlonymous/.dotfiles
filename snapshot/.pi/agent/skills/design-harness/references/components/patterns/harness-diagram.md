---
title: Harness diagram
slug: harness-diagram
status: published
description: "::harness-diagram: the harness as a black-and-white flowchart, Foundations and Intelligence feeding it from the left, Components and Moves from the right; hover lights a layer."
chips:
  - Embed
  - Diagram
created: 2026-11-11T16:05:20Z
updated: 2026-11-11T16:05:35Z
---

Embeds are placed in a post by a paragraph that is only `::name` (`EMBED = /^::([a-z-]+)\s*$/`). `js/embeds.js` replaces it with `<div class="embed embed-NAME" data-embed="NAME" data-stream-skip>`, lazy-imports `js/embeds/NAME.js` and calls `mount(el, ctx)`. Embeds are skipped by the word stream and by the body ink filter (`.col-body article > :not(.embed) { filter: url(#ink-body) }`), so screenshots and diagrams stay sharp.

**What it is.** The design harness in one idea, as a classic black-and-white flowchart built on the site's own tokens, so it follows all twelve themes. The **Harness** box is in the middle. **Foundations** and **Intelligence** are on its left and **Components** and **Moves** on its right, each feeding it through one connector. Connectors are thin, orthogonal, square-cornered lines with small open arrowheads: each side has a line out of each layer, a bus between the pair, and one arrow into the harness. Hovering or focusing a layer lifts it (`.is-lit`), lights its line, and shows its one-line definition (from `js/glossary.js`) underneath. On a phone it is one column (Foundations, Intelligence, Harness, Components, Moves), with a bus down the right side that gathers the four and turns into the harness. It is drawn through the `#ink-diagram` SVG filter. Under reduced motion, cards and wires do not transition and a lit card does not move. A text alternative is included for screen readers.

At 900px and wider, the diagram breaks out of the 640px text column (540px until 2026-11-11):

Source: `site/css/site.css`, lines 85 to 94

```css
/* full-width embeds (Ahmed, Nov 10): the diagram, the work grid and the harness viewer break out of the 640px text column (540 until Nov 11)
   to the page's right padding, capped at 820px (narrower, Ahmed Nov 10) (desktop only; on a phone the column is already the page) */
@media (min-width: 900px) {
  .col-body .embed-harness-diagram, .col-body .embed-harness-flow, .col-body .embed-harness-viewer, .col-body .embed-work-grid {
    max-width: none; align-self: flex-start;
    width: min(820px, calc(100vw - var(--sbw, 0px) - 48px - var(--col-nav, 89px) - var(--col-sub, 248px) - 2 * var(--gap)));
  }
  /* the work grid and the harness viewer run full width to the page's right padding (Ahmed, Nov 10; the viewer for a wider preview) */
  .col-body .embed-work-grid, .col-body .embed-harness-viewer { width: calc(100vw - var(--sbw, 0px) - 48px - var(--col-nav, 89px) - var(--col-sub, 248px) - 2 * var(--gap)); }
}
```


The `#ink-diagram` filter (inline in index.html):

```html
<filter id="ink-diagram" x="-1%" y="-2%" width="102%" height="104%" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="7" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="1.2" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feGaussianBlur in="d" stdDeviation="0.25" result="b"/>
  <feComponentTransfer in="b" result="i"><feFuncA type="linear" slope="1.6" intercept="0"/></feComponentTransfer>
  <feTurbulence type="fractalNoise" baseFrequency="2.4" numOctaves="1" seed="11" result="g"/>
  <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.1 0 0 0 1.5" result="gm"/>
  <feComposite in="i" in2="gm" operator="in"/>
</filter>
```

Icons come from `js/embeds/harness-icons.js` (`svgIcon(name)`). Those are icon-set paths and are **not** reproduced here; leave a 14 to 16px `currentColor` slot of the same size.

Source: `site/css/embeds/harness-diagram.css`, whole file

```css
/* ::harness-diagram (js/embeds/harness-diagram.js): one idea on a small app canvas.
   Designer → Agent → Design, the four layers beneath feeding the agent. */
.embed-harness-diagram { margin: calc(var(--para) * 0.5) 0; }
.hd-fig { margin: 0; display: flex; flex-direction: column; gap: 12px; }
.hd-canvas { --hd-edge: color-mix(in srgb, var(--ink) 11%, transparent); --hd-wire: color-mix(in srgb, var(--ink) 28%, transparent); --hd-tint: color-mix(in srgb, var(--ink) 5%, transparent);
  position: relative; display: flex; flex-direction: column; gap: 64px; padding: 40px clamp(20px, 6%, 64px) 36px; border-radius: 14px;
  background-color: color-mix(in srgb, var(--ink) 2.5%, var(--paper));
  background-image: radial-gradient(circle at 1px 1px, color-mix(in srgb, var(--ink) 9%, transparent) 1px, transparent 1.4px);
  background-size: 14px 14px; background-position: 7px 7px;
  box-shadow: inset 0 0 0 1px var(--hd-edge);
  font: 400 14px/18px var(--ui); letter-spacing: -0.3px; }
.hd-wires { position: absolute; inset: 0; pointer-events: none; overflow: visible; }
.hd-labels { position: absolute; inset: 0; pointer-events: none; z-index: 2; }
/* the agent alone on top, one layer-column wide, centred over the four */
.hd-flow { position: relative; z-index: 1; display: grid; grid-template-columns: calc((100% - 36px) / 4); justify-content: center; }
.hd-layers { position: relative; z-index: 1; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }

/* cards: paper, a hairline, a key and an ambient shadow; a layer lifts when lit */
.hd-card { display: flex; align-items: center; gap: 10px; min-width: 0; height: 48px; padding: 0 14px 0 12px; border-radius: 10px; background: var(--paper); color: var(--ink);
  box-shadow: 0 0 0 1px var(--hd-edge), 0 1px 2px color-mix(in srgb, var(--shadow) calc(6% * var(--shadow-k)), transparent), 0 4px 12px -4px color-mix(in srgb, var(--shadow) calc(10% * var(--shadow-k)), transparent);
  transition: transform 220ms var(--ease-land), box-shadow 220ms var(--ease-land), opacity 220ms var(--ease-land); }
.hd-card { justify-content: center; }
.hd-layer { outline: none; cursor: default; -webkit-tap-highlight-color: transparent; }
.hd-ico { flex: none; display: grid; place-items: center; width: 26px; height: 26px; border-radius: 7px; background: var(--hd-tint); color: var(--ink); }
.hd-ico svg { display: block; width: 16px; height: 16px; }
.hd-agent .hd-ico, .hd-card.is-lit .hd-ico { color: var(--accent-mark); background: color-mix(in srgb, var(--accent-mark) 12%, transparent); }
.hd-title { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hd-layer:focus-visible { box-shadow: 0 0 0 1px var(--ring), 0 0 0 4px color-mix(in srgb, var(--ring) 14%, transparent); }
.hd-card.is-lit { transform: translateY(-2px); box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 22%, transparent), 0 2px 4px color-mix(in srgb, var(--shadow) calc(7% * var(--shadow-k)), transparent), 0 12px 28px -8px color-mix(in srgb, var(--shadow) calc(22% * var(--shadow-k)), transparent); }
.has-lit .hd-layer:not(.is-lit) { opacity: 0.6; }

/* connectors */
.hd-wire { fill: none; stroke: var(--hd-wire); stroke-width: 1; stroke-linecap: round; stroke-linejoin: round; transition: stroke 200ms var(--ease-land); }
.hd-wire.is-lit { stroke: var(--accent-mark); stroke-width: 1.4; }
.hd-wire-label { position: absolute; font-size: 11px; line-height: 13px; letter-spacing: -0.05px; color: var(--muted); white-space: nowrap; }
.hd-wire-label.is-above { transform: translate(-50%, calc(-100% - 5px)); }
.hd-wire-label.is-right { transform: translate(8px, -50%); }

.hd-def { display: flex; flex-direction: column; min-height: 40px; padding-top: 10px; border-top: 1px solid color-mix(in srgb, var(--ink) 8%, transparent); font: 400 14px/20px var(--ui); letter-spacing: -0.2px; color: var(--muted); }
.hd-def-name { color: var(--ink); }
.hd-def-name:empty { display: none; }

/* a phone: the flow stacked, the layers two by two beneath, one line up the right side */
@media (max-width: 599px) {
  .hd-canvas { gap: 44px; padding: 20px 40px 20px 16px; }
  .hd-flow { grid-template-columns: 1fr; row-gap: 40px; }
  .hd-layers { grid-template-columns: 1fr; gap: 8px; }
  .hd-card { height: 44px; }
  .hd-card { justify-content: flex-start; }
  .hd-def { min-height: 60px; }
}
@media (prefers-reduced-motion: reduce) { .hd-card, .hd-wire { transition: none; } .hd-card.is-lit { transform: none; } }

/* classic black-and-white flowchart (Ahmed, Nov 10): the Harness in the middle, two layers each side.
   Square boxes with a 1px black rule, black lines and arrowheads, black icons; no ground of its own (grey removed, Ahmed Nov 10):
   it sits on the page's paper and grain. Lighting is a heavier line, not a colour. */
.hd-canvas { --hd-edge: var(--ink); --hd-wire: var(--ink); color: var(--ink); border-radius: 0; box-shadow: none; padding: 44px clamp(16px, 5%, 48px);
  background: none; }
.hd-board { position: relative; z-index: 1; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr); column-gap: clamp(40px, 9%, 88px); align-items: center; }
.hd-side { display: flex; flex-direction: column; gap: 28px; }
.hd-card, .hd-card.is-lit { color: var(--ink); border-radius: 0; box-shadow: 0 0 0 1px var(--ink); transform: none; justify-content: center; padding: 0 14px; gap: 10px; }
.hd-harness { box-shadow: 0 0 0 1.5px var(--ink); font-weight: 500; }
.hd-card.is-lit { box-shadow: 0 0 0 2px var(--ink); }
.hd-ico, .hd-agent .hd-ico, .hd-card.is-lit .hd-ico { width: 16px; height: 16px; border-radius: 0; background: none; color: var(--ink); }
.has-lit .hd-layer:not(.is-lit) { opacity: 1; }
.hd-wire, .hd-wire.is-lit { stroke: var(--ink); }
.hd-wire.is-lit { stroke-width: 2; }
.hd-layer:focus-visible { box-shadow: 0 0 0 2px var(--ink), 0 0 0 5px var(--paper), 0 0 0 6px var(--ink); }
@media (max-width: 599px) {
  .hd-canvas { padding: 24px 44px 24px 16px; }
  .hd-board { grid-template-columns: 1fr; row-gap: 12px; }
  .hd-side { gap: 12px; }
  .hd-card, .hd-card.is-lit { justify-content: center; }
}

/* the flowchart's style (Ahmed, Nov 10), as in ::harness-flow: compact cards that hug their label (34px, 13px type,
   14px icons), 8px corners, round caps and joins on the lines. The side cards sit against the harness. */
.hd-board { grid-template-columns: auto auto auto; justify-content: start; column-gap: 56px; }
.hd-canvas { padding: 48px 0; }
@media (max-width: 599px) { .hd-board { grid-template-columns: 1fr; } .hd-canvas { padding: 8px 44px 8px 0; } }
.hd-side { gap: 16px; }
.hd-side.is-left { align-items: flex-end; }
.hd-side.is-right { align-items: flex-start; }
.hd-card, .hd-card.is-lit { height: 34px; padding: 0 10px; gap: 6px; border-radius: 8px; font-size: 13px; }
.hd-ico, .hd-agent .hd-ico, .hd-card.is-lit .hd-ico, .hd-ico svg { width: 14px; height: 14px; }
.hd-wire, .hd-wire.is-lit { stroke-linecap: round; stroke-linejoin: round; }
@media (max-width: 599px) { .hd-side.is-left, .hd-side.is-right { align-items: stretch; } }

/* larger scale (Ahmed, Nov 10), matching ::harness-flow: 42px cards, 15px type, 16px icons */
@media (min-width: 600px) {
  .hd-board { column-gap: 72px; }
  .hd-side { gap: 20px; }
  .hd-card, .hd-card.is-lit { height: 42px; padding: 0 14px; gap: 8px; border-radius: 10px; font-size: 15px; }
  .hd-ico, .hd-agent .hd-ico, .hd-card.is-lit .hd-ico, .hd-ico svg { width: 16px; height: 16px; }
  .hd-canvas { padding: 56px 0; }
}
```


Source: `site/js/embeds/harness-diagram.js`, whole file

```js
// ::harness-diagram. The design harness in one idea, as a small app canvas in the
// [product] app's language (cards, hairlines, layered shadows, filled icons),
// built on the site's own tokens so it follows all twelve themes.
// A classic black-and-white flowchart (Ahmed, Nov 10): the Harness in the middle, Foundations and
// Intelligence on its left, Components and Moves on its right, each feeding it through one connector. Hover or focus a layer: it lifts, its line
// lights and its one-line definition shows underneath. Independent of the viewer.
import { LAYERS, GLOSSARY } from '../glossary.js';
import { svgIcon } from './harness-icons.js';

const CSS = 'css/embeds/harness-diagram.css';
const NARROW = matchMedia('(max-width: 599px)');
const ORDER = ['foundations', 'intelligence', 'components', 'moves'];
const LEFT = ['foundations', 'intelligence'], RIGHT = ['components', 'moves'];
const NS = 'http://www.w3.org/2000/svg';

export function mount(el) {
  if (!document.querySelector(`link[href="${CSS}"]`)) document.head.append(Object.assign(document.createElement('link'), { rel: 'stylesheet', href: CSS }));
  const byLayer = Object.fromEntries(LAYERS.map(l => [l.slug, l]));
  const h = (tag, cls) => { const e = document.createElement(tag); if (cls) e.className = cls; return e; };

  el.classList.add('hd');
  el.innerHTML = '';
  const fig = h('figure', 'hd-fig');
  const canvas = h('div', 'hd-canvas');
  const wires = document.createElementNS(NS, 'svg');
  wires.setAttribute('class', 'hd-wires'); wires.setAttribute('aria-hidden', 'true');
  const labels = h('div', 'hd-labels');

  const cards = {};
  const card = (key, title, layer) => {
    const c = h('div', `hd-card hd-${key}` + (layer ? ' hd-layer' : ' hd-node'));
    c.dataset.key = key;
    if (layer) { c.tabIndex = 0; c.setAttribute('role', 'group'); c.setAttribute('aria-label', title); c.setAttribute('aria-describedby', 'hd-def'); }
    else c.setAttribute('aria-hidden', 'true');
    const ico = h('span', 'hd-ico'); ico.innerHTML = svgIcon(key, 16);
    const t = h('span', 'hd-title'); t.textContent = title;
    c.append(ico, t);
    cards[key] = c;
    return c;
  };
  const board = h('div', 'hd-board');
  const side = (keys, cls) => { const c = h('div', `hd-side ${cls}`); keys.forEach(k => c.append(card(k, byLayer[k].title, true))); return c; };
  board.append(side(LEFT, 'is-left'), card('harness', 'Harness', false), side(RIGHT, 'is-right'));
  canvas.append(wires, board, labels);

  const IDLE_NAME = 'Harness', IDLE = GLOSSARY['design-harness'].def;
  const def = h('figcaption', 'hd-def'); def.id = 'hd-def'; def.setAttribute('aria-live', 'polite');
  const defName = h('span', 'hd-def-name'), defText = h('span', 'hd-def-text');
  defName.textContent = IDLE_NAME; defText.textContent = IDLE;
  def.append(defName, defText);
  // the text alternative
  const alt = h('ul', 'sr-only');
  [`Four layers feed the harness: ${ORDER.map(k => byLayer[k].title).join(', ')}.`,
    ...ORDER.map(k => `${byLayer[k].title}: ${byLayer[k].def}`)]
    .forEach(s => { const li = h('li'); li.textContent = s; alt.append(li); });
  fig.append(canvas, def, alt);
  el.append(fig);

  // ---------- connectors: thin, orthogonal, square corners (classic flowchart), small open arrowheads ----------
  let groups = [];
  const box = (k) => { const c = cards[k], r = c.getBoundingClientRect(), o = canvas.getBoundingClientRect(); return { x: r.left - o.left, y: r.top - o.top, w: c.offsetWidth, h: c.offsetHeight }; };
  const rounded = (pts, r = 8) => {
    let d = `M${pts[0][0]} ${pts[0][1]}`;
    for (let i = 1; i < pts.length - 1; i++) {
      const [a, b, c] = [pts[i - 1], pts[i], pts[i + 1]];
      const l1 = Math.hypot(b[0] - a[0], b[1] - a[1]), l2 = Math.hypot(c[0] - b[0], c[1] - b[1]);
      const k = Math.min(r, l1 / 2, l2 / 2);
      const p1 = [b[0] - (b[0] - a[0]) / l1 * k, b[1] - (b[1] - a[1]) / l1 * k], p2 = [b[0] + (c[0] - b[0]) / l2 * k, b[1] + (c[1] - b[1]) / l2 * k];
      d += ` L${p1[0]} ${p1[1]} Q${b[0]} ${b[1]} ${p2[0]} ${p2[1]}`;
    }
    const z = pts[pts.length - 1];
    return d + ` L${z[0]} ${z[1]}`;
  };
  const head = (tip, from) => {
    const dx = Math.sign(tip[0] - from[0]), dy = Math.sign(tip[1] - from[1]), L = 4.5, W = 3.5;
    const bx = tip[0] - dx * L, by = tip[1] - dy * L;
    return ` M${bx + dy * W} ${by - dx * W} L${tip[0]} ${tip[1]} L${bx - dy * W} ${by + dx * W}`;
  };
  const wire = (pts, group, arrow = true) => {
    const g = document.createElementNS(NS, 'path');
    g.setAttribute('d', rounded(pts, 0) + (arrow ? head(pts[pts.length - 1], pts[pts.length - 2]) : ''));
    g.setAttribute('class', 'hd-wire'); g.dataset.group = group;
    wires.append(g); groups.push(g);
  };
  const label = (text, x, y, side) => { const s = h('span', `hd-wire-label is-${side}`); s.textContent = text; s.style.left = `${x}px`; s.style.top = `${y}px`; labels.append(s); };

  function draw() {
    const W = canvas.clientWidth, H = canvas.clientHeight;
    wires.setAttribute('viewBox', `0 0 ${W} ${H}`); wires.setAttribute('width', W); wires.setAttribute('height', H);
    wires.replaceChildren(); labels.replaceChildren(); groups = [];
    const G = 4; // air between a line and a card
    const A = box('harness'), ay = A.y + A.h / 2;
    if (!NARROW.matches) {
      // each side: a line out of each layer, a bus between the pair, one arrow into the harness
      const L = LEFT.map(box), R = RIGHT.map(box);
      const lx = (L[0].x + L[0].w + A.x) / 2, rx = (A.x + A.w + R[0].x) / 2;
      L.forEach((b, i) => wire([[b.x + b.w + G, b.y + b.h / 2], [lx, b.y + b.h / 2], [lx, ay]], LEFT[i], false));
      R.forEach((b, i) => wire([[b.x - G, b.y + b.h / 2], [rx, b.y + b.h / 2], [rx, ay]], RIGHT[i], false));
      wire([[lx, ay], [A.x - G, ay]], 'trunk-l');
      wire([[rx, ay], [A.x + A.w + G, ay]], 'trunk-r');
    } else {
      const Ls = ORDER.map(box);
      // a phone: one column (Foundations, Intelligence, Harness, Components, Moves); a bus down the
      // right side gathers the four and turns into the harness
      const gx = A.x + A.w + 16;
      Ls.forEach((b, i) => wire([[b.x + b.w + G, b.y + b.h / 2], [gx, b.y + b.h / 2], [gx, ay]], ORDER[i], false));
      wire([[gx, ay], [A.x + A.w + G, ay]], 'trunk');
    }
    light(lit);
  }

  // ---------- lighting ----------
  let lit = null, pinned = null;
  function light(key) {
    lit = key;
    canvas.classList.toggle('has-lit', !!key);
    for (const [k, c] of Object.entries(cards)) c.classList.toggle('is-lit', k === key);
    groups.forEach(g => g.classList.toggle('is-lit', !!key && (g.dataset.group === key || g.dataset.group === 'trunk' || g.dataset.group === (LEFT.includes(key) ? 'trunk-l' : 'trunk-r'))));
    const L = key && byLayer[key];
    defName.textContent = L ? L.title : IDLE_NAME;
    defText.textContent = L ? L.def : IDLE;
  }
  const keyOf = (t) => t?.closest?.('.hd-layer')?.dataset.key || null;
  canvas.addEventListener('pointerover', (e) => { const k = keyOf(e.target); if (k) light(k); });
  canvas.addEventListener('pointerout', (e) => { if (!keyOf(e.relatedTarget)) light(pinned); });
  canvas.addEventListener('click', (e) => { const k = keyOf(e.target); pinned = k; light(k); });
  canvas.addEventListener('focusin', (e) => { const k = keyOf(e.target); if (k) light(k); });
  canvas.addEventListener('focusout', (e) => { if (!canvas.contains(e.relatedTarget)) light(pinned); });

  const ro = new ResizeObserver(() => requestAnimationFrame(draw));
  ro.observe(canvas);
  NARROW.addEventListener('change', draw);
  document.fonts?.ready?.then(() => el.isConnected && draw());
  draw();
  return () => { ro.disconnect(); NARROW.removeEventListener('change', draw); };
}
```


## Words (glossary)

Source: `site/js/glossary.js`, whole file

```js
// The design harness glossary: one definition per term, shared by the article's
// inline term chips (written [Term](term:slug) in the content), the harness viewer
// and the architecture diagram. layer: which of the four layers a term belongs to.
// href: the harness page that shows it, when there is one.
// Edit the words here; every place that defines a term reads them.

export const LAYERS = [
  { slug: 'foundations', title: 'Foundations', def: 'The design system values: the decisions every design starts from.' },
  { slug: 'intelligence', title: 'Intelligence', def: 'A layer of context for agents: who does the work, what they may and may not do, and what they remember.' },
  { slug: 'components', title: 'Components', def: 'The built pieces: components, the patterns they combine into, and the screens made of those.' },
  { slug: 'moves', title: 'Commands', def: 'Defined design actions for agents: the ways a prompt becomes a design complete, with the designer in the loop.' },
];

const T = (term, def, extra = {}) => ({ term, def, ...extra });

export const GLOSSARY = {
  // the idea
  'design-harness': T('Design harness', 'An opinionated schema for an agent-native design system. It gives an agent an "eye" for design, the way a coding harness gives it "hands".'),
  'coding-harness': T('Coding harness', 'The software that translates a model into a system that can affect its environment (Rubric Labs). It lets an agent act: read files, run code, call tools.'),
  'agent-native': T('Agent-native', 'Written for agents to read and act on as well as for people: explicit, structured and complete enough that nothing relies on a designer filling the gaps.'),
  'design-complete': T('Design complete', 'Finished to the standard you would ship: every state, edge and detail resolved, not just a convincing first pass.'),
  'design-system': T('Design system', 'The shared values, components and rules a team designs with. Written for people; it relies on a designer for judgement.'),

  // the four layers
  foundations: T('Foundations', LAYERS[0].def, { layer: 'foundations', href: '#/harness' }),
  intelligence: T('Intelligence', LAYERS[1].def, { layer: 'intelligence', href: '#/harness' }),
  components: T('Components', LAYERS[2].def, { layer: 'components', href: '#/harness/components' }),
  moves: T('Commands', LAYERS[3].def, { layer: 'moves' }),

  // Foundations
  brand: T('Brand', 'Who the work is for and how it should feel: positioning, voice, marks and the lines it never crosses.', { layer: 'foundations', href: '#/harness/brand' }),
  colors: T('Colors', 'The palette as named roles (paper, ink, accent, signal) rather than raw hex, so every theme can swap values without changing meaning.', { layer: 'foundations', href: '#/harness/colors' }),
  typography: T('Typography', 'Faces, sizes, line heights and tracking as a small set of named styles, plus when to use each.', { layer: 'foundations', href: '#/harness/typography' }),
  icons: T('Icons', 'One icon set with its grid, stroke and naming, so an agent picks an icon instead of drawing one.', { layer: 'foundations', href: '#/harness/icons' }),
  spacing: T('Spacing', 'A spacing scale and the rules for using it: what sits a step apart and what sits a paragraph apart.', { layer: 'foundations', href: '#/harness/spacing' }),
  motion: T('Motion', 'Durations and easing curves by purpose (arrive, leave, hover, think), so movement feels like one hand made it.', { layer: 'foundations', href: '#/harness/motion' }),
  sound: T('Sound', 'The palette of interface sounds: notes, envelopes and when each plays.', { layer: 'foundations', href: '#/harness/sound' }),
  images: T('Images', 'How imagery is chosen, cropped and treated: sources, ratios, grading and what to avoid.', { layer: 'foundations' }),
  layout: T('Layout', 'Grids, columns and breakpoints: where things go and how they reflow on a phone.', { layer: 'foundations' }),
  materials: T('Materials', 'Surfaces and their physical qualities: grain, edges, shadows, depth.', { layer: 'foundations', href: '#/harness/materials' }),
  writing: T('Writing', 'Voice, tone and the rules for interface copy: what to say, and what never to say.', { layer: 'foundations', href: '#/harness/writing' }),
  themes: T('Themes', 'Complete sets of colour values that swap together, like light, dark or a brand variant.', { layer: 'foundations', href: '#/harness/themes' }),
  shaders: T('Shaders', 'GPU effects with their parameters and limits, kept as values an agent can tune rather than code it rewrites.', { layer: 'foundations', href: '#/harness/shaders' }),

  // Intelligence
  generalists: T('Generalists', 'Agents that lead a piece of work end to end and hand parts of it to specialists.', { layer: 'intelligence', href: '#/harness/agents' }),
  specialists: T('Specialists', 'Agents with one craft (type, motion, sound, accessibility) that a generalist delegates to.', { layer: 'intelligence', href: '#/harness/agents' }),
  policies: T('Policies', 'What agents may and may not do: the rules, permissions and checks a design has to pass.', { layer: 'intelligence', href: '#/harness/policy' }),
  skills: T('Skills', 'Packaged ways of doing a task well, which an agent loads when the task comes up.', { layer: 'intelligence', href: '#/harness/skills' }),
  vocabulary: T('Vocabulary', 'The shared words designers and agents use for the same things, so a brief means one thing.', { layer: 'intelligence', href: '#/harness/vocabulary' }),
  memories: T('Memories', 'Decisions and preferences kept from earlier work, so the agent does not ask twice.', { layer: 'intelligence', href: '#/harness/memories' }),

  // Components
  'components-item': T('Components', 'The smallest built pieces: a button, a field, a chip, each with its states.', { layer: 'components', href: '#/harness/components' }),
  patterns: T('Patterns', 'Components combined into a recurring arrangement, like a nav, a hero or a message row.', { layer: 'components', href: '#/harness/patterns' }),
  screens: T('Screens', 'Whole views made of patterns, with their states (empty, loading, error, full).', { layer: 'components', href: '#/harness/screens' }),
  flows: T('Flows', 'Screens in sequence: how someone gets from one to the next to finish a task.', { layer: 'components' }),

  // Commands (slug stays 'moves')
  steer: T('Steer', 'The agent stops and asks the designer to decide what is theirs to decide (taste, scope, audience) before building.', { layer: 'moves' }),
  concept: T('Concept', 'The agent goes wide first: a few genuinely different directions, side by side, before narrowing to one.', { layer: 'moves' }),
  tune: T('Tune', 'The designer drags broad sliders (density, tone, energy) and the agent reworks the design to sit there.', { layer: 'moves' }),
  comment: T('Comment', 'The designer points at one part of a design and the agent changes just that part.', { layer: 'moves' }),
  review: T('Review', 'The agent checks a design against the harness (its foundations, policies and checks) and fixes what fails.', { layer: 'moves' }),

  // the future
  evals: T('Evals', 'Repeatable tests that score outputs, so a change to the harness can be measured rather than guessed.'),
  'win-rate': T('Win rate', 'How often people prefer one output over another in a blind comparison.'),
  'token-efficiency': T('Token efficiency', 'How much design quality you get for the tokens an agent spends reading and working.'),
  'design-router': T('Design router', 'Something that picks the right design harness for the task at hand, the way a model router picks a model.'),
  distillation: T('Distillation', 'Building a harness by extracting foundations, intelligence and components from design-complete work you already have.'),
};

// the four layers in order, each with its terms, for the viewer and the diagram
export const STRUCTURE = {
  foundations: ['brand', 'colors', 'typography', 'icons', 'spacing', 'motion', 'sound', 'images', 'layout', 'materials', 'writing', 'themes', 'shaders'],
  intelligence: ['generalists', 'specialists', 'policies', 'skills', 'vocabulary', 'memories'],
  components: ['components-item', 'patterns', 'screens'],
  moves: ['steer', 'concept', 'tune', 'comment', 'review'],
};

export const termOf = (slug) => GLOSSARY[slug] || null;
```


Rendered DOM on the live site at 1440 (captured 2026-11-11):

```html
<div class="embed embed-harness-diagram hd" data-embed="harness-diagram" data-stream-skip="">
 <figure class="hd-fig">
  <div class="hd-canvas">
   <svg aria-hidden="true" class="hd-wires" height="216" viewbox="0 0 820 216" width="820">
    <path class="hd-wire" d="(icon path omitted)" data-group="foundations">
    </path>
    <path class="hd-wire" d="(icon path omitted)" data-group="intelligence">
    </path>
    <path class="hd-wire" d="(icon path omitted)" data-group="components">
    </path>
    <path class="hd-wire" d="(icon path omitted)" data-group="moves">
    </path>
    <path class="hd-wire" d="(icon path omitted)" data-group="trunk-l">
    </path>
    <path class="hd-wire" d="(icon path omitted)" data-group="trunk-r">
    </path>
   </svg>
   <div class="hd-board">
    <div class="hd-side is-left">
     <div aria-describedby="hd-def" aria-label="Foundations" class="hd-card hd-foundations hd-layer" data-key="foundations" role="group" tabindex="0">
      <span class="hd-ico">
       <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
        <path d="(icon path omitted)">
        </path>
       </svg>
      </span>
      <span class="hd-title">
       Foundations
      </span>
     </div>
     <div aria-describedby="hd-def" aria-label="Intelligence" class="hd-card hd-intelligence hd-layer" data-key="intelligence" role="group" tabindex="0">
      <span class="hd-ico">
       <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
        <path d="(icon path omitted)">
        </path>
       </svg>
      </span>
      <span class="hd-title">
       Intelligence
      </span>
     </div>
    </div>
    <div aria-hidden="true" class="hd-card hd-harness hd-node" data-key="harness">
     <span class="hd-ico">
      <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
       <path d="(icon path omitted)">
       </path>
      </svg>
     </span>
     <span class="hd-title">
      Harness
     </span>
    </div>
    <div class="hd-side is-right">
     <div aria-describedby="hd-def" aria-label="Components" class="hd-card hd-components hd-layer" data-key="components" role="group" tabindex="0">
      <span class="hd-ico">
       <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
        <path d="(icon path omitted)">
        </path>
       </svg>
      </span>
      <span class="hd-title">
       Components
      </span>
     </div>
     <div aria-describedby="hd-def" aria-label="Moves" class="hd-card hd-moves hd-layer" data-key="moves" role="group" tabindex="0">
      <span class="hd-ico">
       <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
        <path d="(icon path omitted)">
        </path>
       </svg>
      </span>
      <span class="hd-title">
       Moves
      </span>
     </div>
    </div>
   </div>
   <div class="hd-labels">
   </div>
  </div>
  <figcaption aria-live="polite" class="hd-def" id="hd-def">
   <span class="hd-def-name">
    Harness
   </span>
   <span class="hd-def-text">
    An opinionated schema for an agent-native design system. It gives an agent an "eye" for design, the way a coding harness gives it "hands".
   </span>
  </figcaption>
  <ul class="sr-only">
   <li>
    Four layers feed the harness: Foundations, Intelligence, Components, Moves.
   </li>
   <li>
    Foundations: The design system values: the decisions every design starts from.
   </li>
   <li>
    Intelligence: A layer of context for agents: who does the work, what they may and may not do, and what they remember.
   </li>
   <li>
    Components: The built pieces: components, the patterns they combine into, the screens made of those, and the flows between screens.
   </li>
   <li>
    Moves: Defined design actions for agents: the ways a prompt becomes a design complete, with the designer in the loop.
   </li>
  </ul>
 </figure>
</div>

```
