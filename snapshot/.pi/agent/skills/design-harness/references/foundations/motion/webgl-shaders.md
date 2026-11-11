---
title: WebGL shaders
slug: webgl-shaders
status: published
description: "js/glsl.js whole: every vertex and fragment shader of the GL layer, verbatim, with a table of every uniform and its value or animation."
chips:
  - Motion
  - WebGL
  - Shader
created: 2026-11-11T16:29:16Z
updated: 2026-11-11T16:31:20Z
---

Every shader the site's GL layer runs lives in `js/glsl.js`, as `/* glsl */` template strings. They are `THREE.ShaderMaterial` sources: three.js (0.186.1, WebGL2) prepends its own prefix, so `position`, `uv`, `projectionMatrix` and `modelViewMatrix` are declared for you, and `texture2D`, `varying` and `gl_FragColor` are mapped to GLSL ES 3.00. The file is quoted whole at the end. The gallery grids and the harness-flow embed run their own shaders, quoted whole in their records ([bookshelf](../../components/patterns/bookshelf.md), [spine](../../components/components/spine.md), [glyph matrix](../../components/patterns/glyph-matrix.md), [coffee table](../../components/patterns/coffee-table.md), [harness flow](../../components/patterns/harness-flow.md)).

## The programs

| Export | Kind | Used by (js/gl.js) | Draws |
|---|---|---|---|
| `COMMON` | GLSL chunk | prepended to the fragments | simplex noise `snoise`, `fbm`, `hash`, the think ease (`THINK_POW` 2.4, `THINK_LINEAR` .15 from `js/tokens.js`) |
| `QUAD_VERT` | vertex | every on-screen quad | passes `uv` as `vUv`; `projectionMatrix * modelViewMatrix * position` |
| `FS_VERT` | vertex | the JFA passes | `gl_Position = vec4(position.xy, 0, 1)` (a 2×2 plane fills clip space) |
| `JFA_SEED` | fragment | `seedMat` | per texel, the **offset** to its nearest inside (RG) and outside (BA) pixel: a texel with mask alpha > .5 starts as `(0, 0, FAR, FAR)`, else `(FAR, FAR, 0, 0)` (`FAR` 16384, `NONE` 8192) |
| `JFA_STEP` | fragment | `stepMat` | one jump-flood step: the 8 neighbours at ±`stepPx` (inside `res`); keep the shortest inside and outside offsets |
| `JFA_FINAL` | fragment | `finalMat` | signed distance (`inside: −(dOut − .5)`, `outside: dIn − .5`; edge texels `0.5 − alpha` for sub-pixel accuracy) × `invScale` into CSS px, clamped to ±500, into an R16F target |
| `ITEM_FRAG` | fragment | `morphItem` | one element resolving A → B along `t`: field mix, edge noise, grain, blur, the icon dot-matrix dissolve |
| `LINES_FRAG` | fragment | `morphBody` | a post body resolving line by line (staggered, top to bottom) |
| `WORD_FRAG` | fragment | the wordmark mesh | the live wordmark, its five life stages, traces, the Arabic hold mix, the cursor warp, and the whole footer pass (bio, basmala, links, marks, dot strips) |
| `ORB_GLOW_FRAG` | fragment | orbs (`ORB.style` ≠ `'dots'`, the live style) | the yellow "new" orb: core, halo, flare, motes, lean and melt |
| `ORB_DOTS_FRAG` | fragment | orbs when `ORB.style === 'dots'` | the halftone metaball variant |
| `ORB_FRAG` | alias | | `ORB.style === 'dots' ? ORB_DOTS_FRAG : ORB_GLOW_FRAG` |

## The wordmark's life (stages in WORD_FRAG)

Life runs from 0 to 1 (`E.life()`, or `--fnd-life` when above 0). It layers five stages, each fading in as `life × 5` goes from k − 1 to k:

1. edge boil (`LIFE.boil` .7 px)
2. an ink halftone inside the strokes (dot pitch `LIFE.dotPitch` 2.4 px, fbm drift `dotDrift` .6 px)
3. iso-line ripples on the bar clock (92 bpm; spacing `rippleSpacing` 9 px, alpha `rippleAlpha` .13, reach `rippleReach` 46 px)
4. letters melting at the joins (smooth-min of the even and odd glyph fields, radius `meld` .42 × cap / 10), with the dots flowing along the strokes (`flow` 6 px/s)
5. fully alive: found secrets leave yellow traces (radius `traceRadius` .32 × cap), and the `hold` secret leaves the Arabic ghost in the halftone (`ghostAlpha` .16)

