---
title: Orbs
slug: orbs
status: published
description: "The yellow \"new\" marker after a nav label: a 7px halftone metaball (5px small) that blooms in, leans to the cursor and melts into its label."
chips:
  - Motion
  - Orb
  - WebGL
created: 2026-11-11T16:02:22Z
updated: 2026-11-11T16:02:22Z
---

A section or room wears a full orb (`ORB.size` 7) when it is new itself, and a small one (`ORB.sizeSmall` 5) when something new waits inside it. An item works the same way (small when only a paragraph inside it is new). The label gets `.has-orb` (padding-right 13px: a 6px gap plus the 7px orb) and an `.sr-only` ", new". Orbs only exist when something is badged. **With emergence off on the live site, there are none.**

The orb is drawn in the one WebGL canvas (`ORB_DOTS_FRAG`, `ORB.style = 'dots'`). It is a smooth union of three wobbling discs, drawn as a fine halftone on a fixed screen grid (pitch 1.5 device px; dots sized by depth, so the core fills and the edge breaks into dots), with a hairline darker rim (`#A88300`) and a slight lower-right shade.

- **Colours:** yellow `#FFD400`, shade `#F0B400`, rim `#A88300`. In Marathon the light is the accent instead of gold (`accentLook`). On dark paper the falloff past the halo is a shadow, not brown.
- **Bloom:** grows from a point over 720ms with easeOutBack (overshoot 2.2).
- **Melt:** when cleared it melts into its label over 650ms.
- **Lean:** on hover it leans toward the cursor (`leanMax` .6, `leanEase` 6), and wobbles at speed .35.
- **Flare:** 900ms on arrival.
- **Sync:** 30 fps while an orb is on screen and someone is here. The glow style (the older one) is kept as tokens: gold or amber depending on `--fnd-warmth` .35.
- **CSS stand-ins:** `--orb-core: #FFC81A; --orb-edge: #FA9608; --orb-halo: #FFB21A`.

Source: `site/js/orb.js`, whole file

