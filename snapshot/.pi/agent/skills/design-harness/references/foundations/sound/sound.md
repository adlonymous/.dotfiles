---
title: Sound
slug: sound
status: published
description: "Fully synthesised Web Audio: a quiet section-chord bed, droplet hovers, wordmark notes, five press/drag/release palettes, haptics. No audio files."
chips:
  - Foundation
  - Sound
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:00:12Z
---

All sound on saleh.digital is synthesised live with the Web Audio API in `js/audio.js`. There are **no audio files**: no samples, no recordings, nothing to download. Nothing plays before a user gesture. Everything stays very quiet, because this is still a UI.

The aesthetic note in the source: "the Jai Paul pass ("Jasmine", "BTSTU")". Warm, detuned, slightly out-of-tune chords go through a resonant lowpass and chorus, with tape wow and flutter, crushed grit on transients, pumping ducks, a felt sub, and a formant "ahh" for emergences.

## Settings and defaults

| Key (localStorage) | Values | Default | What it does |
|---|---|---|---|
| `sd:sound` | `on` / `off` | on (anything but `off`) | The master switch. `audio.toggle()` flips it and ramps master gain to 1 or 0 with a 0.08s time constant. Turning it on plays one pluck on the top note of the section chord + 12. |
| `sd:bed` | `on` / `off` | on | The quiet background pad and air (`audio.setBed`). Settings has no control for it now; it follows the stored value. |
| `sd:feel` | `felt-hushed`, `felt`, `unison`, `low-tide`, `mist`, `off` | `felt-hushed` | The interaction palette used for press, drag and release. |

- **Where the visitor changes it:** Settings › Sound ([Settings](../../templates/settings.md)). Picking a palette sets `sd:feel`, turns sound on if it was off, and plays that palette's preview. Picking **Off** sets the feel to `off`. There is no separate Sound switch in Settings any more (Ahmed, Nov 9).
- **The actions row** under a post has a sound icon button (`#sound`, `aria-pressed`) that calls `audio.toggle()`. On the live site that button is `hidden` (like Copy link, Copy text and Discuss), so the only control is Settings › Sound.
- **Unlock:** the first `pointerdown`, `keydown` or `touchstart` anywhere creates the `AudioContext`, builds the graph and starts the bed.
- **Suspend:** when muted, the context suspends about 400ms after the fade. It also suspends while the tab is hidden (`visibilitychange`) and resumes when the tab is visible and sound is on.
- **Reduced motion:** the pitch modulation (wow, flutter, drift) is set to 0. The sounds still play.
- **Haptics** ride on the same switch: see the Haptics section below.

## The signal chain

- `master` gain → `DynamicsCompressor` (threshold -24 dB, ratio 3, attack 0.008s, release 0.25s) → destination.
- **Reverb:** a `ConvolverNode` with a generated noise impulse 5.5s long (`AMB.roomSec`) and wet 0.5 (`AMB.wet`). `SOUND.levels.wet` is .22.
- **Chorus:** two modulated delays of .012 and .017s, depth .003, LFO rates .31 and .53 Hz, mix .5.
- **Pitch modulation** on every oscillator: tape wow at .45 Hz ±7 cents, flutter at 5.8 Hz ±1.6 cents, plus slow drift of ±9 cents. Voices are detuned by ±12 cents.
- **Crush** on transients: 5 bits with a downsample of 6. It is an AudioWorklet `sd-crush`, with a `WaveShaper` fallback.
- **Pump:** sidechain-style ducking of the bed, depth .35, release 340ms, beat 420ms.
- Stabs are filtered from 220 to 1500 Hz, blooms from 250 to 2200 Hz.

## Harmony: one chord per section

Root D3 = 146.83 Hz. `SOUND.hz(semitones)` = 146.83 × 2^(n/12). A route change (`resolve:start` with a `section`) sets the section and the chord inversion (item index), then glides the pad to the new chord over `AMB.glideSec` = 4s. The page change itself makes **no** click or stab.

| Section slug | Intervals (semitones from D3) | Chord |
|---|---|---|
| articles | 0, 3, 7, 10, 14 | D minor 9 |
| components | 3, 7, 10, 14 | F major 7 |
| harnesses | 5, 8, 12, 15, 19 | G minor 9 |
| philosophy | -4, 0, 3, 7 | B-flat major 7 |
| library | 7, 10, 14, 17 | A minor 7 |
| friends | -2, 2, 5, 12 | C add 9 |
| experiments | 2, 5, 8, 12 | E minor 7 flat 5 |

A slug that is not in this table (the current rooms use slugs such as `lectures` and `speaking`) falls back to the articles chord (`SOUND.voicing`).

## The bed (ambient)

- **Air:** looped white noise → lowpass at 420 Hz, whose frequency an LFO at .045 Hz moves by ±160 Hz. Level `AMB.air` .0022.
- **Pad:** 4 voices on the chord tones. Each is a sine at .7 plus a triangle at .18, with its own LFO at 1/(11 + 6i) Hz. They go through a lowpass at `AMB.padLp` 680 Hz. Level `AMB.pad` .0055.
- **Warmth** follows the resonance tier (0 to 5): gain × (1 + .22 × tier), lowpass 680 + 70 × tier Hz.

## Every sound event

