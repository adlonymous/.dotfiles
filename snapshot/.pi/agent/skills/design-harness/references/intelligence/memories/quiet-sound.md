---
title: Quiet Sound
slug: quiet-sound
status: published
description: Sound feedback is subtle, never jarring.
chips:
  - Memory
  - Sound
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

## Memory

Sound effects on Saleh Digital are subtle and non-intrusive. They provide gentle confirmation feedback without startling or annoying the user.

## Rules

**Volume**: Keep all sounds at low to moderate volume (typically 20–40% of maximum).

**Frequency**: Use soft, round tones -- avoid sharp, high-pitched, or harsh sounds.

**Duration**: Brief (50–200ms). No sustained tones or loops.

**Trigger**: Only on deliberate user actions (click, toggle, save). Never on automatic events (page load, timers, background updates).

**Opt-out**: Provide sound toggle in settings. Default: on, but easily disabled. Respect user preference persistently.

## Examples

**Good**:
- Soft "thock" on switch toggle (like a mechanical keyboard click, but quieter)
- Gentle chime on successful save
- Subtle whoosh on page transition

**Bad**:
- Loud beep or bell
- Notification ding on background events
- Continuous background music or ambient sound
- High-pitched tones

## Implementation

Use Web Audio API with gain nodes for volume control:
```js
const audioContext = new AudioContext();
const gainNode = audioContext.createGain();
gainNode.gain.value = 0.3; // 30% volume
```

Store sound preference in localStorage:
```js
const soundEnabled = localStorage.getItem('sound') !== 'off';
```

## Related

See `sound.md` for full sound system specification.
