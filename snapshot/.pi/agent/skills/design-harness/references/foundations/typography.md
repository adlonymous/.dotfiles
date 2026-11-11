---
title: Typography
slug: typography
status: published
group: Foundations
order: 4
discuss: 0
created: 2026-11-09T19:23:22Z
updated: 2026-11-09T19:23:22Z
---

The typography system uses three typefaces: Inter Display (UI), Shinka (body/serif), and a system monospace stack (code). Type is rendered with texture filters (`#ink-ui`, `#ink-body`, `#ink-bio`) that apply subtle ink displacement, blur, and grain for a tactile, printed quality.

## Typefaces

### Inter Display (UI)
Primary UI typeface for navigation, headings, labels, and interface elements.

**Font stack:**
```css
--ui: "Inter Display", "Helvetica Neue", Arial, sans-serif
```

**Weights:**
- Regular 400
- Medium 500 (for emphasis)

**Font files:**
- `InterDisplay-Regular.woff2` (400 normal)
- `InterDisplay-Italic.woff2` (400 italic)
- `InterDisplay-Medium.woff2` (500 normal)

**Metric overrides:**
```css
size-adjust: 100.06%;
ascent-override: 90%;
descent-override: 22%;
line-gap-override: 0%;
```

### Shinka (Body / Serif)
Body text typeface for articles and long-form content.

**⚠️ COMMERCIAL LICENSE REQUIRED**

Shinka is a commercially licensed typeface used by Saleh Digital. It is NOT included in this harness. Anyone using this harness must either:
- Purchase their own license from the foundry (Aeiou Tools: https://aeiou.tools/purchase/shinka)
- Use the fallback font stack: `Georgia, serif`

Do not copy, redistribute, or bundle Shinka font files. The owner supplies them separately.

**Font stack:**
```css
--serif: "Shinka", Georgia, serif
```

**Weights:**
- Regular 400
- Italic 400

**Metric overrides:**
```css
size-adjust: 100%;
ascent-override: 91%;
descent-override: 25%;
line-gap-override: 0%;
```

### Monospace (code)
Code, technical values and tabular data. Since 2026-11-11 the `--mono` stack is system monospace only; ABC Favorit Mono Trial is still named directly by the gallery grids' canvas fonts.

**Font stack:**
```css
--mono: "SF Mono", ui-monospace, Menlo, monospace
```

**Weight:** 400 regular only

### Kufigraph (Arabic)
Used for the basmala (بسم الله الرحمن الرحيم) in the footer.

**Weights:**
- Light 300
- Regular 400

### Kult Luxury (Wordmark)
Display typeface for the `salehdigital` wordmark SVG in the footer.

**⚠️ COMMERCIAL LICENSE REQUIRED**

Kult Luxury is a commercially licensed typeface used by Saleh Digital. It is NOT included in this harness. Anyone using this harness must either:
- Purchase their own license from the Kult Luxury foundry
- Use an alternative display font for the wordmark

Do not copy, redistribute, or bundle Kult Luxury font files. The owner supplies them separately.

## Type Scale

### UI (Inter Display)

**Navigation items:**
```css
font: 400 16px/20px var(--ui);
letter-spacing: -0.64px; /* var(--track) */
```

**Headings (h2):**
```css
font: 400 28px/32px var(--ui);
letter-spacing: -1.1px;
```

**Mobile h2:**
```css
font: 400 24px/28px var(--ui);
letter-spacing: -0.9px;
```

**Headings (h3):**
```css
font: 400 20px/24px var(--ui);
letter-spacing: -0.6px;
```

**Body UI:**
```css
font: 400 16px/16px var(--ui);
letter-spacing: var(--track); /* -0.64px */
```

**Small UI / Labels:**
```css
font: 400 14px/20px var(--ui);
letter-spacing: -0.2px;
```

**Tiny UI:**
```css
font: 400 12px/16px var(--ui);
letter-spacing: -0.2px;
```

**Mono / Code:**
```css
font: 400 13px/18px ui-monospace, "SF Mono", Menlo, monospace;
letter-spacing: 0;
```

### Body (Shinka)

**Article body:**
```css
font: 400 16px/20.8px var(--serif);
letter-spacing: var(--track); /* -0.64px */
```

**Paragraph spacing:**
```css
--para: calc(16px + (0.3 - var(--fnd-density)) * 14px);
gap: var(--para); /* default 24px at density 0.3 */
```

## Letter Spacing

**Global tracking:**
```css
--track: -0.64px;
```

Applied to most text. Headings and specific components override with tighter tracking (-0.9px to -1.1px).

**Monospace:** `letter-spacing: 0`

## Ink Filters

All type is rendered through SVG filters that add texture, displacement, and grain:

**UI text** (`#ink-ui`):
- Turbulence: baseFrequency 0.85, numOctaves 2, seed 7
- Displacement: scale 0.7
- Blur: stdDeviation 0.22
- Alpha boost: slope 1.34

**Body text** (`#ink-body`):
- Turbulence: baseFrequency 1.1, numOctaves 1, seed 3
- Displacement: scale 0.24
- Blur: stdDeviation 0.1
- Alpha boost: slope 1.12

**Bio / Basmala** (`#ink-bio`):
- Turbulence: baseFrequency 1.4, numOctaves 2, seed 7
- Displacement: scale 1.8
- Blur: stdDeviation 0.3
- Alpha boost: slope 1.8
- Grain dropouts: baseFrequency 2.4, matrix -1.4 to 1.6

## Font Rendering

```css
-webkit-font-smoothing: antialiased;
-moz-osx-font-smoothing: grayscale;
text-rendering: geometricprecision;
font-kerning: normal;
```

## Text Selection

```css
::selection {
  background: var(--select-bg); /* var(--ink) in light, var(--accent) in marathon */
  color: var(--select-fg);      /* var(--paper) in light, var(--on-accent) in marathon */
}
```

## Strong / Emphasis

**Bold (strong):**
```css
-webkit-text-stroke: 0.5px currentColor;
font-weight: 400; /* no weight change, only stroke */
```

**Italic (em):**
```css
font-style: italic;
```

## Usage

- **Navigation, UI, buttons:** Inter Display 16px
- **Article body:** Shinka 16px/20.8px
- **Headings:** Inter Display 20px–28px, tight tracking
- **Code, values:** `--mono` (system monospace) 13px, zero tracking
- **Arabic text:** Kufigraph (basmala only)

