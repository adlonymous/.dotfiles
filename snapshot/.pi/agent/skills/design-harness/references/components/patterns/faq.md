---
title: FAQ
slug: faq
status: published
description: "::faq: the ### questions and their answers after it, as an accordion; the first starts open; heights move on ease-land."
chips:
  - Embed
  - Accordion
created: 2026-11-11T16:05:20Z
updated: 2026-11-11T16:05:35Z
---

Embeds are placed in a post by a paragraph that is only `::name` (`EMBED = /^::([a-z-]+)\s*$/`). `js/embeds.js` replaces it with `<div class="embed embed-NAME" data-embed="NAME" data-stream-skip>`, lazy-imports `js/embeds/NAME.js` and calls `mount(el, ctx)`. Embeds are skipped by the word stream and by the body ink filter (`.col-body article > :not(.embed) { filter: url(#ink-body) }`), so screenshots and diagrams stay sharp.

**What it is.** `::faq` takes the questions (`###` headings) and the answers after it, up to the next `##` heading, and renders them as an accordion (`js/app.js` passes those paragraphs to it). An answer can hold paragraphs, lists and quotes with the site's inline markup (bold, links, term chips). The first question starts open, without animating in. Heights move on the site's `--ease-land` over `--faq-t` (220ms), which is `0ms` under reduced motion. Each question is a button with `aria-expanded`.

Source: `site/css/embeds/faq.css`, whole file

```css
/* ::faq (js/embeds/faq.js): questions in the UI face, answers in the post's serif */
.embed-faq { --faq-line: color-mix(in srgb, var(--ink) 10%, transparent); --faq-t: 220ms; display: flex; flex-direction: column; }
.faq-bar { display: flex; justify-content: flex-end; margin-bottom: 6px; }
.faq-all {
  height: 24px; padding: 0 9px; margin-right: -9px; border: 0; border-radius: 6px; background: none;
  font: 400 13px/24px var(--ui); letter-spacing: -0.2px; color: var(--ink); opacity: var(--op-meta); cursor: pointer;
  transition: opacity 160ms var(--ease-land), background-color 160ms var(--ease-land);
}
.faq-all:hover { opacity: 1; background: color-mix(in srgb, var(--ink) 5%, transparent); }
.faq-all:focus-visible { outline: none; opacity: 1; box-shadow: 0 0 0 2px var(--ring); }

.faq-list { border-top: 1px solid var(--faq-line); }
.faq-item { border-bottom: 1px solid var(--faq-line); }
.col-body .embed-faq .faq-h { margin: 0; font: inherit; letter-spacing: inherit; }
.faq-q {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; width: 100%;
  padding: 14px 0; border: 0; background: none; color: var(--ink); text-align: left; cursor: pointer;
  font: 400 17px/22px var(--ui); letter-spacing: -0.4px; -webkit-tap-highlight-color: transparent;
}
.faq-label { text-wrap: balance; transition: opacity 160ms var(--ease-land); }
.faq-item:not(.is-open) .faq-label { opacity: .78; }
.faq-q:hover .faq-label { opacity: 1; }
.faq-q:focus-visible { outline: none; }
.faq-q:focus-visible .faq-label { border-radius: 4px; box-shadow: 0 0 0 2px var(--paper), 0 0 0 3px var(--ring); }

/* + that turns into −: two 1.5px bars, the upright one folds flat */
.faq-mark { position: relative; flex: none; width: 12px; height: 12px; margin-top: 5px; opacity: var(--op-meta); transition: opacity 160ms var(--ease-land); }
.faq-q:hover .faq-mark { opacity: 1; }
.faq-mark::before, .faq-mark::after { content: ""; position: absolute; left: 0; top: 5.25px; width: 12px; height: 1.5px; border-radius: 1px; background: currentColor; transition: transform var(--faq-t) var(--ease-land); }
.faq-mark::after { transform: rotate(90deg); }
.is-open .faq-mark::after { transform: rotate(180deg) scaleX(0); }
.is-open .faq-mark { color: var(--accent-mark); opacity: 1; }

/* the answer: rows 0fr to 1fr, so it opens to its own height */
.faq-a { display: grid; grid-template-rows: 0fr; opacity: 0; transition: grid-template-rows var(--faq-t) var(--ease-land), opacity var(--faq-t) var(--ease-land); }
.is-open > .faq-a { grid-template-rows: 1fr; opacity: 1; }
.faq-inner { min-height: 0; overflow: hidden; display: flex; flex-direction: column; gap: calc(var(--para) * 0.75); }
.faq-inner > :first-child { margin-top: 0; }
.faq-inner > :last-child { margin-bottom: 18px; }
.faq-inner p { margin: 0; }
/* the answer's text sits just under the question, inset to the mark's left */
.faq-inner { padding-right: 28px; }

.embed-faq.is-still *, .embed-faq.is-still *::before, .embed-faq.is-still *::after { transition: none !important; }
@media (prefers-reduced-motion: reduce) { .embed-faq { --faq-t: 0ms; } }
@media (max-width: 899px) { .faq-q { padding: 13px 0; font-size: 16px; line-height: 21px; } .faq-inner { padding-right: 0; } }
```


