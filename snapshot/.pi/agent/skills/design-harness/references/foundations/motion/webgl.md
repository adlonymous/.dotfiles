---
title: WebGL
slug: webgl
status: published
description: "One WebGL2 canvas (three.js 0.186.1) draws the live wordmark, the footer pass, every morph and the orbs, on SDF fields built by jump flood, within strict budgets. Hub for the renderer, shader and wordmark records."
chips:
  - Motion
  - WebGL
  - Wordmark
  - Shader
created: 2026-11-11T16:03:37Z
updated: 2026-11-11T16:36:22Z
---

`js/gl.js` creates **one** WebGL2 context for the whole site, on `<canvas id="gl">`. It draws the live wordmark, the footer above it (bio, basmala, the two dot strips and the four marks), every resolve morph, and the yellow orbs. The paper grain is not GL: it is a CSS layer at z-index 11 ([texture](../materials/texture.md)). The favicon is not GL either: it is an SVG dot matrix redrawn per theme ([themes](../themes.md)). The gallery grids (Library, Experiments, Coffee table) each get their own canvas under the page (`canvas.grid-gl`, see the templates).

Everything needed to reproduce the GL layer is in four records. Each one quotes the site's source verbatim, whole files where it matters:

| Record | What it holds |
|---|---|
| [WebGL renderer](webgl-renderer.md) | `js/gl.js`, the whole file: context, render targets, the jump-flood SDF builder, the field cache and budgets, the mesh pool, morphs, the wordmark and footer uniforms, orbs, pointer, the frame loop, visibility pausing, DPR and resize, context loss |
| [WebGL shaders](webgl-shaders.md) | `js/glsl.js`, the whole file (every vertex and fragment shader, GLSL verbatim), and a table of every uniform with its value or how it animates |
| [WebGL wordmark](webgl-wordmark.md) | how `js/app.js` drives it: boot order, fitting the wordmark, the per-glyph fields, the Arabic hold field, baking the footer, the pointer, hold and letter hooks (sound and haptics), resize, the no-WebGL and `?lite` fallbacks; plus `js/raster.js`, `js/footdots.js`, the CSS and the HTML |
| [Orbs](orbs.md) | `js/orb.js` (the orb look and uniforms) and the orb review stage |

## At a glance

- **Library:** three.js 0.186.1 from jsDelivr through an import map, in `<head>` before `js/app.js`:

  ```html
  <script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.186.1/examples/jsm/"}}</script>
  ```

- **Canvas:** `#gl { position: fixed; inset: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 10; }`, hidden in print.
- **Renderer:** `THREE.WebGLRenderer({ alpha: true, antialias: false, depth: false, stencil: false, premultipliedAlpha: true, powerPreference: 'default', failIfMajorPerformanceCaveat: true })`, clear colour transparent. It requires **WebGL2** and **`EXT_color_buffer_float`** (the SDF render targets are half float). If either is missing, or the constructor throws, `createGL` returns `null`.
- **When it starts:** in `boot()`, after `document.fonts.load` of Inter Display, Shinka, Kult Luxury and Kufigraph and `document.fonts.ready`, straight after `fitColumns()` and `startGrain()`. There is no idle or first-touch deferral in the current site: `js/app.js` imports `js/gl.js` statically. Until then the SVG wordmark and the DOM footer show.
- **Shapes:** every shape is a signed distance field built on the GPU by jump flood (JFA) from a 2D canvas raster of the real DOM text or mask image (`js/raster.js`), at the element's computed font.
- **DPR:** `min(devicePixelRatio, 1.5)`; `1.2` while scrolling (restored 150ms after the last scroll event).
- **Loop:** busy → every rAF. Idle but alive (the wordmark or an orb on screen, someone attending) → a timer at `MOTION.idleFps` 15 fps (`MOTION.orbFps` 30 with orbs visible), then one rAF. Otherwise it sleeps until an event wakes it.
- **Pausing:** stops when the tab is hidden (`visibilitychange`, and every running morph lands at once), when the canvas leaves the viewport (`IntersectionObserver`), and when nothing moves. With no focus, "someone attending" means a pointer move in the last 4s.
- **Theme:** `onTheme` re-tints `uInk`, `uSwell`, `uFoot`, and the orb `cYellow`/`cRim` (Marathon: `glow`/`accent-mark`), live.
- **Reduced motion:** no breathing, no cursor warp, no ripples, no flow, no thinking swell, no orb bloom or lean; the Arabic hold mix takes 120ms. See the table in [WebGL wordmark](webgl-wordmark.md).
- **No WebGL:** `html` never gets `.gl`. The SVG `<text>` wordmark paints in `--foot` through `#ink-ui`, the footer shows its DOM with the SVG ink filters, the dot strips draw on their own 2D canvases (`js/footdots.js`), morphs crossfade. A lost context drops back to the same DOM; one restore is allowed, a second loss stays on the DOM.
- **`?lite`:** a debug fallback. GL still draws the wordmark's edge and breathing, but no life stages, no traces, no GL footer, and no grain.

## Budgets

Source: `site/js/gl.js`, lines 17 to 35

```js
const MAXL = 64;
const MB = 1 << 20;

export const BUDGET = {
  dpr: 1.5,               // the canvas never draws above 1.5 device px per CSS px
  dprScrolling: 1.2,      // reduce DPR while scrolling to improve performance
  fieldScale: 1,          // body and wordmark fields: texels per CSS px (the field is smooth)
  fieldMaxPx: 1.5e6,      // one field, texels (scale drops to fit)
  dispMaxPx: 3e6,         // one display raster, texels
  jfaMaxSide: 4096,       // jump-flood ping-pong pool, per side
  jfaMaxPx: 2.4e6,        // ...and its area: 2 x RGBA16F = 38MB at most
  texBytes: 64 * MB,      // every field and display raster alive at once
  cacheBytes: 16 * MB,    // the item field cache, by bytes...
  cacheEntries: 40,       // ...and by count
  buildsPerFrame: 8,      // jump-flood builds in one frame...
  buildPxPerFrame: 2.4e6, // ...and texels; past either, a morph is a crossfade
  maxMorphs: 40,          // morphs drawing at once
  poolIdleMs: 15000       // the pool and the scratch canvas are freed after this long unused
};
```

## Known live behaviour

### Mobile overflow (fixed on 2026-11-11)

Before that day's site sync, at 390 wide the live footer showed only "salehdigi", with and without GL. The cause was in the fonts, not the shader: Kult Luxury was `font-display: optional`. `boot()` `document.fonts.load`s it, so the canvas measure in `fitWordmark` used Kult's metrics, while the DOM `<text>` had already fallen back to a wider serif. The sync made Kult Luxury (and Kufigraph) `font-display: block`. Re-checked live at 390 × 844 after the sync (headless Chrome, 2026-11-11): the `<text>` is `x 6.89, y 28.79, font-size 29.702` and the whole word fits, with `.gl.gl-foot` on.

A rebuild without the licensed Kult file is in the same position the site was in: the canvas measures whatever face "Kult Luxury" resolves to. Fit only after the face has loaded (`document.fonts.load`, then `fitWordmark`), and make the fallback the face both the DOM and the canvas use (see the rebuild's `@font-face` fallback in `examples/saleh-digital-rebuild`).

### Life is 0 on the live site

Emergence is switched off ([emergence](emergence.md)), so `E.life()` is 0 and only stage 0 shows: the static edge noise, the grain, the breathing and the cursor warp. `--fnd-life` above 0 on `:root` forces a level (`lifeValue()` in [WebGL wordmark](webgl-wordmark.md)), which is how the stages can be shown.
