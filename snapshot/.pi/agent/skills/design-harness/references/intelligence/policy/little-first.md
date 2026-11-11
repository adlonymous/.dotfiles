---
title: Little First
slug: little-first
status: published
description: Build the smallest version first, then grow.
chips:
  - Policy
  - Process
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

## Principle

Start with the smallest, simplest implementation that delivers value. Add complexity only when necessity proves it. Resist the urge to build for imagined future requirements.

## In Practice

**Build the minimum**:
- One component at a time, not full pattern libraries
- Essential features first, enhancements later
- Hardcode before abstracting

**Grow from usage**:
- Add props/variants when second real use case appears
- Generalize when third instance needs it
- Delete unused abstractions

**Prefer simple**:
- CSS before JS
- Static before dynamic
- Inline before extracted

## Examples

**Good**:
- Chip component starts with single style, add variants when needed
- Footer dot matrix uses canvas 2D, only move to WebGL if performance demands
- Theme switcher starts with two themes (light/dark), add marathon later

**Bad**:
- Build 12 chip variants before using one
- Abstract component system before writing three components
- Add theme engine for "future themes" when only using light mode

## Decision Tree

1. Can I hardcode this now? → Hardcode
2. Do I have two real use cases? → Maybe abstract
3. Do I have three? → Abstract with confidence

## Related

See `made-live.md` for shipping early and iterating in public. Both policies value incremental delivery over upfront perfection.
