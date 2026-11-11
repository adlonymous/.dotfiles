---
title: Memories
slug: memories
status: published
description: Project-specific facts and rules agents must remember.
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

# Memories Overview

Memories are project-specific facts, rules, and conventions that all agents must remember and follow. They encode decisions, constraints, and principles that might not be obvious from code or design alone.

## Active Memories

**16px Image Corners**: All article images have 16px border-radius (soft, tactile corners).

**Drafts Stay Private**: Draft content never appears in public views, search, or feeds.

**No Em-Dashes**: Type double-hyphen `--` instead of em-dash `—`.

**No Modals for Books**: Library opens book details in-place, not in modal overlays.

**Quiet Sound**: Sound effects are subtle, never jarring or loud.

**Single Green Check**: Show one green check mark after save, not persistent toggle checks.

## Purpose

Memories prevent agents from:
- Reinventing decisions that have already been made
- Violating established conventions
- Forgetting non-obvious rules

## Format

Each memory is a short, actionable rule with rationale. Agents reference memories before making related decisions.

## Maintenance

Add new memories when:
- A decision is made that agents might not infer
- A convention is established that differs from common practice
- A user preference is documented

## Related

See individual memory files in `memories/` directory and `policy/` for higher-level principles.
