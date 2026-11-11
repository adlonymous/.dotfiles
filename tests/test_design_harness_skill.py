import json
import re
import unittest

from tools.sync_config import ROOT, check_secrets

SKILL = ROOT / "snapshot/.pi/agent/skills/design-harness"


class DesignHarnessSkillTests(unittest.TestCase):
    def test_wrapper_routes_before_design_without_forcing_the_reference_brand(self):
        text = (SKILL / "SKILL.md").read_text()
        self.assertTrue(text.startswith("---\nname: design-harness\n"))
        description = re.search(r"^description: (.+)$", text, re.MULTILINE).group(1)
        self.assertLessEqual(len(description), 1024)
        self.assertIn("Read before any visual design or UI work", description)
        self.assertIn("existing visual identity", description)
        self.assertLess(len(text.splitlines()), 500)
        self.assertNotIn("disable-model-invocation: true", text)
        self.assertIn("do not authorize deployments", text)

    def test_wrapper_links_resolve_within_the_bundled_skill(self):
        links = re.findall(r"\]\(([^)]+)\)", (SKILL / "SKILL.md").read_text())
        self.assertGreater(len(links), 20)
        for link in links:
            with self.subTest(link=link):
                self.assertTrue((SKILL / link).is_file())
                self.assertTrue((SKILL / link).resolve().is_relative_to(SKILL.resolve()))

    def test_complete_markdown_bundle_has_manifest_coverage_and_no_binary_assets(self):
        references = [path for path in (SKILL / "references").rglob("*") if path.is_file()]
        self.assertEqual(len(references), 131)
        self.assertTrue(all(path.suffix == ".md" for path in references))
        manifest = json.loads((ROOT / "snapshot/manifest.json").read_text())
        managed = {entry["path"]: entry for entry in manifest["files"]}
        for path in SKILL.rglob("*"):
            if path.is_file():
                relative = path.relative_to(ROOT / "snapshot").as_posix()
                self.assertEqual(managed[relative]["platform"], "all")
                check_secrets(path.read_text(), relative)

    def test_attribution_and_license_restrictions_are_preserved(self):
        source = (SKILL / "SOURCES.md").read_text()
        self.assertIn("Ahmed Saleh", source)
        self.assertIn("https://saleh.digital", source)
        self.assertIn("CC BY 4.0", source)
        self.assertIn("without modification", source)
        original = (SKILL / "references/README.md").read_text()
        for name in ("Shinka", "Kult Luxury", "Amicons"):
            self.assertIn(name, original)
            self.assertIn(name, source)

    def test_global_instructions_require_the_design_skill(self):
        instructions = (ROOT / "snapshot/.pi/agent/AGENTS.md").read_text()
        self.assertIn("# Design work\n", instructions)
        self.assertIn("~/.pi/agent/skills/design-harness/SKILL.md", instructions)
        self.assertIn("required task-relevant reference files", instructions)
