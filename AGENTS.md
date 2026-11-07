# Repository instructions

- This repo stores one-way configuration sync from the current PC (`lombaxPC`) to macOS/Linux. Do not merge destination preferences back into the source automatically.
- `snapshot/` mirrors the selected home-relative files. `snapshot/manifest.json` lists the managed paths, source host, modes, and platform applicability. `__DOTFILES_HOME__` expands only during apply.
- Run `script/capture` only on the source PC. The source allowlist is in `tools/sync_config.py`; do not replace it with a recursive home/config backup.
- Never commit credentials, auth files, session logs, sockets, package caches, model weights, or machine pairing. Model API keys must remain dummy values or environment references. Review and scan every capture before pushing this public repo.
- Apply defaults to a preview. `script/apply --write` backs up changed destination files and replaces only managed paths. Preserve unrelated files, reject symlinked targets, and never delete local credentials.
- Herdr's generated AGENTS.md, type definitions, shipped layouts/mods, and runtime state are not user-owned config. Capture only custom mods/layouts, discovered through installed.json. Run Herdr mod checks in temporary copies because the check writes generated files.
- On macOS, omit the Linux Polkit extension and render the platform-specific privilege instruction. Keep model endpoint limitations documented; never silently point a Mac's localhost at an imagined PC address.
- Python 3.11+ is required. `script/check` runs `script/lint` (Ruff through uvx and Bash syntax), `script/test` (unittest), and snapshot validation. No separate typecheck is configured.
- Captured Pi extensions and skills are source configuration, not application code for this repo's Python linter. Pi package caches and Herdr-managed integrations are reconstructed by their respective tools, not committed.
- Revise this AGENTS.md whenever meaningful changes affect managed files, capture/apply behavior, platform differences, dependencies, restore steps, or verification. README.md is the human-facing setup guide.
