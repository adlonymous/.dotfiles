---
title: Book card
slug: cover
status: published
description: "A book card (Library and Coffee table details): cover, title, author, chips, the catalogue description and its source line; arrows step through the shelf."
chips:
  - Component
  - Book
  - Card
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:07:17Z
---

When a book is opened, its details are set as plain text beside it, never as a modal (see the [no modals for books](../../intelligence/memories/no-modals-for-books.md) memory). The card's fields: the cover, the title, the author, the chips (year, publisher and so on), then the description, whose last line names where it came from (`.info-source`, for example Open Library). A book that has notes gets a wider card, so the text keeps a reading measure. Prev and next [dot-matrix buttons](dot-matrix-button.md) step through the shelf.

Source: `site/js/gallery.js`, lines 205 to 313

```js
// ---------- a book's card: cover, title, author, details; arrows step through the shelf ----------
let card = null, cRecs = [], cAt = 0;
const SOURCE_LINE = /^Description from (Open Library|Google Books)\.?$/;
function inlineText(el, t) {
  for (const r of parseInline(String(t).replace(/\s*\n\s*/g, ' '))) {
    let node = document.createTextNode(r.text);
    if (r.i) { const em = document.createElement('em'); em.append(node); node = em; }
    if (r.b) { const b = document.createElement('strong'); b.append(node); node = b; }
    el.append(node);
  }
}
function buildCard() {
  card = document.createElement('dialog');
  card.className = 'info-card';
  card.innerHTML = `
    <div class="info-sheet">
      <div class="info-cover"><img alt=""></div>
      <div class="info-text">
        <h2 class="info-title"></h2>
        <p class="info-desc"></p>
        <div class="info-chips"></div>
        <div class="info-body"></div>
        <p class="info-source"></p>
        <div class="info-foot">
          <span class="info-count"></span>
          <span class="viewer-ctrls">
            <button type="button" class="viewer-btn" data-go="-1" aria-label="Previous book">${dotIcon('prev')}</button>
            <button type="button" class="viewer-btn" data-go="1" aria-label="Next book">${dotIcon('next')}</button>
          </span>
        </div>
      </div>
      <button type="button" class="viewer-btn info-close" data-close aria-label="Close" autofocus>${dotIcon('close')}</button>
    </div>`;
  document.body.append(card);
  card.addEventListener('click', (e) => {
    if (e.target === card || e.target.closest('[data-close]')) return closeCard();
    const b = e.target.closest('[data-go]'); if (b) cardStep(+b.dataset.go);
  });
  card.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') { e.preventDefault(); cardStep(1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); cardStep(-1); }
  });
  card.addEventListener('cancel', (e) => { e.preventDefault(); closeCard(); });
}
// a book's details, in the site's type: title, author, chips, the description and its source line
export function fillDetails(el, rec) {
  if (!el.querySelector('.info-title')) el.innerHTML = '<h2 class="info-title"></h2><p class="info-desc"></p><div class="info-chips"></div><div class="info-body"></div><p class="info-source"></p>';
  el.querySelector('.info-title').textContent = rec.title;
  const d = el.querySelector('.info-desc'); d.textContent = rec.desc; d.hidden = !rec.desc;
  el.querySelector('.info-chips').replaceChildren(); // books show the title and description only, no tags
  const paras = rec.body.map(p => (typeof p === 'string' ? p : p.t) || '');
  const src = SOURCE_LINE.test(paras[paras.length - 1] || '') ? paras.pop() : '';
  el.querySelector('.info-body').replaceChildren(...paras.map(t => { const p = document.createElement('p'); inlineText(p, t); return p; }));
  const s = el.querySelector('.info-source'); s.textContent = src; s.hidden = !src;
  return paras.length;
}
function fillCard() {
  const rec = cRecs[cAt];
  const img = card.querySelector('.info-cover img');
  card.querySelector('.info-sheet').classList.toggle('no-cover', !rec.images[0]);
  if (rec.images[0]) { img.src = rec.images[0]; img.alt = `Cover of ${rec.title}`; } else { img.removeAttribute('src'); img.alt = ''; }
  card.querySelector('.info-title').textContent = rec.title;
  const d = card.querySelector('.info-desc'); d.textContent = rec.desc; d.hidden = !rec.desc;
  card.querySelector('.info-chips').replaceChildren(); // books show the title and description only, no tags
  // the notes: a catalogue description, its last line naming where it came from
  const paras = rec.body.map(p => (typeof p === 'string' ? p : p.t) || '');
  const src = SOURCE_LINE.test(paras[paras.length - 1] || '') ? paras.pop() : '';
  card.querySelector('.info-body').replaceChildren(...paras.map(t => { const el = document.createElement('p'); inlineText(el, t); return el; }));
  card.querySelector('.info-sheet').classList.toggle('has-body', paras.length > 0);
  card.classList.toggle('has-body', paras.length > 0);
  const s = card.querySelector('.info-source'); s.textContent = src; s.hidden = !src;
  card.querySelector('.info-text').scrollTop = 0;
  card.querySelector('.info-count').textContent = `${cAt + 1}/${cRecs.length}`;
  [cAt + 1, cAt - 1].forEach(k => { if (cRecs[k]?.images[0]) { const p = new Image(); p.src = cRecs[k].images[0]; } });
}
function cardStep(d) {
  if (cRecs.length < 2) return;
  cAt = (cAt + d + cRecs.length) % cRecs.length;
  const sheet = card.querySelector('.info-sheet');
  if (reducedMotion.matches) return fillCard();
  sheet.animate([{ opacity: 1, filter: 'blur(0px)' }, { opacity: 0, filter: 'blur(4px)' }], { duration: 110, easing: 'cubic-bezier(0.4, 0, 1, 1)' }).onfinish = () => {
    fillCard();
    sheet.animate([{ opacity: 0, filter: 'blur(4px)' }, { opacity: 1, filter: 'blur(0px)' }], { duration: 220, easing: 'cubic-bezier(0.2, 0, 0, 1)' });
  };
}
function typeTile(rec, onClick) {
  const b = document.createElement('button'); b.type = 'button'; b.className = 'masonry-cell type-tile';
  b.setAttribute('aria-label', `${rec.title}, details`);
  const t = document.createElement('span'); t.className = 'type-tile-title'; t.textContent = rec.title;
  const d = document.createElement('span'); d.className = 'type-tile-desc'; d.textContent = rec.desc;
  b.append(t, d);
  if (onClick) b.addEventListener('click', onClick);
  requestAnimationFrame(() => b.classList.add('is-in'));
  return b;
}
export function openInfo(recs, at) {
  if (!card) buildCard();
  cRecs = recs; cAt = at;
  fillCard();
  card.showModal();
  if (!reducedMotion.matches) card.querySelector('.info-sheet').animate([{ opacity: 0, filter: 'blur(6px)', transform: 'translateY(6px) scale(.985)' }, { opacity: 1, filter: 'blur(0px)', transform: 'none' }], { duration: 320, easing: 'cubic-bezier(0.2, 0, 0, 1)' });
}
function closeCard() {
  if (!card?.open) return;
  if (reducedMotion.matches) return card.close();
  card.querySelector('.info-sheet').animate([{ opacity: 1 }, { opacity: 0, filter: 'blur(4px)', transform: 'translateY(4px)' }], { duration: 160, easing: 'cubic-bezier(0.4, 0, 1, 1)' }).onfinish = () => card.close();
}
```


