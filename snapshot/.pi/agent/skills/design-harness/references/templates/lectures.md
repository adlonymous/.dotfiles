---
title: Lectures
slug: lectures
status: published
description: "Lectures (and Speaking): a talk page is a plain record (title, then one quiet data line), its intro text, then its slides in a 2-column 16:9 grid across the free width."
chips:
  - Template
  - Lectures
  - Slides
created: 2026-11-11T16:10:00Z
updated: 2026-11-11T16:10:14Z
---

Route: `#/lectures/<item>`. The sub-nav lists the lecture pages (live: "Philosophy of design", "Lead UX and Product Design Instructor"). Speaking (`#/talks`) uses the same template ([speaking](speaking.md)).

The menu at every page (live, 2026-11-11, after that day's site sync): **Welcome, Articles, Lectures, Speaking, Experiments, Library, Coffee table**, a paragraph step, then **Theme, Sound, MCP**. There is one menu entry per room (`js/rooms.js`); Theme, Sound and MCP are app pages, not CMS sections. See [navigation](../components/patterns/navigation.md).

The page has `html.is-slides` when the page has media:

1. **The title and data line,** as a plain record (`.records.is-plain`). The title is `.rec-title`. The data line is `.rec-meta`, Inter Display 14/20, tracking -0.2px, in `--muted`, with `·` separators at .6. Its fields are kind · role · venue · place · date, for example "Lecture · Lecturer and host · Studio 535 · Toronto, ON · Oct 22, 2024".
2. **The intro text** (serif body), streamed.
3. **The slides:** the page's media, in order, in `.masonry.slides`, a 2-column grid of 16:9 frames with a 10px gap (8px on a phone). They sit under the text across the free width (`grid-column: 3 / -1`, 40px above; 28px on a phone), and the menus run down beside both rows. Tapping a slide steps through them full screen from there ([viewer](../components/patterns/viewer.md)). The live Philosophy of design page has 92 slides.

Source: `site/css/site.css`, lines 553 to 568

```css
/* a talk (Presentations): its text where it always is, then its slides under it across the free width,
   a 2-column grid of 16:9 frames with the masonry's gap. The menus run down beside both rows. */
html.is-slides .cols { grid-template-rows: auto 1fr; }
html.is-slides .col-nav { grid-column: 1; grid-row: 1 / span 2; }
html.is-slides .col-sub { grid-column: 2; grid-row: 1 / span 2; }
html.is-slides .col-body { grid-column: 3; grid-row: 1; }
html.is-slides .col-media { grid-column: 4; grid-row: 1; }
html.is-slides .col-gallery { grid-column: 3 / -1; grid-row: 2; margin-top: 40px; }
.masonry.slides { columns: auto; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.slides .masonry-cell { margin: 0; aspect-ratio: 16 / 9; }
.slides .masonry-img { width: 100%; height: 100%; object-fit: cover; }
@media (max-width: 899px) {
  html.is-slides .col-gallery { margin-top: 28px; }
  .masonry.slides { gap: 8px; }
}
```


```html
<article id="article" data-morph-lines="body" tabindex="-1">
  <h1 class="sr-only">Philosophy of design</h1>
  <div class="records is-plain"><div class="record"><div class="rec-body">
    <div class="rec-title">Philosophy of Design</div>
    <p class="rec-meta"><span>Lecture</span><span class="rec-sep" aria-hidden="true">·</span><span>Lecturer and host</span><span class="rec-sep" aria-hidden="true">·</span><span>Studio 535</span><span class="rec-sep" aria-hidden="true">·</span><span>Toronto, ON</span><span class="rec-sep" aria-hidden="true">·</span><span>Oct 22, 2024</span></p>
  </div></div></div>
  <p>A talk on what design is for when the material can think: taste as infrastructure, authorship over output, and why the craft moves up a level instead of disappearing.</p>
</article>
<section class="col col-gallery" aria-label="Frames">
  <div class="masonry slides"><figure class="masonry-cell"><img class="masonry-img" alt="…" src="…"></figure>…</div>
</section>
```

The record template ([record](record.md)) covers the same columns for the page without slides.