| Event (bus) | Trigger | Sound | Level |
|---|---|---|---|
| `hover` | pointer enters a nav or sub-nav item, an icon button, an MCP app mark, a footer mark, or a warm word after its 700ms hover; on touch, a pointerdown on an item | a "droplet": a soft sine at a chord note + 24 semitones with a short decay | `SOFT` .0032 |
| `emerge` | the emergence engine reveals new content (off while `EMERGENCE = false`) | a 4-note rising arpeggio of the chord at +24, notes .11s apart, plus an air shimmer swept from 3000 to 7000 Hz | `SOFT.emerge` .0032, `SOFT.shimmer` .0012 |
| `wordmark:letter` | the pointer crosses a new letter of the footer wordmark | D minor pentatonic [0, 3, 5, 7, 10] mapped across the 12 letters; at least 38ms between notes | .011 × velocity (pointer speed) |
| press | `pointerdown` on anything matching `PRESSABLE` (not inside `[data-feel-skip]`) | the palette's `press` notes | palette gain × AMB.feel |
| drag | after 8px of travel inside `DRAGGABLE`, one step per 48px of travel and at least 90ms apart; a phone shelf (`.sp-row`) scroll counts too | the palette's `drag.steps`, cycling | palette |
| release | letting go after a drag, or after a press held 450ms or more | the palette's `release` notes | palette |
| `sound:toggle` → on | the sound switch turns on | one pluck on the chord's top note + 12 | `levels.pluck` .03 × .8 |
| `resolve:start` | route change | no sound; the pad glides to the section chord | none |
| `copy` | copy link, copy text or MCP copy | silent | none |
| `resonance` | the tier changes | warmth of the bed | none |

`PRESSABLE` = `a[href], button, [role="button"], [role="radio"], [role="switch"], [role="tab"], .item, .masonry-cell, .record.has-media, .warm, .wordmark`

`DRAGGABLE` = `.viewer-stage, .col-gallery, .sp-row, .wordmark`

`FEEL_DRAG` = `{ startPx: 8, stepPx: 48, minMs: 90, longMs: 450 }`

## The interaction palettes (`PALETTES`)

Each note is `[Hz, ms, gain, delayMs?]`. Gains are scaled by `AMB.feel = .0032 / .35`. `audio.preview(id)` plays press at 0, drag steps at 260, 380 and 500ms, and release at 760ms.

| id | Label | press | drag (ms, steps) | release |
|---|---|---|---|---|
| felt | Felt | [146.83, 260, .35], [220, 320, .12, 10] | 420; 293.66 / 329.63 / 349.23 at .08 | [220, 600, .14], [146.83, 900, .10, 80] |
| felt-hushed (default) | Felt, hushed | [146.83, 600, .16], [220, 800, .05] | 420; 293.66 / 311.13 at .04 | [220, 1200, .07], [146.83, 1600, .05] |
| unison | Unison | [146.83, 900, .1], [220, 900, .07] | 1400; [146.83, .05] + [220, .04] | [110, 1800, .1], [146.83, 1800, .07] |
| low-tide | Low tide | [73.42, 500, .3], [110, 500, .08] | 1200; [87.31, .12] + [98, .08] | [110, 900, .12], [73.42, 1600, .14] |
| mist | Mist | [1174.66, 700, .03], [1244.51, 700, .02] | 700; [1760, .015] + [1864.66, .012] | [1174.66, 1500, .025], [880, 1800, .02] |

## Haptics (`js/haptics.js`)

`navigator.vibrate`, only while `audio.enabled` and only where the API exists (phones).

| Event | Pattern (ms) |
|---|---|
| hover (touch/press source only) | [6] |
| resolve (kind `state`) | [8, 30, 12] |
| copy | [10, 40, 10] |
| toggle | [6] |
| emerge | [12, 40, 8, 40, 20] |
| wordmark:letter | [9] on the first and last letter, [4] otherwise |

Source: `site/js/haptics.js`, whole file

```js
// Touch answers that follow the sounds. Respects the sound toggle.
import { bus } from './state.js';
import { HAPTICS } from './tokens.js';
import { audio } from './audio.js';

const can = typeof navigator !== 'undefined' && 'vibrate' in navigator;
function buzz(p) { if (can && audio.enabled) { try { navigator.vibrate(p); } catch (e) {} } }

bus.on('hover', (d) => { if (d.source === 'touch' || d.source === 'press') buzz(HAPTICS.hover); });
bus.on('resolve:start', (d) => { if (d.kind === 'state') buzz(HAPTICS.resolve); });
bus.on('copy', () => buzz(HAPTICS.copy));
bus.on('emerge', () => buzz(HAPTICS.emerge));
bus.on('sound:toggle', () => buzz(HAPTICS.toggle));
bus.on('wordmark:letter', (d) => buzz(d.index === 0 || d.index === d.total - 1 ? [9] : [4])); // a tick per letter, firmer at the ends
```


## Tokens (`SOUND` in `js/tokens.js`)

Source: `site/js/tokens.js`, lines 139 to 166

```js
export const SOUND = {
  root: 146.83,                          // D3
  chords: {                              // semitones from D3
    articles: [0, 3, 7, 10, 14],         // i    Dm9
    components: [3, 7, 10, 14],          // III  Fmaj7
    harnesses: [5, 8, 12, 15, 19],       // iv   Gm9
    philosophy: [-4, 0, 3, 7],           // VI   Bbmaj7
    library: [7, 10, 14, 17],            // v    Am7
    friends: [-2, 2, 5, 12],             // VII  Cadd9
    experiments: [2, 5, 8, 12]           // ii   Em7b5
  },
  detuneCents: 12,        // fixed per-note mistuning, random within +-
  driftCents: 9,          // random walk on top (tape drift)
  wow: { rate: 0.45, cents: 7 }, flutter: { rate: 5.8, cents: 1.6 },
  chorus: { delays: [0.012, 0.017], depth: 0.003, rates: [0.31, 0.53], mix: 0.5 },
  crush: { bits: 5, down: 6 },
  formantAh: [[800, 1, 11], [1150, 0.5, 12], [2900, 0.22, 14]], // Hz, gain, Q
  levels: { stab: 0.045, sub: 0.03, tick: 0.012, emerge: 0.06, vox: 0.035, pluck: 0.03,
            bedNoise: 0.003, bedDrone: 0.0035, warmthPerTier: 0.22, wet: 0.22 },
  pump: { depth: 0.35, releaseMs: 340, beatMs: 420 },
  stabFilter: [220, 1500], bloomFilter: [250, 2200],
  hz(semi) { return this.root * Math.pow(2, semi / 12); },
  voicing(section, inversion = 0) {
    const c = [...(this.chords[section] || this.chords.articles)];
    for (let k = 0; k < inversion % c.length; k++) c.push(c.shift() + 12);
    return c;
  }
};
```


