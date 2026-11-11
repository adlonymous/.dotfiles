---
title: Harness flow
slug: harness-flow
status: published
description: "::harness-flow: Before / After flowchart of how a harness works, with dots flowing along the feedback loops in a three.js SDF shader."
chips:
  - Embed
  - Diagram
  - Animation
created: 2026-11-11T18:00:00Z
updated: 2026-11-11T16:05:35Z
---

Embeds are placed in a post by a paragraph that is only `::name` (`EMBED = /^::([a-z-]+)\s*$/`). `js/embeds.js` replaces it with `<div class="embed embed-NAME" data-embed="NAME" data-stream-skip>`, lazy-imports `js/embeds/NAME.js` and calls `mount(el, ctx)`. Embeds are skipped by the word stream and by the body ink filter (`.col-body article > :not(.embed) { filter: url(#ink-body) }`), so screenshots and diagrams stay sharp.

**What it is.** How a design harness works, as a classic black-and-white flowchart in the same language as the [harness diagram](harness-diagram.md): square boxes, 1px black rules, square-cornered lines, black icons. A **Before / After** toggle (two square segments, black when chosen) switches between two flows:

- **Before:** Prompt → Agent → Design → Design complete. People fine-tune the output, over and over, and nothing is kept.
- **After:** Prompt → Harness → Agent → Design → Design complete. The designer's moves send a design back to the agent, and people fine-tune the harness instead (decisions kept as records).

Hovering or focusing a step makes its box and lines heavier and shows its line in the caption.

## The animation: flowing dots

The feedback loops are dotted lines drawn as an SDF in a three.js shader. A transparent plane sits over the diagram. Each loop is up to 3 segments. A pixel finds its nearest segment and its arc length there, and is ink inside a dot of radius r spaced every SP px, which scrolls with time, so the dots flow along the loop. The dots stop short of the arrowhead, which the SVG keeps. Until the shader is up, or under reduced motion, the SVG draws the dots itself (static): `.has-gl .hf-dots { visibility: visible }` and `.hf-gl { display: none }` under reduced motion.

Icons come from `js/embeds/harness-icons.js` (`svgIcon(name)`). Those are icon-set paths and are **not** reproduced here; leave a 14 to 16px `currentColor` slot of the same size.

Source: `site/css/embeds/harness-flow.css`, whole file

