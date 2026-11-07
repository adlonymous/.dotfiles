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
        self.git("config", "user.name", "Example")
        self.git("config", "user.email", "test@example.invalid")

    def git(self, *args, folder=None):
        return subprocess.run(["git", *args], cwd=folder or self.folder, check=True,
                              capture_output=True, text=True).stdout.strip()

    def request(self, action, **values):
        expected = self.request("status").get("fingerprint") if action not in {"status", "project-info", "project-create", "github-info"} else None
        return backend.handle_request({"action": action, "folder": str(self.folder), "expected": expected, **values}, self.home)

    def seed(self):
        (self.folder / "README.md").write_text("# Example\n")
        self.request("stage", path="README.md")
        self.request("commit", message="test: initial project")

    def test_new_project_initializes_git_without_commit_or_remote(self):
        result = self.request("project-create", name="new-project", parent=str(self.home / "Projects"), description="An example")
        folder = Path(result["folder"])
        self.assertTrue(result["initialized"])
        info = backend.GitRepository(str(folder)).status()
        self.assertEqual(info["branch"], "main")
        self.assertEqual(info["head"], "")
        self.assertEqual(info["remotes"], [])
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
        self.assertFalse(backend.GitRepository(str(self.home)).status()["is_repo"])

    def test_nested_project_uses_parent_and_existing_worktree_is_supported(self):
        self.seed()
        result = self.request("project-create", name="child", parent=str(self.folder))
        self.assertFalse(result["initialized"])
        self.assertFalse((Path(result["folder"]) / ".git").exists())
        self.assertEqual(backend.GitRepository(result["folder"]).status()["root"], str(self.folder))
        worktree = self.home / "feature-worktree"
        self.git("worktree", "add", "-b", "feat/worktree", str(worktree))
        state = backend.GitRepository(str(worktree)).status()
        self.assertEqual(state["root"], str(worktree))
        self.assertEqual(state["branch"], "feat/worktree")

    def test_commit_only_uses_explicitly_staged_files(self):
        (self.folder / "chosen.txt").write_text("chosen\n")
        (self.folder / "leave alone.txt").write_text("not selected\n")
        self.request("stage", path="chosen.txt")
        self.request("unstage", path="chosen.txt")
        self.assertEqual(self.git("ls-files"), "")
        self.request("stage", path="chosen.txt")
        self.request("commit", message="feat: selected content")
        self.assertEqual(self.git("ls-tree", "--name-only", "HEAD"), "chosen.txt")
        (self.folder / "chosen.txt").write_text("updated\n")
        self.request("stage", path="chosen.txt")
        self.request("unstage", path="chosen.txt")
        self.assertEqual(self.git("diff", "--cached"), "")
        self.assertEqual((self.folder / "chosen.txt").read_text(), "updated\n")

    def test_staged_and_working_diffs_are_distinct(self):
        self.seed()
        (self.folder / "README.md").write_text("staged version\n")
        self.request("stage", path="README.md")
        (self.folder / "README.md").write_text("working version\n")
        staged = self.request("diff", path="README.md", staged=True)["text"]
        working = self.request("diff", path="README.md", staged=False)["text"]
        self.assertIn("+staged version", staged)
        self.assertNotIn("working version", staged)
        self.assertIn("+working version", working)
        self.request("commit", message="fix: staged content")
        self.assertEqual(self.git("show", "HEAD:README.md"), "staged version")
        self.assertIn("+working version", self.git("diff"))

    def test_literal_paths_unicode_and_symlinks_do_not_escape_diff(self):
        for name in [":(glob)*", "space ' quote.txt", "中文.txt", "line\nbreak.txt"]:
            (self.folder / name).write_text("content\n")
            self.request("stage", path=name)
        self.assertEqual(len(self.request("status")["files"]), 4)
        (self.home / "outside").write_text("must not read target")
        (self.folder / "link").symlink_to(self.home / "outside")
        diff = self.request("diff", path="link", staged=False)["text"]
        self.assertIn("Symbolic link:", diff)
        self.assertNotIn("must not read target", diff)

    def test_external_edits_and_index_changes_reject_stale_requests(self):
        self.seed()
        (self.folder / "README.md").write_text("first modification\n")
        expected = self.request("status")["fingerprint"]
        (self.folder / "README.md").write_text("second modification\n")
        with self.assertRaisesRegex(ValueError, "Repository changed"):
            self.request("stage", path="README.md", expected=expected)
        self.request("stage", path="README.md")
        expected = self.request("status")["fingerprint"]
        self.git("restore", "--staged", "README.md")
        with self.assertRaisesRegex(ValueError, "Repository changed"):
            self.request("commit", message="test: stale index", expected=expected)

    def test_native_commits_preserve_existing_hooks_and_drafts_are_not_staged(self):
        self.seed()
        (self.folder / "new.txt").write_text("chosen\n")
        with self.assertRaisesRegex(ValueError, "Stage files"):
            self.request("commit", message="test: not selected")
        self.request("stage", path="new.txt")
        hook = self.folder / ".git/hooks/pre-commit"
        hook.write_text("#!/bin/sh\necho 'original hook rejected commit' >&2\nexit 1\n")
        hook.chmod(0o755)
        head = self.request("status")["head"]
        with self.assertRaisesRegex(ValueError, "original hook rejected"):
            self.request("commit", message="test: honor hooks")
        self.assertEqual(self.request("status")["head"], head)
        self.assertIn("new.txt", self.git("diff", "--cached", "--name-only"))

    def test_staged_environment_files_and_private_keys_are_blocked(self):
        (self.folder / ".env").write_text("LOCAL_VALUE=example\n")
        self.request("stage", path=".env")
        with self.assertRaisesRegex(ValueError, "environment file"):
            self.request("commit", message="test: refuse env")
        self.request("unstage", path=".env")
        (self.folder / "key.txt").write_text("-----BEGIN " + "PRIVATE KEY-----\nnot-a-key\n")
        self.request("stage", path="key.txt")
        with self.assertRaisesRegex(ValueError, "Possible secret"):
            self.request("commit", message="test: refuse key")

    def test_create_branch_confirms_dirty_changes_and_switch_requires_clean_tree(self):
        self.seed()
        self.git("branch", "other")
        (self.folder / "new.txt").write_text("pending\n")
        with self.assertRaisesRegex(ValueError, "Confirm"):
            self.request("branch", branch="feat/new")
        self.request("branch", branch="feat/new", carry_changes=True)
        with self.assertRaisesRegex(ValueError, "Commit or stash"):
            self.request("switch", branch="other")
        self.request("stage", path="new.txt")
        self.request("commit", message="feat: branch content")
        self.request("switch", branch="other")
        self.assertFalse((self.folder / "new.txt").exists())
        with self.assertRaises(ValueError):
            self.request("branch", branch="--orphan")

    def test_push_fetch_pull_use_real_local_remote_without_default_branch_push(self):
        self.seed()
        remote = self.home / "remote.git"
        self.git("clone", "--bare", str(self.folder), str(remote))
        self.git("remote", "add", "origin", str(remote))
        with self.assertRaisesRegex(ValueError, "default-branch"):
            self.request("push", remote="origin")
        self.request("branch", branch="feat/work")
        self.request("push", remote="origin")
        self.assertEqual(self.request("status")["upstream"], "origin/feat/work")
        other = self.home / "other"
        self.git("clone", str(remote), str(other))
        self.git("switch", "feat/work", folder=other)
        (other / "remote.txt").write_text("remote change\n")
        self.git("add", "remote.txt", folder=other)
        self.git("commit", "-m", "test: remote change", folder=other)
        self.git("push", "origin", "feat/work", folder=other)
        self.request("fetch", remote="origin")
        self.assertEqual(self.request("status")["behind"], 1)
        self.request("pull", remote="origin")
        self.assertEqual((self.folder / "remote.txt").read_text(), "remote change\n")
        (self.folder / "dirty.txt").write_text("pending\n")
        with self.assertRaisesRegex(ValueError, "clean working tree"):
            self.request("pull", remote="origin")

    def test_custom_remote_default_and_unknown_default_are_blocked(self):
        self.seed()
        self.git("branch", "-m", "production")
        remote = self.home / "custom.git"
        self.git("clone", "--bare", str(self.folder), str(remote))
        self.git("remote", "add", "origin", str(remote))
        with self.assertRaisesRegex(ValueError, "default-branch"):
            self.request("push", remote="origin")
        self.request("branch", branch="feat/work")
        empty = self.home / "empty.git"
        self.git("init", "--bare", str(empty))
        self.git("remote", "set-url", "--push", "origin", str(empty))
        with self.assertRaisesRegex(ValueError, "Cannot verify"):
            self.request("push", remote="origin")
        self.git("remote", "set-url", "--add", "--push", "origin", str(remote))
        with self.assertRaisesRegex(ValueError, "Multiple push"):
            self.request("push", remote="origin")

    def test_github_creation_requires_explicit_visibility_and_never_pushes(self):
        self.seed()
        values = {"owner": "example-owner", "name": "example", "visibility": ""}
        with self.assertRaisesRegex(ValueError, "explicitly"):
            self.request("github-create", **values)
        real_command, calls = backend.command, []
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

    def test_credentials_redacted_and_identity_configuration_is_local(self):
        self.git("remote", "add", "origin", "https://user:example-password@github.com/owner/repo.git")
        info = self.request("status")
        self.assertNotIn("example-password", json.dumps(info))
        self.assertEqual(info["remotes"][0]["github_url"], "https://github.com/owner/repo")
        self.request("identity", name="Example", email="example@example.invalid")
        self.assertEqual(self.git("config", "--local", "user.email"), "example@example.invalid")


if __name__ == "__main__":
    unittest.main()
