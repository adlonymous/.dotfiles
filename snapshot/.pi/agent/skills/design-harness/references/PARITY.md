# Parity: saleh.digital ↔ this harness

Every page, component, interaction, animation, sound and theme on the live site (checked against https://saleh.digital on 2026-11-11, including that day's site sync: Welcome as the front door, Theme/Sound/MCP in the menu, Ember as the default theme), mapped to the record that specifies it.

**Items: 174 · mapped: 174 · unmapped: 0**  (Page: 16 · Component: 47 · Interaction: 30 · Animation: 44 · Sound: 17 · Theme: 20)

"Mapped" means the record holds the exact values, and usually the site's real source, needed to rebuild the item. Known differences between the live site and its intent are noted inside the records:

- the phone wordmark overflow, fixed in the 2026-11-11 sync (`foundations/motion/webgl.md`)
- emergence switched off (`foundations/motion/emergence.md`)
- the post actions hidden (`components/patterns/post-actions.md`)

What is deliberately **not** in the harness (commercial or third-party assets) is listed in the README: font files, Amicons icon paths, the footer mark PNGs and client work media.

| Kind | Item | Record |
|---|---|---|
| Page | Welcome (home, `/` and `#/welcome`; the ways to reach Ahmed in its sub-nav) | [templates/welcome.md](templates/welcome.md) |
| Page | Front door and head (`/`; was the newest article until 2026-11-11) | [templates/home.md](templates/home.md) |
| Page | Articles (`#/articles`) | [templates/article.md](templates/article.md) |
| Page | Article: What is a design harness? | [templates/article.md](templates/article.md) |
| Page | Lectures (`#/lectures/…`) | [templates/lectures.md](templates/lectures.md) |
| Page | Speaking (`#/talks/…`) | [templates/speaking.md](templates/speaking.md) |
| Page | Experiments (`#/experiments`) | [templates/experiments.md](templates/experiments.md) |
| Page | Library (`#/library`) | [templates/library.md](templates/library.md) |
| Page | Coffee table (`#/coffee-table`) | [templates/coffee-table.md](templates/coffee-table.md) |
| Page | Contact (retired 2026-11-11: `#/contact` lands on Welcome) | [templates/contact.md](templates/contact.md) |
| Page | Theme (`#/theme`; was Settings › Theme) | [templates/settings.md](templates/settings.md) |
| Page | Sound (`#/sound`; was Settings › Sound) | [templates/settings.md](templates/settings.md) |
| Page | MCP (`#/mcp`; was Settings › MCP) | [templates/settings.md](templates/settings.md) |
| Page | A record page (single page in a section) | [templates/record.md](templates/record.md) |
| Page | Reading screen (the article view) | [components/screens/reading.md](components/screens/reading.md) |
| Page | Footer screen | [components/screens/footer.md](components/screens/footer.md) |
| Component | Page grid: nav / sub-nav / body / media columns, fitColumns | [foundations/layout-grid.md](foundations/layout-grid.md) |
| Component | Spacing (--gap, --para, --stack) | [foundations/spacing/spacing.md](foundations/spacing/spacing.md) |
| Component | Type: Inter Display UI, Shinka body, Kult Luxury wordmark, Kufigraph basmala, mono | [foundations/typography/type.md](foundations/typography/type.md) |
| Component | Colour tokens (light block) | [foundations/colors.md](foundations/colors.md) |
| Component | Ink filters (#ink-ui, #ink-body, #ink-bio, #ink-bas, #ink-mark, #ink-dots, #ink-diagram) | [foundations/materials/texture.md](foundations/materials/texture.md) |
| Component | Grain layer (#grain) | [foundations/materials/texture.md](foundations/materials/texture.md) |
| Component | Nav menu (#nav) | [components/patterns/navigation.md](components/patterns/navigation.md) |
| Component | Post contents in the sticky sub-nav, with the SDF dot marker (added 2026-11-11) | [components/patterns/toc.md](components/patterns/toc.md) |
| Component | Phone sections pill and its list (liquid glass, added 2026-11-11) | [components/patterns/toc.md](components/patterns/toc.md) |
| Component | Post reading size: 18/28.8 in the 640px column (since 2026-11-11) | [foundations/typography/type.md](foundations/typography/type.md) |
| Component | Sub-nav with group labels (#sub) | [components/patterns/navigation.md](components/patterns/navigation.md) |
| Component | Phone menu glyph and bottom sheet | [components/patterns/navigation.md](components/patterns/navigation.md) |
| Component | Menu item states (rest / peek / active / orb) | [components/components/menu-item.md](components/components/menu-item.md) |
| Component | Post body blocks (h2, h3, lists, quote, links, bold) | [templates/article.md](templates/article.md) |
| Component | Term chip and popover | [components/components/term.md](components/components/term.md) |
| Component | Warm word | [components/components/glow.md](components/components/glow.md) |
| Component | Accent wash highlight (marathon-light) | [components/components/highlighted-word.md](components/components/highlighted-word.md) |
| Component | Record cards (icon, title, description, chips, Details) | [components/patterns/record.md](components/patterns/record.md) |
| Component | Record chips and swatches | [components/components/chip.md](components/components/chip.md) |
| Component | Colour swatch and accent chips | [components/components/swatch.md](components/components/swatch.md) |
| Component | Images revealed on attention (4th column) | [components/patterns/media-reveal.md](components/patterns/media-reveal.md) |
| Component | Full-screen viewer | [components/patterns/viewer.md](components/patterns/viewer.md) |
| Component | Dot-matrix buttons (prev / next / close) | [components/components/dot-matrix-button.md](components/components/dot-matrix-button.md) |
| Component | Post actions row (hidden on live) | [components/patterns/post-actions.md](components/patterns/post-actions.md) |
| Component | Col 4 icon buttons and the green check | [components/components/icon-button.md](components/components/icon-button.md) |
| Component | Embed: harness diagram | [components/patterns/harness-diagram.md](components/patterns/harness-diagram.md) |
| Component | Embed: harness flow (Before / After) | [components/patterns/harness-flow.md](components/patterns/harness-flow.md) |
| Component | Embed: harness viewer | [components/patterns/harness-viewer.md](components/patterns/harness-viewer.md) |
| Component | Embed: work grid | [components/patterns/work-grid.md](components/patterns/work-grid.md) |
| Component | Embed: harness actions (downloads, Book time) | [components/patterns/harness-actions.md](components/patterns/harness-actions.md) |
| Component | Embed: FAQ accordion | [components/patterns/faq.md](components/patterns/faq.md) |
| Component | Footer row: bio, basmala, dot strips, marks, quiet links | [components/patterns/footer.md](components/patterns/footer.md) |
| Component | Footer marks (4 PNG masks) | [components/patterns/footer.md](components/patterns/footer.md) |
| Component | Wordmark (fitted SVG) | [foundations/brand/wordmark.md](foundations/brand/wordmark.md) |
| Component | Library shelf (Spines) | [components/patterns/bookshelf.md](components/patterns/bookshelf.md) |
| Component | Book spine | [components/components/spine.md](components/components/spine.md) |
| Component | Book card / details | [components/components/cover.md](components/components/cover.md) |
| Component | Coffee table (The table) | [components/patterns/coffee-table.md](components/patterns/coffee-table.md) |
| Component | Experiments glyph matrix | [components/patterns/glyph-matrix.md](components/patterns/glyph-matrix.md) |
| Component | Talk slides grid | [templates/lectures.md](templates/lectures.md) |
| Component | Settings theme miniature cards | [templates/settings.md](templates/settings.md) |
| Component | Settings sound score cards | [templates/settings.md](templates/settings.md) |
| Component | MCP conversation and chips | [templates/settings.md](templates/settings.md) |
| Component | Quiet switch | [components/components/switch.md](components/components/switch.md) |
| Component | Contact links sub-nav | [templates/contact.md](templates/contact.md) |
| Component | Icons (Amicons slots) | [foundations/icons/icons.md](foundations/icons/icons.md) |
| Component | Yellow "new" orb | [foundations/motion/orbs.md](foundations/motion/orbs.md) |
| Interaction | Hover / focus peek on menu items | [foundations/motion/resolve.md](foundations/motion/resolve.md) |
| Interaction | Press: active scale and translate states | [components/components/switch.md](components/components/switch.md) |
| Interaction | Route change (hash routing, canonical path) | [foundations/motion/resolve.md](foundations/motion/resolve.md) |
| Interaction | Sub-page change in a gallery | [foundations/motion/resolve.md](foundations/motion/resolve.md) |
| Interaction | Term popover: hover 120ms, pin on click, Escape | [components/components/term.md](components/components/term.md) |
| Interaction | Warm word: 700ms hover lights it, click opens secret | [foundations/motion/hidden-extras.md](foundations/motion/hidden-extras.md) |
| Interaction | Hold wordmark 2s → أحمد صالح | [foundations/motion/hidden-extras.md](foundations/motion/hidden-extras.md) |
| Interaction | Type "harness" secret | [foundations/motion/hidden-extras.md](foundations/motion/hidden-extras.md) |
| Interaction | Night in Toronto secret | [foundations/motion/hidden-extras.md](foundations/motion/hidden-extras.md) |
| Interaction | Play the wordmark by hovering letters | [foundations/motion/hidden-extras.md](foundations/motion/hidden-extras.md) |
| Interaction | Media reveal on 250ms rest; tap inline on phone | [components/patterns/media-reveal.md](components/patterns/media-reveal.md) |
| Interaction | Viewer drag / flick / trackpad / keys / dismiss | [components/patterns/viewer.md](components/patterns/viewer.md) |
| Interaction | Library: tip on hover, pull on click, Escape | [components/patterns/bookshelf.md](components/patterns/bookshelf.md) |
| Interaction | Coffee table: hover lift, click lift, Escape | [components/patterns/coffee-table.md](components/patterns/coffee-table.md) |
| Interaction | Experiments: cursor lens, tap-tap on phone | [components/patterns/glyph-matrix.md](components/patterns/glyph-matrix.md) |
| Interaction | Harness diagram: hover lights a layer | [components/patterns/harness-diagram.md](components/patterns/harness-diagram.md) |
| Interaction | Harness flow: Before / After toggle, hover a step | [components/patterns/harness-flow.md](components/patterns/harness-flow.md) |
| Interaction | Harness viewer: column browser keys, drill-down < 600px | [components/patterns/harness-viewer.md](components/patterns/harness-viewer.md) |
| Interaction | FAQ: open / close questions | [components/patterns/faq.md](components/patterns/faq.md) |
| Interaction | Theme pick (roving radio, View Transition) | [templates/settings.md](templates/settings.md) |
| Interaction | Sound palette pick + preview | [templates/settings.md](templates/settings.md) |
| Interaction | MCP: pick tool, copy server / command | [templates/settings.md](templates/settings.md) |
| Interaction | Copy link / Copy text → copied 1.6s | [foundations/motion/resolve.md](foundations/motion/resolve.md) |
| Interaction | Phone sheet: open, drag-down close | [components/patterns/navigation.md](components/patterns/navigation.md) |
| Interaction | Record Details open / close | [components/patterns/record.md](components/patterns/record.md) |
| Interaction | Footer mark hover resolve | [components/patterns/footer.md](components/patterns/footer.md) |
| Interaction | Haptics | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Animation | think and land curves | [foundations/motion/motion.md](foundations/motion/motion.md) |
| Animation | Every duration / stagger table | [foundations/motion/motion.md](foundations/motion/motion.md) |
| Animation | Text streaming with caret | [foundations/motion/streaming.md](foundations/motion/streaming.md) |
| Animation | Field morph resolve (SDF) | [foundations/motion/resolve.md](foundations/motion/resolve.md) |
| Animation | Reduced-motion fallbacks | [foundations/motion/motion.md](foundations/motion/motion.md) |
| Animation | Focus pull | [foundations/motion/resolve.md](foundations/motion/resolve.md) |
| Animation | flowIn glide (gallery / settings) | [foundations/motion/resolve.md](foundations/motion/resolve.md) |
| Animation | Actions row step-out / back | [components/patterns/post-actions.md](components/patterns/post-actions.md) |
| Animation | Icon halftone toggle | [foundations/motion/resolve.md](foundations/motion/resolve.md) |
| Animation | Emergence reveal (off on live) | [foundations/motion/emergence.md](foundations/motion/emergence.md) |
| Animation | Resonance tiers and life | [foundations/motion/emergence.md](foundations/motion/emergence.md) |
| Animation | Orb bloom / melt / lean / flare | [foundations/motion/orbs.md](foundations/motion/orbs.md) |
| Animation | WebGL wordmark (5 life stages, cursor warp) | [foundations/motion/webgl-shaders.md](foundations/motion/webgl-shaders.md) |
| Animation | WebGL footer pass | [foundations/motion/webgl-wordmark.md](foundations/motion/webgl-wordmark.md) |
| Animation | Wordmark fit (and the phone overflow, fixed 2026-11-11) | [foundations/motion/webgl-wordmark.md](foundations/motion/webgl-wordmark.md) |
| Animation | GL renderer setup: WebGL2 context, half-float targets, the jump-flood SDF builder | [foundations/motion/webgl-renderer.md](foundations/motion/webgl-renderer.md) |
| Animation | GPU budgets, field cache and the over-budget crossfade | [foundations/motion/webgl-renderer.md](foundations/motion/webgl-renderer.md) |
| Animation | GL frame loop: busy rAF, 15/30 fps idle, hidden-tab and off-screen pausing | [foundations/motion/webgl-renderer.md](foundations/motion/webgl-renderer.md) |
| Animation | GL DPR cap (1.5, 1.2 while scrolling) and resize | [foundations/motion/webgl-renderer.md](foundations/motion/webgl-renderer.md) |
| Animation | GL context loss and the one restore | [foundations/motion/webgl-renderer.md](foundations/motion/webgl-renderer.md) |
| Animation | Item morph shader (ITEM_FRAG) and its uniforms | [foundations/motion/webgl-shaders.md](foundations/motion/webgl-shaders.md) |
| Animation | Body line morph shader (LINES_FRAG) and its uniforms | [foundations/motion/webgl-shaders.md](foundations/motion/webgl-shaders.md) |
| Animation | Wordmark shader uniforms and how each animates | [foundations/motion/webgl-shaders.md](foundations/motion/webgl-shaders.md) |
| Animation | Orb shaders (glow and dots) | [foundations/motion/webgl-shaders.md](foundations/motion/webgl-shaders.md) |
| Animation | Wordmark per-glyph fields and the stage-4 melt | [foundations/motion/webgl-wordmark.md](foundations/motion/webgl-wordmark.md) |
| Animation | Wordmark Arabic hold mix | [foundations/motion/webgl-wordmark.md](foundations/motion/webgl-wordmark.md) |
| Animation | Footer dot strips (GL blobs; 2D canvas fallback) | [foundations/motion/webgl-wordmark.md](foundations/motion/webgl-wordmark.md) |
| Animation | No-WebGL and ?lite fallback (SVG wordmark, DOM ink filters) | [foundations/motion/webgl-wordmark.md](foundations/motion/webgl-wordmark.md) |
| Animation | Reduced motion in the GL layer | [foundations/motion/webgl-wordmark.md](foundations/motion/webgl-wordmark.md) |
| Interaction | Wordmark letter notes and haptics (wordmark:letter) | [foundations/motion/webgl-wordmark.md](foundations/motion/webgl-wordmark.md) |
| Interaction | Mark hover focus in the GL footer | [foundations/motion/webgl-wordmark.md](foundations/motion/webgl-wordmark.md) |
| Interaction | Cursor warp on the wordmark (document-space pointer) | [foundations/motion/webgl-renderer.md](foundations/motion/webgl-renderer.md) |
| Theme | GL re-tint on theme change (uInk, uSwell, uFoot, orb colours) | [foundations/motion/webgl-renderer.md](foundations/motion/webgl-renderer.md) |
| Theme | Favicon dot matrix follows the theme | [foundations/themes.md](foundations/themes.md) |
| Animation | Grain jitter 15 fps | [foundations/materials/texture.md](foundations/materials/texture.md) |
| Animation | Footer dot strips (SDF dot matrix) | [components/patterns/footer.md](components/patterns/footer.md) |
| Animation | Harness flow flowing dots shader | [components/patterns/harness-flow.md](components/patterns/harness-flow.md) |
| Animation | Theme crossfade (View Transition) | [foundations/themes.md](foundations/themes.md) |
| Animation | Dot-matrix button breathing | [components/components/dot-matrix-button.md](components/components/dot-matrix-button.md) |
| Animation | Library pull arc / springs | [components/patterns/bookshelf.md](components/patterns/bookshelf.md) |
| Animation | Coffee table depth of field | [components/patterns/coffee-table.md](components/patterns/coffee-table.md) |
| Animation | Glyph matrix lens ripple / write-in | [components/patterns/glyph-matrix.md](components/patterns/glyph-matrix.md) |
| Animation | Viewer spring physics | [components/patterns/viewer.md](components/patterns/viewer.md) |
| Animation | Media reveal dot dissolve | [components/patterns/media-reveal.md](components/patterns/media-reveal.md) |
| Animation | MCP held controls rise-in | [templates/settings.md](templates/settings.md) |
| Animation | Sound score playhead | [templates/settings.md](templates/settings.md) |
| Animation | Slow-motion review aid | [foundations/motion/motion.md](foundations/motion/motion.md) |
| Animation | Contents marker spring glide and pill entrance | [components/patterns/toc.md](components/patterns/toc.md) |
| Animation | Orb review stage (bench tool, not on the site) | [foundations/motion/orbs.md](foundations/motion/orbs.md) |
| Sound | Audio unlock on first gesture | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | Master switch sd:sound (default on) | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | Bed sd:bed (pad + air) | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | Feel palette sd:feel (default felt-hushed) | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | Section chords + pad glide on route change | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | hover droplet | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | emerge arpeggio + shimmer | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | wordmark letter notes | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | press | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | drag steps | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | release | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | toggle-on pluck | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | Silent events (copy, page click) | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | Signal chain (compressor, reverb, chorus, wow/flutter, crush, pump) | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | Resonance warmth | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | Suspend when muted / hidden; reduced-motion pitch | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Sound | Palettes: Felt, Felt hushed, Unison, Low tide, Mist, Off | [foundations/sound/sound.md](foundations/sound/sound.md) |
| Theme | Paper (light) | [foundations/themes/light.md](foundations/themes/light.md) |
| Theme | Night (dark) | [foundations/themes/dark.md](foundations/themes/dark.md) |
| Theme | Acid (marathon-dark lime) | [foundations/themes/marathon-dark.md](foundations/themes/marathon-dark.md) |
| Theme | Static (marathon-dark cyan) | [foundations/themes/marathon-accents.md](foundations/themes/marathon-accents.md) |
| Theme | Siren (marathon-dark red) | [foundations/themes/marathon-accents.md](foundations/themes/marathon-accents.md) |
| Theme | Ember (marathon-dark amber) | [foundations/themes/marathon-accents.md](foundations/themes/marathon-accents.md) |
| Theme | Reactor (marathon-dark green) | [foundations/themes/marathon-accents.md](foundations/themes/marathon-accents.md) |
| Theme | Sulphur (marathon-light lime) | [foundations/themes/marathon-light.md](foundations/themes/marathon-light.md) |
| Theme | Glacier (marathon-light cyan) | [foundations/themes/marathon-accents.md](foundations/themes/marathon-accents.md) |
| Theme | Flare (marathon-light red) | [foundations/themes/marathon-accents.md](foundations/themes/marathon-accents.md) |
| Theme | Honey (marathon-light amber) | [foundations/themes/marathon-accents.md](foundations/themes/marathon-accents.md) |
| Theme | Moss (marathon-light green) | [foundations/themes/marathon-accents.md](foundations/themes/marathon-accents.md) |
| Theme | Semantic token mapping per theme | [foundations/themes.md](foundations/themes.md) |
| Theme | Persistence (sd.theme) and ?theme preview | [foundations/themes.md](foundations/themes.md) |
| Theme | Default for everyone: Ember (no longer follows prefers-color-scheme) | [foundations/themes.md](foundations/themes.md) |
| Theme | First-paint inline script + theme-color meta | [foundations/themes.md](foundations/themes.md) |
| Theme | theme:change event to GL / grain / grids | [foundations/themes.md](foundations/themes.md) |
| Theme | Switcher UI | [templates/settings.md](templates/settings.md) |

## Rebuild check for the WebGL rows

`examples/saleh-digital-rebuild` runs `gl.js`, `glsl.js`, `raster.js` and `orb.js` exactly as copied out of the WebGL records, together with the verbatim wordmark-fit, footer-bake and letter blocks from webgl-wordmark.md. `tools/gl-selftest.sh` checks three pages (home, record and settings) in headless Chrome with SwiftShader. On each page it reads back non-empty `#gl` pixels in the wordmark box and in the footer strip. With WebGL disabled it reports `gl: false`, and the SVG wordmark stays in place. Results are in `examples/saleh-digital-rebuild/screenshots/selftest-gl-*.json`. The rebuild leaves out the footer marks (no masks), the orbs, and the gallery-grid passes.
