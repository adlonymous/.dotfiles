---
title: Wordmark Shader Bench
slug: wordmark-shader-bench
status: published
description: Test and optimize footer wordmark SDF dot matrix shader.
chips:
  - Tool
  - Shader
  - Performance
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Testing and optimization bench for the footer wordmark dot matrix shader. Tune SDF parameters, measure render performance, and export configurations.

## Features

**Parameter Tuning**:
- Dot size (1–4px)
- Dot gap (2–8px)
- SDF threshold (0–1)
- Smoothing amount (0–0.3)

**Canvas Settings**:
- Width and height
- Device pixel ratio (1× or 2×)
- Background color

**Performance Metrics**:
- Render time (ms)
- Frame rate (fps)
- Memory usage
- Canvas size (KB)

**Visual Preview**:
- Live wordmark rendering with current settings
- Zoom controls for pixel inspection
- Grid overlay to visualize dot placement

**Export**:
- Save optimal settings as JSON
- Generate code snippet for production use

## UI

Split-screen layout:
- Left: parameter sliders and settings
- Right: live preview canvas
- Bottom: performance metrics

## Usage

1. Access via `/tools/wordmark-shader-bench`
2. Adjust sliders to tune rendering
3. Observe visual quality and performance
4. Export settings when optimal
5. Apply exported values to `js/footdots.js`

## Optimal Settings (Baseline)

```json
{
  "dotSize": 2,
  "dotGap": 4,
  "threshold": 0.5,
  "smoothing": 0.1,
  "dpr": 2
}
```

## Related

See `vocabulary/glyph-matrix.md` and `skills/sdf-rendering.md` for SDF rendering techniques.
