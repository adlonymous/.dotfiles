---
title: Figma Import
slug: figma-import
status: published
description: Pull designs and specs from Figma files.
chips:
  - Skill
  - Design
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Procedure for importing design specs, tokens, and assets from Figma into the Saleh Digital harness and codebase.

## Steps

**1. Access Figma File**:
- Use Figma API with personal access token
- Fetch file data by file key: `GET /v1/files/:file_key`

**2. Extract Tokens**:
- Parse local styles (colors, text styles, effects)
- Map Figma style names to CSS custom property names
- Generate `tokens.css` or update existing values

**3. Extract Components**:
- Identify component sets and variants
- Read component names, descriptions, properties
- Generate harness component `.md` files with anatomy and states

**4. Export Assets**:
- Download images and icons via Figma export API
- Optimize PNGs and SVGs (SVGO)
- Store in `/assets/` with consistent naming

**5. Update Harness**:
- Write new component specs or update existing ones
- Include exact values (hex colors, px sizes, font weights)
- Add code snippets for implementation

**6. Validate**:
- Check that imported values match Figma source
- Test components in isolation
- Update design tokens in running site

## Figma API Example

```js
const response = await fetch(
  `https://api.figma.com/v1/files/${fileKey}`,
  { headers: { 'X-Figma-Token': process.env.FIGMA_TOKEN } }
);
const figmaData = await response.json();
```

## Mapping

Figma styles → CSS tokens:
- Color: `Primary/Ink` → `--ink`
- Text: `UI/Body` → `font-size: 16px; line-height: 20px`

## Related

See `intelligence/agents/wren.md` for design agent that uses this skill.
