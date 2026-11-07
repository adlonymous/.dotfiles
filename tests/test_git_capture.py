import json
import tempfile
import unittest
from pathlib import Path

from tools.sync_config import portable_text


class GitCaptureTests(unittest.TestCase):
    def test_capture_replaces_runtime_terminal_address_with_placeholder(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            path = home / ".config/herdr-app/layouts/wide-panels.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"id": "root", "children": [
                {"id": "git-controls", "content": {"mod": "changes-readable"}},
                {"id": "git-terminal", "content": {"terminal": "pc/t99"}},
            ]}))
            text = portable_text(path, home)
            self.assertNotIn("pc/t99", text)
            nodes = json.loads(text)["children"]
            self.assertEqual(nodes[0]["content"], {"mod": "changes-readable"})
            self.assertEqual(nodes[1]["content"], {"mod": "changes-readable", "props": {"placeholder": True}})
            self.assertIn("pc/t99", path.read_text())
