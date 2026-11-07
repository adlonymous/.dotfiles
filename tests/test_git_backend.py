import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "snapshot/.config/herdr-app/mods/changes-readable"
spec = importlib.util.spec_from_file_location("git_backend", MOD / "git_backend.py")
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)


class GitBackendTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.folder = self.home / "project with spaces"
        self.folder.mkdir()
        environment = patch.dict(os.environ, {
            "HOME": str(self.home), "XDG_STATE_HOME": str(self.home / "state"),
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_COUNT": "0",
            "GIT_AUTHOR_NAME": "Git panel test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
            "GIT_COMMITTER_NAME": "Git panel test", "GIT_COMMITTER_EMAIL": "test@example.invalid",
        })
        environment.start()
        self.addCleanup(environment.stop)
        self.git("init", "--initial-branch=main")

    def git(self, *args, environment=None):
        return subprocess.run(["git", *args], cwd=self.folder, env=environment, check=True,
                              capture_output=True, text=True).stdout.strip()

    def request(self, action, **values):
        return backend.handle_request({"action": action, "folder": str(self.folder), "workspace": "s1", **values}, self.home)

    def seed(self):
        (self.folder / "README.md").write_text("# Example\n")
        self.git("add", "README.md")
        self.git("commit", "-m", "test: initial project")

    def test_new_project_is_git_backed_but_never_committed_or_published(self):
        result = self.request("project-create", name="new-project", parent=str(self.home / "Projects"), description="An example")
        folder = Path(result["folder"])
        self.assertTrue(result["initialized"])
        info = backend.repository_info(str(folder))
        self.assertEqual(info["branch"], "main")
        self.assertEqual(info["head"], "")
        self.assertFalse(info["has_remotes"])
        self.assertIn("Revise this AGENTS.md", (folder / "AGENTS.md").read_text())
        self.assertIn("An example", (folder / "README.md").read_text())
        self.assertIn(".env", (folder / ".gitignore").read_text())

    def test_existing_home_and_invalid_project_folders_are_untouched(self):
        existing = self.home / "existing"
        existing.mkdir()
        for name, parent in [("existing", self.home), (self.home.name, self.home.parent),
                             ("..", self.home), ("a/b", self.home), (".", self.home), ("child", self.folder / ".git")]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.request("project-create", name=name, parent=str(parent))
        self.assertFalse((existing / ".git").exists())
        self.assertFalse((self.home / ".git").exists())
        self.assertFalse(backend.repository_info(str(self.home))["is_repo"])

    def test_nested_project_reuses_parent_repository(self):
        self.seed()
        result = self.request("project-create", name="child", parent=str(self.folder))
        self.assertFalse(result["initialized"])
        self.assertFalse((Path(result["folder"]) / ".git").exists())
        self.assertEqual(backend.repository_info(result["folder"])["root"], str(self.folder))

    def test_session_never_initializes_existing_non_git_folder(self):
        result = self.request("open", folder=str(self.home))
        self.assertFalse(result["is_repo"])
        self.assertIsNone(result["terminal"])
        self.assertFalse((self.home / ".git").exists())

    def test_github_creation_requires_visibility_and_does_not_push(self):
        self.seed()
        info = backend.repository_info(str(self.folder))
        values = {"expected": info["fingerprint"], "owner": "example-owner", "name": "example", "visibility": ""}
        with self.assertRaisesRegex(ValueError, "explicitly"):
            self.request("github-create", **values)
        real_command = backend.command
        calls = []
        def command(argv, *args, **kwargs):
            if argv[0] == "gh":
                calls.append(argv)
                return subprocess.CompletedProcess(argv, 0, "", "")
            return real_command(argv, *args, **kwargs)
        with patch.object(backend, "command", side_effect=command):
            result = self.request("github-create", **{**values, "visibility": "private", "description": "Example", "homepage": "https://example.invalid"})
        self.assertEqual(result["url"], "https://github.com/example-owner/example")
        self.assertIn("--private", calls[0])
        self.assertIn("--description", calls[0])
        self.assertIn("--homepage", calls[0])
        self.assertNotIn("--push", calls[0])
        self.git("remote", "add", "origin", "https://github.com/example-owner/example.git")
        with self.assertRaisesRegex(ValueError, "Repository changed"):
            self.request("github-create", **{**values, "visibility": "public"})

    def test_scoped_hooks_preserve_existing_hooks_and_leave_repository_config_unchanged(self):
        self.seed()
        hooks = self.folder / "custom-hooks"
        hooks.mkdir()
        self.git("config", "core.hooksPath", "custom-hooks")
        before = (self.folder / ".git/config").read_text()
        hook = hooks / "pre-commit"
        hook.write_text("#!/bin/sh\necho 'original hook rejected commit' >&2\nexit 1\n")
        hook.chmod(0o755)
        (self.folder / "new.txt").write_text("chosen content\n")
        self.git("add", "new.txt")
        with backend.lazygit_environment() as environment:
            result = subprocess.run(["git", "commit", "-m", "test: respect hooks"], cwd=self.folder,
                                    env=environment, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("original hook rejected commit", result.stderr)
        self.assertEqual((self.folder / ".git/config").read_text(), before)
        self.assertIn("new.txt", self.git("diff", "--cached", "--name-only"))

    def test_scoped_secret_scan_blocks_environment_files_and_private_keys(self):
        (self.folder / ".env").write_text("LOCAL_VALUE=example\n")
        self.git("add", ".env")
        with backend.lazygit_environment() as environment:
            result = subprocess.run(["git", "commit", "-m", "test: refuse env"], cwd=self.folder,
                                    env=environment, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("environment file", result.stderr)
        self.git("rm", "--cached", ".env")
        (self.folder / "key.txt").write_text("-----BEGIN " + "PRIVATE KEY-----\nnot-a-key\n")
        self.git("add", "key.txt")
        with self.assertRaisesRegex(ValueError, "Possible secret"):
            backend.scan_staged(self.folder)

    def test_default_branch_guard_checks_destination_refs_not_just_current_branch(self):
        self.seed()
        bare = self.home / "remote.git"
        self.git("clone", "--bare", str(self.folder), str(bare))
        sha = self.git("rev-parse", "HEAD")
        for name in ("main", "master"):
            with self.assertRaisesRegex(ValueError, "Default-branch"):
                backend.guard_push(self.folder, str(bare), f"refs/heads/feat/work {sha} refs/heads/{name} {'0' * 40}\n".encode())
        backend.guard_push(self.folder, str(bare), f"refs/heads/feat/work {sha} refs/heads/feat/work {'0' * 40}\n".encode())
        # Real feature push exercises the hook and forwards its original stdin unchanged.
        self.git("switch", "-c", "feat/work")
        hook = self.folder / ".git/hooks/pre-push"
        hook.write_text('#!/bin/sh\nIFS= read -r update\nprintf "%s" "$update" > original-hook-input\n')
        hook.chmod(0o755)
        with backend.lazygit_environment() as environment:
            self.git("push", str(bare), "feat/work", environment=environment)
        self.assertIn("refs/heads/feat/work", (self.folder / "original-hook-input").read_text())

    def test_custom_remote_default_and_unknown_defaults_fail_closed(self):
        self.seed()
        self.git("branch", "-m", "production")
        bare = self.home / "custom.git"
        self.git("clone", "--bare", str(self.folder), str(bare))
        payload = f"refs/heads/feature {'a' * 40} refs/heads/production {'b' * 40}\n".encode()
        with self.assertRaisesRegex(ValueError, "Default-branch"):
            backend.guard_push(self.folder, str(bare), payload)
        empty = self.home / "empty.git"
        self.git("init", "--bare", str(empty))
        with self.assertRaisesRegex(ValueError, "Cannot verify"):
            backend.guard_push(self.folder, str(empty), payload)

    def test_empty_github_repository_uses_api_default_without_pushing(self):
        payload = f"refs/heads/feature {'a' * 40} refs/heads/production {'b' * 40}\n".encode()
        response = subprocess.CompletedProcess([], 0, "production\n", "")
        with (patch.object(backend, "git", return_value=""),
              patch.object(backend, "command", return_value=response) as call,
              self.assertRaisesRegex(ValueError, "Default-branch")):
            backend.guard_push(self.folder, "git@github.com:owner/new.git", payload)
        self.assertEqual(call.call_args.args[0], ["gh", "api", "repos/owner/new", "--jq", ".default_branch"])

    def test_hooks_added_while_lazygit_runs_are_still_forwarded(self):
        self.seed()
        with backend.lazygit_environment() as environment:
            hook = self.folder / ".git/hooks/pre-commit"
            hook.write_text("#!/bin/sh\necho 'new hook rejected commit' >&2\nexit 1\n")
            hook.chmod(0o755)
            (self.folder / "new.txt").write_text("content\n")
            self.git("add", "new.txt")
            result = subprocess.run(["git", "commit", "-m", "test: honor new hook"], cwd=self.folder,
                                    env=environment, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("new hook rejected commit", result.stderr)

    def test_repository_info_never_returns_embedded_remote_credentials(self):
        self.git("remote", "add", "origin", "https://user:example-password@github.com/owner/repo.git")
        info = backend.repository_info(str(self.folder))
        self.assertNotIn("example-password", json.dumps(info))
        self.assertEqual(info["github_url"], "https://github.com/owner/repo")


if __name__ == "__main__":
    unittest.main()