The cursor warps the word within `mouseR` (gain up to `cursorGain` 2.2 with stage 1). A level rise first swells the word toward `--swell` (`LIFE.swell` 1.4) and settles over `settleMs` 1800. At rest it breathes `breathPx(E)`, 0.9 px at energy .5. **On the live site, with emergence off, life is 0**: only the static edge noise, grain, breathing and cursor response show. The footer takes `FOOT.bio` .3 of every stage for the bio and `FOOT.marks` 1 for the marks, so at life 0 it is as crisp as the DOM. (`FOOT.maxWarp` .4 px is declared in `js/tokens.js` as the bio's displacement cap, but nothing reads it: the shader uses its own `BIO_INK` constants.)

## Uniforms and their values

All lengths are CSS px in **document** space unless noted; boxes are `vec4(x, y, w, h)`. "Per frame" values are set in `step()` of [the renderer](webgl-renderer.md).

### JFA

| Uniform | Value |
|---|---|
| `src` | the mask `CanvasTexture` (nearest) |
| `res` | mask size in texels |
| `prev` | the previous ping-pong target |
| `texSize` | the pool's allocated size (≥ `res`, multiple of 128) |
| `stepPx` | `2^ceil(log2(max(w,h)))/2`, halving to 1, then 1 again |
| `jfa` | the last ping-pong target |
| `invScale` | `1 / scale` (field texels per CSS px) |

### ITEM_FRAG (one element)

| Uniform | Value / animation |
|---|---|
| `sdfA`, `sdfB`, `dispA`, `dispB` | the before/after fields and display rasters (`blank` when absent) |
| `boxA`, `boxB`, `frame` | their boxes, and their union (the quad) |
| `hasA`, `hasB` | 1 or 0 |
| `t`, `raw` | `raw = (now − start) / total`, `t = think(raw)` |
| `time` | the loop clock, seconds (frozen under reduced motion) |
| `amp` | the resolve amplitude passed by `run()` |
| `bA`, `bB`, `oA`, `oB` | each side's CSS blur px and opacity |
| `grain` | `0.3 + 0.5 · texture` |
| `seed` | a random start + 1.37 per item |
| `aa` | `0.6 / dpr` |
| `uInk` | the theme's ink |
| `shift` | B.rect − A.rect when the same text moved, else 0 |
| `dots`, `pitch`, `blurPeak` | icon toggles: dot-matrix dissolve on/off, pitch (default 1.75), peak blur |

### LINES_FRAG (a post body)

| Uniform | Value / animation |
|---|---|
| fields and boxes | as ITEM_FRAG |
| `elapsed` | ms since start, per frame |
| `dur`, `stagger`, `inDelay` | the resolve's duration, `MOTION.staggerMs`, `dur · 0.2` |
| `time`, `amp`, `aa`, `grain`, `uInk` | as ITEM_FRAG |
| `blurMax` | `2.6 + 2 · energy` |
| `linesA[64]`, `linesB[64]`, `nA`, `nB` | line bottoms of each side (unused slots 1e6), and counts (≤ `MAXL` 64) |

### WORD_FRAG (the wordmark and the footer)

| Uniform | Value / animation |
|---|---|
| `sdf`, `box` | the word's field and its document box (follows the SVG anchor every frame) |
| `sdfE`, `sdfO` | even and odd glyph fields, built lazily once life·5 > 3.02 (stage 4 melts adjacent letters with `smin`) |
| `sdfB`, `mixB` | the Arabic hold field; `mixB` runs `from → to` along `think()` over 1100ms (120ms reduced) |
| `st`, `st5` | stages `s1..s4`, `s5`: `smoothstep(k−1, k, life·5)`; all 0 under `?lite` |
| `reach` | the furthest any edge can travel this frame (an early-out bound) |
| `bar`, `beat` | `barPhase(t)` at 92 bpm 4/4 (a bar ≈ 2.61s), `(bar·4) mod 1`; 0 under reduced motion |
| `cap` | the word's cap height (ascent at the fitted size); 80 until fitted |
| `ghost` | `LIFE.ghostAlpha` .16 while the `hold` secret is found and the Arabic field exists |
| `ripples` | 1, or 0 under reduced motion |
| `flowT` | `+= dt · LIFE.flow` (6 px/s) |
| `kBoil` | `LIFE.boil` .7 × `max(.35, capK)`; `capK = min(1, cap/80)` |
| `kCursor` | `LIFE.cursorGain` 2.2 |
| `kPitch` | `max(1.1, LIFE.dotPitch 2.4 × capK)` |
| `kDrift` | `LIFE.dotDrift` .6 |
| `kSpacing` | `max(4, LIFE.rippleSpacing 9 × capK)` |
| `kRipple` | `LIFE.rippleAlpha` .13 |
| `kReach` | `max(12, LIFE.rippleReach 46 × capK)` |
| `kMeld` | `LIFE.meld` .42 |
| `traces[4]` | `(cx, cy, cap · .32, 1)` at each found secret's letter (`traceLetters` warm 9, hold 0, harness 4, night 7) |
| `cYellow`, `cRim` | `ORB.yellow`, `ORB.rim`; in Marathon the theme's `glow` and `accent-mark` |
| `time` | the loop clock, seconds |
| `breath` | `MOTION.breathPx(energy) = 0.3 + 1.2·energy` (0.9 at the default .5); 0 reduced |
| `thinking` | the thinking swell: target decays `×0.5^(dt/450)`, value eases `1 − 0.001^(dt/1000)`; 0 reduced |
| `aa` | `0.6 / dpr` (0.4 before the first fit) |
| `grain` | `0.04 + 0.22 · texture` (0.128 at texture .4) |
| `ink` | `0.05 + 0.3 · texture` (0.17 at texture .4) |
| `uInk`, `uSwell`, `uFoot` | the theme's ink, swell and foot colours |
| `mouse`, `mouseOn`, `mouseR` | pointer in document px; eased presence (`1 − 0.02^(dt/1000)`, 0 reduced); `clamp(W · 0.06, 60, 140)` |
| `frame` | union of the word box and the footer box (the quad) |
| `sdfF`, `boxF`, `hasF`, `aaF` | the footer's field and box, 1 when baked, `0.55 / dpr` |
| `kF`, `kM` | `FOOT.bio` .3, `FOOT.marks` 1: the share of the word's stages the bio and marks take |
| `basF` | the basmala's box (it takes the word's hover at 18px) |
| `dotR[2]` | the two dot strips' boxes (`w = 0`: none) |
| `dotB[16]` | blobs `(x, y, r, strip)`, `w = −1` unused: `x = ((i + .5)/n + .06 sin(.21T + ph)) · w`, `y = h(.5 + .35 sin(.33T + 1.7ph))`, `r = 5 + 4(.5 + .5 sin(.27T + .9ph))`, `ph = 2.399i + 1.3·strip`, `T = s · (0.4 + 1.2·energy)` (0 reduced) |
| `marks[4]`, `markSoft` | each mark's centre, half-size + 2, hover focus (eased τ 90ms); each mark's extra softness px |

