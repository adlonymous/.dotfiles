---
title: SDF Type Bench
slug: sdf-type-bench
status: published
description: Test and tune SDF text rendering parameters.
chips:
  - Tool
  - SDF
  - Performance
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Testing bench for signed-distance field (SDF) type rendering. Tune dot size, gap, threshold, and smoothing parameters for optimal visual quality and performance.

## Features

**Parameter Sliders**:
- Dot size (1–4px)
- Dot gap (2–8px)
- SDF threshold (0–1)
- Smoothing (0–0.3)
- Font size and weight

**Test Strings**:
- Alphabet (uppercase and lowercase)
- Numbers and punctuation
- Sample sentences
- Custom text input

**Performance Metrics**:
- Render time (ms per frame)
- Canvas size (KB)
- Dot count
- Frame rate (fps) during animation

**Visual Tools**:
- Zoom for pixel inspection
- Grid overlay to visualize dot placement
- Threshold visualization (show SDF distance field)

## UI

Split-screen layout:
- Left: parameter controls and test strings
- Right: live SDF-rendered preview canvas
- Bottom: performance metrics panel

## Export

Save optimal settings as JSON:
```json
{
  "dotSize": 2,
  "dotGap": 4,
  "threshold": 0.5,
  "smoothing": 0.1
}
```

Copy code snippet for production use.

## Usage

1. Access via `/tools/sdf-type-bench`
2. Adjust sliders and test different fonts
3. Observe quality vs performance trade-offs
4. Export settings when satisfied
5. Apply to `js/footdots.js` or other SDF rendering code

## Related

See `skills/sdf-rendering.md` and `vocabulary/glyph-matrix.md`.
