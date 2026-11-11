---
title: Brand
slug: brand
status: published
group: Foundations
order: 1
discuss: 0
created: 2026-11-09T19:23:22Z
updated: 2026-11-09T19:23:22Z
---

The brand identity is minimal and typographic. No logo beyond the wordmark.

## Name

**Ahmed Saleh** / **أحمد صالح**

Site domain: **saleh.digital**

## Wordmark

The `salehdigital` wordmark appears in the footer as an SVG text element styled with the Kult Luxury display font.

**Markup:**
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

- Height: 97px (100px viewBox with padding)
- Font size: 120px
- No letter spacing
- Inherits footer color (`--foot`)
- Ink texture filter applied

## Basmala

The Islamic invocation "بسم الله الرحمن الرحيم" (Bismillah) appears in the footer center.

**Styling:**
```css
.basmala {
  font: 300 18px/19.2px "Kufigraph", var(--ui);
  letter-spacing: 0;
  filter: url(#ink-bas);
}
```

- Kufigraph Light 300
- 18px / 19.2px line height
- Right-to-left Arabic text
- Ink bio filter (heavy texture)

## Bio

"Ahmed Saleh أحمد صالح is a designer-founder in pursuit of the infinite."

**Styling:**
```css
.bio {
  filter: url(#ink-bio);
  padding: 0 0 0 12px;
  line-height: 19.2px;
}
```

- 16px UI font
- Heavy ink texture
- Arabic name inline with English

## Brand Marks

Four symbolic marks appear in the footer (to the right). Exact meaning not documented, but they appear as mask-based icons with ink filter.

**Structure:**
```html
<ul class="marks">
  <li><span class="mark" style="--w:20px; --src:url(...)"></span></li>
  <!-- 3 more marks -->
</ul>
```

**Styling:**
```css
.mark {
  height: 20px;
  width: var(--w);
  mask: var(--src) center / contain no-repeat;
  filter: var(--ink, url(#ink-mark)) blur(calc(var(--soft, 0px) + 0.55px));
  background: currentColor;
}
```

- Height: 20px
- Variable width
- Inherit footer color
- Blur + ink texture
- Peek state reduces blur

## Colors

No specific brand color. Themes define `--foot`:
- Light/Dark: `var(--ink)`
- Marathon Dark: `var(--accent)` (neon)
- Marathon Light: `var(--accent-mark)` (darker accent)

## Voice

Concise, technical, first-person. See `foundations/writing` for detailed voice guidelines.

## Usage

- No logo image files
- Wordmark SVG always in footer, never elsewhere
- Basmala always centered in footer
- Bio precedes footer, left-aligned
- Marks to the right of basmala, footer color
