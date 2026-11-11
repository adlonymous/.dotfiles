---
title: Spine
slug: spine
status: published
description: Vertical metadata column in reading view.
chips:
  - Component
  - Vocabulary
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

The vertical column in reading/article view that displays metadata (reading time, date, type) as rotated text.

## Definition

**Spine** refers both to the visual element (a vertical text column) and its conceptual role as the "backbone" metadata for long-form content.

## Visual Form

Appears in column 2 (sub) of the reading grid, rotated 90° clockwise, reading bottom-to-top when the viewer's head is tilted right.

## Content Format

`{minutes} min · {date} · {type}`

Example: `8 min · Nov 4, 2026 · Article`

## Styling

```css
.spine {
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  font-size: 13px;
  line-height: 16px;
  letter-spacing: 0.08em;
  opacity: var(--op-meta); /* 0.56 */
  filter: url(#ink-ui);
}
```

## Purpose

- Shows contextual metadata without interrupting reading flow
- Saves horizontal space in the content column
- Provides subtle visual anchor in the margin
- Metaphor: like the spine of a physical book showing title/author

## Responsive

Hidden on mobile (<900px) where vertical space is at a premium.

## Related

See `components/components/spine.md` for full component specification.