```js
// The "new" marker's look, shared by the site (js/gl.js), its demo
// (components/orb.html) and the tuning bench (tools/orb-bench.html).
// Pure numbers: no WebGL here.
import { ORB } from './tokens.js';

export const hexRGB = (h) => { const n = parseInt(h.replace('#', ''), 16); return [(n >> 16 & 255) / 255, (n >> 8 & 255) / 255, (n & 255) / 255]; };
const mixRGB = (a, b, t) => { const A = hexRGB(a), B = hexRGB(b); return A.map((v, i) => v + (B[i] - v) * t); };

// The four --fnd sliders (glow, sparkle, orbsize, warmth: 0 to 1) around ORB.
// At glow .5, sparkle .5, orbsize .5 you get ORB's values exactly.
export function orbLook(p, small = false) {
  const g = p.glow ?? 0.5, s = p.sparkle ?? 0.5, z = p.orbsize ?? 0.5, w = p.warmth ?? 0.35;
  const k = (6 + 2 * z) / 7;                                    // core 6 to 8px
  const live = 2 * s;                                           // 0 still, 1 as tuned, 2 lively
  return {
    size: (small ? ORB.sizeSmall : ORB.size) * k,
    halo: Math.min(30, (small ? ORB.haloSmall : ORB.halo) * (0.8 + 0.4 * g) * k),
    haloI: Math.min(1, ORB.haloI * (0.45 + 1.1 * g)) * (small ? 0.8 : 1),
    shadeI: ORB.shadeI,
    motes: Math.round((small ? ORB.motesSmall : ORB.motes) * Math.min(1.67, live)),
    pulse: (small ? ORB.pulseSmall : ORB.pulse) * (s < 0.1 ? 0 : 0.6 + 0.4 * live),
    bob: ORB.bob * live,
    speed: 0.4 + 0.6 * live,
    hot: mixRGB(ORB.gold.hot, ORB.amber.hot, w), core: mixRGB(ORB.gold.core, ORB.amber.core, w),
    edge: mixRGB(ORB.gold.edge, ORB.amber.edge, w), haloCol: mixRGB(ORB.gold.halo, ORB.amber.halo, w),
    shade: hexRGB(ORB.shadeCol), ink: hexRGB(ORB.inkCol)
  };
}

// The flare's envelope over its first ORB.flareMs: a fast rise, a long ease out.
export function orbFlare(ms, strength = ORB.flare) {
  const a = ms / ORB.flareMs;
  if (a < 0 || a >= 1) return 0;
  return strength * (a < 0.12 ? a / 0.12 : Math.pow(1 - (a - 0.12) / 0.88, 2));
}

// The bloom: from a point, overshoot, settle (easeOutBack).
export function orbBloom(ms) {
  const x = Math.min(1, Math.max(0, ms / ORB.bloomMs)), k = ORB.bloomOvershoot;
  return x >= 1 ? 1 : 1 + (k + 1) * Math.pow(x - 1, 3) + k * Math.pow(x - 1, 2);
}

// Every uniform the glow shader reads, with neutral values; set them per frame.
export function orbUniforms(THREE) {
  const v = (x) => ({ value: x });
  return {
    frame: v(new THREE.Vector4()), center: v(new THREE.Vector2()), target: v(new THREE.Vector2()), lean: v(new THREE.Vector2()),
    radius: v(3.5), bloom: v(0), melt: v(0), meltMove: v(1), fade: v(1), time: v(0), unit: v(1), seed: v(Math.random() * 50),
    pitch: v(ORB.pitch),
    edge: v(0), halo: v(ORB.halo), haloI: v(ORB.haloI), shadeI: v(ORB.shadeI), hover: v(0), flare: v(0),
    pulse: v(ORB.pulse), motes: v(ORB.motes), bob: v(ORB.bob), bar: v(ORB.barS),
    // colours as raw sRGB triples (Vector3, not THREE.Color, which would convert
    // them to linear; the canvas takes the shader's output as it is)
    cHot: v(new THREE.Vector3()), cCore: v(new THREE.Vector3()), cEdge: v(new THREE.Vector3()), cHalo: v(new THREE.Vector3()),
    cShade: v(new THREE.Vector3(...hexRGB(ORB.shadeCol))), cInk: v(new THREE.Vector3(...hexRGB(ORB.inkCol)))
  };
}

// Copy a look into the uniforms.
export function applyLook(u, L) {
  u.halo.value = L.halo; u.haloI.value = L.haloI; u.shadeI.value = L.shadeI;
  u.motes.value = L.motes; u.pulse.value = L.pulse; u.bob.value = L.bob; u.bar.value = ORB.barS;
  u.cHot.value.set(...L.hot); u.cCore.value.set(...L.core); u.cEdge.value.set(...L.edge); u.cHalo.value.set(...L.haloCol);
  u.cShade.value.set(...L.shade); u.cInk.value.set(...L.ink);
}

// The look in the theme's colours (js/theme.js colors): the sparks land in its
// ink; on dark paper the falloff past the halo is a shadow, not brown; and in
// Marathon the light itself is the accent instead of gold.
const mix3 = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
export function accentLook(L, c) {
  if (!L || !c) return L;
  L.ink = c.ink;
  if (c.dark) L.shade = c.shadow;
  if (c.marathon) {
    const g = c.glow;
    L.hot = mix3(g, [1, 1, 1], 0.82); L.core = g; L.haloCol = g;
    L.edge = c.dark ? mix3(g, [1, 1, 1], 0.25) : c.accentMark;
  }
  return L;
}
```


## Which items get one (app.js)

Source: `site/js/app.js`, lines 430 to 466

