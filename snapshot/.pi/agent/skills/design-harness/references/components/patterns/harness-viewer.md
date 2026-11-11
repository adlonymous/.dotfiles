---
title: Harness viewer
slug: harness-viewer
status: published
description: "::harness-viewer: a three-column browser of every part of a design harness (layers, terms, records, then the record with a live specimen read off the site tokens)."
chips:
  - Embed
  - Viewer
created: 2026-11-11T16:05:20Z
updated: 2026-11-11T16:05:35Z
---

Embeds are placed in a post by a paragraph that is only `::name` (`EMBED = /^::([a-z-]+)\s*$/`). `js/embeds.js` replaces it with `<div class="embed embed-NAME" data-embed="NAME" data-stream-skip>`, lazy-imports `js/embeds/NAME.js` and calls `mount(el, ctx)`. Embeds are skipped by the word stream and by the body ink filter (`.col-body article > :not(.embed) { filter: url(#ink-body) }`), so screenshots and diagrams stay sharp.

**What it is.** Every part of a design harness, defined, laid out like a harness-viewer app: three columns in one frame. The first column is the **layers**, then that layer's **terms**, then the term's **records** (the same list rows). The last pane is the record: its name, term and line beside a **specimen** where one is real. Specimens are read live off the site's own tokens: a token resolved on a hidden probe (optionally under a theme), the twelve theme palettes, the sound palettes (playable), the shaders, the MCP apps and the footer marks. The words come from `js/glossary.js` ([harness diagram](harness-diagram.md) lists it). The records come from `js/embeds/harness-records.js`, which is generated from the site's own `content/harness`.

- **Keyboard:** a column browser. Up/Down moves within a column, Right/Enter moves into the next one, Left goes back.
- **Narrow screens:** under 600px it drills down one column at a time, with a back control.
- **Width:** it runs full width to the page's right padding at 900px and wider (see the full-width rule in [harness diagram](harness-diagram.md)).
- **Icons:** Icons come from `js/embeds/harness-icons.js` (`svgIcon(name)`). Those are icon-set paths and are **not** reproduced here; leave a 14 to 16px `currentColor` slot of the same size.

Source: `site/css/embeds/harness-viewer.css`, whole file