Source: `site/js/embeds/faq.js`, whole file

```js
// ::faq, the questions (### headings) and answers after it, as an accordion.
// ctx: { paras, inline } where paras are { b: 'h3', t } questions each followed by their
// answer blocks (strings or { t }, or a { b: 'ul' | 'ol' | 'quote', t } list), and
// inline(el, text) renders the site's inline markup (bold, links, term chips) into el.
// The first question starts open. Heights move on the site's ease-land; reduced motion is instant.
const CSS = new URL('../../css/embeds/faq.css', import.meta.url).href;
function css() {
  if (document.querySelector(`link[href="${CSS}"]`)) return;
  const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = CSS; document.head.append(l);
}
let uid = 0;
const textOf = (p) => typeof p === 'string' ? p : String(p?.t ?? '');
const lines = (t) => String(t).split('\n').map(x => x.trim()).filter(Boolean);

export function mount(el, ctx = {}) {
  css();
  const inline = ctx.inline || ((n, t) => { n.textContent = t; return n; });
  const make = (tag, cls) => { const n = document.createElement(tag); if (cls) n.className = cls; return n; };

  // group the blocks into { q, answer: [...] }
  const qs = [];
  for (const p of ctx.paras || []) {
    if (p && typeof p === 'object' && p.b === 'h3') qs.push({ q: p.t, a: [] });
    else if (qs.length && textOf(p).trim()) qs[qs.length - 1].a.push(p);
  }
  if (!qs.length) { el.hidden = true; return; }

  const id = `faq-${++uid}`;
  const bar = make('div', 'faq-bar');
  const all = make('button', 'faq-all'); all.type = 'button';
  bar.append(all);
  const list = make('div', 'faq-list');

  const items = qs.map((x, i) => {
    const item = make('div', 'faq-item');
    const h = make('h3', 'faq-h');
    const btn = make('button', 'faq-q'); btn.type = 'button';
    btn.id = `${id}-q${i}`; btn.setAttribute('aria-controls', `${id}-a${i}`);
    const label = make('span', 'faq-label'); inline(label, x.q);
    const mark = make('span', 'faq-mark'); mark.setAttribute('aria-hidden', 'true');
    btn.append(label, mark); h.append(btn);
    const region = make('div', 'faq-a'); region.id = `${id}-a${i}`;
    region.setAttribute('role', 'region'); region.setAttribute('aria-labelledby', btn.id);
    const inner = make('div', 'faq-inner');
    for (const p of x.a) {
      const b = typeof p === 'object' ? p.b : null;
      if (b === 'ul' || b === 'ol') { const l = make(b); l.append(...lines(p.t).map(t => inline(make('li'), t))); inner.append(l); }
      else if (b === 'quote') { const q = make('blockquote'); q.append(...lines(p.t).map(t => inline(make('p'), t))); inner.append(q); }
      else inner.append(inline(make('p'), textOf(p)));
    }
    region.append(inner); item.append(h, region); list.append(item);
    const it = { item, btn, region, open: false };
    btn.addEventListener('click', () => { set(it, !it.open); syncAll(); });
    return it;
  });

  function set(it, open) {
    it.open = open;
    it.btn.setAttribute('aria-expanded', String(open));
    it.item.classList.toggle('is-open', open);
    it.region.inert = !open;
  }
  function syncAll() {
    const every = items.every(it => it.open);
    all.textContent = every ? 'Collapse all' : 'Expand all';
    all.setAttribute('aria-label', every ? 'Collapse all answers' : 'Expand all answers');
  }
  all.addEventListener('click', () => { const open = !items.every(it => it.open); items.forEach(it => set(it, open)); syncAll(); });

  // first open, without animating in
  el.classList.add('is-still');
  items.forEach((it, i) => set(it, i === 0));
  syncAll();
  el.replaceChildren(bar, list);
  requestAnimationFrame(() => requestAnimationFrame(() => el.classList.remove('is-still')));
}
```


