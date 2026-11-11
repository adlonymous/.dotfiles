---
title: WebGL renderer
slug: webgl-renderer
status: published
description: "js/gl.js whole: the one WebGL2 context, half-float jump-flood SDFs, the field cache and GPU budgets, the mesh pool, morphs, the wordmark and footer, orbs, the frame loop, visibility pausing, DPR and context loss."
chips:
  - Motion
  - WebGL
  - Renderer
created: 2026-11-11T16:28:25Z
updated: 2026-11-11T16:36:22Z
---

`createGL(canvas, hooks)` in `js/gl.js` is the whole GL layer. It returns `null` when WebGL2 or `EXT_color_buffer_float` is missing; otherwise an API object (end of the file). This record walks through it, then quotes the file whole.

## Setup

- **Context:** `alpha: true, antialias: false, depth: false, stencil: false, premultipliedAlpha: true, powerPreference: 'default', failIfMajorPerformanceCaveat: true`. `setClearColor(0x000000, 0)`, `autoClear = true`. `maxTextureSize` caps every field.
- **Camera:** `OrthographicCamera(0, 1, 0, -1, -10, 10)`; `resize()` sets `right = W`, `bottom = -H`, so one unit is one CSS px with y down (meshes are placed at `-(y)`). `W = documentElement.clientWidth`, `H = innerHeight`. `renderer.setSize(W, H, false)` and the canvas style is set to the same px.
- **Geometry:** one shared `PlaneGeometry(1, 1)`; every mesh is a quad scaled to its box (`placeMesh`), skipped when off screen. Full-screen passes (the JFA) use a separate `PlaneGeometry(2, 2)` with `FS_VERT`.
- **Shared colour uniforms:** `INK`, `SWELL`, `FOOT_INK` are single `Vector3`s shared by every material; `onTheme` sets them from `readColors()` ([themes](../themes.md)).

## Textures and render targets

| What | Format | Filter | Size |
|---|---|---|---|
| Mask raster (2D canvas → `CanvasTexture`) | RGBA8, `flipY = false`, `NoColorSpace` | Nearest | box × scale |
| JFA ping-pong pair (`pool`) | RGBA **HalfFloat** | Nearest | grows in steps of 128, ≤ `jfaMaxSide` 4096 per side, ≤ `jfaMaxPx` 2.4M texels; freed after `poolIdleMs` 15s unused |
| SDF output field | **Red HalfFloat** (`RedFormat`) | Linear | box × scale; 2 bytes/texel in the ledger |
| Display raster (the element as the DOM paints it) | RGBA8 | Linear | box × `dScale` (≤ dpr) |
| `blank` | 1×1 RGBA8 `DataTexture` | | stands in for any missing texture |

## The SDF (jump flood)

`buildSDF(mask, scale)`: upload the mask; `JFA_SEED` writes, per texel, the offset to its nearest inside (RG) and outside (BA) pixel; then `JFA_STEP` passes at `step = 2^ceil(log2(max(w, h))) / 2`, halving to 1, plus one extra pass at 1 ("JFA+1 cleans up the few wrong seeds"); `JFA_FINAL` turns nearest-seed distances into a signed distance in CSS px (`invScale = 1/scale`) in one red channel. Every build is counted against the per-frame budget (`buildsPerFrame` 8, `buildPxPerFrame` 2.4M; the first build in a frame is always allowed).

`fitScale(box, want, maxPx)` = `min(want, 4096/w, 4096/h, maxTex/w, maxTex/h, sqrt(maxPx/(w·h)))`, floored to 1/64, at least 0.05.

## Fields, cache and memory

- `fieldFor(snap, {pad, cacheable, scale})` builds or reuses the SDF for a snapshot (keyed by `snap.sig#pad#scale`) plus a fresh display raster. Over budget it returns `FAIL` and the caller crossfades instead.
- Cache: LRU `Map`, trimmed to `cacheEntries` 40 and `cacheBytes` 16MB; total live texture bytes ≤ `texBytes` 64MB.
- Item pad: `ceil(14 + extra + 3·blur)`. Body pad: `ceil(16 + amp·2)`. Wordmark pad: 24. Footer pad: 12.
- Mesh pool: one pool per fragment source, up to 12 meshes each, so programs are never recompiled; pooled meshes hold only `blank` textures.

## Morphs

- `morphItem` (one element, `ITEM_FRAG`, render order 1): `grain = 0.3 + 0.5·texture`, `aa = 0.6/dpr`, `shift` when the same text moved, icon toggles add `dots`/`pitch` (default 1.75)/`blurPeak`. At most `maxMorphs` 40 at once.
- `morphBody` (a whole post body, `LINES_FRAG`): line bounds of up to `MAXL` 64 lines per side; `stagger = MOTION.staggerMs`, `inDelay = dur · MOTION.bodyInDelay` (0.2); `blurMax = 2.6 + 2·energy`. Total = `max(dur·0.5 + nA·stagger·0.6, inDelay + dur + (nB−1)·stagger)`.
- `run(group)` starts a group and returns what it could not afford; it raises the thinking target (hover .25, emerge `EMERGE.think`, clock .3, anything else 1). Each frame sets `raw`, `t = think(raw)` and `time`; `REVIEW.freeze` holds frames for the review aid. The newest group emits `resolve:progress`; a finished group emits `resolve:end`.

## Wordmark and footer

- `setWordmark(snap, anchor, extra)`: one field for the word (pad 24, scale `min(fieldScale 1, dpr)`), offset from its anchor (the SVG) so it follows scroll. `extra` carries the even/odd per-glyph snapshots, glyph centres and the cap height; those fields are built lazily through `wordQueue` (one per frame within budget) once life × 5 passes 3.02.
- `setWordmarkAlt(snap)` + `wordmarkTo(v, dur)`: the hold secret's Arabic field, mixed along `think()`; 120ms under reduced motion.
- `setHold(v)`: while held, `thinkTarget ≥ 0.4 + 1.6·hold`.
- `setLife(v)`: eases `lifeShown` to the target over `LIFE.settleMs` 1800 (exponential, τ = 600ms); a rise first swells (`thinkTarget ≥ LIFE.swell` 1.4).
- `setTraces(ids)`: up to four yellow traces at `LIFE.traceLetters` (warm 9, hold 0, harness 4, night 7), radius `cap · 0.32`; `hold` also shows the Arabic ghost at `ghostAlpha` .16. None under `?lite`.
- `setFooter(snap, anchor, marks, bas, dots)`: the bio, basmala, foot links, marks and dot strips in one field, scale `min(FOOT.scale 2, dpr·2)`, drawn in the wordmark's pass. Up to two dot strips; up to 16 blobs (`n = clamp(round(w/140), 2, 8)` per strip), animated on the CPU with the same formulas as `js/footdots.js`. Each mark has a hover focus eased with τ 90ms (`markHover(i, on)`).

## The frame loop and pausing

- `wake()` requests one rAF (never two chains). `sleep(ms)` sets a timer, then one rAF.
- Busy when: morphs are running, `needs`, a scroll in the last 250ms, an orb blooming/melting/easing hover, or the wordmark is on screen and (a pointer move in the last 900ms, thinking > .01, the Arabic mix running, a hold, life settling, a field queued, a mark easing), or the word's visibility changed.
- Ambient (idle but alive): not reduced motion, `attended(t)` (tab visible, canvas visible, and focused or a pointer move in the last 4000ms), and the word or an orb on screen → redraw at 15 fps (30 with orbs).
- Hidden tab: `stopLoop()` and `finishAll()` (every morph lands, its DOM text returns). Visible again: `needs = true; wake()`.
- Off screen: an `IntersectionObserver` on the canvas stops the loop and wakes it again.

## Per frame (wordmark)

