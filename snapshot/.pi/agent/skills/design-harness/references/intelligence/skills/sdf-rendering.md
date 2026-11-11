---
title: SDF Rendering
slug: sdf-rendering
status: published
description: Signed-distance field techniques for text and graphics.
chips:
  - Skill
  - Rendering
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Procedure for implementing signed-distance field (SDF) rendering for smooth, scalable text and graphics.

## Steps

**1. Generate SDF Texture**:
- Load font glyphs as vector paths
- Rasterize each glyph to high-resolution bitmap
- For each pixel, compute signed distance to nearest glyph edge (positive inside, negative outside)
- Normalize distances to 0–1 range
- Store as grayscale texture (8-bit or 16-bit)

**2. Sample SDF in Shader/Canvas**:
- For each output pixel or dot position, sample the SDF texture
- Use bilinear interpolation for smooth sampling
- Compare sampled distance to threshold value

**3. Apply Threshold and Smoothing**:
```glsl
float distance = texture2D(sdfTexture, uv).a;
float alpha = smoothstep(threshold - smoothing, threshold + smoothing, distance);
```

**4. Render Output**:
- For dot matrix: if alpha > 0, draw circle with opacity = alpha
- For smooth text: use alpha as pixel opacity or AA mask

## Parameters

- `threshold`: Distance value at which glyph edge appears (typically 0.5)
- `smoothing`: Transition range for anti-aliasing (0.05–0.15)
- `scale`: Output size vs SDF resolution (lower = sharper, higher = faster)

## Benefits

- Smooth scaling without blur or pixelation
- Small texture size (one channel, low resolution)
- Real-time effects (outlines, shadows, warping)
- Sharp rendering on high-DPI displays

## Usage

Apply to:
- Footer wordmark dot matrix
- Heading text (experimental)
- Icon rendering (alternative to SVG masks)

## Related

See `vocabulary/glyph-matrix.md` for dot matrix rendering specifics and `tools/sdf-type-bench.md` for performance tuning.
