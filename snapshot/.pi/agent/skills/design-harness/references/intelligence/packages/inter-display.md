---
title: Inter Display
slug: inter-display
status: published
description: Open-source UI typeface by Rasmus Andersson.
chips:
  - Package
  - Typography
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Primary UI typeface for Saleh Digital. Open-source font family designed for screen legibility.

## License

SIL Open Font License 1.1 -- free for personal and commercial use. No purchase required.

## Vendor

**Rasmus Andersson**
Website: https://rsms.me/inter/
GitHub: https://github.com/rsms/inter

## Variants Used

- Inter Display Regular (400)
- Inter Display Medium (500)
- Inter Display Semi-Bold (600)

## Loading

```css
@font-face {
  font-family: 'Inter Display';
  src: url('/fonts/InterDisplay-Regular.woff2') format('woff2');
  font-weight: 400;
  font-style: normal;
  font-display: swap;
}
```

## Usage

- All UI text (nav, buttons, labels, chips)
- Article metadata (date, reading time, type)
- Settings and admin interfaces

See `foundations/typography.md` for full type scale and usage.

## Alternatives

If Inter Display is unavailable, fallback to system-ui:
```css
font-family: 'Inter Display', system-ui, -apple-system, sans-serif;
```

## Related

See `shinka.md` and `kult-luxury.md` for commercial fonts used alongside Inter.
