---
title: Amicons
slug: amicons
status: published
order: 9
description: Interface icons.
chips:
  - "2.0"
created: 2026-11-09T22:43:47Z
updated: 2026-11-09T22:43:47Z
---

**⚠️ COMMERCIAL LICENSE REQUIRED — NOT INCLUDED IN THIS HARNESS**

Amicons is a commercial icon set used for UI icons on saleh.digital.

## License

**You must purchase your own license** to use Amicons. It is NOT included in this harness or repository.

**Source:** https://amicons.design/

## Fallback Options

If you don't have an Amicons license, use open-source alternatives:

- [Heroicons](https://heroicons.com/) — Tailwind's icon set
- [Lucide](https://lucide.dev/) — Feather fork
- [Phosphor Icons](https://phosphoricons.com/) — Flexible system
- Simple geometric SVGs matching the minimal style

## Icons Used

The site uses these icon names (16×16px):
- `discuss` — Comment/chat bubble
- `copy` — Clipboard/link
- `copyText` — Document
- `soundOn` — Speaker with waves

## Implementation

Icons are CSS masks with currentColor:

```css
.meta-ico .ico {
  width: 16px;
  height: 16px;
  mask: var(--src) center / 16px 16px no-repeat;
  background: currentColor;
  opacity: var(--op-meta);
}
```

Set via CSS variable:
```css
[data-icon="discuss"] {
  --src: url('...'); /* owner-supplied or fallback */
}
```

## Do NOT Bundle

- No SVG files
- No path data
- No sprite sheets
- No base64 encodings
- Owner supplies icon assets separately

