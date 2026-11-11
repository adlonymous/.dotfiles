# Dotfiles

This PC (`lombaxPC`) is the source of truth for Pi and Herdr configuration. Capture its current setup here, review and push changes, then pull and apply them on the Mac or another PC. This is explicit one-way sync, not a daemon or a merge of both machines' preferences.

## What is shared

- Pi's instructions, settings, model definitions, MCP server definitions, keybindings, Zentui settings, prompts, themes, and local skills.
- Shared skills from `~/.agents/skills`, including the PDF creation skill.
- Herdr app settings, keys, and program launchers, the custom `wide-panels` layout, and the `files-astro`, `changes-readable`, `workspace-tickets`, `workspace-tabs`, and `workspace-agents` mods.
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

## Posting launcher

Herdr's `+` menu includes Posting through `.config/herdr-app/programs.json` (under the menu's built-in "Start an agent" heading). It opens a Posting terminal tab in the selected workspace. Install Posting separately on each workspace host; dotfiles syncs the launcher, not the executable. The entry is disabled when Posting is not installed on that host.

This PC uses the official Posting 3.0.0-beta.1 Linux binary in `~/.local/bin/posting`. See [Posting installation](https://github.com/darrenburns/posting#installation) for current platform instructions. On macOS, the documented beta install is `brew install darrenburns/homebrew/posting@beta`. Ensure `posting` is on the workspace host's PATH.

## Git and GitHub in Changes

Changes embeds the real Lazygit terminal UI. It is independent of Tickets. A Mac-local workspace runs Lazygit on the Mac; a PC workspace viewed from the Mac runs it on the PC. Git, files, GitHub CLI authentication, and existing repository hooks stay on that workspace's machine. Install Python 3.11+, Git, and Lazygit on every workspace host; install and authenticate `gh` there for GitHub repository creation. On the Mac, `brew install lazygit gh` installs those two tools. Linux integration was tested with Lazygit 0.65.1; actual Mac UI testing is still needed.

- Click Changes to attach a workspace-scoped Lazygit session. Reopening reuses the live session. Files/Changes/Tickets switching never creates a ticket or changes the active agent terminal.
- Use Lazygit for staging individual files or hunks, reviewing diffs, commits, branches, fetching, pulling, stashing, and history. Click Expand to give it the workspace area, then Collapse to restore the main terminal. Click inside Lazygit to give it the keyboard. `q` quits; Open Lazygit starts it again. Hidden Changes views do not start processes.
- New project creates a dedicated folder on the selected workspace's machine, initializes Git on `main` unless the folder belongs to a parent repository, and opens a workspace there. It adds README.md, self-updating AGENTS.md instructions, and an environment-file ignore rule. It refuses existing folders and Git's internal directories. Ordinary Herdr New space remains available for existing folders/home and does not initialize Git.
- After the first commit, a repository without remotes offers Create GitHub repository. Choose its owner, name, and public/private visibility explicitly. Description and homepage are optional. Creation adds `origin` but never pushes. The GitHub link opens on the viewing computer.

The embedded process merges the host's existing Lazygit config with a small owned policy: no automatic fetch/branch forwarding/conflict staging, no force push, and no commit-hook skipping shortcut or WIP-prefix bypass. Temporary, process-scoped hook forwarders reject recognizable staged secrets/environment files and pushes to `main`, `master`, or the remote's actual default branch. If the remote default cannot be verified, a branch push is refused. Existing hooks still run with their arguments/stdin; repository hook files and configuration are not changed. This is a client guardrail, not a security sandbox or a substitute for GitHub branch protection. Lazygit's own browser/editor commands execute on the workspace host; use the wrapper's GitHub link to open the repository on the Mac when viewing the PC remotely.

Lazygit sessions live in herdr-core, not Git or dotfiles. A screen-local terminal address is written into the owned layout's `git-terminal` viewport to embed it. Capture always replaces that address with its placeholder, so runtime IDs and remote machine names are not published. Applying or reopening Herdr attaches the live session again when Changes is opened. Exiting the app or hiding the panel does not kill a session another client may be using.

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

## Agents sidebar

The custom Agents sidebar uses industrial machine-module cards. Each session keeps one of six schematic markers across status/title changes, viewer restarts, and local/remote addressing. Markers are decorative identities, not inferred agent roles. Cards show the agent's actual name, project and machine, a shaped/labeled WORKING, NEEDS INPUT, or REPORT READY lamp, and reported activity. Without a report, terminal titles are labeled as such. State age comes from the core's status-change timestamp, not task progress; unknown times are omitted. A parent promoted by a sub-agent shows that child's report and state age. There is no continuous animation.

Agents remain grouped by machine. Within each machine, needs-input comes first, then unvisited done, then working, followed by a collapsible Idle section folded by default. Expand Idle to see the same session schematics with muted IDLE lamps. Machines containing only idle agents remain visible; empty machines and unknown agents stay hidden. Visiting a done agent acknowledges it through Herdr and moves it into Idle; REPORT READY does not accept a ticket. Active sub-agents keep their parent in the active queue and stay reachable by clicking their row.

Drag the sidebar edge to resize it. Cards wrap at intermediate widths, hide secondary text below 140 px, then become a schematic/status rail below 80 px. Hover for full metadata; click to focus the agent. Machine headings collapse their group and retain an attention indicator when folded. The local machine is labeled Local. Cards inherit the active layout's palette and fonts, including Aadil's Ramline when installed.

Update an existing Mac/Linux viewer without replacing its settings, keybindings, terminal dimensions, other mods, or Aadil/wide-panels geometry:

```sh
script/install-agent-cards          # preview
script/install-agent-cards --write  # back up and replace only the Agents files/block
```

The running app reloads the mod. The installer supports either or both existing Aadil/wide-panels layouts; it does not create a theme or replace another custom Agents view. Restore replaced files from the printed backup directory to undo. Actual Mac UI testing is still needed. Use this scoped installer, not a full apply, to retain newer native Git/theme changes from other feature branches.

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

## PC display reconnect diagnostics

For the PC's black-screen/cursor problem after powering its monitor off, install private logging and a recovery shortcut without changing GPU, locking, idle, or sleep settings:

```sh
script/install-display-diagnostics
script/install-display-diagnostics --write
systemctl --user daemon-reload
systemctl --user enable --now adlonymous-display-diagnostics.service
```

Reload Hyprland to register Super+Ctrl+F12. The shortcut captures display state, requests display power on, and reloads Hyprland's configuration. It does not close applications, terminate a lock, or restart the graphical session. If the compositor is unresponsive, the shortcut may not run. From a text login (Ctrl+Alt+F3) or an existing remote connection, run `~/.local/bin/adlonymous-display-diagnostics recover` instead. Recovery is an attempt, not a proven fix for the overnight failure.

Logs live under `${XDG_STATE_HOME:-~/.local/state}/display-diagnostics/`: display hotplug events, a 30-second heartbeat, connector state, window counts, and relevant kernel GPU/suspend messages. Window titles, command lines, event payloads, and screenshots are not collected. Files are private; the event log rotates at 5 MiB with two backups, and the latest 20 captures are retained. State is excluded from dotfiles sync. Captures made by the recovery command include before/after state and command results, not a claim that the screen visibly recovered.

To undo, disable the service with `systemctl --user disable --now adlonymous-display-diagnostics.service`, restore `binds.lua` and any pre-existing helper/service from the printed backup directory, and remove the installed helper/service if they were newly created. Run `systemctl --user daemon-reload` and reload Hyprland. Keep the runtime logs until diagnosis is finished.

## Checks and agent instructions

`script/check` runs Ruff through uvx, Oxlint 1.91.0 through npx for the owned panel JavaScript, Bash syntax checks, Python/Node tests, and snapshot path/JSON/credential checks. The tests cover Linux and macOS application, home-path expansion, dry-run safety, backups, idempotence, executable permissions, excluded runtime files, symlinks, path traversal, credential rejection, workspace routing, and the three ticket launch modes. When hc is installed, an integration test runs real herdr-core in temporary homes and named sessions with a fake Pi process. It checks all launch modes and a second core remotely creating and starting a ticket on the first; it makes no model calls and stops only those test cores. Git tests also cover safe project creation, explicit GitHub visibility, hook preservation, staged-secret checks, default-branch push guards, runtime-address exclusion, and client routing. With hc and Lazygit installed, two isolated cores run real local/remote Lazygit sessions, stage a selected file through keyboard input, verify session reuse, and quit. No GitHub repositories are created by tests. When herdr-app is installed, the check validates temporary copies of the Tickets, Changes, and workspace-tabs mods so generated files never enter the snapshot. No standalone typecheck is configured for these Python/JavaScript tools.

Project-specific instructions: [AGENTS.md](AGENTS.md).

References: [Herdr](https://github.com/herdrdev/herdr-app), [Pi](https://github.com/badlogic/pi-mono).
