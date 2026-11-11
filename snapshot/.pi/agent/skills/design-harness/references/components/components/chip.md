---
title: Record chip
slug: chip
status: published
description: "Record chips: quiet label-value pills under a record; \"#RRGGBB Name\" shows a swatch, a typeface name is set in that typeface."
chips:
  - Component
  - Chip
order: 4
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:07:17Z
---

Chips belong to [records](../patterns/record.md) (`chips:` in a record's frontmatter). Each one is a `span.rec-chip`:

- `#RRGGBB Name` gives an `i.rec-swatch` filled with that colour, then the name.
- A typeface name (`Shinka`, `Inter Display`, `Kult Luxury`) is set in that face (`var(--serif)`, `var(--ui)` or `"Kult Luxury", var(--ui)`).
- Anything else is plain text.

On a plain page (Speaking) the chips are a quiet line of data under the title instead: Inter Display 14/20 in `--muted`, with separators at .6.

Source: `site/js/records.js`, lines 54 to 68

```js
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
```


Source: `site/css/site.css`, lines 354 to 368

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
```


Source: `site/css/site.css`, lines 755 to 757

```css
/* Speaking: the title, then its data in one quiet line */
.records.is-plain .rec-meta { margin: 4px 0 0; display: flex; flex-wrap: wrap; column-gap: 8px; row-gap: 2px; font: 400 14px/20px var(--ui); letter-spacing: -0.2px; color: var(--muted); }
.records.is-plain .rec-sep { opacity: .6; }
```
