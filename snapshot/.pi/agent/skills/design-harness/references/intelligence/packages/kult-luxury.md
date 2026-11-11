---
title: Kult Luxury
slug: kult-luxury
status: published
order: 8
description: The salehdigital wordmark.
chips:
  - Display
created: 2026-11-09T22:43:47Z
updated: 2026-11-09T22:43:47Z
---

**⚠️ COMMERCIAL LICENSE REQUIRED — NOT INCLUDED IN THIS HARNESS**

Kult Luxury is a commercial display typeface used for the `salehdigital` wordmark in the footer.

## License

**You must purchase your own license** to use Kult Luxury. It is NOT included in this harness or repository.

**Source:** buy a license from the Kult Luxury foundry; the owner licenses it separately

## Fallback

If you don't have a Kult Luxury license, use an alternative display font:

```css
font-family: "Arial Black", Impact, sans-serif;
```

Or create the wordmark as text/SVG with any bold display font.

## Usage

**Wordmark SVG:**
```html
<svg class="wordmark" role="img" aria-label="salehdigital" width="1920" height="100">
  <text x="6" y="90" font-size="120">salehdigital</text>
</svg>
```

**Styling:**
```css
.wordmark text {
  letter-spacing: 0;
  fill: var(--foot);
  filter: url(#ink-ui);
  font-family: "Kult Luxury";
}
```

- Font size: 120px in 100px viewBox
- No letter spacing
- Inherits footer color
- Ink texture filter applied

## Do NOT Bundle

- No `.woff`, `.woff2`, `.otf`, or `.ttf` files
- No base64 font data
- Owner supplies font files separately

