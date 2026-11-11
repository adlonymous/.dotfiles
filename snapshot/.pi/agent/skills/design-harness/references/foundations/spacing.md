---
title: Spacing
slug: spacing
status: published
group: Foundations
order: 6
discuss: 0
created: 2026-11-09T19:23:22Z
updated: 2026-11-09T19:23:22Z
---

The spacing system uses density-responsive tokens that scale with the `--fnd-density` foundation variable (default `0.3`).

## Core Tokens

### Gap (horizontal spacing)
```css
--gap: calc(24px + (0.3 - var(--fnd-density)) * 20px);
```
Default: `24px` at density `0.3`

Used for column gaps in the grid layout.

### Para (vertical rhythm)
```css
--para: calc(16px + (0.3 - var(--fnd-density)) * 14px);
```
Default: `24px` at density `0.3`

Used for vertical spacing between paragraphs and content blocks.

### Stack (tight vertical)
```css
--stack: 4px;
```
Fixed value for tightly stacked items (navigation, lists).

## Grid Layout

Desktop (≥900px):
```css
.cols {
  grid-template-columns: 
    var(--col-nav, 89px)    /* left navigation */
    var(--col-sub, 248px)   /* sub-navigation */
    minmax(0, 640px)        /* body content, max 640px (540 until 2026-11-11) */
    minmax(0, 1fr);         /* media/gallery */
  column-gap: var(--gap);    /* 24px default */
  padding: 24px 24px 48px;
}
```

Mobile (<900px):
```css
.cols {
  flex-direction: column;
  gap: 0;
  padding: 20px 12px 40px;
}
```

## Sectional Spacing

**Between major sections (body):**
```css
gap: var(--para); /* 24px */
```

**Heading to content:**
```css
h2 + * { margin-top: calc(var(--para) * -0.5); } /* 12px */
h3 + * { margin-top: calc(var(--para) * -0.5); }
```

**Consecutive headings:**
```css
h2:not(:first-child) { margin-top: calc(var(--para) * 1.5); } /* 36px */
h3:not(:first-child) { margin-top: calc(var(--para) * 0.75); } /* 18px */
```

**List items:**
```css
ul, ol { gap: calc(var(--para) * 0.375); } /* 9px */
```

## Component Spacing

**Navigation items:**
```css
gap: var(--stack); /* 4px */
```

**Sub-navigation groups:**
```css
.sub-group:not(:first-child) {
  margin-top: calc(var(--para) - var(--stack)); /* 20px */
}
```

**Post meta:**
```css
margin-top: calc(var(--para) * 1.5); /* 36px */
gap: 16px;
```

**Footer bio dots:**
```css
gap: 6px;
```

**Marks:**
```css
gap: 8px;
```

## Padding

**Skip link:**
```css
padding: 6px 8px;
```

**Buttons:**
```css
padding: 0 14px; /* mcp-go */
height: 32px;
```

**Cards (mcp-modal):**
```css
padding: 20px 20px 18px;
```

**Dialog fields:**
```css
padding: 8px 8px 8px 12px;
```

## Insets

**Focus ring offset:**
```css
outline-offset: 2px; /* small elements */
outline-offset: 4px; /* larger cards */
```

**Box shadows (layer depth):**
```css
/* Card elevation */
box-shadow: 
  0 0 0 1px color-mix(...),           /* border */
  0 2px 6px color-mix(...),            /* near shadow */
  0 24px 64px -12px color-mix(...);    /* far shadow */
```

## Responsive Adjustments

Mobile breakpoint (`max-width: 899px`):

- Column padding: `20px 12px 40px` (reduced from `24px 24px 48px`)
- Gaps collapse to `0` in flex column layout
- Individual section spacing reduced by ~20-30%

## Density Responsive

The `--fnd-density` token (default `0.3`, range `0`–`1`) controls:
- `--gap`: More density = tighter columns
- `--para`: More density = tighter vertical rhythm
- Specimen grid gaps
- Settings row heights

## Usage

- Use `--para` for major content spacing (between paragraphs, sections)
- Use `--stack` for tightly grouped items (nav, chips, inline actions)
- Use `--gap` for horizontal layout spacing (grid columns)
- Use fixed `px` for micro-spacing (4px, 6px, 8px, 10px, 12px, 16px)
- Never use margins on standalone elements; prefer gap/flex

