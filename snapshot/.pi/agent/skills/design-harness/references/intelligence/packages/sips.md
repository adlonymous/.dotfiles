---
title: sips
slug: sips
status: published
description: macOS scriptable image processing system.
chips:
  - Package
  - Tooling
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

macOS built-in command-line tool for image format conversion, resizing, and optimization.

## Purpose

Used in build scripts or local tooling to process images (book covers, article images, screenshots) for the site.

## Common Operations

**Resize**:
```bash
sips -Z 800 input.jpg --out output.jpg
```

**Convert format**:
```bash
sips -s format png input.jpg --out output.png
```

**Get dimensions**:
```bash
sips -g pixelWidth -g pixelHeight image.jpg
```

**Optimize JPG quality**:
```bash
sips -s formatOptions 80 input.jpg --out output.jpg
```

## Usage in Build

```bash
# Resize all book covers to consistent width
for img in covers/*.jpg; do
  sips -Z 640 "$img" --out "covers/sized/$(basename $img)"
done
```

## Alternatives

- **ImageMagick**: Cross-platform, more features
- **Sharp** (Node.js): Programmatic image processing

sips is preferred on macOS for simplicity (no install required).

## Related

See build scripts for image processing automation.
