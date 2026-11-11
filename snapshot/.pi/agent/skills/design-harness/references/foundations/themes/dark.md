---
title: Dark
slug: dark
status: published
description: "Night: near-black paper and warm off-white ink, picked in Settings or with ?theme=dark."
chips:
  - Theme
  - Dark
created: 2026-11-09T19:23:22Z
updated: 2026-11-11T15:59:05Z
---

Palette name: **Night**. `data-theme="dark"`, no `data-accent`. It is chosen in Settings › Theme or with `?theme=dark`; first visits get Ember (marathon-dark, amber), whatever the system prefers.

It overrides the [light](light.md) base with:

```css
[data-theme="dark"] {
  color-scheme: dark;
  --paper: #0b0b0c;
  --ink: #ece8e1;
  --dot: #2b2a28;
  --glow: #FFC81A;
  --ok: #3ecf7e;
  --accent: var(--ink);
  --shade: #000;
  --shadow: #000;
  --shadow-k: 2.4;
  --warm: #ffb81a;
  --warm-halo: #ffc400;
  --op-meta: 0.6;
  --op-faint: 0.5;
  --grain-k: 1.5;
  --blend-ink: screen;
}
```

- theme-color meta: `#0b0b0c`.
- The accent stays the ink. The success check is a brighter green, `#3ecf7e`.
- Grain is 1.5× and UI shadows 2.4× (`--shadow-k`), so both still read on dark paper.
- `--op-meta` .6 and `--op-faint` .5 (light uses .56 and .39) keep the quiet type legible.
- `--blend-ink: screen`.

See [Themes](../themes.md).
