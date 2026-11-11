---
title: WebGL wordmark
slug: webgl-wordmark
status: published
description: "How the page drives the GL layer: markup, CSS, fonts, boot order, fitting the wordmark and its per-glyph and Arabic fields, the footer pass, the no-WebGL and lite fallbacks, pointer, hold and letter hooks with their sound and haptics, reduced motion, and js/raster.js."
chips:
  - Motion
  - WebGL
  - Wordmark
  - Interaction
created: 2026-11-11T16:30:12Z
updated: 2026-11-11T16:30:12Z
---

How the page drives the GL layer: which DOM it reads, in what order, and what happens when there is no WebGL. The renderer itself is in [WebGL renderer](webgl-renderer.md), the GLSL in [WebGL shaders](webgl-shaders.md).

## The markup

The footer holds the real DOM: the bio, the basmala, two `canvas.foot-dots` strips, the marks list, the foot links, and the SVG wordmark. `#gl` is the last thing in `<body>` before the scripts. The SVG filters in `svg.defs` are the DOM's ink (used when GL is off, and always for the UI type).

Source: `site/index.html`, lines 149 to 167

```html
  <footer class="foot">
    <div class="foot-row">
      <!-- bio on the left, the basmala in the centre, the marks on the right; an SDF dot matrix fills each gap (js/footdots.js) -->
      <div class="foot-side">
        <p class="bio">Ahmed Saleh <span lang="ar" dir="rtl">أحمد صالح</span> is a designer-founder in pursuit of the infinite.</p>
        <canvas class="foot-dots" aria-hidden="true"></canvas>
      </div>
      <p class="basmala" lang="ar" dir="rtl">بسم الله الرحمن الرحيم</p>
      <div class="foot-side foot-end">
        <canvas class="foot-dots" aria-hidden="true"></canvas>
        <ul class="foot-links" id="foot-links" aria-label="More" hidden></ul>
        <ul class="marks" id="marks" aria-label="Marks"></ul>
      </div>
    </div>
    <svg class="wordmark" role="img" aria-label="salehdigital" tabindex="0" width="1920" height="100"><text x="6" y="90" font-size="120">salehdigital</text></svg>
  </footer>
</div>

<canvas id="gl" aria-hidden="true"></canvas>
```

Source: `site/index.html`, lines 52 to 119

```html
<svg class="defs" width="0" height="0" aria-hidden="true" focusable="false">
  <!-- UI type and wordmark: a hair of displacement and ink spread. Values follow --fnd-texture (js/app.js). -->
  <filter id="ink-ui" x="-4%" y="-25%" width="108%" height="150%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="0.7" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="0.22" result="b"/>
    <feComponentTransfer in="b"><feFuncA type="linear" slope="1.34" intercept="0"/></feComponentTransfer>
  </filter>
  <!-- the bio: the wordmark's ink at 16px. A finer, deeper displacement, a hair of
       bleed, and the word's grain as alpha dropouts. Values follow --fnd-texture (js/app.js). -->
  <filter id="ink-bio" x="-2%" y="-30%" width="104%" height="160%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="1.8" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="0.3" result="b"/>
    <feComponentTransfer in="b" result="i"><feFuncA type="linear" slope="1.8" intercept="0"/></feComponentTransfer>
    <feTurbulence type="fractalNoise" baseFrequency="2.4" numOctaves="1" seed="11" result="g"/>
    <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.4 0 0 0 1.6" result="gm"/>
    <feComposite in="i" in2="gm" operator="in"/>
  </filter>
  <!-- the basmala: #ink-bio, and without the GL footer the wordmark's hover eases in here (js/app.js basInk) -->
  <!-- the diagrams (::harness-diagram, ::harness-flow): the bio's ink, a touch gentler for 1px rules and
       14px labels. Fine displacement, a hair of bleed, and a grain of alpha dropouts (Ahmed, Nov 10). -->
  <filter id="ink-diagram" x="-1%" y="-2%" width="102%" height="104%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="1.2" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="0.25" result="b"/>
    <feComponentTransfer in="b" result="i"><feFuncA type="linear" slope="1.6" intercept="0"/></feComponentTransfer>
    <feTurbulence type="fractalNoise" baseFrequency="2.4" numOctaves="1" seed="11" result="g"/>
    <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.1 0 0 0 1.5" result="gm"/>
    <feComposite in="i" in2="gm" operator="in"/>
  </filter>
  <filter id="ink-bas" x="-2%" y="-40%" width="104%" height="180%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="1.8" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="0.3" result="b"/>
    <feComponentTransfer in="b" result="i"><feFuncA type="linear" slope="1.8" intercept="0"/></feComponentTransfer>
    <feTurbulence type="fractalNoise" baseFrequency="2.4" numOctaves="1" seed="11" result="g"/>
    <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.4 0 0 0 1.6" result="gm"/>
    <feComposite in="i" in2="gm" operator="in"/>
  </filter>
  <!-- the marks: the same; js/app.js gives each mark its own copy (ink-mark-0..3) for its hover -->
  <filter id="ink-mark" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="1.8" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="0.3" result="b"/>
    <feComponentTransfer in="b" result="i"><feFuncA type="linear" slope="1.8" intercept="0"/></feComponentTransfer>
    <feTurbulence type="fractalNoise" baseFrequency="2.4" numOctaves="1" seed="11" result="g"/>
    <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.4 0 0 0 1.6" result="gm"/>
    <feComposite in="i" in2="gm" operator="in"/>
  </filter>
  <!-- the footer dot strips: the same, at half the displacement (js/app.js INK_HOVER) -->
  <filter id="ink-dots" x="-2%" y="-40%" width="104%" height="180%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="1.4" numOctaves="2" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="1.8" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="0.3" result="b"/>
    <feComponentTransfer in="b" result="i"><feFuncA type="linear" slope="1.8" intercept="0"/></feComponentTransfer>
    <feTurbulence type="fractalNoise" baseFrequency="2.4" numOctaves="1" seed="11" result="g"/>
    <feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -1.4 0 0 0 1.6" result="gm"/>
    <feComposite in="i" in2="gm" operator="in"/>
  </filter>
  <!-- body: the faintest ink bleed only -->
  <filter id="ink-body" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
    <feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="1" seed="3" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="0.24" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation="0.1" result="b"/>
    <feComponentTransfer in="b"><feFuncA type="linear" slope="1.12" intercept="0"/></feComponentTransfer>
  </filter>
</svg>
```

