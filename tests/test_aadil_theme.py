import json
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from tools.install_aadil_theme import APP, install_aadil_theme
from tools.sync_config import apply, capture, source_files

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "snapshot" / APP


def theme_luminance(color):
    rgb = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in rgb]
    return sum(value * weight for value, weight in zip(linear, [0.2126, 0.7152, 0.0722], strict=True))


def theme_contrast(foreground, background):
    low, high = sorted([theme_luminance(foreground), theme_luminance(background)])
    return (high + 0.05) / (low + 0.05)


class AadilThemeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.app = self.home / APP
        (self.app / "layouts").mkdir(parents=True)
        (self.app / "mods").mkdir()
        self.wide = self.app / "layouts/wide-panels.json"
        layout = json.loads((ASSETS / "layouts/wide-panels.json").read_text())
        layout["font_size"] = 21
        layout["ui_font"] = "Mac UI font"
        layout["children"][0]["size"] = {"px": 197}
        self.wide.write_text(json.dumps(layout))
        self.settings = self.app / "settings.json"
        self.settings.write_text('{"theme":"graphite","font_size":21}')
        self.keys = self.app / "keys.json"
        self.keys.write_text('{"global":{"cmd-t":"tab.new"}}')

    def clone(self, args, **kwargs):
        self.assertEqual(args, ["herdr-app", "do", "layout.clone", "--name", "wide-panels", "--as", "aadil"])
        self.assertTrue(kwargs["check"])
        shutil.copy2(self.wide, self.app / "layouts/aadil.json")

    def test_preview_does_not_clone_or_write(self):
        with patch("tools.install_aadil_theme.subprocess.run") as clone:
            changes = install_aadil_theme(self.home, ROOT, "Darwin", False)
        clone.assert_not_called()
        self.assertIn(APP + "/themes/aadil.json", changes)
        self.assertFalse((self.app / "layouts/aadil.json").exists())
        self.assertFalse((self.home / ".local").exists())

    def test_install_is_separate_preserves_preferences_and_is_idempotent(self):
        before = {path: path.read_text() for path in (self.wide, self.settings, self.keys)}
        with patch("tools.install_aadil_theme.subprocess.run", side_effect=self.clone) as clone:
            install_aadil_theme(self.home, ROOT, "Darwin", True)
            self.assertEqual(install_aadil_theme(self.home, ROOT, "Darwin", True), [])
        self.assertEqual(clone.call_count, 1)
        for path, text in before.items():
            self.assertEqual(path.read_text(), text)
        result = json.loads((self.app / "layouts/aadil.json").read_text())
        for field in ("theme", "colors", "preview", "ui_font"):
            result.pop(field, None)
        original = json.loads(before[self.wide])
        for field in ("theme", "colors", "preview", "ui_font"):
            original.pop(field, None)
        self.assertEqual(result, original)
        self.assertTrue((self.app / "layouts/aadil.svg").is_file())
        self.assertTrue((self.app / "themes/aadil.json").is_file())

    def test_existing_aadil_geometry_is_preserved_on_update(self):
        existing = json.loads(self.wide.read_text())
        existing["font_size"] = 27
        existing["children"][0]["size"] = {"px": 151}
        (self.app / "layouts/aadil.json").write_text(json.dumps(existing))
        with patch("tools.install_aadil_theme.subprocess.run") as clone:
            install_aadil_theme(self.home, ROOT, "Darwin", True)
        clone.assert_not_called()
        result = json.loads((self.app / "layouts/aadil.json").read_text())
        self.assertEqual(result["font_size"], 27)
        self.assertEqual(result["ui_font"], "Ramline")
        self.assertEqual(result["children"][0]["size"], {"px": 151})

    def test_symlink_is_rejected_before_native_clone(self):
        (self.app / "themes").mkdir()
        outside = self.home / "outside"
        outside.write_text("untouched")
        (self.app / "themes/aadil.json").symlink_to(outside)
        with patch("tools.install_aadil_theme.subprocess.run") as clone, self.assertRaisesRegex(ValueError, "symlink"):
            install_aadil_theme(self.home, ROOT, "Darwin", True)
        clone.assert_not_called()
        self.assertEqual(outside.read_text(), "untouched")

    def test_capture_only_includes_owned_layout_theme_and_svg(self):
        (self.app / "installed.json").write_text('{"layout:win98":{}}')
        (self.app / "themes").mkdir()
        for name in ("wide-panels", "win98", "unrelated"):
            (self.app / f"themes/{name}.json").write_text('{}')
        (self.app / "layouts/wide-panels.svg").write_text('<svg/>')
        (self.app / "layouts/win98.json").write_text('{}')
        (self.app / "layouts/win98.svg").write_text('<svg/>')
        paths = {str(path.relative_to(self.home)) for path, _ in source_files(self.home)}
        self.assertIn(APP + "/themes/wide-panels.json", paths)
        self.assertIn(APP + "/layouts/wide-panels.svg", paths)
        self.assertNotIn(APP + "/themes/win98.json", paths)
        self.assertNotIn(APP + "/themes/unrelated.json", paths)
        self.assertNotIn(APP + "/layouts/win98.svg", paths)

    def test_fonts_are_copied_byte_for_byte_and_captured_as_binary(self):
        with patch("tools.install_aadil_theme.subprocess.run", side_effect=self.clone):
            install_aadil_theme(self.home, ROOT, "Darwin", True)
        for weight in ("Heavy", "Light"):
            relative = f"mods/aadil-fonts/fonts/Ramline-{weight}.otf"
            expected = (ASSETS / relative).read_bytes()
            self.assertTrue(expected.startswith(b"OTTO"))
            self.assertEqual((self.app / relative).read_bytes(), expected)
        license_text = (self.app / "mods/aadil-fonts/fonts/LICENSE.txt").read_text()
        self.assertIn("Permission is granted, free of charge", license_text)
        self.assertIn("embed", license_text)
        (self.app / "installed.json").write_text('{}')
        captured = self.home / "captured"
        captured.mkdir()
        capture(self.home, captured)
        destination = self.home / "other-machine"
        destination.mkdir()
        apply(destination, captured, "Darwin", True)
        for weight in ("Heavy", "Light"):
            relative = APP + f"/mods/aadil-fonts/fonts/Ramline-{weight}.otf"
            self.assertEqual((destination / relative).read_bytes(), (self.home / relative).read_bytes())

    def test_palette_has_readable_text_and_distinct_semantic_colors(self):
        palette = json.loads((ASSETS / "themes/aadil.json").read_text())
        self.assertEqual(len(palette["ansi"]), 16)
        for color in [palette["background"], palette["foreground"], *palette["ansi"], *palette["colors"].values()]:
            self.assertRegex(color, r"^#[0-9a-f]{6}$")
        colors = palette["colors"]
        for surface in ("background", "chrome", "selected", "hover"):
            for label in ("foreground", "muted", "dim"):
                self.assertGreaterEqual(theme_contrast(colors[label], colors[surface]), 4.5, (label, surface))
        self.assertGreaterEqual(theme_contrast(colors["solid_foreground"], colors["solid"]), 4.5)
        self.assertNotEqual(palette["ansi"][1], palette["ansi"][2])
        self.assertEqual(len({colors[key] for key in ("working", "blocked", "done")}), 3)
        ET.parse(ASSETS / "layouts/aadil.svg")
