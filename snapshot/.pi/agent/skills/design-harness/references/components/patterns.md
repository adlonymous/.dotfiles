---
title: Patterns
slug: patterns
status: published
description: Composed component patterns.
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

# Patterns Overview

Multi-component patterns that compose atomic components into meaningful UI structures.

## Library Patterns

**Bookshelf**: Grid of book covers with title/author. Compact, high-density layout for browsing large collections.

**Coffee Table**: Featured books grid with larger covers and excerpt text. Highlights currently reading or noteworthy books.

## Content Patterns

**Carousel**: Horizontal scrolling gallery for images or project previews. Snap-scroll with navigation arrows.

**Post Actions**: Meta action buttons row at end of articles (discuss, copy link, sound toggle).

**Record Card**: Design harness record display in Catalogue view. Shows title, description, status chips, file path.

## Settings Patterns

**Settings Row**: Label, description, and control (switch/slider/picker) in a horizontal row. Used in `/settings` view.

## Screen Patterns

**Reading**: Full article layout with 4-column grid (nav, spine, content, margin).

**Footer**: Site-wide footer with bio, dot matrix, basmala, and wordmark.

## Pattern Principles

1. **Composition over inheritance**: Patterns compose primitives, don't extend them
2. **Single responsibility**: Each pattern serves one clear use case
3. **Responsive**: Adapt layout to viewport width
4. **Grid-first**: Use CSS Grid for structure where appropriate
5. **Gap tokens**: Use `--gap`, `--para`, `--stack` for consistent spacing
6. **Theme-aware**: Inherit colors and tokens from global theme
7. **Accessible**: Maintain semantic structure and keyboard navigation
