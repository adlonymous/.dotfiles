"""Git/GitHub actions for one workspace folder, executed on its own machine."""

import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit

GIT = ["git", "--literal-pathspecs", "--no-optional-locks", "-c", "core.fsmonitor=false"]
SECRET = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:ghp_|github_pat_|sk-proj-|sk-ant-)[A-Za-z0-9_-]{20,}|\bAKIA[A-Z0-9]{16}\b")


def redact_url(text: str) -> str:
    return re.sub(r"(https?://)[^/\s@]+@", r"\1<redacted>@", text)


def command(argv: list[str], cwd: Path, check=True) -> subprocess.CompletedProcess:
    environment = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GH_PROMPT_DISABLED": "1"}
    if argv[0] == "gh":
        environment["GH_HOST"] = "github.com"
    result = subprocess.run(argv, cwd=cwd, env=environment, capture_output=True, text=True,
                            errors="surrogateescape", timeout=25, check=False)
    if check and result.returncode:
        raise ValueError(redact_url((result.stderr or result.stdout).strip()) or "Command failed")
    return result


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


class GitRepository:
    def __init__(self, folder: str):
        self.folder = Path(folder).expanduser().resolve() if folder else Path.home()
        top = command([*GIT, "rev-parse", "--show-toplevel"], self.folder, check=False)
        self.root = Path(top.stdout.strip()) if top.returncode == 0 else None

    def git(self, *args: str, check=True) -> str:
        return command([*GIT, *args], self.root, check=check).stdout.rstrip("\n")

    def operation(self) -> str:
        for name in ("MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD", "REVERT_HEAD"):
            if Path(self.git("rev-parse", "--path-format=absolute", "--git-path", name)).exists():
                return name
        return ""

    def remotes(self) -> list[dict]:
        result = []
        for name in self.git("remote").splitlines():
            fetch = self.git("remote", "get-url", name)
            pushes = self.git("remote", "get-url", "--push", "--all", name).splitlines()
            result.append({"name": name, "fetch": fetch, "pushes": pushes})
        return result

    def status(self) -> dict:
        if not self.root:
            return {"is_repo": False, "folder": str(self.folder)}
        raw = self.git("status", "--porcelain=v1", "-z", "--no-renames", "--untracked-files=all")
        files = [{"path": entry[3:], "index": entry[0], "worktree": entry[1],
                  "conflict": "U" in entry[:2] or entry[:2] in {"AA", "DD"}}
                 for entry in raw.split("\0") if entry]
        head = self.git("rev-parse", "--verify", "HEAD", check=False)
        branch = self.git("symbolic-ref", "--quiet", "--short", "HEAD", check=False)
        upstream = self.git("for-each-ref", "--format=%(upstream:short)", f"refs/heads/{branch}") if branch else ""
        counts = self.git("rev-list", "--left-right", "--count", "HEAD...@{upstream}", check=False).split() if upstream else []
        remotes = self.remotes()
        modified = []
        for file in files:
            path = self.root / file["path"]
            if path.exists() or path.is_symlink():
                stat = path.lstat()
                modified.append([file["path"], stat.st_mtime_ns, stat.st_size, stat.st_ino])
        fingerprint = hashlib.sha256(json.dumps([
            str(self.root), head, branch, raw, modified, self.git("ls-files", "--stage", "-z"), remotes,
        ], sort_keys=True).encode()).hexdigest()
        remote_head = self.git("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD", check=False)
        default_branch = remote_head.removeprefix("origin/") if remote_head else "main"
        return {
            "is_repo": True, "folder": str(self.folder), "root": str(self.root), "head": head,
            "branch": branch, "default_branch": default_branch, "upstream": upstream,
            "ahead": int(counts[0]) if len(counts) == 2 else None,
            "behind": int(counts[1]) if len(counts) == 2 else None,
            "files": files, "branches": self.git("for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines(),
            "remotes": [{"name": remote["name"], "url": redact_url(remote["fetch"]),
                         "push_urls": [redact_url(url) for url in remote["pushes"]],
                         "github_url": "https://github.com/" + github_slug(remote["fetch"]) if github_slug(remote["fetch"]) else ""}
                        for remote in remotes],
            "operation": self.operation(), "fingerprint": fingerprint,
            "identity": {"name": self.git("config", "user.name", check=False),
                         "email": self.git("config", "user.email", check=False)},
        }

    def guard(self, expected: str) -> dict:
        state = self.status()
        if not state["is_repo"] or state["fingerprint"] != expected:
            raise ValueError("Repository changed since the preview. Refresh and try again.")
        if state["operation"]:
            raise ValueError("Finish the current merge/rebase/cherry-pick in a terminal first.")
        return state

    @contextmanager
    def mutation_lock(self):
        directory = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "herdr-git/locks"
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        common = self.git("rev-parse", "--path-format=absolute", "--git-common-dir")
        path = directory / (hashlib.sha256(common.encode()).hexdigest() + ".lock")
        descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
        with os.fdopen(descriptor, "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def selected_path(self, state: dict, path: str) -> dict:
        for file in state["files"]:
            if file["path"] == path:
                return file
        raise ValueError("That file is no longer in the change list. Refresh first.")

    def diff(self, request: dict) -> dict:
        state = self.guard(request["expected"])
        file = self.selected_path(state, request["path"])
        staged = request["staged"]
        if file["index"] == "?":
            path = self.root / file["path"]
            if path.is_symlink():
                text = "Symbolic link: " + os.readlink(path)
            else:
                with path.open("rb") as stream:
                    content = stream.read(400001)
                if b"\0" in content:
                    return {"text": "Binary file; no text preview"}
                text = content[:400000].decode("utf-8", "replace")
                if len(content) > 400000:
                    text += "\n[Preview truncated]"
            lines = text.splitlines()
            return {"text": f"@@ -0,0 +1,{len(lines)} @@\n" + "\n".join("+" + line for line in lines)}
        return {"text": self.git("diff", *(["--cached"] if staged else []), "--no-ext-diff",
                                 "--no-textconv", "--no-color", "--", file["path"])[:400000]}

    def scan_staged(self) -> None:
        paths = self.git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split("\0")
        for path in paths:
            if Path(path).name == ".env" or (Path(path).name.startswith(".env.") and not path.endswith(".example")):
                raise ValueError("A staged environment file may contain secrets. Unstage it before committing.")
        diff = self.git("diff", "--cached", "--no-ext-diff", "--no-textconv", "--no-color")
        additions = "\n".join(line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
        if SECRET.search(additions):
            raise ValueError("Possible secret in staged changes. Review and unstage it before committing.")

    def remote(self, name: str) -> dict:
        if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]*", name):
            raise ValueError("Unsupported remote name")
        for remote in self.remotes():
            if remote["name"] == name:
                return remote
        raise ValueError("Select an existing remote")

    def push(self, state: dict, name: str) -> dict:
        if not state["head"] or not state["branch"] or state["branch"] in {"main", "master"}:
            raise ValueError("Create a feature branch before pushing; default-branch pushes are blocked.")
        remote = self.remote(name)
        if len(remote["pushes"]) != 1:
            raise ValueError("Multiple push destinations need a terminal; nothing was pushed.")
        url = remote["pushes"][0]
        refs = self.git("ls-remote", "--symref", url, "HEAD")
        match = re.search(r"^ref: refs/heads/([^\t]+)\tHEAD$", refs, re.MULTILINE)
        default = match[1] if match else ""
        if not default and github_slug(url):
            default = command(["gh", "api", "repos/" + github_slug(url), "--jq", ".default_branch"], self.root).stdout.strip()
        if not default:
            raise ValueError("Cannot verify the remote default branch. Nothing was pushed.")
        if not state["head"] or not state["branch"] or state["branch"] in {"main", "master", default}:
            raise ValueError("Create a feature branch before pushing; default-branch pushes are blocked.")
        self.guard(state["fingerprint"])
        self.git("push", name, f"{state['head']}:refs/heads/{state['branch']}")
        tracking = command([*GIT, "branch", f"--set-upstream-to={name}/{state['branch']}", state["branch"]], self.root, check=False)
        return {"message": "Pushed the reviewed commit." if tracking.returncode == 0 else "Push completed. Configure branch tracking in a terminal."}

    def mutate(self, request: dict) -> dict:
        state = self.guard(request["expected"])
        action = request["action"]
        if action in {"stage", "unstage"}:
            file = self.selected_path(state, request["path"])
            if action == "stage":
                self.git("add", "--", file["path"])
            elif state["head"]:
                self.git("restore", "--staged", "--", file["path"])
            else:
                self.git("rm", "--cached", "--", file["path"])
        elif action == "commit":
            if not request["message"].strip():
                raise ValueError("Enter a commit message")
            if not any(file["index"] not in {" ", "?"} for file in state["files"]):
                raise ValueError("Stage files before committing")
            self.scan_staged()
            self.git("commit", "-m", request["message"].strip())
        elif action == "identity":
            if not request["name"].strip() or not re.fullmatch(r"[^\s@]+@[^\s@]+", request["email"].strip()):
                raise ValueError("Enter a name and email for this repository")
            self.git("config", "--local", "user.name", request["name"].strip())
            self.git("config", "--local", "user.email", request["email"].strip())
        elif action in {"branch", "switch"}:
            branch = request["branch"]
            self.git("check-ref-format", "--branch", branch)
            if action == "switch" and state["files"]:
                raise ValueError("Commit or stash your changes in a terminal before switching branches")
            if action == "branch" and state["files"] and not request.get("carry_changes"):
                raise ValueError("Confirm that current changes should move with the new branch")
            self.git("switch", *(["-c"] if action == "branch" else []), branch)
        elif action == "fetch":
            self.remote(request["remote"])
            self.git("fetch", "--prune", request["remote"])
        elif action == "pull":
            remote = request["remote"]
            self.remote(remote)
            if state["files"] or not state["upstream"].startswith(remote + "/"):
                raise ValueError("Pull needs a clean working tree and an upstream on the selected remote")
            self.git("pull", "--ff-only", "--no-rebase", remote, state["upstream"][len(remote) + 1:])
        elif action == "push":
            return self.push(state, request["remote"])
        elif action == "github-create":
            if state["remotes"] or not state["head"]:
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
                     "--source", str(self.root), "--remote", "origin", "--description", request.get("description", ""),
                     *(["--homepage", homepage] if homepage else [])], self.root)
            return {"url": "https://github.com/" + owner + "/" + name, "message": "Repository created; no commits were pushed."}
        else:
            raise ValueError("Unknown Git action")
        return {"message": "Done"}


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


def handle_request(request: dict, home: Path) -> dict:
    if request["action"] == "project-info":
        return {"parent": str(home / "Projects")}
    if request["action"] == "project-create":
        return create_project(request, home)
    if request["action"] == "github-info":
        result = command(["gh", "api", "user", "--jq", ".login"], home)
        return {"owner": result.stdout.strip()}
    repo = GitRepository(request.get("folder", ""))
    if request["action"] == "status":
        return repo.status()
    if request["action"] == "diff":
        return repo.diff(request)
    if not repo.root:
        raise ValueError("This folder is not a Git repository")
    with repo.mutation_lock():
        return repo.mutate(request)


if __name__ == "__main__":
    try:
        print(json.dumps(handle_request(json.loads(sys.argv[1]), Path.home())))
    except (ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
        message = "Command timed out. It may have completed; refresh before retrying." if isinstance(error, subprocess.TimeoutExpired) else redact_url(str(error))
        print(json.dumps({"error": message}))
        sys.exit(1)