Source: `site/css/site.css`, lines 505 to 542

```css
/* a book's card (Library) */
.info-card { width: min(620px, calc(100vw - 32px)); max-height: calc(100dvh - 48px); padding: 0; border: 0; border-radius: 14px; background: var(--paper); color: var(--ink); overflow: auto;
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 10%, transparent), 0 2px 6px color-mix(in srgb, var(--shadow) calc(6% * var(--shadow-k)), transparent), 0 24px 64px -12px color-mix(in srgb, var(--shadow) calc(22% * var(--shadow-k)), transparent); }
.info-card::backdrop { background: color-mix(in srgb, var(--paper) 78%, transparent); }
.info-sheet { position: relative; display: grid; grid-template-columns: 200px minmax(0, 1fr); gap: 24px; padding: 24px; }
.info-cover img { display: block; width: 100%; height: auto; border-radius: 2px; box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 8%, transparent), 0 12px 32px -12px color-mix(in srgb, var(--shadow) calc(35% * var(--shadow-k)), transparent); }
.info-text { display: flex; flex-direction: column; gap: 6px; min-width: 0; padding-right: 28px; }
.info-title { margin: 0; font: 400 20px/24px var(--ui); letter-spacing: -0.8px; text-wrap: balance; }
.info-desc { margin: 0; font: 400 16px/20.8px var(--serif); letter-spacing: var(--track); color: color-mix(in srgb, var(--ink) 72%, var(--paper)); }
.info-desc[hidden] { display: none; }
.info-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.info-foot { margin-top: auto; padding-top: 16px; display: flex; align-items: center; font: 400 14px/20px var(--ui); color: color-mix(in srgb, var(--ink) 50%, var(--paper)); font-variant-numeric: tabular-nums; }
.info-close { position: absolute; top: 14px; right: 14px; }
/* a book with notes (its catalogue description): a wider card so the text keeps a reading measure,
   and the text column scrolls on its own while the cover and the arrows stay put */
.info-card.has-body { width: min(780px, calc(100vw - 32px)); }
.info-sheet.has-body .info-text { max-height: calc(100dvh - 96px); overflow-y: auto; overscroll-behavior: contain; scrollbar-width: thin; }
.info-body { display: flex; flex-direction: column; gap: 12px; max-width: 60ch; margin-top: calc(var(--para) - 6px); font: 400 16px/20.8px var(--serif); letter-spacing: var(--track); font-kerning: normal; text-wrap: pretty; color: color-mix(in srgb, var(--ink) 72%, var(--paper)); }
.info-body:empty { display: none; }
.info-body p { margin: 0; }
.info-body em { font-style: italic; }
.info-body strong { font-weight: 400; -webkit-text-stroke: .5px currentColor; }
.info-source { margin: 6px 0 0; font: 400 12px/16px var(--ui); letter-spacing: -0.2px; color: color-mix(in srgb, var(--ink) 46%, var(--paper)); }
.info-source[hidden] { display: none; }
.info-sheet.has-body .info-foot { position: sticky; bottom: 0; background: var(--paper); box-shadow: 0 -10px 10px -6px var(--paper); }
@media (max-width: 520px) {
  .info-sheet { grid-template-columns: 1fr; } .info-cover { width: 60%; } .info-text { padding-right: 0; }
  .info-sheet.has-body { gap: 20px; padding: 20px; }
  .info-sheet.has-body .info-cover { width: 44%; }
  .info-sheet.has-body .info-text { max-height: none; overflow: visible; }
  .info-sheet.has-body .info-foot { padding-bottom: 20px; margin-bottom: -20px; }
}
.type-tile { display: flex; flex-direction: column; gap: 8px; aspect-ratio: 3 / 4; padding: 16px; text-align: left; color: var(--ink); background: color-mix(in srgb, var(--ink) 4%, var(--paper)); opacity: 0; transition: opacity 420ms var(--ease-land); }
.type-tile.is-in { opacity: 1; }
.type-tile-title { font: 400 20px/24px var(--ui); letter-spacing: -0.8px; text-wrap: balance; }
.type-tile-desc { margin-top: auto; font: 400 14px/18px var(--serif); color: color-mix(in srgb, var(--ink) 60%, var(--paper)); }
.info-sheet.no-cover { grid-template-columns: 1fr; }
.info-sheet.no-cover .info-cover { display: none; }
```
