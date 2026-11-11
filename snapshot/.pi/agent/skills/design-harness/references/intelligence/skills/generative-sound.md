---
title: Generative Sound
slug: generative-sound
status: published
description: Implement subtle sound feedback for UI interactions.
chips:
  - Skill
  - Sound
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Procedure for implementing generative sound effects for UI interactions on Saleh Digital.

## Steps

**1. Choose Sound Characteristics**:
- Frequency: 200–800 Hz (warm, mid-range)
- Duration: 50–150ms (brief)
- Volume: 20–40% of max (subtle)
- Waveform: sine or triangle (soft, round)

**2. Generate Sound with Web Audio API**:
```js
const audioContext = new AudioContext();

function playTone(frequency, duration, volume = 0.3) {
  const oscillator = audioContext.createOscillator();
  const gainNode = audioContext.createGain();
  
  oscillator.connect(gainNode);
  gainNode.connect(audioContext.destination);
  
  oscillator.type = 'sine';
  oscillator.frequency.value = frequency;
  
  gainNode.gain.setValueAtTime(volume, audioContext.currentTime);
  gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
  
  oscillator.start(audioContext.currentTime);
  oscillator.stop(audioContext.currentTime + duration);
}
```

**3. Map Actions to Sounds**:
- Switch toggle: 400 Hz, 80ms
- Button click: 300 Hz, 60ms
- Save success: 500 Hz → 600 Hz (rising), 120ms
- Error: 250 Hz, 100ms (lower, duller tone)

**4. Respect User Preference**:
```js
const soundEnabled = localStorage.getItem('sound') !== 'off';

function playInteractionSound(frequency, duration) {
  if (soundEnabled) {
    playTone(frequency, duration);
  }
}
```

**5. Add Sound Toggle**:
- Provide on/off switch in settings or nav
- Persist choice in localStorage
- Default: on (but easily disabled)

## Sound Examples

```js
// Switch toggle
playInteractionSound(400, 80);

// Save success (two-tone)
playTone(500, 60);
setTimeout(() => playTone(600, 60), 60);
```

## Related

See `memories/quiet-sound.md` for sound design principles.
