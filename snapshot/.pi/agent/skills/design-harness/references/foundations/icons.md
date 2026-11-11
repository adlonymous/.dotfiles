---
title: Icons
slug: icons
status: published
group: Foundations
order: 5
discuss: 0
created: 2026-11-09T19:23:22Z
updated: 2026-11-09T19:23:22Z
---

The site uses the Amicons icon set for UI icons (discuss, copy, sound, etc.).

## ⚠️ COMMERCIAL LICENSE REQUIRED

**Amicons** is a commercially licensed icon set used by Saleh Digital. It is NOT included in this harness. Anyone using this harness must either:
- Purchase their own license from Amicons (https://amicons.design/)
- Use alternative open-source icons (e.g., Heroicons, Lucide, Phosphor)

Do not copy, redistribute, or bundle Amicons SVG files, path data, sprite sheets, or base64 encodings.

## Icon System

Icons are rendered as CSS masks with currentColor:

```css
.meta-ico .ico {
  width: 16px;
  height: 16px;
  opacity: var(--op-meta);
  mask: var(--src) center / 16px 16px no-repeat;
  background: currentColor;
}
```

## Icon Sizes

- **16×16px**: Standard UI icons (meta actions, navigation)
- **20×20px**: Larger touch targets (viewer controls)
- **28×28px**: Modal/dialog icons

## Icons Used

The site uses these icon names (map to your licensed or open-source set):
- `discuss` — Comment/chat bubble
- `copy` — Clipboard/link copy
- `copyText` — Document copy
- `soundOn` — Speaker with sound waves
- Close (×) — Inline SVG, not from icon set

## Implementation

**Set icon via CSS variable:**
```css
[data-icon="discuss"] {
  --src: url('data:image/svg+xml,...'); /* owner-supplied or fallback */
}
```

**Hover state:**
```css
.meta-ico:hover .ico {
  opacity: 1;
}
```

## Fallback Strategy

If you don't have Amicons:
1. Use semantic HTML entities: `×` for close, `↗` for external
2. Use an open-source icon library with similar 16px optical sizing
3. Create simple geometric icons matching the site's minimal style

## Color

Icons inherit `currentColor` and layer with opacity tokens:
- Rest: `var(--op-meta)` (~0.56)
- Hover: `opacity: 1`
- Hot state: `opacity: 1` (permanent)

## Usage

- Always mask-based, never inline SVG (except close ×)
- 16px touch target minimum (wrap in 24px+ for mobile)
- Use semantic labels: `aria-label="Discuss"` on icon buttons
- Icon-only buttons need visible focus rings

