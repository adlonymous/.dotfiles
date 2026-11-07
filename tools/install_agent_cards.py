"""Update only Agents cards, preserving the viewer's theme, keys, and layout sizes."""

import argparse
import json
import platform
import tempfile
from pathlib import Path

from tools.sync_config import ROOT, apply, target_path

MOD = ".config/herdr-app/mods/workspace-agents"
LAYOUTS = [f".config/herdr-app/layouts/{name}.json" for name in ("wide-panels", "aadil")]


def agents_node(node: dict):
    if node.get("id") == "agents":
        return node
    for child in node.get("children", []):
        found = agents_node(child)
        if found is not None:
            return found
    return None


def install_agent_cards(home: Path, repo: Path, system: str, write: bool) -> list[str]:
    layouts = {}
    for relative in LAYOUTS:
        path = target_path(home, relative)
        if not path.is_file():
            continue
        original = path.read_text()
        tree = json.loads(original)
        node = agents_node(tree)
        if node is None or node.get("type") != "block" or node.get("content", {}).get("mod") not in {"agents", "workspace-agents"}:
            raise ValueError(f"Expected an Agents block in {path.name}; refusing to replace a custom view")
        content = {"mod": "workspace-agents"}
        if node["content"] != content:
            node["content"] = content
            layouts[relative] = json.dumps(tree, indent=2) + "\n"
        else:
            layouts[relative] = original
    if not layouts:
        raise ValueError("Install wide-panels or Aadil before updating Agents")
    # Assets and imported helpers go first so a running viewer can reload main.js last.
    assets = sorted((repo / "snapshot" / MOD / "schematics").glob("*.svg"))
    paths = [str(path.relative_to(repo / "snapshot")) for path in assets]
    paths += [MOD + "/" + name for name in ("agent-card.js", "agent-groups.js", "mod.json", "main.js")]
    with tempfile.TemporaryDirectory() as temporary:
        staging = Path(temporary)
        entries = []
        for relative in paths + list(layouts):
            source = repo / "snapshot" / relative
            destination = staging / "snapshot" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(layouts[relative] if relative in layouts else source.read_text())
            entries.append({"path": relative, "platform": "all", "mode": 0o644})
        (staging / "snapshot/manifest.json").write_text(json.dumps({"files": entries}))
        return apply(home, staging, system, write)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    for relative in install_agent_cards(Path.home(), ROOT, platform.system(), args.write):
        print(("Updated " if args.write else "Would update ") + relative)
    if not args.write:
        print("Preview only. Run script/install-agent-cards --write to update Agents.")
