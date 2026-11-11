---
title: Python Standard Library
slug: python-standard-library
status: published
description: Built-in Python modules for build scripts and tooling.
chips:
  - Package
  - Tooling
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Python's built-in standard library modules used in build scripts, image processing, and data generation for Saleh Digital.

## Common Modules

**pathlib**: File path manipulation
```python
from pathlib import Path
covers = Path('covers').glob('*.jpg')
```

**json**: JSON encoding/decoding
```python
import json
data = json.load(open('books.json'))
```

**subprocess**: Run shell commands
```python
import subprocess
subprocess.run(['sips', '-Z', '800', 'cover.jpg'])
```

**argparse**: Command-line argument parsing
```python
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
args = parser.parse_args()
```

## Usage

Build scripts (e.g., `scripts/process-covers.py`) use standard library for:
- Batch image resizing via sips
- JSON data generation for books/articles
- File organization and renaming
- Markdown parsing and transformation

## No External Dependencies

Prefer standard library over third-party packages for simple tasks (reduces build dependencies).

## Related

See `sips.md` for macOS image processing tool commonly invoked from Python scripts.
