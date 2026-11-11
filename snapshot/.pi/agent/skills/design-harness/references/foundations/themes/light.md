---
title: Light
slug: light
status: published
description: "Paper: white paper, black ink; the base every other theme overrides."
chips:
  - Theme
  - Light
created: 2026-11-09T19:23:22Z
updated: 2026-11-11T15:59:05Z
---

Palette name: **Paper**. `data-theme="light"`, no `data-accent`. It is the base block every other theme overrides. It is not the first-visit theme: that is Ember (marathon-dark, amber), whatever the system prefers.

The base block below applies to `:root` and to every `[data-theme]`. The other themes override only what they change, and everything else falls back to these values.

```css
:root, [data-theme] {
  color-scheme: light;
  --paper: #fff;
  --ink: #000;
  --dot: #e0e0e0;
  --glow: #FFC81A;
  --ok: #1e9e57;
  --accent: #000;
  --accent-text: var(--ink);
  --accent-mark: var(--ink);
  --accent-wash: transparent;
  --on-accent: var(--paper);
  --ring: var(--ink);
  --signal: var(--ink);
  --tint: var(--ink);
  --swell: var(--ink);
  --shade: #dad8d6;
  --shadow: #000;
  --shadow-k: 1;
  --warm: #d69600;
  --warm-halo: #ffc400;
  --select-bg: var(--ink);
  --select-fg: var(--paper);
  --op-meta: 0.56;
  --op-faint: 0.39;
  --grain-k: 1;
  --foot: var(--ink);
  --muted: color-mix(in srgb, var(--ink) calc(var(--op-meta) * 100%), var(--paper));
```

- theme-color meta: `#ffffff`.
- The accent is the ink (`--accent: #000`), so Paper has no colour accent. `--glow` `#FFC81A` is used only by the new-item orbs and secret traces.
- The grain strength `--grain-k` is 1. The footer ink `--foot` is the ink.
- Shadows on the Coffee table fall toward `--shade` `#dad8d6`.
- Selection: ink background, paper text.

See [Themes](../themes.md) for switching and persistence.
