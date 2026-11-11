---
title: Thinking
slug: thinking
status: published
description: Active processing state.
chips:
  - State
  - Vocabulary
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

The visual state shown during active processing, loading, or generation. Indicates the system is working.

## Definition

**Thinking** is the interim state between user action and result. It communicates progress without blocking interaction.

## Visual Forms

**Spinner**: Rotating circle or arc for indeterminate waits.
```css
@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner {
  animation: spin 1s linear infinite;
}
```

**Shimmer**: Subtle wave of light across placeholder content.
```css
@keyframes shimmer {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.7; }
}

.shimmer {
  animation: shimmer 2s ease-in-out infinite;
}
```

**Pulse**: Gentle opacity oscillation for persistent states.
```css
@keyframes pulse {
  0%, 100% { opacity: 0.56; }
  50% { opacity: 0.9; }
}

.pulse {
  animation: pulse 1.6s ease-in-out infinite;
}
```

## Easing

Thinking animations use `--ease-think`: `cubic-bezier(.1, .72, .9, .28)`
- Smooth acceleration and deceleration
- Feels contemplative, not frantic

## Duration

Scales with `--fnd-energy`:
- Low energy: slower, calmer thinking animations
- High energy: faster, snappier transitions

## Transition to Rest

Thinking state resolves to final content with `--motion-resolve` timing and `--ease-land` easing. See `vocabulary/resolve.md`.

## Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  .spinner,
  .shimmer,
  .pulse {
    animation: none;
    opacity: 0.56; /* static reduced opacity */
  }
}
```

## Usage

- Show thinking state for operations >200ms
- Avoid blocking UI during thinking
- Provide cancel option for long operations
- Resolve smoothly to final state (no abrupt cuts)

## Related

See `motion/motion.md` for animation principles and `vocabulary/resolve.md` for completion transitions.
