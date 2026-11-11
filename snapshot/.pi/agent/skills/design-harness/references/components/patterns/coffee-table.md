---
title: Coffee table
slug: coffee-table
status: published
description: "Coffee table, \"The table\": books lying on a tabletop seen from above (three.js), the cursor a raking light with SDF shadows; a click lifts a book to you with its details beside it."
chips:
  - Pattern
  - Coffee table
  - WebGL
  - Grid
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:08:52Z
---

The Coffee table section is one grid page ("The shelf"), with no sub-nav (`html.is-solo`). The concept is by Ada ([ada](../../intelligence/agents/ada.md)).

- **Scene.** The books lie on a tabletop seen from above (three.js, FOV 30°). The table *is* the page: pure paper where no shadow falls, so it meets the nav without an edge. The cursor is a soft raking light. Shadows are SDFs, each book a rounded rect projected away from the light, falling toward `--shade`.
- **Hover** lifts a book a few mm.
- **Click** lifts it, squares it to you, and sets its details beside it as plain text on the page (below it on a phone), with no card and no backdrop. On desktop that is the book, a gap, then a text column, centred across the table at the middle of the window. While a book is up, the rest of the table goes soft behind it: depth of field with a 17-tap Gaussian at half resolution, `DOF = { sigma: 11, fade: .16, wash: .55 }`. Clicking it again, clicking the table or pressing Escape sets it down. The buttons over the books carry focus, Enter, `aria-expanded` and the accessible names.
- **Books without a cover** get cloth: `[cloth, stamp colour, finish]`, with the type stamped in the site's faces and a height map for the light. Cloth colours: `--cloth-ink #1c1b19`, `--cloth-stone #d9d4c8`, `--cloth-graphite #45413b`, `--cloth-grey #b8b1a3`, `--cover-paper #ece8df`.
- **Layout.** A masonry of objects, then scattered by Order. On a phone it is one pile down the page, each book overlapping the last as Order rises. A seeded stream per book makes the table look the same on every visit. At most 12 books (`MAX`).
- **Live params.** `--fnd-order` .45 (Stacked neat → Scattered), `--fnd-light` .65 (Flat → Raking), `--fnd-depth` .55 (2px to 34px thick), energy × .8.
- **No WebGL.** A DOM shelf: the other books go soft behind the lifted one.
- **Live content.** "The shelf", 10 books (2026-11-11).

Source: `site/js/grids/table.js`, whole file

