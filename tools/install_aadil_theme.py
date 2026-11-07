"""Install a separate Aadil layout without replacing the viewer's existing UI preferences."""

import argparse
import json
import platform
import subprocess
import tempfile
from pathlib import Path

from tools.sync_config import ROOT, apply, target_path

APP = ".config/herdr-app"


def aadil_layout(layout: dict, palette: dict) -> dict:
    """Change only the cloned layout's paint, not its geometry, fonts, or mod references."""
    return {**layout, "theme": "aadil", "colors": palette["colors"], "preview": "layouts/aadil.svg"}


def install_aadil_theme(home: Path, repo: Path, system: str, write: bool) -> list[str]:
    source = target_path(home, APP + "/layouts/wide-panels.json")
    if not source.is_file():
        raise ValueError("Install wide-panels before adding the Aadil theme")
    destination = target_path(home, APP + "/layouts/aadil.json")
    palette_path = repo / "snapshot" / APP / "themes/aadil.json"
    palette = json.loads(palette_path.read_text())
    # Preflight every managed destination before asking the running app to clone.
    for relative in ("themes/aadil.json", "layouts/aadil.svg"):
        path = target_path(home, APP + "/" + relative)
        if path.exists() and not path.is_file():
            raise ValueError(f"Expected a file: {path}")
    if destination.exists() and not destination.is_file():
        raise ValueError(f"Expected a file: {destination}")
    fresh = not destination.exists()
    if fresh and write:
        subprocess.run(["herdr-app", "do", "layout.clone", "--name", "wide-panels", "--as", "aadil"],
                       check=True, capture_output=True, text=True, timeout=15)
    layout = json.loads((destination if destination.exists() else source).read_text())
    with tempfile.TemporaryDirectory() as temporary:
        staging = Path(temporary)
        entries = []
        for relative in ("themes/aadil.json", "layouts/aadil.svg", "layouts/aadil.json"):
            path = staging / "snapshot" / APP / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            text = json.dumps(aadil_layout(layout, palette), indent=2) + "\n" if relative == "layouts/aadil.json" else (repo / "snapshot" / APP / relative).read_text()
            path.write_text(text)
            entries.append({"path": APP + "/" + relative, "platform": "all", "mode": 0o644})
        (staging / "snapshot/manifest.json").write_text(json.dumps({"files": entries}))
        changes = apply(home, staging, system, write)
    return changes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    for relative in install_aadil_theme(Path.home(), ROOT, platform.system(), args.write):
        print(("Updated " if args.write else "Would update ") + relative)
    if not args.write:
        print("Preview only. Run script/install-aadil-theme --write with Herdr running.")
    else:
        print("Choose Aadil with: herdr-app do layout.switch --name aadil")
        print("Return with: herdr-app do layout.switch --name wide-panels")