```js
// ---------- the yellow orbs ----------
// A section wears a full orb when it is new itself, a small one when something
// new waits inside it. An item likewise (small when only a paragraph is new).
function orbList() {
  const L = [];
  if (!route) return L;
  const newInside = (it) => it.paras.some(p => paraVisible(p, E.vis) && E.isBadged(p.id));
  // a room wears a full orb when one of its sections is new, a small one when something new waits inside
  for (const rm of visibleRooms()) {
    const secs = roomSections(rm);
    const own = secs.some(s => E.isBadged(s.id));
    const inner = secs.some(s => visibleItems(s, E.vis).some(it => E.isBadged(it.id) || newInside(it)));
    if (own || inner) L.push({ id: `nav:${rm.id}`, sel: `#nav [data-node="${rm.id}"]`, size: own ? ORB.size : ORB.sizeSmall });
  }
  for (const it of route && !route.app ? subItems(route) : []) {
    const own = E.isBadged(it.id);
    if (own || newInside(it)) L.push({ id: `sub:${it.id}`, sel: `#sub [data-node="${it.id}"]`, size: own ? ORB.size : ORB.sizeSmall });
  }
  return L;
}
// room for the orb after the label, and a word for screen readers
function markOrbs(list) {
  const on = new Set(list.map(o => o.sel));
  document.querySelectorAll('.item[data-node]').forEach(a => {
    const want = on.has(`#${a.closest('ul').id} [data-node="${a.dataset.node}"]`);
    a.classList.toggle('has-orb', want);
    let sr = a.querySelector('.sr-only');
    if (want && !sr) { sr = document.createElement('span'); sr.className = 'sr-only'; sr.textContent = ', new'; a.append(sr); }
    if (!want && sr) sr.remove();
  });
}
function syncOrbs() {
  const list = orbList();
  markOrbs(list);
  gl?.syncOrbs(list);
}
```


## The shader

Source: `site/js/glsl.js`, lines 420 to 605

```js
// The yellow "new" orb: a smooth union of three wobbling discs, drawn as a
// fine halftone (dots sized by depth, so the core fills and the edge breaks
// into dots), a hairline darker-yellow rim, and a slight lower-right shade.
// Units: everything in the page's CSS px; 'unit' is one device pixel of the
// real orb (1/dpr on the page, larger on the magnified demo).
// The first orb (ORB.style = 'dots'): a dot-matrix metaball with a darker rim.
export const ORB_DOTS_FRAG = /* glsl */`
${COMMON}
uniform vec4 frame;
uniform vec2 center, target, lean;
uniform float radius, bloom, melt, meltMove, fade, time, unit, pitch, seed;
uniform vec3 cYellow, cShade, cRim, cInk;
varying vec2 vUv;
float smin(float a, float b, float k){ float h = clamp(.5 + .5 * (b - a) / k, 0., 1.); return mix(b, a, h) - k * h * (1. - h); }
void main(){
  vec2 p = frame.xy + vec2(vUv.x, 1. - vUv.y) * frame.zw;
  float me = thinkEase(melt) * meltMove;
  vec2 c = mix(center, target, me);
  float r = radius * bloom * mix(1., .38, me);
  if (r < 0.05) discard;
  vec2 x = p - c;
  float tt = time + seed;
  vec2 o1 = vec2(snoise(vec3(tt, 1.3, 0.)), snoise(vec3(tt, 7.1, 0.))) * r * .2 + lean * .3;
  vec2 o2 = vec2(snoise(vec3(tt, 3.7, 2.)), snoise(vec3(tt, 9.9, 2.))) * r * .24 - lean * .12;
  vec2 o3 = lean * .8 + vec2(snoise(vec3(tt, 5., 4.)), snoise(vec3(tt, 2., 4.))) * r * .16;
  vec2 trail = (center - c) * .55;              // while melting, a drip trails back
  float d1 = length(x - o1) - r * .8;
  float d2 = length(x - o2) - r * .64;
  float d3 = length(x - o3 - trail) - r * .5 * (1. - me * .4);
  float d = smin(smin(d1, d2, r * .6), d3, r * .7);
  d += fbm(vec3(x / max(r, .5) * 1.2, tt * .8)) * r * .07;
  // halftone on a fixed screen grid: the fluid moves through it
  vec2 g = p / pitch;
  float cell = length(fract(g) - .5) * pitch;
  float depth = clamp(-d / (r * .55), 0., 1.);
  float dotR = pitch * (.32 + .3 * depth);
  float dots = 1. - smoothstep(dotR - unit * .5, dotR + unit * .5, cell);
  float inside = 1. - smoothstep(-unit * .5, unit * .5, d);
  float a = inside * mix(dots, 1., depth * depth * .6);
  // hairline rim, a touch inside the edge
  float rim = 1. - smoothstep(unit * .35, unit * 1.05, abs(d + unit * .55));
  vec3 col = mix(cYellow, cShade, clamp(.5 + .5 * dot(x / max(r, .5), vec2(.5, .6)), 0., 1.) * .85);
  col = mix(col, cRim, rim * .92);
  a = max(a, rim * .9 * inside);
  col = mix(col, cInk, smoothstep(.3, .8, me));
  a *= fade * (1. - smoothstep(.72, 1., melt));
  gl_FragColor = vec4(col, a);
}`;

