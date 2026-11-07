import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.install_git_panel import LAYOUT, MOD, changes_node, install_git_panel

ROOT = Path(__file__).resolve().parents[1]


class InstallGitPanelTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.layout = self.home / LAYOUT
        self.layout.parent.mkdir(parents=True)
        self.tree = json.loads((ROOT / "snapshot" / LAYOUT).read_text())
        self.tree["font_size"] = 22
        self.tree["terminal_padding"] = [19, 7]
        self.tree["children"][0]["size"] = {"px": 187}
        node = changes_node(self.tree)
        node["type"] = "column"
        node.pop("content")
        node["children"] = [{"id": "git-terminal", "type": "block", "content": {"terminal": "pc/t99"}}]
        self.layout.write_text(json.dumps(self.tree))
        self.keys = self.home / ".config/herdr-app/keys.json"
        self.keys.write_text('{"global":{"cmd-t":"tab.new"}}')
        self.settings = self.home / ".config/herdr-app/settings.json"
        self.settings.write_text('{"font_size":24,"zoom":1.75}')

    def test_dry_run_does_not_change_any_files(self):
        before = self.layout.read_text()
        changes = install_git_panel(self.home, ROOT, "Darwin", False)
        self.assertIn(LAYOUT, changes)
        self.assertEqual(self.layout.read_text(), before)
        self.assertFalse((self.home / MOD / "main.js").exists())
        self.assertFalse((self.home / ".local").exists())

    def test_mac_update_preserves_keys_settings_fonts_and_all_other_layout_nodes(self):
        keys, settings = self.keys.read_text(), self.settings.read_text()
        before = self.layout.read_text()
        install_git_panel(self.home, ROOT, "Darwin", True)
        after = json.loads(self.layout.read_text())
        expected = copy.deepcopy(self.tree)
        node = changes_node(expected)
        node.pop("children")
        node.update(type="block", content={"mod": "changes-readable"})
        self.assertEqual(after, expected)
        self.assertEqual(self.keys.read_text(), keys)
        self.assertEqual(self.settings.read_text(), settings)
        backups = list((self.home / ".local/state/dotfiles/backups").glob("*/" + LAYOUT))
        self.assertEqual(backups[0].read_text(), before)
        self.assertEqual(install_git_panel(self.home, ROOT, "Darwin", True), [])

    def test_retired_policy_is_backed_up_and_removed(self):
        policy = self.home / MOD / "lazygit.yml"
        policy.parent.mkdir(parents=True)
        policy.write_text("old policy\n")
        install_git_panel(self.home, ROOT, "Linux", True)
        self.assertFalse(policy.exists())
        backups = list((self.home / ".local/state/dotfiles/backups").glob("*/" + MOD + "/lazygit.yml"))
        self.assertEqual(backups[0].read_text(), "old policy\n")

    def test_symlink_or_missing_changes_node_fails_before_writing(self):
        target = self.home / "original.js"
        target.write_text("leave alone")
        main = self.home / MOD / "main.js"
        main.parent.mkdir(parents=True)
        main.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            install_git_panel(self.home, ROOT, "Darwin", True)
        self.assertEqual(target.read_text(), "leave alone")
        self.assertEqual(json.loads(self.layout.read_text()), self.tree)
        self.layout.write_text('{"id":"root","type":"row","children":[]}')
        with self.assertRaisesRegex(ValueError, "no Changes"):
            install_git_panel(self.home, ROOT, "Darwin", True)