## The CSS

Source: `site/css/site.css`, lines 32 to 41

```css
/* the one canvas: above everything, never in the way */
#gl { position: fixed; inset: 0; width: 100vw; height: 100vh; pointer-events: none; z-index: 10; }
/* the grain (js/grain.js): a noise tile at one device pixel per texel, over
   everything; 0.45 is the alpha baked into the tile (GRAIN_K) */
#grain {
  position: fixed; left: 0; top: 0; z-index: 11; pointer-events: none;
  background-repeat: repeat; image-rendering: pixelated; will-change: transform;
  opacity: calc((0.01 + 0.05 * var(--fnd-texture)) * var(--grain-k) / 0.45);
}
@media print { #gl, #grain { display: none; } }
```

Source: `site/css/site.css`, lines 168 to 191

```css
.basmala { margin: 0; font: 300 18px/19.2px "Kufigraph", var(--ui); letter-spacing: 0; white-space: nowrap; filter: url(#ink-bas); }
/* the SDF dot matrix: fills the row between the bio and the marks, three bio lines tall at most */
.foot-dots { flex: 1 1 0; width: 0; min-width: 12px; height: 19.2px; align-self: flex-end; display: block; filter: url(#ink-dots); }
.marks { list-style: none; display: flex; align-items: flex-end; gap: 8px; margin: 0; padding: 0 8px; }
/* the way home: the bio itself; and the quiet links (Book a call, MCP, Settings) beside the marks,
   in the bio's type and colour. At rest plain text; hover and focus underline them in --foot */
.bio-home, .foot-link { color: inherit; text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px;
  text-decoration-color: transparent; transition: text-decoration-color 160ms var(--ease-land); outline: none; }
.bio-home:hover, .bio-home:focus-visible, .foot-link:hover, .foot-link:focus-visible, .foot-link[aria-current] { text-decoration-color: var(--foot); }
.foot-end { display: flex; align-items: flex-end; column-gap: 0; row-gap: 10px; margin-left: auto; }
.foot-links { display: flex; gap: 16px; line-height: 19.2px; white-space: nowrap; filter: url(#ink-ui); }
.gl.gl-foot .foot-link { color: transparent; }
.mark { display: block; height: 20px; width: var(--w); background: currentColor;
  -webkit-mask: var(--src) center / contain no-repeat; mask: var(--src) center / contain no-repeat;
  filter: var(--ink, url(#ink-mark)) blur(calc(var(--soft, 0px) + .55px)); }
.mark.is-peek { filter: var(--ink, url(#ink-mark)) blur(var(--soft, 0px)); }
/* while the wordmark's pass draws the footer, its DOM steps aside (still selectable and read aloud) */
.gl.gl-foot .foot-dots { visibility: hidden; } /* drawn in the GL footer pass, so they scroll with it */
.gl.gl-foot .bio, .gl.gl-foot .basmala { color: transparent; } /* the GL footer draws them, with the wordmark's ink */
.gl.gl-foot .mark { background-color: transparent; }
.wordmark { display: block; width: 100%; height: 97px; overflow: hidden; user-select: none; -webkit-user-select: none; -webkit-touch-callout: none; touch-action: manipulation; outline: none; }
.wordmark:focus-visible { box-shadow: inset 0 -1px 0 var(--ring); }
.wordmark text { font-family: "Kult Luxury"; letter-spacing: 0; fill: var(--foot); filter: url(#ink-ui); }
.gl .wordmark text { fill: transparent; filter: none; }
```

`.rz` hides an element's DOM text while its morph draws it (`.rz, .rz * { color: transparent !important; text-decoration-color: transparent !important; }`); a lost context strips it.

## Fonts the fields are built from

| Field | Font (canvas font string) | Licence |
|---|---|---|
| Wordmark `salehdigital` | `normal 400 {fs}px "Kult Luxury"` | commercial: the file is not in this harness ([kult-luxury](../../intelligence/packages/kult-luxury.md)) |
| Hold field `أحمد صالح` | `normal 400 {100·ka}px "SF Arabic", "Geeza Pro", sans-serif`, `direction: rtl` | system fonts |
| Bio, links | the element's computed font (`fontOf(getComputedStyle(el))`): Inter Display 16px | SIL OFL |
| Basmala | `300 18px/19.2px "Kufigraph", var(--ui)` | owner-supplied |
| Marks | the PNG masks in `assets/footer/` (not in this harness) | owner's |

`boot()` waits for `document.fonts.load` of `'400 16px "Inter Display"'`, `'400 16px Shinka'`, `'400 100px "Kult Luxury"'` and `'300 18px Kufigraph'` (sample text "Ahmed", "salehdigital", "بسم الله"), then `document.fonts.ready`, before any field is built: a field rasterised with a fallback font would not match the DOM.

## Boot order

Source: `site/js/app.js`, lines 1056 to 1090

```js
async function boot() {
  readParams(); applyTexture();
  E.setArticle(article);
  E.init(onReveal);
  initMedia();
  go(true);
  const fonts = ['400 16px "Inter Display"', '400 16px Shinka', '400 100px "Kult Luxury"', '300 18px Kufigraph'];
  try { await Promise.all(fonts.map(f => document.fonts.load(f, f.includes('Inter Display') ? 'Ahmed' : f.includes('Kufigraph') ? 'بسم الله' : 'salehdigital'))); } catch (e) {}
  await document.fonts.ready;
  fitColumns();
  startGrain();
  gl = createGL($('#gl'), {
    // a lost context: the DOM draws everything (the SVG wordmark included) until it is back
    lost() { document.documentElement.classList.remove('gl'); setGL(null); },
    restored() { document.documentElement.classList.add('gl'); setGL(gl); fitKey = ''; fitWordmark(); bakeFooter(); updateLife(); syncOrbs(); }
  });
  if (gl) { setGL(gl); document.documentElement.classList.add('gl'); }
  fitWordmark();
  bakeFooter();
  updateLife();
  syncOrbs();
  prewarmIcons();
  let rt = 0, lastW = document.documentElement.clientWidth;
  new ResizeObserver(() => {
    const w = document.documentElement.clientWidth;
    if (w === lastW) return;
    lastW = w; clearTimeout(rt); rt = setTimeout(() => { fitWordmark(); bakeFooter(); }, 120);
  }).observe(document.documentElement);
  document.documentElement.classList.add('ready');
  mountFavicon(); // the tab's icon follows the theme
  // locally the panel is always there (as you left it: full or pill); Shift+D hides and shows it
  // ?embed (the CMS preview) leaves the panel shut
  if (DEV && !new URLSearchParams(location.search).has('embed')) openDebug(window.SD_DEBUG || {});
}
boot();
```

