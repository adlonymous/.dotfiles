"""Preview/install PC-only display diagnostics without changing power or GPU settings."""

import argparse
import json
import platform
import tempfile
from pathlib import Path

from tools.sync_config import ROOT, apply, target_path

BIND_PATH = ".config/hypr/config/binds.lua"
HELPER_PATH = ".local/bin/adlonymous-display-diagnostics"
SERVICE_PATH = ".config/systemd/user/adlonymous-display-diagnostics.service"
BINDING = '''-- BEGIN ADLONYMOUS DISPLAY DIAGNOSTICS
hl.bind("SUPER + CTRL + F12", hl.dsp.exec_cmd('\"$HOME/.local/bin/adlonymous-display-diagnostics\" recover'), { locked = true })
-- END ADLONYMOUS DISPLAY DIAGNOSTICS
'''
SERVICE = '''[Unit]
Description=Private display reconnect diagnostics
PartOf=graphical-session.target
After=graphical-session.target

[Service]
ExecStart=%h/.local/bin/adlonymous-display-diagnostics watch
Restart=on-failure
RestartSec=5
UMask=0077

[Install]
WantedBy=graphical-session.target
'''


def install_display_diagnostics(home: Path, repo: Path, system: str, write: bool) -> list[str]:
    """Back up only an existing keybinding file/helper/service; preserve all other configuration."""
    if system != "Linux":
        raise ValueError("Display diagnostics require Linux and Hyprland")
    path = target_path(home, BIND_PATH)
    original = path.read_text()
    if BINDING in original:
        binds = original
    else:
        if "SUPER + CTRL + F12" in original or "ADLONYMOUS DISPLAY DIAGNOSTICS" in original:
            raise ValueError("Display recovery shortcut conflicts with existing bindings; review manually")
        binds = original.rstrip() + "\n\n" + BINDING
    files = {
        HELPER_PATH: ((repo / "tools/display_diagnostics.py").read_text(), 0o755),
        SERVICE_PATH: (SERVICE, 0o644),
        BIND_PATH: (binds, path.stat().st_mode & 0o777),
    }
    with tempfile.TemporaryDirectory() as temporary:
        staging = Path(temporary)
        entries = []
        for relative, (text, mode) in files.items():
            destination = staging / "snapshot" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(text)
            entries.append({"path": relative, "platform": "Linux", "mode": mode})
        (staging / "snapshot/manifest.json").write_text(json.dumps({"files": entries}))
        return apply(home, staging, system, write)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    for relative in install_display_diagnostics(Path.home(), ROOT, platform.system(), args.write):
        print(("Updated " if args.write else "Would update ") + relative)
    print("After installing: systemctl --user daemon-reload && systemctl --user enable --now adlonymous-display-diagnostics.service")
    print("Reload Hyprland to register Super+Ctrl+F12. Restore the printed backups to undo existing-file changes.")
    if not args.write:
        print("Preview only. Use script/install-display-diagnostics --write to install.")
