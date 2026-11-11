---
title: Hidden extras
slug: hidden-extras
status: published
description: "The secrets: warm words, holding the wordmark for 2s, typing harness, being here at night in Toronto, and the wordmark played by hovering."
chips:
  - Motion
  - Secrets
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:02:22Z
---

Small rewards for attention, all in `js/app.js` and `js/emergence.js`. Each found secret adds +10 resonance and leaves a yellow trace in a letter of the wordmark (`LIFE.traceLetters`: warm → letter 9, hold → 0, harness → 4, night → 7, each a dot cluster of radius .32 × cap). While emergence is off ([emergence](emergence.md)), the reveals they would unlock are already visible.

1. **(a) Warm words.** Text written `{{word|secret}}` in the CMS renders as `span.warm` (role button, tabbable). It rests faintly warm (`--warm`, no underline). After a 700ms hover, or on focus, it resolves heavier (`.is-lit`, a hover morph) and emits `hover`. A click or Enter opens the hidden piece, navigating after 1.5s if the click revealed something new.
2. **(b) Hold the wordmark for 2s.** Holding a pointer (or Space/Enter) on the footer wordmark builds up `setHold(p)` over 2000ms. At 1 the field morphs into **أحمد صالح** (set in Inter Display, centred, about the word's height) over 1100ms. The aria-label changes to it, it holds for 3600ms, then morphs back over 1100ms, and it cannot be retriggered until 4800ms. This unlocks `hold`. Afterwards a faint Arabic ghost (alpha `LIFE.ghostAlpha` .16) stays in the halftone.
3. **(c) Type "harness".** Typing the word anywhere outside an input unlocks `harness`. The last 16 keys are kept.
4. **(d) Night.** Being on the site between 23:00 and 05:00 Toronto time unlocks `night`.
5. **Playing the wordmark.** Moving across the footer wordmark plays a note per letter crossed: D minor pentatonic over the 12 letters, velocity from pointer speed, at least 38ms apart. A phone gets a haptic tick: [9] on the first and last letter, [4] between. See [sound](../sound/sound.md).

The footer bio, basmala and marks share the wordmark's hover: under the cursor their outlines warp, then melt and bleed. In GL that is `FOOT_HOVER` in the wordmark pass. Without GL, or with `?lite`, it is the SVG `#ink-mark` / `#ink-bio` filters, and it is off under reduced motion.

Source: `site/js/app.js`, lines 532 to 613

```js
// (a) warm words: faintly warm at rest, resolve heavier on a long hover, open a hidden piece
function warmWord(word, secret) {
  const w = document.createElement('span');
  w.className = 'warm'; w.textContent = word;
  w.dataset.secret = secret; w.dataset.morph = `warm-${warmCount++}`;
  w.tabIndex = 0; w.setAttribute('role', 'button');
  let timer = 0;
  const lit = (on) => {
    if (w.classList.contains('is-lit') === on) return;
    transition(() => w.classList.toggle('is-lit', on), { keys: [w.dataset.morph], kind: 'hover' });
    if (on) bus.emit('hover', { el: w, source: 'warm' });
  };
  w.addEventListener('pointerenter', () => { clearTimeout(timer); timer = setTimeout(() => lit(true), 700); });
  w.addEventListener('pointerleave', () => { clearTimeout(timer); lit(false); });
  w.addEventListener('focus', () => lit(true));
  w.addEventListener('blur', () => lit(false));
  w.addEventListener('click', () => openSecret(secret));
  w.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openSecret(secret); } });
  return w;
}

// (c) typing a word anywhere
let typed = '';
window.addEventListener('keydown', (e) => {
  if (e.metaKey || e.ctrlKey || e.altKey || e.key.length !== 1 || e.target.closest?.('input, textarea, select')) return;
  typed = (typed + e.key.toLowerCase()).slice(-16);
  if (typed.endsWith('harness')) { typed = ''; E.unlock('harness'); }
});

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

// slow hovers feed resonance
let slowTimer = 0;
document.addEventListener('pointerover', (e) => {
  const el = e.target.closest('a, button, .warm, .wordmark');
  clearTimeout(slowTimer);
  if (!el) return;
  slowTimer = setTimeout(() => E.slowHover(el.dataset.morph || el.dataset.node || el.id || el.getAttribute('class')), 600);
});
```