Resizes: a `ResizeObserver` on `<html>` refits only when `clientWidth` changes, debounced 120ms, then re-bakes the footer. The renderer itself listens to `resize` for the canvas size.

## Fitting the wordmark, and its fields

`fitWordmark()` sets the SVG (`viewBox`, `width`, `height`, and the `<text>`'s `x`, `y`, `font-size`) so the word's ink runs edge to edge with 6px margins, then, only when the width changed (`fitKey`), hands GL three things:

1. the whole word as one run (`setWordmark`), box = the ink box;
2. `extra`: the glyphs alternately in an **even** and an **odd** snapshot (so adjacent letters can melt into each other with `smin` at stage 4), each glyph's centre (also used for the letter notes), and the cap height `asc`;
3. the Arabic hold field (`setWordmarkAlt`), centred, scaled `ka = min(asc·1.2 / inkH, vw·0.9 / inkW)`.

At 1440 (clientWidth 1425 with a 15px scrollbar) the SVG is 1425 × 239 and the font-size 310.411. Without Kult Luxury the canvas measures the fallback face instead (see the overflow note in [WebGL](webgl.md)).

Source: `site/js/app.js`, lines 822 to 879

```js
// ---------- wordmark: fit edge to edge ----------
const mctx = document.createElement('canvas').getContext('2d');
let fitKey = '';
function fitWordmark() {
  const vw = document.documentElement.clientWidth;
  // frame: 6px side margins, cap top 6px under the bio's line box (the text
  // ink sits about 2px clear), baseline 7px above the page edge, so the
  // descending spur of each "a" bleeds off the bottom
  const margin = 6, above = vw < 900 ? 8 : 6;
  mctx.font = '400 100px "Kult Luxury"';
  const m = mctx.measureText(WORD);
  const inkW = m.actualBoundingBoxLeft + m.actualBoundingBoxRight;
  const k = (vw - margin * 2) / inkW;
  const fs = 100 * k;
  const asc = m.actualBoundingBoxAscent * k, desc = m.actualBoundingBoxDescent * k;
  const below = Math.max(3, asc * 0.088);
  const h = Math.round(above + asc + below);
  const x = margin + m.actualBoundingBoxLeft * k, y = above + asc;
  wordSvg.setAttribute('viewBox', `0 0 ${vw} ${h}`);
  wordSvg.setAttribute('width', vw); wordSvg.setAttribute('height', h);
  wordSvg.style.height = h + 'px';
  Object.entries({ x: x.toFixed(2), y: y.toFixed(2), 'font-size': fs.toFixed(3) }).forEach(([a, v]) => wordText.setAttribute(a, v));
  if (gl && fitKey !== `${vw}`) {
    fitKey = `${vw}`;
    const r = wordSvg.getBoundingClientRect();
    const sx = window.scrollX, sy = window.scrollY;
    const font = `normal 400 ${fs}px "Kult Luxury"`;
    const run = { t: WORD, x: r.left + sx + x, y: r.top + sy + y, font, ls: 0, a: 1 };
    const snap = { runs: [run], rect: { x: r.left + sx + margin, y: r.top + sy + above, w: vw - margin * 2, h: asc + desc }, blur: 0, opacity: 1, sig: 'wordmark' };
    // the glyphs one by one, alternating into two fields, so adjacent letters
    // can melt into each other (smooth-min) as the wordmark comes alive
    const even = [], odd = [], glyphs = [];
    mctx.font = font;
    for (let i = 0; i < WORD.length; i++) {
      const gx = run.x + mctx.measureText(WORD.slice(0, i)).width;
      const gw = mctx.measureText(WORD[i]).width;
      (i % 2 ? odd : even).push({ ...run, t: WORD[i], x: gx });
      glyphs.push({ ch: WORD[i], cx: gx + gw / 2, cy: run.y - asc / 2 });
    }
    wordGlyphs = glyphs.map(g => ({ ...g }));
    gl.setWordmark(snap, wordSvg, {
      even: { ...snap, runs: even, sig: 'wm-even' }, odd: { ...snap, runs: odd, sig: 'wm-odd' }, glyphs, cap: asc
    });
    // the hold secret's second field: أحمد صالح, centred, about the wordmark's height
    mctx.font = '400 100px "SF Arabic", "Geeza Pro", sans-serif'; mctx.direction = 'rtl'; mctx.textAlign = 'left';
    const ma = mctx.measureText(WORD_AR);
    mctx.direction = 'ltr';
    const inkH = ma.actualBoundingBoxAscent + ma.actualBoundingBoxDescent;
    const inkW = ma.actualBoundingBoxLeft + ma.actualBoundingBoxRight;
    const ka = Math.min((asc * 1.2) / inkH, (vw * 0.9) / inkW);
    const top = above + ((asc + below) - inkH * ka) / 2;
    const ax = (vw - inkW * ka) / 2 + ma.actualBoundingBoxLeft * ka;
    const ay = top + ma.actualBoundingBoxAscent * ka;
    const runA = { t: WORD_AR, x: r.left + sx + ax, y: r.top + sy + ay, font: `normal 400 ${100 * ka}px "SF Arabic", "Geeza Pro", sans-serif`, ls: 0, a: 1, dir: 'rtl' };
    gl.setWordmarkAlt({ runs: [runA], rect: snap.rect, blur: 0, opacity: 1, sig: 'wordmark-ar' });
    updateLife();
  }
}
```

## The footer pass

`bakeFooter()` snapshots the bio, the basmala, the foot links and the marks into one field, and passes the marks' boxes (with their `soft` px), the basmala's box and the dot strips' boxes. When `setFooter` succeeds, `html` gets `.gl-foot` and the DOM steps aside (still selectable and read aloud). Without GL, with `?lite`, or over budget, `.gl-foot` is removed and the DOM draws.

Source: `site/js/app.js`, lines 881 to 904

```js
// ---------- the footer above the word, drawn in the wordmark's pass ----------
// The bio stays real DOM text (selectable, read aloud) but steps aside, colour
// transparent, while the field draws it; without WebGL, after a lost context
// or with ?lite the DOM shows as before.
async function bakeFooter() {
  const root = document.documentElement;
  if (!gl || LITE || !gl.setFooter) { root.classList.remove('gl-foot'); return; }
  const marks = [...document.querySelectorAll('#marks .mark')];
  await Promise.all(marks.map(m => preloadMask(m.dataset.maskSrc).decode?.().catch(() => {})));
  const bio = snapshot($('.bio'), 'bio');
  const links = [...document.querySelectorAll('#foot-links .foot-link')].map(a => snapshot(a, a.dataset.morph));
  const basmala = $('.basmala') ? snapshot($('.basmala'), 'basmala') : null; // drawn like the bio: the wordmark's ink and grain
  const parts = [bio, basmala, ...links, ...marks.map(m => snapshot(m, m.dataset.morph))].filter(p => p && !p.empty);
  const runs = parts.flatMap(p => p.runs);
  if (!runs.length) return;
  const x0 = Math.min(...parts.map(p => p.rect.x)), y0 = Math.min(...parts.map(p => p.rect.y));
  const x1 = Math.max(...parts.map(p => p.rect.x + p.rect.w)), y1 = Math.max(...parts.map(p => p.rect.y + p.rect.h));
  const snap = { runs, rect: { x: x0, y: y0, w: x1 - x0, h: y1 - y0 }, blur: 0, opacity: 1, sig: 'footer' };
  const geo = marks.map((m, i) => { const r = m.getBoundingClientRect(); return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height, soft: MARKS[i]?.soft || 0 }; });
  const br = basmala && $('.basmala').getBoundingClientRect(); // the basmala takes the word's hover
  const bas = br && { x: br.left + scrollX, y: br.top + scrollY, w: br.width, h: br.height };
  const dots = [...document.querySelectorAll('.foot-dots')].map(c => { const r = c.getBoundingClientRect(); return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height }; });
  root.classList.toggle('gl-foot', !!gl.setFooter(snap, wordSvg, geo, bas, dots));
}
```

### The DOM fallback ink (no WebGL, `?lite`, or a lost context)

The same look in SVG filters: `--fnd-texture` drives `#ink-ui`, `#ink-body` and the footer filters, and the footer's hover eases in (`1 − 0.02^(dt/1000)`) like the GL cursor. Off with reduced motion, and skipped while `.gl-foot` is on.

Source: `site/js/app.js`, lines 906 to 954

```js
// ---------- texture: the SVG ink filters follow --fnd-texture ----------
function applyTexture() {
  const T = params.texture;
  const set = (sel, attr, v) => document.querySelectorAll(sel).forEach(n => n.setAttribute(attr, v));
  set('#ink-ui feDisplacementMap', 'scale', (0.3 + 1.0 * T).toFixed(3));
  set('#ink-ui feGaussianBlur', 'stdDeviation', (0.08 + 0.35 * T).toFixed(3));
  set('#ink-ui feFuncA', 'slope', (1.1 + 0.6 * T).toFixed(3));
  basInk(); // the footer's filters, #ink-bio among them (GL: BIO_INK in js/glsl.js)
  set('#ink-body feDisplacementMap', 'scale', (0.1 + 0.35 * T).toFixed(3));
  set('#ink-body feGaussianBlur', 'stdDeviation', (0.04 + 0.16 * T).toFixed(3));
}
bus.on('params', applyTexture);
// the footer (bio, basmala, dot strips, marks): #ink-bio's values plus the wordmark's hover (the
// edge warps, melts and bleeds), easing in like the word's cursor. The GL footer draws its own
// (FOOT_HOVER in js/glsl.js); this is the DOM's, for ?lite and no WebGL. Off with reduced motion.
// One filter per hover target: k scales the displacement (the dots are 0.45 to 1.7px, so half).
// Each mark gets its own copy of #ink-mark, so only the one under the cursor moves.
const markInk = [...document.querySelectorAll('#marks .mark')].map((el, i) => {
  const f = $('#ink-mark').cloneNode(true); f.id = `ink-mark-${i}`; $('#ink-mark').after(f);
  el.style.setProperty('--ink', `url(#ink-mark-${i})`);
  return { id: f.id, els: [el], k: 1, kh: 1 };
});
const INK_HOVER = [{ id: 'ink-bio', sel: '.bio', k: 1, kh: 0.6 }, { id: 'ink-bas', sel: '.basmala', k: 1 }, { id: 'ink-dots', sel: '.foot-dots', k: 0.5 }, ...markInk]
  .map(o => ({ kh: 1, ...o, els: o.els || [...document.querySelectorAll(o.sel)], h: 0, to: 0, raf: 0, t: 0 })); // kh: hover strength (the bio's 16px counters take less, as in the GL)