```css
/* ::harness-flow (js/embeds/harness-flow.js): how a design harness works, as a classic black-and-white
   flowchart, the same language as ::harness-diagram. No ground of its own: it sits on the page's paper. */
.embed-harness-flow { margin: calc(var(--para) * 0.5) 0; }
.hf-fig { margin: 0; display: flex; flex-direction: column; gap: 12px; }
.hf-canvas { position: relative; padding: 48px 0 48px; color: var(--ink); font: 400 14px/18px var(--ui); letter-spacing: -0.3px; }
.hf-wires { position: absolute; inset: 0; pointer-events: none; overflow: visible; }
.hf-labels { position: absolute; inset: 0; pointer-events: none; z-index: 2; }
/* compact (Ahmed, Nov 10): cards hug their label, 34px tall, 13px type; the arrows carry the spacing */
.hf-row { position: relative; z-index: 1; display: flex; align-items: center; gap: 36px; }

.hf-card { display: flex; align-items: center; justify-content: center; gap: 6px; flex: none; min-width: 0; height: 34px; padding: 0 10px; border-radius: 8px; font-size: 13px; color: var(--ink); box-shadow: 0 0 0 1px var(--ink);
  outline: none; cursor: default; -webkit-tap-highlight-color: transparent; transition: box-shadow 160ms var(--ease-land); }
.hf-card.is-lit { box-shadow: 0 0 0 2px var(--ink); }
.hf-card:focus-visible { box-shadow: 0 0 0 2px var(--ink), 0 0 0 5px var(--paper), 0 0 0 6px var(--ink); }
.hf-harness { box-shadow: 0 0 0 1.5px var(--ink); font-weight: 500; }
.hf-ico { flex: none; display: grid; place-items: center; width: 14px; height: 14px; }
.hf-ico svg { width: 14px; height: 14px; }
.hf-ico svg { display: block; }
.hf-title { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.hf-wire { fill: none; stroke: var(--ink); stroke-width: 1; stroke-linecap: round; stroke-linejoin: round; }
.hf-wire.is-lit { stroke-width: 2; }
.hf-label { position: absolute; font-size: 11px; line-height: 13px; letter-spacing: -0.05px; color: var(--ink); white-space: nowrap; background: var(--paper); padding: 0 6px; }
.hf-label.is-above { transform: translate(-50%, calc(-100% - 4px)); }
.hf-label.is-below { transform: translate(-50%, 4px); }

.hf-def { display: flex; flex-direction: column; min-height: 40px; padding-top: 10px; border-top: 1px solid color-mix(in srgb, var(--ink) 8%, transparent); font: 400 14px/20px var(--ui); letter-spacing: -0.2px; color: var(--muted); }
.hf-def-name { color: var(--ink); }

@media (max-width: 599px) {
  .hf-canvas { padding: 8px 48px 8px 0; }
  .hf-row { flex-direction: column; align-items: stretch; gap: 24px; }
  .hf-label { display: none; }
  .hf-def { min-height: 80px; }
}
@media (prefers-reduced-motion: reduce) { .hf-card { transition: none; } }

/* the Before / After toggle: two square segments on a 1px black rule, the chosen one filled black */
.hf-toggle { display: inline-flex; align-self: flex-start; border-radius: 8px; overflow: hidden; box-shadow: 0 0 0 1px var(--ink); background: var(--paper); }
.hf-tab { appearance: none; border: 0; margin: 0; padding: 0 14px; height: 30px; background: transparent; color: var(--ink); font: 400 13px/30px var(--ui); letter-spacing: -0.2px; cursor: pointer;
  transition: background-color 140ms var(--ease-land), color 140ms var(--ease-land); }
.hf-tab + .hf-tab { box-shadow: inset 1px 0 0 var(--ink); }
.hf-tab:hover { background: color-mix(in srgb, var(--ink) 6%, var(--paper)); }
.hf-tab[aria-pressed="true"] { background: var(--ink); color: var(--paper); }
.hf-tab:focus-visible { outline: 2px solid var(--ink); outline-offset: 3px; }
@media (prefers-reduced-motion: reduce) { .hf-tab { transition: none; } }

/* the loops: dotted, drawn live by the SDF shader (.hf-gl); the SVG keeps the arrowhead, and draws the dots
   itself (round-capped zero-length dashes) until the shader is up or under reduced motion */
.hf-gl { position: absolute; inset: 0; pointer-events: none; z-index: 1; }
.hf-dots { stroke-dasharray: 0 6; stroke-width: 2; stroke-linecap: round; }
.hf-dots.is-lit { stroke-width: 2.7; }
.has-gl .hf-dots { visibility: hidden; }
@media (prefers-reduced-motion: reduce) { .has-gl .hf-dots { visibility: visible; } .hf-gl { display: none; } }

/* larger scale (Ahmed, Nov 10): 42px cards, 15px type, 16px icons, longer arrows, 12px labels */
@media (min-width: 600px) {
  .hf-row { gap: 44px; }
  .hf-card { height: 42px; padding: 0 14px; gap: 8px; border-radius: 10px; font-size: 15px; }
  .hf-ico, .hf-ico svg { width: 16px; height: 16px; }
  .hf-label { font-size: 12px; line-height: 15px; }
  .hf-canvas { padding: 56px 0; }
  .hf-tab { height: 34px; line-height: 34px; font-size: 14px; padding: 0 16px; }
  .hf-toggle { border-radius: 10px; }
}
```


Source: `site/js/embeds/harness-flow.js`, whole file

