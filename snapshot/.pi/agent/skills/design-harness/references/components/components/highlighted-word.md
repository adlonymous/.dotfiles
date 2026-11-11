---
title: Accent wash
slug: highlighted-word
status: published
description: "On light Marathon paper the accent is a highlighter behind the ink: a band from 12% to 92% of the line, 3px past each side."
chips:
  - Component
  - Marathon
  - Highlight
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:07:17Z
---

On marathon-light, the accent (lime, cyan and so on) can never be type, because it fails contrast on pale paper. Wherever the accent marks "this one", it is a **highlighter band behind the ink** instead:

```css
background: linear-gradient(transparent 12%, var(--accent-wash) 12%, var(--accent-wash) 92%, transparent 92%);
box-shadow: -3px 0 0 var(--accent-wash), 3px 0 0 var(--accent-wash);
```

It is used on `.col-nav .item.is-active`, `.nav-sheet-list .item.is-active`, and the Settings miniature's active nav item (`.mini[data-theme="marathon-light"] .m-nav .m-i.on .t`). Selection on marathon-light is `--select-bg: var(--accent-wash)` with ink text.

`--accent-wash` per accent on marathon-light: lime `#c2fe0b`, cyan `#01ffff`, red `#f88088`, amber `#ffd47a`, green `#96cd74`. In marathon-dark the active item is simply `color: var(--accent-text)`.
