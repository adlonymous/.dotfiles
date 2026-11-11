---
title: Three.js
slug: three-js
status: published
description: WebGL library for 3D graphics and shaders.
chips:
  - Package
  - WebGL
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

JavaScript library for creating 3D graphics and WebGL shaders in the browser. Potentially used for experimental 3D elements or advanced shader effects.

## License

MIT License -- free for personal and commercial use.

## Vendor

**Three.js Authors**
Website: https://threejs.org
GitHub: https://github.com/mrdoob/three.js

## Installation

```bash
npm install three
```

## Usage on Saleh Digital

Experimental: May be used for:
- 3D book covers in library (WebGL-rendered spines)
- Orb shader effects
- Particle systems or generative backgrounds
- Advanced shader work beyond canvas 2D

## Basic Scene Example

```js
import * as THREE from 'three';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Add objects, lights, etc.
```

## Performance

WebGL can be GPU-intensive. Test on mid-range devices and provide fallbacks for older browsers or devices without GPU acceleration.

## Related

See `tools/orb-bench.md` for shader performance testing and `skills/sdf-rendering.md` for SDF-based effects.
