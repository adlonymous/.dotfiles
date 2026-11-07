#!/usr/bin/env python3
"""Capture this PC's portable configuration and apply it without runtime state."""

import argparse
import json
import os
import platform
import re
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME_TOKEN = "__DOTFILES_HOME__"
SKIP_PARTS = {".git", "node_modules", "__pycache__", ".DS_Store"}
SECRET_PATTERNS = (
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    r"\b(?:ghp_|github_pat_|sk-proj-|sk-ant-)[A-Za-z0-9_-]{20,}",
    r"\bAKIA[A-Z0-9]{16}\b",
)


def check_secrets(text: str, name: str) -> None:
    """Reject recognizable private keys and tokens without printing their values."""
    if any(re.search(pattern, text) for pattern in SECRET_PATTERNS):
        raise ValueError(f"Possible credential in {name}; refusing to copy it")
    for key, value in re.findall(
        r'"(apiKey|api_key|password|authorization|access_token|client_secret)"\s*:\s*"([^"\n]*)"',
        text,
        re.IGNORECASE,
    ):
        if (value and value not in {"ollama", "local", "none", "dummy", "unused", "bonsai"}
                and not re.match(r"\$|!|<|YOUR_|your_|process\.env|os\.environ", value)):
            raise ValueError(f"Review literal {key} in {name}; refusing to copy it")


def portable_text(path: Path, home: Path) -> str:
    """Replace only the source home path, leaving model IDs and preferences intact."""
    text = path.read_text()
    check_secrets(text, str(path.relative_to(home)))
    return text.replace(str(home), HOME_TOKEN)


def source_files(home: Path):
    """Yield an allowlist of portable files and the Linux-only Polkit extension."""
    for name in (
        "AGENTS.md", "settings.json", "keybindings.json", "mcp.jsonc", "models.json", "zentui.json"
    ):
        path = home / ".pi/agent" / name
        if path.is_file():
            yield path, "all"
    for folder in (".pi/agent/prompts", ".pi/agent/themes", ".pi/agent/skills", ".agents/skills"):
        root = home / folder
        if root.exists():
            for path in sorted(root.rglob("*")):
                if any(part in SKIP_PARTS for part in path.relative_to(root).parts):
                    continue
                if path.name.startswith(".env") or path.suffix == ".pyc":
                    continue
                if path.is_symlink():
                    raise ValueError(f"Review skill/resource symlink before capture: {path}")
                if path.is_file():
                    yield path, "all"
    extension = home / ".pi/agent/extensions/polkit-sudo-guard.ts"
    if extension.is_file():
        yield extension, "Linux"
    app = home / ".config/herdr-app"
    for name in ("settings.json", "keys.json", "programs.json"):
        path = app / name
        if path.is_file():
            yield path, "all"
    installed = json.loads((app / "installed.json").read_text())
    for path in sorted((app / "layouts").glob("*.json")):
        if f"layout:{path.stem}" not in installed:
            yield path, "all"
    for mod in sorted((app / "mods").iterdir()):
        if mod.is_dir() and mod.name not in installed:
            for path in sorted(mod.rglob("*")):
                if any(part in SKIP_PARTS for part in path.relative_to(mod).parts):
                    continue
                if path.suffix == ".pyc" or path.name.startswith(".env"):
                    continue
                if path.is_file() and path.name not in {"jsconfig.json", "gpui-kit.d.ts", "herdr.d.ts"}:
                    yield path, "all"
    core = home / ".config/herdr-core/config.toml"
    if core.is_file():
        yield core, "all"


