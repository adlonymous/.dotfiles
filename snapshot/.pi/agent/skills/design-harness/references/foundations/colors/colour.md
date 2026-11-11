---
title: Colour
slug: colour
status: published
description: Semantic color tokens and theme overrides.
chips:
  - Foundation
  - Colors
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Detailed semantic color token definitions and per-theme overrides. All colors reference British spelling "colour" in file/folder names but American "color" in code tokens.

## Semantic Tokens

Defined in `colors.md`:
- `--paper`: Background
- `--ink`: Primary text
- `--dot`: Low-opacity elements (dividers, secondary UI)
- `--accent`: Interactive elements, active states
- `--signal`: Warning/alert
- `--ok`: Success/confirmation (green)
- `--warm`: Emphasis glow (gold)
- `--shadow`: Drop shadow color
- `--shade`: Subtle tint variations

## Theme Overrides

Each theme (light, dark, marathon-dark, marathon-light) defines specific hex values for these tokens. See individual theme files in `themes/` for complete values.

## Opacity Tokens

- `--op-rest`: ~0.39 (resting state)
- `--op-peek`: ~0.70 (hover state)
- `--op-meta`: ~0.56 (metadata/secondary text)
- `--op-faint`: ~0.32 (very subtle)

## Usage

Always reference semantic names, never hardcode hex:
```css
color: var(--ink);
background: var(--paper);
border-color: color-mix(in srgb, var(--dot) 20%, transparent);
```

## Related

See `colors.md` for overview and `themes/*.md` for per-theme values.