Constants in the shader: `BIO_INK = (1.4, 3, .6)`, `FOOT_HOVER = (1.2, .14, 1, .42)`, `DOT_PITCH 4.8`, `DOT_RMAX 1.7`, `DOT_RMIN .45`, `DOT_INK = (1.4, 2.6, .6)`, `DOT_HOVER = (.8, .3, .8, .42)`.

### Orbs

The orb uniforms come from `orbUniforms(THREE)` and `applyLook()` in `js/orb.js` ([orbs](orbs.md)). Per frame `js/gl.js` sets `center`, `target` (the label's first letter), `lean` (eased `1 − e^(−ORB.leanEase·dt)`), `radius`, `bloom` (easeOutBack over `ORB.bloomMs`, overshoot `ORB.bloomOvershoot`), `melt` (over `ORB.burstMs`; 160ms reduced), `meltMove` (0 reduced), `unit = 1/dpr`, `flare = orbFlare(age)`, `time` (orb clock × look speed), `hover` (τ `ORB.hoverMs/3`), `edge` (the label's right edge + .5), and `frame`. On the live site no orb is drawn, because emergence is off.

## The file

Source: `site/js/glsl.js`, whole file

```js
// Shared GLSL: simplex noise, fbm, hash, the think ease and the shader sources.
import { THINK_POW, THINK_LINEAR, ORB } from './tokens.js';

export const COMMON = /* glsl */`
#define PI 3.14159265
vec3 mod289(vec3 x){return x-floor(x*(1./289.))*289.;}
vec4 mod289(vec4 x){return x-floor(x*(1./289.))*289.;}
vec4 permute(vec4 x){return mod289(((x*34.)+1.)*x);}
vec4 taylorInvSqrt(vec4 r){return 1.79284291400159-0.85373472095314*r;}
float snoise(vec3 v){
  const vec2 C=vec2(1./6.,1./3.); const vec4 D=vec4(0.,.5,1.,2.);
  vec3 i=floor(v+dot(v,C.yyy)); vec3 x0=v-i+dot(i,C.xxx);
  vec3 g=step(x0.yzx,x0.xyz); vec3 l=1.-g; vec3 i1=min(g.xyz,l.zxy); vec3 i2=max(g.xyz,l.zxy);
  vec3 x1=x0-i1+C.xxx; vec3 x2=x0-i2+C.yyy; vec3 x3=x0-D.yyy;
  i=mod289(i);
  vec4 p=permute(permute(permute(i.z+vec4(0.,i1.z,i2.z,1.))+i.y+vec4(0.,i1.y,i2.y,1.))+i.x+vec4(0.,i1.x,i2.x,1.));
  float n_=0.142857142857; vec3 ns=n_*D.wyz-D.xzx;
  vec4 j=p-49.*floor(p*ns.z*ns.z);
  vec4 x_=floor(j*ns.z); vec4 y_=floor(j-7.*x_);
  vec4 x=x_*ns.x+ns.yyyy; vec4 y=y_*ns.x+ns.yyyy; vec4 h=1.-abs(x)-abs(y);
  vec4 b0=vec4(x.xy,y.xy); vec4 b1=vec4(x.zw,y.zw);
  vec4 s0=floor(b0)*2.+1.; vec4 s1=floor(b1)*2.+1.; vec4 sh=-step(h,vec4(0.));
  vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy; vec4 a1=b1.xzyw+s1.xzyw*sh.zzww;
  vec3 p0=vec3(a0.xy,h.x); vec3 p1=vec3(a0.zw,h.y); vec3 p2=vec3(a1.xy,h.z); vec3 p3=vec3(a1.zw,h.w);
  vec4 norm=taylorInvSqrt(vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3)));
  p0*=norm.x;p1*=norm.y;p2*=norm.z;p3*=norm.w;
  vec4 m=max(.6-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),0.); m=m*m;
  return 42.*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));
}
float fbm(vec3 p){ float a=.5, s=0.; for(int i=0;i<3;i++){ s+=a*snoise(p); p=p*2.03+vec3(1.7,9.2,3.1); a*=.5; } return s/.875; }
// two octaves: for slow, low-frequency warps where the third is under a pixel
float fbm2(vec3 p){ return (.5*snoise(p) + .25*snoise(p*2.03+vec3(1.7,9.2,3.1))) / .75; }
vec2 warp2(vec3 c){ return vec2(snoise(c), snoise(c + vec3(19.1, 3.3, -7.7))); }
float hash12(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
float thinkEase(float t){ t=clamp(t,0.,1.); float u=2.*t-1.; float s=.5+.5*sign(u)*pow(abs(u),${THINK_POW.toFixed(3)}); return ${THINK_LINEAR.toFixed(3)}*t+${(1 - THINK_LINEAR).toFixed(3)}*s; }
`;

export const QUAD_VERT = /* glsl */`
varying vec2 vUv;
void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;

export const FS_VERT = /* glsl */`void main(){ gl_Position = vec4(position.xy, 0.0, 1.0); }`;

// Jump flood, in a grow-only pooled RGBA16F pair (js/gl.js). Each texel holds
// the OFFSET to its nearest seed, not the seed's position: offsets are whole
// pixels and stay small where the field matters, so half floats store them
// exactly (to 2048 px). RG: nearest inside pixel, BA: nearest outside pixel.
// res is the region in use (the pool is often larger), texSize the pool.
const JFA_FAR = /* glsl */`
#define FAR 16384.
#define NONE 8192.`;

export const JFA_SEED = /* glsl */`
${JFA_FAR}
uniform sampler2D src; uniform vec2 res;
void main(){
  vec2 p = gl_FragCoord.xy; float a = texture2D(src, p / res).a;
  gl_FragColor = a > 0.5 ? vec4(0., 0., FAR, FAR) : vec4(FAR, FAR, 0., 0.);
}`;

export const JFA_STEP = /* glsl */`
${JFA_FAR}
uniform sampler2D prev; uniform vec2 res, texSize; uniform float stepPx;
void main(){
  vec2 p = gl_FragCoord.xy; vec4 best = texture2D(prev, p / texSize);
  float dI = length(best.xy), dO = length(best.zw);
  for (int j = -1; j <= 1; j++) for (int i = -1; i <= 1; i++) {
    if (i == 0 && j == 0) continue;
    vec2 off = vec2(float(i), float(j)) * stepPx;
    vec2 q = p + off;
    if (q.x < 0. || q.y < 0. || q.x > res.x || q.y > res.y) continue;
    vec4 s = texture2D(prev, q / texSize);
    if (s.x < NONE) { vec2 o = s.xy + off; float a = length(o); if (a < dI) { dI = a; best.xy = o; } }
    if (s.z < NONE) { vec2 o = s.zw + off; float b = length(o); if (b < dO) { dO = b; best.zw = o; } }
  }
  gl_FragColor = best;
}`;

// Signed distance in CSS px (negative inside), into a single-channel R16F
// target. Edge pixels use coverage for sub-pixel accuracy.
export const JFA_FINAL = /* glsl */`
uniform sampler2D jfa; uniform sampler2D src; uniform vec2 res, texSize; uniform float invScale;
void main(){
  vec2 p = gl_FragCoord.xy; vec4 s = texture2D(jfa, p / texSize); float a = texture2D(src, p / res).a;
  float dIn = length(s.xy), dOut = length(s.zw);
  float d = a > 0.5 ? -(dOut - 0.5) : (dIn - 0.5);
  if ((a > 0.5 ? dOut : dIn) < 1.01) d = 0.5 - a;
  gl_FragColor = vec4(clamp(d * invScale, -500., 500.), 0., 0., 1.);
}`;

// One morph item: field A to field B, noise peaking mid-flight, blur as a widened edge.
export const ITEM_FRAG = /* glsl */`
${COMMON}
uniform sampler2D sdfA, sdfB, dispA, dispB;
uniform vec4 boxA, boxB, frame;
uniform float hasA, hasB, t, raw, time, amp, bA, bB, oA, oB, grain, seed, aa;
uniform vec2 shift; // same text that moved: both fields travel together
uniform vec3 uInk; // the theme's ink (js/theme.js)
uniform float dots, pitch, blurPeak; // icon toggles: dissolve through a dot matrix mid-flight (0 = off)
varying vec2 vUv;
float fA(vec2 p){ if (hasA < .5) return 24.; return texture2D(sdfA, (p - boxA.xy) / boxA.zw).r; }
float fB(vec2 p){ if (hasB < .5) return 24.; return texture2D(sdfB, (p - boxB.xy) / boxB.zw).r; }
float gA(vec2 p){ if (hasA < .5) return 0.; vec2 u = (p - boxA.xy) / boxA.zw; return (u.x<0.||u.y<0.||u.x>1.||u.y>1.) ? 0. : texture2D(dispA, u).a; }
float gB(vec2 p){ if (hasB < .5) return 0.; vec2 u = (p - boxB.xy) / boxB.zw; return (u.x<0.||u.y<0.||u.x>1.||u.y>1.) ? 0. : texture2D(dispB, u).a; }
void main(){
  vec2 p = frame.xy + vec2(vUv.x, 1. - vUv.y) * frame.zw;
  float env = sin(PI * t);
  float n = amp * env;
  vec3 c = vec3(p * 0.06, time * 0.8 + seed);
  vec2 warp = vec2(fbm(c), fbm(c + vec3(17.3, -9.1, 4.7)));
  vec2 q = p + warp * n;
  float d = mix(fA(q - shift * t), fB(q + shift * (1. - t)), t);
  d += snoise(vec3(p * 0.4, time * 5. + seed)) * 0.2 * n;
  float b = mix(bA, bB, t);
  float w = aa + b * 1.6;
  float a = 1. - smoothstep(-w, w, d + b * 0.9);
  if (dots > 0.) {
    // the icon toggle: mid-flight the shape becomes a halftone. Dots sit on a
    // ~1.75px grid, their centres jittered by the fbm; each dot's radius follows
    // a widened (blurred) coverage of the field, so dots are fattest inside the
    // shape and shrink to nothing past its edge. Crisp at t = 0 and 1.
    float de = env * dots;
    float wd = aa + blurPeak * de;
    float cov = 1. - smoothstep(-wd, wd, d);
    vec2 cell = fract((p + warp * pitch * .4 * de) / pitch) - .5;
    float dotR = pitch * .64 * sqrt(cov);
    float dotA = 1. - smoothstep(dotR - aa, dotR + aa, length(cell) * pitch);
    dotA *= smoothstep(.02, .16, cov); // past the edge the dots shrink to nothing, not to an anti-aliased haze
    a = mix(a, dotA, smoothstep(0., .3, de));
  }
  a *= mix(oA, oB, t);
  float g = hash12(floor(p * 2.) + floor(time * 24.) * 7.31);
  a *= 1. - grain * env * g;
  a = mix(a, gA(p - shift * t), 1. - smoothstep(0., .14, raw));
  a = mix(a, gB(p + shift * (1. - t)), smoothstep(.86, 1., raw));
  gl_FragColor = vec4(uInk, a);
}`;

// Body: line by line, staggered top to bottom. Outgoing lines boil away,
// incoming lines condense from a noisy, wide field to sharp.
export const LINES_FRAG = /* glsl */`
${COMMON}
#define MAXL 64
uniform sampler2D sdfA, sdfB, dispA, dispB;
uniform vec4 boxA, boxB, frame;
uniform float hasA, hasB, elapsed, dur, stagger, inDelay, time, amp, aa, grain, blurMax;
uniform float linesA[MAXL]; uniform float linesB[MAXL];
uniform int nA, nB;
uniform vec3 uInk;
varying vec2 vUv;
float fA(vec2 p){ if (hasA < .5) return 24.; return texture2D(sdfA, (p - boxA.xy) / boxA.zw).r; }
float fB(vec2 p){ if (hasB < .5) return 24.; return texture2D(sdfB, (p - boxB.xy) / boxB.zw).r; }
float gA(vec2 p){ vec2 u = (p - boxA.xy) / boxA.zw; return (hasA<.5||u.x<0.||u.y<0.||u.x>1.||u.y>1.) ? 0. : texture2D(dispA, u).a; }
float gB(vec2 p){ vec2 u = (p - boxB.xy) / boxB.zw; return (hasB<.5||u.x<0.||u.y<0.||u.x>1.||u.y>1.) ? 0. : texture2D(dispB, u).a; }
void main(){
  vec2 p = frame.xy + vec2(vUv.x, 1. - vUv.y) * frame.zw;
  float iA = 0., iB = 0.;
  for (int i = 0; i < MAXL - 1; i++) { if (i >= nA - 1 || p.y <= linesA[i]) break; iA += 1.; }
  for (int i = 0; i < MAXL - 1; i++) { if (i >= nB - 1 || p.y <= linesB[i]) break; iB += 1.; }
  vec3 c = vec3(p * 0.05, time * 0.8);
  vec2 warp = vec2(fbm(c), fbm(c + vec3(17.3, -9.1, 4.7)));
  float boil = snoise(vec3(p * 0.35, time * 5.));

  // outgoing
  float to = clamp((elapsed - iA * stagger * 0.6) / (dur * 0.5), 0., 1.);
  float eo = thinkEase(to);
  float nO = amp * 1.2 * eo;
  float bo = blurMax * eo;
  float dO = fA(p + warp * nO) + boil * 0.25 * nO;
  float wO = aa + bo * 1.6;
  float aO = (1. - smoothstep(-wO, wO, dO + bo * 0.9)) * (1. - smoothstep(.3, 1., to));
  aO = mix(aO, gA(p), 1. - smoothstep(0., .12, to));

  // incoming
  float ti = clamp((elapsed - inDelay - iB * stagger) / dur, 0., 1.);
  float ei = thinkEase(ti);
  float nI = amp * 1.4 * (1. - ei);
  float bi = blurMax * (1. - ei);
  float dI = fB(p + warp * nI) + boil * 0.25 * nI;
  float wI = aa + bi * 1.6;
  float aI = (1. - smoothstep(-wI, wI, dI + bi * 0.9)) * smoothstep(0., .35, ti);
  aI *= 1. - grain * (1. - ei) * hash12(floor(p * 2.) + floor(time * 24.) * 7.31);
  aI = mix(aI, gB(p), smoothstep(.86, 1., ti));

  float a = aO + aI - aO * aI;
  gl_FragColor = vec4(uInk, a);
}`;

// The wordmark: a permanent live field and the visible resonance meter.
// life (0 to 1) layers five stages, each fading in as life*5 goes k-1 to k:
// 1 edge boil, 2 ink halftone in the strokes, 3 iso-line ripples on the bar
// clock, 4 letters melting at the joins with dots flowing along the strokes,
// 5 fully alive; secrets found leave yellow traces and an Arabic ghost.
// Cost: the stages arrive as uniforms (st = stages 1 to 4, st5) worked out once
// on the CPU, so each stage branch is uniform and free until life reaches it.
// Pixels further than 'reach' CSS px from every glyph (js/gl.js works out the
// most the warps, noise and ripples can move an edge) stop after one read.
export const WORD_FRAG = /* glsl */`
${COMMON}
uniform sampler2D sdf, sdfE, sdfO, sdfB; uniform vec4 box;
uniform float mixB;  // the hold secret: salehdigital -> أحمد صالح
uniform float time, breath, thinking, aa, grain, ink, reach;
uniform vec3 uInk, uSwell; // the theme's ink, and the colour it leans to at the peak of a thinking swell
uniform vec3 uFoot; // the footer's colour: the wordmark, bio and marks (the accent in Marathon)
uniform vec2 mouse; uniform float mouseOn, mouseR;
uniform vec4 st; uniform float st5;
uniform float bar, beat, cap, ghost, ripples, flowT;
uniform float kBoil, kCursor, kPitch, kDrift, kSpacing, kRipple, kReach, kMeld;
uniform vec4 traces[4];
uniform vec3 cYellow, cRim;
// the footer above the word (the bio and the four marks), baked into a second
// field and drawn in this same pass, with every stage attenuated by kF / kM
uniform sampler2D sdfF; uniform vec4 boxF, frame; uniform float hasF, kF, kM, aaF;
const vec3 BIO_INK = vec3(1.4, 3., .6); // bio ink edge: pitch /px, amplitude and bleed (x ink)
// the footer takes the word's cursor response, scaled to 18px (the basmala; bio and marks scale
// it in the shader): warp px, melt pitch /px, melt px, and the reach as a share of the word's (mouseR)
const vec4 FOOT_HOVER = vec4(1.2, .14, 1., .42);
// the footer's dot matrix (was js/footdots.js, which stays the DOM fallback): a 4.8px grid
// in each strip whose dots swell inside a few drifting blobs (CPU-placed) and one under the cursor
const float DOT_PITCH = 4.8, DOT_RMAX = 1.7, DOT_RMIN = .45;
const vec3 DOT_INK = vec3(1.4, 2.6, .6);       // rest: edge-noise pitch /px, amplitude and bleed (x ink), as BIO_INK but gentler
const vec4 DOT_HOVER = vec4(.8, .3, .8, .42);  // hover: warp px, melt pitch /px, melt px, reach (x mouseR)
uniform vec4 dotR[2];  // the two strips, document px (z = 0: none)
uniform vec4 dotB[16]; // blobs: xy centre, z radius, w strip (-1: unused)
float sminQ(float a, float b, float k){ float h = max(k - abs(a - b), 0.) / k; return min(a, b) - h * h * k * .25; }
uniform vec4 basF; // the basmala's box, document px (w = 0: none)
uniform vec4 marks[4]; uniform vec4 markSoft; // marks: xy centre, z half-size, w hover focus 0..1
varying vec2 vUv;
float smin(float a, float b, float k){ float h = clamp(.5 + .5 * (b - a) / k, 0., 1.); return mix(b, a, h) - k * h * (1. - h); }
void main(){
  vec2 p = frame.xy + vec2(vUv.x, 1. - vUv.y) * frame.zw;
  float s1 = st.x, s2 = st.y, s3 = st.z, s4 = st.w, s5 = st5;

  // ---- the footer: as crisp as the DOM at life 0; the stages at 25 to 35% ----
  float aF = 0., nearF = 1e3, gF = .5; // gF: the footer's grain (the bio takes the word's full grain)
  if (hasF > .5) {
    float df0 = texture2D(sdfF, (p - boxF.xy) / boxF.zw).r;
    nearF = df0;
    if (df0 < 12.) {
      float inM = 0., soft = 0., bump = 0.;
      for (int i = 0; i < 4; i++) {
        vec4 m = marks[i];
        vec2 dd = abs(p - m.xy);
        if (m.z > 0. && dd.x < m.z && dd.y < m.z) {
          inM = 1.;
          soft = markSoft[i] * .5 + .28 * (1. - m.w); // rest a hair soft, hover sharp
          bump = 4. * m.w * (1. - m.w);             // the hover's little noise, mid-flight
        }
      }
      float k = mix(kF, kM, inM);
      vec3 cf = vec3(p * 0.02, time * 0.08);
      vec2 wf = vec2(snoise(cf), snoise(cf + vec3(5.2, 1.3, 8.1)));
      // warp capped at 0.4px: the faintest breathing at life 0, a little more alive later
      float brf = min(mix(.4, 1.6, inM), breath * (.1 + k * (s1 * .6 + s5 * .4)) + thinking * mix(.3, 1., inM) * k); // marks breathe like the word
      vec2 qf = p + wf * brf;
      // the wordmark's hover on all of it (bio, basmala, marks): under the cursor the outline warps,
      // then melts and bleeds, with the word's easing (mouseOn) and level boost (kCursor), sized per
      // region: 16px bio .6 (its counters are about 2px, so less melt keeps it legible), 18px basmala 1, 20px marks .7 (their fine counters, like the bio's)
      float fB = 0.;
      if (mouseOn > .001) {
        vec2 dm = p - mouse; float rB = mouseR * FOOT_HOVER.w;
        float inB = (basF.z > 0. && all(greaterThan(p, basF.xy - 8.)) && all(lessThan(p, basF.xy + basF.zw + 8.))) ? 1. : 0.;
        float sc = inM > .5 ? .7 : mix(.6, 1., inB);
        fB = exp(-dot(dm, dm) / (rB * rB * (1. + s1 * .5))) * mouseOn * (1. + (kCursor - 1.) * s1) * sc;
        qf += wf.yx * fB * FOOT_HOVER.x;
      }
      float df = texture2D(sdfF, (qf - boxF.xy) / boxF.zw).r;
      if (fB > .002) df += fB * (snoise(vec3(p * FOOT_HOVER.y, time * .7)) * FOOT_HOVER.z - FOOT_HOVER.z * .46);
      df += bump * .45 * snoise(vec3(p * .6, time * 4.));
      // the bio, basmala and marks wear the word's ink: its static edge noise, a hair of bleed and
      // its grain, at a finer pitch for 16 to 20px shapes (the word's .42/px is cut for a 100px cap)
      df += snoise(vec3(p * BIO_INK.x, 3.7)) * ink * BIO_INK.y - ink * BIO_INK.z; gF = 1.6;
      if (s1 > 0.) df += k * s1 * kBoil * mix(.5, 1., inM) * snoise(vec3(p * .35, time * 1.3)); // 1: a quieter boil (full on the marks)
      float w = aaF + soft;
      float solidF = 1. - smoothstep(-w, w, df + soft * .3);
      // 2: dots only in a thin band at the edge, so 16px letterforms never break
      if (s2 > 0.) {
        float band = mix(1. - smoothstep(.12, .55, -df), 1. - smoothstep(.4, 2.2, -df), inM); // marks: halftone reaches inside, like the word
        float cdF = length(fract((p + warp2(cf) * kDrift * s2) / 1.2) - .5) * 1.2;
        float dotsF = 1. - smoothstep(.4 - aaF, .4 + aaF, cdF);
        solidF *= 1. - s2 * k * 1.6 * band * (1. - dotsF);
      }
      aF = solidF;
      // 3: its own faint, short ripples
      if (s3 > 0. && ripples > 0. && df > 0.) {
        float dist = abs(fract(df / 5. - bar + .5) - .5) * 5.;
        aF = max(aF, (1. - smoothstep(.2, .2 + aaF * 1.6, dist)) * exp(-df / 7.) * kRipple * k * s3 * ripples);
      }
    }
  }

  // the dot matrix: the nearest grid dot's radius, read off the blob field at its centre
  float aD = 0.;
  for (int sI = 0; sI < 2; sI++) {
    vec4 R = dotR[sI];
    if (R.z <= 0. || p.x < R.x || p.y < R.y || p.x > R.x + R.z || p.y > R.y + R.w) continue;
    vec2 n = floor(R.zw / DOT_PITCH + 1e-3);
    vec2 o = R.xy + (R.zw - (n - 1.) * DOT_PITCH) * .5;
    vec2 c = o + clamp(floor((p - o) / DOT_PITCH + .5), vec2(0.), n - 1.) * DOT_PITCH;
    float d = 1e5;
    for (int i = 0; i < 16; i++) {
      vec4 b = dotB[i];
      if (b.w != float(sI)) continue;
      vec2 q = c - b.xy;
      d = sminQ(d, length(vec2(q.x * .55, q.y)) - b.z, 10.);
    }
    vec2 mq = mouse - R.xy;
    if (mq.x > -40. && mq.x < R.z + 40. && mq.y > -40. && mq.y < R.w + 40.) d = sminQ(d, length(c - mouse) - 7., 14.);
    float k = 1. - clamp((d + 2.) / 8., 0., 1.);
    float r = DOT_RMIN + (DOT_RMAX - DOT_RMIN) * k * k * (3. - 2. * k);
    // the wordmark's ink on each dot, scaled by its size so the small ones keep the halftone:
    // edge noise and a hair of bleed at rest; under the cursor its warp and melt (the word's easing and level boost)
    float sz = r / DOT_RMAX, fD = 0.;
    vec2 qd = p;
    if (mouseOn > .001) {
      vec2 dm = p - mouse; float rD = mouseR * DOT_HOVER.w;
      fD = exp(-dot(dm, dm) / (rD * rD * (1. + s1 * .5))) * mouseOn * (1. + (kCursor - 1.) * s1);
      qd += vec2(snoise(vec3(p * .05, time * .3)), snoise(vec3(p * .05 + 7.1, time * .3))) * fD * DOT_HOVER.x;
    }
    float dd = length(qd - c) - r;
    dd += (snoise(vec3(p * DOT_INK.x, 3.7)) * DOT_INK.y - DOT_INK.z) * ink * (.4 + .6 * sz);
    if (fD > .002) dd += fD * (snoise(vec3(p * DOT_HOVER.y, time * .7)) - .46) * DOT_HOVER.z * (.5 + .5 * sz);
    aD = (1. - smoothstep(-aaF, aaF, dd)) * (1. - grain * 1.6 * hash12(floor(p * 2.) + floor(time * 15.) * 3.17)); // the bio's grain
  }

  // early out: no edge, ripple or ghost of the word can reach this pixel
  vec2 uv0 = (p - box.xy) / box.zw;
  float d0 = (uv0.x < 0. || uv0.y < 0. || uv0.x > 1. || uv0.y > 1.) ? 1e3 : texture2D(sdf, uv0).r;
  if (ghost > 0. || mixB > 0.) d0 = min(d0, texture2D(sdfB, uv0).r);
  if (d0 > reach) {
    if (aF <= 0. && aD <= 0.) discard;
    gl_FragColor = vec4(uFoot, max(aD, aF * (1. - grain * gF * hash12(floor(p * 2.) + floor(time * 15.) * 3.17))));
    return;
  }
  vec3 c = vec3(p * 0.0045, time * 0.06);
  vec2 warp = vec2(fbm2(c), fbm2(c + vec3(19.1, 3.3, -7.7)));
  float br = breath * (1. + thinking * 2.5) * (1. + s1 * .6 + s5 * .4);
  vec2 q = p + warp * br;
  float cg = 1. + (kCursor - 1.) * s1;
  float fall = 0.;
  if (mouseOn > 0.001) {
    vec2 dm = p - mouse;
    fall = exp(-dot(dm, dm) / (mouseR * mouseR * (1. + s1 * .5))) * mouseOn;
    q += warp.yx * fall * 3. * cg;
  }
  vec2 uv = (q - box.xy) / box.zw;
  float d = texture2D(sdf, uv).r;
  // 4: adjacent letters melt into each other at the joins
  if (s4 > 0.) {
    float k = cap * kMeld * .1 * s4 * (.75 + .25 * sin(time * .6));
    d = mix(d, smin(texture2D(sdfE, uv).r, texture2D(sdfO, uv).r, max(k, .001)), s4);
  }
  if (mixB > 0.) {
    float env = sin(PI * mixB);
    vec2 ub = (q + warp * env * 10. - box.xy) / box.zw;
    d = mix(texture2D(sdf, ub).r, texture2D(sdfB, ub).r, mixB);
    d += snoise(vec3(p * 0.06, time * 2.)) * env * 3.;
  }
  if (fall > .002) d += fall * (snoise(vec3(p * 0.035, time * 0.7)) * 2.4 - 1.1) * cg;
  if (thinking > .01) d += thinking * snoise(vec3(p * 0.05, time * 1.6)) * 1.6;
  d += snoise(vec3(p * 0.42, 3.7)) * ink;                       // static ink edge
  d += breath * 0.35 * snoise(vec3(p * 0.012, time * 0.11));    // edge breathing
  if (s1 > 0.) d += s1 * kBoil * snoise(vec3(p * 0.22, time * 1.3)); // 1: the edge boils
  float solid = 1. - smoothstep(-aa, aa, d);
  float a = solid, cd = 0.;

  // 2: an ink halftone inside the strokes; dots grow with depth, so the
  // letters read as points near their edges. 4: the grid flows along the strokes.
  if (s2 > 0. || ghost > 0. || traces[0].w > 0.) {
    vec2 tang = vec2(0.);
    if (s4 > 0.) {
      vec2 e = vec2(1.5, 0.) / box.zw;
      vec2 g = vec2(texture2D(sdf, uv + e.xy).r - texture2D(sdf, uv - e.xy).r, texture2D(sdf, uv + e.yx).r - texture2D(sdf, uv - e.yx).r);
      tang = normalize(vec2(-g.y, g.x) + 1e-5);
    }
    vec2 gp = p + warp * kDrift * 4. * s2 - tang * flowT * s4;
    cd = length(fract(gp / kPitch) - .5) * kPitch;
    float depth = clamp(-d / max(cap * .055, .5), 0., 1.);
    float dotR = kPitch * (.2 + .42 * depth);
    float dots = (1. - smoothstep(dotR - aa, dotR + aa, cd)) * solid;
    a = mix(solid, dots, s2 * .92);
  }

  // the Arabic ghost left by the hold secret, in the halftone
  if (ghost > 0.) {
    float da = texture2D(sdfB, uv).r;
    float gd = 1. - smoothstep(kPitch * .2 - aa, kPitch * .2 + aa, cd);
    a = max(a, gd * (1. - smoothstep(-aa, aa, da)) * ghost);
  }

  // 3: iso-lines ripple outward like heat or sonar, pulsing on the bar clock
  if (s3 > 0. && ripples > 0. && d > 0.) {
    float dist = abs(fract(d / kSpacing - bar + .5) - .5) * kSpacing;
    float line = 1. - smoothstep(.22, .22 + aa * 1.6, dist);
    float pulse = .55 + .45 * pow(1. - beat, 3.);
    a = max(a, line * exp(-d / kReach) * pulse * kRipple * s3 * ripples * smoothstep(1., 7., nearF)); // they pass around the footer
  }

  a = max(a, aF * (1. - grain * max(0., gF - 1.) * hash12(floor(p * 2.) + floor(time * 15.) * 3.17))); // the bio's extra grain; the word's comes next
  float anyTrace = traces[0].w + traces[1].w + traces[2].w + traces[3].w;
  if (a <= 0. && aD <= 0. && (anyTrace <= 0. || solid <= 0.)) discard;
  a *= 1. - grain * hash12(floor(p * 2.) + floor(time * 15.) * 3.17);
  a = max(a, aD); // the dots carry their own grain

  // 5: traces of found secrets, a yellow dot cluster lodged in a letter
  vec3 col = mix(uFoot, uSwell, smoothstep(.15, 1.2, thinking) * .85);
  for (int i = 0; i < 4; i++) {
    vec4 tr = traces[i];
    if (tr.w <= 0.) continue;
    float m = (1. - smoothstep(tr.z * .55, tr.z, length(p - tr.xy))) * tr.w * solid;
    float yd = 1. - smoothstep(kPitch * .34 - aa, kPitch * .34 + aa, cd);
    col = mix(col, mix(cRim, cYellow, yd), m);
    a = max(a, m * .95);
  }
  gl_FragColor = vec4(col, a);
}`;

// (The paper grain is no longer a shader: see js/grain.js.)

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