// The "new" marker as a game pickup (ORB.style = 'glow'). Light on paper: additive
// light vanishes on white, so the glow is pigment. A hot pale core in a saturated
// yellow-to-amber body, a tinted halo that runs paler inside and warmer outside,
// a faint darker falloff past the halo so it pops, a pulse ring, orbiting motes,
// a flare when it first appears and, on open, sparks that fly into the label and
// darken to ink as they land. Everything is in CSS px; time in seconds.
export const ORB_GLOW_FRAG = /* glsl */`
uniform vec4 frame;
uniform vec2 center, target, lean;
uniform float radius, bloom, melt, meltMove, fade, time, unit, seed;
uniform float edge, halo, haloI, shadeI, hover, flare, pulse, motes, bob, bar;
uniform vec3 cHot, cCore, cEdge, cHalo, cShade, cInk;
varying vec2 vUv;
#define TAU 6.2831853
float h11(float n){ return fract(sin(n * 91.345 + 7.13) * 43758.5453); }
vec4 over(vec4 dst, vec3 c, float a){ a = clamp(a, 0., 1.); return vec4(c * a + dst.rgb * (1. - a), a + dst.a * (1. - a)); }
vec4 overP(vec4 dst, vec4 src){ return src + dst * (1. - src.a); }
// distance to a segment, and how far along it (0 at a, 1 at b)
vec2 segD(vec2 p, vec2 a, vec2 b){ vec2 pa = p - a, ba = b - a; float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-4), 0., 1.); return vec2(length(pa - ba * h), h); }
// a four-point twinkle: a round dot with two thin rays
float sparkle(vec2 q, float s){
  float dotA = 1. - smoothstep(s * .35, s * .35 + unit * 1.2, length(q));
  float rays = exp(-abs(q.x) / (unit * .9 + s * .08)) * max(0., 1. - abs(q.y) / (s * 1.4))
             + exp(-abs(q.y) / (unit * .9 + s * .08)) * max(0., 1. - abs(q.x) / (s * 1.4));
  return max(dotA, rays * .85);
}
void main(){
  vec2 p = frame.xy + vec2(vUv.x, 1. - vUv.y) * frame.zw;
  float tt = time + seed;
  float sp = mix(1., 2.2, hover);
  float fl = flare * (1. - min(1., melt * 4.));      // an open cuts a late flare short                       // hover: the shimmer runs faster
  float burst = melt * meltMove;                        // open: sparks fly (a plain fade under reduced motion)
  float pop = 1. - smoothstep(0., .22, burst);          // the core pops at the start of the burst
  float life = fade * (1. - smoothstep(.0, 1., melt) * (1. - meltMove));
  float breathe = .5 + .5 * sin(tt * TAU / bar * sp);
  vec2 c = center + vec2(0., sin(tt * TAU / (bar * 1.5)) * bob) + lean * .35;
  vec2 x = p - c;
  float d = length(x);
  float r = radius * bloom * pop * (1. + .07 * breathe + .18 * fl + .06 * hover);
  float H = .5 * halo * max(bloom, 0.) * (.9 + .1 * breathe) * (1. + .45 * fl + .12 * hover) * (1. + 1.2 * burst * (1. - burst));
  float I = haloI * (1. + .35 * hover + .6 * fl) * (1. - smoothstep(.1, .6, burst));
  // keep the light off the label: nothing but the sparks crosses its right edge
  // (a soft ramp, only across the label's own line)
  float band = 1. - smoothstep(radius * 1.2, radius * 3., abs(p.y - center.y));
  float mask = mix(1., pow(smoothstep(edge - 1.5, edge + 8., p.x), 1.5), band);
  vec4 o = vec4(0.);
  // a faint darker falloff just past the halo, so the light reads against paper
  float sh = shadeI * I * exp(-pow((d - H * .62) / (H * .28 + .01), 2.));
  o = over(o, cShade, sh * mask);
  // the halo: gaussian plus a short exponential skirt, paler inside, warmer outside
  float sg = max(H * .4, .01);
  float ha = I * (.7 * exp(-d * d / (2. * sg * sg)) + .3 * exp(-d / max(H * .28, .01)));
  vec3 hc = mix(mix(cHot, cCore, .6), cHalo, smoothstep(r * .8, H * .7, d));
  o = over(o, hc, ha * mask);
  // the pulse ring: once a cycle, a thin amber ring rides out and thins away
  if (pulse > 0.) {
    float ph = fract(tt * pulse / (bar * 2.) + .37);
    float k = clamp(ph / .55, 0., 1.);
    float rr = mix(r * 1.3, H * .95, 1. - pow(1. - k, 3.));
    float w = mix(unit * 1.6, unit * .8, k);
    float ring = 1. - smoothstep(w * .5, w * .5 + unit, abs(d - rr));
    o = over(o, cEdge, ring * .55 * pow(1. - k, 1.6) * step(ph, .55) * mask * (1. - burst) * bloom);
  }
  // motes on a tilted ellipse; those behind the core are hidden by it
  vec4 back = vec4(0.), front = vec4(0.);
  for (int i = 0; i < 6; i++) {
    float fi = float(i);
    float on = clamp(motes - fi, 0., 1.);
    if (on <= 0.) break;
    float ph = h11(fi + seed);
    float a = tt * TAU / (3.4 + fi * .9) * sp * (mod(fi, 2.) < .5 ? 1. : -.8) + ph * TAU;
    float R = r + (H - r) * (.5 + .22 * h11(fi * 3.1 + seed));
    vec2 q = vec2(cos(a) * R, sin(a) * R * .42);
    float tilt = -.35 + ph * .7;
    q = mat2(cos(tilt), sin(tilt), -sin(tilt), cos(tilt)) * q;
    float depth = sin(a);
    float tw = .55 + .45 * sin(tt * (5. + fi * 1.7) * sp + ph * 9.);
    float s = (1.3 + .5 * depth) * (1. + .25 * hover);
    float m = sparkle(x - q, s) * tw * on * (1. - burst) * clamp(bloom, 0., 1.) * mask;
    vec3 mc = mix(cEdge, cCore, .35 + .35 * tw);
    if (depth < 0.) back = over(back, mc, m * .8); else front = over(front, mc, m);
  }
  // the core: hot pale centre up and to the left, saturated body, amber edge
  // a light, not a ball: no gloss, a white-hot centre and an edge that bleeds into the halo
  float inside = 1. - smoothstep(r * .7 - unit * .5, r + unit * .7, d);
  float kh = length(x + vec2(.08, .1) * r) / max(r, .01);
  vec3 cc = mix(cHot, cCore, smoothstep(.1, .85, kh));
  cc = mix(cc, cEdge, smoothstep(.7, 1.15, d / max(r, .01)) * .55);
  // hover: a glint sweeps across
  float glint = smoothstep(.8, 1., sin((x.x - x.y) / max(r, .01) * 1.3 - tt * 5.5)) * hover;
  cc = mix(cc, cHot, glint * .8);
  // a hairline of ink-warm edge so the core holds its shape on white
  float rim = (1. - smoothstep(unit * .3, unit * 1.1, abs(d - r + unit * .5))) * .1;
  // back motes, the core, then front motes
  o = overP(o, back);
  o = over(o, mix(cc, cShade, rim), inside);
  o = overP(o, front);
  // the fl: a four-point lens star and a flash, the "new item!" moment
  if (fl > 0.) {
    float L = H * (1.1 + .9 * fl);
    float th = unit * .7 + r * .12;
    float star = exp(-abs(x.y) / th) * pow(max(0., 1. - abs(x.x) / L), 2.) + exp(-abs(x.x) / th) * pow(max(0., 1. - abs(x.y) / L), 2.);
    vec2 xd = mat2(.7071, .7071, -.7071, .7071) * x;
    star += .5 * (exp(-abs(xd.y) / th) * pow(max(0., 1. - abs(xd.x) / (L * .45)), 2.) + exp(-abs(xd.x) / th) * pow(max(0., 1. - abs(xd.y) / (L * .45)), 2.));
    o = over(o, mix(cEdge, cCore, exp(-d / (r + .01))), clamp(star, 0., 1.) * fl * mask);
  }
  // open: six sparks burst out, arc over and land across the label, darkening to ink
  if (burst > 0.) {
    for (int i = 0; i < 6; i++) {
      float fi = float(i);
      float s = clamp((burst - fi * .045) / .72, 0., 1.);
      if (s <= 0.) continue;
      float ang = fi / 6. * TAU + seed + (h11(fi + 2.) - .5) * .8;
      vec2 p0 = center, p1 = center + vec2(cos(ang), sin(ang) * .8) * halo * (.5 + .3 * h11(fi + 5.));
      vec2 p2 = vec2(mix(target.x, edge - 2., h11(fi * 7.3) * .85), target.y + (h11(fi * 1.9) - .5) * radius * 1.4);
      float e = s < .5 ? 2. * s * s : 1. - pow(-2. * s + 2., 2.) / 2.;
      float e0 = max(0., e - .06);
      vec2 a = mix(mix(p0, p1, e0), mix(p1, p2, e0), e0);
      vec2 b = mix(mix(p0, p1, e), mix(p1, p2, e), e);
      float sz = mix(1.3, .6, s) * (radius / 3.5);
      vec2 sd = segD(p, a, b);
      float live = (1. - smoothstep(.82, 1., s)) * smoothstep(0., .04, s);
      // a thin tail that fades behind a twinkling head
      float tail = (1. - smoothstep(sz * .22, sz * .22 + unit, sd.x)) * sd.y * sd.y * .8;
      float head = sparkle(p - b, sz * 1.7);
      float glow = exp(-length(p - b) / (sz * 1.2)) * .4 * (1. - s);
      vec3 sc = mix(mix(cHot, cEdge, smoothstep(0., .6, s)), cInk, smoothstep(.55, .95, s));
      o = over(o, cHalo, glow * live);
      o = over(o, sc, max(tail, head) * live);
    }
  }
  o *= life;
  if (o.a < .002) discard;
  gl_FragColor = vec4(o.rgb / o.a, o.a);
}`;

