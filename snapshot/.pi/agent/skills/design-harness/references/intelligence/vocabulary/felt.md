---
title: Felt
slug: felt
status: published
description: Tactile quality of interactions.
chips:
  - Interaction
  - Vocabulary
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

The tactile quality of user interactions -- how UI elements "feel" to use through timing, resistance, and feedback.

## Definition

**Felt** describes the sensory impression of interacting with UI elements: the weight of a slider, the snap of a toggle, the friction of a drag, the bounce of a spring animation. It is the interface's "hand-feel."

## Components of Felt

**Weight**: How heavy or light an element feels to move.
- Heavy: Long duration, strong easing, large mass
- Light: Short duration, gentle easing, small mass

**Resistance**: How much the element "pushes back" during interaction.
- High resistance: Stepped increments, magnetic snapping
- Low resistance: Smooth continuous motion

**Response**: How quickly the element reacts to input.
- Instant: Synchronous with touch/click
- Delayed: Brief lag for confirmation or processing

**Feedback**: Sensory confirmation of action (visual, audio, haptic).
- Visual: State change, animation, color shift
- Audio: Click, chime, whoosh
- Haptic: Vibration (mobile)

## Examples

**Switch toggle**:
- Weight: Medium (200ms transition)
- Resistance: Binary snap (no intermediate states)
- Response: Instant visual change
- Feedback: Track color + thumb position + optional sound

**Slider**:
- Weight: Light (thumb follows pointer smoothly)
- Resistance: Continuous, magnetic at endpoints
- Response: Real-time value update
- Feedback: Value label, optional sound on release

**Button press**:
- Weight: Light (scale down 2% on press)
- Resistance: None (instant press)
- Response: Immediate visual feedback
- Feedback: Scale transform + color shift + optional sound

## Tuning Felt

Adjust these tokens to change global "feel":
- `--fnd-energy`: Higher = snappier, shorter durations
- `--motion-resolve`: Base duration for state transitions
- `--ease-land` / `--ease-think`: Easing curves for weight

## Design Principle

"**Detail Over Decoration**" applies to felt: every timing, easing, and feedback detail must serve usability, not just aesthetics. Felt should be consistent, predictable, and intentional.

## Usage

When documenting interactions, describe:
1. What triggers the action
2. How it feels (weight, resistance, response)
3. What feedback is provided
4. How it resolves to rest

## Related

See `motion.md`, `sound.md`, and individual component specs for specific felt implementations.
