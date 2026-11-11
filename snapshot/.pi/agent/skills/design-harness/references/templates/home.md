---
title: Home Template
slug: home
status: published
description: "The front door: since 2026-11-11 / opens Welcome; before that, the newest article."
chips:
  - Template
  - Layout
created: 2026-11-11T15:03:00Z
updated: 2026-11-11T15:03:00Z
---

**Since 2026-11-11** `https://saleh.digital/` opens **Welcome** (`#/welcome`), the first room in the menu: one serif paragraph introducing Ahmed, with the ways to reach him as its sub-nav. See [welcome](welcome.md). The static `<title>` is "Ahmed Saleh" and the canonical URL `https://saleh.digital/`; the app sets the title to "Welcome, Ahmed Saleh".

Before that day, `/` resolved to the newest article ("What is a design harness?") and rendered it with the [article](article.md) template, with Articles active. That article is now at `#/articles`.

There is still no hero, no list of recent posts, no header logo and no "Home" menu item.

## Head (from the live page)

```html
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>What is a design harness?, Ahmed Saleh</title>
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="Ahmed Saleh — writing" href="https://saleh.digital/feed.xml">
<link rel="preload" href="fonts/InterDisplay-Regular.woff2" as="font" type="font/woff2" crossorigin>
```

Other rooms (Lectures, Speaking, Library, …) are reached from the menu; see `templates/record.md` for a record page such as a lecture and `templates/library.md` for the grid rooms.