```css
/* ::harness-viewer (js/embeds/harness-viewer.js): the app's three-column harness viewer,
   inside the article. Layers | terms | the term, one rounded frame, hairline dividers. */
.embed-harness-viewer { container-type: inline-size; margin: calc(var(--para) * 0.5) 0; font: 400 14px/20px var(--ui); letter-spacing: -0.2px; }
.hv-frame { --hv-edge: color-mix(in srgb, var(--ink) 10%, transparent);
  display: grid; position: relative; grid-template-columns: clamp(140px, 15%, 172px) clamp(132px, 15%, 180px) clamp(150px, 18%, 210px) minmax(0, 1fr); height: clamp(420px, 34vw, 480px); overflow: hidden; container-type: inline-size;
  border-radius: 12px; background: color-mix(in srgb, var(--ink) 2.5%, var(--paper)); }
.hv-frame::after { content: ''; position: absolute; inset: 0; border-radius: inherit; box-shadow: inset 0 0 0 1px var(--hv-edge); pointer-events: none; z-index: 1; }
.hv-bar { display: none; }
.hv-col { min-width: 0; overflow-y: auto; overscroll-behavior: contain; outline: none; scrollbar-width: none; }
.hv-col::-webkit-scrollbar { display: none; }
.hv-col + .hv-col { box-shadow: inset 1px 0 0 var(--hv-edge); }
.hv-layers, .hv-terms, .hv-records { display: flex; flex-direction: column; gap: 1px; padding: 8px 6px; }
.hv-right { display: flex; flex-direction: column; background: var(--paper); }
.hv-detail { flex: none; padding: 18px 20px 18px; display: flex; flex-direction: column; align-items: flex-start; gap: 6px; outline: none; }
.hv-detail > .hv-d-def { max-width: 56ch; }
/* the preview pane: the term's example from this site, large, on its own surface */
.hv-preview { flex: 1 0 auto; display: flex; flex-direction: column; min-width: 0; container-type: inline-size; background: color-mix(in srgb, var(--ink) 3.5%, var(--paper)); box-shadow: inset 0 1px 0 var(--hv-edge); }
.hv-p-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; padding: 12px 20px 0; }
.hv-p-title { font-size: 12px; line-height: 16px; color: var(--ink); }
.hv-p-sub { font-size: 11px; line-height: 16px; color: var(--muted); }
.hv-p-body { flex: 1; padding: 16px 20px 22px; font-size: 13px; line-height: 17px; letter-spacing: 0; }
/* wide: four columns, the preview the widest, each scrolling on its own */
@container (min-width: 800px) {
  .hv-frame { grid-template-columns: clamp(156px, 14%, 176px) clamp(150px, 14%, 184px) clamp(170px, 17%, 220px) minmax(0, 1fr); }
  /* the preview gets the room (Ahmed, Nov 10): the definition narrows, the preview takes about two thirds */
  .hv-right { display: grid; grid-template-columns: minmax(200px, 0.65fr) minmax(0, 1.6fr); overflow: hidden; }
  .hv-detail, .hv-preview { overflow-y: auto; scrollbar-width: none; }
  .hv-preview { box-shadow: inset 1px 0 0 var(--hv-edge); }
  .hv-p-head { padding: 16px 24px 0; }
  .hv-p-body { padding: 20px 24px 28px; }
}

/* rows: the nav's language. Receding at rest, sharp when chosen; the layer in the accent like the active nav item */
.hv-opt { display: flex; align-items: center; gap: 8px; min-height: 28px; padding: 4px 8px; border-radius: 6px; color: var(--ink); cursor: pointer; outline: none; user-select: none; -webkit-user-select: none;
  opacity: var(--op-meta); filter: url(#ink-ui); -webkit-tap-highlight-color: transparent; transition: opacity 140ms var(--ease-land), background-color 140ms var(--ease-land); }
.hv-opt:hover { opacity: 1; }
.hv-ico { flex: none; display: grid; place-items: center; width: 16px; height: 16px; margin-left: -1px; color: currentColor; transition: color 140ms var(--ease-land); }
.hv-ico svg { display: block; width: 16px; height: 16px; }
.hv-opt.is-active .hv-ico { color: var(--accent-mark); }
.hv-d-ico { flex: none; display: grid; place-items: center; width: 20px; height: 20px; color: var(--accent-mark); transform: translateY(-1px); }
.hv-d-ico svg { display: block; }
.hv-opt-label { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hv-n { flex: none; font-size: 11px; font-variant-numeric: tabular-nums; letter-spacing: 0; color: var(--muted); }
.hv-opt.is-active { opacity: 1; background: color-mix(in srgb, var(--ink) 6%, transparent); }
.hv-layer.is-active { color: var(--accent-text); }
[data-theme="marathon-light"] .hv-layer.is-active { color: var(--ink); background: var(--accent-wash); }
.hv-opt:focus-visible { opacity: 1; box-shadow: inset 0 0 0 1px var(--ring); }

/* the term */
.hv-detail p, .hv-preview p { margin: 0; }
.hv-d-layer { font-size: 11px; line-height: 16px; letter-spacing: 0.2px; text-transform: uppercase; color: var(--muted); }
.hv-d-term { display: flex; align-items: center; gap: 8px; margin: 0; font: 400 20px/24px var(--ui); letter-spacing: -0.6px; }
.hv-d-def { margin-top: 2px !important; font: 400 16px/20.8px var(--serif); letter-spacing: var(--track); }
.hv-d-go { margin-top: 2px; color: var(--ink); text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; text-decoration-color: color-mix(in srgb, var(--ink) 30%, transparent); transition: text-decoration-color 160ms var(--ease-land); }
.hv-d-go:hover, .hv-d-go:focus-visible { outline: none; text-decoration-color: currentColor; }

/* specimens: quiet, real values */
.hvs-k { color: var(--ink); }
.hvs-v { color: var(--muted); font-family: var(--mono); font-size: 11px; font-variant-numeric: tabular-nums; }
.hvs-colors { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px 8px; }
.hvs-sw { display: grid; grid-template-columns: 18px 1fr; column-gap: 7px; align-items: center; }
.hvs-chip { grid-row: span 2; width: 18px; height: 18px; border-radius: 5px; box-shadow: inset 0 0 0 1px var(--hv-edge); }
.hvs-themes { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 5px; }
.hvs-theme { position: relative; display: flex; flex-direction: column; justify-content: space-between; height: 40px; padding: 4px 6px; border-radius: 6px; box-shadow: inset 0 0 0 1px var(--hv-edge); overflow: hidden; }
.hvs-theme-aa { font: 400 13px/14px var(--ui); letter-spacing: -0.3px; }
.hvs-theme-n { font-size: 9px; line-height: 10px; opacity: .7; white-space: nowrap; }
.hvs-theme-dot { position: absolute; top: 6px; right: 6px; width: 6px; height: 6px; border-radius: 50%; }
.hvs-type { display: flex; flex-direction: column; gap: 8px; }
.hvs-type-row { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; }
.hvs-type-aa { color: var(--ink); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.hvs-space { display: flex; flex-direction: column; gap: 8px; }
.hvs-space-row { display: grid; grid-template-columns: 40px 1fr auto; align-items: center; gap: 8px; }
.hvs-space-bar { height: 8px; border-radius: 1px; background: var(--accent-mark); opacity: .85; }
.hvs-motion { display: flex; gap: 16px; }
.hvs-motion-c { display: grid; gap: 2px; }
.hvs-curve-box svg { display: block; overflow: visible; }
.hvs-axis { fill: none; stroke: var(--hv-edge); stroke-width: 1; }
.hvs-curve { fill: none; stroke: var(--accent-mark); stroke-width: 1.5; stroke-linecap: round; }
.hvs-icons { display: flex; gap: 14px; }
.hvs-icon { width: 20px; height: 20px; background: var(--ink); -webkit-mask: var(--src) center / contain no-repeat; mask: var(--src) center / contain no-repeat; }

/* phone: one column at a time, a back control above */
@media (max-width: 599px) {
  .hv-frame { display: flex; flex-direction: column; height: auto; min-height: 340px; }
  .hv-bar { display: flex; align-items: center; gap: 8px; height: 40px; padding: 0 8px; box-shadow: inset 0 -1px 0 var(--hv-edge); }
  .hv-back { display: inline-flex; align-items: center; gap: 4px; height: 32px; padding: 0 8px 0 4px; border: 0; border-radius: 6px; background: none; color: var(--ink); font: inherit; letter-spacing: inherit; cursor: pointer; -webkit-tap-highlight-color: transparent; }
  .hv-back[hidden] { display: none; }
  .hv-back-arrow { font-size: 20px; line-height: 1; transform: translateY(-1px); }
  .hv-back:focus-visible { outline: none; box-shadow: inset 0 0 0 1px var(--ring); }
  .hv-crumb { margin-left: auto; padding-right: 8px; color: var(--muted); }
  .hv-back[hidden] + .hv-crumb { margin-left: 0; padding-left: 8px; }
  .hv-col { display: none; overflow: visible; }
  .hv-col + .hv-col { box-shadow: none; }
  .hv-frame[data-depth="0"] .hv-layers, .hv-frame[data-depth="1"] .hv-terms, .hv-frame[data-depth="2"] .hv-records, .hv-frame[data-depth="3"] .hv-right { display: flex; }
  .hv-layers, .hv-terms, .hv-records { padding: 8px; }
  .hv-opt { min-height: 44px; align-items: center; font-size: 16px; letter-spacing: -0.4px; padding: 0 12px; }
  .hv-opt::after { content: '\203A'; flex: none; color: var(--muted); font-size: 18px; }
  .hv-detail { padding: 16px; }
  .hv-p-head { padding: 12px 16px 0; }
  .hv-p-body { padding: 14px 16px 18px; }
}
/* the site's own examples, under the definition */
.hvs-stack { display: flex; flex-direction: column; gap: 10px; }
.hvs-lead { margin: 0; font-size: 13px; line-height: 18px; letter-spacing: -0.1px; color: var(--ink); }
.hvs-note { margin: 0; font-size: 12px; line-height: 16px; color: var(--muted); }
.hvs-quote { margin: 0; font: 400 15px/19.5px var(--serif); letter-spacing: var(--track); color: var(--ink); }
.hvs-code { font-family: var(--mono); }
.hvs-recs { display: grid; grid-template-columns: 1fr; gap: 0; }
@container (min-width: 520px) { .hvs-recs { grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 20px; } }
@container (min-width: 760px) { .hvs-recs { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
.hvs-rec { display: flex; flex-direction: column; gap: 2px; padding: 8px 0; border-top: 1px solid var(--hv-edge); }
.hvs-rec:first-child { border-top: 0; padding-top: 0; }
@container (min-width: 520px) { .hvs-rec { border-top: 0; padding-top: 0; } }
.hvs-rec-t { font-size: 13px; line-height: 18px; letter-spacing: -0.15px; color: var(--ink); }
.hvs-rec-l { font: 400 13.5px/18px var(--serif); letter-spacing: -0.2px; color: color-mix(in srgb, var(--ink) 72%, var(--paper)); }
.hvs-more { margin: 4px 0 0; font-size: 11.5px; color: var(--muted); grid-column: 1 / -1; }
.hvs-brand { display: flex; flex-direction: column; gap: 12px; }
.hvs-wordmark { font: 400 clamp(18px, 5cqi, 34px)/1.1 "Kult Luxury", var(--ui); white-space: nowrap; letter-spacing: 0; color: var(--ink); filter: url(#ink-ui); }
.hvs-marks { display: flex; align-items: center; gap: 12px; }
.hvs-mark { display: block; height: 20px; background: var(--ink); -webkit-mask: var(--src) center / contain no-repeat; mask: var(--src) center / contain no-repeat; }
.hvs-sound { display: flex; flex-direction: column; }
.hvs-sound-row { display: grid; grid-template-columns: 24px minmax(0, 1fr) auto auto; align-items: center; gap: 10px; min-height: 32px; border-top: 1px solid var(--hv-edge); }
.hvs-sound-row:first-child { border-top: 0; }
.hvs-play { display: grid; place-items: center; width: 24px; height: 24px; padding: 0; border: 0; border-radius: 6px; background: color-mix(in srgb, var(--ink) 6%, transparent); color: var(--ink); cursor: pointer; transition: background-color 140ms var(--ease-land), transform 120ms var(--ease-land); }
.hvs-play:hover { background: color-mix(in srgb, var(--ink) 12%, transparent); }
.hvs-play:active { transform: scale(0.94); }
.hvs-play:focus-visible { outline: none; box-shadow: 0 0 0 1px var(--ring); }
.hvs-play-ico { width: 0; height: 0; margin-left: 2px; border-left: 7px solid currentColor; border-top: 4.5px solid transparent; border-bottom: 4.5px solid transparent; }
.hvs-tag { min-width: 40px; text-align: right; font-size: 11px; color: var(--accent-text); }
.hvs-images { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
.hvs-img { display: block; width: 100%; aspect-ratio: 4 / 3; object-fit: cover; border-radius: 16px; background: var(--hv-edge); }
.hvs-layout { display: flex; gap: var(--gap); }
.hvs-col { display: flex; flex-direction: column; justify-content: space-between; min-width: 0; height: 64px; padding: 6px 7px; border-radius: 6px; box-shadow: inset 0 0 0 1px var(--hv-edge); background: color-mix(in srgb, var(--ink) 3%, transparent); }
.hvs-col:last-child { background: color-mix(in srgb, var(--accent-mark) 10%, transparent); }
.hvs-materials { display: flex; gap: 20px; flex-wrap: wrap; }
.hvs-mat { display: flex; flex-direction: column; gap: 4px; }
.hvs-mat-aa { font: 400 26px/1.1 var(--serif); letter-spacing: -0.6px; color: var(--ink); }
.hvs-mat-aa.is-ui { font-family: var(--ui); }
.hvs-consts { display: flex; flex-direction: column; }
.hvs-const { display: grid; grid-template-columns: minmax(84px, auto) minmax(0, auto) minmax(0, 1fr); align-items: baseline; gap: 12px; padding: 5px 0; border-top: 1px solid var(--hv-edge); }
.hvs-const:first-child { border-top: 0; }
.hvs-const .is-val { color: var(--ink); }
.hvs-c { font-size: 11.5px; line-height: 15px; color: var(--muted); }
.hvs-flow { margin: 0; padding: 0; list-style: none; counter-reset: f; display: flex; flex-direction: column; gap: 6px; font: 400 14px/18.2px var(--serif); letter-spacing: -0.3px; }
.hvs-flow li { counter-increment: f; display: grid; grid-template-columns: 18px 1fr; }
.hvs-flow li::before { content: counter(f); font: 400 11px/18px var(--ui); font-variant-numeric: tabular-nums; color: var(--muted); }
.hvs-options { display: flex; flex-wrap: wrap; gap: 6px; }
.hvs-option { display: inline-flex; align-items: center; gap: 6px; height: 26px; padding: 0 10px; border-radius: 7px; box-shadow: inset 0 0 0 1px var(--hv-edge); font-size: 12.5px; color: var(--muted); }
.hvs-option.is-on { color: var(--ink); box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--ink) 40%, transparent); }
.hvs-option.is-on::before { content: ''; width: 5px; height: 5px; border-radius: 50%; background: var(--accent-mark); }
.hvs-option-n { font-size: 11px; color: var(--muted); }
.hvs-tune { display: flex; flex-direction: column; gap: 8px; }
.hvs-tune-row { display: grid; grid-template-columns: 64px minmax(80px, 1fr) auto; align-items: center; gap: 12px; }
.hvs-track { position: relative; height: 2px; border-radius: 1px; background: var(--hv-edge); }
.hvs-track::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: calc(var(--x) * 100%); border-radius: inherit; background: var(--accent-mark); }
.hvs-knob { position: absolute; top: 50%; left: calc(var(--x) * 100%); width: 10px; height: 10px; border-radius: 50%; background: var(--paper); box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 35%, transparent), 0 1px 2px color-mix(in srgb, var(--shadow) calc(12% * var(--shadow-k)), transparent); transform: translate(-50%, -50%); }
.hvs-comment { display: flex; flex-direction: column; gap: 3px; padding-left: 10px; box-shadow: inset 1px 0 0 var(--hv-edge); }
@container (min-width: 520px) { .hvs-images { gap: 12px; } .hvs-colors { grid-template-columns: repeat(6, minmax(0, 1fr)); } .hvs-themes { grid-template-columns: repeat(6, minmax(0, 1fr)); } .hvs-type { max-width: 440px; } .hvs-space, .hvs-tune, .hvs-sound, .hvs-consts { max-width: 560px; } }

/* the specimens at the pane's scale */
.hv-preview .hvs-chip { width: 28px; height: 28px; border-radius: 7px; }
.hv-preview .hvs-sw { grid-template-columns: 28px 1fr; column-gap: 9px; }
.hv-preview .hvs-theme { height: 64px; padding: 7px 8px; border-radius: 8px; }
.hv-preview .hvs-theme-aa { font-size: 18px; line-height: 20px; }
.hv-preview .hvs-theme-n { font-size: 10px; }
.hv-preview .hvs-type { gap: 14px; max-width: none; }
.hv-preview .hvs-wordmark { font-size: clamp(20px, 5.4cqi, 48px); }
.hv-preview .hvs-mark { height: 26px; }
.hv-preview .hvs-mat-aa { font-size: 40px; }
.hv-preview .hvs-materials { gap: 32px; }
.hv-preview .hvs-curve-box svg { width: 112px; height: 112px; }
.hv-preview .hvs-motion { gap: 32px; }
.hv-preview .hvs-icon { width: 28px; height: 28px; }
.hv-preview .hvs-icons { gap: 22px; }
.hv-preview .hvs-space-bar { height: 12px; }
.hv-preview .hvs-col { height: 96px; }
.hv-preview .hvs-lead { font-size: 14px; line-height: 19px; }
.hv-preview .hvs-rec-t { font-size: 14px; }
.hv-preview .hvs-rec-l { font-size: 14.5px; line-height: 19px; }
.hv-preview .hvs-flow { font-size: 16px; line-height: 21px; gap: 9px; }
.hv-preview .hvs-quote { font-size: 17px; line-height: 22px; }

@media (prefers-reduced-motion: reduce) { .hv-opt { transition: none; } }

/* UI type only (Ahmed, Nov 10): the viewer is UI, so it speaks in Inter Display (--ui). Shinka (--serif) stays
   only where it is the thing being previewed: the brand bio, the Body type row, the materials Aa. */
.hv-d-def { font: 400 14px/20px var(--ui); letter-spacing: -0.2px; }
.hvs-quote { font: 400 14px/19px var(--ui); letter-spacing: -0.2px; }
.hvs-quote.is-specimen { font: 400 15px/19.5px var(--serif); letter-spacing: var(--track); }
.hvs-rec-l { font: 400 13px/18px var(--ui); letter-spacing: -0.15px; }
.hvs-flow { font: 400 13px/18px var(--ui); letter-spacing: -0.15px; }

/* the third column: the term's records, the same rows as layers and terms (Ahmed, Nov 10) */
.hv-recs-none { margin: 0; padding: 4px 8px; font-size: 12.5px; line-height: 17px; color: var(--muted); }
.hv-d-head { display: flex; flex-direction: column; align-items: flex-start; gap: 6px; }
/* no specimen: the record takes the whole right side */
.hv-right.is-solo .hv-preview { display: none; }
@container (min-width: 800px) {
  .hv-right.is-solo { grid-template-columns: minmax(0, 1fr); }
  .hv-right.is-solo .hv-d-head { max-width: 56ch; }
}

/* the fourth column is one pane: a preview of the chosen record, its specimen under it (Ahmed, Nov 10) */
.hv-right { overflow-y: auto; }
.hv-preview { flex: none; background: none; box-shadow: none; }
.hv-p-body { padding: 4px 20px 22px; }
@container (min-width: 800px) {
  .hv-right, .hv-right.is-solo { display: flex; flex-direction: column; overflow-y: auto; }
  .hv-detail, .hv-preview { overflow: visible; }
  .hv-detail { padding: 20px 24px 16px; }
  .hv-detail .hv-d-head { max-width: 56ch; }
  .hv-preview { box-shadow: none; }
  .hv-p-body { padding: 8px 24px 28px; }
}
```


