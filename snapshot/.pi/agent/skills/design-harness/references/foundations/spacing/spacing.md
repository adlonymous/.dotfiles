---
title: Spacing
slug: spacing
status: published
order: 3
description: Each column is exactly as wide as its longest title, so the gaps between menu, pages and post stay even.
chips:
  - Column gap 24
  - Paragraph 16
  - Post 640 wide
created: 2026-11-09T14:21:21Z
updated: 2026-11-09T17:23:21Z
---


Three spacing tokens do almost all of the work. They live in `css/tokens.css` on `:root` and scale with one density value (`--fnd-density`, default `.3`).

```css
:root {
  --fnd-density: .3;
  --gap:   calc(24px + (.3 - var(--fnd-density)) * 20px);  /* 24px: between grid columns */
  --para:  calc(16px + (.3 - var(--fnd-density)) * 14px);  /* 16px: between paragraphs and blocks */
  --stack: 4px;                                             /* between menu items (16px lines, so a 20px pitch) */
}
```

## Where each one goes

| Place | Value |
| --- | --- |
| Page padding, desktop | `24px 24px 48px` |
| Page padding, below 900px | `20px 12px 40px` |
| Between grid columns | `var(--gap)` = 24px |
| Between menu items | `var(--stack)` = 4px (16px line + 4px = 20px pitch) |
| Before the Contact / Settings group in the menu | `calc(var(--para) - var(--stack))` = 12px extra, so the pitch there is 32px |
| Between blocks of a post (`article` is a flex column) | `gap: var(--para)` = 16px |
| Above a heading that is not first | `margin-top: calc(var(--para) * 0.75)` = 12px, on top of the 16px gap (28px total) |
| Under a heading | the next block gets `margin-top: calc(var(--para) * -0.5)` = -8px, so 8px total |
| List items | `gap: calc(var(--para) * 0.375)` = 6px, `padding-left: 20px` on the list, `6px` on each item |
| Under the post (actions row) | `margin-top: calc(var(--para) * 1.5)` = 24px |
| Phone: under the menu glyph to the page title | `margin-top: 20px` on `.col-sub` |
| Phone: page title to the post | `margin-top: 28px` on `.col-body` |
| Phone: between page titles | `gap: 8px` |
| Footer row gap when it wraps | `row-gap: 10px` |
| Footer marks | `gap: 8px`, `padding: 0 8px` |

Heading rhythm in CSS, exactly as shipped (the later rule wins over the 1.5x one because they have the same specificity):

```css
.col-body article { display: flex; flex-direction: column; gap: var(--para); outline: none; }
.col-body article > h2:not(:first-child) { margin-top: calc(var(--para) * 1.5); }
.col-body article > :is(h2, h3):not(:first-child) { margin-top: calc(var(--para) * 0.75); }
.col-body article > :is(h2, h3) + * { margin-top: calc(var(--para) * -0.5); }
```

## Rules

- Never add margins to paragraphs; the article's flex `gap` spaces them.
- Columns are as wide as their longest label (see `layout-grid.md`), so every gap on the page reads the same 24px.
- Corners: 16px on image frames and masonry cells, 10px on the Before/After toggle and flow cards (8px under 600px), 6px on chips, 16px 16px 0 0 on the phone menu sheet.
