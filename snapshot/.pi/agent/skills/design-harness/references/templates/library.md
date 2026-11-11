---
title: Library
slug: library
status: published
description: "Library: one grid page (\"Books\"), no sub-nav; the books stand spine-out on shelves drawn in three.js, and a click pulls one out with its details beside it."
chips:
  - Template
  - Library
  - Grid
created: 2026-11-11T15:03:00Z
updated: 2026-11-11T16:10:14Z
---

Route: `#/library`. It is a section that is one grid page, so `html` has `is-solo is-gallery is-flat`: there is no sub-nav, and the grid starts right after the menu (`.col-gallery { grid-column: 2 / -1 }`).

The menu at every page (live, 2026-11-11, after that day's site sync): **Welcome, Articles, Lectures, Speaking, Experiments, Library, Coffee table**, a paragraph step, then **Theme, Sound, MCP**. There is one menu entry per room (`js/rooms.js`); Theme, Sound and MCP are app pages, not CMS sections. See [navigation](../components/patterns/navigation.md).

- **Header** (`.sp-head`): the page title "Books" (`.sp-title`) and a count (`.sp-count`).
- **Grid:** the [Library shelf](../components/patterns/bookshelf.md) ("Spines"), made of [book spines](../components/components/spine.md). A pulled book shows its [book card](../components/components/cover.md) details beside it in `.sp-reader` (cover, title, by, details).
- **Live:** 34 books on 2 shelves at 1440 × 1000. With GL on, `html` also has `has-grid-gl sp-gl`.
- **Fallbacks:** without WebGL or under reduced motion, static DOM spines.
- **Sound:** a phone shelf scroll steps the drag palette.

Rendered structure (live at 1440, 2026-11-11; trimmed to the first two books of each shelf):

```html
'+open('/workspace/lib-excerpt.html').read()+'
```
