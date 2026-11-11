---
title: Marathon light
slug: marathon-light
status: published
description: "The acid graphic look on cool light paper: the accent sits behind the ink as a highlighter, never as type."
chips:
  - Theme
  - Marathon
created: 2026-11-09T19:23:22Z
updated: 2026-11-11T15:59:05Z
---

Palettes: **Sulphur** (lime), **Glacier** (cyan), **Flare** (red), **Honey** (amber), **Moss** (green). `data-theme="marathon-light"` and `data-accent` set to one of the five (default lime).

The paper is `#f1f3f7` and the ink a navy, `#29324f`. On light paper lime cannot be type, so `--accent-text` is the ink and the accent shows only as a wash behind the ink (`--accent-wash`), for example on the active nav item. Small marks (focus rings, the footer) use `--accent-mark`, a deepened accent with 3:1 contrast.

```css
[data-theme="marathon-light"] {
  color-scheme: light;
  --foot: var(--accent-mark);     /* the accent, deepened so it reads on light paper */
  --paper: #f1f3f7;
  --ink: #29324f;
  --dot: #d5dae4;
  --accent: #c2fe0b;
  --accent-text: var(--ink);       /* lime is never type on light paper: it sits behind it */
  --accent-mark: #587c00;
  --accent-wash: var(--accent);
  --on-accent: var(--ink);
  --signal: #ff0d1a;
  --glow: var(--accent);
  --ok: #38801a;
  --ring: var(--accent-mark);
  --tint: var(--ink);
  --swell: var(--signal);
  --shade: #c3c9d6;
  --shadow: #29324f;
  --shadow-k: 1.2;
  --warm: #8fbf00;
  --warm-halo: var(--accent);
  --select-bg: var(--accent-wash);
  --select-fg: var(--ink);
  --op-meta: 0.78;
  --op-faint: 0.72;
  --grain-k: 1.1;
}
[data-theme="marathon-light"][data-accent="cyan"] { --accent: #01ffff; --accent-mark: #007f88; --warm: #00b3bf; }
[data-theme="marathon-light"][data-accent="red"] { --accent: #ff0d1a; --accent-wash: #f88088; --accent-mark: #e00012; --signal: #fd6c1d; --warm: #ff0d1a; }
[data-theme="marathon-light"][data-accent="amber"] { --accent: #ffb000; --accent-wash: #ffd47a; --accent-mark: #9a6200; --warm: #e09a00; }
[data-theme="marathon-light"][data-accent="green"] { --accent: #59b41d; --accent-wash: #96cd74; --accent-mark: #38801a; --warm: #59b41d; }
```

The active nav item and the nav sheet's active item:

```css
[data-theme=marathon-light] .col-nav .item.is-active { background: linear-gradient(transparent 12%, var(--accent-wash) 12%, var(--accent-wash) 92%, transparent 92%); box-shadow: -3px 0 0 var(--accent-wash), 3px 0 0 var(--accent-wash); }
```

- theme-color meta: `#f1f3f7`.

See [marathon-accents](marathon-accents.md).
