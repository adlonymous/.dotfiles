# saleh.digital Design Harness

This harness documents the design system, visual foundations, components, and design constraints for [saleh.digital](https://saleh.digital), Ahmed Saleh's personal website.

## Purpose

This harness enables AI agents to understand and recreate the saleh.digital design system. It contains:

- **Foundations**: Typography, colors, spacing, motion, themes, materials, sound, writing voice
- **Components**: UI building blocks, patterns, and screen layouts
- **Intelligence**: Agent context, policies, memories, vocabulary, skills, tools, and packages

## Commercial Assets

### ⚠️ LICENSING NOTICE

This design harness references **three commercially licensed assets** used by Saleh Digital:

1. **Shinka** (serif typeface) — Aeiou Tools
   - https://aeiou.tools/purchase/shinka
2. **Kult Luxury** (display typeface for wordmark) — commercial; buy a license from its foundry
   - (foundry link not recorded; the owner licensed it separately)
3. **Amicons** (icon set)
   - https://amicons.design/

**These assets are NOT included in this harness, the npm packages, or this repository.**

If you use this harness to build a project, you must either:
- Purchase your own licenses for Shinka, Kult Luxury, and Amicons
- Use the documented fallback alternatives (Georgia serif, Arial Black/Impact, open-source icons)

**Do NOT copy, redistribute, or bundle:**
- Shinka or Kult Luxury font files (`.woff`, `.woff2`, `.otf`, `.ttf`)
- Amicons SVG files, path data, sprite sheets, or base64 encodings

The owner supplies these assets separately for the live site.

### Other typefaces

- **Inter Display** (UI) — SIL Open Font License 1.1, https://rsms.me/inter/. Free to use; still not bundled here.
- **ABC Favorit Mono Trial** (`--mono`, rarely seen) and **Kufigraph** (the footer basmala) — not open licenses that this repo can grant. They are not bundled either; license them yourself or use the fallbacks in the stacks.

## Using This Harness

See the [main README](../../README.md) for installation and CLI usage.

**To recreate saleh.digital:**
1. Start from `templates/article.md` (the home page is the newest article, see `templates/home.md`) and `templates/record.md` for Lectures and Speaking pages. They list every record to read, in build order.
2. The frame: `foundations/layout-grid.md`. Tokens: `foundations/colors.md`, `foundations/spacing/spacing.md`, `foundations/typography/type.md`, `foundations/motion/motion.md`.
3. The look that is easy to miss: `foundations/materials/texture.md` (ink filters and grain).
4. The parts: `components/patterns/navigation.md`, `components/patterns/footer.md`, `components/patterns/harness-flow.md`, `components/components/term.md`.
5. Supply your own licensed Shinka, Kult Luxury and Amicons, or use the documented fallbacks.
6. Compare with `examples/saleh-digital-rebuild/`, which was built from these records alone and screenshotted against the live site.

## File Structure

```
saleh-digital/
├── foundations/
│   ├── typography.md (⚠️ notes Shinka license)
│   ├── colors.md
│   ├── spacing.md
│   ├── motion.md
│   ├── themes/
│   ├── icons.md (⚠️ notes Amicons license)
│   ├── materials.md
│   ├── sound.md
│   └── writing.md
├── components/
│   ├── components/
│   ├── patterns/
│   └── screens/
└── intelligence/
    ├── policy.md
    ├── memories/
    ├── vocabulary/
    ├── agents/
    ├── skills/
    ├── tools/
    └── packages/ (⚠️ includes shinka.md, kult-luxury.md, amicons.md with license notes)
```

### Also not included

- **Footer marks:** `site/assets/footer/27-45.png`, `27-48.png`, `27-49.png` and `27-50.png` in the owner's site repo. Two of them are national symbols (the emblem of Oman, a maple leaf), not original artwork. They are described in `components/patterns/footer.md`. A rebuild loads them from an owner-supplied `assets/footer/` folder, or leaves the slots empty.
- **Client work media** in the work grid: the component is described generically in `components/patterns/work-grid.md`.
- **Audio:** none exists. All sound is synthesised (`foundations/sound/sound.md`).
- **Icon paths:** any SVG path data in the copied source is replaced by `(icon path omitted)`.

## Parity

`PARITY.md` maps every page, component, interaction, animation, sound and theme on the live site to the record that specifies it.

The WebGL layer (the live wordmark, the footer pass, morphs and orbs) is reproducible from four records: [webgl](foundations/motion/webgl.md), [webgl-renderer](foundations/motion/webgl-renderer.md) (`js/gl.js` whole), [webgl-shaders](foundations/motion/webgl-shaders.md) (`js/glsl.js` whole, every uniform) and [webgl-wordmark](foundations/motion/webgl-wordmark.md). `examples/saleh-digital-rebuild` renders it from those records alone.

The records were re-checked against the site repo and the live site after the site's 2026-11-11 sync: Welcome is the front door, Theme, Sound and MCP are menu pages, Ember is the default theme, posts read at 18/28.8 in a 640px column with their contents in the sub-nav.

## Content License

The design harness content (Markdown files) is licensed under **CC BY 4.0**.

The code examples in this repository are licensed under **MIT**.

See [LICENSE-CONTENT](../../LICENSE-CONTENT) for details.

## Links

- [saleh.digital](https://saleh.digital) — Live site
- [Design Harness Specification](../../spec/SPEC.md)
- [Aeiou Tools (Shinka)](https://aeiou.tools/purchase/shinka)
- Kult Luxury: buy a license from its foundry
- [Amicons](https://amicons.design/)
- [Inter (Inter Display)](https://rsms.me/inter/)
