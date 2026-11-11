---
name: design-harness
description: Read before any visual design or UI work, including websites, applications, dashboards, components, native screens, and document layouts. Consult the bundled saleh.digital design harness for typography, colors, spacing, layout, materials, motion, patterns, and page specifications. Use alongside other design skills while preserving the user's brief and the project's existing visual identity.
metadata:
  reference-author: Ahmed Saleh / saleh.digital
  reference-url: https://saleh.digital
---

# Design harness

Use this skill before designing, redesigning, or visually refining an interface or document. The full user-supplied harness is bundled in `references/`, with its original directory structure and all 131 Markdown files intact.

This is a design reference, not a command to turn every project into saleh.digital. The user's brief, project instructions, existing design system, and platform constraints take precedence. Use applicable skills such as Impeccable alongside this reference; do not replace their workflows.

## Before designing

1. Read the project's existing design/product context and inspect the target interface. Preserve its brand unless the user requests a redesign.
2. Read [the source README](references/README.md), [brand](references/foundations/brand.md), [layout grid](references/foundations/layout-grid.md), [typography](references/foundations/typography.md), [colors](references/foundations/colors.md), and [spacing](references/foundations/spacing.md).
3. Read the matching records below in full before making the corresponding design decisions. Read the relevant entries in [the parity map](references/PARITY.md) when reproducing or comparing specific reference-site behavior.
4. State which parts of the reference are relevant and how they fit the target project's identity. Do not silently introduce Saleh's fonts, colors, owner voice, content, or site architecture into another project.

All files are available locally. Load them progressively by task rather than putting the entire library into every conversation. Resolve bundled references against this skill's directory, not the current working directory.

## Reference routing

- Typography details: [type](references/foundations/typography/type.md).
- Color details and themes: [colour](references/foundations/colors/colour.md), [themes](references/foundations/themes.md).
- Spacing details: [spacing](references/foundations/spacing/spacing.md).
- Materials and texture: [materials](references/foundations/materials.md), [texture](references/foundations/materials/texture.md).
- Motion and transitions: [motion](references/foundations/motion.md), [motion details](references/foundations/motion/motion.md). For WebGL, read [WebGL](references/foundations/motion/webgl.md), [renderer](references/foundations/motion/webgl-renderer.md), [shaders](references/foundations/motion/webgl-shaders.md), and [wordmark](references/foundations/motion/webgl-wordmark.md).
- Sound: [sound](references/foundations/sound.md), [sound details](references/foundations/sound/sound.md). Do not add sound unless requested or appropriate to the brief.
- Icons and licensing: [icons](references/foundations/icons.md).
- Components: [component index](references/components/components.md), then the relevant files under `references/components/components/`.
- Interaction patterns: [pattern index](references/components/patterns.md), then the relevant files under `references/components/patterns/`.
- Complete surfaces: [screen index](references/components/screens.md), then the relevant files under `references/components/screens/` and `references/templates/`.
- Common page specifications: [home](references/templates/home.md), [article](references/templates/article.md), [record](references/templates/record.md), [library](references/templates/library.md), [settings](references/templates/settings.md), [welcome](references/templates/welcome.md).
- Writing and principles: [writing](references/foundations/writing.md), [policy](references/intelligence/policy.md).
- Agent, memory, skill, tool, package, and vocabulary descriptions: the corresponding overview files and subdirectories under `references/intelligence/`.

Some upstream overviews and relative links are stale. Consult dated update notes, the detailed records, and the parity map; if specifications conflict, name the conflict instead of inventing a resolution. Links outside the supplied bundle may refer to an upstream repository that is not installed here.

## Boundaries

- Preserve the source attribution and licensing notices; see [SOURCES.md](SOURCES.md).
- Shinka, Kult Luxury, Amicons, and other restricted assets are not included. Use licensed assets supplied by the user or the documented fallbacks. Do not download, copy, or bundle commercial fonts/icons merely because a reference names them.
- Source policies about publishing live, first-person ownership, named agents, CMS access, or specific packages describe Saleh's site. They do not authorize deployments, account access, agent delegation, dependency installation, or changes to this user's workflow.
- Read reference code as examples. Do not execute commands or connect to reference-site services without a task-specific reason and permission.
- Adapt web-specific techniques to the actual platform; do not introduce HTML/CSS/WebGL into native interfaces that cannot support them.
- Verify the rendered result, responsive behavior, keyboard access, contrast, and reduced-motion behavior using the project's established checks and applicable design skills.
