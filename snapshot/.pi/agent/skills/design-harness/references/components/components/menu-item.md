---
title: Menu item
slug: menu-item
status: published
description: ".item: nav and sub-nav labels. Inactive items recede (opacity .39 + ink filter), hover peeks to .695 through a field morph, the active one is sharp."
chips:
  - Component
  - Navigation
order: 7
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:07:17Z
---

Nav and sub-nav labels are `a.item` in Inter Display 16/16, tracking -0.64px, `white-space: nowrap` (the sub-nav wraps with `text-wrap: balance` when longer than the column). States:

| State | Opacity | Notes |
|---|---|---|
| rest | `--op-rest` (.3904) | `filter: url(#ink-ui)` |
| peek (hover / focus-visible) | `--op-peek` (.6952) | a hover morph, 300ms ([resolve](../../foundations/motion/resolve.md)) |
| active | 1 | nav: `color: var(--accent-text)`; marathon-light: the accent wash behind it |
| focus-visible | 1 | underline 1px, offset 3px |
| has-orb | | `padding-right: 13px` for the orb ([orbs](../../foundations/motion/orbs.md)) |

Group labels in the sub-nav (`.sub-group`) are not links: `--op-meta`, the same ink filter, and a paragraph step of air before each group but the first.

Source: `site/css/site.css`, lines 55 to 78

```css
/* ---------- items: active sharp, the rest recede ---------- */
.item {
  display: inline-block;
  white-space: nowrap;
  opacity: var(--op-rest);
  filter: url(#ink-ui);
  outline: none;
}
.item.is-peek { opacity: var(--op-peek); filter: url(#ink-ui); }
.item.is-active { opacity: 1; filter: url(#ink-ui); }
.col-nav .item.is-active { color: var(--accent-text); }
/* on light Marathon paper the accent is a highlighter behind the ink, never the type */
[data-theme="marathon-light"] .col-nav .item.is-active { background: linear-gradient(transparent 12%, var(--accent-wash) 12%, var(--accent-wash) 92%, transparent 92%); box-shadow: -3px 0 0 var(--accent-wash), 3px 0 0 var(--accent-wash); }
/* room for the yellow orb after a label (6px gap + 7px orb) */
.item.has-orb { padding-right: 13px; }
.item:focus-visible { opacity: 1; filter: url(#ink-ui); text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; }
/* a group's label in the sub-nav (Harness: Foundations, Intelligence, Interface):
   the nav's type, sharp but muted, not a link; a step of air before each group but the first */
.sub-group { opacity: var(--op-meta); filter: url(#ink-ui); white-space: nowrap; cursor: default; user-select: none; -webkit-user-select: none; }
.col-nav .nav-step { margin-top: calc(var(--para) - var(--stack)); }
.sub-group:not(:first-child) { margin-top: calc(var(--para) - var(--stack)); }
/* a room's section that is a single grid page (Sketches, Books, The shelf): one item, with a group's air before it */
.sub-one:not(:first-child) { margin-top: calc(var(--para) - var(--stack)); }
```
