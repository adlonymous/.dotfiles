---
title: 16px Image Corners
slug: 16px-image-corners
status: published
description: Images have 16px border-radius.
chips:
  - Memory
  - Styling
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

## Memory

All images in article content (photos, diagrams, screenshots) use a 16px border-radius. This creates soft, rounded corners that feel tactile and modern without being overly playful.

## Rules

**Radius**: 16px on all four corners.

**Scope**: Applies to:
- Article body images (`<img>` in `.article-body`)
- Figure images (`<figure><img>`)
- Gallery and viewer images

**Exceptions**:
- Book covers: 2px radius (minimal, preserves rectangular book shape)
- Icons and avatars: varies by component
- Full-bleed images: no radius (edge-to-edge)

## CSS

```css
.article-body img,
.article-body figure img {
  border-radius: 16px;
}
```

## Rationale

**Tactility**: 16px is large enough to feel rounded and soft, suggesting a physical object.

**Not too playful**: Smaller radii (4–8px) feel generic. Larger radii (24–32px) feel toy-like. 16px strikes a balance.

**Consistent detail**: Using one specific value across all content images creates visual rhythm.

**Differentiates from book covers**: Books get minimal 2px radius (they are rectangular objects). Photos get 16px (they are framed moments).

## Usage

Apply this radius automatically to all images inserted into articles via CMS or Markdown renderer.

## Related

See `materials.md` for other border-radius tokens.
