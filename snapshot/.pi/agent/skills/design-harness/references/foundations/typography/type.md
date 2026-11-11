---
title: Type
slug: type
status: published
order: 2
description: Shinka for reading, Inter Display for interface and everything around it, and Kult Luxury, drawn as a shader, for the wordmark.
chips:
  - Shinka 16/20.8
  - Inter Display 16/16
  - Kult Luxury
  - Tracking −0.64
created: 2026-11-09T14:21:21Z
updated: 2026-11-09T17:23:21Z
---


Three faces, each with one job. Shinka is the reading face, Inter Display is everything around the reading, and Kult Luxury is only the footer wordmark.

> **Licensing.** Shinka (Aeiou Tools, https://aeiou.tools/purchase/shinka) and Kult Luxury are commercial typefaces. They are not in this repository or its npm packages. If you build with this harness, buy your own licenses or use the fallbacks below. Never commit, bundle or base64 the font files.

## Stacks (`css/tokens.css`)

```css
:root {
  --ui:    "Inter Display", "Helvetica Neue", "SF Arabic", "Geeza Pro", Arial, sans-serif;
  --serif: "Shinka", Georgia, serif;
  --mono:  "SF Mono", ui-monospace, Menlo, monospace;
  --track: -.64px;
}
```

As of the site on 2026-11-11, `--mono` no longer names ABC Favorit Mono Trial, and `--ui` adds the system Arabic faces before Arial. The gallery grids still name the trial face directly in their own canvas fonts (see [spine](../../components/components/spine.md) and [glyph matrix](../../components/patterns/glyph-matrix.md)).

## Faces (`css/site.css`), with owner-supplied files

```css
@font-face { font-family: "Inter Display"; src: url(../fonts/InterDisplay-Regular.woff2) format("woff2"); font-weight: 400; font-style: normal; font-display: swap; size-adjust: 100.06%; ascent-override: 90%; descent-override: 22%; line-gap-override: 0%; }
@font-face { font-family: "Inter Display"; src: url(../fonts/InterDisplay-Italic.woff2) format("woff2"); font-weight: 400; font-style: italic; font-display: swap; size-adjust: 100.06%; ascent-override: 90%; descent-override: 22%; line-gap-override: 0%; }
@font-face { font-family: "Inter Display"; src: url(../fonts/InterDisplay-Medium.woff2) format("woff2"); font-weight: 500; font-style: normal; font-display: swap; size-adjust: 100.06%; ascent-override: 90%; descent-override: 22%; line-gap-override: 0%; }
/* commercial: supply your own licensed files at these paths */
@font-face { font-family: "Shinka"; src: url(../fonts/Shinka-Regular.otf) format("opentype"); font-weight: 400; font-style: normal; font-display: swap; size-adjust: 100%; ascent-override: 91%; descent-override: 25%; line-gap-override: 0%; }
@font-face { font-family: "Shinka"; src: url(../fonts/Shinka-RegularItalic.otf) format("opentype"); font-weight: 400; font-style: italic; font-display: swap; size-adjust: 100%; ascent-override: 91%; descent-override: 25%; line-gap-override: 0%; }
@font-face { font-family: "Kult Luxury"; src: url(../fonts/Kult-Luxury.woff2) format("woff2"), url(../fonts/Kult-Luxury.otf) format("opentype"); font-weight: 400; font-style: normal; font-display: block; }
@font-face { font-family: "Kufigraph"; src: url(../fonts/Kufigraph-Light.otf) format("opentype"); font-weight: 300; font-style: normal; font-display: block; }
@font-face { font-family: "Kufigraph"; src: url(../fonts/Kufigraph-Regular.otf) format("opentype"); font-weight: 400; font-style: normal; font-display: block; }
```

Since 2026-11-11 Kult Luxury and Kufigraph are `font-display: block` (they were `optional`), and the ABC Favorit Mono Trial face is no longer declared in `css/site.css`.

Shinka has a single weight. Bold is drawn, not loaded: `.col-body strong { font-weight: 400; -webkit-text-stroke: .5px currentColor; }`.

## Scale

| Role | Face | Size / line | Tracking |
| --- | --- | --- | --- |
| Body copy (`.col-body`) | Shinka | 16 / 20.8 | -0.64 |
| Post heading `h2`, desktop | Inter Display 400 | 28 / 32 | -1.1 |
| Post heading `h2`, below 900px | Inter Display 400 | 24 / 28 | -0.9 |
| Post heading `h3` | Inter Display 400 | 20 / 24 | -0.6 |
| Menu, page titles, UI (`body`) | Inter Display 400 | 16 / 16 (4px stack, 20px pitch) | -0.64 |
| Record title | Inter Display 400 | 16 / 20 | -0.64 |
| Record meta line, figure caption | Inter Display 400 | 14 / 20 | -0.2 |
| Flow cards | Inter Display 400 (Harness card 500) | 15 (13 under 600px) | inherit |
| Before / After tabs | Inter Display 400 | 14 / 34 (13 / 30 under 600px) | -0.2 |
| Phone menu sheet items | Inter Display 400 | 24 / 28 | -0.96 |
| Footer bio | Inter Display 400 | 16 / 19.2 | -0.64 |
| Footer basmala | Kufigraph 300 | 18 / 19.2 | 0 |
| Wordmark | Kult Luxury 400 | fitted to the window width (see brand/wordmark.md) | 0 |

There is no post title on the page: the `h1` is `.sr-only`, and the current page title is shown in the section list (column 2). The first visible line of an article is its first `h2`.

```css
.col-body { font: 400 16px/20.8px var(--serif); letter-spacing: var(--track); font-kerning: normal; }
.col-body h2, .col-body h3 { margin: 0; font: 400 16px/20px var(--ui); letter-spacing: var(--track); text-wrap: balance; }
.col-body h2 { font-size: 28px; line-height: 32px; letter-spacing: -1.1px; }
.col-body h3 { font-size: 20px; line-height: 24px; letter-spacing: -0.6px; }
@media (max-width: 899px) { .col-body h2 { font-size: 24px; line-height: 28px; letter-spacing: -0.9px; } }
.col-body em { font-style: italic; }
```

## Fallbacks when you have no license

- Shinka → `Georgia, serif`. Georgia sets wider than Shinka, so expect each line to hold a few fewer words. Keep 16 / 20.8.
- Kult Luxury → any high-contrast book serif (for example `"Times New Roman", serif`); keep the fitting rule so the word still spans the window.
- Inter Display is open (SIL OFL 1.1, https://rsms.me/inter/); fallback `"Helvetica Neue", Arial, sans-serif`.

## Rules

- Never set body copy in Inter Display or headings in Shinka.
- No bold weights in the UI. Weight 500 appears in one place, the Harness card of the flow diagram.
- All type gets the ink filter (see materials/texture.md); without it the page looks digital and flat.

## Reading size (since 2026-11-11)

Posts set the body at the long-read standard: **18px on a 1.6 line (28.8px)**, tracking eased from −0.64px to **−0.2px**, paragraph gap `--para + 6px`, about 74 characters to the **640px** line (540px before that day). Phones: 17/27.2. Headings keep their sizes. Galleries keep 16/16 Inter Display. A post's opening heading sits on the nav's line (−3.35px top margin at ≥ 900px).

Source: `site/css/site.css`, lines 910 to 919

```css
/* reading size (Ahmed, Nov 11): posts at the common long-read standard, 18px on a 1.6 line (28.8px),
   about 74 characters to the 640px line (Ahmed widened it from 540, Nov 11); tracking eased from -0.64 (tuned for 16/20.8) to -0.2, since
   tight tracking tires the eye at length. Paragraph gap follows the line: about 1.1 lines.
   Phones: 17/27.2. Headings keep their sizes; the list markers and quotes follow the body. */
.col-body article { font-size: 18px; line-height: 1.6; letter-spacing: -0.2px; gap: calc(var(--para) + 6px); }
.col-body article > :is(h2, h3) + * { margin-top: calc(var(--para) * -0.35); }
.col-body article li::marker { font-size: 15px; }
.col-body article blockquote { gap: calc(var(--para) * 0.6); }
@media (max-width: 899px) { .col-body article { font-size: 17px; line-height: 1.6; } }
html.is-gallery .col-body article { font: 400 16px/16px var(--ui); letter-spacing: var(--track); }
```
