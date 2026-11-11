---
title: Resolve
slug: resolve
status: published
description: Transition from thinking to rested state.
chips:
  - Motion
  - Vocabulary
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

The smooth transition from a loading/thinking/processing state to the final rested state.

## Definition

**Resolve** is the motion curve and timing applied when an element finishes processing and settles into its final state. It uses a strong deceleration easing to communicate "done."

## Implementation

```css
.is-thinking {
  opacity: 0.56;
  /* shimmer or spinner animation */
}

.is-resolved {
  opacity: 1;
  transition: opacity var(--motion-resolve) var(--ease-land);
}
```

## Timing

- **Duration**: `--motion-resolve` = `calc(.6s - .18s * var(--fnd-energy))`
  - Low energy (0): 600ms
  - Default energy (0.5): 510ms
  - High energy (1): 420ms

## Easing

`--ease-land`: `cubic-bezier(.2, 0, 0, 1)`
- Strong deceleration
- Feels like "landing" or "settling"
- Conveys completion and rest

## Usage

- Spinner → content reveal
- Shimmer → final text
- Button press → success state
- Data load → render
- AI generation → final output

## Visual Pattern

1. **Thinking**: Shimmer, spinner, or reduced opacity
2. **Resolve**: Fade/scale to full opacity, content appears
3. **Rest**: Final state, no animation

## Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  .is-resolved {
    transition-duration: 0.1s; /* brief but instant-feeling */
  }
}
```

## Related

See `motion/resolve.md` for full specification.