## The whole engine

This is the complete source, so the synthesis can be rebuilt exactly.

Source: `site/js/audio.js`, whole file

```js
// Generative sound, the Jai Paul pass ("Jasmine", "BTSTU"): warm, detuned,
// slightly out-of-tune chords through a resonant lowpass and chorus, tape wow
// and flutter, crushed grit on transients, pumping ducks, a felt sub, and a
// formant "ahh" for emergences. Still a UI: everything stays quiet.
// Everything is synthesised; nothing plays before a gesture.
import { bus, reducedMotion, barMs } from './state.js';
import { SOUND, think } from './tokens.js';

const KEY = 'sd:sound';
let stored = null;
try { stored = localStorage.getItem(KEY); } catch (e) {}

let padVoices = null;
const AMB = { roomSec: 5.5, wet: 0.5, padLp: 680, pad: 0.0055, air: 0.0022, glideSec: 4, drop: 0.0032 };
let ctx = null, master, wet, chorusIn, crushIn, pitchMod, pump, bedNoiseGain, droneGain, droneLp, noiseBuf;
let section = 'articles', inversion = 0, tier = 0;
// the visitor's choices (Settings): the background pad, and the interaction palette
const BED_KEY = 'sd:bed', FEEL_KEY = 'sd:feel';
const readKey = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };
const writeKey = (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} };

export const audio = {
  enabled: stored !== 'off',   // default on once unlocked
  unlocked: false,
  bed: readKey(BED_KEY) !== 'off',
  feel: null,                  // the interaction palette id (set below, once PALETTES exists)
  setBed(on) {
    this.bed = !!on; writeKey(BED_KEY, on ? 'on' : 'off');
    warmth(tier, 0.6);
    bus.emit('sound:bed', { on: this.bed });
  },
  setFeel(id) {
    if (!FEEL_IDS.includes(id)) return;
    this.feel = id; writeKey(FEEL_KEY, id);
    bus.emit('sound:feel', { id });
  },
  toggle() {
    this.enabled = !this.enabled;
    try { localStorage.setItem(KEY, this.enabled ? 'on' : 'off'); } catch (e) {}
    if (ctx) {
      sync(); // resumes the context when sound comes back on
      const now = ctx.currentTime;
      master.gain.cancelScheduledValues(now);
      master.gain.setTargetAtTime(this.enabled ? 1 : 0, now, 0.08);
      if (this.enabled) pluck(SOUND.hz(SOUND.voicing(section).slice(-1)[0] + 12), now + 0.03, SOUND.levels.pluck * 0.8);
    }
    bus.emit('sound:toggle', { enabled: this.enabled });
    return this.enabled;
  }
};

function unlock() {
  if (ctx) return;
  const AC = window.AudioContext || window.webkitAudioContext;
  if (!AC) return;
  ctx = new AC();
  build();
  sync();
  audio.unlocked = true;
  ['pointerdown', 'keydown', 'touchstart'].forEach(t => window.removeEventListener(t, unlock, true));
  bus.emit('audio:unlocked', {});
}
['pointerdown', 'keydown', 'touchstart'].forEach(t => window.addEventListener(t, unlock, true));

const rand = (a, b) => a + Math.random() * (b - a);

// ---------- running only when heard ----------
// The context runs (and its two timers tick) only while sound is on and the tab
// is visible; otherwise it is suspended: no drone, no reverb, no worklet, no timers.
let timers = [], startTimers = () => {};
function stopTimers() { timers.forEach(clearInterval); timers = []; }
let suspendT = 0;
function sync() {
  if (!ctx) return;
  clearTimeout(suspendT);
  if (audio.enabled && !document.hidden) {
    if (ctx.state !== 'running') ctx.resume().catch(() => {});
    if (!timers.length) startTimers();
  } else {
    stopTimers();
    // muted: let the 80ms fade finish first; hidden: at once
    suspendT = setTimeout(() => {
      if (!(audio.enabled && !document.hidden) && ctx.state === 'running') ctx.suspend().catch(() => {});
    }, document.hidden ? 0 : 400);
  }
}
// a voice is only scheduled while the context is actually running
const live = () => ctx && audio.enabled && ctx.state === 'running' && !document.hidden;

// Every per-event oscillator takes the tape wobble (pitchMod) on its detune. That
// connection keeps the oscillator alive forever unless it is undone: undo it,
// and let go of the chain behind it, when the oscillator ends.
function wobble(o, ...chain) {
  pitchMod.connect(o.detune);
  o.onended = () => {
    try { pitchMod.disconnect(o.detune); } catch (e) {}
    try { o.disconnect(); } catch (e) {}
    chain.forEach(n => { try { n.disconnect(); } catch (e) {} });
  };
}
function releaseOnEnd(src, ...chain) {
  src.onended = () => { [src, ...chain].forEach(n => { try { n.disconnect(); } catch (e) {} }); };
}
function curve(n, fn) { const a = new Float32Array(n); for (let i = 0; i < n; i++) a[i] = fn(i / (n - 1)); return a; }

function build() {
  const L = SOUND.levels;
  master = ctx.createGain(); master.gain.value = audio.enabled ? 1 : 0;
  const comp = ctx.createDynamicsCompressor();
  comp.threshold.value = -24; comp.ratio.value = 3; comp.attack.value = 0.008; comp.release.value = 0.25;
  master.connect(comp).connect(ctx.destination);

  // a long, soft generated room: the ambient space everything sits in
  const len = Math.floor(ctx.sampleRate * AMB.roomSec);
  const ir = ctx.createBuffer(2, len, ctx.sampleRate);
  for (let c = 0; c < 2; c++) {
    const d = ir.getChannelData(c); let lp = 0;
    for (let i = 0; i < len; i++) { const k = i / len; lp += (Math.random() * 2 - 1 - lp) * (0.45 - 0.4 * k); d[i] = lp * Math.pow(1 - k, 1.8); }
  }
  const verb = ctx.createConvolver(); verb.buffer = ir;
  wet = ctx.createGain(); wet.gain.value = AMB.wet;
  wet.connect(verb).connect(master);

  // chorus: two short delays, slowly modulated, beside the dry signal
  chorusIn = ctx.createGain();
  chorusIn.connect(master); chorusIn.connect(wet);
  SOUND.chorus.delays.forEach((t, i) => {
    const dl = ctx.createDelay(0.05); dl.delayTime.value = t;
    const lfo = ctx.createOscillator(); lfo.frequency.value = SOUND.chorus.rates[i];
    const amt = ctx.createGain(); amt.gain.value = SOUND.chorus.depth;
    lfo.connect(amt).connect(dl.delayTime); lfo.start();
    const g = ctx.createGain(); g.gain.value = SOUND.chorus.mix;
    chorusIn.connect(dl).connect(g).connect(master);
  });

  // tape: wow + flutter + a random-walk drift, summed into every oscillator's detune
  pitchMod = ctx.createGain(); pitchMod.gain.value = reducedMotion.matches ? 0 : 1;
  [[SOUND.wow.rate, SOUND.wow.cents], [SOUND.flutter.rate, SOUND.flutter.cents]].forEach(([r, c]) => {
    const o = ctx.createOscillator(); o.frequency.value = r;
    const g = ctx.createGain(); g.gain.value = c; o.connect(g).connect(pitchMod); o.start();
  });
  const drift = ctx.createConstantSource(); drift.offset.value = 0; drift.connect(pitchMod); drift.start();
  reducedMotion.addEventListener?.('change', () => { pitchMod.gain.value = reducedMotion.matches ? 0 : 1; });

  // grit: a bit-crusher with sample-rate reduction for transients
  crushIn = ctx.createGain();
  const fallback = () => {
    const ws = ctx.createWaveShaper(); const q = Math.pow(2, SOUND.crush.bits);
    ws.curve = curve(1024, x => Math.round((x * 2 - 1) * q) / q);
    crushIn.connect(ws).connect(master);
  };
  if (ctx.audioWorklet) {
    const code = `class Crush extends AudioWorkletProcessor{constructor(){super();this.h=[0,0];this.n=0}
      process(i,o){const a=i[0],b=o[0];if(!a||!a.length)return true;const q=Math.pow(2,${SOUND.crush.bits}),dn=${SOUND.crush.down};
      for(let c=0;c<b.length;c++){const x=a[c]||a[0],y=b[c];for(let k=0;k<y.length;k++){if((this.n+k)%dn===0)this.h[c&1]=Math.round(x[k]*q)/q;y[k]=this.h[c&1]}}
      this.n+=b[0].length;return true}}registerProcessor('sd-crush',Crush)`;
    const url = URL.createObjectURL(new Blob([code], { type: 'application/javascript' }));
    ctx.audioWorklet.addModule(url).then(() => { crushIn.connect(new AudioWorkletNode(ctx, 'sd-crush')).connect(master); }).catch(fallback);
  } else fallback();

  noiseBuf = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate);
  const nd = noiseBuf.getChannelData(0);
  for (let i = 0; i < nd.length; i++) nd[i] = Math.random() * 2 - 1;

  // the bed: an ambient pad on the section's chord, each voice swelling on its own
  // slow cycle so it never repeats, with a far-off breath of air. No pump, no grit.
  pump = ctx.createGain(); pump.gain.value = 1; pump.connect(master); pump.connect(wet);
  const bn = ctx.createBufferSource(); bn.buffer = noiseBuf; bn.loop = true;
  const blp = ctx.createBiquadFilter(); blp.type = 'lowpass'; blp.frequency.value = 420; blp.Q.value = 0.3;
  const airLfo = ctx.createOscillator(); airLfo.frequency.value = 0.045;
  const airAmt = ctx.createGain(); airAmt.gain.value = 160; airLfo.connect(airAmt).connect(blp.frequency); airLfo.start();
  bedNoiseGain = ctx.createGain(); bedNoiseGain.gain.value = 0;
  bn.connect(blp).connect(bedNoiseGain).connect(pump); bn.start();
  droneLp = ctx.createBiquadFilter(); droneLp.type = 'lowpass'; droneLp.frequency.value = AMB.padLp; droneLp.Q.value = 0.4;
  droneGain = ctx.createGain(); droneGain.gain.value = 0;
  padVoices = padNotes(section).map((semi, i) => {
    const g = ctx.createGain(); g.gain.value = 0.5;
    // each voice breathes on its own slow cycle (11 to 29 seconds)
    const lfo = ctx.createOscillator(); lfo.frequency.value = 1 / (11 + i * 6);
    const depth = ctx.createGain(); depth.gain.value = 0.45; lfo.connect(depth).connect(g.gain); lfo.start(ctx.currentTime + i * 1.7);
    const oscs = [['sine', 0], ['triangle', 4 + i]].map(([type, cents]) => {
      const o = ctx.createOscillator(); o.type = type; o.frequency.value = SOUND.hz(semi); o.detune.value = cents;
      const og = ctx.createGain(); og.gain.value = type === 'sine' ? 0.7 : 0.18;
      o.connect(og).connect(g); o.start();
      return o;
    });
    g.connect(droneLp);
    return oscs;
  });
  droneLp.connect(droneGain).connect(pump);
  warmth(tier, 3);

  // only a slow drift runs in the background, and only while the context does (sync)
  startTimers = () => {
    timers.push(setInterval(() => { if (live()) drift.offset.setTargetAtTime(rand(-1, 1) * SOUND.driftCents * 0.4, ctx.currentTime, 2); }, 2500));
  };
}

// the pad's notes for a section: its chord, low and open, four voices
function padNotes(slug) { return SOUND.voicing(slug || 'articles').slice(0, 4).map((x, i) => x - 12 + (i > 1 ? 12 : 0)); }
// a page change in another section: the harmony drifts there over a few seconds, nothing is struck
function padTo(slug) {
  if (!ctx || !padVoices) return;
  const now = ctx.currentTime;
  padNotes(slug).forEach((semi, i) => padVoices[i]?.forEach(o => o.frequency.setTargetAtTime(SOUND.hz(semi), now, AMB.glideSec / 3)));
}

// the site gets warmer the more has been discovered
function warmth(t, tau = 1.5) {
  if (!ctx || !bedNoiseGain) return;
  const L = SOUND.levels, k = (audio.bed ? 1 : 0) * (1 + L.warmthPerTier * t), now = ctx.currentTime;
  bedNoiseGain.gain.setTargetAtTime(AMB.air * k, now, tau);
  droneGain.gain.setTargetAtTime(AMB.pad * k, now, tau);
  droneLp.frequency.setTargetAtTime(AMB.padLp + 70 * t, now, tau);
}

// sidechain-like pump on the bed
function duck(at, depth = SOUND.pump.depth, release = SOUND.pump.releaseMs / 1000) {
  pump.gain.cancelScheduledValues(at);
  pump.gain.setValueAtTime(pump.gain.value, at);
  pump.gain.linearRampToValueAtTime(depth, at + 0.012);
  pump.gain.setTargetAtTime(1, at + 0.03, release / 3);
}

// one warm, slightly wrong voice: two detuned saws and a square below, resonant lowpass
function voice(f, at, { level, attack, hold, release, lp, q = 7, lpCurve = null, lpDur = 0 }) {
  const out = ctx.createGain(); out.gain.value = 0;
  const filt = ctx.createBiquadFilter(); filt.type = 'lowpass'; filt.Q.value = q;
  if (lpCurve) filt.frequency.setValueCurveAtTime(lpCurve, at, lpDur); else filt.frequency.value = lp;
  const off = rand(-1, 1) * SOUND.detuneCents; // this note is a little out of tune, and stays so
  const end = at + attack + hold + release * 4;
  [['sawtooth', 1, off - 6, 0.5], ['sawtooth', 1, off + 7, 0.5], ['square', 0.5, off, 0.18]].forEach(([type, mul, cents, g], i) => {
    const o = ctx.createOscillator(); o.type = type; o.frequency.value = f * mul; o.detune.value = cents;
    const og = ctx.createGain(); og.gain.value = g;
    wobble(o, og, ...(i === 0 ? [filt, out] : [])); // the first one lets go of the voice's filter and gain too
    o.connect(og).connect(filt); o.start(at); o.stop(end);
  });
  filt.connect(out).connect(chorusIn);
  out.gain.setValueAtTime(0, at);
  out.gain.linearRampToValueAtTime(level, at + attack);
  out.gain.setTargetAtTime(0, at + attack + hold, release);
  return filt;
}

function sub(f, at, level, attack, decay) {
  const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.value = f;
  const g = ctx.createGain(); g.gain.value = 0;
  g.gain.setValueAtTime(0, at); g.gain.linearRampToValueAtTime(level, at + attack); g.gain.setTargetAtTime(0, at + attack, decay / 3);
  releaseOnEnd(o, g);
  o.connect(g).connect(master); o.start(at); o.stop(at + attack + decay * 2);
}

function grit(at, level, ms = 14, freq = 2600) {
  const src = ctx.createBufferSource(); src.buffer = noiseBuf;
  const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = freq; bp.Q.value = 2.5;
  const g = ctx.createGain(); g.gain.setValueAtTime(level, at); g.gain.exponentialRampToValueAtTime(0.0001, at + ms / 1000);
  releaseOnEnd(src, bp, g);
  src.connect(bp).connect(g).connect(crushIn); src.start(at, Math.random()); src.stop(at + ms / 1000 + 0.02);
}

function pluck(f, at, level) {
  const filt = ctx.createBiquadFilter(); filt.type = 'lowpass'; filt.Q.value = 4;
  filt.frequency.setValueAtTime(4200, at); filt.frequency.exponentialRampToValueAtTime(420, at + 0.18);
  const g = ctx.createGain(); g.gain.setValueAtTime(0, at); g.gain.linearRampToValueAtTime(level, at + 0.004); g.gain.setTargetAtTime(0, at + 0.01, 0.14);
  [['sawtooth', -5], ['square', 6]].forEach(([type, c], i) => {
    const o = ctx.createOscillator(); o.type = type; o.frequency.value = f; o.detune.value = c + rand(-1, 1) * SOUND.detuneCents;
    wobble(o, ...(i === 0 ? [filt, g] : []));
    o.connect(filt); o.start(at); o.stop(at + 0.8);
  });
  filt.connect(g).connect(chorusIn);
  grit(at, level * 0.5, 8, 3400);
}

// Page change and emergence are deliberately quiet: felt more than heard.
// No stab, no sub, no grit, no pump: a breath of air and soft sines, mostly in the room.
const SOFT = { page: 0.0045, air: 0.0035, emerge: 0.0032, shimmer: 0.0012 };

// one soft sine that blooms and fades, mostly into the reverb
function softTone(f, at, level, attack, decay, dry = 0.35) {
  const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.value = f; o.detune.value = rand(-4, 4);
  const g = ctx.createGain();
  g.gain.setValueAtTime(0, at); g.gain.linearRampToValueAtTime(level, at + attack); g.gain.setTargetAtTime(0, at + attack, decay / 3);
  const d = ctx.createGain(); d.gain.value = dry;
  releaseOnEnd(o, g, d);
  o.connect(g); g.connect(d).connect(master); g.connect(wet);
  o.start(at); o.stop(at + attack + decay * 2);
}
// a breath of filtered air that opens along the think ease, like a page turning
function air(at, dur, level, lo = 500, hi = 2600) {
  const src = ctx.createBufferSource(); src.buffer = noiseBuf;
  const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.Q.value = 0.9;
  bp.frequency.setValueCurveAtTime(curve(32, x => lo * Math.pow(hi / lo, think(x))), at, dur);
  const g = ctx.createGain();
  g.gain.setValueAtTime(0, at); g.gain.linearRampToValueAtTime(level, at + dur * 0.45); g.gain.linearRampToValueAtTime(0, at + dur);
  releaseOnEnd(src, bp, g);
  src.connect(bp).connect(g); g.connect(master); g.connect(wet);
  src.start(at, Math.random()); src.stop(at + dur + 0.05);
}

// page change: a soft breath and two quiet notes from the section's chord
function stab({ dur, sectionSlug, item = 0 }) {
  if (!live()) return;
  const now = ctx.currentTime + 0.01, d = Math.min(0.7, Math.max(0.25, dur / 1000));
  const chord = SOUND.voicing(sectionSlug || section, item);
  air(now, d, SOFT.air);
  softTone(SOUND.hz(chord[0] + 12), now + d * 0.35, SOFT.page, 0.08, 0.7);
  softTone(SOUND.hz(chord[2 % chord.length] + 12), now + d * 0.35 + 0.04, SOFT.page * 0.6, 0.1, 0.8);
  heard('page', { chord: chordName(sectionSlug || section) });
}

// something new appears: a slow, quiet rising arpeggio, high and mostly reverb, with a faint shimmer
function emerge({ node }) {
  if (!live()) return;
  const now = ctx.currentTime + 0.02;
  const s = node.kind === 'section' ? node.slug : node.kind === 'item' ? node.section.slug : node.item.section.slug;
  const chord = SOUND.voicing(s, 1);
  chord.slice(0, 4).forEach((semi, i) => softTone(SOUND.hz(semi + 24), now + i * 0.11, SOFT.emerge * (1 - i * 0.12), 0.18, 1.3, 0.25));
  air(now + 0.05, 1.1, SOFT.shimmer, 3000, 7000);
  heard('emerge', { chord: chordName(s) });
}

function copied() {
  if (!live()) return;
  const chord = SOUND.voicing(section, inversion), now = ctx.currentTime + 0.01;
  pluck(SOUND.hz(chord[chord.length - 2] + 12), now, SOUND.levels.pluck);
  pluck(SOUND.hz(chord[chord.length - 1] + 12), now + 0.11, SOUND.levels.pluck * 0.85);
  heard('copy', { chord: chordName(section) });
}

function tick() {
  if (!live()) return;
  // a soft droplet: a high note from the section's chord, mostly in the room
  const chord = SOUND.voicing(section), semi = chord[Math.floor(Math.random() * chord.length)] + 24;
  softTone(SOUND.hz(semi), ctx.currentTime + 0.005, AMB.drop, 0.006, 0.35, 0.2);
  heard('hover');
}


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

// ---------- touch: press, drag and release ----------
// Five palettes Ahmed auditioned (Nov 9), written as he heard them: [Hz, ms, gain, delay ms].
// Sines with soft attacks, mostly in the room. The gains are scaled as one by AMB.feel,
// so the loudest note of all (Felt's press) sits exactly at the hover droplet's level.
AMB.feel = AMB.drop / 0.35;
export const PALETTES = {
  felt: { label: 'Felt',
    press: [[146.83, 260, 0.35], [220, 320, 0.12, 10]],
    drag: { ms: 420, steps: [[[293.66, 0.08]], [[329.63, 0.08]], [[349.23, 0.08]]] },
    release: [[220, 600, 0.14], [146.83, 900, 0.10, 80]] },
  'felt-hushed': { label: 'Felt hushed',
    press: [[146.83, 600, 0.16], [220, 800, 0.05]],
    drag: { ms: 420, steps: [[[293.66, 0.04]], [[311.13, 0.04]]] },
    release: [[220, 1200, 0.07], [146.83, 1600, 0.05]] },
  unison: { label: 'Unison',
    press: [[146.83, 900, 0.1], [220, 900, 0.07]],
    drag: { ms: 1400, steps: [[[146.83, 0.05], [220, 0.04]]] },
    release: [[110, 1800, 0.1], [146.83, 1800, 0.07]] },
  'low-tide': { label: 'Low tide',
    press: [[73.42, 500, 0.3], [110, 500, 0.08]],
    drag: { ms: 1200, steps: [[[87.31, 0.12], [98, 0.08]]] },
    release: [[110, 900, 0.12], [73.42, 1600, 0.14]] },
  mist: { label: 'Mist',
    press: [[1174.66, 700, 0.03], [1244.51, 700, 0.02]],
    drag: { ms: 700, steps: [[[1760, 0.015], [1864.66, 0.012]]] },
    release: [[1174.66, 1500, 0.025], [880, 1800, 0.02]] },
};
const FEEL_IDS = [...Object.keys(PALETTES), 'off'];
audio.feel = FEEL_IDS.includes(readKey(FEEL_KEY)) ? readKey(FEEL_KEY) : 'felt-hushed'; // the default: Felt, hushed (Ahmed's pick)

// one sine that swells in (no click) and dies away over about ms, half dry, half in the room
function feltTone(f, at, peak, ms) {
  const dur = ms / 1000, attack = Math.min(0.04, Math.max(0.014, dur * 0.08));
  const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.value = f; o.detune.value = rand(-3, 3);
  const g = ctx.createGain();
  g.gain.setValueAtTime(0, at); g.gain.linearRampToValueAtTime(peak, at + attack); g.gain.setTargetAtTime(0, at + attack, (dur - attack) / 4);
  const d = ctx.createGain(); d.gain.value = 0.5;
  releaseOnEnd(o, g, d);
  o.connect(g); g.connect(d).connect(master); g.connect(wet);
  o.start(at); o.stop(at + dur * 1.6 + 0.05);
}
function feel(kind, step = 0, id = audio.feel) {
  const pal = PALETTES[id];
  if (!pal || !live()) return;
  const now = ctx.currentTime + 0.005, K = AMB.feel;
  if (kind === 'drag') pal.drag.steps[step % pal.drag.steps.length].forEach(([f, g]) => feltTone(f, now, g * K, pal.drag.ms));
  else pal[kind].forEach(([f, ms, g, d = 0]) => feltTone(f, now + d / 1000, g * K, ms));
  heard(kind, { palette: pal.label });
}

// where they play. press: pointerdown on anything you can press. drag: moving while held
// in the places that drag (the viewer's strip, the gallery grids, a phone's book shelf, the
// wordmark), one step per stretch of travel, so a faster drag steps faster (never more than
// one step per FEEL_DRAG.minMs). release: letting go after a drag or a long press.
const PRESSABLE = 'a[href], button, [role="button"], [role="radio"], [role="switch"], [role="tab"], .item, .masonry-cell, .record.has-media, .warm, .wordmark';
const DRAGGABLE = '.viewer-stage, .col-gallery, .sp-row, .wordmark';
const FEEL_DRAG = { startPx: 8, stepPx: 48, minMs: 90, longMs: 450 };
let gest = null;
window.addEventListener('pointerdown', (e) => {
  if (e.button !== 0 || audio.feel === 'off') { gest = null; return; }
  const t = e.target instanceof Element ? e.target : null;
  gest = { id: e.pointerId, x0: e.clientX, y0: e.clientY, lx: e.clientX, ly: e.clientY, t0: performance.now(),
    zone: !!t?.closest(DRAGGABLE), drag: false, acc: 0, step: 0, last: 0 };
  if (t?.closest(PRESSABLE) && !t.closest('[data-feel-skip]')) feel('press');
}, { capture: true, passive: true });
window.addEventListener('pointermove', (e) => {
  const g = gest; if (!g || e.pointerId !== g.id) return;
  const d = Math.hypot(e.clientX - g.lx, e.clientY - g.ly); g.lx = e.clientX; g.ly = e.clientY;
  if (!g.drag) { if (!g.zone || Math.hypot(e.clientX - g.x0, e.clientY - g.y0) < FEEL_DRAG.startPx) return; g.drag = true; }
  g.acc += d;
  const now = performance.now();
  if (g.acc >= FEEL_DRAG.stepPx && now - g.last >= FEEL_DRAG.minMs) { g.acc = 0; g.last = now; feel('drag', g.step++); }
}, { capture: true, passive: true });
const letGo = (e) => {
  const g = gest; if (!g || e.pointerId !== g.id) return;
  gest = null;
  if (g.drag || (e.type === 'pointerup' && performance.now() - g.t0 >= FEEL_DRAG.longMs)) feel('release');
};
window.addEventListener('pointerup', letGo, { capture: true, passive: true });
window.addEventListener('pointercancel', letGo, { capture: true, passive: true });
// a phone's book shelf scrolls natively (the browser cancels the pointer): its travel steps the drag
let shelf = null;
document.addEventListener('scroll', (e) => {
  const el = e.target; if (!(el instanceof Element) || !el.matches('.sp-row') || audio.feel === 'off') return;
  const now = performance.now();
  if (!shelf || shelf.el !== el) shelf = { el, x: el.scrollLeft, acc: 0, step: 0, last: 0 };
  shelf.acc += Math.abs(el.scrollLeft - shelf.x); shelf.x = el.scrollLeft;
  if (shelf.acc >= FEEL_DRAG.stepPx && now - shelf.last >= FEEL_DRAG.minMs) { shelf.acc = 0; shelf.last = now; feel('drag', shelf.step++); }
  clearTimeout(shelf.t); shelf.t = setTimeout(() => { if (shelf?.step) feel('release'); shelf = null; }, 180);
}, { capture: true, passive: true });

// a palette, start to finish: press, three drag steps, release (Settings' play buttons)
audio.preview = (id = audio.feel) => {
  if (!PALETTES[id]) return false;
  unlock();
  if (!ctx) return false;
  if (ctx.state !== 'running') ctx.resume().catch(() => {});
  const run = () => {
    feel('press', 0, id);
    [260, 380, 500].forEach((ms, i) => setTimeout(() => feel('drag', i, id), ms));
    setTimeout(() => feel('release', 0, id), 760);
  };
  ctx.state === 'running' ? run() : setTimeout(run, 60);
  return true;
};

// ---------- what the debug panel shows: every sound, in plain words ----------
const NOTE_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'];
const CHORD_NAMES = { articles: 'D minor 9', components: 'F major 7', harnesses: 'G minor 9', philosophy: 'B-flat major 7', library: 'A minor 7', friends: 'C add 9', experiments: 'E minor 7 flat 5' };
const chordName = (slug) => CHORD_NAMES[slug] || CHORD_NAMES.articles;
const counts = {};
function heard(id, d = {}) { counts[id] = (counts[id] || 0) + 1; bus.emit('sound:play', { id, ...d }); }

export const SOUNDS = [
  { id: 'emerge', name: 'Something new appears', when: 'A hidden page or section is revealed.',
    what: 'A slow, quiet rising arpeggio of four high sine notes from the section\'s chord, mostly reverb, with a faint shimmer of air over it. About a second and a half.' },
  { id: 'letter', name: 'Wordmark letters', when: 'You run the cursor along salehdigital.',
    what: 'Each of the 12 letters is a step up D minor pentatonic. A breath of noise settles onto a soft sine that rings out into the room. Moving faster plays a little brighter.' },
  { id: 'hover', name: 'Hover droplet', when: 'Your cursor rests on a menu item.',
    what: 'A soft, high droplet: one note from the section\'s chord, mostly reverb.' },
  { id: 'press', name: 'Press', when: 'You press a link, a button or a menu item.',
    what: 'Two soft sines from the chosen palette (Felt unless changed in Settings), mostly in the room. Felt is D and the A above it, the A a moment later.' },
  { id: 'drag', name: 'Drag', when: 'You drag the viewer\'s pictures, a gallery or a phone\'s book shelf.',
    what: 'One soft note for every stretch you drag, so a faster drag steps faster. Felt climbs D, E, F and starts over.' },
  { id: 'release', name: 'Release', when: 'You let go after a drag or a long press.',
    what: 'Two low sines that ring out longer than the press. Felt is A, then D under it.' },
  { id: 'bed', name: 'Background', when: 'Always, very quietly, while sound is on.',
    what: 'An ambient pad on the section\'s chord: four soft voices, each swelling on its own slow cycle, with a far-off breath of air. When you move to another section the harmony drifts there over a few seconds. It warms a little at every level.' },
];
export const SOUND_CHAIN = 'Everything sits in a long, soft generated reverb. Nothing is struck hard and nothing is a recording: every sound is made live in the browser.';

// play one sound on demand (the panel's play buttons); the click is the gesture that wakes audio
audio.play = (id) => {
  unlock();
  if (!ctx) return false;
  if (ctx.state !== 'running') ctx.resume().catch(() => {});
  const go = () => {
    if (!live()) return;
    if (id === 'emerge') emerge({ node: { kind: 'section', slug: section } });
    else if (id === 'letter') { let i = 0; const run = () => { letter({ index: i, total: 12, speed: 0.4 }); if (++i < 12) setTimeout(run, 70); }; run(); }
    else if (id === 'hover') tick();
    else if (id === 'press' || id === 'release') feel(id);
    else if (id === 'drag') [0, 1, 2].forEach(i => setTimeout(() => feel('drag', i), i * 140));
    else if (id === 'bed') { // swell it up for two seconds so it can be heard, then settle back
      if (!audio.bed) return;
      const now = ctx.currentTime, L = SOUND.levels, k = 7 * (1 + L.warmthPerTier * tier);
      bedNoiseGain.gain.setTargetAtTime(AMB.air * k, now, 0.25); droneGain.gain.setTargetAtTime(AMB.pad * k, now, 0.25);
      setTimeout(() => warmth(tier, 0.6), 2200); heard('bed');
    }
  };
  ctx.state === 'running' ? go() : setTimeout(go, 60);
  return true;
};
audio.status = () => ({
  on: audio.enabled, bedOn: audio.bed, feel: audio.feel, ready: !!ctx, state: ctx ? ctx.state : 'waiting', tier, section, chord: chordName(section),
  bed: ctx && bedNoiseGain ? (1 + SOUND.levels.warmthPerTier * tier) : 0, counts: { ...counts }
});

bus.on('resolve:start', (d) => {
  if (d.sectionSlug) { if (d.sectionSlug !== section) padTo(d.sectionSlug); section = d.sectionSlug; inversion = d.item || 0; }
  // page change is silent: the post writing itself in carries it (Ahmed, Nov 9)
  // 'clock' is silent: a visual micro-resolve only. 'emerge' sounds on the emerge event.
});
bus.on('emerge', emerge);
bus.on('hover', tick);
// copy is silent too (Ahmed, Nov 9): the icon morph and the haptic tap are enough
bus.on('resonance', (d) => { tier = d.tier; warmth(tier); });
document.addEventListener('visibilitychange', sync);
```
