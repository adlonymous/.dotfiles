"""Update only Changes, leaving the viewing machine's keys, fonts, and layout sizes alone."""

import argparse
import json
import platform
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from tools.sync_config import ROOT, apply, target_path

MOD = ".config/herdr-app/mods/changes-readable"
LAYOUT = ".config/herdr-app/layouts/wide-panels.json"


def changes_node(node: dict):
    if node.get("id") == "changes":
        return node
    for child in node.get("children", []):
        found = changes_node(child)
        if found is not None:
            return found
    return None


def install_git_panel(home: Path, repo: Path, system: str, write: bool) -> list[str]:
    layout_path = target_path(home, LAYOUT)
    if not layout_path.is_file():
        raise ValueError("Install the wide-panels layout before updating Changes")
    tree = json.loads(layout_path.read_text())
    node = changes_node(tree)
    if node is None:
        raise ValueError("The wide-panels layout has no Changes view")
    node.pop("children", None)
    node["type"] = "block"
    node["content"] = {"mod": "changes-readable"}
    retired = target_path(home, MOD + "/lazygit.yml")
    if retired.exists() and not retired.is_file():
        raise ValueError("Expected the retired Lazygit policy to be a file")
    with tempfile.TemporaryDirectory() as temporary:
        staging = Path(temporary)
        entries = []
        for relative in [MOD + "/" + name for name in ("main.js", "git_backend.py", "git-context.mjs", "mod.json")] + [LAYOUT]:
            source = repo / "snapshot" / relative
            destination = staging / "snapshot" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(json.dumps(tree, indent=2) + "\n" if relative == LAYOUT else source.read_text())
            entries.append({"path": relative, "platform": "all", "mode": source.stat().st_mode & 0o777})
        (staging / "snapshot/manifest.json").write_text(json.dumps({"files": entries}))
        changes = apply(home, staging, system, write)
    if retired.exists():
        changes.append(MOD + "/lazygit.yml (remove retired policy)")
        if write:
            stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
            backup = target_path(home, f".local/state/dotfiles/backups/{stamp}/{MOD}/lazygit.yml")
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(retired, backup)
            retired.unlink()
            print(f"Retired policy backup: {backup}")
    return changes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    for relative in install_git_panel(Path.home(), ROOT, platform.system(), args.write):
        print(("Updated " if args.write else "Would update ") + relative)
    if not args.write:
        print("Preview only. Run script/install-git-panel --write to update Changes.")
