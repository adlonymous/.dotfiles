import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools/sync_config.py"
SPEC = importlib.util.spec_from_file_location("sync_config", MODULE_PATH)
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


class ConfigSyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.target = self.root / "target"
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.target.mkdir()
        app = self.source / ".config/herdr-app"
        (app / "layouts").mkdir(parents=True)
        (app / "mods/shipped").mkdir(parents=True)
        (app / "mods/custom").mkdir()
        (app / "installed.json").write_text('{"shipped": {}, "layout:main": {}}')
        (app / "layouts/main.json").write_text('{}')
        (app / "layouts/personal.json").write_text('{"id":"root"}')
        (app / "mods/shipped/main.js").write_text('shipped')
        (app / "mods/custom/main.js").write_text('custom')
        (app / "mods/custom/gpui-kit.d.ts").write_text('generated')
        (app / "mods/custom/__pycache__").mkdir()
        (app / "mods/custom/__pycache__/helper.pyc").write_bytes(b'\x00\xff')
        (app / "mods/custom/.env").write_text('PRIVATE=value')
        (app / "settings.json").write_text('{"font_size":16}')
        pi = self.source / ".pi/agent"
        (pi / "extensions").mkdir(parents=True)
        (pi / "AGENTS.md").write_text(
            '# Instructions\n# Privileged commands\n- Linux Polkit instruction\n\n# Git\n- Keep branches\n'
        )
        (pi / "settings.json").write_text(json.dumps({"theme": "source-theme", "path": str(self.source)}))
        (pi / "auth.json").write_text('private runtime authentication')
        (pi / "extensions/polkit-sudo-guard.ts").write_text('linux guard')
        skills = pi / "skills/my-skill/scripts"
        skills.mkdir(parents=True)
        (skills.parent / "SKILL.md").write_text('skill instructions')
        script = skills / "run.sh"
        script.write_text('#!/bin/sh\necho example\n')
        script.chmod(0o755)
        sync.capture(self.source, self.repo)

    def test_capture_excludes_runtime_and_generated_files(self):
        paths = {entry['path'] for entry in json.loads((self.repo / 'snapshot/manifest.json').read_text())['files']}
        self.assertNotIn('.pi/agent/auth.json', paths)
        self.assertNotIn('.config/herdr-app/mods/shipped/main.js', paths)
        self.assertNotIn('.config/herdr-app/layouts/main.json', paths)
        self.assertNotIn('.config/herdr-app/mods/custom/gpui-kit.d.ts', paths)
        self.assertNotIn('.config/herdr-app/mods/custom/__pycache__/helper.pyc', paths)
        self.assertNotIn('.config/herdr-app/mods/custom/.env', paths)
        self.assertIn('.config/herdr-app/mods/custom/main.js', paths)
        self.assertIn('.config/herdr-app/layouts/personal.json', paths)

    def test_dry_run_does_not_create_configuration_or_backups(self):
        self.assertTrue(sync.apply(self.target, self.repo, 'Linux', False))
        self.assertEqual(list(self.target.iterdir()), [])

    def test_apply_rebases_paths_and_is_idempotent(self):
        sync.apply(self.target, self.repo, 'Linux', True)
        settings = json.loads((self.target / '.pi/agent/settings.json').read_text())
        self.assertEqual(settings['path'], str(self.target))
        self.assertEqual(sync.apply(self.target, self.repo, 'Linux', True), [])

    def test_apply_preserves_executable_mode(self):
        sync.apply(self.target, self.repo, 'Linux', True)
        script = self.target / '.pi/agent/skills/my-skill/scripts/run.sh'
        self.assertEqual(script.stat().st_mode & 0o777, 0o755)

    def test_apply_backs_up_existing_config_and_leaves_credentials(self):
        pi = self.target / '.pi/agent'
        pi.mkdir(parents=True)
        (pi / 'settings.json').write_text('{"old": true}')
        (pi / 'auth.json').write_text('local secret stays here')
        sync.apply(self.target, self.repo, 'Linux', True)
        backups = list(self.target.glob('.local/state/dotfiles/backups/*/.pi/agent/settings.json'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), '{"old": true}')
        self.assertEqual((pi / 'auth.json').read_text(), 'local secret stays here')

    def test_mac_skips_linux_guard_and_changes_privilege_instruction(self):
        sync.apply(self.target, self.repo, 'Darwin', True)
        pi = self.target / '.pi/agent'
        self.assertFalse((pi / 'extensions/polkit-sudo-guard.ts').exists())
        self.assertIn('On macOS', (pi / 'AGENTS.md').read_text())
        self.assertNotIn('Linux Polkit instruction', (pi / 'AGENTS.md').read_text())

    def test_rejects_destination_symlink_before_any_write(self):
        elsewhere = self.root / 'elsewhere'
        elsewhere.mkdir()
        (self.target / '.pi').symlink_to(elsewhere)
        with self.assertRaisesRegex(ValueError, 'destination symlink'):
            sync.apply(self.target, self.repo, 'Linux', True)
        self.assertEqual(list(elsewhere.iterdir()), [])
        self.assertFalse((self.target / '.config').exists())

    def test_rejects_path_traversal(self):
        for path in ['../outside', '/tmp/outside', 'a/../../outside']:
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'Invalid managed path'):
                sync.target_path(self.target, path)

    def test_rejects_secret_without_changing_previous_snapshot(self):
        previous = (self.repo / 'snapshot/.pi/agent/settings.json').read_text()
        (self.source / '.pi/agent/settings.json').write_text('{"apiKey":"a-real-literal-credential"}')
        with self.assertRaisesRegex(ValueError, 'Review literal apiKey'):
            sync.capture(self.source, self.repo)
        self.assertEqual((self.repo / 'snapshot/.pi/agent/settings.json').read_text(), previous)

    def test_rejects_private_key_without_printing_it(self):
        with self.assertRaisesRegex(ValueError, 'Possible credential in example'):
            sync.check_secrets('-----BEGIN OPENSSH PRIVATE KEY-----', 'example')

    def test_local_model_dummy_keys_and_environment_references_are_allowed(self):
        sync.check_secrets('{"apiKey":"ollama"}', 'models.json')
        sync.check_secrets('{"apiKey":"$MODEL_API_KEY"}', 'models.json')


if __name__ == '__main__':
    unittest.main()
