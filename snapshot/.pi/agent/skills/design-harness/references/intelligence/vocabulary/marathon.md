---
title: Marathon
slug: marathon
status: published
description: High-contrast focus theme.
chips:
  - Theme
  - Vocabulary
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

A high-contrast, high-energy theme mode designed for extended focus sessions. Available in light and dark variants with customizable accent colors.

## Definition

**Marathon** is a theme mode optimized for prolonged reading, writing, or coding sessions. It uses elevated contrast, vivid accent colors, and reduced texture for minimal eye strain and maximum clarity.

## Variants

**Marathon Dark** (`data-theme="marathon-dark"`):
- Near-black background (#000000 to #0a0a0a)
- Pure white ink (#ffffff)
- High contrast (~20:1 ratio)

**Marathon Light** (`data-theme="marathon-light"`):
- Bright white background (#ffffff)
- Deep black ink (#000000)
- High contrast (~21:1 ratio)
- Accent wash highlights on active nav items

## Accent Colors

Marathon supports five accent options (`data-accent`):

**Lime** (default): `#97ee2c` -- bright yellow-green
**Cyan**: `#33d8ff` -- electric blue
**Red**: `#ff3350` -- vivid coral red
**Amber**: `#ffbb14` -- warm gold
**Green**: `#00cc88` -- teal green

## Differences from Default Themes

**Higher contrast**:
- Marathon: ~20:1 ratio (WCAG AAA+)
- Default dark: ~14:1 ratio

**Reduced texture**:
- Ink filters less pronounced
- Grain overlay lighter or disabled
- Crisp edges, minimal blur

**Accent-driven**:
- Active states use vivid accent colors
- Links and interactive elements highly saturated
- Clear visual hierarchy

**No glow effects**:
- `.warm` glow disabled or reduced in Marathon
- Focus on readability over atmosphere

## Foundation Slider Overrides

Marathon ignores or clamps some foundation sliders:
- `--fnd-texture`: forced low (0.1–0.2)
- `--fnd-glow`: forced off (0)
- `--fnd-focus`: clamped high (0.8–1.0)

## Usage

Enable Marathon mode in `/settings`:
1. Choose Marathon Dark or Marathon Light
2. Select accent color (lime, cyan, red, amber, green)
3. Settings persist in localStorage

## Use Cases

- Long reading sessions (articles, books)
- Writing and editing
- Coding and debugging
- Accessibility (low vision, high contrast preference)

## Related

See `themes/marathon-dark.md`, `themes/marathon-light.md`, and `themes/marathon-accents.md` for full token specifications.
