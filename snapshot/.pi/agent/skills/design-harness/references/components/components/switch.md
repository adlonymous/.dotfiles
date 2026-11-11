---
title: Quiet switch
slug: switch
status: published
description: "The quiet switch: a label and three 5px dots that fill with the accent mark when on, one after another."
chips:
  - Component
  - Switch
  - Settings
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:07:17Z
---

There is no toggle track or knob on saleh.digital. A switch is a **label and three dots**: a `<button role="switch" aria-checked>` in the nav's type (Inter Display 16/20). Off, the label sits at `--op-meta` and the dots are `--dot`, with the third dot `--muted`. On, the label goes to 1 and the dots fill with `--accent-mark`, 0, 50 and 100ms apart over 180ms. A press nudges it down .5px. Focus-visible underlines the label.

Settings no longer shows a switch (the Sound switch was removed on Nov 9: picking a sound palette turns sound on, and Off is the off). The component is still in the code (`quiet()` in `js/settings.js`) and the CSS.

```html
<button type="button" class="qs" role="switch" aria-checked="false">
  <span class="qs-label">Sound</span>
  <span class="qs-dots" aria-hidden="true"><i></i><i></i><i></i></span>
</button>
```

Source: `site/css/site.css`, lines 777 to 791

```css
/* the quiet switch: a label and three dots that fill */
.spec-switches { display: flex; flex-wrap: wrap; column-gap: 28px; row-gap: 10px; }
.qs { display: inline-flex; align-items: center; gap: 10px; min-height: 24px; outline: none; filter: url(#ink-ui); -webkit-tap-highlight-color: transparent; transition: opacity 160ms var(--ease-land); }
.qs-label { opacity: var(--op-meta); transition: opacity 160ms var(--ease-land); }
.qs:hover .qs-label, .qs[aria-checked="true"] .qs-label { opacity: 1; }
.qs:focus-visible .qs-label { opacity: 1; text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; }
.qs-dots { display: inline-flex; gap: 3px; }
.qs-dots i { width: 5px; height: 5px; border-radius: 50%; background: var(--dot); transition: background-color 180ms var(--ease-land); }
.qs[aria-checked="true"] .qs-dots i { background: var(--accent-mark); }
.qs[aria-checked="true"] .qs-dots i:nth-child(2) { transition-delay: 50ms; }
.qs[aria-checked="true"] .qs-dots i:nth-child(3) { transition-delay: 100ms; }
.qs[aria-checked="false"] .qs-dots i:nth-child(3) { background: var(--muted); }
.qs:active { transform: translateY(0.5px); }
.qs.is-muted, .spec-grid.is-muted .spec { opacity: var(--op-faint); }
```


Source: `site/js/settings.js`, lines 101 to 108

```js
// the quiet switch: a label and three dots that fill
function quiet(label, onFlip) {
  const s = h('button', { type: 'button', class: 'qs', role: 'switch', 'aria-checked': 'false' },
    h('span', { class: 'qs-label' }, label), h('span', { class: 'qs-dots', 'aria-hidden': 'true' }, h('i'), h('i'), h('i')));
  s.addEventListener('click', onFlip);
  s.set = (v) => s.setAttribute('aria-checked', String(v));
  return s;
}
```