```js
// ::harness-flow. How a design harness works, as a classic black-and-white flowchart in the same
// language as ::harness-diagram (square boxes, 1px black rules, square-cornered lines, black icons).
// A Before / After toggle (Ahmed, Nov 10):
//   Before: Prompt → Agent → Design → Design complete; people fine-tune the output, over and over; nothing is kept.
//   After:  Prompt → Harness → Agent → Design → Design complete; the designer's moves send a design back
//           to the agent, and people fine-tune the harness instead (decisions kept as records).
// Hover or focus a step: its box and lines get heavier and its line shows in the caption.
import { svgIcon } from './harness-icons.js';

const CSS = 'css/embeds/harness-flow.css';
const NARROW = matchMedia('(max-width: 599px)');
const NS = 'http://www.w3.org/2000/svg';

const STATES = {
  before: {
    tab: 'Before',
    idleName: 'Without a harness',
    idle: 'People fine-tune each output by hand. Nothing they decide is kept, so the next design starts from zero.',
    alt: 'Before: a prompt goes to the agent, the agent makes a design, and people fine-tune the output and prompt again, over and over, until it is design complete. Nothing is kept.',
    steps: [
      { key: 'prompt', icon: 'comment-fill', title: 'Prompt', def: 'The designer describes what they want, and describes it again for every design.' },
      { key: 'agent', icon: 'sparkles-fill', title: 'Agent', def: 'With nothing but the prompt to go on, it guesses at taste: generic type, colour and spacing.' },
      { key: 'design', icon: 'browser-fill', title: 'Design', def: 'Close, but not right. People fine-tune this output by hand or re-prompt, and what they learn stays in this one design.' },
      { key: 'complete', icon: 'shield-check-fill', title: 'Design complete', def: 'Reached eventually, after round after round. Nothing decided on the way is kept, so the next design starts from zero.' },
    ],
    loops: [
      { key: 'finetune', from: 'design', to: 'prompt', side: 'below', label: 'fine-tune the output, again and again', lights: ['design', 'prompt', 'agent'] },
    ],
  },
  after: {
    tab: 'After',
    idleName: 'With a harness',
    idle: 'People fine-tune the harness, not the output. Every decision is kept, so each design starts further along than the last.',
    alt: 'After: a prompt goes to the harness, the harness gives the agent its context, the agent makes a design, and the design becomes design complete. The designer’s moves send the design back to the agent, and people fine-tune the harness: decisions are kept as records.',
    steps: [
      { key: 'prompt', icon: 'comment-fill', title: 'Prompt', def: 'The designer says what they want, in their own words. No prompt engineering.' },
      { key: 'harness', icon: 'cube-fill', title: 'Harness', def: 'Before it builds, the agent reads the harness: the foundations it must use and the intelligence it must follow.' },
      { key: 'agent', icon: 'sparkles-fill', title: 'Agent', def: 'It builds from the harness’s components, then reviews its own work against the harness before showing it.' },
      { key: 'design', icon: 'browser-fill', title: 'Design', def: 'The designer answers with moves: steer a decision, pick a concept, tune a slider, comment on one part. The agent goes round again.' },
      { key: 'complete', icon: 'shield-check-fill', title: 'Design complete', def: 'Finished to the standard you would ship. What was decided on the way goes into the harness as records, so people fine-tune the harness, not the next output.' },
    ],
    loops: [
      { key: 'moves', from: 'design', to: 'agent', side: 'below', label: 'moves: steer, concept, tune, comment', lights: ['design', 'agent'] },
      { key: 'records', from: 'complete', to: 'harness', side: 'above', label: 'fine-tune the harness: decisions kept as records', lights: ['complete', 'harness'] },
    ],
  },
};

export function mount(el) {
  if (!document.querySelector(`link[href="${CSS}"]`)) document.head.append(Object.assign(document.createElement('link'), { rel: 'stylesheet', href: CSS }));
  const h = (tag, cls) => { const e = document.createElement(tag); if (cls) e.className = cls; return e; };
  el.innerHTML = '';
  let state = 'after';

  const fig = h('figure', 'hf-fig');
  // the toggle: two square segments, black when chosen
  const toggle = h('div', 'hf-toggle'); toggle.setAttribute('role', 'group'); toggle.setAttribute('aria-label', 'Show the work before or after a design harness');
  const btns = {};
  ['before', 'after'].forEach(k => {
    const b = h('button', 'hf-tab'); b.type = 'button'; b.textContent = STATES[k].tab; b.dataset.state = k;
    b.addEventListener('click', () => set(k));
    toggle.append(b); btns[k] = b;
  });
  const canvas = h('div', 'hf-canvas');
  const wires = document.createElementNS(NS, 'svg');
  wires.setAttribute('class', 'hf-wires'); wires.setAttribute('aria-hidden', 'true');
  const labels = h('div', 'hf-labels');
  const row = h('div', 'hf-row');
  canvas.append(wires, row, labels);
  const def = h('figcaption', 'hf-def'); def.id = 'hf-def'; def.setAttribute('aria-live', 'polite');
  const defName = h('span', 'hf-def-name'), defText = h('span', 'hf-def-text');
  def.append(defName, defText);
  const alt = h('p', 'sr-only');
  fig.append(toggle, canvas, def, alt);
  el.append(fig);

  let cards = {};
  const S = () => STATES[state];
  function build() {
    row.replaceChildren(); cards = {};
    row.dataset.state = state;
    S().steps.forEach(s => {
      const c = h('div', `hf-card hf-${s.key}`);
      c.dataset.key = s.key; c.tabIndex = 0; c.setAttribute('role', 'group'); c.setAttribute('aria-label', s.title); c.setAttribute('aria-describedby', 'hf-def');
      const ico = h('span', 'hf-ico'); ico.innerHTML = svgIcon(s.icon, 16);
      const t = h('span', 'hf-title'); t.textContent = s.title;
      c.append(ico, t); row.append(c); cards[s.key] = c;
    });
    alt.textContent = S().alt;
    for (const [k, b] of Object.entries(btns)) b.setAttribute('aria-pressed', String(k === state));
  }
  function set(k) { if (k === state) return; state = k; lit = pinned = null; build(); draw(); }

  // ---------- lines: thin, orthogonal, square corners, small open arrowheads ----------
  let paths = [];
  const box = (k) => { const c = cards[k], r = c.getBoundingClientRect(), o = canvas.getBoundingClientRect(); return { x: r.left - o.left, y: r.top - o.top, w: c.offsetWidth, h: c.offsetHeight }; };
  const head = (tip, from) => {
    const dx = Math.sign(tip[0] - from[0]), dy = Math.sign(tip[1] - from[1]), L = 5, W = 3.5;
    const bx = tip[0] - dx * L, by = tip[1] - dy * L;
    return ` M${bx + dy * W} ${by - dx * W} L${tip[0]} ${tip[1]} L${bx - dy * W} ${by + dx * W}`;
  };
  const wire = (pts, keys) => {
    const p = document.createElementNS(NS, 'path');
    p.setAttribute('d', 'M' + pts.map(q => q.join(' ')).join(' L') + head(pts[pts.length - 1], pts[pts.length - 2]));
    p.setAttribute('class', 'hf-wire'); p.dataset.keys = keys.join(' ');
    wires.append(p); paths.push(p);
  };
  const label = (text, x, y, cls) => { const s = h('span', `hf-label ${cls}`); s.textContent = text; s.style.left = `${x}px`; s.style.top = `${y}px`; labels.append(s); };

  // the loops: a dotted line as an SDF in a three.js shader (dots flow along the loop's arc length), with the
  // SVG keeping only the arrowhead. Until the shader is up, or under reduced motion, the SVG draws the dots itself.
  let loops = [];
  const loop = (pts, keys) => {
    const tip = pts[pts.length - 1], prev = pts[pts.length - 2];
    const hp = document.createElementNS(NS, 'path');
    hp.setAttribute('d', head(tip, prev).trim()); hp.setAttribute('class', 'hf-wire'); hp.dataset.keys = keys.join(' ');
    const dp = document.createElementNS(NS, 'path');
    dp.setAttribute('d', 'M' + pts.map(q => q.join(' ')).join(' L')); dp.setAttribute('class', 'hf-wire hf-dots'); dp.dataset.keys = keys.join(' ');
    wires.append(dp, hp); paths.push(hp, dp);
    loops.push({ pts, keys });
  };
  const gl = dotsGL(canvas);

  function draw() {
    loops = [];
    const W = canvas.clientWidth, H = canvas.clientHeight;
    wires.setAttribute('viewBox', `0 0 ${W} ${H}`); wires.setAttribute('width', W); wires.setAttribute('height', H);
    wires.replaceChildren(); labels.replaceChildren(); paths = [];
    const { steps, loops: LPS } = S();
    const G = 4, keys = steps.map(s => s.key), B = Object.fromEntries(keys.map(k => [k, box(k)]));
    const first = B[keys[0]];
    if (!NARROW.matches) {
      const y = first.y + first.h / 2;
      for (let i = 0; i < keys.length - 1; i++) { const a = B[keys[i]], b = B[keys[i + 1]]; wire([[a.x + a.w + G, y], [b.x - G, y]], [keys[i], keys[i + 1]]); }
      const off = 30;
      LPS.forEach(l => {
        const a = B[l.from], b = B[l.to], below = l.side === 'below';
        const ay = below ? a.y + a.h + G : a.y - G, by = below ? b.y + b.h + G : b.y - G, ly = below ? a.y + a.h + off : a.y - off;
        const ax = a.x + a.w / 2, bx = b.x + b.w / 2;
        loop([[ax, ay], [ax, ly], [bx, ly], [bx, by]], [...l.lights, l.key]);
        label(l.label, (ax + bx) / 2, ly, below ? 'is-below' : 'is-above');
      });
    } else {
      const x = first.x + first.w / 2;
      for (let i = 0; i < keys.length - 1; i++) { const a = B[keys[i]], b = B[keys[i + 1]]; wire([[x, a.y + a.h + G], [x, b.y - G]], [keys[i], keys[i + 1]]); }
      LPS.forEach((l, i) => {
        const a = B[l.from], b = B[l.to], gx = a.x + a.w + 14 + i * 14;
        loop([[a.x + a.w + G, a.y + a.h / 2], [gx, a.y + a.h / 2], [gx, b.y + b.h / 2], [b.x + b.w + G, b.y + b.h / 2]], [...l.lights, l.key]);
      });
    }
    light(lit);
  }

  // ---------- lighting ----------
  let lit = null, pinned = null;
  function light(key) {
    lit = key;
    for (const [k, c] of Object.entries(cards)) c.classList.toggle('is-lit', k === key);
    paths.forEach(p => p.classList.toggle('is-lit', !!key && p.dataset.keys.split(' ').includes(key)));
    gl.set(loops.map(l => ({ pts: l.pts, lit: !!key && l.keys.includes(key) })));
    const s = key && S().steps.find(s => s.key === key);
    defName.textContent = s ? s.title : S().idleName;
    defText.textContent = s ? s.def : S().idle;
  }
  const keyOf = (t) => t?.closest?.('.hf-card')?.dataset.key || null;
  canvas.addEventListener('pointerover', (e) => { const k = keyOf(e.target); if (k) light(k); });
  canvas.addEventListener('pointerout', (e) => { if (!keyOf(e.relatedTarget)) light(pinned); });
  canvas.addEventListener('click', (e) => { const k = keyOf(e.target); pinned = k; light(k); });
  canvas.addEventListener('focusin', (e) => { const k = keyOf(e.target); if (k) light(k); });
  canvas.addEventListener('focusout', (e) => { if (!canvas.contains(e.relatedTarget)) light(pinned); });

  build();
  const ro = new ResizeObserver(() => requestAnimationFrame(draw));
  ro.observe(canvas);
  NARROW.addEventListener('change', draw);
  document.fonts?.ready?.then(() => el.isConnected && draw());
  draw();
  return () => { ro.disconnect(); NARROW.removeEventListener('change', draw); gl.dispose(); };
}

// ---------- the dotted SDF ----------
// One transparent three.js plane over the canvas. Each loop is up to 3 segments; a pixel finds its nearest
// segment, its arc length there, and is ink inside a dot of radius r spaced every SP px, scrolling with time.
const THREE_URL = 'https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js';
const MAX = 8, SP = 6, SPEED = 14, TIP = 6;
function dotsGL(host) {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let T = null, renderer, scene, cam, mat, raf = 0, visible = false, dead = false, data = [];
  const cv = document.createElement('canvas'); cv.className = 'hf-gl'; cv.setAttribute('aria-hidden', 'true');
  const io = new IntersectionObserver(es => { visible = es[0].isIntersecting; tick(); });
  io.observe(host);
  const frag = `
    uniform vec4 uSeg[${MAX}]; uniform float uCum[${MAX}]; uniform float uLit[${MAX}]; uniform int uN;
    uniform float uTime, uDpr, uH; uniform vec3 uInk;
    void main() {
      vec2 p = vec2(gl_FragCoord.x, uH * uDpr - gl_FragCoord.y) / uDpr;
      float a = 0.0;
      for (int i = 0; i < ${MAX}; i++) {
        if (i >= uN) break;
        vec2 A = uSeg[i].xy, B = uSeg[i].zw, ab = B - A;
        float L = max(length(ab), 1e-3);
        float t = clamp(dot(p - A, ab) / (L * L), 0.0, 1.0);
        float d = length(p - (A + ab * t));
        float s = uCum[i] + t * L - uTime * ${SPEED.toFixed(1)};
        float al = mod(s, ${SP.toFixed(1)}) - ${(SP / 2).toFixed(1)};
        float r = mix(0.9, 1.35, uLit[i]);
        float sd = length(vec2(al, d)) - r;
        a = max(a, 1.0 - smoothstep(-0.6, 0.6, sd));
      }
      gl_FragColor = vec4(uInk * a, a);
    }`;
  import(THREE_URL).then(mod => {
    if (dead) return;
    T = mod;
    renderer = new T.WebGLRenderer({ canvas: cv, alpha: true, antialias: false, premultipliedAlpha: true });
    renderer.setClearColor(0x000000, 0);
    scene = new T.Scene(); cam = new T.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    mat = new T.ShaderMaterial({
      transparent: true, depthTest: false,
      uniforms: { uSeg: { value: Array.from({ length: MAX }, () => new T.Vector4()) }, uCum: { value: new Array(MAX).fill(0) }, uLit: { value: new Array(MAX).fill(0) },
        uN: { value: 0 }, uTime: { value: 0 }, uDpr: { value: 1 }, uH: { value: 1 }, uInk: { value: new T.Vector3() } },
      vertexShader: 'void main(){ gl_Position = vec4(position.xy, 0.0, 1.0); }',
      fragmentShader: frag,
    });
    scene.add(new T.Mesh(new T.PlaneGeometry(2, 2), mat));
    host.append(cv); host.classList.add('has-gl');
    push(); tick();
  }).catch(() => {});
  function push() {
    if (!mat) return;
    const W = host.clientWidth, H = host.clientHeight, dpr = Math.min(devicePixelRatio || 1, 2);
    renderer.setPixelRatio(dpr); renderer.setSize(W, H, false);
    cv.style.width = W + 'px'; cv.style.height = H + 'px';
    const m = getComputedStyle(host).color.match(/[\d.]+/g) || [0, 0, 0];
    mat.uniforms.uInk.value.set(m[0] / 255, m[1] / 255, m[2] / 255);
    mat.uniforms.uDpr.value = dpr; mat.uniforms.uH.value = H;
    let n = 0;
    data.forEach(l => {
      // stop the dots short of the arrowhead
      const pts = l.pts.map(p => p.slice()), k = pts.length - 1, a = pts[k - 1], b = pts[k];
      const len = Math.hypot(b[0] - a[0], b[1] - a[1]) || 1;
      b[0] -= (b[0] - a[0]) / len * TIP; b[1] -= (b[1] - a[1]) / len * TIP;
      let cum = 0;
      for (let i = 0; i < pts.length - 1 && n < MAX; i++, n++) {
        mat.uniforms.uSeg.value[n].set(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1]);
        mat.uniforms.uCum.value[n] = cum; mat.uniforms.uLit.value[n] = l.lit ? 1 : 0;
        cum += Math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]);
      }
    });
    mat.uniforms.uN.value = n;
    renderer.render(scene, cam);
  }
  function frame(t) {
    raf = 0;
    if (!mat || dead) return;
    mat.uniforms.uTime.value = t / 1000;
    renderer.render(scene, cam);
    tick();
  }
  function tick() { if (!raf && mat && visible && !reduced.matches && !dead) raf = requestAnimationFrame(frame); }
  return {
    set(next) { data = next; push(); },
    dispose() { dead = true; cancelAnimationFrame(raf); io.disconnect(); cv.remove(); host.classList.remove('has-gl'); mat?.dispose(); renderer?.dispose(); },
  };
}
```