function basInk() { INK_HOVER.forEach(inkHover); }
function inkHover(o) {
  const T = params.texture, h = o.h * o.kh, f = `#${o.id} `;
  const set = (sel, attr, v) => document.querySelectorAll(f + sel).forEach(n => n.setAttribute(attr, v));
  set('feDisplacementMap', 'scale', (o.k * (0.6 + 3 * T + 1.1 * h)).toFixed(3));
  set('feGaussianBlur', 'stdDeviation', (0.1 + 0.5 * T + 0.3 * h).toFixed(3));
  set('feFuncA', 'slope', (1.8 + 2.2 * h).toFixed(3));
  set('feTurbulence[result="n"]', 'baseFrequency', (1.4 - 0.5 * h).toFixed(3));
  set('feColorMatrix', 'values', `0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  ${-(0.4 + 2.5 * T).toFixed(3)} 0 0 0 ${(1 + 1.5 * T).toFixed(3)}`);
}
INK_HOVER.forEach(o => {
  const step = (t) => {
    const dt = Math.min(64, t - (o.t || t)); o.t = t;
    o.h += (o.to - o.h) * (1 - Math.pow(0.02, dt / 1000));
    if (Math.abs(o.to - o.h) < 0.004) o.h = o.to;
    inkHover(o);
    o.raf = o.h === o.to ? 0 : requestAnimationFrame(step);
  };
  o.els.forEach(el => ['pointerenter', 'pointerleave'].forEach(type => el.addEventListener(type, (e) => {
    const on = type === 'pointerenter';
    if (on && (e.pointerType === 'touch' || reducedMotion.matches || document.documentElement.classList.contains('gl-foot'))) return;
    o.to = on ? 1 : 0; o.t = 0;
    if (!o.raf) o.raf = requestAnimationFrame(step);
  })));
});
```

### The dot strips without GL

`js/footdots.js` draws the strips on their own 2D canvases when `.gl-foot` is off: a 4.8px grid, each dot's radius between 0.45 and 1.7px read off a smooth-union SDF of drifting blobs (about one per 140px) and one under the cursor. The GL footer uses the same blob formulas (`dotB` in the shaders record).

Source: `site/js/footdots.js`, whole file

```js
// The footer's dot matrix (Ahmed, Nov 9): strips of dots on a fixed grid in the gaps
// between the bio, the basmala and the marks. Each dot's radius is read off a signed distance field: a few soft
// blobs drifting along the strip, smooth-unioned (smin) with a small one under the
// cursor. Inside the field a dot swells to full size, outside it shrinks to a pinprick,
// so the shapes read as halftone. Colour: the footer's ink (--foot). Still under
// reduced motion. Energy (--fnd-energy) sets the drift speed.
// With the GL footer on (html.gl-foot) js/gl.js draws them instead, so they scroll in
// lockstep with the bio and the wordmark; this canvas is the ?lite / no-WebGL fallback.
import { onTheme } from './theme.js';

