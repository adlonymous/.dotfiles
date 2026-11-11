---
title: Swatch
slug: swatch
status: published
description: "Colour swatches: the rec-swatch inside a colour chip, and the 14px accent chip dots of the Marathon theme cards."
chips:
  - Component
  - Colour
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:07:17Z
---

Two swatches exist:

1. **`i.rec-swatch`**, inside a record chip written `#RRGGBB Name` ([chip](chip.md)): a small filled square in that colour before the name.
2. **`.chip`**, the Marathon accent dots (the CSS is in site.css under the Settings specimens): a 14px circle filled with `--accent`, a 1px inset ink ring at 10%, and a hit area 6px larger. Hover scales it to 1.15. When checked it has a 1px outline in `--ring-page`, offset 2px. Focus-visible gives a dashed outline. The current Theme page has one card per palette and does not show these chips; the CSS is still there.

Source: `site/css/site.css`, lines 836 to 843

```css
/* Marathon: its five accents as chips under the card; hovering one recolours that card */
.chips { display: flex; gap: 8px; align-items: center; min-height: 18px; }
.chip { width: 14px; height: 14px; border-radius: 50%; background: var(--accent); outline: 1px solid transparent; outline-offset: 2px; position: relative;
  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--ink) 10%, transparent); transition: transform 160ms var(--ease-land), outline-color 160ms var(--ease-land); -webkit-tap-highlight-color: transparent; }
.chip::before { content: ""; position: absolute; inset: -6px; }
.chip:hover { transform: scale(1.15); }
.chip[aria-checked="true"] { outline-color: var(--ring-page); }
.chip:focus-visible { outline: 1px dashed var(--ring-page); }
```
