---
title: Debug Panel
slug: debug-panel
status: published
description: Runtime inspector for component state and tokens.
chips:
  - Tool
  - Dev
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Overlay debug panel for inspecting runtime state, theme tokens, component props, and feature flags during development.

## Features

**Theme Inspector**:
- Current theme and accent values
- Live token values (colors, spacing, motion)
- Foundation slider states (energy, texture, focus, density, etc.)

**Component Inspector**:
- Highlight component boundaries on hover
- Show component name, props, and state
- Inspect DOM structure and computed styles

**Feature Flags**:
- List all active feature flags
- Toggle flags on/off for testing

**Performance**:
- Frame rate meter
- Paint flash visualization
- Long-task detection

**Console Shortcuts**:
- Quick access to common debugging commands
- Log component tree, theme state, or DOM queries

## Keyboard Shortcut

`Cmd+Shift+D` (Mac) / `Ctrl+Shift+D` (Windows/Linux)

## UI

Draggable overlay panel with tabs:
1. Tokens
2. Components
3. Flags
4. Performance

## Styling

```css
.debug-panel {
  position: fixed;
  bottom: 20px;
  right: 20px;
  width: 360px;
  max-height: 480px;
  background: var(--paper);
  border: 1px solid var(--dot);
  border-radius: 8px;
  box-shadow: 0 8px 24px color-mix(in srgb, var(--shadow) 20%, transparent);
  overflow-y: auto;
  z-index: 9999;
  font-family: var(--mono);
  font-size: 12px;
}
```

## Usage

Dev only. Not included in production builds.