```js
// Coffee table, "The table" (concept by Ada). The books lie on a tabletop seen from above
// (three.js). The cursor is a soft raking light; shadows are SDFs, each book a rounded rect
// projected away from the light. Hover lifts a book a few mm. A click lifts it, squares it
// to you and sets its details beside it as plain text on the page (below it on a phone):
// no card, no backdrop. Click it again, click the table or press Escape to set it down.
// The buttons over the books carry focus, Enter, aria-expanded and the accessible names.
import { root, reduced, loadThree, readFnd, gridCanvas, lifetime, disposeGL } from './common.js';
import { onTheme } from '../theme.js';

const MAX = 12;
const css = (n) => getComputedStyle(root).getPropertyValue(n).trim();
const CLOTH_VARS = { '--cloth-ink': '#1c1b19', '--cloth-stone': '#d9d4c8', '--cloth-graphite': '#45413b', '--cloth-grey': '#b8b1a3', '--cover-paper': '#ece8df', '--page-edge': '#efebe2', '--foil-paper': '#f4f1ea', '--foil-gold': '#c2a466' };
// cloth for the books without a cover: [cloth, stamp colour, finish]
const CLOTHS = [
  ['--cover-paper', '#141414', 'print'],
  ['--cloth-ink', '--foil-paper', 'foil'],
  ['--cloth-stone', null, 'blind'],
  ['--cloth-graphite', '--foil-gold', 'foil'],
  ['--cloth-grey', '#141414', 'foil'],
];
const colorOf = (v) => v?.startsWith('--') ? (css(v) || CLOTH_VARS[v]) : v;

// a seeded stream per book, so the table looks the same on every visit
function rng(str) {
  let h = 1779033703 ^ str.length;
  for (let i = 0; i < str.length; i++) { h = Math.imul(h ^ str.charCodeAt(i), 3432918353); h = h << 13 | h >>> 19; }
  return () => { h = Math.imul(h ^ h >>> 16, 2246822507); h = Math.imul(h ^ h >>> 13, 3266489909); return ((h ^= h >>> 16) >>> 0) / 4294967296; };
}

export async function mount({ col, recs, fillDetails, signal }) {
  const life = lifetime(signal);
  const P = { order: 0.45, light: 0.65, depth: 0.55, energy: 0.4 };
  const SCALE = { energy: 0.8 }; // the site's Energy (0.5) reads as this grid's 0.4
  readFnd(P, SCALE);

  // ---------- the DOM shelf: the static fallback and the accessible layer ----------
  const tableEl = document.createElement('div'); tableEl.className = 'ct';
  const shelf = document.createElement('ul'); shelf.className = 'ct-shelf'; shelf.setAttribute('aria-label', 'The shelf');
  const detail = document.createElement('div'); detail.className = 'ct-detail'; detail.id = 'ct-detail'; detail.hidden = true;
  const say = document.createElement('p'); say.className = 'sr-only'; say.setAttribute('aria-live', 'polite');
  tableEl.append(shelf, detail, say);
  col.replaceChildren(tableEl);
  let clothAt = 0;
  const books = recs.map((rec, i) => {
    const li = document.createElement('li');
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'ct-book';
    b.setAttribute('aria-label', `${rec.title}${rec.desc ? ', ' + rec.desc : ''}`);
    b.setAttribute('aria-expanded', 'false'); b.setAttribute('aria-controls', 'ct-detail');
    const book = { i, rec, el: b, li, rand: rng(rec.slug), magazine: /magazine/i.test(rec.title), up: 0, anim: null };
    if (rec.images[0]) {
      const img = new Image(); img.alt = ''; img.decoding = 'async'; img.src = rec.images[0];
      b.append(img); book.img = img;
    } else {
      const [c, f, finish] = CLOTHS[clothAt++ % CLOTHS.length];
      book.cloth = { color: colorOf(c), stamp: f ? colorOf(f) : null, finish };
      const face = document.createElement('span'); face.className = 'ct-cloth';
      face.style.setProperty('--c', book.cloth.color);
      face.style.setProperty('--f', book.cloth.stamp || 'color-mix(in srgb, var(--ink) 55%, var(--c))');
      const t = document.createElement('span'); t.className = 'ct-cloth-title'; t.textContent = rec.title;
      const d = document.createElement('span'); d.className = 'ct-cloth-desc'; d.textContent = rec.desc;
      face.append(t, d); b.append(face);
    }
    li.append(b); shelf.append(li);
    return book;
  });
  life.later(() => root.classList.remove('ct-gl', 'ct-pending', 'ct-open'));

  // ---------- lifting: the shared part (GL or not) ----------
  let presented = null;
  let gl = null; // set when the table draws: { lift(bk), lower(bk), place() }
  function showDetail(bk) {
    fillDetails(detail, bk.rec);
    detail.hidden = false;
    detail.classList.remove('is-in');
    gl?.place(bk); // the static shelf: the details sit under it
    requestAnimationFrame(() => requestAnimationFrame(() => { detail.classList.add('is-in'); gl?.kick(); }));
  }
  function hideDetail() {
    detail.classList.remove('is-in'); gl?.kick();
    if (reduced.matches) { detail.hidden = true; return; }
    setTimeout(() => { if (!presented) detail.hidden = true; }, 200);
  }
  function lift(bk) {
    if (presented === bk) return;
    if (presented) lower(presented, true);
    presented = bk;
    root.classList.add('ct-open');
    bk.el.setAttribute('aria-expanded', 'true'); bk.el.classList.add('is-up');
    say.textContent = `${bk.rec.title}, lifted. Its details follow.`;
    if (gl) gl.lift(bk, () => { if (presented === bk) showDetail(bk); });
    else showDetail(bk);
  }
  function lower(bk, swapping = false) {
    if (!bk) return;
    if (presented === bk) presented = null;
    bk.el.setAttribute('aria-expanded', 'false'); bk.el.classList.remove('is-up');
    if (!swapping) { root.classList.remove('ct-open'); hideDetail(); say.textContent = `${bk.rec.title}, set down.`; }
    else detail.classList.remove('is-in');
    gl?.lower(bk);
  }
  for (const bk of books) life.on(bk.el, 'click', () => presented === bk ? lower(bk) : lift(bk));
  // Escape sets it down (focus stays on, or returns to, the book)
  life.on(document, 'keydown', (e) => {
    if (e.key !== 'Escape' || !presented || document.querySelector('dialog[open]')) return;
    const bk = presented; lower(bk); bk.el.focus({ preventScroll: true });
  });
  // a click on the table (anywhere but a book or its details) sets it down
  life.on(document, 'click', (e) => {
    if (!presented || e.target.closest('.ct-book, .ct-detail, dialog, a, button, input, .debug, [role="dialog"]')) return;
    if (getSelection()?.toString()) return;
    lower(presented);
  });

  // ---------- three ----------
  const THREE = await loadThree();
  if (life.dead || !THREE) return { destroy: () => life.kill() };
  const canvas = gridCanvas('table');
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'high-performance' }); }
  catch { canvas.remove(); root.classList.remove('has-grid-gl'); return { destroy: () => life.kill() }; }
  const scene = new THREE.Scene();
  life.later(() => disposeGL(THREE, renderer, scene, canvas));
  // while the table is being set (covers decoded, type stamped) the plain shelf waits unseen, so it never jumps
  root.classList.add('ct-pending');
  const pendingT = setTimeout(() => root.classList.remove('ct-pending'), 4000);
  life.later(() => clearTimeout(pendingT));

  await Promise.all([
    ...books.filter(b => b.img).map(b => b.img.decode().catch(() => {})),
    document.fonts.load('400 40px "Inter Display"').catch(() => {}),
    document.fonts.load('400 40px "Shinka"').catch(() => {}),
  ]);
  if (life.dead) return null;

  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setClearColor(0xffffff, 1);
  const camera = new THREE.PerspectiveCamera(30, 1, 10, 20000);
  const FOVT = Math.tan(THREE.MathUtils.degToRad(15));
  const aniso = renderer.capabilities.getMaxAnisotropy();

  // shared light and shadow uniforms (the table and every book read the same objects)
  const U = {
    uL: { value: new THREE.Vector3() },
    uAmb: { value: 0.6 }, uKey: { value: 0.4 }, uSoft: { value: 0.3 },
    uPoolR: { value: 900 }, uPoolAmt: { value: 0.3 }, uShadowAmt: { value: 0.35 },
    uA: { value: Array.from({ length: MAX }, () => new THREE.Vector4()) },
    uB: { value: Array.from({ length: MAX }, () => new THREE.Vector4()) },
    uN: { value: 0 },
    // the theme (js/theme.js): the table is the paper, and a shadow falls toward --shade
    uPaper: { value: new THREE.Color(1, 1, 1) }, uShade: { value: new THREE.Color(.70, .69, .67) },
  };
  let shadowK = 1; // on dark paper a shadow has to be deeper to read at all (set from the theme, below)
  // uB.w: how far a book has stepped back while another is lifted (its shadow goes with it)
  const SHADOW = /* glsl */`
    uniform vec3 uL, uPaper, uShade; uniform float uAmb, uKey, uSoft, uPoolR, uPoolAmt, uShadowAmt;
    uniform vec4 uA[${MAX}]; uniform vec4 uB[${MAX}]; uniform int uN;
    float sdRB(vec2 p, vec2 b, float r) { vec2 q = abs(p) - b + r; return length(max(q, 0.)) + min(max(q.x, q.y), 0.) - r; }
    vec2 unrot(vec2 p, float a) { float c = cos(a), s = sin(a); return vec2(c * p.x + s * p.y, -s * p.x + c * p.y); }
    float visibility(vec3 p, int self) {
      float v = 1.;
      for (int i = 0; i < ${MAX}; i++) {
        if (i >= uN) break;
        if (i == self) continue;
        vec4 a = uA[i]; vec4 b = uB[i];
        float zb = a.z, zt = a.z + b.z;
        if (zb < p.z - 0.6) continue;
        if (uL.z <= zt + 1.) continue;
        float h = zt - p.z;
        vec2 qt = p.xy + (uL.xy - p.xy) * (h / (uL.z - p.z));
        vec2 qb = p.xy + (uL.xy - p.xy) * (max(zb - p.z, 0.) / (uL.z - p.z));
        float d = min(sdRB(unrot(qt - a.xy, a.w), b.xy, 2.5), sdRB(unrot(qb - a.xy, a.w), b.xy, 2.5));
        float throwLen = length(qt - p.xy);
        float w = 1.2 + h * uSoft + throwLen * .35;
        float sh = smoothstep(-w, w * 1.2, d);
        float gap = max(zb - p.z, 0.);
        float df = sdRB(unrot(p.xy - a.xy, a.w), b.xy, 2.5);
        float ao = 1. - (1. - smoothstep(-1.5, 4. + b.z * .9 + gap * .8, df)) * exp(-gap / 14.) * .42;
        ao *= 1. - (1. - smoothstep(-1.5, 2.5, df)) * exp(-gap / 4.) * .25;
        v *= mix(mix(1., sh, uShadowAmt / (1. + h * .0035 + throwLen * .012)) * ao, 1., b.w);
      }
      return v;
    }
    float pool(vec3 p) { return mix(1., 1. - smoothstep(uPoolR * .2, uPoolR, length(uL.xy - p.xy)) * .85, uPoolAmt); }
  `;
  const VERT = /* glsl */`
    varying vec3 vW; varying vec3 vN; varying vec2 vUv; varying vec3 vP;
    void main() {
      vUv = uv; vP = position;
      vec4 w = modelMatrix * vec4(position, 1.);
      vW = w.xyz; vN = normalize(mat3(modelMatrix) * normal);
      gl_Position = projectionMatrix * viewMatrix * w;
    }`;
  // the table: the page itself. Pure paper where no shadow falls, so it meets the nav without an edge.
  const table = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.ShaderMaterial({
    uniforms: { ...U }, vertexShader: VERT,
    fragmentShader: /* glsl */`
      ${SHADOW}
      varying vec3 vW;
      float hash(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
      void main() {
        float v = visibility(vec3(vW.xy, 0.), -1);
        vec3 c = mix(uShade, uPaper, v);
        c += (hash(gl_FragCoord.xy) - .5) / 255.;
        gl_FragColor = vec4(c, 1.);
        #include <colorspace_fragment>
      }`,
  }));
  scene.add(table);

  const BOOK_FRAG = /* glsl */`
    ${SHADOW}
    uniform int uSelf; uniform vec3 uColor; uniform sampler2D uMap; uniform sampler2D uNrm;
    uniform float uRot; uniform vec2 uSize; uniform float uThick; uniform float uLit; uniform float uFade;
    varying vec3 vW; varying vec3 vN; varying vec2 vUv; varying vec3 vP;
    void main() {
      vec3 N = normalize(vN);
      vec3 alb = uColor; float foil = 0.;
      #if KIND == 0
        alb = texture2D(uMap, vUv).rgb;
        vec3 nm = texture2D(uNrm, vUv).rgb;
        vec2 n = nm.xy * 2. - 1.; foil = nm.b;
        float c = cos(uRot), s = sin(uRot);
        N = normalize(vec3(c * n.x - s * n.y, s * n.x + c * n.y, 1.));
        vec2 px = vUv * uSize;
        float e = min(min(px.x, uSize.x - px.x), min(px.y, uSize.y - px.y));
        alb *= mix(.82, 1., smoothstep(0., 1.4, e));
      #elif KIND == 2
        float z = (vP.z + .5) * uThick;
        alb *= .95 + .05 * sin(z * 6.2831 / .7);
      #endif
      vec3 Lv = uL - vW; vec3 ld = normalize(Lv);
      float lam = max(dot(N, ld), 0.);
      float vis = visibility(vW, uSelf);
      float pl = pool(vW);
      vec3 col = alb * (uAmb * mix(1., vis, .55) + uKey * lam * pl * vis) * uLit;
      vec3 V = normalize(cameraPosition - vW); vec3 H = normalize(ld + V);
      col += foil * mix(alb, vec3(1.), .35) * (pow(max(dot(N, H), 0.), 40.) * .9 + .1 * lam) * pl * vis;
      gl_FragColor = vec4(col, 1.);
      #include <colorspace_fragment>
    }`;
  const flatNrm = new THREE.DataTexture(new Uint8Array([128, 128, 0, 255]), 1, 1); flatNrm.needsUpdate = true;
  const box = new THREE.BoxGeometry(1, 1, 1);
  life.later(() => { flatNrm.dispose(); box.dispose(); });
  function mat(kind, bk, extra = {}) {
    return new THREE.ShaderMaterial({
      uniforms: { ...U, uSelf: { value: bk.i }, uColor: { value: new THREE.Color(extra.color || '#fff') },
        uMap: { value: extra.map || flatNrm }, uNrm: { value: extra.nrm || flatNrm }, uRot: { value: 0 },
        uSize: { value: new THREE.Vector2(1, 1) }, uThick: { value: 1 }, uLit: { value: 1 }, uFade: { value: 0 } },
      defines: { KIND: kind }, vertexShader: VERT, fragmentShader: BOOK_FRAG,
    });
  }

  // ---------- the cloth covers: type stamped in the site's faces, with a height map for the light ----------
  function wrapText(ctx, text, maxW) {
    const words = text.split(/\s+/); const lines = []; let line = '';
    for (const w of words) { const t = line ? line + ' ' + w : w; if (ctx.measureText(t).width > maxW && line) { lines.push(line); line = w; } else line = t; }
    if (line) lines.push(line);
    return lines;
  }
  function balanced(ctx, text, maxW) {
    const n = wrapText(ctx, text, maxW).length; let w = maxW;
    while (w > maxW * .5 && wrapText(ctx, text, w - 8).length === n) w -= 8;
    return wrapText(ctx, text, w);
  }
  function clothTextures(bk, aspect) {
    const W = 768, H = Math.round(W / aspect);
    const { color, stamp, finish } = bk.cloth;
    const mk = () => { const c = document.createElement('canvas'); c.width = W; c.height = H; return [c, c.getContext('2d', { willReadFrequently: true })]; };
    const [ac, a] = mk(); const [, h] = mk(); const [, f] = mk();
    const r = rng(bk.rec.slug + 'cloth');
    a.fillStyle = color; a.fillRect(0, 0, W, H);
    const id = a.getImageData(0, 0, W, H); const d = id.data;
    const weave = finish === 'print' ? 3 : 9;
    for (let p = 0; p < d.length; p += 4) { const k = (r() - .5) * weave; d[p] += k; d[p + 1] += k; d[p + 2] += k; }
    a.putImageData(id, 0, 0);
    h.fillStyle = '#fff'; h.fillRect(0, 0, W, H);
    if (finish !== 'print') {
      const hd = h.getImageData(0, 0, W, H); const q = hd.data;
      for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
        const v = 235 + 20 * (0.5 + 0.25 * Math.sin(x * 2.1) + 0.25 * Math.sin(y * 2.3)) * (0.6 + 0.4 * r());
        const o = (y * W + x) * 4; q[o] = q[o + 1] = q[o + 2] = v;
      }
      h.putImageData(hd, 0, 0);
    }
    f.fillStyle = '#000'; f.fillRect(0, 0, W, H);
    const m = W * .085, ts = W * .082;
    const set = (ctx, style) => {
      ctx.fillStyle = style; ctx.textBaseline = 'alphabetic';
      ctx.font = `400 ${ts}px "Inter Display"`; ctx.letterSpacing = `${-ts * .04}px`;
      balanced(ctx, bk.rec.title, W - m * 2.2).forEach((l, i) => ctx.fillText(l, m, m + ts * .8 + i * ts * 1.08));
      const ds = ts * .5;
      ctx.font = `400 ${ds}px "Shinka"`; ctx.letterSpacing = `${-ds * .02}px`;
      const dl = wrapText(ctx, bk.rec.desc, W * .62);
      dl.forEach((l, i) => ctx.fillText(l, m, H - m - (dl.length - 1 - i) * ds * 1.3));
    };
    set(a, finish === 'blind' ? 'rgba(0,0,0,.16)' : stamp);
    if (finish !== 'print') { h.filter = 'blur(1.2px)'; set(h, '#555'); h.filter = 'none'; }
    if (finish === 'foil') set(f, '#fff');
    const hd = h.getImageData(0, 0, W, H).data, fd = f.getImageData(0, 0, W, H).data;
    const out = new Uint8Array(W * H * 4); const S = finish === 'blind' ? 5 : 3.2;
    const at = (x, y) => hd[((Math.min(H - 1, Math.max(0, y))) * W + Math.min(W - 1, Math.max(0, x))) * 4] / 255;
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const dx = (at(x + 1, y) - at(x - 1, y)) * S, dy = (at(x, y + 1) - at(x, y - 1)) * S;
      const l = Math.hypot(dx, dy, 1);
      const o = ((H - 1 - y) * W + x) * 4;
      out[o] = (-dx / l * .5 + .5) * 255; out[o + 1] = (dy / l * .5 + .5) * 255; out[o + 2] = fd[(y * W + x) * 4]; out[o + 3] = 255;
    }
    const map = new THREE.CanvasTexture(ac); map.colorSpace = THREE.SRGBColorSpace; map.anisotropy = aniso;
    const nrm = new THREE.DataTexture(out, W, H); nrm.needsUpdate = true; nrm.anisotropy = aniso;
    nrm.generateMipmaps = true; nrm.minFilter = THREE.LinearMipmapLinearFilter; nrm.magFilter = THREE.LinearFilter;
    return { map, nrm };
  }
  function avgColor(img) {
    const c = document.createElement('canvas'); c.width = c.height = 8; const x = c.getContext('2d', { willReadFrequently: true });
    x.drawImage(img, 0, 0, 8, 8); const d = x.getImageData(0, 0, 8, 8).data; let r = 0, g = 0, b = 0;
    for (let i = 0; i < d.length; i += 4) { r += d[i]; g += d[i + 1]; b += d[i + 2]; }
    const n = d.length / 4;
    return new THREE.Color(`rgb(${Math.round(r / n * .72)},${Math.round(g / n * .72)},${Math.round(b / n * .72)})`);
  }

  // ---------- springs ----------
  const spring = (x = 0) => ({ x, v: 0, t: x });
  function stepSpring(s, dt) {
    const k = 140 + 240 * P.energy, z = 1 - 0.42 * P.energy, c = 2 * z * Math.sqrt(k);
    const a = -k * (s.x - s.t) - c * s.v;
    s.v += a * dt; s.x += s.v * dt;
    if (Math.abs(s.x - s.t) < 0.005 && Math.abs(s.v) < 0.005) { s.x = s.t; s.v = 0; return false; }
    return true;
  }
  // the site's landing curve, cubic-bezier(0.2, 0, 0, 1)
  function land(t) {
    let lo = 0, hi = 1, u = t;
    for (let i = 0; i < 24; i++) { u = (lo + hi) / 2; const x = 3 * (1 - u) * (1 - u) * u * .2 + u * u * u; if (x < t) lo = u; else hi = u; }
    return 3 * (1 - u) * u * u + u * u * u;
  }

  // ---------- build the books ----------
  const CLOTH_ASPECT = [0.74, 0.78, 0.82, 0.7, 0.9];
  const pageCol = colorOf('--page-edge');
  books.forEach((bk, k) => {
    const r = bk.rand;
    bk.aspect = bk.img?.naturalWidth ? bk.img.naturalWidth / bk.img.naturalHeight : (bk.magazine ? 0.75 : CLOTH_ASPECT[k % CLOTH_ASPECT.length]);
    bk.size = 0.8 + 0.18 * r();
    bk.thickF = bk.magazine ? 0.16 : 0.75 + 0.4 * r();
    bk.jx = r() * 2 - 1; bk.jy = r() * 2 - 1; bk.jr = r() * 2 - 1;
    let topMat, edge;
    if (bk.img?.naturalWidth) {
      const map = new THREE.Texture(bk.img); map.colorSpace = THREE.SRGBColorSpace; map.anisotropy = aniso; map.needsUpdate = true;
      topMat = mat(0, bk, { map }); edge = avgColor(bk.img);
    } else {
      bk.cloth ||= { color: colorOf('--cloth-stone'), stamp: null, finish: 'blind' };
      const t = clothTextures(bk, bk.aspect);
      topMat = mat(0, bk, { map: t.map, nrm: t.nrm }); edge = new THREE.Color(bk.cloth.color);
    }
    const clothMat = mat(1, bk, { color: edge });
    const pagesMat = mat(2, bk, { color: pageCol });
    bk.mats = [topMat, clothMat, pagesMat];
    bk.g = new THREE.Group();
    bk.top = new THREE.Mesh(box, [clothMat, clothMat, clothMat, clothMat, topMat, clothMat]);
    bk.bottom = new THREE.Mesh(box, clothMat);
    bk.pages = new THREE.Mesh(box, pagesMat);
    bk.spine = new THREE.Mesh(box, bk.magazine ? pagesMat : clothMat);
    bk.g.add(bk.bottom, bk.pages, bk.top, bk.spine);
    scene.add(bk.g);
    bk.lift = spring(); bk.tx = spring(); bk.ty = spring(); bk.fade = 0;
  });

  // ---------- layout: a masonry of objects, then scattered by Order ----------
  let vw = 0, vh = 0, tableH = 0, phone = false;
  function layout() {
    vw = innerWidth; vh = innerHeight; phone = vw < 900;
    const rect = tableEl.getBoundingClientRect();
    const x0 = rect.left + scrollX, y0 = rect.top + scrollY, W = rect.width;
    const o = P.order, T = 2 + 32 * P.depth;
    if (!phone) {
      const gap = 48, n = Math.max(2, Math.min(4, Math.floor((W + gap) / (280 + gap))));
      const cw = (W - gap * (n - 1)) / n;
      const colH = new Array(n).fill(14);
      for (const bk of books) {
        let w = cw * bk.size, h = w / bk.aspect;
        if (h > cw * 1.42) { h = cw * 1.42; w = h * bk.aspect; }
        let c = 0; colH.forEach((v, j) => { if (v < colH[c] - 1) c = j; });
        bk.w = w; bk.h = h;
        bk.x = x0 + c * (cw + gap) + cw / 2 + o * (bk.jx * ((cw - w) / 2 + gap * .45));
        bk.y = y0 + colH[c] + h / 2 + o * bk.jy * gap * .5;
        bk.rot = o * bk.jr * 0.2;
        bk.x = Math.min(x0 + W - w / 2 - 8, Math.max(x0 + w / 2 + 8, bk.x));
        colH[c] += h + gap * (1 - o * .35);
      }
      tableH = Math.max(...colH) + 40;
    } else {
      // phone: one pile down the page, each book overlapping the last as Order rises
      let y = 10;
      for (const bk of books) {
        let w = W * (0.56 + 0.16 * bk.size), h = w / bk.aspect;
        if (h > W * .9) { h = W * .9; w = h * bk.aspect; }
        bk.w = w; bk.h = h;
        bk.x = x0 + W / 2 + o * bk.jx * (W - w) * .45;
        bk.y = y0 + y + h / 2;
        bk.rot = o * bk.jr * 0.14;
        y += h + 24 - o * (h * .14 + 24);
      }
      tableH = y + 60;
    }
    for (const bk of books) bk.T = Math.max(1.2, T * bk.thickF);
    // books that overlap rest on the ones before them
    books.forEach((bk, i) => {
      bk.base = 0;
      for (let j = 0; j < i; j++) if (overlap(bk, books[j])) bk.base = Math.max(bk.base, books[j].base + books[j].T);
    });
    books.forEach(sizeBook);
    if (presented) place(presented); else setHeight();
  }
  let extraH = 0;
  const setHeight = () => tableEl.style.setProperty('--table-h', `${Math.ceil(Math.max(tableH, extraH))}px`);
  function corners(b) {
    const c = Math.cos(b.rot), s = Math.sin(b.rot), hw = b.w / 2, hh = b.h / 2;
    return [[-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh]].map(([x, y]) => [b.x + c * x - s * y, b.y + s * x + c * y]);
  }
  function overlap(a, b) {
    const A = corners(a), B = corners(b);
    for (const poly of [A, B]) for (let i = 0; i < 4; i++) {
      const p = poly[i], q = poly[(i + 1) % 4], nx = q[1] - p[1], ny = p[0] - q[0];
      const pa = A.map(v => v[0] * nx + v[1] * ny), pb = B.map(v => v[0] * nx + v[1] * ny);
      if (Math.max(...pa) < Math.min(...pb) + 2 || Math.max(...pb) < Math.min(...pa) + 2) return false;
    }
    return true;
  }
  function sizeBook(bk) {
    const { w, h, T } = bk, mag = bk.magazine;
    const board = mag ? T * .12 : Math.min(2.2, T * .14);
    const over = mag ? 0 : Math.min(3, T * .15);
    const spineW = mag ? 0.01 : Math.min(T * .3, 5);
    const pw = w - over - spineW, ph = h - over * 2, pt = Math.max(.01, T - board * 2);
    bk.bottom.scale.set(w, h, board); bk.bottom.position.set(0, 0, board / 2);
    bk.top.scale.set(w, h, board); bk.top.position.set(0, 0, T - board / 2);
    bk.pages.scale.set(pw, ph, pt); bk.pages.position.set(-w / 2 + spineW + pw / 2, 0, board + pt / 2);
    bk.spine.scale.set(spineW, h, T); bk.spine.position.set(-w / 2 + spineW / 2, 0, T / 2);
    for (const m of bk.mats) { m.uniforms.uSize.value.set(w, h); m.uniforms.uThick.value = m === bk.mats[2] ? pt : T; }
  }

  // ---------- where a lifted book goes, and its details beside (or under) it ----------
  // The target is in page px (it scrolls with the page, with the text), at a height that
  // shows its top face at scale bk.s. Desktop: the book, a gap, then a text column, centred
  // across the table at the middle of the window. Phone: the book at the top, the text under it.
  function place(bk) {
    const r = tableEl.getBoundingClientRect();
    const ox = r.left + scrollX, oy = r.top + scrollY;
    let s, textW, tx, ty, cx, cy;
    if (!phone) {
      textW = Math.min(400, Math.max(280, r.width * 0.34));
      const gap = 56;
      s = Math.min(1.3, (vh * 0.74) / bk.h, Math.max(0.6, (r.width - textW - gap - 32) / bk.w));
      const bw = bk.w * s, bh = bk.h * s, groupW = bw + gap + textW;
      const left = r.left + Math.max(0, (r.width - groupW) / 2);
      cx = left + bw / 2 + scrollX;
      cy = Math.max(r.top + bh / 2 + 16, vh / 2) + scrollY;
      tx = left + bw + gap + scrollX; ty = cy - bh / 2;
    } else {
      textW = r.width;
      s = Math.min(1.12, (vh * 0.5) / bk.h, (r.width - 24) / bk.w);
      const bh = bk.h * s;
      cx = r.left + r.width / 2 + scrollX;
      cy = Math.max(r.top, 16) + bh / 2 + 8 + scrollY;
      tx = r.left + scrollX; ty = cy + bh / 2 + 24;
    }
    bk.s = s; bk.goX = cx; bk.goY = cy;
    wash = { x: tx, y: ty, w: textW };
    detail.style.width = `${textW}px`;
    detail.style.transform = `translate(${Math.round(tx - ox)}px, ${Math.round(ty - oy)}px)`;
    extraH = ty - oy + detail.offsetHeight + 48;
    setHeight();
  }

  // ---------- light ----------
  const light = { x: spring(), y: spring(), on: false };
  function lightParams() {
    const l = P.light;
    U.uAmb.value = 0.8 - 0.3 * l; U.uKey.value = 1 - U.uAmb.value + 0.06 * l;
    U.uSoft.value = 0.75 - 0.6 * l;
    U.uPoolR.value = 1500 - 800 * l; U.uPoolAmt.value = 0.55 * l;
    U.uShadowAmt.value = (0.26 + 0.18 * l) * shadowK;
    return 240 + 2300 * (1 - l) * (1 - l); // the light's height above the table
  }
  function restLight() {
    const r = tableEl.getBoundingClientRect();
    return [Math.max(r.left, 0) + Math.min(r.width, vw) * .2, vh * .18];
  }

  // ---------- frame ----------
  let last = 0, running = false, washK = 0;
  const kick = () => { if (!running && !life.dead) { running = true; life.frame(frame); } };
  life.later(onTheme((c) => {
    U.uPaper.value.setRGB(...c.paper, THREE.SRGBColorSpace);
    U.uShade.value.setRGB(...c.shade, THREE.SRGBColorSpace);
    renderer.setClearColor(U.uPaper.value, 1);
    shadowK = c.dark ? 1.6 : 1;
    lightParams(); kick();
  }));
  function frame(t) {
    running = false;
    const dt = Math.min(1 / 30, last ? (t - last) / 1000 : 1 / 60); last = t;
    let busy = false;
    for (const bk of books) { busy = stepSpring(bk.lift, dt) | busy; busy = stepSpring(bk.tx, dt) | busy; busy = stepSpring(bk.ty, dt) | busy; }
    busy = stepSpring(light.x, dt) | busy; busy = stepSpring(light.y, dt) | busy;
    for (const bk of books) {
      const a = bk.anim; if (!a) continue;
      const p = a.dur ? Math.min(1, (t - a.t0) / a.dur) : 1;
      bk.up = a.from + (a.to - a.from) * land(p);
      if (a.at != null && p >= a.at) { const f = a.fire; a.at = null; f?.(); }
      if (p >= 1) { bk.anim = null; a.done?.(); } else busy = true;
    }
    // the paper wash under the details comes and goes with the text
    const washTo = presented && detail.classList.contains('is-in') ? 1 : 0, fk = reduced.matches ? 1 : 1 - Math.exp(-dt * 9);
    washK += (washTo - washK) * fk;
    if (Math.abs(washTo - washK) > 0.002) busy = true; else washK = washTo;
    draw();
    if (busy) kick(); else last = 0;
  }
  function draw() {
    const D = (vh / 2) / FOVT;
    const camX = scrollX + vw / 2, camY = -(scrollY + vh / 2);
    camera.position.set(camX, camY, D); camera.lookAt(camX, camY, 0);
    camera.aspect = vw / vh; camera.near = D * .05; camera.far = D * 2; camera.updateProjectionMatrix();
    table.scale.set(vw * 1.4, vh * 1.4, 1); table.position.set(camX, camY, 0);
    const lz = lightParams();
    U.uL.value.set(camX + light.x.x - vw / 2, camY - (light.y.x - vh / 2), lz);
    U.uN.value = books.length;
    const r = tableEl.getBoundingClientRect();
    const ox = r.left + scrollX, oy = r.top + scrollY;
    books.forEach((bk, i) => {
      const u = bk.up;
      // lifted: toward you, squared, its top face landing on the target at scale bk.s
      let px = bk.x, py = bk.y, zb = bk.base + bk.lift.x;
      if (u > 0 && bk.s) {
        const zT = Math.max(0, D * (1 - 1 / bk.s) - bk.T);
        const sT = D / (D - zT - bk.T);
        const gx = scrollX + vw / 2 + (bk.goX - (scrollX + vw / 2)) / sT;
        const gy = scrollY + vh / 2 + (bk.goY - (scrollY + vh / 2)) / sT;
        px = bk.x + (gx - bk.x) * u; py = bk.y + (gy - bk.y) * u; zb = zb * (1 - u) + zT * u;
      }
      const rot = bk.rot * (1 - u);
      bk.g.position.set(px, -py, zb);
      bk.g.rotation.set(bk.tx.x * (1 - u), bk.ty.x * (1 - u), -rot);
      for (const m of bk.mats) m.uniforms.uRot.value = -rot;
      U.uA.value[i].set(px, -py, zb, -rot);
      U.uB.value[i].set(bk.w / 2, bk.h / 2, bk.T, 0);
      // the button over it, where the top face lands on screen
      const s = D / (D - (zb + bk.T));
      const sx = vw / 2 + (px - camX) * s + scrollX, sy = vh / 2 + (py - (scrollY + vh / 2)) * s + scrollY;
      bk.el.style.width = `${bk.w * s}px`; bk.el.style.height = `${bk.h * s}px`;
      bk.el.style.transform = `translate(${sx - ox - bk.w * s / 2}px, ${sy - oy - bk.h * s / 2}px) rotate(${rot}rad)`;
    });
    // depth of field: while a book is up, the rest of the table goes soft behind it. The amount
    // follows the lifted book's own present/settle curve (bk.up), so the two move as one.
    const sharp = books.filter(b => b.up > 0.001);
    const k = sharp.reduce((m, b) => Math.max(m, b.up), 0);
    if (!k) { renderer.render(scene, camera); return; }
    renderDof(sharp, k);
  }

  // ---------- the depth of field: the others drawn small, blurred, then the lifted book sharp on top ----------
  // Lazily made on the first lift, sized at half the CSS resolution (so a quarter of the pixels at
  // 1x, a sixteenth at 2x), half-float so dark themes don't band. Disposed when the section goes.
  const DOF = { sigma: 11, fade: 0.16, wash: 0.55 }; // blur in CSS px at full lift; a light paper fade; the wash under the text
  let post = null;
  function makePost() {
    const o = { type: THREE.HalfFloatType, depthBuffer: true, stencilBuffer: false };
    const a = new THREE.WebGLRenderTarget(2, 2, o), b = new THREE.WebGLRenderTarget(2, 2, { ...o, depthBuffer: false });
    const quad = new THREE.PlaneGeometry(2, 2);
    const QV = /* glsl */`varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`;
    const blur = new THREE.ShaderMaterial({
      uniforms: { tSrc: { value: null }, uDir: { value: new THREE.Vector2() } },
      vertexShader: QV, depthTest: false, depthWrite: false,
      // a 17-tap Gaussian, taps spaced so they span ±2.5 sigma at any radius (uDir carries sigma / 3.2 in uv)
      fragmentShader: /* glsl */`
        uniform sampler2D tSrc; uniform vec2 uDir; varying vec2 vUv;
        void main() {
          vec4 s = vec4(0.); float wt = 0.;
          for (int i = -8; i <= 8; i++) { float f = float(i); float w = exp(-.5 * f * f / 10.24); s += texture2D(tSrc, vUv + uDir * f) * w; wt += w; }
          gl_FragColor = s / wt;
        }`,
    });
    const comp = new THREE.ShaderMaterial({
      uniforms: { tSrc: { value: b.texture }, uK: { value: 0 }, uA: { value: 1 }, uFade: { value: 0 }, uPaper: U.uPaper,
        uWash: { value: new THREE.Vector4() }, uWashAmt: { value: 0 }, uRes: { value: new THREE.Vector2(1, 1) } },
      vertexShader: QV, transparent: true, depthTest: false, depthWrite: false,
      fragmentShader: /* glsl */`
        uniform sampler2D tSrc; uniform float uK, uA, uFade, uWashAmt; uniform vec3 uPaper; uniform vec4 uWash; uniform vec2 uRes;
        varying vec2 vUv;
        float sdBox(vec2 p, vec2 b) { vec2 q = abs(p) - b; return length(max(q, 0.)) + min(max(q.x, q.y), 0.); }
        void main() {
          vec3 c = texture2D(tSrc, vUv).rgb;
          c = mix(c, uPaper, uFade * uK);
          // a soft paper wash under the details text: no edge, just more paper where the words sit
          vec2 p = vec2(vUv.x, 1. - vUv.y) * uRes;
          float d = sdBox(p - uWash.xy, uWash.zw);
          c = mix(c, uPaper, uWashAmt * uK * (1. - smoothstep(-24., 72., d)));
          gl_FragColor = vec4(c, uA);
          #include <colorspace_fragment>
        }`,
    });
    const scn = new THREE.Scene(); const mesh = new THREE.Mesh(quad, blur); mesh.frustumCulled = false; scn.add(mesh);
    const cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    return { a, b, blur, comp, scn, mesh, cam, w: 0, h: 0, quad };
  }
  function sizePost() {
    if (!post) return;
    const w = Math.max(2, Math.ceil(vw / 2)), h = Math.max(2, Math.ceil(vh / 2));
    if (w === post.w && h === post.h) return;
    post.w = w; post.h = h; post.a.setSize(w, h); post.b.setSize(w, h);
  }
  life.later(() => { if (!post) return; post.a.dispose(); post.b.dispose(); post.blur.dispose(); post.comp.dispose(); post.quad.dispose(); post = null; });
  let wash = null; // the details' box in page px, set by place()
  function renderDof(sharp, k) {
    if (!post) { post = makePost(); sizePost(); }
    const { a, b, blur, comp, scn, mesh, cam } = post;
    const auto = renderer.autoClear;
    // 1. the table and the other books, at half resolution
    sharp.forEach(s => { s.g.visible = false; });
    renderer.setRenderTarget(a); renderer.clear(); renderer.render(scene, camera);
    // 2. blur, horizontal then vertical; the radius grows with the lift, so it focuses in rather than switching
    const sg = (DOF.sigma * k) / 2 / 3.2; // in half-res px per tap
    mesh.material = blur;
    blur.uniforms.tSrc.value = a.texture; blur.uniforms.uDir.value.set(sg / post.w, 0);
    renderer.setRenderTarget(b); renderer.render(scn, cam);
    blur.uniforms.tSrc.value = b.texture; blur.uniforms.uDir.value.set(0, sg / post.h);
    renderer.setRenderTarget(a); renderer.render(scn, cam);
    renderer.setRenderTarget(null);
    // 3. the screen: early in the lift the sharp table shows through (the half-res layer would look soft at once)
    renderer.autoClear = false;
    renderer.clear();
    const A = Math.min(1, k / 0.3);
    if (A < 1) renderer.render(scene, camera);
    mesh.material = comp;
    comp.uniforms.tSrc.value = a.texture;
    comp.uniforms.uK.value = k; comp.uniforms.uA.value = A * A * (3 - 2 * A); comp.uniforms.uFade.value = DOF.fade;
    comp.uniforms.uRes.value.set(vw, vh);
    if (wash && presented && !detail.hidden) {
      const hw = wash.w / 2, hh = Math.max(40, detail.offsetHeight) / 2;
      comp.uniforms.uWash.value.set(wash.x - scrollX + hw, wash.y - scrollY + hh, hw, hh);
      comp.uniforms.uWashAmt.value = DOF.wash * washK;
    } else comp.uniforms.uWashAmt.value = 0;
    renderer.render(scn, cam);
    // 4. the lifted book, sharp, over it all
    renderer.clearDepth();
    table.visible = false;
    for (const bk of books) bk.g.visible = sharp.includes(bk);
    renderer.render(scene, camera);
    table.visible = true; for (const bk of books) bk.g.visible = true;
    renderer.autoClear = auto;
  }
  function resize() {
    renderer.setSize(innerWidth, innerHeight, false);
    vw = innerWidth; vh = innerHeight; sizePost();
    layout();
    if (!light.on) { const [x, y] = restLight(); light.x.x = light.x.t = x; light.y.x = light.y.t = y; }
    kick();
  }

  // ---------- interaction ----------
  let hovered = null;
  const liftH = () => 5 + 11 * P.energy;
  function hover(bk) {
    if (hovered === bk) return;
    if (hovered && hovered !== presented) { hovered.lift.t = 0; hovered.tx.t = 0; hovered.ty.t = 0; }
    hovered = bk;
    if (bk && !reduced.matches) bk.lift.t = liftH();
    if (reduced.matches && bk) bk.lift.x = bk.lift.t = 0;
    kick();
  }
  function moveLight(x, y, snap) {
    if (reduced.matches) return;
    light.on = true; light.x.t = x; light.y.t = y;
    if (snap) { light.x.x = x; light.y.x = y; }
    kick();
  }
  life.on(window, 'pointermove', (e) => {
    if (presented) return;
    moveLight(e.clientX, e.clientY, e.pointerType !== 'mouse');
    if (hovered && !reduced.matches) {
      // lively: the book tips a degree or two toward the light, as if a finger pressed its corner
      const r = hovered.el.getBoundingClientRect();
      const nx = ((e.clientX - r.left) / r.width - .5), ny = ((e.clientY - r.top) / r.height - .5);
      const a = 0.05 * P.energy;
      hovered.ty.t = -nx * a; hovered.tx.t = -ny * a;
    }
  }, { passive: true });
  life.on(root, 'pointerleave', () => {
    if (presented) return;
    light.on = false; const [x, y] = restLight(); light.x.t = x; light.y.t = y; hover(null);
  });
  for (const bk of books) {
    life.on(bk.el, 'pointerenter', (e) => { if (!presented && e.pointerType === 'mouse') hover(bk); });
    life.on(bk.el, 'pointerleave', (e) => { if (!presented && e.pointerType === 'mouse' && hovered === bk) hover(null); });
    life.on(bk.el, 'focus', () => {
      if (presented || !bk.el.matches(':focus-visible')) return;
      hover(bk);
      const r = bk.el.getBoundingClientRect();
      moveLight(r.left + r.width * .2, r.top + r.height * .15);
    });
    life.on(bk.el, 'blur', () => { if (!presented && hovered === bk) hover(null); });
  }

  const still = () => reduced.matches;
  gl = {
    place, kick,
    lift(bk, then) {
      hover(bk); bk.tx.t = bk.ty.t = 0;
      place(bk);
      moveLight(vw * .32, vh * .2);
      bk.anim = { from: bk.up, to: 1, t0: performance.now(), dur: still() ? 0 : 560, at: still() ? 0 : .55, fire: then };
      kick();
    },
    lower(bk) {
      bk.anim = { from: bk.up, to: 0, t0: performance.now(), dur: still() ? 0 : 480, done: () => {
        if (!bk.el.matches(':hover') && !bk.el.matches(':focus-visible') && hovered === bk) hover(null);
        else if (hovered !== bk) { bk.lift.t = 0; }
        if (!presented) { extraH = 0; setHeight(); }
      } };
      if (!presented) { light.on = false; const [x, y] = restLight(); light.x.t = x; light.y.t = y; }
      kick();
    },
  };

  life.on(window, 'resize', resize);
  life.on(window, 'scroll', kick, { passive: true });
  life.on(reduced, 'change', () => { books.forEach(b => { b.lift.x = b.lift.t = 0; }); resize(); });
  const reparams = () => { if (readFnd(P, SCALE)) { layout(); if (hovered) hovered.lift.t = liftH(); kick(); } };
  const iv = setInterval(() => { if (!document.hidden) reparams(); }, 400);
  life.later(() => clearInterval(iv));
  const ro = new ResizeObserver(() => resize());
  ro.observe(tableEl);
  life.later(() => ro.disconnect());

  root.classList.add('ct-gl');
  resize();
  root.classList.remove('ct-pending');
  // a book lifted before the table was set: lift it here too
  if (presented) { const bk = presented; presented = null; detail.hidden = true; lift(bk); }
  // dev hook: ?lift=N lifts the Nth book (1-based) once the table is set
  const liftQ = Number(new URLSearchParams(location.search).get('lift'));
  if (liftQ && books[liftQ - 1] && !presented) lift(books[liftQ - 1]);
  return { destroy: () => life.kill() };
}
```


Source: `site/css/site.css`, lines 703 to 739

```css
/* Coffee table, "The table": the books as objects on the page, seen from above. A lifted book's details sit beside it as text. */
.ct { position: relative; min-width: 0;
  --cloth-ink: #1c1b19; --cloth-stone: #d9d4c8; --cloth-graphite: #45413b; --cloth-grey: #b8b1a3;
  --cover-paper: #ece8df; --page-edge: #efebe2; --foil-paper: #f4f1ea; --foil-gold: #c2a466; }
.ct-shelf { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 24px; align-items: start; }
.ct-book { display: flex; flex-direction: column; gap: 8px; width: 100%; padding: 0; text-align: left; color: var(--ink); cursor: pointer; border-radius: 2px; -webkit-tap-highlight-color: transparent; }
.ct-book img { display: block; width: 100%; height: auto; border-radius: 2px; box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 8%, transparent), 0 10px 24px -14px color-mix(in srgb, var(--shadow) calc(40% * var(--shadow-k)), transparent); }
.ct-cloth { display: flex; flex-direction: column; aspect-ratio: 3 / 4; padding: 16px; border-radius: 2px; background: var(--c, var(--cloth-stone)); color: var(--f, var(--ink)); }
.ct-cloth-title { font: 400 20px/24px var(--ui); letter-spacing: -0.8px; text-wrap: balance; }
.ct-cloth-desc { margin-top: auto; font: 400 14px/18px var(--serif); letter-spacing: var(--track); opacity: .72; }
.ct-book:focus-visible { outline: 1px solid var(--ring); outline-offset: 4px; }
.ct-book.is-up img, .ct-book.is-up .ct-cloth { outline: 1px solid var(--ink); outline-offset: 4px; }
html.ct-pending:not(.ct-gl) .ct-shelf { visibility: hidden; }
/* with the table drawing: the buttons sit over the drawn books, for the cursor, focus and screen readers */
html.ct-gl .ct { height: var(--table-h, 100vh); }
html.ct-gl .ct-shelf { display: block; position: absolute; left: 0; top: 0; width: 100%; height: 100%; }
html.ct-gl .ct-shelf li { display: contents; }
html.ct-gl .ct-book { position: absolute; left: 0; top: 0; display: block; transform-origin: 50% 50%; will-change: transform; background: none; }
html.ct-gl .ct-book > * { visibility: hidden; }
html.ct-gl .ct-book:focus-visible { outline-offset: 5px; }
html.ct-gl .ct-book.is-up:focus-visible { outline-color: transparent; }
html.ct-open .ct-book:not(.is-up) { cursor: default; }
/* no WebGL: the other books go soft behind the lifted one, as the table does in GL */
html:not(.ct-gl) .ct-book img, html:not(.ct-gl) .ct-book .ct-cloth { transition: filter 560ms var(--ease-land), opacity 560ms var(--ease-land); }
html.ct-open:not(.ct-gl) .ct-book:not(.is-up) :is(img, .ct-cloth) { filter: blur(6px); opacity: .84; }
@media (prefers-reduced-motion: reduce) { html:not(.ct-gl) .ct-book :is(img, .ct-cloth) { transition: none; } }
/* the details: plain text on the page, in the site's type */
.ct-detail { display: flex; flex-direction: column; gap: 6px; max-width: 60ch; margin-top: 32px;
  opacity: 0; filter: blur(4px); transition: opacity 280ms var(--ease-land), filter 320ms var(--ease-land); }
.ct-detail.is-in { opacity: 1; filter: blur(0); }
.ct-detail[hidden] { display: none; }
html.ct-gl .ct-detail { position: absolute; left: 0; top: 0; margin: 0; max-width: none; }
.ct-detail .info-chips { margin-top: 6px; }
.ct-detail .info-body { margin-top: calc(var(--para) - 6px); }
@media (prefers-reduced-motion: reduce) { .ct-detail { filter: none; transition: none; } }
@media (max-width: 899px) { .ct-shelf { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; } }
```
