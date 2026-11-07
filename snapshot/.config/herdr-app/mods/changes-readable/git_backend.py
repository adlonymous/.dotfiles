"""Launch workspace-local Lazygit; keep project creation and GitHub publishing explicit."""

import fcntl
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit

GIT = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false"]
HERE = Path(__file__).resolve().parent
SECRET = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:ghp_|github_pat_|sk-proj-|sk-ant-)[A-Za-z0-9_-]{20,}|\bAKIA[A-Z0-9]{16}\b")
HOOKS = [
    "applypatch-msg", "pre-applypatch", "post-applypatch", "pre-commit", "pre-merge-commit",
    "prepare-commit-msg", "commit-msg", "post-commit", "pre-rebase", "post-checkout", "post-merge",
    "pre-push", "pre-receive", "update", "proc-receive", "post-receive", "post-update",
    "reference-transaction", "push-to-checkout", "pre-auto-gc", "post-rewrite", "sendemail-validate",
    "fsmonitor-watchman", "p4-changelist", "p4-prepare-changelist", "p4-post-changelist", "p4-pre-submit", "post-index-change",
]


def redact_url(text: str) -> str:
    return re.sub(r"(https?://)[^/\s@]+@", r"\1<redacted>@", text)


def command(argv: list[str], cwd: Path, check=True, environment=None) -> subprocess.CompletedProcess:
    environment = {**(environment if environment is not None else os.environ), "GIT_TERMINAL_PROMPT": "0", "GH_PROMPT_DISABLED": "1"}
    if argv[0] == "gh":
        environment["GH_HOST"] = "github.com"
    result = subprocess.run(argv, cwd=cwd, env=environment, capture_output=True, text=True,
                            errors="surrogateescape", timeout=25, check=False)
    if check and result.returncode:
        raise ValueError(redact_url((result.stderr or result.stdout).strip()) or "Command failed")
    return result


def git(folder: Path, *args: str, check=True, environment=None) -> str:
    return command([*GIT, *args], folder, check, environment).stdout.rstrip("\n")


def github_slug(url: str) -> str:
    if url.startswith("git@github.com:"):
        path = url.removeprefix("git@github.com:")
    else:
        parsed = urlsplit(url)
        if parsed.hostname != "github.com":
            return ""
        path = parsed.path.lstrip("/")
    path = path.removesuffix(".git").rstrip("/")
    return path if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", path) else ""