`thinkTarget *= 0.5^(dt/450)`; `thinking` eases to it (`1 − 0.001^(dt/1000)`); `mouseOn` eases to `mouseTarget` (`1 − 0.02^(dt/1000)`). Stages `s1..s5 = smoothstep(k−1, k, life·5)` (s4 waits for the per-glyph fields). `bar = barPhase(t)` (92 bpm, 4/4), `beat = (bar·4) mod 1`. `flowT += dt · LIFE.flow` (6 px/s). Stage sizes scale with `capK = min(1, cap/80)`: `kPitch = max(1.1, 2.4·capK)`, `kSpacing = max(4, 9·capK)`, `kReach = max(12, 46·capK)`, `kBoil = 0.7·max(.35, capK)`. `breath = MOTION.breathPx(energy) = 0.3 + 1.2·energy`; `grain = 0.04 + 0.22·texture`; `ink = 0.05 + 0.3·texture`; `mouseR = clamp(W·0.06, 60, 140)`. `reach` bounds how far any edge can move from the base field, so the shader can early-out.

## Pointer

`pointermove` (not touch) stores the pointer in **document** px (`clientX + scrollX`), sets `mouseTarget = 1`; `pointerleave` on the document and window `blur` set it to 0. Orbs lean toward it inside their label's box.

## Context loss

`webglcontextlost`: stop, land every morph, strip `.rz` from the DOM, drop every GPU reference, hide the canvas, `hooks.lost()` (the app removes `.gl` and `setGL(null)`). `webglcontextrestored`: only once (a second loss stays on the DOM); `resize()`, `hooks.restored()` (the app re-adds `.gl`, refits the wordmark, re-bakes the footer, re-syncs life and orbs).

## Debug

`salehdigital.gl.stats()` → `{ texMB, cacheMB, cacheEntries, poolMB, morphs, dpr, lost, running }`.

## The file

Source: `site/js/gl.js`, whole file