Rendered DOM on the live site at 1440 (captured 2026-11-11):

```html
<div class="embed embed-harness-flow" data-embed="harness-flow" data-stream-skip="">
 <figure class="hf-fig">
  <div aria-label="Show the work before or after a design harness" class="hf-toggle" role="group">
   <button aria-pressed="false" class="hf-tab" data-state="before" type="button">
    Before
   </button>
   <button aria-pressed="true" class="hf-tab" data-state="after" type="button">
    After
   </button>
  </div>
  <div class="hf-canvas has-gl">
   <svg aria-hidden="true" class="hf-wires" height="154" viewbox="0 0 820 154" width="820">
    <path class="hf-wire" d="(icon path omitted)" data-keys="prompt harness">
    </path>
    <path class="hf-wire" d="(icon path omitted)" data-keys="harness agent">
    </path>
    <path class="hf-wire" d="(icon path omitted)" data-keys="agent design">
    </path>
    <path class="hf-wire" d="(icon path omitted)" data-keys="design complete">
    </path>
    <path class="hf-wire hf-dots" d="(icon path omitted)" data-keys="design agent moves">
    </path>
    <path class="hf-wire" d="(icon path omitted)" data-keys="design agent moves">
    </path>
    <path class="hf-wire hf-dots" d="(icon path omitted)" data-keys="complete harness records">
    </path>
    <path class="hf-wire" d="(icon path omitted)" data-keys="complete harness records">
    </path>
   </svg>
   <div class="hf-row" data-state="after">
    <div aria-describedby="hf-def" aria-label="Prompt" class="hf-card hf-prompt" data-key="prompt" role="group" tabindex="0">
     <span class="hf-ico">
      <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
       <path d="(icon path omitted)">
       </path>
      </svg>
     </span>
     <span class="hf-title">
      Prompt
     </span>
    </div>
    <div aria-describedby="hf-def" aria-label="Harness" class="hf-card hf-harness" data-key="harness" role="group" tabindex="0">
     <span class="hf-ico">
      <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
       <path d="(icon path omitted)">
       </path>
      </svg>
     </span>
     <span class="hf-title">
      Harness
     </span>
    </div>
    <div aria-describedby="hf-def" aria-label="Agent" class="hf-card hf-agent" data-key="agent" role="group" tabindex="0">
     <span class="hf-ico">
      <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
       <path d="(icon path omitted)">
       </path>
      </svg>
     </span>
     <span class="hf-title">
      Agent
     </span>
    </div>
    <div aria-describedby="hf-def" aria-label="Design" class="hf-card hf-design" data-key="design" role="group" tabindex="0">
     <span class="hf-ico">
      <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
       <path d="(icon path omitted)">
       </path>
      </svg>
     </span>
     <span class="hf-title">
      Design
     </span>
    </div>
    <div aria-describedby="hf-def" aria-label="Design complete" class="hf-card hf-complete" data-key="complete" role="group" tabindex="0">
     <span class="hf-ico">
      <svg aria-hidden="true" fill="currentColor" focusable="false" height="16" viewbox="0 0 24 24" width="16">
       <path d="(icon path omitted)">
       </path>
      </svg>
     </span>
     <span class="hf-title">
      Design complete
     </span>
    </div>
   </div>
   <div class="hf-labels">
    <span class="hf-label is-below" style="left: 403.484px; top: 128px;">
     moves: steer, concept, tune, comment
    </span>
    <span class="hf-label is-above" style="left: 418.281px; top: 26px;">
     fine-tune the harness: decisions kept as records
    </span>
   </div>
   <canvas aria-hidden="true" class="hf-gl" data-engine="three.js r186" height="154" style="width: 820px; height: 154px;" width="820">
   </canvas>
  </div>
  <figcaption aria-live="polite" class="hf-def" id="hf-def">
   <span class="hf-def-name">
    With a harness
   </span>
   <span class="hf-def-text">
    People fine-tune the harness, not the output. Every decision is kept, so each design starts further along than the last.
   </span>
  </figcaption>
  <p class="sr-only">
   After: a prompt goes to the harness, the harness gives the agent its context, the agent makes a design, and the design becomes design complete. The designer’s moves send the design back to the agent, and people fine-tune the harness: decisions are kept as records.
  </p>
 </figure>
</div>

```
