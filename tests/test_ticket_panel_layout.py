import json
import unittest
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "snapshot/.config/herdr-app"


def layout_node(root, node_id):
    if root.get("id") == node_id:
        return root
    for child in root.get("children", []):
        found = layout_node(child, node_id)
        if found:
            return found
    return None


class TicketPanelLayoutTests(unittest.TestCase):
    def test_tickets_share_the_files_and_changes_panel(self):
        layout = json.loads((APP / "layouts/wide-panels.json").read_text())
        panel = layout_node(layout, "panel")
        body = layout_node(panel, "panel-body")
        self.assertEqual([child["id"] for child in body["children"]], ["files", "changes", "tickets"])
        self.assertEqual(body["children"][2]["content"]["mod"], "workspace-tickets")
        self.assertIsNone(layout_node(layout, "tickets-panel"))
        self.assertEqual(body["active"], "tickets")
        self.assertFalse(panel["hidden"])

    def test_custom_header_exposes_tickets_without_requiring_local_shared_state(self):
        layout = json.loads((APP / "layouts/wide-panels.json").read_text())
        self.assertEqual(layout_node(layout, "tabs")["content"]["mod"], "workspace-tabs")
        header = (APP / "mods/workspace-tabs/main.js").read_text()
        self.assertIn('panelButton("tickets", "Tickets"', header)
        self.assertIn('"tickets"]', header)
