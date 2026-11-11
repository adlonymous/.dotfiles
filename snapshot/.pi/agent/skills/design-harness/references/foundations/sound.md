---
title: Sound
slug: sound
status: published
group: Foundations
order: 9
discuss: 0
created: 2026-11-09T19:23:22Z
updated: 2026-11-09T19:23:22Z
---

Sound is referenced but currently disabled on the site (hidden UI controls).

## Sound Toggle

A sound toggle button exists in the post-meta sidebar but is currently hidden:

```html
<button class="meta-ico" id="sound" type="button" aria-label="Sound" aria-pressed="true" hidden>
  <span class="ico" data-icon="soundOn" data-morph="ico-sound"></span>
</button>
```

To enable: remove `hidden` attribute.

## Philosophy

When implemented, sound would:
- Be subtle, optional, and off by default
- Provide tactile feedback for interactions (hover, click, transitions)
- Enhance the material/texture aesthetic
- Never autoplay or be intrusive
- Have a global toggle that persists across sessions

## Expected Implementation

**Interaction sounds:**
- Button press: subtle click/thud
- Hover: soft whoosh/breath
- Page transition: gentle swoosh
- Navigation: minimal tap

**Characteristics:**
- Short (50–200ms)
- Low volume (10–30%)
- Natural/organic timbres (paper, wood, fabric)
- Spatial positioning (left/right pan)

**Web Audio API:**
```javascript
const audioContext = new AudioContext();
// Load sound buffers
// Play on interaction with gain control
```

**Settings:**
- Global sound toggle in `/settings`
- Stored in `localStorage`
- Respects `prefers-reduced-motion`

## Current Status

Sound is currently disabled site-wide. The toggle UI exists but is hidden. No sound files are bundled.

## Do / Don't

**Do:**
- Make sound optional and off by default
- Use short, subtle samples
- Respect reduced-motion preference
- Provide global toggle

**Don't:**
- Autoplay any audio
- Use continuous background music
- Play on every interaction (reserve for key moments)
- Exceed 200ms duration
