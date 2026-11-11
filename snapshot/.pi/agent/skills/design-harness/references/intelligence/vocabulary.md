---
title: Vocabulary
slug: vocabulary
status: published
description: Project-specific design and interaction terms.
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

# Vocabulary

Saleh Digital uses specific terms for design concepts, interactions, and interface states. This vocabulary creates a shared language across the harness, code, and agent communication.

## Core Terms

**Emergence**: The animation and stagger of elements appearing on page load. Orchestrated sequence of fades, translates, and scale transforms. See `vocabulary/emergence.md`.

**Resolve**: The transition from thinking/loading state to final rested state. Smooth deceleration. See `vocabulary/resolve.md` and `motion/resolve.md`.

**Felt**: The tactile quality of UI interactions -- weight, friction, response timing. How buttons, switches, and sliders "feel" to use. See `vocabulary/felt.md`.

**Spine**: Vertical metadata column in reading view with rotated text. Shows reading time, date, and type. See `components/components/spine.md`.

**Thinking**: Active processing state (loading, computing, generating). Shows spinner or shimmer. See `vocabulary/thinking.md`.

**Marathon**: High-contrast, high-energy theme mode for focus sessions. Available in light and dark variants with accent colors. See `themes/marathon-*.md`.

**Glyph Matrix**: SDF-based dot matrix text rendering for footer and wordmark. See `vocabulary/glyph-matrix.md`.

## UI Terms

**Chips**: Small rounded labels for categories, tags, or status. Non-interactive pills (vs buttons).

**Warm**: The gold/amber glow effect on emphasized words. Interactive hover state.

**Hot**: Active/on state for icon buttons (e.g., sound toggle when enabled).

**Peek**: Intermediate opacity state on hover (op-peek ~ 0.70).

**Faint**: Lowest opacity for meta text (op-faint ~ 0.32).

**Dots**: Low-opacity circles for dividers, backgrounds, and the SDF dot matrix.

## Layout Terms

**Cols**: The 4-column grid layout (nav, sub, content, margin).

**Para**: Paragraph-spacing token, scales with density.

**Gap**: Column and grid gap, scales with density.

**Stack**: Minimal vertical spacing (4px), for tight groups.

## Motion Terms

**Land**: Smooth deceleration easing (cubic-bezier(.2, 0, 0, 1)).

**Stagger**: Sequential delay between sibling animations (12ms default).

**VT**: View transition, browser-native page transition (Chrome/Edge).

## Texture Terms

**Ink**: SVG filter adding grain and displacement to text/UI.

**Grain**: Noise overlay for depth and paper texture.

**Glass**: Blurred background with semi-transparent foreground (modals, sheets).

## Usage

Always use these terms in harness documentation, code comments, and agent communication for consistency. Define new terms here when introducing new concepts.
