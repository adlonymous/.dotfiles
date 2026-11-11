---
title: Icon button
slug: icon-button
status: published
description: "The col 4 actions: 16px mask icons at --op-meta, hot at 1, morphing line to solid through a halftone; Copy shows a single green check."
chips:
  - Component
  - Icon
  - Button
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:07:17Z
---

`.meta-ico`: a 16px icon (`.ico`, a CSS mask of the icon file, `background: currentColor`) at `--op-meta`, with an optional count at `--op-faint`. Hot (hover or focus) is opacity 1. Pressed is the solid variant. Every change morphs through the WebGL field as a halftone ([resolve](../../foundations/motion/resolve.md) › Press and icon toggles). Success is `.is-ok`, a single check in `--ok`. The focus ring is 1px `--ring`, offset 2px.

The icons are Amicons (commercial): see [amicons](../../intelligence/packages/amicons.md). The files are not in this harness; leave `<span class="ico">` slots.

On the live site the actions row (Discuss, Copy link, Copy text, Sound) is rendered but `hidden`. With every action switched off, the row takes no room.

Source: `site/css/site.css`, lines 128 to 153

```css
/* ---------- meta ---------- */
.col-meta { display: flex; flex-direction: column; align-items: flex-start; gap: var(--stack); filter: url(#ink-ui); }
.openin { display: flex; align-items: center; gap: 9px; height: 16px; }
.dots { display: flex; gap: 6px; }
.dot {
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--dot);
  transition: background-color 160ms var(--ease-land), transform 160ms var(--ease-land);
}
.dot:hover, .dot:focus-visible { background: var(--muted); outline: none; }
[data-theme^="marathon"] .dot:hover, [data-theme^="marathon"] .dot:focus-visible { background: var(--accent-mark); }
.dot:active { transform: scale(0.84); }
/* col 4 icons: 16px, stacked on the 20px row pitch, optically on the cap height */
.meta-ico { display: inline-flex; align-items: center; gap: 4px; height: 16px; padding: 0; margin: 0; border: 0; background: none; color: inherit; cursor: pointer; border-radius: 4px; }
.meta-ico .ico { display: block; width: 16px; height: 16px; background: currentColor; opacity: var(--op-meta);
  -webkit-mask: var(--src) center / 16px 16px no-repeat; mask: var(--src) center / 16px 16px no-repeat;
  translate: 0 -0.5px; }
.meta-ico .ico.is-hot { opacity: 1; }
.meta-ico .count { opacity: var(--op-faint); line-height: 16px; }
.meta-ico:focus-visible { outline: 1px solid var(--ring); outline-offset: 2px; }
.meta-link { display: inline-block; line-height: 16px; height: 16px; white-space: nowrap; }
.meta-link .count { opacity: var(--op-faint); }
.meta-link .faint { opacity: var(--op-meta); }
.meta-link:hover .faint, .meta-link:hover .count { opacity: 1; }
.meta-link:focus-visible { outline: none; text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; }
.meta-link:active { transform: translateY(0.5px); }
```


Source: `site/css/site.css`, lines 741 to 742

```css
/* success state for icon actions: a single check in green */
.meta-ico .ico.is-ok { background: var(--ok); opacity: 1; }
```
