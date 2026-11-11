---
title: Contents (sub-nav and sections pill)
slug: toc
status: published
description: "A post's contents: its h2s under the title in the sticky sub-nav with an SDF dot-matrix marker on desktop, and a liquid-glass sections pill on phones. Added 2026-11-11."
chips:
  - Pattern
  - Navigation
  - Reading
created: 2026-11-11T16:35:49Z
updated: 2026-11-11T16:35:54Z
---

Added to the live site on 2026-11-11. A post with two or more visible `h2`s gets its contents in two places:

- **Desktop (≥ 900px): under its title in the sub-nav.** A `ul.toc` (aria-label "On this page") of `a.toc-link`s, one per `h2` (and an embed's `h2[data-toc]`), in 14/18 Inter Display, tracking −0.2px, indented 12px under the active page title, 6px apart. Rest opacity `--op-rest`, hover `--op-peek`, the section being read `is-current` at full ink with `aria-current="location"`. The sub-nav is `position: sticky; top: 24px` with its own hidden scrollbar, so the title and the contents stay in view.
- **The marker:** a 2-column strip of dots (pitch 4px, radius 0.3 to 1.35px) in the contents' 8px gutter, in `--accent-mark`. Each dot's radius is read off a capsule SDF as tall as the active link (soft edge 5px, smoothstep). The capsule glides to the next heading on a critically damped spring (ω 26/s); under reduced motion it jumps. Redrawn on theme change and resize.
- **Phones (< 900px): a floating "sections pill".** `nav.toc-pill` (aria-label "Sections"), fixed at the bottom centre, `min(100vw − 32px, 360px)` × 48px, fully rounded, in liquid glass (`backdrop-filter: blur(18px) saturate(1.8) brightness(1.04)` over 52% paper, a specular rim and sheen). Previous / the current section ("n/N" in 12px muted, then its title) / next. Tapping the label opens `#toc-pop`, the full list in the same glass above the pill. The page gets 72px of bottom padding while the pill shows. It enters over 320ms (`toc-pill-in`), the list over 220ms; no animation under reduced motion; a solid 94% paper fallback without backdrop-filter.
- **Scrolling:** the current section is the last `h2` above 30% of the viewport, synced on scroll (one rAF). A link scrolls smoothly to the heading (24px from the top on desktop, 16px on phones; instant under reduced motion) and focuses it.
- Not on galleries or slides.

## Code

Source: `site/js/app.js`, lines 120 to 252

```js
// ---------- the post's contents (Ahmed, Nov 11): its h2s as links under its title in the sub-nav ----------
// The sub-nav is sticky on desktop, so the title and these links stay in view while reading. The hash is
// the router, so the links scroll in place; the one being read is sharp, like the active page.
const tocHeads = () => [...article.querySelectorAll(':scope > h2, :scope > .embed h2[data-toc]')]; // an embed may take its section's heading inside (harness-install)
let tocTitles = [], tocCur = 0;
function toHead(i) {
  const h = tocHeads()[i]; if (!h) return;
  const y = h.getBoundingClientRect().top + scrollY - (matchMedia('(max-width: 899px)').matches ? 16 : 24);
  scrollTo({ top: y, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  h.setAttribute('tabindex', '-1'); h.focus({ preventScroll: true });
}
function addToc(r) {
  tocTitles = [];
  const heads = r.item.paras.filter(p => paraVisible(p, E.vis) && p.b === 'h2' && p.t);
  const at = sub.querySelector('.item.is-active');
  if (heads.length < 2 || !at || isGallery(r) || isSlides(r)) { pill.root.hidden = true; return; }
  tocTitles = heads.map(p => p.t);
  const ul = document.createElement('ul'); ul.className = 'toc'; ul.setAttribute('aria-label', 'On this page');
  heads.forEach((p, i) => {
    const a = document.createElement('a');
    a.className = 'toc-link'; a.href = r.hash; a.textContent = p.t; a.dataset.i = i;
    a.addEventListener('click', (e) => { e.preventDefault(); toHead(i); });
    ul.append(li(a));
  });
  at.closest('li').append(ul);
  tocDots.mount(ul);
  pill.build(r.hash);
  syncToc();
}
// phones (Ahmed, Nov 11): the sub-nav sits above the post, so the sections ride in a glass pill at the
// bottom instead: previous, the section being read (tap for all of them), next.
const pill = (() => {
  const root = document.createElement('nav'); root.className = 'toc-pill'; root.setAttribute('aria-label', 'Sections'); root.hidden = true;
  const btn = (cls, label, html) => { const b = document.createElement('button'); b.type = 'button'; b.className = cls; b.setAttribute('aria-label', label); b.innerHTML = html; return b; };
  const chev = (d) => `<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true"><path d="${d}" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  const prev = btn('toc-pill-step', 'Previous section', chev('M10 3.5 5.5 8l4.5 4.5'));
  const next = btn('toc-pill-step', 'Next section', chev('M6 3.5 10.5 8 6 12.5'));
  const label = btn('toc-pill-label', 'All sections', '<span class="toc-pill-n"></span><span class="toc-pill-t"></span>');
  label.setAttribute('aria-expanded', 'false'); label.setAttribute('aria-controls', 'toc-pop');
  const pop = document.createElement('div'); pop.className = 'toc-pop'; pop.id = 'toc-pop'; pop.hidden = true;
  root.append(prev, label, next);
  document.body.append(pop); // a sibling, not a child: inside the pill's backdrop-filter its own blur would see nothing behind it
  document.body.append(root);
  const open = (on) => { pop.hidden = !on; label.setAttribute('aria-expanded', String(on)); root.classList.toggle('is-open', on); };
  prev.addEventListener('click', () => toHead(Math.max(0, tocCur - 1)));
  next.addEventListener('click', () => toHead(Math.min(tocTitles.length - 1, tocCur + 1)));
  label.addEventListener('click', () => open(pop.hidden));
  addEventListener('keydown', (e) => { if (e.key === 'Escape' && !pop.hidden) { open(false); label.focus(); } });
  addEventListener('pointerdown', (e) => { if (!pop.hidden && !root.contains(e.target) && !pop.contains(e.target)) open(false); }, true);
  return {
    root,
    build(hash) {
      const ul = document.createElement('ul');
      tocTitles.forEach((t, i) => {
        const a = document.createElement('a'); a.href = hash; a.className = 'toc-pop-link'; a.textContent = t; a.dataset.i = i;
        a.addEventListener('click', (e) => { e.preventDefault(); open(false); toHead(i); });
        ul.append(li(a));
      });
      pop.replaceChildren(ul); open(false); root.hidden = false;
    },
    sync(i) {
      label.querySelector('.toc-pill-n').textContent = `${i + 1}/${tocTitles.length}`;
      label.querySelector('.toc-pill-t').textContent = tocTitles[i] || '';
      prev.disabled = i <= 0; next.disabled = i >= tocTitles.length - 1;
      pop.querySelectorAll('.toc-pop-link').forEach((a, k) => a.classList.toggle('is-current', k === i));
    },
  };
})();
function syncToc() {
  const links = sub.querySelectorAll('.toc-link'); if (!links.length) return;
  const heads = tocHeads(), line = innerHeight * 0.3;
  let cur = -1;
  heads.forEach((h, i) => { if (h.getBoundingClientRect().top <= line) cur = i; });
  // at the end of the page the last sections can't scroll up to the line: the bottom reads as the last one
  if (innerHeight + scrollY >= document.documentElement.scrollHeight - 4) cur = heads.length - 1;
  tocCur = Math.max(cur, 0);
  links.forEach((a, i) => { const on = i === tocCur; a.classList.toggle('is-current', on); on ? a.setAttribute('aria-current', 'location') : a.removeAttribute('aria-current'); });
  pill.sync(tocCur);
  tocDots.to(links[tocCur]);
}
// the active heading's marker (Ahmed, Nov 11): the footer's SDF dot matrix in the contents' gutter, in the
// accent. A strip of dots on a fixed grid; each dot's radius is read off a signed distance field, a capsule
// as tall as the active link, so inside it the dots swell to full size and outside they shrink to pinpricks.
// The capsule glides to the next heading on the site's ease (a critically damped spring); still under reduced motion.
const tocDots = (() => {
  const PITCH = 4, COLS = 2, RMAX = 1.35, RMIN = 0.3, SOFT = 5;
  let cv = null, cx = null, ul = null, y = null, h = 0, ty = 0, th = 0, v = 0, raf = 0, ink = '#000', last = 0;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const readInk = () => { if (cv) ink = getComputedStyle(cv).getPropertyValue('--accent-mark').trim() || getComputedStyle(cv).color; };
  function draw() {
    if (!cv) return;
    const W = cv.clientWidth, H = ul.clientHeight, dpr = Math.min(2, devicePixelRatio || 1);
    if (cv.width !== Math.round(W * dpr) || cv.height !== Math.round(H * dpr)) { cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); cv.style.height = H + 'px'; }
    cx.setTransform(dpr, 0, 0, dpr, 0, 0); cx.clearRect(0, 0, W, H); cx.fillStyle = ink;
    const x0 = (W - (COLS - 1) * PITCH) / 2;
    for (let r = 0, gy = PITCH / 2; gy < H; r++, gy += PITCH) {
      // the capsule's distance, in px: < 0 inside the active link's band
      const d = Math.abs(gy - y) - h / 2;
      const k = Math.min(1, Math.max(0, d / SOFT)), t = 1 - k * k * (3 - 2 * k); // smoothstep falloff
      const rad = RMIN + (RMAX - RMIN) * t;
      if (rad < 0.32 && d > SOFT * 2) cx.globalAlpha = 0.35; else cx.globalAlpha = 0.35 + 0.65 * t;
      for (let c = 0; c < COLS; c++) { cx.beginPath(); cx.arc(x0 + c * PITCH, gy, rad, 0, Math.PI * 2); cx.fill(); }
    }
    cx.globalAlpha = 1;
  }
  function step(now) {
    const dt = Math.min(0.05, (now - (last || now)) / 1000); last = now;
    const w = 26, a = w * w * (ty - y) - 2 * w * v; // critically damped spring toward the target
    v += a * dt; y += v * dt; h += (th - h) * Math.min(1, dt * 18);
    draw();
    if (Math.abs(ty - y) > 0.2 || Math.abs(v) > 0.5 || Math.abs(th - h) > 0.2) raf = requestAnimationFrame(step); else { y = ty; h = th; v = 0; raf = 0; last = 0; draw(); }
  }
  return {
    mount(list) {
      ul = list; cv = document.createElement('canvas'); cv.className = 'toc-dots'; cv.setAttribute('aria-hidden', 'true');
      list.prepend(cv); cx = cv.getContext('2d'); y = null; readInk();
    },
    to(a) {
      if (!cv || !a || !cv.isConnected) return;
      const ur = ul.getBoundingClientRect(), r = a.getBoundingClientRect();
      ty = r.top - ur.top + r.height / 2; th = r.height;
      if (y == null || reduce.matches || !ul.offsetParent) { y = ty; h = th; v = 0; draw(); return; }
      if (!raf) raf = requestAnimationFrame(step);
    },
    redraw() { readInk(); draw(); },
  };
})();
onTheme(() => requestAnimationFrame(() => tocDots.redraw()));
addEventListener('resize', () => { const a = sub.querySelector('.toc-link.is-current'); if (a) { tocDots.redraw(); tocDots.to(a); } });