Source: `site/js/embeds/harness-viewer.js`, whole file

```js
// ::harness-viewer. Every part of a design harness, defined, laid out like the
// [product] app's harness viewer: three columns in one frame. Layers, then the
// layer's terms, then the term's records (the same list rows), then the record:
// its name, term and line, beside (where it is real) a
// specimen read off the site's own tokens.
// A column browser on the keyboard: Up/Down within a column, Right/Enter into the
// next, Left back. Under 600px it drills down one column at a time with a back control.
// All words come from js/glossary.js.
import { LAYERS, STRUCTURE, GLOSSARY } from '../glossary.js';
import { PALETTE } from '../theme.js';
import { ICONS, iconSrc, MARKS } from '../content.js';
import { audio, PALETTES } from '../audio.js';
import { WORD_FRAG, ITEM_FRAG, LINES_FRAG } from '../glsl.js';
import { APPS } from '../mcp.js';
import { RECORDS } from './harness-records.js';
import { svgIcon } from './harness-icons.js';

const CSS = 'css/embeds/harness-viewer.css';
const NARROW = matchMedia('(max-width: 599px)');
let uid = 0;

const h = (tag, attrs = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === 'class') e.className = v; else if (k === 'style') e.style.cssText = v; else e.setAttribute(k, v === true ? '' : v);
  }
  e.append(...kids.flat().filter(x => x != null));
  return e;
};

// ---------- specimens: only what the site really has, read at the moment it shows ----------
const hex = (c) => { const m = c.match(/[\d.]+/g); if (!m) return c; const k = c.startsWith('color(') ? 255 : 1; const [r, g, b] = m.slice(0, 3).map(v => Number(v) * k); const a = c.includes('/') || c.startsWith('rgba') ? Number(m[3]) : 1; if (a === 0) return 'none'; return '#' + [r, g, b].map(v => Math.round(v).toString(16).padStart(2, '0')).join(''); };
// resolve a token on a hidden probe (optionally under a theme) to what the browser computes
function probe(host, css, read, attrs = {}) {
  const p = h('div', { ...attrs, style: `position:absolute;visibility:hidden;pointer-events:none;${css}` });
  host.append(p);
  const v = read(getComputedStyle(p), p);
  p.remove();
  return v;
}
// a few of the site's own harness records: title and its line
// each term's records, read from the site's own harness (js/embeds/harness-records.js)
const R = (k) => RECORDS[k] || [];
const pick = (k, ...slugs) => R(k).filter(r => slugs.includes(r.slug));
const RECS = {
  brand: () => R('brand'), colors: () => R('colors'),
  typography: () => [...R('typography'), ...pick('packages', 'shinka', 'abc-favorit-arabic', 'abc-favorit-mono', 'kult-luxury')],
  icons: () => [...R('icons'), ...pick('packages', 'amicons')],
  spacing: () => R('spacing'), motion: () => R('motion'), sound: () => [...R('sound'), ...pick('memories', 'quiet-sound')],
  images: () => pick('memories', '16px-image-corners'), layout: () => pick('screens', 'reading'),
  materials: () => R('materials'), writing: () => [...R('writing'), ...pick('memories', 'no-em-dashes', 'every-word-is-mine')],
  themes: () => R('themes'), shaders: () => pick('packages', 'three-js'),
  generalists: () => R('agents').filter(r => !/^Specialist/.test(r.line)),
  specialists: () => R('agents').filter(r => /^Specialist/.test(r.line)),
  policies: () => R('policy'), skills: () => R('skills'), vocabulary: () => R('vocabulary'), memories: () => R('memories'),
  'components-item': () => R('components'), patterns: () => R('patterns'), screens: () => R('screens'),
  review: () => pick('skills', 'screenshot-review'),
};
const recsOf = (term) => RECS[term]?.() || [];
// a url() in a custom property resolves against the stylesheet, so pass it whole
const abs = (src) => new URL(src, document.baseURI).href;
const NOTES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'];
const noteName = (f) => { const n = Math.round(12 * Math.log2(f / 440)) + 69; return NOTES[n % 12] + (Math.floor(n / 12) - 1); };
const SPEC = {
  colors(host) {
    const roles = [['--paper', 'Paper'], ['--ink', 'Ink'], ['--muted', 'Muted'], ['--accent', 'Accent'], ['--accent-mark', 'Mark'], ['--accent-wash', 'Wash']];
    return h('div', { class: 'hvs-colors' }, roles.map(([v, name]) => {
      const c = probe(host, `background:var(${v})`, s => s.backgroundColor);
      return h('div', { class: 'hvs-sw' }, h('span', { class: 'hvs-chip', style: `background:${c}` }), h('span', { class: 'hvs-k' }, name), h('span', { class: 'hvs-v' }, hex(c)));
    }));
  },
  themes(host) {
    return h('div', { class: 'hvs-themes' }, PALETTE.map(p => {
      const attrs = { 'data-theme': p.theme, ...(p.accent ? { 'data-accent': p.accent } : {}) };
      const [paper, ink, acc] = probe(host, 'color:var(--ink);background:var(--paper);border-color:var(--accent-mark)', s => [s.backgroundColor, s.color, s.borderTopColor], attrs);
      return h('div', { class: 'hvs-theme', title: p.name, style: `background:${paper};color:${ink}` }, h('span', { class: 'hvs-theme-aa' }, 'Aa'), h('span', { class: 'hvs-theme-dot', style: `background:${acc}` }), h('span', { class: 'hvs-theme-n' }, p.name));
    }));
  },
  typography() {
    const art = document.querySelector('.col-body article');
    const rows = [
      ['Heading', art?.querySelector('h2'), 'var(--ui)'],
      ['Subhead', art?.querySelector('h3'), 'var(--ui)'],
      ['Body', art?.querySelector(':scope > p'), 'var(--serif)'],
      ['Interface', document.querySelector('#nav .item'), 'var(--ui)'],
    ];
    return h('div', { class: 'hvs-type' }, rows.filter(r => r[1]).map(([name, el]) => {
      const s = getComputedStyle(el);
      const size = Math.round(parseFloat(s.fontSize)), lh = Math.round(parseFloat(s.lineHeight) * 10) / 10;
      return h('div', { class: 'hvs-type-row' },
        h('span', { class: 'hvs-type-aa', style: `font-family:${s.fontFamily};font-size:${size}px;line-height:1;letter-spacing:${s.letterSpacing}` }, name),
        h('span', { class: 'hvs-v' }, `${size}/${lh}`));
    }));
  },
  spacing(host) {
    const steps = [['--stack', 'Stack'], ['--para', 'Paragraph'], ['--gap', 'Column gap']];
    return h('div', { class: 'hvs-space' }, steps.map(([v, name]) => {
      const px = probe(host, `width:var(${v})`, s => parseFloat(s.width));
      return h('div', { class: 'hvs-space-row' }, h('span', { class: 'hvs-space-bar', style: `width:${px}px` }), h('span', { class: 'hvs-k' }, name), h('span', { class: 'hvs-v' }, `${Math.round(px * 10) / 10}px`));
    }));
  },
  motion(host) {
    const curves = [['--ease-land', 'Land'], ['--ease-think', 'Think']];
    return h('div', { class: 'hvs-motion' }, curves.map(([v, name]) => {
      const raw = probe(host, `transition-timing-function:var(${v})`, s => s.transitionTimingFunction);
      const m = raw.match(/cubic-bezier\(([^)]+)\)/);
      if (!m) return null;
      const [x1, y1, x2, y2] = m[1].split(',').map(Number);
      const S = 56, P = (x, y) => `${(x * S).toFixed(1)} ${((1 - y) * S).toFixed(1)}`;
      const svg = `<svg viewBox="-2 -2 ${S + 4} ${S + 4}" width="${S + 4}" height="${S + 4}" aria-hidden="true"><path d="(icon path omitted: icon set is commercial)" class="hvs-axis"/><path d="(icon path omitted: icon set is commercial)" class="hvs-curve"/></svg>`;
      const fig = h('div', { class: 'hvs-curve-box' }); fig.innerHTML = svg;
      return h('div', { class: 'hvs-motion-c' }, fig, h('span', { class: 'hvs-k' }, name), h('span', { class: 'hvs-v' }, `${x1}, ${y1}, ${x2}, ${y2}`));
    }));
  },
  icons() {
    const names = ['copyText', 'discuss', 'copy', 'soundOn', 'soundOff', 'copied'];
    return h('div', { class: 'hvs-icons' }, names.map(k => {
      const v = ICONS[k]; if (!v) return null;
      const file = typeof v === 'string' ? v : v.line;
      return h('span', { class: 'hvs-icon', title: k, style: `--src:url("${abs(iconSrc(file))}")` });
    }));
  },

  // ---------- the rest: real records and live values from this site ----------
  brand() {
    const bio = document.querySelector('.bio')?.textContent?.trim();
    return h('div', { class: 'hvs-brand' },
      h('div', { class: 'hvs-wordmark', lang: 'en' }, 'salehdigital'),
      h('div', { class: 'hvs-marks' }, MARKS.map(m => h('span', { class: 'hvs-mark', role: 'img', 'aria-label': m.label, style: `--src:url("${abs(m.src)}");width:${m.w}px` }))),
      bio ? h('p', { class: 'hvs-quote is-specimen' }, bio) : null, // the site's bio, set as it is on the site
      null);
  },
  sound() {
    const rows = Object.entries(PALETTES).map(([id, p]) => {
      const notes = [...new Set(p.press.map(n => noteName(n[0])))].join(' ');
      const b = h('button', { type: 'button', class: 'hvs-play', 'aria-label': `Play ${p.label}` }, h('span', { class: 'hvs-play-ico', 'aria-hidden': 'true' }));
      b.addEventListener('click', () => audio.preview?.(id));
      return h('div', { class: 'hvs-sound-row' + (audio.feel === id ? ' is-current' : '') }, b, h('span', { class: 'hvs-k' }, p.label), h('span', { class: 'hvs-v' }, notes), h('span', { class: 'hvs-tag' }, audio.feel === id ? 'in use' : ''));
    });
    return h('div', { class: 'hvs-sound' }, rows);
  },
  images() {
    const shots = [['assets/media/harness/neo-app.webp', 'Neo app'], ['assets/media/harness/sf-home.webp', 'Home'], ['assets/media/harness/sf-phone.webp', 'Phone']];
    return h('div', { class: 'hvs-images' }, shots.map(([src, alt]) => h('img', { class: 'hvs-img', src, alt, loading: 'lazy', decoding: 'async' })));
  },
  layout(host) {
    const px = (v) => probe(host, `width:var(${v})`, s => parseFloat(s.width));
    const cols = [['Menu', px('--col-nav')], ['Pages', px('--col-sub')], ['Post', 540]];
    const gap = px('--gap'), total = cols.reduce((a, c) => a + c[1], 0) + gap * 2;
    return h('div', { class: 'hvs-stack' },
      h('div', { class: 'hvs-layout', style: `--gap:${(gap / total) * 100}%` }, cols.map(([n, w]) => h('div', { class: 'hvs-col', style: `flex:${w}` }, h('span', { class: 'hvs-k' }, n), h('span', { class: 'hvs-v' }, `${Math.round(w)}px`)))),
      h('p', { class: 'hvs-note' }, `${Math.round(gap)}px between columns. Below 900px they stack into one.`));
  },
  materials() {
    const s = 'Printed';
    return h('div', { class: 'hvs-stack' },
      h('div', { class: 'hvs-materials' },
        h('div', { class: 'hvs-mat' }, h('span', { class: 'hvs-mat-aa', style: 'filter:none' }, s), h('span', { class: 'hvs-v' }, 'no filter')),
        h('div', { class: 'hvs-mat' }, h('span', { class: 'hvs-mat-aa', style: 'filter:url(#ink-body)' }, s), h('span', { class: 'hvs-v' }, '#ink-body')),
        h('div', { class: 'hvs-mat' }, h('span', { class: 'hvs-mat-aa is-ui', style: 'filter:url(#ink-ui)' }, s), h('span', { class: 'hvs-v' }, '#ink-ui'))));
  },
  shaders() {
    const src = [WORD_FRAG, ITEM_FRAG, LINES_FRAG].join('\n');
    const out = [];
    for (const m of src.matchAll(/const (?:float|vec[234]) ([^;]+);[ \t]*(?:\/\/\s*([^\n]*))?/g)) {
      for (const part of m[1].split(/,(?![^(]*\))/)) { const [k, v] = part.split('=').map(x => x.trim()); if (k && v && k.length > 2) out.push([k, v, m[2] || '']); }
    }
    return h('div', { class: 'hvs-stack' },
      h('p', { class: 'hvs-lead' }, 'The wordmark and the footer are one GL field. Its constants, read from js/glsl.js:'),
      h('div', { class: 'hvs-consts' }, out.slice(0, 6).map(([k, v, c]) => h('div', { class: 'hvs-const' }, h('span', { class: 'hvs-v hvs-code' }, k), h('span', { class: 'hvs-v hvs-code is-val' }, v), c ? h('span', { class: 'hvs-c' }, c) : null))));
  },
  flows() {
    const a = APPS.claude;
    return h('div', { class: 'hvs-stack' },
      h('p', { class: 'hvs-lead' }, `Connect ${a.name} to this site’s MCP server (Settings, MCP):`),
      h('ol', { class: 'hvs-flow' }, a.steps().map(s => h('li', {}, s))),
      h('p', { class: 'hvs-note' }, `The same page has the flow for ${Object.values(APPS).filter(x => x !== a).map(x => x.name).join(' and ')}.`));
  },

  // Moves: one real instance of each, from how this site was made
  steer: () => h('div', { class: 'hvs-stack' },
    h('p', { class: 'hvs-lead' }, 'This viewer on a phone: one column at a time, or all three stacked?'),
    h('div', { class: 'hvs-options' }, [['Drill-down', true], ['Stacked', false]].map(([o, on]) => h('span', { class: 'hvs-option' + (on ? ' is-on' : '') }, o))),
    h('p', { class: 'hvs-note' }, 'Drill-down was picked: it is what you get here at 390px.')),
  concept: () => {
    const wren = RECORDS.agents.find(r => r.slug === 'wren');
    return h('div', { class: 'hvs-stack' },
      h('p', { class: 'hvs-lead' }, 'The Library, four directions side by side:'),
      h('div', { class: 'hvs-options' }, [['Spines', 'shipped'], ['Halftone shelf', 'too intense'], ['Specimens', ''], ['Lens', '']].map(([o, n]) => h('span', { class: 'hvs-option' + (n === 'shipped' ? ' is-on' : '') }, o, n ? h('span', { class: 'hvs-option-n' }, n) : null))),
      wren ? h('p', { class: 'hvs-note' }, `From ${wren.title}’s record (${wren.line.replace(/\.$/, '')}).`) : null);
  },
  tune(host) {
    const AX = [['--fnd-energy', 'Energy', 'Still', 'Lively'], ['--fnd-texture', 'Texture', 'Clean', 'Worn'], ['--fnd-focus', 'Focus', 'Dreamy', 'Focused'], ['--fnd-density', 'Density', 'Airy', 'Packed']];
    const cs = getComputedStyle(document.documentElement);
    return h('div', { class: 'hvs-stack' },
      h('p', { class: 'hvs-lead' }, 'The sliders this site is tuned on, at their values right now:'),
      h('div', { class: 'hvs-tune' }, AX.map(([v, n, lo, hi]) => {
        const x = Math.max(0, Math.min(1, parseFloat(cs.getPropertyValue(v)) || 0));
        return h('div', { class: 'hvs-tune-row' }, h('span', { class: 'hvs-k' }, n), h('span', { class: 'hvs-track', style: `--x:${x}` }, h('span', { class: 'hvs-knob' })), h('span', { class: 'hvs-v' }, `${lo} ${x.toFixed(2)} ${hi}`));
      })));
  },
  comment: () => h('div', { class: 'hvs-stack' },
    [['mcp page should be a chat-like experience where the user is met with a greeting and shown a few buttons for the respective MCP options.', 'Settings, MCP became a short conversation.'],
     ['make sure the harness viewer records is populated with example data based off this website', 'Every term here now shows something real from the site.']]
      .map(([q, a]) => h('div', { class: 'hvs-comment' }, h('p', { class: 'hvs-quote' }, `“${q}”`), h('p', { class: 'hvs-note' }, a)))),
  review: () => {
    return h('div', { class: 'hvs-stack' },
      h('p', { class: 'hvs-lead' }, 'This viewer’s own review:'),
      h('div', { class: 'hvs-options' }, ['Light', 'Dark', 'Marathon dark, red', '1440', '1100', '390'].map(o => h('span', { class: 'hvs-option' }, o))));
  },
};

export function mount(el) {
  if (!document.querySelector(`link[href="${CSS}"]`)) document.head.append(Object.assign(document.createElement('link'), { rel: 'stylesheet', href: CSS }));
  const id = `hv${++uid}`;
  const layerOf = Object.fromEntries(LAYERS.map(l => [l.slug, l]));
  const lastTerm = {}; // the term last chosen in each layer
  let layer = LAYERS[0].slug, term = STRUCTURE[layer][0], rec = null, depth = 0; // depth: which column shows when narrow

  el.classList.add('hv');
  el.innerHTML = '';
  const frame = h('div', { class: 'hv-frame', 'data-depth': '0' });
  const bar = h('div', { class: 'hv-bar' });
  const back = h('button', { type: 'button', class: 'hv-back' }, h('span', { class: 'hv-back-arrow', 'aria-hidden': 'true' }, '‹'), h('span', { class: 'hv-back-label' }));
  const crumb = h('span', { class: 'hv-crumb' });
  bar.append(back, crumb);
  const colL = h('div', { class: 'hv-col hv-layers', role: 'listbox', 'aria-label': 'Layers', id: `${id}-layers` });
  const colT = h('div', { class: 'hv-col hv-terms', role: 'listbox', id: `${id}-terms` });
  const colR = h('div', { class: 'hv-col hv-records', role: 'listbox', id: `${id}-records` });
  const lastRec = {}; // the record last chosen under each term
  // the fourth column: a preview of the chosen record, its specimen under it
  const colD = h('div', { class: 'hv-detail', role: 'region', 'aria-live': 'polite', tabindex: '-1', id: `${id}-detail` });
  const colP = h('div', { class: 'hv-preview' });
  const right = h('div', { class: 'hv-col hv-right' }, colD, colP);
  frame.append(bar, colL, colT, colR, right);
  el.append(frame);

  const ico = (key, size, cls) => { const s = h('span', { class: cls, 'aria-hidden': 'true' }); s.innerHTML = svgIcon(key, size); return s; };
  const opt = (cls, key, label, n, icon = key) => h('div', { role: 'option', class: `hv-opt ${cls}`, 'data-key': key, tabindex: '-1', 'aria-selected': 'false' },
    ico(icon, 16, 'hv-ico'), h('span', { class: 'hv-opt-label' }, label), n != null ? h('span', { class: 'hv-n', 'aria-hidden': 'true' }, String(n)) : null);

  colL.append(...LAYERS.map(L => opt('hv-layer', L.slug, L.title, STRUCTURE[L.slug].length)));

  const mark = (col, key) => col.querySelectorAll('.hv-opt').forEach(o => { const on = o.dataset.key === key; o.setAttribute('aria-selected', String(on)); o.tabIndex = on ? 0 : -1; o.classList.toggle('is-active', on); });

  function renderTerms() {
    const L = layerOf[layer];
    colT.setAttribute('aria-label', `${L.title} terms`);
    colT.replaceChildren(...STRUCTURE[layer].map(k => opt('hv-term', k, GLOSSARY[k].term, recsOf(k).length || null)));
    mark(colT, term);
  }
  function renderRecords() {
    const recs = recsOf(term);
    colR.setAttribute('aria-label', `${GLOSSARY[term].term} records`);
    colR.replaceChildren(...(recs.length
      ? recs.map(r => opt('hv-record', r.slug, r.title, null, term))
      : [h('p', { class: 'hv-recs-none' }, 'No records kept yet. This one lives in how the team works.')]));
    rec = recs.length ? (recs.find(r => r.slug === lastRec[term]) || recs[0]).slug : null;
    mark(colR, rec);
  }
  function renderDetail() {
    const g = GLOSSARY[term], L = layerOf[layer];
    const specKey = Object.prototype.hasOwnProperty.call(SPEC, term) ? term : null;
    const r = recsOf(term).find(x => x.slug === rec);
    colD.replaceChildren(r
      ? h('div', { class: 'hv-d-head' },
          h('h3', { class: 'hv-d-term' }, ico(term, 20, 'hv-d-ico'), h('span', {}, r.title)),
          h('p', { class: 'hv-d-layer' }, `${L.title} · ${g.term}`),
          h('p', { class: 'hv-d-def' }, r.line))
      : h('div', { class: 'hv-d-head' },
          h('h3', { class: 'hv-d-term' }, ico(term, 20, 'hv-d-ico'), h('span', {}, g.term)),
          h('p', { class: 'hv-d-layer' }, L.title),
          h('p', { class: 'hv-d-def' }, g.def)));
    right.classList.toggle('is-solo', !specKey);
    colP.hidden = !specKey;
    colP.replaceChildren(...(specKey ? [
      h('div', { class: 'hv-p-body' }, SPEC[specKey](el))] : []));
    colD.setAttribute('aria-label', r ? r.title : g.term);
  }
  function syncBar() {
    frame.dataset.depth = String(depth);
    back.hidden = depth === 0;
    const backTo = depth === 3 ? GLOSSARY[term].term : depth === 2 ? layerOf[layer].title : 'Layers';
    back.querySelector('.hv-back-label').textContent = backTo;
    back.setAttribute('aria-label', `Back to ${backTo}`);
    crumb.textContent = depth === 0 ? 'Design harness' : depth === 1 ? layerOf[layer].title : depth === 2 ? GLOSSARY[term].term : '';
  }

  function chooseLayer(k) {
    if (layer !== k) { layer = k; term = lastTerm[k] || STRUCTURE[k][0]; renderTerms(); renderRecords(); renderDetail(); }
    mark(colL, layer);
  }
  function chooseTerm(k) { term = k; lastTerm[layer] = k; mark(colT, term); renderRecords(); renderDetail(); }
  function chooseRec(k) { rec = k; lastRec[term] = k; mark(colR, rec); renderDetail(); }

  // focus moves by column; on a phone the column it lands in is the one shown
  const focusCol = (c) => {
    if (c === 2 && !rec && !NARROW.matches) c = 3; // nothing to list: straight to the term
    if (NARROW.matches) { depth = c; syncBar(); }
    const sel = (col) => col.querySelector('[aria-selected="true"]');
    const target = [sel(colL), sel(colT), sel(colR) || colR, colD][c];
    target?.focus({ preventScroll: true });
  };

  colL.addEventListener('click', (e) => { const o = e.target.closest('.hv-opt'); if (!o) return; chooseLayer(o.dataset.key); if (NARROW.matches) focusCol(1); });
  colT.addEventListener('click', (e) => { const o = e.target.closest('.hv-opt'); if (!o) return; chooseTerm(o.dataset.key); if (NARROW.matches) focusCol(rec ? 2 : 3); });
  colR.addEventListener('click', (e) => { const o = e.target.closest('.hv-opt'); if (!o) return; chooseRec(o.dataset.key); if (NARROW.matches) focusCol(3); });
  back.addEventListener('click', () => focusCol(depth === 3 && !rec ? 1 : depth - 1));

  const step = (list, cur, key) => {
    const i = list.indexOf(cur), n = list.length;
    const to = { ArrowDown: i + 1, ArrowUp: i - 1, Home: 0, End: n - 1 }[key];
    return to == null ? null : list[Math.max(0, Math.min(n - 1, to))];
  };
  colL.addEventListener('keydown', (e) => {
    const nx = step(LAYERS.map(l => l.slug), layer, e.key);
    if (nx) { e.preventDefault(); chooseLayer(nx); colL.querySelector(`[data-key="${nx}"]`).focus(); return; }
    if (e.key === 'ArrowRight' || e.key === 'Enter' || e.key === ' ') { e.preventDefault(); focusCol(1); }
  });
  colT.addEventListener('keydown', (e) => {
    const nx = step(STRUCTURE[layer], term, e.key);
    if (nx) { e.preventDefault(); chooseTerm(nx); colT.querySelector(`[data-key="${nx}"]`).focus(); return; }
    if (e.key === 'ArrowRight' || e.key === 'Enter' || e.key === ' ') { e.preventDefault(); focusCol(rec ? 2 : 3); }
    else if (e.key === 'ArrowLeft' || (e.key === 'Escape' && NARROW.matches)) { e.preventDefault(); focusCol(0); }
  });
  colR.addEventListener('keydown', (e) => {
    const nx = rec && step(recsOf(term).map(r => r.slug), rec, e.key);
    if (nx) { e.preventDefault(); chooseRec(nx); colR.querySelector(`[data-key="${nx}"]`).focus(); return; }
    if (e.key === 'ArrowRight' || e.key === 'Enter' || e.key === ' ') { e.preventDefault(); focusCol(3); }
    else if (e.key === 'ArrowLeft' || (e.key === 'Escape' && NARROW.matches)) { e.preventDefault(); focusCol(1); }
  });
  colD.addEventListener('keydown', (e) => {
    if (e.target !== colD && e.key !== 'Escape') return; // the link keeps its own keys
    if (e.key === 'ArrowLeft' || e.key === 'Escape') { e.preventDefault(); focusCol(rec ? 2 : 1); }
  });

  // the specimens read the theme: redraw when it changes
  const onTheme = () => requestAnimationFrame(renderDetail);
  addEventListener('theme:change', onTheme);
  const onNarrow = () => { depth = 0; syncBar(); };
  NARROW.addEventListener('change', onNarrow);

  chooseLayer(layer); renderTerms(); renderRecords(); renderDetail(); mark(colL, layer); syncBar();
  return () => { removeEventListener('theme:change', onTheme); NARROW.removeEventListener('change', onNarrow); };
}
```


