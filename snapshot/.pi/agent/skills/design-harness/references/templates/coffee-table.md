---
title: Coffee table
slug: coffee-table
status: published
description: "Coffee table: one grid page (\"The shelf\"), no sub-nav; books lie on the page seen from above under a cursor light; a click lifts one to you with its details."
chips:
  - Template
  - Coffee table
  - Grid
created: 2026-11-11T16:10:00Z
updated: 2026-11-11T16:10:14Z
---

Route: `#/coffee-table`. It is a one-grid section (`html.is-solo.is-gallery.is-flat`, plus `has-grid-gl ct-gl` with GL), with no sub-nav.

The menu at every page (live, 2026-11-11, after that day's site sync): **Welcome, Articles, Lectures, Speaking, Experiments, Library, Coffee table**, a paragraph step, then **Theme, Sound, MCP**. There is one menu entry per room (`js/rooms.js`); Theme, Sound and MCP are app pages, not CMS sections. See [navigation](../components/patterns/navigation.md).

- **Grid:** the [Coffee table](../components/patterns/coffee-table.md) ("The table"). There are 10 books live. `.ct` holds `.ct-shelf` (one `button.ct-book` per book, over the drawn books) and `.ct-detail` (the lifted book's details as plain text).
- **Fallbacks:** without WebGL, a DOM shelf in which the other books go soft behind the lifted one.
