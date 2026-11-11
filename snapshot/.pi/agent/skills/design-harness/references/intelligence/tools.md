---
title: Tools
slug: tools
status: published
description: Developer tools and benches.
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

# Tools Overview

Developer tools and testing benches for performance tuning, visual debugging, and shader optimization on Saleh Digital.

## Available Tools

**Debug Panel**: Runtime inspector for component state, theme tokens, and feature flags. Overlay panel accessible via keyboard shortcut.

**CMS**: Content management system for creating, editing, and publishing articles, experiments, and library entries.

**Orb Bench**: Performance testing and tuning interface for the orb shader (if used in site experiments or animations).

**SDF Type Bench**: Signed-distance field type rendering test bench. Tune dot size, gap, threshold, and smoothing parameters for glyph matrix rendering.

**Wordmark Shader Bench**: Optimize the footer wordmark dot matrix shader. Test different SDF parameters, canvas sizes, and rendering performance.

## Tool Principles

1. **Dev-only**: Tools are only accessible in development builds or authenticated admin sessions. Never exposed to public users.

2. **Non-blocking**: Tools run in separate threads or deferred to idle time. They do not slow down the main UI.

3. **Persistent settings**: Tool configurations persist in localStorage for iterative tuning.

4. **Export results**: Benches can export performance metrics and settings as JSON for version control.

## Usage

Access tools via:
- Keyboard shortcuts (e.g., `Cmd+Shift+D` for debug panel)
- Admin menu (`/admin/tools`)
- URL routes (`/tools/sdf-type-bench`)

## Related

See individual tool files for full specifications.
