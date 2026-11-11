---
title: Record card
slug: record
status: published
description: "A page's records as cards: a small line icon, the title, the description, chips with values; notes behind a quiet Details control that streams open."
chips:
  - Pattern
  - Record
  - Card
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:08:52Z
---

Records are a page's items, each its own CMS file (`content/<section>/<page>/<record>.md`, `{ slug, title, description, chips, media, body? }`). They render after the page's text as cards:

- a small line icon, picked by the title (`ICONS`: the owner's own 20px stroke icons; their paths are omitted below)
- the title
- the description
- the [chips](../components/chip.md)

Notes in parts (an `h3` and then its paragraphs: Design, Where it's used, Connects to, History) sit behind a quiet **Details** control: a label column and the text. They open with the site's stream (the words ink in behind the caret) while the panel's height eases open over 360ms (`grid-template-rows`, land; the chevron moves on think). A record with media takes attention ([media reveal](media-reveal.md)). **Plain** records (Speaking) have no icon and no description, and their chips are a quiet line of data under the title.

Source: `site/js/records.js`, whole file

```js
// Records: a page's items (item.records), each its own file in the CMS
// (content/<section>/<page>/<record>.md): { slug, title, description, chips, media, body? }.
// They render as cards: an icon, the title, the description, and chips with values.
// Chips: "#RRGGBB Name" shows a swatch; a typeface name is set in that typeface.
// Images (media) are revealed on attention (js/media.js).
import { streamIn } from './resolve.js';
export const recordsOf = (item) => item?.records || [];

const S = (d) => `<svg viewBox="0 0 20 20" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round">${d}</svg>`;
// one small line icon per record, picked by its title
const ICONS = [
  [/^(?:light)$/i, S('<circle cx="10" cy="10" r="3.2"/><path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:dark)$/i, S('<path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:marathon (?:dark|light))$/i, S('<rect x="3.5" y="3.5" width="13" height="13" rx="2"/><path d="(icon path omitted: icon set is commercial)" /><path d="(icon path omitted: icon set is commercial)" fill="currentColor" stroke="none" opacity=".9"/>')],
  [/^(?:marathon accents)$/i, S('<circle cx="6" cy="7" r="2.2" fill="currentColor"/><circle cx="14" cy="7" r="2.2"/><circle cx="6" cy="14" r="2.2"/><circle cx="14" cy="14" r="2.2" fill="currentColor" opacity=".5"/>')],
  [/^(?:colou?r)$/i, S('<circle cx="10" cy="10" r="6.5"/><path d="(icon path omitted: icon set is commercial)" fill="currentColor" stroke="none"/>')],
  [/^(?:type)$/i, S('<path d="(icon path omitted: icon set is commercial)"/><path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:spacing)$/i, S('<rect x="3" y="4" width="4" height="12" rx="1"/><rect x="13" y="4" width="4" height="12" rx="1"/><path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:texture)$/i, S('<circle cx="5" cy="5" r=".6" fill="currentColor"/><circle cx="10" cy="5" r=".6" fill="currentColor"/><circle cx="15" cy="5" r=".6" fill="currentColor"/><circle cx="7.5" cy="10" r=".6" fill="currentColor"/><circle cx="12.5" cy="10" r=".6" fill="currentColor"/><circle cx="5" cy="15" r=".6" fill="currentColor"/><circle cx="10" cy="15" r=".6" fill="currentColor"/><circle cx="15" cy="15" r=".6" fill="currentColor"/>')],
  [/^(?:resolve)$/i, S('<circle cx="7.5" cy="10" r="4"/><rect x="9" y="6" width="8" height="8" rx="2" stroke-dasharray="1.6 1.6"/>')],
  [/^(?:motion)$/i, S('<path d="(icon path omitted: icon set is commercial)"/><circle cx="3" cy="16" r="1" fill="currentColor"/><circle cx="17" cy="4" r="1" fill="currentColor"/>')],
  [/^(?:sound)$/i, S('<path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:menu item)$/i, S('<path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:highlighted word)$/i, S('<path d="(icon path omitted: icon set is commercial)"/><path d="(icon path omitted: icon set is commercial)" stroke-dasharray="1.5 2"/><path d="(icon path omitted: icon set is commercial)" opacity=".4"/>')],
  [/^(?:glow|orb bench)$/i, S('<circle cx="10" cy="10" r="2.5" fill="currentColor"/><circle cx="10" cy="10" r="6.5" opacity=".35"/>')],
  [/^(?:icons)$/i, S('<rect x="3.5" y="3.5" width="5" height="5" rx="1.2"/><rect x="11.5" y="3.5" width="5" height="5" rx="2.5"/><rect x="3.5" y="11.5" width="5" height="5" rx="2.5"/><rect x="11.5" y="11.5" width="5" height="5" rx="1.2"/>')],
  [/^(?:mcp)$/i, S('<path d="(icon path omitted: icon set is commercial)"/><path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:streaming)$/i, S('<path d="(icon path omitted: icon set is commercial)"/><rect x="13.5" y="8.2" width="2.2" height="3.6" rx=".4" fill="currentColor" stroke="none"/><path d="(icon path omitted: icon set is commercial)" opacity=".4"/>')],
  [/^(?:emergence)$/i, S('<path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:hidden extras)$/i, S('<circle cx="7" cy="10" r="3"/><path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:wordmark)$/i, S('<path d="(icon path omitted: icon set is commercial)"/><circle cx="15.5" cy="13.5" r=".7" fill="currentColor"/><circle cx="17.5" cy="13.5" r=".7" fill="currentColor"/><circle cx="15.5" cy="11.5" r=".7" fill="currentColor"/>')],
  [/^(?:reading)$/i, S('<rect x="3" y="3.5" width="14" height="13" rx="1.5"/><path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:footer)$/i, S('<rect x="3" y="3.5" width="14" height="13" rx="1.5"/><path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:debug panel)$/i, S('<path d="(icon path omitted: icon set is commercial)"/><circle cx="8" cy="6" r="1.4" fill="var(--paper)"/><circle cx="13" cy="10" r="1.4" fill="var(--paper)"/><circle cx="6.5" cy="14" r="1.4" fill="var(--paper)"/>')],
  [/^(?:cms)$/i, S('<path d="(icon path omitted: icon set is commercial)"/><path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:sdf type bench)$/i, S('<circle cx="10" cy="10" r="2"/><circle cx="10" cy="10" r="4.5" opacity=".6"/><circle cx="10" cy="10" r="7" opacity=".3"/>')],
  [/^(?:wordmark shader bench)$/i, S('<path d="(icon path omitted: icon set is commercial)"/><path d="(icon path omitted: icon set is commercial)" opacity=".6"/><path d="(icon path omitted: icon set is commercial)" opacity=".3"/>')],
  [/^(?:my words)$/i, S('<path d="(icon path omitted: icon set is commercial)"/><path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:made live)$/i, S('<circle cx="10" cy="10" r="1.6" fill="currentColor"/><path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:little first)$/i, S('<circle cx="10" cy="10" r="1.3" fill="currentColor"/><circle cx="10" cy="10" r="4" opacity=".55"/><circle cx="10" cy="10" r="6.8" opacity=".25"/>')],
  [/^(?:detail)$/i, S('<circle cx="8.5" cy="8.5" r="4.5"/><path d="(icon path omitted: icon set is commercial)"/>')],
  [/^(?:punctuation)$/i, S('<path d="(icon path omitted: icon set is commercial)"/>')],
];
// records that hold images: one picture, or a stack of frames
const PICTURE = S('<rect x="3.5" y="4" width="13" height="12" rx="1.5"/><circle cx="7.5" cy="8" r="1.2"/><path d="(icon path omitted: icon set is commercial)"/>');
const FRAMES = S('<rect x="5.5" y="6.5" width="11" height="9.5" rx="1.5"/><path d="(icon path omitted: icon set is commercial)"/>');
const BOOK = S('<path d="(icon path omitted: icon set is commercial)"/><path d="(icon path omitted: icon set is commercial)"/>');
const MIC = S('<rect x="7.5" y="3" width="5" height="9" rx="2.5"/><path d="(icon path omitted: icon set is commercial)"/>');
const kindIcon = (chips) => chips.some(c => /^\s*(lecture|talk|presentation|teaching|panel|workshop|fireside)/i.test(c)) ? MIC : chips.some(c => /^\s*\d{4}\s*$/.test(c)) ? BOOK : null;
const iconFor = (title) => (ICONS.find(([re]) => re.test(title)) || [null, S('<circle cx="10" cy="10" r="2" fill="currentColor"/>')])[1];
const FONTS = { 'shinka': 'var(--serif)', 'inter display': 'var(--ui)', 'kult luxury': '"Kult Luxury", var(--ui)' };

function chipEl(text) {
  const c = document.createElement('span');
  c.className = 'rec-chip';
  const hex = text.match(/^(#[0-9a-f]{3,8})\b\s*(.*)$/i);
  if (hex) {
    const sw = document.createElement('i'); sw.className = 'rec-swatch'; sw.style.background = hex[1];
    c.append(sw, document.createTextNode(hex[2] ? `${hex[2]} ` : ''));
    const v = document.createElement('span'); v.className = 'rec-val'; v.textContent = hex[1].toUpperCase(); c.append(v);
    return c;
  }
  const font = Object.keys(FONTS).find(f => text.toLowerCase().startsWith(f));
  if (font) c.style.fontFamily = FONTS[font];
  c.textContent = text;
  return c;
}

// Notes in parts (an h3 then its paragraphs: Design, Where it's used, Connects to, History)
// sit behind a quiet "Details" control: a label column and the text, opening with the
// site's stream (words ink in behind the caret) while the panel's height eases open.
let detailsSeq = 0;
function detailsEl(blocks, paraEl) {
  const id = `rec-notes-${++detailsSeq}`;
  const btn = document.createElement('button');
  btn.type = 'button'; btn.className = 'rec-more';
  btn.setAttribute('aria-expanded', 'false'); btn.setAttribute('aria-controls', id);
  btn.innerHTML = '<span class="rec-more-t">Details</span><svg viewBox="0 0 10 10" aria-hidden="true"><path d="(icon path omitted: icon set is commercial)"/><path class="v" d="(icon path omitted: icon set is commercial)"/></svg>';
  const panel = document.createElement('div'); panel.className = 'rec-notes'; panel.id = id; panel.hidden = true;
  const dl = document.createElement('dl'); dl.className = 'rec-parts';
  let dd = null;
  for (const b of blocks) {
    if (b.b === 'h3') {
      const part = document.createElement('div'); part.className = 'rec-part';
      const dt = document.createElement('dt'); dt.textContent = b.t;
      dd = document.createElement('dd'); part.append(dt, dd); dl.append(part);
      continue;
    }
    if (!dd) { const part = document.createElement('div'); part.className = 'rec-part is-lead'; dd = document.createElement('dd'); part.append(dd); dl.append(part); }
    dd.append(paraEl(b));
  }
  const inner = document.createElement('div'); inner.className = 'rec-notes-in'; inner.append(dl);
  panel.append(inner);
  let timer = 0;
  const set = (open) => {
    clearTimeout(timer);
    btn.setAttribute('aria-expanded', String(open));
    btn.querySelector('.rec-more-t').textContent = open ? 'Hide details' : 'Details';
    if (open) {
      panel.hidden = false;
      requestAnimationFrame(() => panel.classList.add('is-open'));
      // the words stream in, unless the post itself is still streaming (one stream at a time)
      if (!document.querySelector('[data-streaming]')) streamIn(dl, 'state');
      else dl.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 200 });
    } else {
      panel.classList.remove('is-open');
      timer = setTimeout(() => { panel.hidden = true; }, 320);
    }
  };
  btn.addEventListener('click', () => set(btn.getAttribute('aria-expanded') !== 'true'));
  panel.addEventListener('keydown', (e) => { if (e.key === 'Escape') { set(false); btn.focus(); } });
  btn.addEventListener('keydown', (e) => { if (e.key === 'Escape' && btn.getAttribute('aria-expanded') === 'true') { e.stopPropagation(); set(false); } });
  return [btn, panel];
}

// paraEl renders a record's notes (its optional body), block by block, under the description
// plain: no icon, no description, and the chips as a quiet line of data under the title (Talks)
export function recordsEl(records, inlineInto, paraEl, { plain = false } = {}) {
  const wrap = document.createElement('div');
  wrap.className = 'records' + (plain ? ' is-plain' : '');
  for (const rec of records) {
    if (plain) {
      const r = document.createElement('div'); r.className = 'record';
      const t = document.createElement('div'); t.className = 'rec-title'; t.textContent = rec.title;
      const m = document.createElement('p'); m.className = 'rec-meta';
      (rec.chips || []).filter(Boolean).forEach((c, i) => { if (i) m.append(Object.assign(document.createElement('span'), { className: 'rec-sep', textContent: '·', ariaHidden: 'true' })); m.append(Object.assign(document.createElement('span'), { textContent: c })); });
      const body = document.createElement('div'); body.className = 'rec-body';
      body.append(t); if (m.childElementCount) body.append(m);
      r.append(body); wrap.append(r); continue;
    }
    const title = rec.title, desc = rec.description || '', chips = rec.chips || [];
    const r = document.createElement('div'); r.className = 'record';
    const media = rec.media || [];
    const ico = document.createElement('span'); ico.className = 'rec-ico'; ico.innerHTML = media.length ? (media.length > 1 ? FRAMES : PICTURE) : (ICONS.find(([re]) => re.test(title.trim()))?.[1] || kindIcon(chips) || iconFor(title));
    const body = document.createElement('div'); body.className = 'rec-body';
    const t = document.createElement('div'); t.className = 'rec-title'; t.textContent = title; t.prepend(ico);
    const cs = document.createElement('div'); cs.className = 'rec-chips';
    cs.append(...chips.filter(Boolean).map(chipEl));
    body.append(t);
    if (desc) { const d = inlineInto(document.createElement('p'), desc); d.className = 'rec-desc'; body.append(d); }
    const blocks = (rec.body || []).map(b => typeof b === 'string' ? { t: b } : b);
    const parted = blocks.some(b => b.b === 'h3');
    if (!parted) for (const b of blocks) { const n = paraEl(b); n.classList.add('rec-desc'); body.append(n); }
    if (cs.childElementCount) body.append(cs);
    if (parted) body.append(...detailsEl(blocks, paraEl));
    r.append(body);
    if (media.length) {
      // something to discover: a quiet mark after the title, and the record takes attention (hover, focus, a tap)
      r.dataset.media = media.join(',');
      r.classList.add('has-media');
      r.tabIndex = 0;
      const mk = document.createElement('i'); mk.className = 'rec-mark'; mk.setAttribute('aria-hidden', 'true');
      const sr = document.createElement('span'); sr.className = 'sr-only'; sr.textContent = media.length === 1 ? ', with an image' : `, with ${media.length} images`;
      t.append(mk, sr);
    }
    wrap.append(r);
  }
  return wrap;
}
```


Source: `site/css/site.css`, lines 354 to 399

```css
/* ---------- harness records: icon, title, description, chips ---------- */
.records { display: flex; flex-direction: column; gap: 0; margin-top: 4px; }
.record { display: block; padding: 14px 0; box-shadow: inset 0 -1px 0 color-mix(in srgb, var(--ink) 8%, transparent); }
.record:first-child { padding-top: 6px; }
.record:last-child { box-shadow: none; }
.rec-ico { display: inline-block; width: 16px; height: 16px; margin-right: 6px; vertical-align: -2.5px; color: var(--ink); }
.rec-ico svg { width: 16px; height: 16px; display: block; }
.rec-body { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.rec-title { font: 400 16px/20px var(--ui); letter-spacing: var(--track); }
.rec-desc { margin: 0; color: color-mix(in srgb, var(--ink) 72%, var(--paper)); }
.rec-chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.rec-chip { display: inline-flex; align-items: center; gap: 6px; height: 22px; padding: 0 8px; border-radius: 6px; font: 400 12px/16px var(--ui); letter-spacing: -0.2px; font-variant-numeric: tabular-nums; white-space: nowrap; color: var(--ink); background: color-mix(in srgb, var(--ink) 4%, var(--paper)); box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--ink) 7%, transparent); }
.rec-swatch { width: 10px; height: 10px; border-radius: 3px; box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--ink) 18%, transparent); }
.rec-val { color: color-mix(in srgb, var(--ink) 50%, var(--paper)); font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 11px; letter-spacing: 0; }

/* a record's notes in parts, behind a quiet "Details" control (js/records.js detailsEl) */
.rec-more {
  align-self: flex-start; display: inline-flex; align-items: center; gap: 6px;
  margin: 6px 0 0 -6px; padding: 4px 6px; border: 0; border-radius: 6px; background: none; cursor: pointer;
  font: 400 12px/16px var(--ui); letter-spacing: -0.2px; color: var(--muted);
  transition: color 160ms var(--ease-land), background 160ms var(--ease-land), transform 120ms var(--ease-land);
}
.rec-more svg { width: 10px; height: 10px; fill: none; stroke: currentColor; stroke-width: 1.25; stroke-linecap: round; overflow: visible; }
.rec-more .v { transform-origin: 5px 5px; transition: transform 360ms var(--ease-think), opacity 200ms var(--ease-land); }
.rec-more[aria-expanded="true"] .v { transform: rotate(90deg); opacity: 0; }
.rec-more:hover, .rec-more[aria-expanded="true"] { color: var(--ink); }
.rec-more:hover { background: color-mix(in srgb, var(--ink) 4%, transparent); }
.rec-more:active { transform: scale(0.97); }
.rec-more:focus-visible { outline: none; box-shadow: 0 0 0 2px var(--paper), 0 0 0 3px var(--ring); }
.rec-notes { display: grid; grid-template-rows: 0fr; opacity: 0; transition: grid-template-rows 360ms var(--ease-land), opacity 200ms var(--ease-land); }
.rec-notes.is-open { grid-template-rows: 1fr; opacity: 1; }
.rec-notes[hidden] { display: none; }
.rec-notes-in { min-height: 0; overflow: hidden; }
.rec-parts { position: relative; margin: 0; padding: 10px 0 4px; display: flex; flex-direction: column; gap: 14px; }
.rec-part { display: grid; grid-template-columns: 112px minmax(0, 1fr); column-gap: 16px; }
.rec-part dt { font: 400 12px/16px var(--ui); letter-spacing: -0.2px; color: var(--muted); padding-top: 3px; }
.rec-part dd { margin: 0; color: color-mix(in srgb, var(--ink) 80%, var(--paper)); }
.rec-part dd > * { margin: 0; }
.rec-part dd > * + * { margin-top: 8px; }
.rec-part.is-lead { grid-template-columns: minmax(0, 1fr); }
@media (max-width: 600px) {
  .rec-part { grid-template-columns: minmax(0, 1fr); row-gap: 4px; }
  .rec-part dt { padding-top: 0; }
}
@media (prefers-reduced-motion: reduce) { .rec-notes, .rec-more .v { transition: opacity 120ms linear; } }
```
