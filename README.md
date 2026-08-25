# Dotfiles

Personal dotfiles and agent configuration.

Currently includes Pi agent configuration under `pi/agent/`.

## Restore Pi config

From the repository root:

```bash
rsync -a pi/agent/ ~/.pi/agent/
```

Secrets and runtime state are intentionally not tracked. Re-authenticate with Pi after restoring if needed.
