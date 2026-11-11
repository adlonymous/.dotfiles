---
title: Orb Bench
slug: orb-bench
status: published
description: Performance testing for orb shader (if used).
chips:
  - Tool
  - Shader
  - Performance
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Performance testing and tuning bench for the orb shader (experimental 3D/WebGL element, if implemented on the site).

## Features

**Shader Parameters**:
- Glow intensity
- Rotation speed
- Noise scale and octaves
- Color gradients

**Performance Metrics**:
- Frame rate (fps)
- GPU memory usage
- Shader compile time
- Draw call count

**Quality Settings**:
- Low (optimized for mobile)
- Medium (balanced)
- High (desktop with GPU)

**Visual Preview**:
- Live-rendered orb with current settings
- Rotation and lighting controls
- Background color picker

## UI

Two-column layout:
- Left: parameter sliders and quality presets
- Right: full-screen orb preview canvas
- Bottom: real-time performance metrics

## Export

Save quality preset and shader params as JSON for production.

## Usage

1. Access via `/tools/orb-bench`
2. Tune shader parameters for desired visual effect
3. Monitor frame rate and GPU usage
4. Test across quality presets
5. Export optimal settings for production use

## Related

See `packages/three-js.md` for WebGL library and `skills/sdf-rendering.md` for related shader techniques.
