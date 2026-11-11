---
title: Glyph Matrix
slug: glyph-matrix
status: published
description: SDF dot matrix text rendering.
chips:
  - Rendering
  - Vocabulary
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Signed-distance field (SDF) based dot matrix rendering technique for text. Used in footer wordmark and dot-rendered buttons.

## Definition

**Glyph Matrix** is the system for rendering text as a grid of small circles (dots) whose opacity is determined by a signed-distance field derived from glyph outlines.

## How It Works

1. **Generate SDF**: Convert font glyphs to signed-distance field textures (distance from glyph edge at each pixel)
2. **Sample grid**: For each dot position in the grid, sample the SDF value
3. **Threshold and smooth**: If SDF > threshold, render dot with opacity based on distance (smoothstep)
4. **Render dots**: Draw circles at 2× device pixel ratio for sharpness

## Parameters

**Dot size**: 2px (1px in low-density mode)
**Dot gap**: 4px (spacing between dot centers)
**Threshold**: 0.5 (SDF value at which dots appear)
**Smoothing**: 0.1 (transition range for anti-aliasing)

## Rendering Code (Conceptual)

```js
function renderGlyphMatrix(ctx, text, x, y, dotSize, dotGap) {
  const sdf = generateSDF(text, font);
  
  for (let row = 0; row < sdf.height; row += dotGap) {
    for (let col = 0; col < sdf.width; col += dotGap) {
      const distance = sdf.sample(col, row);
      
      if (distance > threshold) {
        const opacity = smoothstep(threshold - smoothing, threshold + smoothing, distance);
        ctx.fillStyle = `rgba(var(--dot-rgb), ${opacity})`;
        ctx.fillRect(x + col, y + row, dotSize, dotSize);
      }
    }
  }
}
```

## Visual Effect

- Retro display aesthetic (dot matrix printer, LED signage)
- Smooth scaling (SDF allows arbitrary sizes without pixelation)
- Texture and depth (individual dots create grain)
- Theme-aware (dot color uses `--dot` token)

## Usage

**Footer wordmark**: Large "salehdigital" text rendered as dots
**Footer links**: Smaller dot-rendered button labels
**Experimental UI**: Optional dot rendering for headings or logos

## Performance

- Pre-render SDF textures at build time
- Render dots to canvas at 2× for retina clarity
- Cache rendered canvases, regenerate only on resize or theme change

## Related

See `skills/sdf-rendering.md` for implementation details and `tools/sdf-type-bench.md` for performance testing.
