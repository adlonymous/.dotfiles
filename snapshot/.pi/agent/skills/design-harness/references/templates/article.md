---
title: Article Template
slug: article
status: published
description: Article/post reading layout.
chips:
  - Template
  - Reading
created: 2026-11-11T15:03:00Z
updated: 2026-11-11T15:03:00Z
---

The article page (`/articles/:slug`, routed as `#/articles/:slug`). This is the blueprint an agent should follow to rebuild it. Everything below comes from the live site; every value is defined in the linked records.

## Build order

1. `<html lang="en" data-theme="light" class="has-nav-sheet" style="--col-nav: 80px; --col-sub: 253px;">` (or measure the columns, see foundations/layout-grid.md).
2. CSS, in this order: tokens (foundations/colors.md light block, foundations/spacing/spacing.md, foundations/motion/motion.md, foundations/typography/type.md stacks), `@font-face` (type.md), base + layout (foundations/layout-grid.md), navigation (components/patterns/navigation.md), body type and post blocks (components/screens/reading.md, type.md), terms (components/components/term.md), the flow embed (components/patterns/harness-flow.md), footer (components/patterns/footer.md), grain (foundations/materials/texture.md).
3. `<body>`: the ink-filter `<svg class="defs">` first (texture.md), then the skip link, then `.site` > `.cols` + `footer.foot`.
4. Scripts: grain, wordmark fit, flow wires (all small, in the records above).

## Skeleton

```html
<body>
  <svg class="defs" width="0" height="0" aria-hidden="true" focusable="false">…ink-ui, ink-bio, ink-diagram, ink-bas, ink-mark, ink-dots, ink-body…</svg>
  <a class="skip" href="#article">Skip to the writing</a>
  <div class="site">
    <div class="cols">
      <nav class="col col-nav" aria-label="Sections">
        <button type="button" class="nav-btn" aria-label="Menu" aria-expanded="false" aria-controls="nav-sheet"><span class="nav-btn-l"></span><span class="nav-btn-l"></span></button>
        <ul id="nav">…Articles (is-active) · Lectures · Speaking · Experiments · Library · Coffee table · [nav-step] Contact · Settings…</ul>
      </nav>
      <nav class="col col-sub" aria-label="In this section">
        <ul id="sub" aria-label="Articles"><li><a class="item is-active" aria-current="page" href="#/articles/what-is-a-design-harness">What is a design harness?</a></li></ul>
      </nav>
      <main class="col col-body" id="main">
        <article id="article" tabindex="-1">
          <h1 class="sr-only">What is a design harness?</h1>
          <h2>Designing with agents</h2>
          <p>…</p>
          <h2>What is a design harness?</h2>
          <p>A <button class="term" …>design harness</button> is … <a href="https://rubriclabs.com/blog/what-is-an-agent-harness" target="_blank" rel="noopener">"What is an Agent Harness?"</a> …</p>
          <h2>How does a design harness work?</h2>
          <div class="embed embed-harness-flow">…components/patterns/harness-flow.md…</div>
          <h2>Why build a design harness?</h2>
          <p>…</p>
        </article>
        <aside class="post-meta col-meta" aria-label="Actions"><!-- every action is hidden for now --></aside>
      </main>
      <aside class="col col-media" aria-hidden="true"></aside>
    </div>
    <footer class="foot">…components/patterns/footer.md…</footer>
  </div>
  <dialog id="nav-sheet" class="nav-sheet" aria-label="Menu">…</dialog>
</body>
```

```css
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); clip-path: inset(50%); white-space: nowrap; }
.skip { position: absolute; left: 24px; top: -40px; z-index: 20; background: var(--ink); color: var(--paper); padding: 6px 8px; }
.skip:focus { top: 8px; }
.defs { position: absolute; width: 0; height: 0; overflow: hidden; }
```

## Checks before you call it done (compare against the live page)

- At 1440 x 900: menu at x 24, section list at x 128, the first `h2` at x 405 on the same top line (y 24), body column 540px wide; Shinka 16/20 (measured before the 2026-11-11 sync; since then the column is 640px and the body 18/28.8 with −0.2px tracking, see [type](../foundations/typography/type.md#reading-size-since-2026-11-11), and the sub-nav carries the post's contents, see [contents](../components/patterns/toc.md)).8; the grain is visible as a faint speckle over the white; no footer in view.
- At 390 x 844: the two-line glyph top left, the article title under it, then the post; no row of menu links.
- Headings are Inter Display 28/32 (24/28 on phones), never bold.
- Terms have dotted underlines, the Rubric Labs link a solid faint one.
- The Before/After switch shows After pressed (black segment), with five outlined cards under it.
- The footer appears only after the end of the post, with the wordmark spanning the full window.

## Content

Use the post's real text. Keep the owner's punctuation and spelling as published (straight quotes, "realize", the em dash in "the way you work — instead of"). See foundations/writing for the voice.
