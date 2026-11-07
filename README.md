# Dotfiles

This PC (`lombaxPC`) is the source of truth for Pi and Herdr configuration. Capture its current setup here, review and push changes, then pull and apply them on the Mac or another PC. This is explicit one-way sync, not a daemon or a merge of both machines' preferences.

## What is shared

- Pi's instructions, settings, model definitions, MCP server definitions, keybindings, Zentui settings, prompts, themes, and local skills.
- Shared skills from `~/.agents/skills`, including the PDF creation skill.
- Herdr app settings and keys, the custom `wide-panels` layout, and the `files-astro` and `changes-readable` panels.
- A herdr-core `config.toml` if the source PC has one. The initial capture has none.

The snapshot contains configuration and source files, not installed applications or model weights. Source versions when set up: Pi 1.5.0, Herdr app 0.1.12, herdr-core 0.1.17. Install compatible versions separately and open Herdr once before applying.

Credentials, authentication tokens, session history, SSH/machine pairing, package caches, Herdr window/session state, generated type files, and shipped Herdr layouts/mods are not copied. Herdr's generated legacy `herdr-agent-state.ts` integration is also excluded: the installed Herdr/Pi versions must provide their own integration.

## Apply on another machine

Requires Python 3.11+, Git, Pi, and the Herdr app/core. GitHub CLI is used in the clone example. For checks, install `uv` so `script/lint` can run Ruff. No Python application dependencies are required.

Keep the canonical bare-repo/worktree layout:

```bash
mkdir -p ~/Projects/dotfiles
cd ~/Projects/dotfiles
gh repo clone adlonymous/.dotfiles .bare -- --bare
printf '%s\n' 'gitdir: ./.bare' > .git
git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
git config core.logAllRefUpdates true
git config worktree.useRelativePaths true
git fetch origin
git worktree add sync -b sync-herdr-pi origin/feat/sync-herdr-pi
cd sync
script/apply                # preview changes only
script/apply --write        # apply with backups
pi update --extensions     # fetch the packages declared in Pi's settings
```

Restart Pi or use `/reload`. Herdr hot-reloads configuration; select the custom layout in its command palette or run this in a terminal on the Mac:

```bash
herdr-app do layout.switch --name wide-panels
```

The selected layout is screen-local state and is deliberately not copied. Your existing Mac-to-PC connection and spaces remain intact. Connect the PC through Herdr's Machines settings if the Mac has not been paired yet.

Changed files are backed up under `~/.local/state/dotfiles/backups/<timestamp>/`, preserving their home-relative paths and permissions. Applying the same snapshot twice is a no-op. Only managed files are replaced: unrelated local files, including other extensions and mods, are not deleted. Symlinked destinations are refused before any files are changed. Review the preview and resolve those links explicitly rather than forcing through them.

## macOS differences

Home paths are expanded to the destination machine's actual home directory; the snapshot uses `__DOTFILES_HOME__` instead of this PC's account path. On macOS the Linux Polkit guard is not installed, and the privilege section of Pi's instructions is replaced with a macOS instruction. Other preferences and keybindings stay as configured on the PC, including the Ctrl-based Herdr keys.

The Herdr UI uses Noto Sans Mono. Install that font on the Mac for the same typography. Executables named by settings and skills (`nvim`, `gh`, Parallel CLI, Poppler, and others) are separate prerequisites; copying a skill does not install its tools. The PDF skill points to `~/Projects/Aadil/pdf-workshop`, so that project must be copied separately to generate PDFs locally on the Mac, or used in Pi on the PC.

Pi's copied default is the PC's Bonsai provider at `http://127.0.0.1:8090/v1`; Ollama is configured at `http://127.0.0.1:11434/v1`. When Pi itself runs on the PC through Herdr, these keep working unchanged. When Pi runs locally on the Mac, those loopback addresses mean the Mac. To use the PC servers, keep this SSH tunnel running on the Mac, substituting its existing SSH host alias:

```bash
ssh -N -o ExitOnForwardFailure=yes -L 8090:127.0.0.1:8090 -L 11434:127.0.0.1:11434 YOUR_PC_SSH_ALIAS
```

Alternatively choose a provider through Pi's `/login` and `/model`, or change the local model endpoints. Credentials remain local on each machine. A subsequent apply restores source-managed preferences, so capture permanent preference changes on the PC instead.

## Update from the source PC

```bash
cd ~/Projects/Aadil/dotfiles/sync-herdr-pi
script/capture
script/check
git diff
# Review, scan for secrets, then commit and push this feature branch.
```

`script/capture` is restricted to the source host named in `snapshot/manifest.json`, to avoid accidentally making the Mac the source. It discovers custom Herdr mods/layouts by excluding names in Herdr's installed-file manifest. It captures no shipped mod even if it was edited in place: clone shipped mods before customizing them, as Herdr requires.

On another machine, inside its checkout:

```bash
git pull --ff-only
script/apply
script/apply --write
pi update --extensions
```

There is no background Git push, automatic pull, credential sync, live-session sync, or automatic deletion. The token scan is a guardrail, not proof that arbitrary future files are safe to publish. Review every capture before pushing this public repository. Git-backed Pi packages retain the source's existing package declarations and may follow upstream; caches are not a package lockfile.

## Checks and agent instructions

`script/check` runs Ruff, Bash syntax checks, standard-library unit tests, and snapshot path/JSON/credential checks. The tests cover Linux and macOS application, home-path expansion, dry-run safety, backups, idempotence, executable permissions, excluded runtime files, symlinks, path traversal, and credential rejection. No standalone typecheck is configured for these Python tools.

Project-specific instructions: [AGENTS.md](AGENTS.md).

References: [Herdr](https://github.com/herdrdev/herdr-app), [Pi](https://github.com/badlogic/pi-mono).
