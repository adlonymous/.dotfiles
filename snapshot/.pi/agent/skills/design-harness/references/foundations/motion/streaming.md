---
title: Streaming
slug: streaming
status: published
description: "The post writes itself word by word: 9ms apart, each word inking in from a 5px blur in 141ms, behind an accent caret."
chips:
  - Motion
  - Streaming
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:01:22Z
---

A post (and every MCP chat reply) writes itself in front of you, word by word. Each word inks in from a soft blur, with a small caret at the leading edge in the theme's accent.

## When it runs

- **First load:** `go(true)` renders the route, puts the actions row away (`.post-meta.is-away`), then calls `streamIn(article, 'load')`.
- **Every page change:** `transition(…, { body: true })` calls `streamIn` on the `[data-morph-lines]` element when its text changed.
- **Emergence:** with kind `emerge`, the per-word delay is ×1.25.
- **MCP chat:** each reply is streamed. The buttons, fields and code in it are `data-stream-skip` and `data-held`, and rise in afterwards.

The actions row comes back on `stream:end`.

## Exact timing (energy E = .5)

- `slow = MOTION.streamWordMs / 14`, which is 9/14 ≈ .643 (the source comment says "follows slow motion review").
- `per = min(9 × (kind == emerge ? 1.25 : 1) × (1.3 − .6E), 650 × slow / max(1, wordsOnScreen))`, which is at most **9ms** between words. With many words on screen it shrinks so they all start within 418ms.
- `ink = 220 × slow` ≈ **141ms** per word.
- Keyframes for a word on screen: `{opacity 0, blur(5px)}` → at .45 `{opacity .55, blur(1.4px)}` → `{opacity 1, blur(0)}`, easing `cubic-bezier(0.2, 0, 0, 1)`, `fill: backwards`.
- Words below the fold: a 200ms plain opacity fade, all at the last on-screen delay.
- **LCP rule:** the words of the first paragraph (`p:first-of-type`) are shown at once and never animate. Streaming starts with the second paragraph.
- Total = last delay + ink. `stream:end` fires 20ms after.
- **Caret:** a `span.stream-caret` follows the current word on rAF. It sits at `translate(right + 3px, top + 18% of the line)`, lags by ink × .4, and fades out over 360ms after a 160ms delay at the end.
- **Reduced motion:** one 160ms opacity fade, done at 170ms.
- Words are wrapped as `span.sw`. Inside a flex or grid parent the words go into one `span.sw-run`, so nothing reflows. Text inside `.sr-only`, `.stream-caret` or `[data-stream-skip]` is not wrapped. Everything is unwrapped again at the end.

## CSS

Source: `site/css/site.css`, lines 309 to 312

```css
/* the post streaming in: words ink in behind a small caret at the leading edge, in the theme's accent (ink in Paper and Night) */
.col-body article { position: relative; }
.col-body .sw { display: inline; }
.stream-caret { position: absolute; left: 0; top: 0; width: 7px; height: 0.72em; background: var(--accent-mark, currentColor); border-radius: 1px; pointer-events: none; opacity: .85; filter: blur(.3px); will-change: transform; }
```


## Code (verbatim)

Source: `site/js/resolve.js`, lines 95 to 195