const byGL = () => document.documentElement.classList.contains('gl-foot');
document.querySelectorAll('.foot-dots').forEach((cv, seed) => {
  const cx = cv.getContext('2d');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const PITCH = 4.8;            // grid step, px: four rows in the 19.2px line
  const RMAX = 1.7, RMIN = 0.45; // dot radius inside and far outside the field
  let W = 0, H = 0, dpr = 1, ink = '#000', mouse = null, raf = 0, t0 = performance.now(), seen = true;

  const smin = (a, b, k) => { const h = Math.max(k - Math.abs(a - b), 0) / k; return Math.min(a, b) - h * h * k * 0.25; };
  // the field, in px: < 0 inside a blob
  function sdf(x, y, t) {
    let d = 1e9;
    const n = Math.max(2, Math.round(W / 140)); // about one blob per 140px of strip
    for (let i = 0; i < n; i++) {
      const ph = i * 2.399 + seed * 1.3;                     // golden-angle spread; each strip its own
      const bx = ((i + 0.5) / n + 0.06 * Math.sin(t * 0.21 + ph)) * W;
      const by = H * (0.5 + 0.35 * Math.sin(t * 0.33 + ph * 1.7));
      const r = 5 + 4 * (0.5 + 0.5 * Math.sin(t * 0.27 + ph * 0.9));
      const dx = (x - bx) * 0.55, dy = y - by;                // stretched along the strip
      d = smin(d, Math.hypot(dx, dy) - r, 10);
    }
    if (mouse) d = smin(d, Math.hypot(x - mouse.x, y - mouse.y) - 7, 14);
    return d;
  }
  function size() {
    const r = cv.getBoundingClientRect();
    dpr = Math.min(2, devicePixelRatio || 1);
    W = r.width; H = r.height;
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    draw();
  }
  function draw() {
    if (!W || !H || byGL()) return;
    const speed = 0.4 + 1.2 * (parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--fnd-energy')) || 0.5);
    const t = reduce.matches ? 0 : (performance.now() - t0) / 1000 * speed;
    cx.setTransform(dpr, 0, 0, dpr, 0, 0);
    cx.clearRect(0, 0, W, H);
    cx.fillStyle = ink;
    const cols = Math.floor(W / PITCH), rows = Math.floor(H / PITCH);
    const ox = (W - (cols - 1) * PITCH) / 2, oy = (H - (rows - 1) * PITCH) / 2;
    cx.beginPath();
    for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
      const x = ox + i * PITCH, y = oy + j * PITCH;
      const k = 1 - Math.min(1, Math.max(0, (sdf(x, y, t) + 2) / 8)); // 1 inside, 0 eight px out
      const r = RMIN + (RMAX - RMIN) * k * k * (3 - 2 * k);
      cx.moveTo(x + r, y); cx.arc(x, y, r, 0, Math.PI * 2);
    }
    cx.fill();
  }
  function loop() { raf = 0; if (!seen || byGL()) return; draw(); if (!reduce.matches) raf = requestAnimationFrame(loop); }
  const kick = () => { if (!raf) raf = requestAnimationFrame(loop); };

  onTheme(() => { ink = getComputedStyle(cv).color || getComputedStyle(document.documentElement).getPropertyValue('--foot'); draw(); });
  new ResizeObserver(size).observe(cv);
  new IntersectionObserver(([e]) => { seen = e.isIntersecting; if (seen) kick(); }).observe(cv);
  addEventListener('pointermove', (e) => {
    const r = cv.getBoundingClientRect();
    const x = e.clientX - r.left, y = e.clientY - r.top;
    mouse = (x > -40 && x < W + 40 && y > -40 && y < H + 40) ? { x, y } : null;
    if (reduce.matches) draw();
  }, { passive: true });
  reduce.addEventListener?.('change', () => { draw(); kick(); });
  new MutationObserver(kick).observe(document.documentElement, { attributes: true, attributeFilter: ['class'] }); // GL footer off: back to the canvas
  size(); kick();
});
```

## Interaction and sound hooks

| Gesture | What it does | GL call | Bus event → sound / haptics |
|---|---|---|---|
| Pointer anywhere (not touch) | the word warps within `mouseR` of the cursor; orbs lean | renderer's `pointermove` | none |
| Pointer along the word | each letter crossed is a note | none | `wordmark:letter {index, total, ch, speed, source}` → `audio.js` `letter()`: D minor pentatonic, step per letter (`12·floor(i/5) + [0,3,5,7,10][i mod 5]` semitones over `SOUND.root`), velocity `min(1, .35 + .9·speed)`, at most one per 38ms; `haptics.js` `[9]` at the ends, `[4]` between |
| Press and hold 2s (or Space/Enter) | the word swells, then resolves into أحمد صالح for 3.6s | `setHold(p)`, then `wordmarkTo(1, 1100)` and back `wordmarkTo(0, 1100)` | `hold`; the `hold` secret unlocks (a trace on letter 0 and the Arabic ghost) |
| Hover a mark (GL footer on) | a local focus bump on that mark | `markHover(i, on)` | `hover {source: 'mark'}` → the hover tick |
| Slow hover (600ms) on the word | feeds resonance | none | via `E.slowHover` |
| Life changes (resonance, secrets, `--fnd-life`) | stages fade in | `setLife`, `setTraces` | none |

Source: `site/js/app.js`, lines 509 to 521

```js
// ---------- the wordmark's life: the visible resonance meter ----------
function lifeValue() {
  const forced = params.life;
  if (forced > 0) return forced;
  return E.life();
}
function updateLife() {
  gl?.setLife(lifeValue());
  gl?.setTraces(E.state().secrets);
}
bus.on('resonance', updateLife);
bus.on('secret', updateLife);
bus.on('params', updateLife);
```

Source: `site/js/app.js`, lines 562 to 604

```js
// (b) press and hold the wordmark for 2s: it resolves into أحمد صالح
let holdStart = 0, holdRaf = 0, holdBusy = false;
function holdTick() {
  const p = (performance.now() - holdStart) / 2000;
  gl?.setHold(Math.min(1, p));
  if (p >= 1) { holdEnd(); holdComplete(); return; }
  holdRaf = requestAnimationFrame(holdTick);
}
function holdBegin() { if (holdBusy) return; holdStart = performance.now(); cancelAnimationFrame(holdRaf); holdRaf = requestAnimationFrame(holdTick); }
function holdEnd() { cancelAnimationFrame(holdRaf); holdRaf = 0; gl?.setHold(0); }
function holdComplete() {
  holdBusy = true;
  bus.emit('hold', {});
  gl?.wordmarkTo(1, 1100);
  wordSvg.setAttribute('aria-label', WORD_AR);
  E.unlock('hold');
  setTimeout(() => { gl?.wordmarkTo(0, 1100); wordSvg.setAttribute('aria-label', WORD); }, 3600);
  setTimeout(() => { holdBusy = false; }, 4800);
}
wordSvg.addEventListener('pointerdown', (e) => { e.preventDefault(); holdBegin(); });
['pointerup', 'pointerleave', 'pointercancel'].forEach(t => wordSvg.addEventListener(t, () => { if (holdRaf) holdEnd(); }));
wordSvg.addEventListener('contextmenu', (e) => e.preventDefault());
// hovering the wordmark plays it: each letter crossed is a note, with a tick of haptics
let wordGlyphs = [], lastLetter = -1, lastMoveX = 0, lastMoveT = 0;
function letterAt(clientX) {
  if (!wordGlyphs.length) return -1;
  const x = clientX + window.scrollX;
  let best = 0, bd = Infinity;
  wordGlyphs.forEach((g, i) => { const d = Math.abs(g.cx - x); if (d < bd) { bd = d; best = i; } });
  return best;
}
wordSvg.addEventListener('pointermove', (e) => {
  const i = letterAt(e.clientX);
  const t = performance.now(), dt = Math.max(1, t - lastMoveT);
  const speed = Math.min(1, Math.abs(e.clientX - lastMoveX) / dt / 2); // px per ms, normalised
  lastMoveX = e.clientX; lastMoveT = t;
  if (i < 0 || i === lastLetter) return;
  lastLetter = i;
  bus.emit('wordmark:letter', { index: i, total: wordGlyphs.length, ch: wordGlyphs[i].ch, speed, source: e.pointerType });
});
wordSvg.addEventListener('pointerleave', () => { lastLetter = -1; });
wordSvg.addEventListener('keydown', (e) => { if ((e.key === ' ' || e.key === 'Enter') && !e.repeat) { e.preventDefault(); holdBegin(); } });
wordSvg.addEventListener('keyup', (e) => { if (e.key === ' ' || e.key === 'Enter') { if (holdRaf) holdEnd(); } });
```

Source: `site/js/app.js`, lines 798 to 819

```js
// ---------- footer marks: decorative for now; their labels live in content.js ----------
function buildMarks() {
  $('#marks').replaceChildren(...MARKS.map((m, i) => {
    preloadMask(m.src);
    const el = document.createElement('span');
    el.className = 'mark'; el.setAttribute('role', 'img');
    el.setAttribute('aria-label', m.label); el.dataset.label = m.label;
    el.dataset.morph = `mark-${m.id}`; el.dataset.maskSrc = m.src;
    el.style.setProperty('--w', `${m.w}px`); el.style.setProperty('--src', `url("${new URL(m.src, document.baseURI).href}")`); // absolute: a url() in a custom property resolves against the stylesheet
    if (m.soft) el.style.setProperty('--soft', `${m.soft}px`);
    // hover resolves it, blur to sharp with a little noise, like an inactive nav item
    const peek = (on) => { if (el.classList.contains('is-peek') === on) return;
      // drawn by the wordmark's pass: a local focus bump on this mark; otherwise the DOM morph
      if (gl?.hasFooter?.() && document.documentElement.classList.contains('gl-foot')) { el.classList.toggle('is-peek', on); gl.markHover(i, on); }
      else transition(() => el.classList.toggle('is-peek', on), { keys: [el.dataset.morph], kind: 'hover' });
      if (on) bus.emit('hover', { el, source: 'mark' }); };
    el.addEventListener('pointerenter', (e) => { if (e.pointerType !== 'touch') peek(true); });
    el.addEventListener('pointerleave', () => peek(false));
    return li(el);
  }));
}
buildMarks();
```

Source: `site/js/audio.js`, lines 339 to 371

```js
// wordmark hover: running the cursor along salehdigital plays it like an instrument.
// Each letter is a step up D minor pentatonic (12 letters, two and a half octaves);
// a clean v1-style voice: a breath of noise closing onto a soft sine. Speed sets the touch.
const PENTA = [0, 3, 5, 7, 10];
let lastLetterAt = 0;
function letter({ index = 0, total = 12, speed = 0 }) {
  if (!live()) return;
  const t = performance.now();
  if (t - lastLetterAt < 38) return; lastLetterAt = t;
  const semi = 12 * Math.floor(index / 5) + PENTA[index % 5];
  const f = SOUND.root * Math.pow(2, semi / 12);
  const at = ctx.currentTime + 0.005;
  const vel = Math.min(1, 0.35 + speed * 0.9);           // a slow drag is soft, a flick brighter
  const lvl = 0.011 * vel;
  // the breath: noise through a band that closes onto the note
  const src = ctx.createBufferSource(); src.buffer = noiseBuf;
  const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.Q.value = 9;
  bp.frequency.setValueAtTime(f * 6, at); bp.frequency.exponentialRampToValueAtTime(f, at + 0.09);
  const ng = ctx.createGain(); ng.gain.setValueAtTime(0, at); ng.gain.linearRampToValueAtTime(lvl * 0.7, at + 0.012); ng.gain.setTargetAtTime(0, at + 0.03, 0.05);
  releaseOnEnd(src, bp, ng);
  src.connect(bp).connect(ng); ng.connect(master); ng.connect(wet);
  src.start(at, Math.random()); src.stop(at + 0.35);
  // the note: a soft sine and a whisper of its octave, ringing into the reverb
  [[1, 1], [2, 0.18]].forEach(([mul, g]) => {
    const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.value = f * mul;
    const og = ctx.createGain(); og.gain.setValueAtTime(0, at + 0.06); og.gain.linearRampToValueAtTime(lvl * g, at + 0.09); og.gain.setTargetAtTime(0, at + 0.1, 0.45 + 0.4 * (1 - vel));
    const dry = ctx.createGain(); dry.gain.value = 0.4; og.connect(dry).connect(master); og.connect(wet); releaseOnEnd(o, og, dry);
    o.start(at + 0.06); o.stop(at + 2.6);
  });
  heard('letter', { note: NOTE_NAMES[(semi + 2) % 12] + (3 + Math.floor((semi + 2) / 12)) });
}
bus.on('wordmark:letter', letter);
```

## Reduced motion

| Thing | Normal | `prefers-reduced-motion: reduce` |
|---|---|---|
| Loop clock `time` | runs | frozen |
| Breathing | `0.3 + 1.2·energy` px | 0 |
| Cursor warp (`mouseOn`) | eased presence | 0 |
| Thinking swell | rises and decays | 0 |
| Ripples, bar, beat | on the bar clock | 0 |
| Flow along the strokes | 6 px/s | stopped |
| Arabic hold mix | 1100ms | 120ms |
| Ambient idle redraws | 15 / 30 fps | none (only when something changes) |
| Orbs | bloom, lean, flare, pulse, bob | appear at size; no lean, flare, pulse or bob; melt 160ms |
| Footer dot blobs | drift | still |
| DOM footer hover ink | eases in | off |

## Raster and snapshot (js/raster.js)

`snapshot(el, key)` records an element's text word by word from DOM ranges (exact font, size, tracking and position) or, for an element with `data-mask-src`, its picture. `rasterize(snap, box, scale, mode, …)` draws a snapshot into the shared scratch canvas: `'mask'` (alpha for the SDF) or `'display'` (as the DOM paints it, with blur and opacity). `linesOf` gives the body's line bounds for `LINES_FRAG`; `ascentOf` and `capHeightOf` measure `'Hxg'` and `'H'`.

Source: `site/js/raster.js`, whole file

```js
// Snapshots of real DOM text (exact font, size, tracking and position, word by
// word from DOM ranges) and their rasterisation to offscreen 2D canvases.