@contextmanager
def workspace_lock(key: str):
    directory = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "herdr-git"
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(directory / (hashlib.sha256(key.encode()).hexdigest() + ".lock"), os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(descriptor, "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def repository_info(folder: str) -> dict:
    path = Path(folder).expanduser().resolve() if folder else Path.home()
    top = command([*GIT, "rev-parse", "--show-toplevel"], path, check=False)
    if top.returncode:
        return {"is_repo": False, "folder": str(path)}
    root = Path(top.stdout.strip())
    remotes = [(name, git(root, "remote", "get-url", name)) for name in git(root, "remote").splitlines()]
    head = git(root, "rev-parse", "--verify", "HEAD", check=False)
    fingerprint = hashlib.sha256(json.dumps([str(root), head, remotes]).encode()).hexdigest()
    slug = next((github_slug(url) for _, url in remotes if github_slug(url)), "")
    return {"is_repo": True, "folder": str(path), "root": str(root), "head": head,
            "branch": git(root, "symbolic-ref", "--quiet", "--short", "HEAD", check=False),
            "has_remotes": bool(remotes), "github_url": "https://github.com/" + slug if slug else "",
            "identity": {"name": git(root, "config", "user.name", check=False), "email": git(root, "config", "user.email", check=False)},
            "fingerprint": fingerprint}


def lazygit_session(request: dict, start: bool) -> dict:
    info = repository_info(request.get("folder", ""))
    if not info["is_repo"]:
        return {**info, "terminal": None}
    key = json.dumps([request["workspace"], info["root"]])
    label = "dotfiles.git=" + hashlib.sha256(key.encode()).hexdigest()[:24]
    with workspace_lock(key):
        listed = json.loads(command(["hc", "ls", "--json", "--label", label], Path(info["root"])).stdout)
        live = listed["terminals"]
        if live:
            return {**info, "terminal": live[0]["address"]}
        if not start:
            return {**info, "terminal": None}
        if not shutil.which("lazygit"):
            raise ValueError("Install lazygit on this workspace's machine first (Mac: brew install lazygit).")
        created = command(["hc", "run", "--json", "--bg", "--no-parent", "--outlive-parent", "--no-notify",
                           "--cwd", info["root"], "--label", label, "--", sys.executable,
                           str(HERE / "git_backend.py"), "run-lazygit"], Path(info["root"]))
        return {**info, "terminal": json.loads(created.stdout)["address"]}


def scan_staged(folder: Path) -> None:
    paths = git(folder, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split("\0")
    if any(Path(path).name == ".env" or (Path(path).name.startswith(".env.") and not path.endswith(".example")) for path in paths):
        raise ValueError("A staged environment file may contain secrets. Unstage it before committing.")
    diff = git(folder, "diff", "--cached", "--no-ext-diff", "--no-textconv", "--no-color")
    additions = "\n".join(line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
    if SECRET.search(additions):
        raise ValueError("Possible secret in staged changes. Review and unstage it before committing.")


def guard_push(folder: Path, destination: str, payload: bytes) -> None:
    branches = [line.split()[2].removeprefix("refs/heads/") for line in payload.decode("utf-8", "surrogateescape").splitlines()
                if len(line.split()) == 4 and line.split()[2].startswith("refs/heads/")]
    if not branches:
        return
    if {"main", "master"}.intersection(branches):
        raise ValueError("Default-branch pushes are blocked. Create and push a feature branch.")
    refs = git(folder, "ls-remote", "--symref", destination, "HEAD")
    match = re.search(r"^ref: refs/heads/([^\t]+)\tHEAD$", refs, re.MULTILINE)
    default = match[1] if match else ""
    if not default and github_slug(destination):
        default = command(["gh", "api", "repos/" + github_slug(destination), "--jq", ".default_branch"], folder).stdout.strip()
    if not default:
        raise ValueError("Cannot verify the remote default branch. Nothing was pushed.")
    if default in branches:
        raise ValueError("Default-branch pushes are blocked. Create and push a feature branch.")


def forward_git_hook(name: str, original_count: str, args: list[str]) -> int:
    # Resolve hooks afresh in the current repo, even if Lazygit switched repositories.
    environment = {**os.environ, "GIT_CONFIG_COUNT": original_count}
    folder = Path.cwd()
    configured = git(folder, "config", "--path", "--get", "core.hooksPath", check=False, environment=environment)
    directory = Path(configured).expanduser() if configured else Path(git(folder, "rev-parse", "--path-format=absolute", "--git-path", "hooks", environment=environment))
    original = (folder / directory / name).resolve()
    payload = sys.stdin.buffer.read() if name == "pre-push" else None
    if name == "pre-push":
        guard_push(folder, args[1], payload)
    if name == "pre-commit":
        scan_staged(folder)
    if original.is_file() and os.access(original, os.X_OK):
        return subprocess.run([str(original), *args], env=environment, input=payload, check=False).returncode
    return 0


@contextmanager
def lazygit_environment():
    with tempfile.TemporaryDirectory(prefix="herdr-git-hooks-") as temporary:
        hooks = Path(temporary)
        original_count = os.environ.get("GIT_CONFIG_COUNT", "0")
        for name in HOOKS:
            hook = hooks / name
            hook.write_text("#!/bin/sh\nexec " + shlex.quote(sys.executable) + " " + shlex.quote(str(HERE / "git_backend.py"))
                            + " git-hook " + shlex.quote(name) + " " + shlex.quote(original_count) + ' "$@"\n')
            hook.chmod(0o700)
        environment = dict(os.environ)
        count = int(original_count)
        environment.update({"GIT_CONFIG_COUNT": str(count + 1), f"GIT_CONFIG_KEY_{count}": "core.hooksPath",
                            f"GIT_CONFIG_VALUE_{count}": str(hooks)})
        yield environment


def run_lazygit() -> int:
    folder = Path.cwd()
    configured = os.environ.get("LG_CONFIG_FILE", "")
    if configured:
        configs = configured.split(",")
    else:
        directory = command(["lazygit", "--print-config-dir"], folder).stdout.strip()
        global_config = Path(directory) / "config.yml"
        configs = [str(global_config)] if global_config.is_file() else []
    configs.append(str(HERE / "lazygit.yml"))
    with lazygit_environment() as environment:
        return subprocess.run(["lazygit", "--use-config-file", ",".join(configs)], env=environment, check=False).returncode


def create_project(request: dict, home: Path) -> dict:
    name = request["name"].strip()
    if not name or name in {".", ".."} or any(char in name for char in "/\\\n\r\0"):
        raise ValueError("Use a single project-folder name")
    parent = Path(request["parent"]).expanduser().resolve()
    target = parent / name
    if {".git", ".bare"}.intersection(parent.parts):
        raise ValueError("Choose a project folder outside Git's internal directories")
    if target in {home.resolve(), Path("/")} or target.exists() or target.is_symlink():
        raise ValueError("Choose a new dedicated folder; existing folders are never initialized")
    parent.mkdir(parents=True, exist_ok=True)
    inherited = command([*GIT, "rev-parse", "--show-toplevel"], parent, check=False)
    target.mkdir()
    if inherited.returncode:
        command([*GIT, "init", "--initial-branch=main"], target)
    (target / ".gitignore").write_text(".env\n.env.*\n!.env.example\n.DS_Store\n")
    (target / "README.md").write_text("# " + name + "\n\n" + request.get("description", "").strip() + "\n")
    (target / "AGENTS.md").write_text(
        "# Project instructions\n\n- Keep secrets in ignored environment files.\n"
        "- Document the actual stack and check commands here as the project is built.\n"
        "- Revise this AGENTS.md whenever meaningful project changes affect setup, scripts, or conventions.\n"
    )
    return {"folder": str(target), "name": name, "initialized": inherited.returncode != 0}


def create_github_repository(request: dict) -> dict:
    info = repository_info(request["folder"])
    if not info["is_repo"] or info["fingerprint"] != request["expected"]:
        raise ValueError("Repository changed since the preview. Close and reopen this form.")
    if info["has_remotes"] or not info["head"]:
        raise ValueError("Create the first commit first; GitHub creation requires a repository without remotes")
    owner, name = request["owner"], request["name"]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", owner) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", name) or name in {".", ".."}:
        raise ValueError("Enter a valid GitHub owner and repository name")
    if request["visibility"] not in {"public", "private"}:
        raise ValueError("Choose public or private explicitly")
    homepage = request.get("homepage", "").strip()
    if homepage and urlsplit(homepage).scheme not in {"http", "https"}:
        raise ValueError("Homepage must be an HTTP(S) URL")
    command(["gh", "repo", "create", owner + "/" + name, "--" + request["visibility"],
             "--source", info["root"], "--remote", "origin", "--description", request.get("description", ""),
             *(["--homepage", homepage] if homepage else [])], Path(info["root"]))
    return {"url": "https://github.com/" + owner + "/" + name}


def handle_request(request: dict, home: Path) -> dict:
    action = request["action"]
    if action == "project-info":
        return {"parent": str(home / "Projects")}
    if action == "project-create":
        return create_project(request, home)
    if action == "github-info":
        return {"owner": command(["gh", "api", "user", "--jq", ".login"], home).stdout.strip()}
    if action == "github-create":
        with workspace_lock(str(Path(request["folder"]).resolve())):
            return create_github_repository(request)
    if action in {"open", "session"}:
        return lazygit_session(request, start=action == "open")
    raise ValueError("Unknown workspace Git action")


if __name__ == "__main__":
    try:
        if sys.argv[1] == "run-lazygit":
            sys.exit(run_lazygit())
        if sys.argv[1] == "git-hook":
            sys.exit(forward_git_hook(sys.argv[2], sys.argv[3], sys.argv[4:]))
        print(json.dumps(handle_request(json.loads(sys.argv[1]), Path.home())))
    except (ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
        message = "Command timed out. It may have completed; check before retrying." if isinstance(error, subprocess.TimeoutExpired) else redact_url(str(error))
        if sys.argv[1] in {"run-lazygit", "git-hook"}:
            print(message, file=sys.stderr)
        else:
            print(json.dumps({"error": message}))
        sys.exit(1)