def capture(home: Path, repo: Path) -> int:
    """Build the entire snapshot before replacing the repository's previous copy."""
    files = list(source_files(home))
    with tempfile.TemporaryDirectory(dir=repo, prefix=".capture-") as temporary:
        staged = Path(temporary) / "snapshot"
        staged.mkdir()
        entries = []
        for source, system in files:
            if source.is_symlink():
                raise ValueError(f"Refusing source symlink: {source}")
            relative = source.relative_to(home)
            destination = staged / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(portable_text(source, home))
            mode = source.stat().st_mode & 0o777
            destination.chmod(mode)
            entries.append({"path": relative.as_posix(), "platform": system, "mode": mode})
        manifest = {
            "source_host": platform.node(),
            "source_platform": platform.system(),
            "captured_at": datetime.now(UTC).isoformat(),
            "files": entries,
        }
        (staged / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        previous = repo / "snapshot"
        if previous.exists():
            shutil.rmtree(previous)
        shutil.move(staged, previous)
    return len(entries)


def target_path(home: Path, relative: str) -> Path:
    """Reject traversal and symlinked targets before touching a destination."""
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"Invalid managed path: {relative}")
    destination = home / path
    for parent in (destination, *destination.parents):
        if parent == home:
            break
        if parent.is_symlink():
            raise ValueError(f"Refusing destination symlink: {parent}")
    return destination


def render_file(text: str, relative: str, home: Path, system: str) -> str:
    """Expand home paths and use a macOS-specific privilege instruction."""
    text = text.replace(HOME_TOKEN, str(home))
    if system == "Darwin" and relative == ".pi/agent/AGENTS.md":
        start = text.index("# Privileged commands\n")
        end = text.index("\n# ", start + 1)
        text = text[:start] + (
            "# Privileged commands\n"
            "- Pi's bash tool has no terminal. On macOS, ask me to run privileged commands "
            "in a real interactive terminal. Never pass a password through stdin, arguments, "
            "or environment variables. Linux-only Polkit commands do not apply here.\n"
        ) + text[end:]
    return text


def apply(home: Path, repo: Path, system: str, write: bool) -> list[str]:
    """Preflight all files, then back up and replace only changed managed files."""
    snapshot = repo / "snapshot"
    manifest = json.loads((snapshot / "manifest.json").read_text())
    changes = []
    for entry in manifest["files"]:
        if entry["platform"] not in ("all", system):
            continue
        relative = entry["path"]
        destination = target_path(home, relative)
        source = target_path(snapshot, relative)
        text = source.read_text()
        check_secrets(text, relative)
        text = render_file(text, relative, home, system)
        if destination.exists() and not destination.is_file():
            raise ValueError(f"Expected a file: {destination}")
        if (not destination.exists() or destination.read_text() != text
                or destination.stat().st_mode & 0o777 != entry["mode"]):
            changes.append((relative, destination, text, entry["mode"]))
    if write and changes:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
        backup = target_path(home, f".local/state/dotfiles/backups/{stamp}")
        for relative, destination, _text, _mode in changes:
            if destination.exists():
                saved = backup / relative
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(destination, saved)
        for _relative, destination, text, mode in changes:
            destination.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temporary = tempfile.mkstemp(dir=destination.parent, prefix=".dotfiles-")
            try:
                with os.fdopen(descriptor, "w") as stream:
                    stream.write(text)
                os.chmod(temporary, mode)
                os.replace(temporary, destination)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        print(f"Backups of replaced files: {backup}")
    return [relative for relative, _destination, _text, _mode in changes]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("capture", "apply", "check"))
    parser.add_argument("--write", action="store_true", help="apply changes; otherwise preview only")
    args = parser.parse_args()
    if args.command == "capture":
        manifest = ROOT / "snapshot/manifest.json"
        if manifest.exists() and json.loads(manifest.read_text())["source_host"] != platform.node():
            parser.error("Capture is allowed only on the source PC named in snapshot/manifest.json")
        print(f"Captured {capture(Path.home(), ROOT)} files from this machine")
    elif args.command == "apply":
        for relative in apply(Path.home(), ROOT, platform.system(), args.write):
            print(("Applied " if args.write else "Would apply ") + relative)
        if not args.write:
            print("Preview only. Run script/apply --write to apply with backups.")
    else:
        snapshot = ROOT / "snapshot"
        for entry in json.loads((snapshot / "manifest.json").read_text())["files"]:
            relative = entry["path"]
            text = target_path(snapshot, relative).read_text()
            check_secrets(text, relative)
            if relative.endswith(".json"):
                json.loads(text)
        print("Snapshot paths, JSON, and credential checks passed")


if __name__ == "__main__":
    main()