```js
// One WebGL context for the whole site: the live wordmark, every morph and the
// yellow orbs. (The paper grain is a CSS layer now: js/grain.js.)
//
// Safety first. Every GPU allocation and every jump-flood build is budgeted
// (BUDGET below); past a budget a morph falls back to a plain crossfade rather
// than queueing GPU work. The loop draws only what is alive and on screen, idles
// on a timer, stops when the window is hidden, unfocused or nothing moves, and
// a lost context hands everything back to the DOM.
import * as THREE from 'three';
import { QUAD_VERT, FS_VERT, JFA_SEED, JFA_STEP, JFA_FINAL, ITEM_FRAG, LINES_FRAG, WORD_FRAG, ORB_FRAG } from './glsl.js';
import { rasterize, linesOf, ascentOf, capHeightOf, fontOf } from './raster.js';
import { bus, params, reducedMotion, barPhase, LITE } from './state.js';
import { MOTION, think, REVIEW, EMERGE, ORB, LIFE, FOOT } from './tokens.js';
import { orbLook, orbFlare, orbUniforms, applyLook, accentLook } from './orb.js';
import { onTheme } from './theme.js';

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

const smooth = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

// hooks: { lost(), restored() }
export function createGL(canvas, hooks = {}) {
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({
      canvas, alpha: true, antialias: false, depth: false, stencil: false, premultipliedAlpha: true,
      powerPreference: 'default', failIfMajorPerformanceCaveat: true
    });
  } catch (e) { console.warn('WebGL unavailable', e); return null; }
  if (!renderer.capabilities.isWebGL2 || !renderer.extensions.has('EXT_color_buffer_float')) { renderer.dispose(); return null; }
  renderer.setClearColor(0x000000, 0);
  renderer.autoClear = true;
  const maxTex = renderer.capabilities.maxTextureSize;

  const capDpr = () => Math.min(window.devicePixelRatio || 1, BUDGET.dpr);
  let dpr = capDpr();
  let W = 0, H = 0, sizeDirty = false;
  let lost = false, losses = 0;
  let canvasVisible = true;
  let isScrolling = false;
  let scrollTimeout = 0;
  const camera = new THREE.OrthographicCamera(0, 1, 0, -1, -10, 10);
  const scene = new THREE.Scene();
  const quad = new THREE.PlaneGeometry(1, 1);
  // the theme's ink and swell tint: one Vector3 each, shared by every material (js/theme.js)
  const INK = new THREE.Vector3(0, 0, 0), SWELL = new THREE.Vector3(0, 0, 0), FOOT_INK = new THREE.Vector3(0, 0, 0);
  let theme = null;

  function resize() {
    sizeDirty = false;
    const targetDpr = isScrolling ? Math.min(capDpr(), BUDGET.dprScrolling) : capDpr();
    if (Math.abs(dpr - targetDpr) > 0.01) {
      dpr = targetDpr;
      renderer.setPixelRatio(dpr);
    }
    W = document.documentElement.clientWidth; H = window.innerHeight;
    renderer.setSize(W, H, false);
    canvas.style.width = W + 'px'; canvas.style.height = H + 'px';
    camera.right = W; camera.bottom = -H; camera.updateProjectionMatrix();
    wordU.aa.value = 0.6 / dpr;
    needs = true;
  }

  // ---------- GPU memory ledger ----------
  let texUsed = 0;
  const take = (bytes) => { texUsed += bytes; };
  const give = (bytes) => { texUsed = Math.max(0, texUsed - bytes); };
  function freeField(rt) { if (!rt) return; give(rt.bytes || 0); rt.dispose(); }
  function freeTex(t) { if (!t || t === blank) return; give(t.bytes || 0); t.dispose(); }

  // per-frame build budget (also a time window, for builds while the loop sleeps)
  const spent = { t: -1e9, builds: 0, px: 0 };
  function budgetOk(px) {
    const t = performance.now();
    if (t - spent.t > 16) { spent.t = t; spent.builds = 0; spent.px = 0; }
    if (spent.builds === 0) return true; // always one build a frame
    return spent.builds < BUDGET.buildsPerFrame && spent.px + px <= BUDGET.buildPxPerFrame;
  }
  function memOk(bytes) {
    if (texUsed + bytes > BUDGET.texBytes) trimCache(bytes);
    return texUsed + bytes <= BUDGET.texBytes;
  }

  // ---------- jump flood SDF ----------
  const fsScene = new THREE.Scene();
  const fsCam = new THREE.Camera();
  const fsMesh = new THREE.Mesh(new THREE.PlaneGeometry(2, 2));
  fsMesh.frustumCulled = false; fsScene.add(fsMesh);
  const mk = (frag, uniforms) => new THREE.ShaderMaterial({ vertexShader: FS_VERT, fragmentShader: frag, uniforms, depthTest: false, depthWrite: false });
  const V2 = () => new THREE.Vector2();
  const seedMat = mk(JFA_SEED, { src: { value: null }, res: { value: V2() } });
  const stepMat = mk(JFA_STEP, { prev: { value: null }, res: { value: V2() }, texSize: { value: V2() }, stepPx: { value: 1 } });
  const finalMat = mk(JFA_FINAL, { jfa: { value: null }, src: { value: null }, res: { value: V2() }, texSize: { value: V2() }, invScale: { value: 1 } });
  const base = { depthBuffer: false, stencilBuffer: false, generateMipmaps: false, wrapS: THREE.ClampToEdgeWrapping, wrapT: THREE.ClampToEdgeWrapping };
  const jfaOpts = { ...base, type: THREE.HalfFloatType, format: THREE.RGBAFormat, minFilter: THREE.NearestFilter, magFilter: THREE.NearestFilter };
  const outOpts = { ...base, type: THREE.HalfFloatType, format: THREE.RedFormat, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter };

  function canvasTex(c, filter = THREE.LinearFilter) {
    const t = new THREE.CanvasTexture(c);
    t.flipY = false; t.generateMipmaps = false; t.minFilter = filter; t.magFilter = filter;
    t.colorSpace = THREE.NoColorSpace; t.needsUpdate = true;
    return t;
  }

  // one scratch 2D canvas for every mask and display raster; each is uploaded at once
  const scratch = document.createElement('canvas');

  // the ping-pong pair: grow-only up to the cap, freed when unused for a while
  let pool = null, poolTimer = 0;
  function poolFor(w, h) {
    if (pool && pool.w >= w && pool.h >= h) return pool;
    const r = (v) => Math.min(BUDGET.jfaMaxSide, Math.ceil(v / 128) * 128);
    let pw = r(Math.max(w, pool?.w || 0)), ph = r(Math.max(h, pool?.h || 0));
    if (pw * ph > BUDGET.jfaMaxPx) { pw = r(w); ph = r(h); }
    pool?.a.dispose(); pool?.b.dispose();
    pool = { w: pw, h: ph, a: new THREE.WebGLRenderTarget(pw, ph, jfaOpts), b: new THREE.WebGLRenderTarget(pw, ph, jfaOpts) };
    return pool;
  }
  function releaseSoon() {
    clearTimeout(poolTimer);
    poolTimer = setTimeout(() => {
      pool?.a.dispose(); pool?.b.dispose(); pool = null;
      scratch.width = scratch.height = 1;
    }, BUDGET.poolIdleMs);
  }

  function pass(mat, target) { fsMesh.material = mat; renderer.setRenderTarget(target); renderer.render(fsScene, fsCam); }

  // the scale a field (or raster) of this box can afford
  function fitScale(box, want, maxPx) {
    const s = Math.min(want, BUDGET.jfaMaxSide / box.w, BUDGET.jfaMaxSide / box.h, maxTex / box.w, maxTex / box.h, Math.sqrt(maxPx / Math.max(1, box.w * box.h)));
    return Math.max(0.05, Math.floor(s * 64) / 64);
  }

  function buildSDF(mask, scale) {
    const w = mask.width, h = mask.height;
    const P = poolFor(w, h);
    const src = canvasTex(mask, THREE.NearestFilter);
    let a = P.a, b = P.b;
    a.viewport.set(0, 0, w, h); b.viewport.set(0, 0, w, h);
    seedMat.uniforms.src.value = src; seedMat.uniforms.res.value.set(w, h);
    pass(seedMat, a);
    stepMat.uniforms.res.value.set(w, h); stepMat.uniforms.texSize.value.set(P.w, P.h);
    let step = Math.pow(2, Math.ceil(Math.log2(Math.max(w, h)))) / 2;
    const steps = [];
    while (step >= 1) { steps.push(step); step /= 2; }
    steps.push(1); // JFA+1 cleans up the few wrong seeds
    for (const s of steps) {
      stepMat.uniforms.prev.value = a.texture; stepMat.uniforms.stepPx.value = s;
      pass(stepMat, b); [a, b] = [b, a];
    }
    const out = new THREE.WebGLRenderTarget(w, h, outOpts);
    finalMat.uniforms.jfa.value = a.texture; finalMat.uniforms.src.value = src;
    finalMat.uniforms.res.value.set(w, h); finalMat.uniforms.texSize.value.set(P.w, P.h); finalMat.uniforms.invScale.value = 1 / scale;
    pass(finalMat, out);
    renderer.setRenderTarget(null);
    src.dispose();
    seedMat.uniforms.src.value = finalMat.uniforms.src.value = null;
    out.bytes = w * h * 2; take(out.bytes);
    if (performance.now() - spent.t > 16) { spent.t = performance.now(); spent.builds = 0; spent.px = 0; }
    spent.builds++; spent.px += w * h;
    releaseSoon();
    return out;
  }

  // the display raster (as the DOM shows it), uploaded right away
  function displayTex(snap, box, scale, blur, opacity) {
    const t = canvasTex(rasterize(snap, box, scale, 'display', blur, opacity, scratch));
    renderer.initTexture(t);
    t.bytes = scratch.width * scratch.height * 4; take(t.bytes);
    return t;
  }

  // ---------- field cache (per string + font + size + layout), LRU by bytes ----------
  const cache = new Map(); // sig -> {rt, refs, used, bytes}; Map order = least recent first
  let cacheBytes = 0;
  const blank = new THREE.DataTexture(new Uint8Array(4), 1, 1); blank.needsUpdate = true;
  const FAIL = Symbol('over budget');

  function trimCache(extra = 0) {
    for (const [k, e] of cache) {
      if (cache.size <= BUDGET.cacheEntries && cacheBytes <= BUDGET.cacheBytes && texUsed + extra <= BUDGET.texBytes) break;
      if (e.refs > 0) continue;
      cache.delete(k); cacheBytes -= e.bytes; freeField(e.rt);
    }
  }

  function padFor(snap, extra) { return Math.ceil(14 + extra + 3 * (snap.blur || 0)); }

  // Builds (or reuses) the field and display raster for one snapshot.
  // Returns null (no snapshot), FAIL (over budget) or the field.
  function fieldFor(snap, { pad, cacheable, scale: want }) {
    if (!snap || snap.empty) return null;
    const box = { x: snap.rect.x - pad, y: snap.rect.y - pad, w: snap.rect.w + pad * 2, h: snap.rect.h + pad * 2 };
    const scale = fitScale(box, want, BUDGET.fieldMaxPx);
    const dScale = fitScale(box, dpr, BUDGET.dispMaxPx);
    const sig = `${snap.sig}#${pad}#${scale}`;
    let entry = cacheable ? cache.get(sig) : null;
    const dBytes = Math.ceil(box.w * dScale) * Math.ceil(box.h * dScale) * 4;
    if (entry) {
      entry.refs++;
      if (!memOk(dBytes)) { entry.refs--; return FAIL; }
      cache.delete(sig); cache.set(sig, entry); // most recent last
    } else {
      const px = Math.ceil(box.w * scale) * Math.ceil(box.h * scale);
      if (!budgetOk(px) || !memOk(px * 2 + dBytes)) return FAIL;
      const rt = buildSDF(rasterize(snap, box, scale, 'mask', null, null, scratch), scale);
      entry = { rt, refs: 1, used: 0, cacheable, bytes: rt.bytes };
      if (cacheable) { cache.set(sig, entry); cacheBytes += entry.bytes; }
    }
    entry.used = performance.now();
    const disp = displayTex(snap, box, dScale);
    let done = false;
    return {
      box, sdf: entry.rt.texture, disp,
      release() {
        if (done) return; done = true;
        freeTex(disp); entry.refs--;
        if (!entry.cacheable && entry.refs <= 0) freeField(entry.rt);
      }
    };
  }

  const v4 = (b) => b ? new THREE.Vector4(b.x, b.y, b.w, b.h) : new THREE.Vector4(0, 0, 1, 1);
  function unionBox(a, b) {
    if (!a) return b; if (!b) return a;
    const x = Math.min(a.x, b.x), y = Math.min(a.y, b.y);
    return { x, y, w: Math.max(a.x + a.w, b.x + b.w) - x, h: Math.max(a.y + a.h, b.y + b.h) - y };
  }

  // ---------- mesh pool: materials are reused, so programs are never torn down and recompiled ----------
  const meshPool = new Map(); // fragment source -> [mesh]
  function takeMesh(frag, uniforms, order) {
    let mesh = meshPool.get(frag)?.pop();
    if (mesh) { const u = mesh.material.uniforms; for (const k in uniforms) u[k].value = uniforms[k].value; }
    else {
      mesh = new THREE.Mesh(quad, new THREE.ShaderMaterial({ vertexShader: QUAD_VERT, fragmentShader: frag, uniforms, transparent: true, depthTest: false, depthWrite: false }));
      mesh.frustumCulled = false;
    }
    mesh.renderOrder = order; mesh.visible = true;
    scene.add(mesh);
    return mesh;
  }
  function giveMesh(mesh) {
    scene.remove(mesh);
    const u = mesh.material.uniforms;
    for (const k in u) if (u[k].value && u[k].value.isTexture) u[k].value = blank; // pooled meshes hold no textures
    const frag = mesh.material.fragmentShader;
    let list = meshPool.get(frag); if (!list) meshPool.set(frag, list = []);
    if (list.length < 12) list.push(mesh); else mesh.material.dispose();
  }

  // ---------- active morphs ----------
  const active = new Map(); // key -> item
  let now = performance.now();

  function placeMesh(mesh, box) {
    mesh.scale.set(box.w, box.h, 1);
    mesh.position.set(box.x - window.scrollX + box.w / 2, -(box.y - window.scrollY + box.h / 2), 0);
    // nothing off screen is drawn
    const top = box.y - window.scrollY, left = box.x - window.scrollX;
    mesh.visible = top < H && top + box.h > 0 && left < W && left + box.w > 0;
  }

  function cancel(key) {
    const it = active.get(key);
    if (!it) return;
    giveMesh(it.mesh);
    it.fA?.release(); it.fB?.release();
    active.delete(key);
  }

  // item: {key, A, B, onEnd}; opts: {dur, amp, group, seed}. false: over budget
  function morphItem({ key, A, B, onEnd }, { dur, amp, group, seed, style = null }) {
    cancel(key);
    if (active.size >= BUDGET.maxMorphs) return false;
    const pad = padFor(A || B, amp * 1.5 + Math.max(A?.blur || 0, B?.blur || 0) * 3);
    const fA = fieldFor(A, { pad, cacheable: true, scale: dpr });
    if (fA === FAIL) return false;
    const fB = fieldFor(B, { pad, cacheable: true, scale: dpr });
    if (fB === FAIL) { fA?.release(); return false; }
    if (!fA && !fB) { onEnd?.(); return true; }
    const frame = unionBox(fA?.box, fB?.box);
    const mesh = takeMesh(ITEM_FRAG, {
      sdfA: { value: fA?.sdf || blank }, sdfB: { value: fB?.sdf || blank },
      dispA: { value: fA?.disp || blank }, dispB: { value: fB?.disp || blank },
      boxA: { value: v4(fA?.box) }, boxB: { value: v4(fB?.box) }, frame: { value: v4(frame) },
      hasA: { value: fA ? 1 : 0 }, hasB: { value: fB ? 1 : 0 },
      t: { value: 0 }, raw: { value: 0 }, time: { value: 0 }, amp: { value: amp },
      bA: { value: A?.blur || 0 }, bB: { value: B?.blur || 0 },
      oA: { value: A ? A.opacity : 0 }, oB: { value: B ? B.opacity : 0 },
      grain: { value: 0.3 + 0.5 * params.texture }, seed: { value: seed }, aa: { value: 0.6 / dpr }, uInk: { value: INK },
      shift: { value: (A && B && A.sig === B.sig) ? new THREE.Vector2(B.rect.x - A.rect.x, B.rect.y - A.rect.y) : new THREE.Vector2() },
      dots: { value: style?.dots || 0 }, pitch: { value: style?.pitch || 1.75 }, blurPeak: { value: style?.blur || 0 }
    }, 1);
    active.set(key, { key, mesh, u: mesh.material.uniforms, fA, fB, frame, start: now, dur, total: dur, group, onEnd, A, B, lines: false });
    return true;
  }

  function morphBody({ key, A, B, onEnd }, { dur, amp, group }) {
    cancel(key);
    if (active.size >= BUDGET.maxMorphs) return false;
    const pad = Math.ceil(16 + amp * 2);
    const want = Math.min(BUDGET.fieldScale, dpr);
    const fA = fieldFor(A, { pad, cacheable: false, scale: want });
    if (fA === FAIL) return false;
    const fB = fieldFor(B, { pad, cacheable: false, scale: want });
    if (fB === FAIL) { fA?.release(); return false; }
    if (!fA && !fB) { onEnd?.(); return true; }
    const frame = unionBox(fA?.box, fB?.box);
    const LA = A && !A.empty ? linesOf(A) : { count: 0, bounds: [] };
    const LB = B && !B.empty ? linesOf(B) : { count: 0, bounds: [] };
    const arr = (b) => { const a = new Float32Array(MAXL); a.fill(1e6); b.slice(0, MAXL).forEach((v, i) => a[i] = v); return a; };
    const stagger = MOTION.staggerMs, inDelay = dur * MOTION.bodyInDelay;
    const total = Math.max(dur * 0.5 + LA.count * stagger * 0.6, inDelay + dur + Math.max(0, Math.min(LB.count, MAXL) - 1) * stagger);
    const mesh = takeMesh(LINES_FRAG, {
      sdfA: { value: fA?.sdf || blank }, sdfB: { value: fB?.sdf || blank },
      dispA: { value: fA?.disp || blank }, dispB: { value: fB?.disp || blank },
      boxA: { value: v4(fA?.box) }, boxB: { value: v4(fB?.box) }, frame: { value: v4(frame) },
      hasA: { value: fA ? 1 : 0 }, hasB: { value: fB ? 1 : 0 },
      elapsed: { value: 0 }, dur: { value: dur }, stagger: { value: stagger }, inDelay: { value: inDelay },
      time: { value: 0 }, amp: { value: amp }, aa: { value: 0.6 / dpr },
      grain: { value: 0.3 + 0.5 * params.texture }, blurMax: { value: 2.6 + 2 * params.energy }, uInk: { value: INK },
      linesA: { value: arr(LA.bounds) }, linesB: { value: arr(LB.bounds) },
      nA: { value: Math.min(LA.count, MAXL) }, nB: { value: Math.min(LB.count, MAXL) }
    }, 1);
    active.set(key, { key, mesh, u: mesh.material.uniforms, fA, fB, frame, start: now, dur, total, group, onEnd, A, B, lines: true });
    return true;
  }

  // current visual params of a morph, so a hover-out can start where hover-in is
  function current(key) {
    const it = active.get(key);
    if (!it || it.lines || !it.A || !it.B) return null;
    const t = it.u.t.value;
    return { sameText: it.A.sig === it.B.sig, blur: it.A.blur + (it.B.blur - it.A.blur) * t, opacity: it.A.opacity + (it.B.opacity - it.A.opacity) * t };
  }

  const groups = new Map(); // id -> {kind, keys:Set}
  let thinking = 0, thinkTarget = 0;

  // returns the items it could not afford: the caller crossfades them
  function run(group) {
    const { id, kind, items, body, dur, amp, style = null } = group;
    if (lost) return [...items, ...(body ? [body] : [])];
    now = performance.now();
    const keys = new Set(), fallback = [];
    let seed = Math.random() * 100;
    for (const it of items) {
      if (!morphItem(it, { dur, amp, group: id, seed: seed += 1.37, style })) fallback.push(it);
      else if (active.has(it.key)) keys.add(it.key);
    }
    if (body) {
      if (!morphBody(body, { dur, amp, group: id })) fallback.push(body);
      else if (active.has(body.key)) keys.add(body.key);
    }
    if (keys.size) groups.set(id, { kind, keys, dur });
    else bus.emit('resolve:end', { id, kind });
    thinkTarget = Math.max(thinkTarget, kind === 'hover' ? 0.25 : kind === 'emerge' ? EMERGE.think : kind === 'clock' ? 0.3 : 1);
    trimCache();
    wake();
    return fallback;
  }

  // every morph lands now (hidden tab, lost context): its DOM text comes back
  function finishAll() {
    for (const [key, it] of [...active]) { cancel(key); try { it.onEnd?.(); } catch (e) { console.error(e); } }
    for (const [id, g] of groups) bus.emit('resolve:end', { id, kind: g.kind });
    groups.clear();
  }

  // ---------- wordmark ----------
  let word = null;
  const wordU = {
    sdf: { value: blank }, box: { value: new THREE.Vector4(0, 0, 1, 1) },
    sdfB: { value: blank }, mixB: { value: 0 }, sdfE: { value: blank }, sdfO: { value: blank },
    st: { value: new THREE.Vector4() }, st5: { value: 0 }, reach: { value: 1e4 },
    bar: { value: 0 }, beat: { value: 0 }, cap: { value: 80 }, ghost: { value: 0 }, ripples: { value: 1 }, flowT: { value: 0 },
    kBoil: { value: LIFE.boil }, kCursor: { value: LIFE.cursorGain }, kPitch: { value: LIFE.dotPitch }, kDrift: { value: LIFE.dotDrift },
    kSpacing: { value: LIFE.rippleSpacing }, kRipple: { value: LIFE.rippleAlpha }, kReach: { value: LIFE.rippleReach }, kMeld: { value: LIFE.meld },
    traces: { value: [0, 1, 2, 3].map(() => new THREE.Vector4(0, 0, 0, 0)) },
    cYellow: { value: new THREE.Color(ORB.yellow) }, cRim: { value: new THREE.Color(ORB.rim) },
    time: { value: 0 }, breath: { value: 1 }, thinking: { value: 0 }, aa: { value: 0.4 },
    grain: { value: 0.1 }, ink: { value: 0.15 }, uInk: { value: INK }, uSwell: { value: SWELL }, uFoot: { value: FOOT_INK },
    mouse: { value: new THREE.Vector2(-1e4, -1e4) }, mouseOn: { value: 0 }, mouseR: { value: 90 },
    // the footer (bio + marks) baked into a second field, drawn in the same pass
    frame: { value: new THREE.Vector4(0, 0, 1, 1) }, sdfF: { value: blank }, boxF: { value: new THREE.Vector4(0, 0, 1, 1) },
    basF: { value: new THREE.Vector4() },
    dotR: { value: [0, 1].map(() => new THREE.Vector4()) }, dotB: { value: Array.from({ length: 16 }, () => new THREE.Vector4(0, 0, 0, -1)) },
    hasF: { value: 0 }, kF: { value: FOOT.bio }, kM: { value: FOOT.marks }, aaF: { value: 0.4 },
    marks: { value: [0, 1, 2, 3].map(() => new THREE.Vector4(0, 0, 0, 0)) }, markSoft: { value: new THREE.Vector4() }
  };
  const wordMesh = new THREE.Mesh(quad, new THREE.ShaderMaterial({ vertexShader: QUAD_VERT, fragmentShader: WORD_FRAG, uniforms: wordU, transparent: true, depthTest: false, depthWrite: false }));
  wordMesh.renderOrder = 0; wordMesh.frustumCulled = false; wordMesh.visible = false;
  scene.add(wordMesh);

  // ---------- the footer above the word: bio and marks in the wordmark's pass ----------
  // snap: runs (bio words + mark images) in document px; marks: [{ x, y, w, h, soft }]
  let foot = null;
  const markFocus = [0, 0, 0, 0], markTarget = [0, 0, 0, 0], dotT0 = performance.now();
  function setFooter(snap, anchor, marks = [], bas = null, dots = []) {
    if (lost) return false;
    const pad = 12;
    const box = { x: snap.rect.x - pad, y: snap.rect.y - pad, w: snap.rect.w + pad * 2, h: snap.rect.h + pad * 2 };
    const scale = fitScale(box, Math.min(FOOT.scale, dpr * FOOT.scale), BUDGET.fieldMaxPx); // ~2x for crisp 16px text, if the budget allows
    const mask = rasterize(snap, box, scale, 'mask', null, null, scratch);
    const px = mask.width * mask.height;
    if (!budgetOk(px) || !memOk(px * 2)) { dropFooter(); return false; }
    const rt = buildSDF(mask, scale);
    dropFooter();
    const ar = anchor.getBoundingClientRect();
    const ax = ar.left + window.scrollX, ay = ar.top + window.scrollY;
    foot = { rt, box, scale, off: { x: box.x - ax, y: box.y - ay },
      marks: marks.map(m => ({ x: m.x + m.w / 2 - ax, y: m.y + m.h / 2 - ay, r: Math.max(m.w, m.h) / 2 + 2, soft: m.soft || 0 })),
      bas: bas && { x: bas.x - ax, y: bas.y - ay, w: bas.w, h: bas.h }, // the basmala: the word's hover, at 18px
      dots: dots.slice(0, 2).map(d => ({ x: d.x - ax, y: d.y - ay, w: d.w, h: d.h })) }; // the dot strips, drawn here so they scroll with the rest
    wordU.sdfF.value = rt.texture; wordU.hasF.value = 1; wordU.aaF.value = 0.55 / dpr; wordU.basF.value.set(0, 0, 0, 0);
    wordU.markSoft.value.set(...[0, 1, 2, 3].map(i => foot.marks[i]?.soft || 0));
    needs = true; wake();
    return true;
  }
  function dropFooter() { if (!foot) return; freeField(foot.rt); foot = null; wordU.sdfF.value = blank; wordU.hasF.value = 0; wordU.dotR.value.forEach(v => v.set(0, 0, 0, 0)); }
  function markHover(i, on) { markTarget[i] = on ? 1 : 0; wake(); }

  // the wordmark's extra fields (the hold secret, the per-glyph melt) are built
  // lazily, one per frame, through this queue
  const wordQueue = [];
  function queueWord(kind) {
    if (!word || word[kind] || wordQueue.includes(kind)) return;
    if (kind === 'alt' ? !word.altSnap : !word.extra) return;
    wordQueue.push(kind); wake();
  }
  function buildWord(kind) {
    const i = wordQueue.indexOf(kind); if (i >= 0) wordQueue.splice(i, 1);
    if (!word || word[kind] || lost) return;
    const snap = kind === 'alt' ? word.altSnap : word.extra?.[kind];
    if (!snap) return;
    trimCache(word.px * 2);
    const rt = buildSDF(rasterize(snap, word.box, word.scale, 'mask', null, null, scratch), word.scale);
    word[kind] = rt;
    (kind === 'alt' ? wordU.sdfB : kind === 'even' ? wordU.sdfE : wordU.sdfO).value = rt.texture;
  }
  function drainWordQueue() {
    while (wordQueue.length && word && budgetOk(word.px)) buildWord(wordQueue[0]);
  }
  function dropWord() {
    if (!word) return;
    ['rt', 'alt', 'even', 'odd'].forEach(k => freeField(word[k]));
    wordU.sdf.value = wordU.sdfB.value = wordU.sdfE.value = wordU.sdfO.value = blank;
    wordQueue.length = 0;
    word = null;
  }

  // life: the wordmark eases to a new level; a rise swells it first
  let lifeTarget = 0, lifeShown = 0, lifeInit = false, flowT = 0;
  let traceIds = [], ghostWant = 0;
  function setLife(v) {
    v = Math.max(0, Math.min(1, v));
    if (!lifeInit) { lifeShown = v; lifeInit = true; }
    else if (v > lifeTarget + 0.004) thinkTarget = Math.max(thinkTarget, LIFE.swell);
    lifeTarget = v; wake();
  }
  function setTraces(ids) { traceIds = ids || []; placeTraces(); wake(); }
  function placeTraces() {
    if (!word || !word.glyphs) return;
    const tr = wordU.traces.value;
    tr.forEach(t => t.set(0, 0, 0, 0));
    ghostWant = 0;
    if (LITE) return;
    traceIds.slice(0, 4).forEach((id, i) => {
      const g = word.glyphs[LIFE.traceLetters[id] ?? i];
      if (g) tr[i].set(g.cx + word.dx, g.cy + word.dy, word.cap * LIFE.traceRadius, 1);
    });
    ghostWant = traceIds.includes('hold') ? LIFE.ghostAlpha : 0;
    ensureAlt();
  }
  // snap: a snapshot-like {runs, rect, blur:0, opacity:1}; anchor: the element it follows
  function setWordmark(snap, anchor, extra = null) {
    if (lost) return;
    const pad = 24;
    const box = { x: snap.rect.x - pad, y: snap.rect.y - pad, w: snap.rect.w + pad * 2, h: snap.rect.h + pad * 2 };
    const scale = fitScale(box, Math.min(BUDGET.fieldScale, dpr), BUDGET.fieldMaxPx);
    const altSnap = word?.altSnap || null;
    dropWord();
    const mask = rasterize(snap, box, scale, 'mask', null, null, scratch);
    trimCache(mask.width * mask.height * 2);
    const rt = buildSDF(mask, scale);
    const ar = anchor.getBoundingClientRect();
    word = { rt, box, anchor, scale, px: mask.width * mask.height, alt: null, even: null, odd: null, altSnap, off: { x: box.x - (ar.left + window.scrollX), y: box.y - (ar.top + window.scrollY) } };
    wordU.sdf.value = rt.texture;
    if (extra) {
      word.extra = extra; // the per-glyph fields are built only when life nears stage 4
      word.glyphs = extra.glyphs; word.cap = extra.cap; wordU.cap.value = extra.cap;
      word.dx = 0; word.dy = 0; word.base = { x: box.x, y: box.y };
      placeTraces();
    }
    wordU.aa.value = 0.6 / dpr;
    wordMesh.visible = true;
    needs = true; wake();
  }

  // the hold secret: a second field in the same box, and a mix that runs along the think ease
  let wordMix = { from: 0, to: 0, start: 0, dur: 1 };
  // built lazily: when a hold begins, or when the Arabic ghost is due
  function setWordmarkAlt(snap) { if (!word) return; word.altSnap = snap; freeField(word.alt); word.alt = null; wordU.sdfB.value = blank; ensureAlt(); }
  function ensureAlt() {
    if (!word || word.alt || !word.altSnap) return;
    if (ghostWant > 0 || wordMix.to > 0) queueWord('alt');
  }
  function wordmarkTo(v, dur) {
    if (v > 0 && word && !word.alt) buildWord('alt'); // a deliberate gesture: build it now
    wordMix = { from: wordU.mixB.value, to: v, start: performance.now(), dur: reducedMotion.matches ? 120 : dur };
    wake();
  }
  let hold = 0;
  function setHold(v) { hold = v; if (v > 0) queueWord('alt'); wake(); }
  function thinkUp(v) { thinkTarget = Math.max(thinkTarget, v); wake(); }

  // ---------- the yellow orbs ----------
  const orbs = new Map(); // id -> orb
  const orbCol = (hex) => new THREE.Color(hex);
  const GLOW = ORB.style !== 'dots';
  const orbMs = () => GLOW ? ORB.burstMs : ORB.meltMs;
  const orbLiveMs = Math.max(ORB.bloomMs, GLOW ? ORB.flareMs : 0) + 50;
  function makeOrb(w) {
    const mesh = takeMesh(ORB_FRAG, GLOW ? orbUniforms(THREE) : {
      frame: { value: new THREE.Vector4() }, center: { value: new THREE.Vector2() }, target: { value: new THREE.Vector2() },
      lean: { value: new THREE.Vector2() }, radius: { value: w.size / 2 }, bloom: { value: 0 }, melt: { value: 0 },
      meltMove: { value: 1 }, fade: { value: 1 }, time: { value: 0 }, unit: { value: 1 / dpr }, pitch: { value: ORB.pitch / dpr },
      seed: { value: Math.random() * 50 },
      cYellow: { value: orbCol(ORB.yellow) }, cShade: { value: orbCol(ORB.shade) }, cRim: { value: orbCol(ORB.rim) }, cInk: { value: orbCol(ORB.ink) }
    }, 1.5);
    mesh.visible = false;
    return { id: w.id, sel: w.sel, size: w.size, sizeNow: w.size, u: mesh.material.uniforms, mesh, born: performance.now(), melt: 0, leanX: 0, leanY: 0, hover: 0, font: null };
  }
  function dropOrb(o) { giveMesh(o.mesh); orbs.delete(o.id); }
  // list: [{ id, sel, size }]. New ids bloom; ids no longer listed melt into their label.
  function syncOrbs(list) {
    if (lost) return;
    const want = new Map(list.map(w => [w.id, w]));
    for (const o of orbs.values()) if (!want.has(o.id) && !o.melt) o.melt = performance.now();
    for (const w of list) {
      let o = orbs.get(w.id);
      if (o && o.melt) { dropOrb(o); o = null; }
      if (!o) { o = makeOrb(w); orbs.set(w.id, o); }
      o.sel = w.sel; o.size = w.size; o.small = w.size < ORB.size;
    }
    wake();
  }
  const orbRange = document.createRange();
  function labelGeom(o, el) {
    let tn = null;
    for (const n of el.childNodes) if (n.nodeType === 3 && n.data.trim()) { tn = n; break; }
    if (!tn) return null;
    if (!o.font) { const cs = getComputedStyle(el); o.font = fontOf(cs); }
    orbRange.selectNodeContents(tn);
    const rs = orbRange.getClientRects();
    if (!rs.length) return null;
    const first = rs[0], last = rs[rs.length - 1];
    const asc = ascentOf(o.font), cap = capHeightOf(o.font);
    const sx = window.scrollX, sy = window.scrollY;
    return {
      cx: last.right + sx + ORB.gap, cy: last.top + sy + asc - cap / 2, right: last.right + sx, cap,
      tx: first.left + sx + cap * 0.22, ty: first.top + sy + asc - cap / 2,
      box: el.getBoundingClientRect()
    };
  }
  let orbClock = 0;
  function updateOrbs(t, dt, reduced) {
    let anyVis = false;
    const look = { [false]: GLOW && accentLook(orbLook(params, false), theme), [true]: GLOW && accentLook(orbLook(params, true), theme) };
    if (!reduced && GLOW) orbClock += dt / 1000 * look[false].speed;
    for (const o of [...orbs.values()]) {
      const el = document.querySelector(o.sel);
      const g = el && labelGeom(o, el);
      if (!g) { if (o.melt) dropOrb(o); else o.mesh.visible = false; continue; }
      const L = GLOW ? look[!!o.small] : null;
      const want = GLOW ? L.size : o.size;
      o.sizeNow += (want - o.sizeNow) * (1 - Math.pow(0.001, dt / 1000));
      const r = o.sizeNow / 2;
      const cx = g.cx + r, cy = g.cy;
      // bloom: from a point, overshoot, settle (easeOutBack)
      let b = 1;
      if (!reduced) { const x = Math.min(1, (t - o.born) / ORB.bloomMs), k = ORB.bloomOvershoot; b = x >= 1 ? 1 : 1 + (k + 1) * Math.pow(x - 1, 3) + k * Math.pow(x - 1, 2); }
      // hover: lean toward the cursor
      const m = wordU.mouse.value, bx = g.box;
      const over = mouseTarget > 0 && m.x - window.scrollX >= bx.left - 4 && m.x - window.scrollX <= bx.right + 12 && m.y - window.scrollY >= bx.top - 4 && m.y - window.scrollY <= bx.bottom + 4;
      let lx = 0, ly = 0;
      if (over && !reduced) { lx = m.x - cx; ly = m.y - cy; const L = Math.hypot(lx, ly), max = r * ORB.leanMax * 2; if (L > max) { lx *= max / L; ly *= max / L; } }
      const k2 = 1 - Math.exp(-ORB.leanEase * dt / 1000);
      o.leanX += (lx - o.leanX) * k2; o.leanY += (ly - o.leanY) * k2;
      const melt = o.melt ? Math.min(1, (t - o.melt) / (reduced ? 160 : orbMs())) : 0;
      if (melt >= 1) { dropOrb(o); continue; }
      const u = o.u;
      u.center.value.set(cx, cy); u.target.value.set(g.tx, g.ty); u.lean.value.set(o.leanX, o.leanY);
      u.radius.value = r; u.bloom.value = b; u.melt.value = melt; u.meltMove.value = reduced ? 0 : 1;
      u.unit.value = 1 / dpr; u.pitch.value = ORB.pitch / dpr;
      let pad = o.sizeNow * 2.2;
      if (GLOW) {
        o.hover += ((over && !reduced ? 1 : 0) - o.hover) * (1 - Math.exp(-dt / (ORB.hoverMs / 3)));
        u.flare.value = reduced ? 0 : orbFlare(t - o.born);
        u.time.value = reduced ? 0 : orbClock;
        u.hover.value = o.hover; u.edge.value = g.right + 0.5;
        applyLook(u, L);
        if (reduced) { u.pulse.value = 0; u.bob.value = 0; }
        pad = L.halo * (1.05 + 0.9 * u.flare.value) + 2; // room for the flare's rays while it lasts
      } else {
        u.time.value = reduced ? 0 : clock * ORB.wobbleSpeed;
      }
      const x0 = Math.min(cx, g.tx) - pad, y0 = Math.min(cy, g.ty) - pad;
      const fr = { x: x0, y: y0, w: Math.max(cx, g.tx) + pad - x0, h: Math.max(cy, g.ty) + pad - y0 };
      u.frame.value.set(fr.x, fr.y, fr.w, fr.h);
      placeMesh(o.mesh, fr);
      anyVis = anyVis || o.mesh.visible;
    }
    return anyVis;
  }

  // ---------- pointer, scroll, focus ----------
  let mouseOn = 0, mouseTarget = 0, lastPointer = -1e9, lastScroll = -1e9;
  let focused = document.hasFocus();
  window.addEventListener('pointermove', (e) => {
    if (e.pointerType === 'touch') return;
    wordU.mouse.value.set(e.clientX + window.scrollX, e.clientY + window.scrollY);
    mouseTarget = 1; lastPointer = performance.now(); wake();
  }, { passive: true });
  document.addEventListener('pointerleave', () => { mouseTarget = 0; });
  window.addEventListener('blur', () => { mouseTarget = 0; focused = false; });
  window.addEventListener('focus', () => { focused = true; wake(); });
  window.addEventListener('scroll', () => {
    lastScroll = performance.now();
    if (!isScrolling) {
      isScrolling = true;
      sizeDirty = true;
    }
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      isScrolling = false;
      sizeDirty = true;
      wake();
    }, 150);
    wake();
  }, { passive: true });
  // someone is here: the window has focus, or the pointer moved over it lately
  const attended = (t) => !document.hidden && canvasVisible && (focused || t - lastPointer < 4000);

  // ---------- loop ----------
  // Busy: every frame (rAF). Idle but alive (the wordmark or an orb on screen,
  // someone here): a timer at MOTION.idleFps / orbFps, then one rAF. Otherwise
  // nothing runs until an event wakes it.
  let raf = 0, timer = 0, lastRender = 0, needs = true, clock = 0, lastNow = performance.now();
  let wordWasVis = true, orbsWereVis = false, inFrame = false, again = false;

  function wake() {
    if (lost || document.hidden || !canvasVisible) return;
    if (inFrame) { again = true; return; } // never a second rAF chain

    if (timer) { clearTimeout(timer); timer = 0; }
    if (!raf) raf = requestAnimationFrame(frame);
  }
  function sleep(ms) {
    if (raf || timer || lost) return;
    timer = setTimeout(() => { timer = 0; if (!raf && !lost && !document.hidden) raf = requestAnimationFrame(frame); }, Math.max(0, ms));
  }
  function stopLoop() { cancelAnimationFrame(raf); clearTimeout(timer); raf = 0; timer = 0; }

  function frame(t) {
    raf = 0;
    if (document.hidden || lost || !canvasVisible) return;
    inFrame = true; again = false;
    try { step(t); } finally { inFrame = false; }
    if (!raf && !lost && !document.hidden && canvasVisible && (lastBusy || again)) { clearTimeout(timer); timer = 0; raf = requestAnimationFrame(frame); }
  }
  let lastBusy = false;

  function step(t) {
    lastBusy = false;
    if (sizeDirty) resize();
    now = t;
    const dt = Math.min(64, t - lastNow); lastNow = t;
    spent.t = -1e9; // a fresh build budget each frame
    drainWordQueue();
    const reduced = reducedMotion.matches;

    // where the wordmark is (document space) and whether it is on screen
    let wbox = null, wordVis = false;
    if (word) {
      const ar = word.anchor.getBoundingClientRect();
      wbox = { x: ar.left + window.scrollX + word.off.x, y: ar.top + window.scrollY + word.off.y, w: word.box.w, h: word.box.h };
      const top = wbox.y - window.scrollY;
      wordVis = top < H && top + wbox.h > 0;
    }
    const pointerLive = t - lastPointer < 900 || mouseOn > 0.01 && mouseTarget === 0;
    const orbLive = [...orbs.values()].some(o => o.melt || t - o.born < orbLiveMs || (o.hover > 0.01 && o.hover < 0.99));
    const mixLive = t - wordMix.start < wordMix.dur + 50;
    const settling = Math.abs(lifeTarget - lifeShown) > 0.002;
    const marksEasing = markFocus.some((f, i) => Math.abs(f - markTarget[i]) > 0.003);
    const wordBusy = wordVis && (pointerLive || thinking > 0.01 || mixLive || hold > 0 || settling || wordQueue.length > 0 || marksEasing);
    const busy = active.size > 0 || needs || t - lastScroll < 250 || orbLive || wordBusy || wordVis !== wordWasVis
      || (pointerLive && orbsWereVis);
    const ambient = !reduced && attended(t) && (wordVis || orbsWereVis);
    const idleMs = 1000 / (orbsWereVis ? MOTION.orbFps : MOTION.idleFps);
    if (!busy) {
      if (!ambient) return; // nothing alive: sleep until an event wakes the loop
      if (t - lastRender < idleMs - 4) { sleep(idleMs - (t - lastRender)); return; }
    }

    if (!reduced) clock += dt / 1000;
    const E = params.energy, T = params.texture;

    // thinking swell: rises fast, decays slow
    thinkTarget *= Math.pow(0.5, dt / 450);
    if (hold > 0) thinkTarget = Math.max(thinkTarget, 0.4 + hold * 1.6);
    thinking += (thinkTarget - thinking) * (1 - Math.pow(0.001, dt / 1000));
    if (reduced) thinking = 0;
    mouseOn += (mouseTarget - mouseOn) * (1 - Math.pow(0.02, dt / 1000));

    // morphs
    for (const [key, it] of [...active]) {
      if (REVIEW.freeze != null) it.start = t - REVIEW.freeze * it.total; // review: hold the frame
      const raw = Math.min(1, (t - it.start) / it.total);
      if (it.lines) { it.u.elapsed.value = t - it.start; }
      else { it.u.raw.value = raw; it.u.t.value = think(raw); }
      it.u.time.value = clock;
      placeMesh(it.mesh, it.frame);
      if (t - it.start >= it.total) {
        cancel(key);
        it.onEnd?.();
        const g = groups.get(it.group);
        if (g) { g.keys.delete(key); if (!g.keys.size) { groups.delete(it.group); bus.emit('resolve:end', { id: it.group, kind: g.kind }); } }
      }
    }
    // progress of the newest group
    let newest = null;
    for (const [id, g] of groups) newest = { id, g };
    if (newest) {
      const any = [...active.values()].find(i => i.group === newest.id);
      if (any) { const raw = Math.min(1, (t - any.start) / any.dur); bus.emit('resolve:progress', { id: newest.id, kind: newest.g.kind, raw, t: think(raw) }); }
    }

    // wordmark
    if (word) {
      const box = wbox;
      // keep the field in document space so the cursor math stays simple
      wordU.box.value.set(box.x, box.y, box.w, box.h);
      if (word.base && (word.dx !== box.x - word.base.x || word.dy !== box.y - word.base.y)) { word.dx = box.x - word.base.x; word.dy = box.y - word.base.y; placeTraces(); }
      // life: ease toward the target; stages, ripples and flow ride on it
      lifeShown += (lifeTarget - lifeShown) * (1 - Math.exp(-dt / (LIFE.settleMs / 3)));
      const L5 = LITE ? 0 : lifeShown * 5;
      if (L5 > 3.02) { queueWord('even'); queueWord('odd'); }
      const s1 = smooth(0, 1, L5), s2 = smooth(1, 2, L5), s3 = smooth(2, 3, L5);
      const s4 = (word.even && word.odd) ? smooth(3, 4, L5) : 0, s5 = smooth(4, 5, L5);
      wordU.st.value.set(s1, s2, s3, s4); wordU.st5.value = s5;
      wordU.ghost.value = word.alt ? ghostWant : 0;
      const bp = reduced ? 0 : barPhase(t);
      wordU.bar.value = bp; wordU.beat.value = (bp * 4) % 1;
      wordU.ripples.value = reduced ? 0 : 1;
      if (!reduced) flowT += dt / 1000 * LIFE.flow;
      wordU.flowT.value = flowT;
      let frame = box;
      if (foot) {
        const ar = word.anchor.getBoundingClientRect();
        const ax = ar.left + window.scrollX, ay = ar.top + window.scrollY;
        const fb = { x: ax + foot.off.x, y: ay + foot.off.y, w: foot.box.w, h: foot.box.h };
        wordU.boxF.value.set(fb.x, fb.y, fb.w, fb.h);
        frame = unionBox(box, fb);
        const k = 1 - Math.exp(-dt / (reduced ? 1 : 90));
        if (foot.bas) wordU.basF.value.set(ax + foot.bas.x, ay + foot.bas.y, foot.bas.w, foot.bas.h);
        // the dot matrix's blobs, as js/footdots.js places them (about one per 140px, each strip its own phase)
        const dT = reduced ? 0 : (t - dotT0) / 1000 * (0.4 + 1.2 * params.energy);
        let bi = 0;
        foot.dots.forEach((d, si) => {
          const R = { x: ax + d.x, y: ay + d.y, w: d.w, h: d.h };
          wordU.dotR.value[si].set(R.x, R.y, R.w, R.h);
          if (!R.w) return;
          const n = Math.min(8, Math.max(2, Math.round(R.w / 140)));
          for (let i = 0; i < n; i++) {
            const ph = i * 2.399 + si * 1.3;
            wordU.dotB.value[bi++].set(R.x + ((i + 0.5) / n + 0.06 * Math.sin(dT * 0.21 + ph)) * R.w,
              R.y + R.h * (0.5 + 0.35 * Math.sin(dT * 0.33 + ph * 1.7)), 5 + 4 * (0.5 + 0.5 * Math.sin(dT * 0.27 + ph * 0.9)), si);
          }
        });
        for (; bi < 16; bi++) wordU.dotB.value[bi].set(0, 0, 0, -1);
        foot.marks.forEach((m, i) => {
          markFocus[i] += (markTarget[i] - markFocus[i]) * k;
          wordU.marks.value[i].set(ax + m.x, ay + m.y, m.r, markFocus[i]);
        });
      }
      wordU.frame.value.set(frame.x, frame.y, frame.w, frame.h);
      // the stage sizes follow the word's cap height, so a 16px-tall wordmark on a phone keeps its letterforms
      const capK = Math.min(1, (word.cap || 80) / 80);
      wordU.kPitch.value = Math.max(1.1, LIFE.dotPitch * capK);
      wordU.kSpacing.value = Math.max(4, LIFE.rippleSpacing * capK);
      wordU.kReach.value = Math.max(12, LIFE.rippleReach * capK);
      wordU.kBoil.value = LIFE.boil * Math.max(0.35, capK);
      placeMesh(wordMesh, frame);
      wordU.time.value = clock;
      const breath = reduced ? 0 : MOTION.breathPx(E);
      wordU.breath.value = breath;
      wordU.thinking.value = thinking;
      const mOn = reduced ? 0 : mouseOn;
      wordU.mouseOn.value = mOn;
      wordU.grain.value = 0.04 + 0.22 * T;
      wordU.ink.value = 0.05 + 0.3 * T;
      wordU.mouseR.value = Math.max(60, Math.min(140, W * 0.06));
      const mx = Math.min(1, (t - wordMix.start) / wordMix.dur);
      wordU.mixB.value = word.alt ? wordMix.from + (wordMix.to - wordMix.from) * think(mx) : 0;
      // reach: the furthest any edge, ripple or melt can land from the base field
      const cg = 1 + (LIFE.cursorGain - 1) * s1, mixing = wordU.mixB.value > 0;
      const shift = 1.3 * (breath * (1 + thinking * 2.5) * (1 + s1 * 0.6 + s5 * 0.4) + mOn * 3 * cg + (mixing ? 10 : 0));
      const noise = 1.3 * (mOn * 3.5 * cg + thinking * 1.6 + wordU.ink.value + breath * 0.35 + s1 * LIFE.boil + (mixing ? 3 : 0));
      let reach = shift + noise + (word.cap || 80) * LIFE.meld * 0.1 * s4 + 2;
      if (s3 > 0 && !reduced) reach += LIFE.rippleReach * 3.6;
      wordU.reach.value = reach;
    }
    const orbsVis = updateOrbs(t, dt, reduced);

    renderer.setRenderTarget(null);
    renderer.render(scene, camera);
    lastRender = t; needs = false;
    wordWasVis = wordVis; orbsWereVis = orbsVis;
    if (busy) lastBusy = true;
    else if (ambient) sleep(idleMs);
  }

  // ---------- hidden tab, lost context ----------
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) { stopLoop(); finishAll(); }
    else { lastNow = performance.now(); needs = true; wake(); }
  });
  window.addEventListener('resize', () => { sizeDirty = true; wake(); });
  bus.on('params', () => { needs = true; wake(); });
  // a theme change re-tints everything drawn here, live
  onTheme((c) => {
    theme = c;
    INK.set(...c.ink); SWELL.set(...c.swell); FOOT_INK.set(...c.foot);
    wordU.cYellow.value.set(c.marathon ? c.hex.glow : ORB.yellow);
    wordU.cRim.value.set(c.marathon ? c.hex.accentMark : ORB.rim);
    needs = true; wake();
  });

  canvas.addEventListener('webglcontextlost', () => {
    // three.js has already called preventDefault, so the browser may restore it once
    losses++; lost = true;
    stopLoop(); finishAll();
    document.querySelectorAll('.rz').forEach(el => { el.classList.remove('rz'); delete el.dataset.rz; });
    // every GPU object went with the context: drop the references, free nothing
    cache.clear(); cacheBytes = 0; texUsed = 0; pool = null; clearTimeout(poolTimer);
    word = null; wordQueue.length = 0; wordMesh.visible = false;
    for (const o of [...orbs.values()]) { scene.remove(o.mesh); orbs.delete(o.id); }
    canvas.style.visibility = 'hidden';
    console.warn('[gl] context lost: the page is plain DOM until it is restored');
    try { hooks.lost?.(); } catch (e) { console.error(e); }
  });
  canvas.addEventListener('webglcontextrestored', () => {
    if (losses > 1) { console.warn('[gl] lost twice: staying on the DOM'); return; } // one rebuild, never a loop
    lost = false;
    canvas.style.visibility = '';
    resize();
    try { hooks.restored?.(); } catch (e) { console.error(e); }
    needs = true; wake();
  });

  // Observe canvas visibility to pause rendering when off-screen
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const wasVisible = canvasVisible;
        canvasVisible = entry.isIntersecting;
        if (canvasVisible && !wasVisible) {
          wake();
        } else if (!canvasVisible && wasVisible) {
          stopLoop();
        }
      });
    }, { threshold: 0 });
    observer.observe(canvas);
  }

  resize();
  wake();

  return {
    run, current, setWordmark, setWordmarkAlt, wordmarkTo, setHold, think: thinkUp, syncOrbs, setLife, setTraces, cancel,
    get dpr() { return dpr; },
    isActive: (key) => active.has(key),
    morphKeys: () => [...active.keys()], // read-only, for the debug panel
    setFooter, dropFooter, markHover, hasFooter: () => !!foot,
    // build and cache fields ahead of time (the icon variants: tiny, built once, within BUDGET)
    prewarm(snaps, extra = 0) {
      if (lost) return 0;
      let n = 0;
      for (const sn of snaps) { const f = fieldFor(sn, { pad: padFor(sn, extra), cacheable: true, scale: dpr }); if (f && f !== FAIL) { f.release(); n++; } }
      trimCache();
      return n;
    },
    canMorph: () => !lost && !document.hidden,
    invalidate() { needs = true; wake(); },
    // for checking the budgets from the console: salehdigital.gl.stats()
    stats: () => ({ texMB: +(texUsed / MB).toFixed(1), cacheMB: +(cacheBytes / MB).toFixed(1), cacheEntries: cache.size,
      poolMB: pool ? +(pool.w * pool.h * 16 / MB).toFixed(1) : 0, morphs: active.size, dpr, lost, running: !!(raf || timer) })
  };
}
```