Rendered DOM on the live site at 1440 (captured 2026-11-11):

```html
<div class="embed embed-faq" data-embed="faq" data-stream-skip="">
 <div class="faq-bar">
  <button aria-label="Expand all answers" class="faq-all" type="button">
   Expand all
  </button>
 </div>
 <div class="faq-list">
  <div class="faq-item is-open">
   <h3 class="faq-h">
    <button aria-controls="faq-1-a0" aria-expanded="true" class="faq-q" id="faq-1-q0" type="button">
     <span class="faq-label">
      Who are design harnesses for?
     </span>
     <span aria-hidden="true" class="faq-mark">
     </span>
    </button>
   </h3>
   <div aria-labelledby="faq-1-q0" class="faq-a" id="faq-1-a0" role="region">
    <div class="faq-inner">
     <p>
      Design harnesses are for people who seek above-average design, which usually means designers or founders or anyone who is willing to go the extra mile for design quality.
     </p>
    </div>
   </div>
  </div>
  <div class="faq-item">
   <h3 class="faq-h">
    <button aria-controls="faq-1-a1" aria-expanded="false" class="faq-q" id="faq-1-q1" type="button">
     <span class="faq-label">
      How do I use a design harness?
     </span>
     <span aria-hidden="true" class="faq-mark">
     </span>
    </button>
   </h3>
   <div aria-labelledby="faq-1-q1" class="faq-a" id="faq-1-a1" inert="" role="region">
    <div class="faq-inner">
     <p>
      A design harness is a set of files your agent reads before it designs anything, like your foundations, components, skills and policies. Once it's in place, I mostly work the way I normally would. I give a brief, the agent steers me on the decisions that are mine to make, shows me a few concepts, and I tune from there. Most of the time I don't notice the harness at all (which I think is how it should be).
     </p>
    </div>
   </div>
  </div>
  <div class="faq-item">
   <h3 class="faq-h">
    <button aria-controls="faq-1-a2" aria-expanded="false" class="faq-q" id="faq-1-q2" type="button">
     <span class="faq-label">
      When should I use a design harness?
     </span>
     <span aria-hidden="true" class="faq-mark">
     </span>
    </button>
   </h3>
   <div aria-labelledby="faq-1-q2" class="faq-a" id="faq-1-a2" inert="" role="region">
    <div class="faq-inner">
     <p>
      I think of a design harness as "always-on". I use mine for everything, from a full landing page to a single button state.
     </p>
    </div>
   </div>
  </div>
  <div class="faq-item">
   <h3 class="faq-h">
    <button aria-controls="faq-1-a3" aria-expanded="false" class="faq-q" id="faq-1-q3" type="button">
     <span class="faq-label">
      How is a design harness different from a design system?
     </span>
     <span aria-hidden="true" class="faq-mark">
     </span>
    </button>
   </h3>
   <div aria-labelledby="faq-1-q3" class="faq-a" id="faq-1-a3" inert="" role="region">
    <div class="faq-inner">
     <p>
      I see a design harness as the next step after a
      <button aria-controls="term-pop" aria-describedby="term-def-design-system" aria-expanded="false" aria-haspopup="dialog" class="term" data-term="design-system" type="button">
       design system
      </button>
      . A design system was written for people. It describes the work and relies on a designer for judgment and discretion. A design harness keeps the design system at its core and adds two things around it. Intelligence gives agents the context they need, and moves give them a defined way to get from a prompt to design complete.
     </p>
    </div>
   </div>
  </div>
  <div class="faq-item">
   <h3 class="faq-h">
    <button aria-controls="faq-1-a4" aria-expanded="false" class="faq-q" id="faq-1-q4" type="button">
     <span class="faq-label">
      Do I need a design system before I can build a design harness?
     </span>
     <span aria-hidden="true" class="faq-mark">
     </span>
    </button>
   </h3>
   <div aria-labelledby="faq-1-q4" class="faq-a" id="faq-1-a4" inert="" role="region">
    <div class="faq-inner">
     <p>
      No, but it helps. If you already have one, it becomes your foundations. If you don't, I'd start with work you're already proud of (a shipped product, a brand book, even a deck) and distill the harness out of that.
     </p>
    </div>
   </div>
  </div>
  <div class="faq-item">
   <h3 class="faq-h">
    <button aria-controls="faq-1-a5" aria-expanded="false" class="faq-q" id="faq-1-q5" type="button">
     <span class="faq-label">
      How do I make my own design harness?
     </span>
     <span aria-hidden="true" class="faq-mark">
     </span>
    </button>
   </h3>
   <div aria-labelledby="faq-1-q5" class="faq-a" id="faq-1-a5" inert="" role="region">
    <div class="faq-inner">
     <p>
      The most effective method I've found is
      <button aria-controls="term-pop" aria-describedby="term-def-distillation" aria-expanded="false" aria-haspopup="dialog" class="term" data-term="distillation" type="button">
       distillation
      </button>
      . I take a few design-complete artifacts and extract the foundations, intelligence and components from them. I'd recommend starting small. Your colors, your type and a short list of things you'd never do will already get you further than a blank prompt. From there, I add to the harness every time I settle a decision while I work.
     </p>
    </div>
   </div>
  </div>
  <div class="faq-item">
   <h3 class="faq-h">
    <button aria-controls="faq-1-a6" aria-expanded="false" class="faq-q" id="faq-1-q6" type="button">
     <span class="faq-label">
      Which agents does it work with?
     </span>
     <span aria-hidden="true" class="faq-mark">
     </span>
    </button>
   </h3>
   <div aria-labelledby="faq-1-q6" class="faq-a" id="faq-1-a6" inert="" role="region">
    <div class="faq-inner">
     <p>
      In principle, any agent that can read files, since a design harness is just files. I use mine with [product], so that's where I've tested it the most.
     </p>
    </div>
   </div>
  </div>
  <div class="faq-item">
   <h3 class="faq-h">
    <button aria-controls="faq-1-a7" aria-expanded="false" class="faq-q" id="faq-1-q7" type="button">
     <span class="faq-label">
      Won't everything start to look the same?
     </span>
     <span aria-hidden="true" class="faq-mark">
     </span>
    </button>
   </h3>
   <div aria-labelledby="faq-1-q7" class="faq-a" id="faq-1-a7" inert="" role="region">
    <div class="faq-inner">
     <p>
      It can, if the harness is too strict. I've found it's a balance. If it's too loose, the agent ignores it. If it's too tight, every output starts to feel like a template. I try to keep the parts that make the work feel like mine and leave room for the agent to explore. Moves like
      <button aria-controls="term-pop" aria-describedby="term-def-steer" aria-expanded="false" aria-haspopup="dialog" class="term" data-term="steer" type="button">
       Steer
      </button>
      and
<!-- … truncated here; the rest repeats the same structure -->
```