## The records it lists

Source: `site/js/embeds/harness-records.js`, whole file

```js
// Generated by js/embeds/harness-records.py from content/harness. Do not edit:
// edit the records, then run python3 js/embeds/harness-records.py
export const RECORDS = {
 "agents": [
  {
   "slug": "web",
   "title": "Web",
   "line": "Lead. Multiplayer: talks with Ahmed and hands work to the specialists."
  },
  {
   "slug": "wren",
   "title": "Wren",
   "line": "Specialist: site design."
  },
  {
   "slug": "dev",
   "title": "Dev",
   "line": "Specialist: front-end build."
  },
  {
   "slug": "ada",
   "title": "Ada",
   "line": "Specialist: performance and accessibility."
  }
 ],
 "policy": [
  {
   "slug": "made-live",
   "title": "Made live",
   "line": "Nothing is a recording: the sound and the motion are generated as you go."
  },
  {
   "slug": "little-first",
   "title": "Little first",
   "line": "Show little at first, and more with attention."
  },
  {
   "slug": "detail",
   "title": "Detail",
   "line": "Detail is the point."
  }
 ],
 "skills": [
  {
   "slug": "figma-import",
   "title": "Figma import",
   "line": "Reading a Figma file as the source of truth and carrying its values over, not redrawing them."
  },
  {
   "slug": "catalogue-lookup",
   "title": "Catalogue lookup",
   "line": "Finding a book's real details in a public catalogue instead of writing them."
  },
  {
   "slug": "screenshot-review",
   "title": "Screenshot review",
   "line": "Looking at the real page before calling it done."
  },
  {
   "slug": "theme-tokens",
   "title": "Theme tokens",
   "line": "One set of semantic colours, swapped by an attribute."
  },
  {
   "slug": "generative-sound",
   "title": "Generative sound",
   "line": "Every sound is synthesised in the browser with Web Audio, nothing is a recording, and nothing plays before a gesture."
  },
  {
   "slug": "sdf-rendering",
   "title": "SDF rendering",
   "line": "Turning type into signed distance fields so it can melt, boil and resolve while staying real text."
  },
  {
   "slug": "cms-records",
   "title": "CMS records",
   "line": "Each list entry is its own file: content/<section>/<page>/<record>.md, with title, slug, status (backlog, draft or published), order, description, chips, media, created and updated."
  }
 ],
 "vocabulary": [
  {
   "slug": "emergence",
   "title": "Emergence",
   "line": "The site's word for content unfolding with attention."
  },
  {
   "slug": "thinking",
   "title": "Thinking",
   "line": "The beat in the middle of every change, when the site seems to consider before it lands."
  },
  {
   "slug": "resolve",
   "title": "Resolve",
   "line": "A change of state that passes through a distance-field morph and lands sharp."
  },
  {
   "slug": "spine",
   "title": "Spine",
   "line": "A book stood spine-out, the Library's way of showing a book."
  },
  {
   "slug": "glyph-matrix",
   "title": "Glyph matrix",
   "line": "An image drawn as type: each sketch is a grid of cells that sample its luminance into SDF glyphs from the ramp ' .:-=+*#%@', set in ABC Favorit Mono and slowly re-sampled, as if thinking."
  },
  {
   "slug": "felt",
   "title": "Felt",
   "line": "The default touch palette: soft sines, swelled in with no click, half dry and half in the room."
  },
  {
   "slug": "marathon",
   "title": "Marathon",
   "line": "The acid graphic theme family: one bright accent on dark or cool paper."
  }
 ],
 "memories": [
  {
   "slug": "every-word-is-mine",
   "title": "Every word is mine",
   "line": "The site's words are Ahmed's."
  },
  {
   "slug": "no-em-dashes",
   "title": "No em dashes",
   "line": "No em dashes anywhere: commas, colons, full stops or brackets instead."
  },
  {
   "slug": "drafts-stay-private",
   "title": "Drafts stay private",
   "line": "Drafts never show on the site, locally included."
  },
  {
   "slug": "quiet-sound",
   "title": "Quiet sound",
   "line": "Sound stays ambient and low."
  },
  {
   "slug": "no-modals-for-books",
   "title": "No modals for books",
   "line": "Books open in place, never in a modal."
  },
  {
   "slug": "single-green-check",
   "title": "Single green check",
   "line": "Success is one check that turns green, not a double check."
  },
  {
   "slug": "16px-image-corners",
   "title": "16px image corners",
   "line": "Images in grids get 16px corners."
  }
 ],
 "writing": [
  {
   "slug": "my-words",
   "title": "My words",
   "line": "Every word on the site is written by me."
  },
  {
   "slug": "punctuation",
   "title": "Punctuation",
   "line": "Commas, colons and full stops."
  }
 ],
 "brand": [
  {
   "slug": "wordmark",
   "title": "Wordmark",
   "line": "Comes alive as the site opens: still letters, then dot matrix, ripples and traces."
  }
 ],
 "components": [
  {
   "slug": "menu-item",
   "title": "Menu item",
   "line": "Rests out of focus, and sharpens when you are on it or close to it."
  },
  {
   "slug": "highlighted-word",
   "title": "Highlighted word",
   "line": "A warm word in the text that opens something hidden."
  },
  {
   "slug": "glow",
   "title": "Glow",
   "line": "The marker for anything new: a small amber light with a halo."
  },
  {
   "slug": "chip",
   "title": "Chip",
   "line": "A small value tag: 22px tall, 8px side padding, 6px radius, ABC Favorit Arabic 12/16 at -0.2px with tabular figures."
  },
  {
   "slug": "swatch",
   "title": "Swatch",
   "line": "A colour sample."
  },
  {
   "slug": "dot-matrix-button",
   "title": "Dot-matrix button",
   "line": "An icon drawn as a 7 by 7 grid of dots, 4px apart in a 28px box on a 40px button with a 10px radius."
  },
  {
   "slug": "icon-button",
   "title": "Icon button",
   "line": "A 16px icon as a mask in currentColor, on a 16px row with no frame."
  },
  {
   "slug": "switch",
   "title": "Switch",
   "line": "An on or off control with its label beside it."
  },
  {
   "slug": "spine",
   "title": "Spine",
   "line": "A book standing spine-out, drawn in three.js over a DOM slot that keeps focus and clicks."
  },
  {
   "slug": "cover",
   "title": "Cover",
   "line": "A book's front, shown at its real proportions."
  }
 ],
 "patterns": [
  {
   "slug": "navigation",
   "title": "Navigation",
   "line": "Two menu columns of Menu items: sections, then the pages of the chosen section."
  },
  {
   "slug": "record",
   "title": "Record",
   "line": "One item on a page: a 16px line icon inline before the title, no tile; the title in ABC Favorit Arabic 16/20; the description in Shinka at 72% ink; then Chips."
  },
  {
   "slug": "carousel",
   "title": "Carousel",
   "line": "A full-screen viewer: the site blurred behind it (28px blur, saturate 1.15) under a paper wash at 52%."
  },
  {
   "slug": "bookshelf",
   "title": "Bookshelf",
   "line": "Spines standing on shelves, in order."
  },
  {
   "slug": "coffee-table",
   "title": "Coffee table",
   "line": "The books lie on a tabletop seen from above, in three.js."
  },
  {
   "slug": "settings-row",
   "title": "Settings row",
   "line": "A row in Settings: a control, then its label in ABC Favorit Arabic 16/20, 10px apart and at least 24px tall."
  },
  {
   "slug": "post-actions",
   "title": "Post actions",
   "line": "A row of Icon buttons under the post: Copy link and Copy text."
  },
  {
   "slug": "footer",
   "title": "Footer",
   "line": "Three pieces in one field: the bio, four marks and the Wordmark."
  }
 ],
 "screens": [
  {
   "slug": "reading",
   "title": "Reading",
   "line": "Menu, pages, the post and its actions, side by side."
  },
  {
   "slug": "footer",
   "title": "Footer",
   "line": "A line about me, four marks, and the wordmark across the bottom."
  }
 ],
 "materials": [
  {
   "slug": "texture",
   "title": "Texture",
   "line": "A fine grain over everything, and ink that bleeds a little into the paper, so the type feels printed."
  }
 ],
 "sound": [
  {
   "slug": "sound",
   "title": "Sound",
   "line": "Ambient and quiet, in D minor. Nothing is struck hard, and page changes are silent."
  }
 ],
 "motion": [
  {
   "slug": "motion",
   "title": "Motion",
   "line": "One curve, called think: quick off the mark, lingering through the middle, gentle to land."
  },
  {
   "slug": "emergence",
   "title": "Emergence",
   "line": "The site opens up over six levels as your interest grows."
  },
  {
   "slug": "hidden-extras",
   "title": "Hidden extras",
   "line": "Secrets found by doing something, not by looking for them."
  },
  {
   "slug": "resolve",
   "title": "Resolve",
   "line": "Every change morphs through a distance field, like a thought settling."
  },
  {
   "slug": "streaming",
   "title": "Streaming",
   "line": "A post writes itself in as you arrive, word by word, behind a small caret."
  }
 ],
 "themes": [
  {
   "slug": "light",
   "title": "Light",
   "line": "The default. Follows the device setting."
  },
  {
   "slug": "dark",
   "title": "Dark",
   "line": "Follows the device setting."
  },
  {
   "slug": "marathon-dark",
   "title": "Marathon dark",
   "line": "The footer takes the accent."
  },
  {
   "slug": "marathon-light",
   "title": "Marathon light",
   "line": "The footer takes the accent, deepened."
  },
  {
   "slug": "marathon-accents",
   "title": "Marathon accents",
   "line": "One accent per Marathon theme."
  }
 ],
 "colors": [
  {
   "slug": "colour",
   "title": "Colour",
   "line": "Ink on paper, and nothing else. Only something new is allowed to glow."
  }
 ],
 "typography": [
  {
   "slug": "type",
   "title": "Type",
   "line": "Shinka for reading, ABC Favorit Arabic for everything around it, and Kult Luxury, drawn as a shader, for the wordmark."
  }
 ],
 "icons": [
  {
   "slug": "icons",
   "title": "Icons",
   "line": "Change shape by dissolving through a dot matrix."
  }
 ],
 "spacing": [
  {
   "slug": "spacing",
   "title": "Spacing",
   "line": "Each column is exactly as wide as its longest title, so the gaps between menu, pages and post stay even."
  }
 ],
 "packages": [
  {
   "slug": "three-js",
   "title": "three.js",
   "line": "SDF wordmark, grain, text morphs and the gallery grids."
  },
  {
   "slug": "tiptap",
   "title": "Tiptap",
   "line": "The CMS writing editor."
  },
  {
   "slug": "python-standard-library",
   "title": "Python standard library",
   "line": "The CMS server: http.server, json, pathlib, threading."
  },
  {
   "slug": "sips",
   "title": "sips",
   "line": "Resizes uploaded images in the CMS."
  },
  {
   "slug": "neo-kit",
   "title": "Neo kit",
   "line": "The CMS admin interface."
  },
  {
   "slug": "abc-favorit-arabic",
   "title": "ABC Favorit Arabic",
   "line": "Interface type."
  },
  {
   "slug": "abc-favorit-mono",
   "title": "ABC Favorit Mono",
   "line": "Glyph matrix and captions."
  },
  {
   "slug": "shinka",
   "title": "Shinka",
   "line": "Body type."
  },
  {
   "slug": "kult-luxury",
   "title": "Kult Luxury",
   "line": "The salehdigital wordmark."
  },
  {
   "slug": "amicons",
   "title": "Amicons",
   "line": "Interface icons."
  },
  {
   "slug": "open-library",
   "title": "Open Library",
   "line": "Book covers and descriptions."
  }
 ]
};
```


