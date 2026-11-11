---
title: Layout Grid
slug: layout-grid
status: published
description: One page frame for every room. Four grid columns on desktop (menu, section list, the 640px post, media), one stacked column below 900px.
chips:
  - Desktop 4 columns
  - Breakpoint 900
  - Post 640
  - Padding 24 / 24 / 48
created: 2026-11-11T15:03:00Z
updated: 2026-11-11T18:00:00Z
---

Every page on saleh.digital is the same frame. The values below are copied from the live `css/site.css` and `js/app.js`; use them as is.

## Page skeleton (order matters)

```html
<body>
  <svg class="defs" width="0" height="0" aria-hidden="true" focusable="false"><!-- ink filters, see materials/texture.md --></svg>
  <a class="skip" href="#article">Skip to the writing</a>
  <div class="site">
    <div class="cols">
      <nav class="col col-nav" aria-label="Sections">…menu, see components/patterns/navigation.md…</nav>
      <nav class="col col-sub" aria-label="In this section"><ul id="sub">…this room's pages…</ul></nav>
      <main class="col col-body" id="main">
        <article id="article" tabindex="-1">…the post…</article>
      </main>
      <aside class="col col-media" aria-hidden="true"></aside>
    </div>
    <footer class="foot">…see components/patterns/footer.md…</footer>
  </div>
  <!-- #grain is appended to <body> by script, see materials/texture.md -->
</body>
```

The footer is the last child of `.site`, never inside `.cols`. `.site` is a full-height flex column and `.cols` takes `flex: 1`, so on a short page (one record) the footer sits on the bottom edge of the window, and on a long post it comes after the last paragraph. It never floats mid-page.

## Desktop (900px and wider)

```css
*, *::before, *::after { box-sizing: border-box; }
html { background: var(--paper); color: var(--ink); -webkit-text-size-adjust: 100%; scrollbar-gutter: stable; }
body { margin: 0; font: 400 16px/16px var(--ui); letter-spacing: var(--track);
  -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale;
  text-rendering: geometricPrecision; font-kerning: normal; }
a { color: inherit; text-decoration: none; }
ul { list-style: none; margin: 0; padding: 0; }
p { margin: 0; }

.site { min-height: 100vh; min-height: 100svh; display: flex; flex-direction: column; }
.cols {
  flex: 1;
  display: grid;
  grid-template-columns: var(--col-nav, 89px) var(--col-sub, 248px) minmax(0, 640px) minmax(0, 1fr);   /* 540px until 2026-11-11 */
  column-gap: var(--gap);          /* 24px at the default density */
  align-items: start;
  padding: 24px 24px 48px;
}
.col ul { display: flex; flex-direction: column; gap: var(--stack); }   /* 4px */
.col-media { align-self: stretch; position: relative; contain: size layout; pointer-events: none; }
```

### Column widths are measured, not fixed

`--col-nav` and `--col-sub` are set on `<html>` by script so each column is exactly as wide as its longest label, and the three gaps read the same:

- `--col-nav` = the widest top-level menu label, measured with canvas `measureText` in `400 16px "Inter Display"` at `letterSpacing -0.64px`, rounded up. On the live site that is **80px** ("Coffee table").
- `--col-sub` = the widest page title over all rooms, capped at **264px**; per room it may grow up to `max(that, floor(innerWidth * 0.3))`. On the live site it is **253px** on every room at 1440 wide.
- `--sbw` = `innerWidth - document.documentElement.clientWidth` (the scrollbar), used only by wide embeds.

If you do not run the measuring script, hardcode `--col-nav: 80px; --col-sub: 253px;` on `<html>`. With the 24px padding and 24px gaps the post column then starts at x = 24 + 80 + 24 + 253 + 24 = **405px** and is **540px** wide (405 to 945) at any desktop width; the media column takes the rest.

### Wide embeds

Diagrams and the Before/After flow break out of the 640px column to the right:

```css
@media (min-width: 900px) {
  .col-body .embed-harness-diagram, .col-body .embed-harness-flow, .col-body .embed-harness-viewer, .col-body .embed-work-grid {
    max-width: none; align-self: flex-start;
    width: min(820px, calc(100vw - var(--sbw, 0px) - 48px - var(--col-nav, 89px) - var(--col-sub, 248px) - 2 * var(--gap)));
  }
  .col-body .embed-work-grid, .col-body .embed-harness-viewer { width: calc(100vw - var(--sbw, 0px) - 48px - var(--col-nav, 89px) - var(--col-sub, 248px) - 2 * var(--gap)); }
}
```

## Below 900px: one column

```css
@media (max-width: 899px) {
  .cols { display: flex; flex-direction: column; padding: 20px 12px 40px; gap: 0; }
  .col-nav ul { flex-direction: row; flex-wrap: wrap; column-gap: 12px; row-gap: 8px; }
  .col-sub { margin-top: 20px; }
  .col-sub ul { gap: 8px; }
  .col-sub .item { white-space: normal; }
  .col-body { margin-top: 28px; width: 100%; }
  .col-meta { margin-top: 28px; gap: 10px; }
  .item { padding: 2px 0; }
  .col-media { display: none; }
}
```

On a phone the top-level menu is not shown as a row: `<html>` carries `class="has-nav-sheet"`, which hides `#nav` and shows the two-line menu button instead (components/patterns/navigation.md). So a phone page reads, top to bottom: the menu glyph at the top left (x 12), the current page title 20px under it, the post 28px under that, the footer.

## Rooms that change the grid

- `html.is-solo` (Library, Experiments, Coffee table): `.col-sub { display: none; }`, the gallery spans from column 2.
- `html.is-gallery .cols { grid-template-columns: var(--col-nav, 89px) var(--col-sub, 248px) max-content minmax(0, 1fr); }`
- `html.is-slides` (Lectures with slides): body in row 1, the slide grid under it across columns 3 to 4.

## Related

`spacing/spacing.md` (the tokens), `components/patterns/navigation.md`, `components/patterns/footer.md`, `templates/article.md`.
