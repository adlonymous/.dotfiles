import json
import tempfile
import unittest
from pathlib import Path

from tools.install_agent_cards import LAYOUTS, MOD, agents_node, install_agent_cards
from tools.sync_config import ROOT


class AgentCardsInstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.tree = {
            "id": "root", "type": "row", "font": "Mac font", "children": [
                {"id": "sidebar", "type": "column", "size": {"px": 217}, "children": [
                    {"id": "agents", "type": "block", "size": {"weight": 1}, "min": 90,
                     "content": {"mod": "agents"}},
                ]},
                {"id": "main", "type": "block", "size": {"weight": 2}, "content": {"mod": "my-tabs"}},
            ],
        }
        for relative in LAYOUTS:
            path = self.home / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self.tree))
        self.settings = self.home / ".config/herdr-app/settings.json"
        self.settings.write_text('{"font_family":"Mac Font","font_size":17,"default_terminal_cols":103}')
        self.keys = self.settings.with_name("keys.json")
        self.keys.write_text('{"cmd-j":"agent.next"}')
        self.foreign = self.home / ".config/herdr-app/mods/other-mod/main.js"
        self.foreign.parent.mkdir(parents=True)
        self.foreign.write_text("untouched")

    def install(self, write=True):
        return install_agent_cards(self.home, ROOT, "Darwin", write)

    def test_preview_does_not_write_anything(self):
        before = {path: path.read_bytes() for path in self.home.rglob("*") if path.is_file()}
        changes = self.install(False)
        self.assertIn(MOD + "/main.js", changes)
        self.assertEqual(before, {path: path.read_bytes() for path in self.home.rglob("*") if path.is_file()})

    def test_scoped_install_preserves_viewer_settings_geometry_and_unrelated_mods(self):
        settings, keys = self.settings.read_bytes(), self.keys.read_bytes()
        self.install()
        for relative in LAYOUTS:
            tree = json.loads((self.home / relative).read_text())
            self.assertEqual(agents_node(tree)["content"], {"mod": "workspace-agents"})
            agents_node(tree)["content"] = {"mod": "agents"}
            self.assertEqual(tree, self.tree)
        self.assertEqual(self.settings.read_bytes(), settings)
        self.assertEqual(self.keys.read_bytes(), keys)
        self.assertEqual(self.foreign.read_text(), "untouched")
        self.assertEqual(len(list((self.home / MOD / "schematics").glob("*.svg"))), 9)
        self.assertTrue((self.home / MOD / "agent-card.js").is_file())
        self.assertEqual(self.install(), [])

    def test_backups_and_already_owned_layouts_keep_exact_bytes(self):
        old = self.home / MOD / "main.js"
        old.parent.mkdir(parents=True)
        old.write_text("previous cards")
        originals = {relative: (self.home / relative).read_bytes() for relative in LAYOUTS}
        self.install()
        backups = self.home / ".local/state/dotfiles/backups"
        self.assertTrue(any(path.read_text() == "previous cards" for path in backups.rglob("main.js")))
        for relative in LAYOUTS:
            self.assertTrue(any(path.read_bytes() == originals[relative] for path in backups.rglob(Path(relative).name)))
        tree = self.home / LAYOUTS[0]
        tree.write_text(json.dumps(json.loads(tree.read_text()), separators=(",", ":")))
        before = tree.read_bytes()
        self.install()
        self.assertEqual(tree.read_bytes(), before)

    def test_an_aadil_only_viewer_is_supported_without_creating_other_layouts(self):
        (self.home / LAYOUTS[0]).unlink()
        self.install()
        self.assertFalse((self.home / LAYOUTS[0]).exists())
        self.assertEqual(agents_node(json.loads((self.home / LAYOUTS[1]).read_text()))["content"]["mod"], "workspace-agents")

    def test_custom_agents_and_missing_layouts_are_not_overwritten(self):
        for relative in LAYOUTS:
            (self.home / relative).unlink()
        with self.assertRaisesRegex(ValueError, "Install wide-panels or Aadil"):
            self.install()
        path = self.home / LAYOUTS[0]
        custom = {"id": "agents", "type": "block", "content": {"mod": "other-agents"}}
        path.write_text(json.dumps(custom))
        with self.assertRaisesRegex(ValueError, "refusing to replace a custom view"):
            self.install()
        self.assertEqual(json.loads(path.read_text()), custom)
        self.assertFalse((self.home / MOD).exists())

    def test_symlinks_are_rejected_before_any_install(self):
        destination = self.home / MOD
        destination.parent.mkdir(parents=True, exist_ok=True)
        elsewhere = self.home / "elsewhere"
        elsewhere.mkdir()
        destination.symlink_to(elsewhere, target_is_directory=True)
        before = (self.home / LAYOUTS[0]).read_bytes()
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.install()
        self.assertEqual((self.home / LAYOUTS[0]).read_bytes(), before)
        self.assertEqual(list(elsewhere.iterdir()), [])
