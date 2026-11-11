---
title: Warm word
slug: glow
status: published
description: "Warm words: a secret written {{word|secret}} glows faintly in --warm; a 700ms hover resolves it heavier; a click opens its hidden piece."
chips:
  - Component
  - Secret
  - Text
order: 5
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:07:17Z
---

A **warm word** is text written `{{word|secret}}` in the CMS. It renders as `<span class="warm" role="button" tabindex="0" data-secret>` and rests faintly warm: a .6px text-shadow in `--warm` at 55% plus a 5px halo in `--warm-halo` at 14%, with no underline. After a 700ms hover, or on focus, it is lit (`.is-lit`, a hover morph): a .42px stroke, with the halo at 70% / 7px / 26%. Clicking it, or Enter/Space, opens the hidden piece. See [hidden extras](../../foundations/motion/hidden-extras.md).

`--warm` / `--warm-halo` per theme: light `#d69600` / `#ffc400`; dark `#ffb81a` / `#ffc400`; Marathon dark: the accent; Marathon light: `#8fbf00` (lime), `#00b3bf` (cyan), `#ff0d1a` (red), `#e09a00` (amber) or `#59b41d` (green), with the accent as the halo.

Source: `site/css/site.css`, lines 121 to 126

```css
/* warm words: faintly warm, no underline; a long hover resolves them heavier */
.warm { cursor: pointer; outline: none; border-radius: 2px;
  text-shadow: 0 0 .6px color-mix(in srgb, var(--warm) 55%, transparent), 0 0 5px color-mix(in srgb, var(--warm-halo) 14%, transparent); }
.warm.is-lit { -webkit-text-stroke: .42px currentColor; text-shadow: 0 0 .6px color-mix(in srgb, var(--warm) 70%, transparent), 0 0 7px color-mix(in srgb, var(--warm-halo) 26%, transparent); }
.warm:focus-visible { -webkit-text-stroke: .42px currentColor; box-shadow: 0 1px 0 color-mix(in srgb, var(--warm) 80%, var(--ink)); }
.clock span { opacity: var(--op-meta); }
```
