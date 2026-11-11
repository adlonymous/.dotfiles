---
title: Record page
slug: record
status: published
description: A page in Lectures or Speaking. The title, then its facts in one quiet grey line split by middle dots. Short, so the footer sits on the bottom of the window.
chips:
  - Title 16/20
  - Meta 14/20 muted
  - Separator ·
created: 2026-11-11T18:00:00Z
updated: 2026-11-11T18:00:00Z
---

Lectures and Speaking pages are records, not essays. Example: `#/lectures/lead-ux-and-product-design-instructor`.

## On screen at 1440 x 900

- Menu with **Lectures** active.
- Column 2: the room's pages, "Philosophy of design" (faded) and "Lead UX and Product Design Instructor" (active). The long title stays on one line because the column is 253px wide.
- Column 3: the record title in Inter Display 16/20 at full ink, then the facts line in 14/20 muted grey, wrapping inside the 640px column.
- Empty paper, then the footer line and the full-width wordmark at the bottom of the window.

## Markup

```html
<main class="col col-body" id="main">
  <article id="article" tabindex="-1">
    <h1 class="sr-only">Lead UX and Product Design Instructor</h1>
    <div class="records is-plain">
      <div class="record">
        <div class="rec-body">
          <div class="rec-title">Lead UX and Product Design Instructor</div>
          <p class="rec-meta"><span>Teaching</span><span class="rec-sep" aria-hidden="true">·</span><span>Lead Instructor</span><span class="rec-sep" aria-hidden="true">·</span><span>Bitmaker (now General Assembly)</span><span class="rec-sep" aria-hidden="true">·</span><span>Greater Toronto Area, ON</span><span class="rec-sep" aria-hidden="true">·</span><span>Oct 2017 to Aug 2018</span></p>
        </div>
      </div>
    </div>
  </article>
</main>
```

## CSS

```css
.records { display: flex; flex-direction: column; gap: 0; margin-top: 4px; }
.record { display: block; padding: 14px 0; box-shadow: inset 0 -1px 0 color-mix(in srgb, var(--ink) 8%, transparent); }
.record:first-child { padding-top: 6px; }
.record:last-child { box-shadow: none; }
.rec-body { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.rec-title { font: 400 16px/20px var(--ui); letter-spacing: var(--track); }
.records.is-plain .rec-meta { margin: 4px 0 0; display: flex; flex-wrap: wrap; column-gap: 8px; row-gap: 2px;
  font: 400 14px/20px var(--ui); letter-spacing: -0.2px; color: var(--muted); }
.records.is-plain .rec-sep { opacity: .6; }
```

The record sits inside `article`, so it also gets `filter: url(#ink-body)`. The frame, menu and footer are the same as every page (foundations/layout-grid.md, components/patterns/navigation.md, components/patterns/footer.md).

## Data (Lectures room, as published)

| Page | Title | Facts |
| --- | --- | --- |
| philosophy-of-design | Philosophy of Design | Lecture · Lecturer and host · Studio 535 · Toronto, ON · Oct 22, 2024 (plus a description line and a slide grid) |
| lead-ux-and-product-design-instructor | Lead UX and Product Design Instructor | Teaching · Lead Instructor · Bitmaker (now General Assembly) · Greater Toronto Area, ON · Oct 2017 to Aug 2018 |
