# Dotfiles

This PC (`lombaxPC`) is the source of truth for Pi and Herdr configuration. Capture its current setup here, review and push changes, then pull and apply them on the Mac or another PC. This is explicit one-way sync, not a daemon or a merge of both machines' preferences.

## What is shared

- Pi's instructions, settings, model definitions, MCP server definitions, keybindings, Zentui settings, prompts, themes, and local skills.
- Shared skills from `~/.agents/skills`, including the PDF creation skill.
- Herdr app settings and keys, the custom `wide-panels` layout, and the `files-astro`, `changes-readable`, `workspace-tickets`, and `workspace-tabs` mods.
- A herdr-core `config.toml` if the source PC has one. The initial capture has none.

The snapshot contains configuration and source files, not installed applications or model weights. Source versions: Pi 1.5.0, Herdr app 0.1.13, herdr-core 0.1.17. Install compatible versions separately and open Herdr once before applying.

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

## Aadil theme

`wide-panels` is a layout, not a color theme: it arranges the sidebar, terminals, and shared Files / Changes / Tickets panel. Herdr 98 is another layout with its own look. Aadil is a separate, reversible themed copy of your existing wide-panels layout, inspired by [aadil.work](https://aadil.work): dark indigo panels, muted blue-violet chrome, soft-white text, silver borders, and warm orange accents. Red/green diffs and agent status colors stay distinct.

With Herdr running and wide-panels already installed:

```bash
script/install-aadil-theme          # preview only
script/install-aadil-theme --write  # create/update only the Aadil choice
herdr-app do layout.switch --name aadil
```

On first installation the native layout.clone command copies your existing layout and saved size choices. The updater changes the copy's paint and UI typeface, and installs themes/aadil.json, its layout-picker SVG preview, and the licensed Ramline 0.101 OTF pair. Existing Aadil geometry is preserved on subsequent updates. It never edits wide-panels, settings.json, keys, font sizes, terminal/code fonts, agents, or machine connections. Use this scoped updater rather than full apply on an existing Mac.

Return to the previous look at any time:

```bash
herdr-app do layout.switch --name wide-panels
```

The choice appears alongside the other layouts in Settings and the layout switcher. The palette applies to Herdr chrome and terminal ANSI colors on this screen; terminal programs that draw their own true-color interfaces can retain their own colors. The palette JSON is the color source of truth; run the updater after editing it to regenerate the layout's paint overrides. Ramline Light is used for UI body text and Heavy for weighted headings. The two fonts and their embedding/distribution permission notice are bundled under mods/aadil-fonts/fonts; no system-wide font installation is needed. Terminals and code diffs stay monospace because Ramline is proportional and has limited Latin coverage. No website images are installed. Linux screenshots verify Files, Changes, Tickets, and switching back; actual Mac UI testing remains needed.

## Git and GitHub in Changes

Changes is a native Herdr UI backed directly by Git and `gh`, not an embedded terminal or Lazygit backend. It is independent of Tickets. A Mac-local workspace executes on the Mac; a PC workspace viewed from the Mac executes on the PC. Install Python 3.11+ and Git on every workspace host, plus authenticated `gh` for GitHub creation. Lazygit is not required. Actual Mac UI testing is still needed.

- The repository comes from the workspace's first terminal folder, falling back to its configured folder. Keyboard focus and ticket selection do not change it. The panel shows the repository and machine explicitly.
- Use per-file +/− buttons to stage/unstage. Staged and unstaged versions have separate diff previews. Commit only includes staged files, preserves Git hooks, and retains your draft/error if a commit fails. Configure a missing commit identity locally through the panel.
- The branch menu creates branches or switches existing branches. Moving pending work to a new branch requires confirmation; switching existing branches requires a clean tree. No automatic stash, worktree, merge, or rebase.
- Fetch, fast-forward-only Pull, and Push each require a confirmation showing the destination. Push sends the reviewed commit, never forces, and refuses main/master/the remote's actual default branch. If the default cannot be verified, it fails closed.
- New project creates a dedicated folder on the selected machine, initializes Git on main unless it belongs to a parent repository, and opens a workspace there. It adds README.md, self-updating AGENTS.md instructions, and environment-file ignore rules. Existing folders and Git internals are refused. Ordinary Herdr New space remains unchanged.
- After the first commit, repositories without remotes offer Create GitHub repository. Choose owner, name, and public/private visibility explicitly. Creation adds origin but never pushes. Description/homepage are optional. Browser links open on the viewing computer, not the remote host.

Mutations reject stale repository/index previews and are serialized across clients with private locks under `$XDG_STATE_HOME/herdr-git/locks`. External Git clients do not share those locks. Recognizable staged secrets/environment files are refused before committing; this is a guardrail, not a substitute for review or server-side branch protection. Conflict resolution, history, stash management, and hunk-level staging are not in this first version.

On an existing Mac or PC, update only this panel without replacing keys, fonts, pane sizes, other mods, or other layout nodes:

```bash
script/install-git-panel          # preview
script/install-git-panel --write  # back up and update Changes only
```

This requires the existing wide-panels layout. It replaces the old embedded viewport with the native mod and backs up/removes its retired Lazygit policy. It creates no terminal processes and never writes runtime terminal IDs into layouts. Use this scoped updater for this feature instead of full apply on an existing Mac.

## Workspace tickets

The `wide-panels` layout includes `Files | Changes | Tickets` buttons in its top bar. They select views in the same right-hand panel, not separate columns. The custom `workspace-tabs` header is cloned from Herdr's shipped tabs mod so updates do not overwrite the Tickets button. It is Pi-native and does not install Shepherdr.

1. Select a workspace, click `+ New`, enter a title and description, and create the ticket.
2. Select the ticket and choose its conversation context:
   - Fresh starts a new interactive Pi session with the title and description as its prompt.
   - Fork starts a new Pi session from a saved conversation in the same workspace folder, then sends the ticket prompt. Use `/name` in Pi to make saved sessions recognizable. This version searches Pi's default `~/.pi/agent/sessions/` directory, not custom session directories.
   - Existing sends the prompt to a live, ready Pi terminal in the same folder (`idle` or `done` after a completed turn). Busy, blocked, and non-Pi programs are refused during preflight. The core's atomic idle guard is used for `idle`; core 0.1.17 has no equivalent `done` guard, so those use a normal, non-forcing send. Do not type into the selected agent simultaneously: a newly started turn could receive the ticket as follow-up input. A dialog is never forced through.
3. Click `Start ticket`, then `Open Pi terminal` to view the agent. New terminals are adopted into the workspace's active tab through Herdr's core labels.
4. Click `Mark done` when the work is finished. Idle does not mean done; marking a ticket done never kills its agent.

Ticket status and live agent status are shown separately; an agent reporting `done` means its turn finished, not that the ticket has been accepted. Fresh and forked sessions still share the workspace's files: this version creates no worktrees and allows one running ticket per workspace. This is not a lock against unrelated agents editing those files. There is no automatic completion, review, merge, session-history synchronization, or coordinator agent.

The panel sends helper requests through `exec(..., { on: space.machine })`, so a Mac viewing a PC workspace uses the PC's tickets, sessions, and core. The helper must be installed on both machines by applying this branch. It never copies a PC path into a Mac-local command. Ticket data is private runtime state under `$XDG_DATA_HOME/herdr-tickets/` (default `~/.local/share/herdr-tickets/`) on the workspace's machine and is not captured in dotfiles. Per-workspace file locks and atomic writes protect concurrent clients.

Click Tickets to open its view, or click it again to hide the shared panel. To select it explicitly, run on the machine displaying Herdr:

```bash
herdr-app do layout.select --stack panel-body --child tickets
herdr-app do layout.show --id panel
```

## macOS differences

Home paths are expanded to the destination machine's actual home directory; the snapshot uses `__DOTFILES_HOME__` instead of this PC's account path. On macOS the Linux Polkit guard is not installed, and the privilege section of Pi's instructions is replaced with a macOS instruction. Full apply still copies source-managed settings/keybindings and does not preserve existing Mac UI overrides. For this Git-panel update, use script/install-git-panel instead: it preserves both font settings and pane dimensions, plus existing keybindings.

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

`script/capture` is restricted to the source host named in `snapshot/manifest.json`, to avoid accidentally making the Mac the source. It discovers custom Herdr mods/layouts by excluding names in Herdr's installed-file manifest. For owned layouts it also captures same-name SVG previews and theme JSON files; shipped themes/previews and arbitrary theme directories are excluded. It captures no shipped mod even if it was edited in place: clone shipped mods before customizing them, as Herdr requires.

On another machine, inside its checkout:

```bash
git pull --ff-only
script/apply
script/apply --write
pi update --extensions
```

There is no background Git push, automatic pull, credential sync, live-session sync, or automatic deletion. The token scan is a guardrail, not proof that arbitrary future files are safe to publish. Review every capture before pushing this public repository. Git-backed Pi packages retain the source's existing package declarations and may follow upstream; caches are not a package lockfile.

## Checks and agent instructions

`script/check` runs Ruff through uvx, Oxlint 1.91.0 through npx for the owned panel JavaScript, Bash syntax checks, Python/Node tests, and snapshot path/JSON/credential checks. The tests cover Linux and macOS application, home-path expansion, dry-run safety, backups, idempotence, executable permissions, excluded runtime files, symlinks, path traversal, credential rejection, workspace routing, and the three ticket launch modes. When hc is installed, an integration test runs real herdr-core in temporary homes and named sessions with a fake Pi process. It checks all launch modes and a second core remotely creating and starting a ticket on the first; it makes no model calls and stops only those test cores. Git tests also cover safe project creation, explicit GitHub visibility, existing hooks, staged-secret checks, default-branch push guards, stale requests, and the scoped updater preserving Mac settings/layout geometry. With hc installed, two isolated cores run real local/remote Git mutations and push only feature branches to local bare remotes, without creating terminal processes. No GitHub repositories are created by tests. When herdr-app is installed, the check validates temporary copies of the Tickets, Changes, and workspace-tabs mods so generated files never enter the snapshot. No standalone typecheck is configured for these Python/JavaScript tools.

Project-specific instructions: [AGENTS.md](AGENTS.md).

References: [Herdr](https://github.com/herdrdev/herdr-app), [Pi](https://github.com/badlogic/pi-mono).
