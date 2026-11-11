---
title: Harness actions
slug: harness-actions
status: published
description: "::harness-actions: three full-width rows under the article: Download my harness, Download harness schema, Book time."
chips:
  - Embed
  - Download
  - CTA
created: 2026-11-11T16:05:20Z
updated: 2026-11-11T16:05:35Z
---

Embeds are placed in a post by a paragraph that is only `::name` (`EMBED = /^::([a-z-]+)\s*$/`). `js/embeds.js` replaces it with `<div class="embed embed-NAME" data-embed="NAME" data-stream-skip>`, lazy-imports `js/embeds/NAME.js` and calls `mount(el, ctx)`. Embeds are skipped by the word stream and by the body ink filter (`.col-body article > :not(.embed) { filter: url(#ink-body) }`), so screenshots and diagrams stay sharp.

**What it is.** The article's call to action, under "If you would like a design harness…". It is three full-width rows in the diagrams' language (34px, 8px corners, 1px ink rule, the diagram ink filter). Each row has an icon, a title, and a reason under it:

| Row | Title | Reason | Target |
|---|---|---|---|
| 1 (`is-primary`) | Download my harness | If you want to make sites like mine | `assets/downloads/salehdigital-design-harness.zip` (download attribute `salehdigital-design-harness.zip`) |
| 2 | Download harness schema | If you want to create your own harness | `assets/downloads/design-harness-starter.zip` (`design-harness-starter.zip`) |
| 3 | Book time | If you want help making your own harness | `BOOKING_URL` (new tab), else `#/friends/say-hello` |

The two zips are built by the site's `tools/build-harness-zip.py`. A rebuild links to its own zips. The "Open in Claude / ChatGPT / Grok" buttons were removed (Ahmed, Nov 10); the constants are still in the file. Row icons: a 14px download icon and a 14px calendar icon (`currentColor`; the paths are omitted here).

Source: `site/css/embeds/harness-actions.css`, whole file

```css
/* ::harness-actions (js/embeds/harness-actions.js): Download harness, Book time, Open in (AI icons).
   The diagrams' language: 34px, 8px corners, 1px ink rule, 13px UI type, 14px icons, the diagram ink. */
.embed-harness-actions { margin: calc(var(--para) * -0.25) 0 calc(var(--para) * 0.25); }
.ha-row { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; filter: url(#ink-diagram); }
.ha-btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; height: 34px; padding: 0 12px; border-radius: 8px;
  box-shadow: 0 0 0 1px var(--ink); background: var(--paper); color: var(--ink); font: 400 13px/1 var(--ui); letter-spacing: -0.2px; text-decoration: none; white-space: nowrap;
  -webkit-tap-highlight-color: transparent; transition: background-color 140ms var(--ease-land), color 140ms var(--ease-land), transform 140ms var(--ease-land); }
.ha-btn svg { flex: none; display: block; }
.ha-btn:hover { background: color-mix(in srgb, var(--ink) 6%, var(--paper)); }
.ha-btn:active { transform: translateY(1px); }
.ha-btn.is-primary { background: var(--ink); color: var(--paper); }
.ha-btn.is-primary:hover { background: color-mix(in srgb, var(--ink) 86%, var(--paper)); }
.ha-btn:focus-visible { outline: 2px solid var(--ink); outline-offset: 3px; }
.ha-open { display: inline-flex; align-items: center; gap: 6px; margin-left: 8px; }
.ha-open-label { font: 400 13px/1 var(--ui); letter-spacing: -0.2px; color: var(--muted); margin-right: 2px; }
.ha-btn.is-icon { width: 34px; padding: 0; }
.ha-ai { width: 15px; height: 15px; background: currentColor; -webkit-mask: var(--ai) center / contain no-repeat; mask: var(--ai) center / contain no-repeat; }
@media (max-width: 599px) { .ha-open { margin-left: 0; width: 100%; } }
@media (prefers-reduced-motion: reduce) { .ha-btn { transition: none; } .ha-btn:active { transform: none; } }

/* the two downloads: a title and the reason under it (Ahmed, Nov 10) */
.ha-dls { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; filter: url(#ink-diagram); }
.ha-btn.ha-dl { height: auto; min-height: 48px; padding: 8px 14px 8px 12px; gap: 10px; justify-content: flex-start; text-align: left; }
.ha-dl-text { display: flex; flex-direction: column; gap: 2px; }
.ha-dl-title { font: 500 13px/16px var(--ui); letter-spacing: -0.2px; }
.ha-dl-sub { font: 400 12px/15px var(--ui); letter-spacing: -0.1px; opacity: .62; }
@media (max-width: 599px) { .ha-btn.ha-dl { flex: 1 1 100%; } }
/* buttons, not links: no article underline */
.col-body article a.ha-btn, .col-body article a.ha-btn:hover { text-decoration: none; }
.col-body article a.ha-btn:focus-visible { outline: 2px solid var(--ink); outline-offset: 3px; }
.ha-dls { margin-bottom: 0; }

/* the post's width and the theme's accent (Ahmed, Nov 10): three rows as wide as the post; the first filled in
   --accent with --on-accent type, the others ruled and iconed in --accent-mark; focus in --ring */
.ha-dls { flex-direction: column; flex-wrap: nowrap; gap: 8px; }
.ha-btn.ha-dl { width: 100%; box-sizing: border-box; min-height: 52px; box-shadow: 0 0 0 1px var(--accent-mark); }
.ha-btn.ha-dl svg { color: var(--accent-mark); }
.ha-btn.ha-dl:hover { background: color-mix(in srgb, var(--accent) 8%, var(--paper)); }
.ha-btn.ha-dl.is-primary { background: var(--accent); color: var(--on-accent); box-shadow: 0 0 0 1px var(--accent); }
.ha-btn.ha-dl.is-primary svg { color: var(--on-accent); }
.ha-btn.ha-dl.is-primary:hover { background: color-mix(in srgb, var(--accent) 88%, var(--on-accent)); }
.ha-btn.ha-dl.is-primary .ha-dl-sub { opacity: .72; }
.col-body article a.ha-btn.ha-dl:focus-visible { outline-color: var(--ring); }
```