```js
// streaming: the post is written in front of you, word by word, each word inking
// in from a soft blur, a small ink caret at the leading edge. Only the words on
// screen stream; the rest are there by the time you scroll. Ends with 'stream:end'.
// LCP fix: first paragraph renders immediately, animation starts from second paragraph
let streamRun = 0;
export function streamIn(el, kind = 'state', id = null) {
  const run = ++streamRun;
  el.getAnimations({ subtree: true }).forEach(a => a.cancel());
  unwrapWords(el);
  el.querySelector(':scope > .stream-caret')?.remove();
  const done = (ms) => setTimeout(() => { if (run !== streamRun) return; unwrapWords(el); delete el.dataset.streaming; bus.emit('stream:end', { id, kind }); }, ms);
  el.dataset.streaming = '1';
  if (reducedMotion.matches) { el.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 160 }); done(170); return 170; }
  
  // Find first paragraph and make it visible immediately for LCP
  const firstP = el.querySelector('p:first-of-type');
  if (firstP) firstP.style.opacity = '1';
  
  const words = wrapWords(el);
  if (!words.length) { done(0); return 0; }
  
  // Skip animation for words in first paragraph (LCP optimization)
  const firstPWords = firstP ? Array.from(firstP.querySelectorAll('span.sw')) : [];
  const firstPEnd = firstPWords.length;
  
  const vh = innerHeight;
  let onScreen = words.findIndex(w => w.getBoundingClientRect().top > vh);
  if (onScreen < 0) onScreen = words.length;
  const energy = params.energy ?? 0.5;
  const slow = MOTION.streamWordMs / 14; // follows slow motion review
  const per = Math.min(MOTION.streamWordMs * (kind === 'emerge' ? 1.25 : 1) * (1.3 - 0.6 * energy), MOTION.streamMaxMs * slow / Math.max(1, onScreen));
  const ink = MOTION.streamInkMs * slow;
  const last = per * Math.max(0, onScreen - firstPEnd - 1);
  
  words.forEach((w, i) => {
    // Skip animation for first paragraph words (appear immediately)
    if (i < firstPEnd) {
      w.style.opacity = '1';
      w.style.filter = 'none';
      return;
    }
    const vis = i < onScreen;
    const delay = vis ? per * Math.max(0, i - firstPEnd) : last;
    w.animate(vis ? [
      { opacity: 0, filter: 'blur(5px)' },
      { opacity: 0.55, filter: 'blur(1.4px)', offset: 0.45 },
      { opacity: 1, filter: 'blur(0px)' }
    ] : [{ opacity: 0 }, { opacity: 1 }], { duration: vis ? ink : 200, delay, easing: 'cubic-bezier(0.2, 0, 0, 1)', fill: 'backwards' });
  });
  
  if (onScreen > firstPEnd) {
    caret(el, words.slice(firstPEnd), per, onScreen - firstPEnd, run, ink * 0.4);
  }
  const total = last + ink;
  done(total + 20);
  return total;
}
function caret(el, words, per, n, run, lag = 0) {
  const c = document.createElement('span');
  c.className = 'stream-caret'; c.setAttribute('aria-hidden', 'true');
  el.append(c);
  const t0 = performance.now();
  const step = (t) => {
    if (run !== streamRun || !c.isConnected) { c.remove(); return; }
    const i = Math.max(0, Math.min(n - 1, Math.floor((performance.now() - t0 - lag) / per)));
    const r = words[i].getBoundingClientRect(), b = el.getBoundingClientRect();
    c.style.transform = `translate(${r.right - b.left + 3}px, ${r.top - b.top + r.height * 0.18}px)`;
    if (i < n - 1) requestAnimationFrame(step);
    else c.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 360, delay: 160, fill: 'forwards' }).onfinish = () => c.remove();
  };
  requestAnimationFrame(step);
}
function wrapWords(el) {
  const out = [];
  const walk = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, { acceptNode: (n) => (n.parentElement.closest('.sr-only, .stream-caret, [data-stream-skip]') || !n.nodeValue.trim()) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT });
  const nodes = []; while (walk.nextNode()) nodes.push(walk.currentNode);
  // In a flex or grid parent (a numbered step is a 20px | 1fr grid) each word span would become
  // its own item and the line would break up into cells until the stream ends. There the words
  // go in one run span, a single item just like the text's own anonymous box, so nothing reflows.
  const boxed = new Map();
  const isBox = (p) => { if (!boxed.has(p)) boxed.set(p, /flex|grid/.test(getComputedStyle(p).display)); return boxed.get(p); };
  for (const n of nodes) {
    const run = isBox(n.parentElement) ? Object.assign(document.createElement('span'), { className: 'sw-run' }) : null;
    const frag = run || document.createDocumentFragment();
    for (const part of n.nodeValue.split(/(\s+)/)) {
      if (!part) continue;
      if (/^\s+$/.test(part)) { frag.append(part); continue; }
      const s = document.createElement('span'); s.className = 'sw'; s.textContent = part;
      frag.append(s); out.push(s);
    }
    n.replaceWith(frag);
  }
  return out;
}
function unwrapWords(el) {
  const ws = el.querySelectorAll('span.sw');
  if (!ws.length) return;
  ws.forEach(s => s.replaceWith(s.textContent));
  el.querySelectorAll('span.sw-run').forEach(r => r.replaceWith(...r.childNodes));
  el.normalize();
}
```
