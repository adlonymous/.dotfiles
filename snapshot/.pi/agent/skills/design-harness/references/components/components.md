---
title: Components
slug: components
status: published
description: UI components overview.
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

# Components Overview

This section documents the atomic UI components that compose Saleh Digital's interface.

## Component Categories

### Primitives
- **Chip**: Rounded label for categories, tags, or states
- **Icon Button**: Small icon-only button for meta actions
- **Switch**: Binary on/off toggle control
- **Swatch**: Color preview for theme/accent pickers

### Text Components
- **Highlighted Word**: Inline marked text with subtle background
- **Glow**: Warm emphasis with gold text-shadow (interactive)
- **Spine**: Vertical metadata divider with rotated text

### Interactive Elements
- **Menu Item**: Navigation list item with hover states
- **Dot Matrix Button**: SDF dot-rendered footer buttons

### Media Components
- **Cover**: Book cover image with shadow/border styling

## Component Principles

1. **Minimal markup**: Semantic HTML, minimal wrapper divs
2. **CSS Custom Properties**: All tokens from `tokens.css`
3. **Filter-first**: Use SVG filters (`#ink-ui`, `#ink-body`) for texture
4. **Opacity scales**: `--op-rest`, `--op-peek`, `--op-meta`, `--op-faint`
5. **Motion tokens**: `--ease-land`, `--ease-think`, `--motion-resolve`
6. **Theme-aware**: All colors via CSS variables
7. **Reduced motion**: Respect `prefers-reduced-motion`
8. **Touch-friendly**: 24px minimum touch targets
9. **Accessible**: Semantic HTML, ARIA labels, focus states

## Patterns

See `patterns/` for composed multi-component patterns:
- **Bookshelf**, **Coffee Table**, **Carousel**
- **Post Actions**, **Record Card**, **Settings Row**

## Screens

See `screens/` for full-page layouts:
- **Reading**, **Footer**