Rendered DOM on the live site at 1440 (captured 2026-11-11):

```html
<div class="embed embed-harness-viewer hv" data-embed="harness-viewer" data-stream-skip="">
 <div class="hv-frame" data-depth="0">
  <div class="hv-bar">
   <button aria-label="Back to Layers" class="hv-back" hidden="" type="button">
    <span aria-hidden="true" class="hv-back-arrow">
     ‹
    </span>
    <span class="hv-back-label">
     Layers
    </span>
   </button>
   <span class="hv-crumb">
    Design harness
   </span>
  </div>
  <div aria-label="Layers" class="hv-col hv-layers" id="hv1-layers" role="listbox">
   <div aria-selected="true" class="hv-opt hv-layer is-active" data-key="foundations" role="option" tabindex="0">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Foundations
    </span>
    <span aria-hidden="true" class="hv-n">
     13
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-layer" data-key="intelligence" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Intelligence
    </span>
    <span aria-hidden="true" class="hv-n">
     6
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-layer" data-key="components" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Components
    </span>
    <span aria-hidden="true" class="hv-n">
     4
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-layer" data-key="moves" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Moves
    </span>
    <span aria-hidden="true" class="hv-n">
     5
    </span>
   </div>
  </div>
  <div aria-label="Foundations terms" class="hv-col hv-terms" id="hv1-terms" role="listbox">
   <div aria-selected="true" class="hv-opt hv-term is-active" data-key="brand" role="option" tabindex="0">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Brand
    </span>
    <span aria-hidden="true" class="hv-n">
     1
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-term" data-key="colors" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Colors
    </span>
    <span aria-hidden="true" class="hv-n">
     1
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-term" data-key="typography" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Typography
    </span>
    <span aria-hidden="true" class="hv-n">
     5
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-term" data-key="icons" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Icons
    </span>
    <span aria-hidden="true" class="hv-n">
     2
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-term" data-key="spacing" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Spacing
    </span>
    <span aria-hidden="true" class="hv-n">
     1
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-term" data-key="motion" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Motion
    </span>
    <span aria-hidden="true" class="hv-n">
     5
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-term" data-key="sound" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Sound
    </span>
    <span aria-hidden="true" class="hv-n">
     2
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-term" data-key="images" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Images
    </span>
    <span aria-hidden="true" class="hv-n">
     1
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-term" data-key="layout" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Layout
    </span>
    <span aria-hidden="true" class="hv-n">
     1
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-term" data-key="materials" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Materials
    </span>
    <span aria-hidden="true" class="hv-n">
     1
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-term" data-key="writing" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Writing
    </span>
    <span aria-hidden="true" class="hv-n">
     4
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-term" data-key="themes" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Themes
    </span>
    <span aria-hidden="true" class="hv-n">
     5
    </span>
   </div>
   <div aria-selected="false" class="hv-opt hv-term" data-key="shaders" role="option" tabindex="-1">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Shaders
    </span>
    <span aria-hidden="true" class="hv-n">
     1
    </span>
   </div>
  </div>
  <div aria-label="Brand records" class="hv-col hv-records" id="hv1-records" role="listbox">
   <div aria-selected="true" class="hv-opt hv-record is-active" data-key="wordmark" role="option" tabindex="0">
    <span aria-hidden="true" class="hv-ico">
     <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
      <path d="(icon path omitted)">
      </path>
     </svg>
    </span>
    <span class="hv-opt-label">
     Wordmark
    </span>
<!-- … truncated here; the rest repeats the same structure -->
```