Source: `site/js/embeds/harness-actions.js`, whole file

```js
// ::harness-actions. The article's call to action, under "If you would like a design harness…":
// Download harness (the published harness as a zip, built by tools/build-harness-zip.py), Book time
// (the site's booking link), and Open in Claude / ChatGPT / Grok with the article as the prompt.
// Same language as the diagrams: 34px, 8px corners, 1px ink rule, the diagram ink filter.
import { BOOKING_URL } from '../content.js';

const CSS = 'css/embeds/harness-actions.css';
const ZIP = 'assets/downloads/salehdigital-design-harness.zip';
const STARTER = 'assets/downloads/design-harness-starter.zip';
const ARTICLE = 'https://saleh.digital/#/articles/what-is-a-design-harness';
const PROMPT = `Read Ahmed Saleh's article "What is a design harness?" at ${ARTICLE} and help me understand how a design harness works and how I could make my own.`;
const AI = [
  { key: 'claude', name: 'Claude', icon: 'assets/icons/brand/claude.svg', href: (q) => `https://claude.ai/new?q=${q}` },
  { key: 'chatgpt', name: 'ChatGPT', icon: 'assets/icons/brand/codex.svg', href: (q) => `https://chatgpt.com/?q=${q}` },
  { key: 'grok', name: 'Grok', icon: 'assets/icons/brand/grok.svg', href: (q) => `https://grok.com/?q=${q}` },
];
const ICON = {
  download: '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true"><path d="(icon path omitted: icon set is commercial)"/></svg>',
  calendar: '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true"><path d="(icon path omitted: icon set is commercial)"/></svg>',
};

export function mount(el) {
  if (!document.querySelector(`link[href="${CSS}"]`)) document.head.append(Object.assign(document.createElement('link'), { rel: 'stylesheet', href: CSS }));
  const h = (tag, cls, attrs = {}) => { const e = document.createElement(tag); if (cls) e.className = cls; Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v)); return e; };
  el.innerHTML = '';
  const row = h('div', 'ha-row');

  // two downloads (Ahmed, Nov 10): mine, to make sites like mine; and a starter, to make your own
  const dlRow = h('div', 'ha-dls');
  [{ href: ZIP, file: 'salehdigital-design-harness.zip', title: 'Download my harness', sub: 'If you want to make sites like mine', cls: 'is-primary' },
   { href: STARTER, file: 'design-harness-starter.zip', title: 'Download harness schema', sub: 'If you want to create your own harness', cls: '' }]
    .forEach(d => {
      const a = h('a', `ha-btn ha-dl ${d.cls}`.trim(), { href: d.href, download: d.file });
      a.innerHTML = `${ICON.download}<span class="ha-dl-text"><span class="ha-dl-title">${d.title}</span><span class="ha-dl-sub">${d.sub}</span></span>`;
      dlRow.append(a);
    });
  el.append(dlRow);

  const book = h('a', 'ha-btn', BOOKING_URL ? { href: BOOKING_URL, target: '_blank', rel: 'noopener' } : { href: '#/friends/say-hello' });
  book.className = 'ha-btn ha-dl';
  book.innerHTML = `${ICON.calendar}<span class="ha-dl-text"><span class="ha-dl-title">Book time</span><span class="ha-dl-sub">If you want help making your own harness</span></span>`;
  dlRow.append(book); // three full-width rows, each a title and its reason
  // Open in Claude / ChatGPT / Grok removed (Ahmed, Nov 10)
}
```


Rendered DOM on the live site at 1440 (captured 2026-11-11):

```html
<div class="embed embed-harness-actions" data-embed="harness-actions" data-stream-skip="">
 <div class="ha-dls">
  <a class="ha-btn ha-dl is-primary" download="salehdigital-design-harness.zip" href="assets/downloads/salehdigital-design-harness.zip">
   <svg aria-hidden="true" fill="currentColor" height="14" viewbox="0 0 24 24" width="14">
    <path d="(icon path omitted)">
    </path>
   </svg>
   <span class="ha-dl-text">
    <span class="ha-dl-title">
     Download my harness
    </span>
    <span class="ha-dl-sub">
     If you want to make sites like mine
    </span>
   </span>
  </a>
  <a class="ha-btn ha-dl" download="design-harness-starter.zip" href="assets/downloads/design-harness-starter.zip">
   <svg aria-hidden="true" fill="currentColor" height="14" viewbox="0 0 24 24" width="14">
    <path d="(icon path omitted)">
    </path>
   </svg>
   <span class="ha-dl-text">
    <span class="ha-dl-title">
     Download harness schema
    </span>
    <span class="ha-dl-sub">
     If you want to create your own harness
    </span>
   </span>
  </a>
  <a class="ha-btn ha-dl" href="https://cal.com/ahmed-saleh/30min" rel="noopener" target="_blank">
   <svg aria-hidden="true" fill="currentColor" height="14" viewbox="0 0 24 24" width="14">
    <path d="(icon path omitted)">
    </path>
   </svg>
   <span class="ha-dl-text">
    <span class="ha-dl-title">
     Book time
    </span>
    <span class="ha-dl-sub">
     If you want help making your own harness
    </span>
   </span>
  </a>
 </div>
</div>

```
