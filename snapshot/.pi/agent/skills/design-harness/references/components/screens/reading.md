---
title: Reading
slug: reading
status: published
description: Article/post reading view.
chips:
  - Screen
  - Layout
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

The reading screen is the article page, and also the home page: `https://saleh.digital/` opens the newest article ("What is a design harness?") with Articles active. It uses the standard frame from `foundations/layout-grid.md`; there is no separate reading grid, no spine column and no visible post title.

## What is on screen at 1440 x 900

- x 24: the menu (Articles active, five rooms faded, a gap, Contact and Settings faded), first line at y 24.
- x 128: the section list, here a single item, the article title "What is a design harness?" at full ink.
- x 405 to 945: the post. It starts directly with its first `h2` ("Designing with agents", Inter Display 28/32) at the same top line as the menu, then Shinka 16/20.8 paragraphs 16px apart.
- Right of 945: empty (the media column, used only for image reveals).
- No footer in view; it comes after the end of the post.

## At 390 x 844

- The two-line menu glyph at the top left (x 12, y ~26).
- The article title in Inter Display 16px under it (y ~62).
- The post 28px lower: `h2` at 24/28, Shinka paragraphs at 16/20.8 across the full 366px width.

## Post content

The post body is a flex column (`gap: var(--para)`) of: `h2` and `h3` headings in Inter Display, `p` in Shinka, inline `.term` chips (dotted underline, see components/components/term.md), external links (thin solid underline at 28% ink), `em`, lists, blockquotes and full-width embeds such as the Before/After flow (components/patterns/harness-flow.md).

```css
.col-body article a { text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px;
  text-decoration-color: color-mix(in srgb, var(--ink) 28%, transparent); transition: text-decoration-color 160ms var(--ease-land); }
.col-body article a:hover, .col-body article a:focus-visible { text-decoration-color: currentColor; outline: none; }
.col-body :is(ul, ol) { margin: 0; padding: 0 0 0 20px; display: flex; flex-direction: column; gap: calc(var(--para) * 0.375); }
.col-body ul { list-style: "–"; }
.col-body li { padding-left: 6px; }
.col-body li::marker { font-family: var(--ui); font-size: 14px; color: var(--muted); }
.col-body blockquote { margin: 0; padding-left: 19px; box-shadow: inset 1px 0 0 color-mix(in srgb, var(--ink) 22%, transparent); font-style: italic;
  display: flex; flex-direction: column; gap: calc(var(--para) * 0.5); }
.col-body article > :not(.embed) { filter: url(#ink-body); }
```

Under the post there is an actions row (`aside.post-meta`) whose items are all `hidden` right now; it renders nothing.

The full page blueprint is `templates/article.md`.
