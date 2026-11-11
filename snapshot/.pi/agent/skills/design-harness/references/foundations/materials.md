---
title: Materials
slug: materials
status: published
group: Foundations
order: 8
discuss: 0
created: 2026-11-09T19:23:22Z
updated: 2026-11-09T19:23:22Z
---

The material system applies texture, grain, and ink filters to create a tactile, printed aesthetic.

## Texture (Ink Filters)

All text and UI elements are filtered through SVG filters that simulate ink on paper:

### ink-ui (Navigation, headings, UI)
```html
<filter id="ink-ui" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="7" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="0.7" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feGaussianBlur in="d" stdDeviation="0.22" result="b"/>
  <feComponentTransfer in="b"><feFuncA type="linear" slope="1.34" intercept="0"/></feComponentTransfer>
</filter>
```

- Light displacement (0.7)
- Minimal blur (0.22)
- Alpha boost (1.34)

### ink-body (Body text)
```html
<filter id="ink-body" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="1" seed="3" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="0.24" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feGaussianBlur in="d" stdDeviation="0.1" result="b"/>
  <feComponentTransfer in="b"><feFuncA type="linear" slope="1.12" intercept="0"/></feComponentTransfer>
</filter>
```

- Faintest displacement (0.24)
- Minimal blur (0.1)
- Light alpha boost (1.12)

### ink-bio (Bio, basmala, marks)
```html
<filter id="ink-bio" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="7" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="1.8" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feGaussianBlur in="d" stdDeviation="0.3" result="b"/>
  <feComponentTransfer in="b" result="i"><feFuncA type="linear" slope="1.8" intercept="0"/></feComponentTransfer>
  <feTurbulence type="fractalNoise" baseFrequency="2.4" numOctaves="1" seed="11" result="g"/>
  <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.4 0 0 0 1.6" result="gm"/>
  <feComposite in="i" in2="gm" operator="in"/>
</filter>
```

- Strong displacement (1.8)
- More blur (0.3)
- Alpha boost (1.8)
- Grain alpha dropouts via color matrix

### ink-diagram (Diagrams, flows)
```html
<filter id="ink-diagram" color-interpolation-filters="sRGB">
  <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="7" result="n"/>
  <feDisplacementMap in="SourceGraphic" in2="n" scale="1.2" xChannelSelector="R" yChannelSelector="G" result="d"/>
  <feGaussianBlur in="d" stdDeviation="0.25" result="b"/>
  <feComponentTransfer in="b" result="i"><feFuncA type="linear" slope="1.6" intercept="0"/></feComponentTransfer>
  <feTurbulence type="fractalNoise" baseFrequency="2.4" numOctaves="1" seed="11" result="g"/>
  <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.1 0 0 0 1.5" result="gm"/>
  <feComposite in="i" in2="gm" operator="in"/>
</filter>
```

- Gentler than bio for 1px rules and 14px labels

## Grain

A tiled grain texture overlays the entire page:

```css
#grain {
  z-index: 11;
  pointer-events: none;
  image-rendering: pixelated;
  opacity: calc((0.01 + 0.05 * var(--fnd-texture)) * var(--grain-k) / 0.45);
  background-repeat: repeat;
  position: fixed;
  top: 0;
  left: 0;
}
```

**Opacity formula:**
```
opacity = (0.01 + 0.05 * fnd-texture) * grain-k / 0.45
```

Where:
- `--fnd-texture`: 0.4 default (foundation slider 0–1)
- `--grain-k`: 1 (light), 1.5 (dark), 1.4 (marathon-dark), 1.1 (marathon-light)

Result: More visible in dark themes.

## Foundation Variables

The material intensity is controlled by foundation variables:

```css
--fnd-texture: 0.4;  /* ink displacement & grain intensity */
--fnd-focus: 0.6;    /* blur amount */
```

These map to user-adjustable sliders in Settings.

## Glass / Blur

Cards and modals use backdrop blur:

```css
background: color-mix(in srgb, var(--paper) 68%, transparent);
backdrop-filter: blur(20px) saturate(1.3);
```

**Blur tokens:**
```css
--blur-rest: calc(4px * (0.4 + var(--fnd-focus)));
--blur-peek: calc(var(--blur-rest) * 0.375);
```

## Shadows

Layered shadows with `--shadow-k` multiplier:

```css
box-shadow: 
  0 0 0 1px color-mix(in srgb, var(--ink) 10%, transparent),
  0 2px 6px color-mix(in srgb, var(--shadow) calc(6% * var(--shadow-k)), transparent),
  0 24px 64px -12px color-mix(in srgb, var(--shadow) calc(22% * var(--shadow-k)), transparent);
```

- Light: `shadow-k: 1`
- Dark: `shadow-k: 2.4` (stronger)
- Marathon Light: `shadow-k: 1.2`

## Border Radius

Consistent rounding:
- Cards/modals: `14px–16px`
- Buttons: `6px–10px`
- Chips: `6px`
- Images/covers: `1px–2px` (minimal, to preserve texture)

## Usage

- Apply `filter: url(#ink-ui)` to all UI text
- Apply `filter: url(#ink-body)` to article body
- Apply `filter: url(#ink-bio)` to footer bio, basmala, marks
- Grain is global, always present
- Use backdrop-filter for glass surfaces (modals, sheets)
- Scale shadows with `--shadow-k` per theme
