---
title: Theme Tokens
slug: theme-tokens
status: published
description: How to apply and document design tokens.
chips:
  - Skill
  - Tokens
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Procedure for using and documenting design tokens (CSS custom properties) on Saleh Digital.

## Steps

**1. Reference Tokens in CSS**:
- Always use token names, never hardcoded values
- Example: `color: var(--ink);` not `color: #1a1a1a;`

**2. Understand Token Categories**:
- **Colors**: `--paper`, `--ink`, `--accent`, `--dot`, `--shadow`, etc.
- **Spacing**: `--gap`, `--para`, `--stack`
- **Motion**: `--motion-resolve`, `--motion-stagger`, `--ease-land`, `--ease-think`
- **Opacity**: `--op-rest`, `--op-peek`, `--op-meta`, `--op-faint`
- **Foundation Sliders**: `--fnd-energy`, `--fnd-texture`, `--fnd-focus`, `--fnd-density`, etc.

**3. Apply Tokens Correctly**:
```css
.button {
  background: var(--accent);
  color: var(--paper);
  border-radius: 8px;
  padding: calc(var(--stack) * 2) var(--para);
  transition: transform var(--motion-resolve) var(--ease-land);
}
```

**4. Document New Tokens**:
- If adding a new token, document it in `foundations/tokens.css` or relevant theme file
- Provide default value and explanation
- List where it is used

**5. Respect Theme Overrides**:
- Tokens change per theme (`light`, `dark`, `marathon-dark`, etc.)
- Test components in all themes
- Do not hardcode theme-specific values outside theme files

## Token Calculation Example

```css
/* Spacing scales with density slider */
--gap: calc(24px + (.3 - var(--fnd-density)) * 20px);

/* Motion duration scales with energy slider */
--motion-resolve: calc(.6s - .18s * var(--fnd-energy));
```

## Related

See `foundations/spacing.md`, `foundations/colors.md`, `foundations/motion.md`, and all `foundations/themes/*.md` files for token definitions.
