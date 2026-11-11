---
title: Screens
slug: screens
status: published
description: Full-page screen layouts.
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

# Screens Overview

Full-page layouts for major views in Saleh Digital.

## Screen Types

**Reading**: Article/post reading view with 4-column grid (nav, spine, content, margin). Optimized for long-form reading with 640px content width.

**Footer**: Site-wide footer component that appears at bottom of all pages. Features bio, SDF dot matrix canvases, Arabic basmala, and wordmark.

## Core Layout Grid

All screens share the base 4-column grid system:

```css
.cols {
  display: grid;
  grid-template-columns: var(--col-nav, 89px) var(--col-sub, 248px) minmax(0, 640px) minmax(0, 1fr);
  column-gap: var(--gap);
}
```

### Column Roles

1. **Nav (89px)**: Primary navigation menu
2. **Sub (248px)**: Secondary navigation, metadata, or spine
3. **Content (max 640px)**: Main content area
4. **Margin (1fr)**: Breathing room, auxiliary content

## Responsive Collapse

On narrow screens (<900px):

```css
@media (max-width: 899px) {
  .cols {
    display: flex;
    flex-direction: column;
    padding: 0 var(--para);
  }
}
```

Navigation moves to bottom sheet modal dialog.

## Page Templates

Additional page-specific templates should be documented in `templates/`:
- Home page layout
- Library (bookshelf + coffee table)
- Settings page
- Experiments/portfolio grid
- Article reading view

## Common Elements

All screens include:
- Global nav (column 1 on desktop, bottom sheet on mobile)
- Footer at bottom (see `footer.md`)
- Theme/accent switcher (in settings or nav)
- Sound toggle (in nav or post actions)
