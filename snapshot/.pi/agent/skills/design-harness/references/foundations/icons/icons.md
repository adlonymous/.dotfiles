---
title: Icons
slug: icons
status: published
description: Icon set and usage.
chips:
  - Foundation
  - Icons
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Icon system using Amicons commercial icon set. Icons are applied via CSS mask for theme-aware coloring.

## Icon Set

**Amicons** (commercial license required)
Vendor: https://amicons.amie.so/
License: Commercial -- others must purchase their own license. See `intelligence/packages/amicons.md` and repo README.

## Implementation

CSS mask-based rendering:
```css
.ico {
  width: 16px;
  height: 16px;
  mask: var(--src) center / contain no-repeat;
  background: currentColor;
}

[data-icon="copy"] {
  --src: url(/icons/copy.svg); /* owner-supplied */
}
```

## Icon Sizing

- UI icons: 16×16px
- Touch targets: Wrap in 24×24px minimum clickable area
- Scale with `em` for inline text icons

## Color

Icons inherit `currentColor`, so they adapt to theme and context automatically.

## Usage

Icon-only buttons must include `aria-label`:
```html
<button class="meta-ico" aria-label="Copy link">
  <span class="ico" data-icon="copy"></span>
</button>
```

## Fallback

If Amicons unavailable, use Unicode symbols or simple SVG shapes:
```css
.ico[data-icon="copy"]::before {
  content: '⎘'; /* fallback character */
}
```

## Related

See `components/components/icon-button.md` and `intelligence/packages/amicons.md`.
