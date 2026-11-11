---
title: Colors
slug: colors
status: published
group: Foundations
order: 3
discuss: 0
created: 2026-11-09T19:23:22Z
updated: 2026-11-09T19:23:22Z
---

The color system uses semantic tokens that adapt across four themes: Light, Dark, Marathon Dark, and Marathon Light. Colors are defined with hex values and `color-mix()` for opacity variants.

## Semantic Tokens

### Light Theme (default)

**Surface:**
```css
--paper: #ffffff;
--ink: #000000;
--dot: #e0e0e0;
```

**Accent:**
```css
--accent: #000000;
--accent-text: var(--ink);
--accent-mark: var(--ink);
--accent-wash: transparent;
--on-accent: var(--paper);
```

**Feedback:**
```css
--ok: #1e9e57;     /* success green */
--signal: var(--ink);
--ring: var(--ink); /* focus ring */
```

**Warm glow:**
```css
--glow: #ffc81a;
--warm: #d69600;
--warm-halo: #ffc400;
```

**Shadow & structure:**
```css
--shade: #dad8d6;
--shadow: #000000;
--shadow-k: 1;     /* shadow intensity multiplier */
--tint: var(--ink);
--swell: var(--ink);
```

**Selection:**
```css
--select-bg: var(--ink);
--select-fg: var(--paper);
```

**Footer:**
```css
--foot: var(--ink);
```

### Dark Theme

**Surface:**
```css
--paper: #0b0b0c;
--ink: #ece8e1;
--dot: #2b2a28;
```

**Accent:**
```css
--accent: var(--ink);
```

**Feedback:**
```css
--ok: #3ecf7e;
```

**Warm glow:**
```css
--warm: #ffb81a;
--warm-halo: #ffc400;
```

**Shadow:**
```css
--shade: #000000;
--shadow: #000000;
--shadow-k: 2.4; /* stronger shadows in dark */
--grain-k: 1.5;  /* more visible grain */
```

### Marathon Dark

High-contrast dark theme with neon accent system.

**Surface:**
```css
--paper: #0b0b0c;
--ink: #ece8e1;
--dot: #2b2a28;
```

**Accent (lime, default):**
```css
--accent: #c2fe0b;
--accent-text: #c2fe0b;
--accent-mark: #c2fe0b;
--accent-wash: #c2fe0b;
--on-accent: #0b0b0c;
```

**Accent variants:**
- **Cyan:** `--accent: #01ffff; --signal: #c2fe0b`
- **Red:** `--accent: #ff0d1a; --accent-text: #ff4d55; --accent-mark: #ff4d55; --on-accent: #fff`
- **Amber:** `--accent: #ffb000`
- **Green:** `--accent: #59b41d`

**Signal:**
```css
--signal: #01ffff;
--tint: var(--signal);
--swell: var(--signal);
```

**Feedback:**
```css
--ok: var(--accent);
--glow: var(--accent);
--ring: var(--accent-mark);
```

**Footer:**
```css
--foot: var(--accent);
```

**Selection:**
```css
--select-bg: var(--accent);
--select-fg: var(--on-accent);
```

### Marathon Light

High-contrast light theme with neon accent system.

**Surface:**
```css
--paper: #f1f3f7;
--ink: #29324f;
--dot: #d5dae4;
```

**Accent (lime, default):**
```css
--accent: #c2fe0b;
--accent-text: var(--ink);
--accent-mark: #587c00;
--accent-wash: #c2fe0b;
--on-accent: var(--ink);
```

**Accent variants:**
- **Cyan:** `--accent: #01ffff; --accent-mark: #007f88; --warm: #00b3bf`
- **Red:** `--accent: #ff0d1a; --accent-wash: #f88088; --accent-mark: #e00012; --signal: #fd6c1d`
- **Amber:** `--accent: #ffb000; --accent-wash: #ffd47a; --accent-mark: #9a6200; --warm: #e09a00`
- **Green:** `--accent: #59b41d; --accent-wash: #96cd74; --accent-mark: #38801a`

**Signal:**
```css
--signal: #ff0d1a;
--swell: var(--signal);
```

**Feedback:**
```css
--ok: #38801a;
--glow: var(--accent);
--ring: var(--accent-mark);
```

**Shadows:**
```css
--shade: #c3c9d6;
--shadow: #29324f;
--shadow-k: 1.2;
```

**Selection:**
```css
--select-bg: var(--accent-wash);
--select-fg: var(--ink);
```

**Footer:**
```css
--foot: var(--accent-mark);
```

## Opacity Tokens

Contextual opacity for layering and hierarchy:

```css
--op-rest: calc(0.85 - 0.766 * var(--fnd-focus));  /* default ~0.39 at focus 0.6 */
--op-peek: calc((var(--op-rest) + 1) / 2);          /* ~0.70 */
--op-meta: 0.56;   /* light theme, 0.60 dark, 0.64 marathon-dark */
--op-faint: 0.39;  /* light theme, 0.50 dark, 0.52 marathon-dark */
```

**Muted text:**
```css
--muted: color-mix(in srgb, var(--ink) calc(var(--op-meta) * 100%), var(--paper));
```

## Orb Colors

The animated orb gradient (when present):

```css
--orb-core: #ffc81a;
--orb-edge: #fa9608;
--orb-halo: #ffb21a;
```

## Color Mixing

All semi-transparent colors use `color-mix()` in sRGB:

**Example (card background):**
```css
background: color-mix(in srgb, var(--ink) 4%, var(--paper));
```

**Example (shadow):**
```css
box-shadow: 0 24px 64px -12px color-mix(in srgb, var(--shadow) calc(22% * var(--shadow-k)), transparent);
```

## Theme Meta Tags

```html
<meta name="theme-color" content="#ffffff"> <!-- set via JS on load -->
```

Values:
- Light: `#ffffff`
- Dark: `#0b0b0c`
- Marathon Dark: `#1c2338`
- Marathon Light: `#f1f3f7`

## Usage

- **Always use semantic tokens** (`--ink`, `--paper`, `--accent`) not raw hex
- **Layer with opacity tokens** for hierarchy
- **Accent marks active nav** in Light/Dark; accent wash in Marathon Light
- **Warm glow** for hover/focus highlights on emphasized words
- **Signal** for real-time streaming indicators


## Light theme (Paper), verbatim from css/tokens.css

This is the default theme (`<html data-theme="light">`). Copy it as is; several values below (`--op-meta`, `--op-faint`, `--muted`, `--grain-k`) are needed for the menu, captions and grain.

```css
:root, [data-theme] {
  color-scheme: light;
  --paper: #fff; --ink: #000; --dot: #e0e0e0; --glow: #ffc81a; --ok: #1e9e57;
  --accent: #000; --accent-text: var(--ink); --accent-mark: var(--ink); --accent-wash: transparent; --on-accent: var(--paper);
  --ring: var(--ink); --signal: var(--ink); --tint: var(--ink); --swell: var(--ink);
  --shade: #dad8d6; --shadow: #000; --shadow-k: 1; --warm: #d69600; --warm-halo: #ffc400;
  --select-bg: var(--ink); --select-fg: var(--paper);
  --op-meta: .56; --op-faint: .39; --grain-k: 1; --foot: var(--ink);
  --muted: color-mix(in srgb, var(--ink) calc(var(--op-meta) * 100%), var(--paper));
}
::selection { background: var(--select-bg); color: var(--select-fg); }
```

The site's ink is pure black on pure white. What makes it read warm and printed is the ink filters and the grain (foundations/materials/texture.md), not an off-white paper colour.
