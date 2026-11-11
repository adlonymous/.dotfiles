---
title: Speaking
slug: speaking
status: published
description: "Speaking (slug talks): the talks listed in the sub-nav; each page is a plain record (title and data line), optional text, and slides when it has them."
chips:
  - Template
  - Speaking
created: 2026-11-11T16:10:00Z
updated: 2026-11-11T16:10:14Z
---

Route: `#/talks/<item>`; the menu label is **Speaking**. The sub-nav lists the talks (six live, newest first). Each page uses the [lectures](lectures.md) template: a plain record title, a data line (kind · role · host · place · date, for example "Talk · Speaker and host · [host] · Montréal, QC · Nov 26, 2025"), optional intro text, and the slides grid when the page has media (`SLIDE_SECTIONS = new Set(['talks', 'lectures'])`). Pages without media have no `is-slides`, and the body ends after the data line.

The menu at every page (live, 2026-11-11, after that day's site sync): **Welcome, Articles, Lectures, Speaking, Experiments, Library, Coffee table**, a paragraph step, then **Theme, Sound, MCP**. There is one menu entry per room (`js/rooms.js`); Theme, Sound and MCP are app pages, not CMS sections. See [navigation](../components/patterns/navigation.md).