let tocRaf = 0;
addEventListener('scroll', () => { if (!tocRaf) tocRaf = requestAnimationFrame(() => { tocRaf = 0; syncToc(); }); }, { passive: true });
```

Source: `site/css/site.css`, lines 920 to 986

```css
/* the post's contents under its title, and the sub-nav sticky on desktop so both stay in view (Ahmed, Nov 11).
   The links are the sub-nav's type a step smaller, indented under the title; the one being read is sharp. */
@media (min-width: 900px) {
  .col-sub { position: sticky; top: 24px; max-height: calc(100vh - 48px); overflow-y: auto; scrollbar-width: none; overscroll-behavior: contain; }
  .col-sub::-webkit-scrollbar { display: none; }
}
.col-sub .toc { display: flex; flex-direction: column; gap: 6px; margin: 10px 0 4px; padding: 0 0 0 12px; list-style: none; }
.toc-link { display: block; font: 400 14px/18px var(--ui); letter-spacing: -0.2px; color: var(--ink); text-decoration: none; text-wrap: balance;
  opacity: var(--op-rest); filter: url(#ink-ui); transition: opacity 160ms var(--ease-land); }
.toc-link:hover { opacity: var(--op-peek); }
.toc-link.is-current { opacity: 1; }
.toc-link:focus-visible { outline: none; opacity: 1; text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; }
@media (max-width: 899px) { .col-sub .toc { display: none; } }

/* the sections pill on phones (Ahmed, Nov 11): liquid glass, floating over the post at the bottom.
   A frosted, saturated backdrop; a specular rim lit from above; a soft lift. Previous, the section being
   read (its number, then its name; tap for all of them), next. */
.toc-pill { display: none; }
@media (max-width: 899px) {
  .toc-pill:not([hidden]) { display: flex; }
  .toc-pill { position: fixed; z-index: 40; left: 50%; bottom: max(16px, env(safe-area-inset-bottom)); transform: translateX(-50%);
    align-items: center; gap: 2px; width: min(calc(100vw - 32px), 360px); height: 48px; padding: 4px; border-radius: 999px; box-sizing: border-box;
    color: var(--ink); font: 400 15px/20px var(--ui); letter-spacing: -0.2px;
    background: color-mix(in srgb, var(--paper) 52%, transparent);
    -webkit-backdrop-filter: blur(18px) saturate(1.8) brightness(1.04); backdrop-filter: blur(18px) saturate(1.8) brightness(1.04);
    box-shadow: inset 0 1px 0 color-mix(in srgb, #fff 55%, transparent), inset 0 -1px 0 color-mix(in srgb, var(--ink) 5%, transparent),
      inset 0 0 0 1px color-mix(in srgb, var(--ink) 9%, transparent), 0 1px 2px color-mix(in srgb, #000 8%, transparent), 0 10px 30px -8px color-mix(in srgb, #000 22%, transparent);
    animation: toc-pill-in 320ms var(--ease-land) both; }
  /* the specular sheen across the top half */
  .toc-pill::before { content: ''; position: absolute; inset: 1px 1px 50% 1px; border-radius: 999px 999px 40% 40% / 999px 999px 100% 100%; pointer-events: none;
    background: linear-gradient(to bottom, color-mix(in srgb, #fff 26%, transparent), transparent); }
  :is([data-theme="dark"], [data-theme="marathon-dark"]) .toc-pill { background: color-mix(in srgb, var(--paper) 46%, transparent);
    box-shadow: inset 0 1px 0 color-mix(in srgb, #fff 16%, transparent), inset 0 0 0 1px color-mix(in srgb, #fff 9%, transparent), 0 10px 30px -8px color-mix(in srgb, #000 60%, transparent); }
  :is([data-theme="dark"], [data-theme="marathon-dark"]) .toc-pill::before { background: linear-gradient(to bottom, color-mix(in srgb, #fff 7%, transparent), transparent); }
  .toc-pill button { position: relative; display: flex; align-items: center; justify-content: center; height: 40px; border: 0; border-radius: 999px; background: none; color: inherit; font: inherit; letter-spacing: inherit;
    cursor: pointer; -webkit-tap-highlight-color: transparent; transition: background-color 140ms var(--ease-land), opacity 140ms var(--ease-land), transform 140ms var(--ease-land); }
  .toc-pill button:active { background: color-mix(in srgb, var(--ink) 8%, transparent); transform: scale(.97); }
  .toc-pill button:focus-visible { outline: none; box-shadow: inset 0 0 0 1.5px var(--ring); }
  .toc-pill-step { flex: none; width: 40px; }
  .toc-pill-step:disabled { opacity: .3; pointer-events: none; }
  .toc-pill-label { flex: 1; min-width: 0; gap: 8px; padding: 0 8px; }
  .toc-pill-n { flex: none; font-size: 12px; color: var(--muted); } /* proportional figures (Ahmed, Nov 11) */
  .toc-pill-t { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  /* all the sections, in the same glass, above the pill */
  .toc-pop { position: fixed; z-index: 41; left: 50%; translate: -50% 0; width: min(calc(100vw - 32px), 360px); box-sizing: border-box; bottom: calc(max(16px, env(safe-area-inset-bottom)) + 48px + 8px); max-height: 60vh;
    color: var(--ink); font: 400 15px/20px var(--ui); letter-spacing: -0.2px; overflow-y: auto; padding: 6px; border-radius: 22px;
    background: color-mix(in srgb, var(--paper) 72%, transparent); -webkit-backdrop-filter: blur(24px) saturate(1.8); backdrop-filter: blur(24px) saturate(1.8);
    box-shadow: inset 0 1px 0 color-mix(in srgb, #fff 45%, transparent), inset 0 0 0 1px color-mix(in srgb, var(--ink) 9%, transparent), 0 16px 40px -12px color-mix(in srgb, #000 28%, transparent);
    transform-origin: 50% 100%; animation: toc-pop-in 220ms var(--ease-land) both; }
  .toc-pop[hidden] { display: none; }
  .toc-pop ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; }
  .toc-pop-link { display: block; padding: 10px 14px; border-radius: 16px; color: var(--ink); text-decoration: none; opacity: var(--op-peek); -webkit-tap-highlight-color: transparent; }
  .toc-pop-link.is-current { opacity: 1; background: color-mix(in srgb, var(--ink) 6%, transparent); }
  .toc-pop-link:active { background: color-mix(in srgb, var(--ink) 9%, transparent); }
  /* room under the post for the pill */
  html:has(.toc-pill:not([hidden])) .site { padding-bottom: 72px; }
}
@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .toc-pill, .toc-pop { background: color-mix(in srgb, var(--paper) 94%, transparent) !important; }
}
@keyframes toc-pill-in { from { opacity: 0; transform: translate(-50%, 12px) scale(.96); } }
@keyframes toc-pop-in { from { opacity: 0; transform: translateY(6px) scale(.97); } }
@media (prefers-reduced-motion: reduce) { .toc-pill, .toc-pop { animation: none; } }
/* the active heading's dot-matrix marker in the contents' gutter (js/app.js tocDots) */
.col-sub .toc { position: relative; padding-left: 16px; }
.toc-dots { position: absolute; left: 0; top: 0; width: 8px; pointer-events: none; color: var(--accent-mark); }
```
