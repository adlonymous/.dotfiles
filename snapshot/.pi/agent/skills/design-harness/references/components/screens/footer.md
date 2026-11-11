---
title: Footer
slug: footer
status: published
description: Site-wide footer.
chips:
  - Screen
  - Layout
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

The footer screen is the bottom of every page: the bio line and the full-width wordmark. Its full spec (markup, CSS, the wordmark fit and the dot strips) is in `components/patterns/footer.md`; this record covers how it sits on the screen.

- **Desktop, short page** (a record page such as a lecture): the post ends high on the page, then empty paper, then the footer line and the wordmark pinned to the bottom of the window. At 1440 x 900 the bio line sits at about y 640 and the wordmark fills the last ~250px.
- **Desktop, long article:** the footer is below the last block of the post, after the 48px bottom padding of `.cols`. At the top of the page it is not visible at all.
- **Phone:** the same order; the bio wraps to two lines, the basmala under it, then the wordmark across the full width.

The live site keeps this behaviour by making `.site` a `min-height: 100svh` flex column with `.cols { flex: 1 }`. A pending change on the site (not yet live) also gives `.foot` a `min-height: 212px` so the line does not jump while the WebGL footer loads; the wordmark geometry is unchanged.

Theme: the footer uses `--foot` (ink in Paper and Night; the accent in Marathon).
