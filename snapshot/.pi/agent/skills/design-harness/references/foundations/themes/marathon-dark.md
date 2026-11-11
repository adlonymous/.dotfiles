---
title: Marathon dark
slug: marathon-dark
status: published
description: "The acid graphic look on dark paper: one accent for the footer, highlights and glow. Ember (amber) is the site default for every first visit."
chips:
  - Theme
  - Marathon
created: 2026-11-09T19:23:22Z
updated: 2026-11-11T15:59:05Z
---

Palettes: **Acid** (lime), **Static** (cyan), **Siren** (red), **Ember** (amber), **Reactor** (green). `data-theme="marathon-dark"` and `data-accent` set to one of `lime cyan red amber green` (default lime).

The paper and ink are the dark theme's own (`#0b0b0c` / `#ece8e1`, "no navy"). The accent drives the footer (wordmark, marks and bio: `--foot: var(--accent)`), selection, focus rings, the orbs (`--glow`), warm words and the success check. `--signal` (cyan, or lime when the accent is cyan) is the second colour: it tints the Library dots and Experiments glyphs (`--tint`) and the wordmark's thinking swell (`--swell`).

```css
[data-theme="marathon-dark"] {
  color-scheme: dark;
  --paper: #0b0b0c;               /* the dark theme's paper, no navy */
  --ink: #ece8e1;
  --dot: #2b2a28;
  --foot: var(--accent);          /* footer wordmark, marks and bio in the accent */
  --accent: #c2fe0b;
  --accent-text: var(--accent);
  --accent-mark: var(--accent);
  --accent-wash: var(--accent);
  --on-accent: #0b0b0c;
  --signal: #01ffff;
  --glow: var(--accent);
  --ok: var(--accent);
  --ring: var(--accent-mark);
  --tint: var(--signal);
  --swell: var(--signal);
  --shade: #000;
  --shadow: #000;
  --shadow-k: 2.4;
  --warm: var(--accent);
  --warm-halo: var(--accent);
  --select-bg: var(--accent);
  --select-fg: var(--on-accent);
  --op-meta: 0.64;
  --op-faint: 0.52;
  --grain-k: 1.4;
  --blend-ink: screen;
}
[data-theme="marathon-dark"][data-accent="cyan"] { --accent: #01ffff; --signal: #c2fe0b; }
[data-theme="marathon-dark"][data-accent="red"] { --accent: #ff0d1a; --accent-text: #ff4d55; --accent-mark: #ff4d55; --ok: #59b41d; --on-accent: #fff; }
[data-theme="marathon-dark"][data-accent="amber"] { --accent: #ffb000; }
[data-theme="marathon-dark"][data-accent="green"] { --accent: #59b41d; }
```

- The inline first-paint script writes theme-color `#1c2338`, then `js/theme.js` replaces it with the computed paper `#0b0b0c`.
- In Marathon the orb's light itself is the accent instead of gold (`accentLook` in `js/orb.js`).

See [marathon-accents](marathon-accents.md) and [Themes](../themes.md).
