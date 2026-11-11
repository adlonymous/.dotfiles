---
title: Catalogue Lookup
slug: catalogue-lookup
status: published
description: Query the design harness for reference.
chips:
  - Skill
  - Harness
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Procedure for searching and referencing the Saleh Digital design harness (catalogue) to ensure consistency.

## Steps

**1. Identify Question**:
- What component, pattern, or foundation do I need?
- What value (color, size, duration) does this use?
- How is this interaction supposed to work?

**2. Search Harness**:
- Search harness files by keyword (e.g., "chip", "footer", "spacing")
- Check frontmatter `chips` for tags
- Grep for specific values (hex colors, px sizes, token names)

**3. Read Specification**:
- Open relevant `.md` file
- Read anatomy, styling, states, and usage sections
- Note exact values and code snippets

**4. Apply to Work**:
- Use the documented values and patterns
- Do not invent new values or deviate from spec
- If spec is unclear or missing, flag for harness update

**5. Update Harness (if needed)**:
- If new component or pattern, write new `.md` file
- If existing spec is wrong or incomplete, update it
- Commit harness changes with work

## Search Methods

**By component name**:
```bash
find harnesses/saleh-digital -name "*chip*"
```

**By keyword**:
```bash
grep -r "border-radius" harnesses/saleh-digital
```

**By color value**:
```bash
grep -r "#1a1a1a" harnesses/saleh-digital/foundations/themes
```

## Usage

Agents (Ada, Dev, Wren) use this skill before making design or code decisions to ensure consistency with documented specs.

## Related

See `README.md` for harness overview.