export const ORB_FRAG = ORB.style === 'dots' ? ORB_DOTS_FRAG : ORB_GLOW_FRAG;
```

## The orb stage (review bench, not on the site)

`orb-stage.js` draws the same marker outside the site, for the demo page and the bench tiles. It renders a 16px Inter Display label on white with the marker after it, magnified into any 2D canvas. One offscreen WebGL renderer serves every canvas, so a page never runs out of WebGL contexts. It uses the same shader (`ORB_GLOW_FRAG`) and the same uniforms (`orbUniforms`, `applyLook`, `orbFlare`, `orbBloom`) as the site. Nothing on saleh.digital imports it, and with emergence off no orb is drawn there anyway.

Source: `site/js/orb-stage.js`, whole file

```js
// A stage for looking at the "new" marker outside the site: a 16px label on
// white with the marker after it, magnified, drawn into any 2D canvas. One
// offscreen WebGL renderer serves every canvas (the demo, every bench tile),
// so a page never runs out of contexts. Same shader, same uniforms as the site.
import { ORB_GLOW_FRAG, QUAD_VERT } from './glsl.js';
import { ORB } from './tokens.js';
import { orbUniforms, applyLook, orbFlare, orbBloom } from './orb.js';

export const LABEL_FONT = '"Inter Display", "Helvetica Neue", Arial, sans-serif';