const mctx = document.createElement('canvas').getContext('2d');
const ascents = new Map();
const HAS_LS = 'letterSpacing' in mctx;

export function fontOf(cs) {
  return `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
}

const caps = new Map();
export function capHeightOf(font) {
  let c = caps.get(font);
  if (c == null) { mctx.font = font; c = mctx.measureText('H').actualBoundingBoxAscent; caps.set(font, c); }
  return c;
}

export function ascentOf(font) {
  let a = ascents.get(font);
  if (a == null) {
    mctx.font = font;
    const m = mctx.measureText('Hxg');
    a = m.fontBoundingBoxAscent ?? m.actualBoundingBoxAscent;
    ascents.set(font, a);
  }
  return a;
}

function parseBlur(filter) {
  const m = /blur\(([\d.]+)px\)/.exec(filter || '');
  return m ? parseFloat(m[1]) : 0;
}

const range = document.createRange();

// Image runs: an element with data-mask-src (the footer marks) is snapshotted
// as its picture, so it can resolve through the field like text does.
const images = new Map();
export function preloadMask(src) {
  if (images.has(src)) return images.get(src);
  const img = new Image(); img.decoding = 'async'; img.src = src;
  images.set(src, img);
  return img;
}

// clip: {top, bottom} in document px; words outside are skipped (long bodies)
export function snapshot(el, key, clip = null) {
  const cs = getComputedStyle(el);
  const sx = window.scrollX, sy = window.scrollY;
  if (el.dataset.maskSrc) {
    const br = el.getBoundingClientRect();
    const img = preloadMask(el.dataset.maskSrc);
    const rect = { x: br.left + sx, y: br.top + sy, w: br.width, h: br.height };
    const ok = img.complete && img.naturalWidth > 0;
    return {
      key, el, rect, runs: ok ? [{ img: el.dataset.maskSrc, x: rect.x, y: rect.y, w: rect.w, h: rect.h, a: 1, top: rect.y, bottom: rect.y + rect.h }] : [],
      sig: `img|${el.dataset.maskSrc}|${rect.w.toFixed(2)}|${rect.h.toFixed(2)}`,
      blur: parseBlur(cs.filter), opacity: parseFloat(cs.opacity), empty: !ok
    };
  }
  const runs = [];
  const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
  let n;
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  while ((n = walker.nextNode())) {
    const parent = n.parentElement;
    if (!parent || parent.closest('.sr-only')) continue;
    const pcs = parent === el ? cs : getComputedStyle(parent);
    if (pcs.display === 'none' || pcs.visibility === 'hidden') continue;
    const font = fontOf(pcs);
    const ls = parseFloat(pcs.letterSpacing) || 0;
    const wt = parseFloat(pcs.webkitTextStrokeWidth || pcs.getPropertyValue('-webkit-text-stroke-width')) || 0;
    const asc = ascentOf(font);
    let alpha = 1;
    for (let p = parent; p && p !== el; p = p.parentElement) alpha *= parseFloat(getComputedStyle(p).opacity);
    const re = /\S+/g; let m;
    while ((m = re.exec(n.data))) {
      range.setStart(n, m.index); range.setEnd(n, m.index + m[0].length);
      const rects = range.getClientRects();
      if (!rects.length) continue;
      // a word broken across lines (at a hyphen, say) becomes one piece per line
      const pieces = [];
      if (rects.length === 1) pieces.push({ t: m[0], r: rects[0] });
      else {
        let cur = null;
        for (let k = 0; k < m[0].length; k++) {
          range.setStart(n, m.index + k); range.setEnd(n, m.index + k + 1);
          const cr = range.getBoundingClientRect();
          if (!cr.width && !cr.height) continue;
          if (cur && Math.abs(cr.top - cur.r.top) < 2) { cur.t += m[0][k]; cur.right = cr.right; }
          else { cur = { t: m[0][k], r: cr, right: cr.right }; pieces.push(cur); }
        }
        pieces.forEach(pc => { pc.r = { left: pc.r.left, top: pc.r.top, bottom: pc.r.bottom, right: pc.right }; });
      }
      for (const { t: word, r } of pieces) {
        const top = r.top + sy, bottom = r.bottom + sy;
        if (clip && (bottom < clip.top || top > clip.bottom)) continue;
        runs.push({ t: word, x: r.left + sx, y: top + asc, top, bottom, font, ls, a: alpha, wt });
        minX = Math.min(minX, r.left + sx); maxX = Math.max(maxX, r.right + sx);
        minY = Math.min(minY, top); maxY = Math.max(maxY, bottom);
      }
    }
  }
  const br = el.getBoundingClientRect();
  const rect = runs.length
    ? { x: minX, y: minY, w: maxX - minX, h: maxY - minY }
    : { x: br.left + sx, y: br.top + sy, w: br.width, h: br.height };
  const sig = runs.map(r => `${r.t}|${(r.x - rect.x).toFixed(2)}|${(r.y - rect.y).toFixed(2)}|${r.font}|${r.ls}|${r.a}|${r.wt}`).join('~');
  return {
    key, el, runs, rect, sig,
    blur: parseBlur(cs.filter),
    opacity: parseFloat(cs.opacity),
    empty: runs.length === 0
  };
}

// Lines for staggered body resolves: tops grouped within 3px.
export function linesOf(snap) {
  const lines = [];
  for (const r of snap.runs) {
    let l = lines.find(L => Math.abs(L.top - r.top) < 3);
    if (!l) { l = { top: r.top, bottom: r.bottom }; lines.push(l); }
    l.bottom = Math.max(l.bottom, r.bottom);
  }
  lines.sort((a, b) => a.top - b.top);
  // boundaries between consecutive lines, document px
  const bounds = [];
  for (let i = 0; i < lines.length - 1; i++) bounds.push((lines[i].bottom + lines[i + 1].top) / 2);
  return { count: lines.length, bounds };
}

// box: {x, y, w, h} document px. mode 'mask' (sharp, opaque: SDF source) or
// 'display' (as the DOM shows it: opacity and blur).
// into: a scratch canvas to reuse (js/gl.js uploads it at once), so a morph
// never leaves big 2D canvases waiting on garbage collection.
export function rasterize(snap, box, scale, mode, blurOverride = null, opacityOverride = null, into = null) {
  const c = into || document.createElement('canvas');
  c.width = Math.max(1, Math.ceil(box.w * scale));
  c.height = Math.max(1, Math.ceil(box.h * scale));
  const ctx = c.getContext('2d');
  ctx.setTransform(scale, 0, 0, scale, -box.x * scale, -box.y * scale);
  ctx.fillStyle = '#000';
  ctx.textBaseline = 'alphabetic';
  const display = mode === 'display';
  const blur = display ? (blurOverride ?? snap.blur) : 0;
  const op = display ? (opacityOverride ?? snap.opacity) : 1;
  if (blur > 0.05) ctx.filter = `blur(${(blur * scale).toFixed(2)}px)`;
  for (const r of snap.runs) {
    if (r.img) { ctx.globalAlpha = display ? r.a * op : 1; ctx.drawImage(images.get(r.img), r.x, r.y, r.w, r.h); continue; }
    ctx.font = r.font;
    ctx.globalAlpha = display ? r.a * op : 1;
    ctx.direction = r.dir || 'ltr'; ctx.textAlign = 'left';
    if (HAS_LS) {
      ctx.letterSpacing = `${r.ls}px`;
      ctx.fillText(r.t, r.x, r.y);
      if (r.wt) { ctx.lineWidth = r.wt; ctx.strokeStyle = '#000'; ctx.lineJoin = 'round'; ctx.strokeText(r.t, r.x, r.y); }
    } else {
      let x = r.x;
      for (const ch of r.t) { ctx.fillText(ch, x, r.y); x += ctx.measureText(ch).width + r.ls; }
    }
  }
  return c;
}
```
