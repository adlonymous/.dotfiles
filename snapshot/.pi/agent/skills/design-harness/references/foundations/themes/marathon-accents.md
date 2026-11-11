---
title: Marathon accents
slug: marathon-accents
status: published
description: "The five accents (lime, cyan, red, amber, green) and the exact token each one overrides, per Marathon theme."
chips:
  - Theme
  - Marathon
  - Colour
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T15:59:05Z
---

`ACCENTS = ['lime', 'cyan', 'red', 'amber', 'green']`. The default is lime. An accent exists only with a Marathon theme: `data-accent` is removed for light and dark.

| Accent | marathon-dark (name) | marathon-dark overrides | marathon-light (name) | marathon-light overrides |
|---|---|---|---|---|
| lime | Acid | base: `--accent #c2fe0b`, `--signal #01ffff` | Sulphur | base: `--accent #c2fe0b`, `--accent-mark #587c00`, `--warm #8fbf00`, `--signal #ff0d1a` |
| cyan | Static | `--accent #01ffff; --signal #c2fe0b` | Glacier | `--accent #01ffff; --accent-mark #007f88; --warm #00b3bf` |
| red | Siren | `--accent #ff0d1a; --accent-text #ff4d55; --accent-mark #ff4d55; --ok #59b41d; --on-accent #fff` | Flare | `--accent #ff0d1a; --accent-wash #f88088; --accent-mark #e00012; --signal #fd6c1d; --warm #ff0d1a` |
| amber | Ember | `--accent #ffb000` | Honey | `--accent #ffb000; --accent-wash #ffd47a; --accent-mark #9a6200; --warm #e09a00` |
| green | Reactor | `--accent #59b41d` | Moss | `--accent #59b41d; --accent-wash #96cd74; --accent-mark #38801a; --warm #59b41d` |

In marathon-dark, `--accent-text`, `--accent-mark`, `--accent-wash`, `--glow`, `--ok` (except red), `--warm`, `--warm-halo` and `--foot` all follow `--accent`, so a one-line override recolours the footer, glow, highlights and checks together.

Storage: `localStorage['sd.theme'] = {"theme":"marathon-dark","accent":"cyan"}`. A preview URL is `?theme=marathon-light&accent=red`.
