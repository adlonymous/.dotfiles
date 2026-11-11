---
title: Emergence
slug: emergence
status: published
description: Page-load animation sequence.
chips:
  - Motion
  - Vocabulary
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

The staggered animation of elements appearing on page load. Each element fades in and translates upward in sequence.

## Definition

**Emergence** is the coordinated reveal of page content during initial render. Elements animate from hidden to visible with a slight upward translation, staggered by a short delay.

## Implementation

Base animation:
```css
@keyframes emerge {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.emerge {
  animation: emerge var(--motion-resolve) var(--ease-land);
  animation-delay: calc(var(--emerge-index, 0) * var(--motion-stagger));
}
```

## Parameters

- **Duration**: `--motion-resolve` (~420–600ms)
- **Delay**: `--motion-stagger` (12ms per index)
- **Distance**: 8px translateY
- **Easing**: `--ease-land` (cubic-bezier(.2, 0, 0, 1))

## Stagger Index

Each sibling element gets an incremented `--emerge-index`:
```css
.item:nth-child(1) { --emerge-index: 0; }
.item:nth-child(2) { --emerge-index: 1; }
.item:nth-child(3) { --emerge-index: 2; }
```

## Usage

- Apply to page sections, cards, list items on initial render
- Skip on subsequent navigations (use View Transitions instead)
- Respect `prefers-reduced-motion` (instant appear)
- Keep stagger subtle (12ms is barely perceptible individually, but creates flow)

## Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  .emerge {
    animation: none;
    opacity: 1;
    transform: none;
  }
}
```

## Related

See `motion/emergence.md` for full specification.
