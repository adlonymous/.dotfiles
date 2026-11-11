---
title: Experiments
slug: experiments
status: published
description: "Experiments: one grid page (\"Sketches\"), no sub-nav; each sketch is drawn as a matrix of ASCII glyphs that dissolve into the image under a cursor lens."
chips:
  - Template
  - Experiments
  - Grid
created: 2026-11-11T16:10:00Z
updated: 2026-11-11T16:10:14Z
---

Route: `#/experiments`. It is a one-grid section (`html.is-solo.is-gallery.is-flat`, plus `has-grid-gl` with GL), with no sub-nav.

The menu at every page (live, 2026-11-11, after that day's site sync): **Welcome, Articles, Lectures, Speaking, Experiments, Library, Coffee table**, a paragraph step, then **Theme, Sound, MCP**. There is one menu entry per room (`js/rooms.js`); Theme, Sound and MCP are app pages, not CMS sections. See [navigation](../components/patterns/navigation.md).

- **Grid:** the [Glyph matrix](../components/patterns/glyph-matrix.md). There are 16 tiles live: `.xg-tile` > `.xg-frame` and `.xg-cap` (title `.t`, number `.n`, date `.d`). The canvas draws every cell.
- **Click** opens the [viewer](../components/patterns/viewer.md).
- **Fallbacks:** without WebGL, the masonry (`html.is-solo .masonry { columns: 4 200px }`).
