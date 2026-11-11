---
title: Single Green Check
slug: single-green-check
status: published
description: Show one green check mark after save, not persistent toggles.
chips:
  - Memory
  - UI
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

## Memory

After a successful save action (settings, form submission, content update), show a single green check mark that appears briefly and then fades out. Do not leave persistent check marks on toggle controls.

## Rules

**Transient feedback**: Check mark appears for 1.5–2 seconds after save, then fades away.

**Location**: Show next to save button, or as inline confirmation near the changed field.

**Style**: Simple green check icon (✓), not a filled circle or badge.

**No persistent checks**: Toggle switches and checkboxes show their on/off state via position/color, not a persistent check mark overlay.

**One check per save**: Do not show multiple checks for batch updates -- one confirmation for the entire save operation.

## Implementation

```js
function showSaveConfirmation(element) {
  const check = document.createElement('span');
  check.className = 'save-check';
  check.textContent = '✓';
  check.style.color = 'var(--ok)'; // green
  
  element.appendChild(check);
  
  setTimeout(() => {
    check.style.opacity = '0';
    setTimeout(() => check.remove(), 300);
  }, 1500);
}
```

## CSS

```css
.save-check {
  display: inline-block;
  font-size: 18px;
  margin-left: 8px;
  color: var(--ok);
  opacity: 1;
  transition: opacity 0.3s var(--ease-land);
}
```

## Related

See `colors.md` for `--ok` (green) token value.