export async function loadLabelFont(base) {
  try {
    const fs = [new FontFace('Inter Display', `url(${base}fonts/InterDisplay-Regular.woff2)`)];
    for (const f of await Promise.all(fs.map(f => f.load()))) document.fonts.add(f);
  } catch (e) { console.warn('label font', e); }
}

export function createOrbStage(THREE) {
  const glc = document.createElement('canvas');
  const renderer = new THREE.WebGLRenderer({ canvas: glc, alpha: true, antialias: false, premultipliedAlpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setClearColor(0, 0);
  const camera = new THREE.OrthographicCamera(-0.5, 0.5, 0.5, -0.5, -1, 1);
  const scene = new THREE.Scene();
  const u = orbUniforms(THREE);
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.ShaderMaterial({ vertexShader: QUAD_VERT, fragmentShader: ORB_GLOW_FRAG, uniforms: u, transparent: true, depthTest: false, depthWrite: false }));
  scene.add(mesh);

  // s: { width, height (CSS px of the target), dpr, zoom, label, look, time (s),
  //      age (ms since it appeared), hover 0..1, melt 0..1, lean {x,y}, seed, reduced }
  // Returns the layout in site px, so a caller can hit-test the marker.
  function draw(ctx, s) {
    const dpr = s.dpr || 1, Z = s.zoom || 1, W = s.width, H = s.height;
    const pw = Math.max(1, Math.round(W * dpr)), ph = Math.max(1, Math.round(H * dpr));
    if (glc.width !== pw || glc.height !== ph) renderer.setSize(pw, ph, false);
    // the scene in site px
    const sw = W / Z, sh = H / Z, L = s.look;
    ctx.save();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H);
    ctx.scale(Z, Z);
    ctx.font = `400 16px ${LABEL_FONT}`;
    if ('letterSpacing' in ctx) ctx.letterSpacing = '-0.64px';
    const label = s.label || 'Articles';
    const tw = ctx.measureText(label).width, cap = ctx.measureText('H').actualBoundingBoxAscent || 11.4;
    const r = L.size / 2 * (s.sizeScale || 1);
    const left = Math.round((sw - (tw + ORB.gap + 2 * r)) / 2 + (s.shift || 0)), base = Math.round(sh / 2 + cap / 2 - (s.lift || 0));
    ctx.fillStyle = '#000'; ctx.textBaseline = 'alphabetic';
    ctx.fillText(label, left, base);
    ctx.restore();
    const cy = base - cap / 2, cx = left + tw + ORB.gap + r;
    u.frame.value.set(0, 0, sw, sh);
    u.center.value.set(cx, cy); u.target.value.set(left + cap * 0.22, cy);
    u.lean.value.set(s.lean?.x || 0, s.lean?.y || 0);
    u.edge.value = left + tw + 0.5;
    u.radius.value = r;
    applyLook(u, L);
    const age = s.age ?? 1e9;
    u.bloom.value = s.reduced ? 1 : orbBloom(age);
    u.flare.value = s.reduced ? 0 : orbFlare(age, L.flare ?? ORB.flare);
    u.melt.value = s.melt || 0; u.meltMove.value = s.reduced ? 0 : 1; u.fade.value = 1;
    u.hover.value = s.hover || 0; u.time.value = s.reduced ? 0 : (s.time || 0);
    u.unit.value = 1 / (Z * dpr); u.seed.value = s.seed ?? 3.1;
    if (s.reduced) { u.pulse.value = 0; u.bob.value = 0; }
    renderer.render(scene, camera);
    ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.drawImage(glc, 0, 0, ctx.canvas.width, ctx.canvas.height);
    ctx.restore();
    return { cx, cy, r, left, right: left + tw, zoom: Z };
  }
  return { draw, renderer };
}
```

