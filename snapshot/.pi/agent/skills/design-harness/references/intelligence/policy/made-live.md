---
title: Made Live
slug: made-live
status: published
description: Build and test in production, iterate in public.
chips:
  - Policy
  - Process
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

## Principle

Build features in production, not in a staging vacuum. Ship early, iterate in public, and respond to real usage. Perfection is a process, not a prerequisite for launch.

## In Practice

**Ship early**:
- Launch features when minimally usable, not fully polished
- Iterate based on real user feedback and behavior
- Publish draft articles to see how they read in context

**No staging theater**:
- Staging environments diverge from production
- Edge cases only appear with real users and data
- "Works on staging" is not confidence; "works in production" is

**Iterate in public**:
- Fix bugs and refine based on live observations
- Update content and design continuously
- No "grand reveals" or version numbers

**Version control and rollback**:
- Use git and feature flags to manage risk
- Can roll back a broken deploy in minutes
- Deploy often, deploy small changes

## Examples

**Good**:
- Ship new chip component to one article, observe, refine, roll out
- Publish draft article as "published" and edit live based on re-reads
- Deploy footer dot matrix shader and tune parameters in production

**Bad**:
- Build entire feature set in staging for months before launch
- Wait for "perfect" state before shipping
- Hide work-in-progress behind auth until "ready"

## Exceptions

- Breaking changes: test thoroughly before deploy (database migrations, API changes)
- Sensitive content: review legal/privacy implications before publishing

## Related

See `little-first.md` for preference for small, incremental changes.
