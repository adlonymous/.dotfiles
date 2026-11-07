import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HELPER = (Path(__file__).resolve().parents[1]
          / "snapshot/.config/herdr-app/mods/workspace-tickets/ticket_store.py")
SPEC = importlib.util.spec_from_file_location("ticket_store", HELPER)
tickets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tickets)


class WorkspaceTicketTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.folder = self.home / "project with spaces"
        self.folder.mkdir()
        self.environment = patch.dict(os.environ, {"XDG_DATA_HOME": str(self.home / "data")})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.store = tickets.TicketStore(self.home, "s1", str(self.folder))

    def ticket(self):
        return self.store.create("Repair login", "Keep the existing login behavior.\nAdd regression tests.")

    def session(self, folder=None, name="Login decisions"):
        path = self.home / ".pi/agent/sessions/project/session.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps(entry) for entry in [
            {"type": "session", "id": "session-123", "cwd": str(folder or self.folder),
             "timestamp": "2026-11-07T12:00:00Z"},
            {"type": "session_info", "name": name},
            {"type": "message", "message": {"role": "user", "content": "PRIVATE CONVERSATION"}},
        ]) + "\n")
        return path

    def terminal(self, state="idle", app="pi"):
        return {"address": "t7", "state": "live", "cwd": str(self.folder),
                "status": {"state": state, "app": app}, "title": "Login agent"}

    def test_ticket_persists_and_isolated_by_workspace(self):
        ticket = self.ticket()
        with patch.object(tickets, "hc_command", return_value={"terminals": []}):
            restored = tickets.TicketStore(self.home, "s1", str(self.folder)).list_tickets()
            other = tickets.TicketStore(self.home, "s2", str(self.folder)).list_tickets()
        self.assertEqual(restored["tickets"][0]["title"], ticket["title"])
        self.assertEqual(other["tickets"], [])
        self.assertEqual(self.store.file.stat().st_mode & 0o777, 0o600)

    def test_workspace_without_folder_uses_its_machines_home(self):
        store = tickets.TicketStore(self.home, "home-space", "")
        self.assertEqual(store.create("Home task", "Details")["folder"], str(self.home))

    def test_title_and_description_required(self):
        for title, description in [(" ", "details"), ("title", " ")]:
            with self.subTest(title=title), self.assertRaises(ValueError):
                self.store.create(title, description)

    def test_sessions_expose_metadata_not_conversations(self):
        self.session()
        sessions = self.store.sessions_in_folder()
        self.assertEqual(sessions[0]["name"], "Login decisions")
        self.assertNotIn("PRIVATE CONVERSATION", json.dumps(sessions))
        self.session(folder=self.home)
        self.assertEqual(self.store.sessions_in_folder(), [])

    def test_fresh_start_has_exact_prompt_and_workspace_labels(self):
        ticket = self.store.create("Title $(touch bad)", "Description; not a shell command")
        with patch.object(tickets, "hc_command", return_value={"address": "t9"}) as command:
            result = self.store.start(ticket["id"], "fresh", "", "tab1")
        args = command.call_args.args
        self.assertIn("herdr.space=s1", args)
        self.assertIn("herdr.tab=tab1", args)
        self.assertIn("--no-parent", args)
        self.assertEqual(args[-1], "Ticket: Title $(touch bad)\n\nDescription; not a shell command")
        self.assertEqual(result["terminal"], "t9")
        self.assertEqual(result["status"], "running")
        self.assertFalse((self.folder / "bad").exists())

    def test_fork_uses_new_pi_session_without_modifying_source(self):
        source = self.session()
        original = source.read_bytes()
        ticket = self.ticket()
        with patch.object(tickets, "hc_command", return_value={"address": "t9"}) as command:
            result = self.store.start(ticket["id"], "fork", str(source), "tab1")
        args = command.call_args.args
        self.assertIn("--fork", args)
        self.assertNotIn("--session", args)
        self.assertEqual(args[args.index("--fork") + 1], str(source))
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(result["source"], str(source))

    def test_fork_rejects_another_folder_or_outside_sessions(self):
        ticket = self.ticket()
        source = self.session(folder=self.home)
        for path in [str(source), str(self.home / "auth.json")]:
            with self.subTest(path=path), patch.object(tickets, "hc_command") as command:
                with self.assertRaisesRegex(ValueError, "saved Pi session"):
                    self.store.start(ticket["id"], "fork", path, "tab1")
                command.assert_not_called()

    def test_existing_requires_idle_pi_and_uses_guarded_send(self):
        ticket = self.ticket()
        with patch.object(tickets, "hc_command", side_effect=[self.terminal(), {}]) as command:
            result = self.store.start(ticket["id"], "existing", "t7", "tab1")
        self.assertEqual(command.call_args.args[:4], ("send", "--if", "idle", "t7"))
        self.assertIn(ticket["description"], command.call_args.args[-1])
        self.assertEqual(result["terminal"], "t7")

    def test_completed_pi_turn_can_continue_without_forcing_a_dialog(self):
        ticket = self.ticket()
        with patch.object(tickets, "hc_command", side_effect=[self.terminal("done"), {}]) as command:
            result = self.store.start(ticket["id"], "existing", "t7", "tab1")
        self.assertEqual(command.call_args.args[:2], ("send", "t7"))
        self.assertNotIn("--force", command.call_args.args)
        self.assertEqual(result["terminal"], "t7")

    def test_busy_blocked_and_other_programs_are_not_prompted(self):
        ticket = self.ticket()
        for state, app in [("working", "pi"), ("blocked", "pi"), ("idle", "shell")]:
            with self.subTest(state=state), patch.object(tickets, "hc_command", return_value=self.terminal(state, app)) as command:
                with self.assertRaisesRegex(ValueError, "ready Pi terminal"):
                    self.store.start(ticket["id"], "existing", "t7", "tab1")
                self.assertEqual(command.call_count, 1)

    def test_double_start_and_parallel_ticket_are_refused(self):
        first, second = self.ticket(), self.ticket()
        with patch.object(tickets, "hc_command", return_value={"address": "t9"}) as command:
            self.store.start(first["id"], "fresh", "", "tab1")
            with self.assertRaisesRegex(ValueError, "already started"):
                self.store.start(first["id"], "fresh", "", "tab1")
            with self.assertRaisesRegex(ValueError, "Finish the running ticket"):
                self.store.start(second["id"], "fresh", "", "tab1")
            self.assertEqual(command.call_count, 1)

    def test_failed_launch_keeps_ticket_todo(self):
        ticket = self.ticket()
        with (patch.object(tickets, "hc_command", side_effect=ValueError("core offline")),
              self.assertRaisesRegex(ValueError, "core offline")):
            self.store.start(ticket["id"], "fresh", "", "tab1")
        with self.store.locked() as records:
            self.assertEqual(records[0].status, "todo")
            self.assertEqual(records[0].terminal, "")

    def test_idle_is_not_automatic_completion(self):
        ticket = self.ticket()
        with patch.object(tickets, "hc_command", return_value={"address": "t7"}):
            self.store.start(ticket["id"], "fresh", "", "tab1")
        with patch.object(tickets, "hc_command", return_value={"terminals": [
            {"address": "t7", "state": "live", "cwd": str(self.folder), "agent": "pi", "status": "idle"}
        ]}):
            record = self.store.list_tickets()["tickets"][0]
        self.assertEqual(record["status"], "running")
        self.assertEqual(record["agent_status"], "idle")
        with patch.object(tickets, "hc_command") as command:
            self.store.set_status(ticket["id"], "done")
            command.assert_not_called()

    def test_existing_candidates_include_the_terminal_title(self):
        listed = {"terminals": [{"address": "t7", "state": "live", "agent": "pi",
                                  "status": "idle", "cwd": str(self.folder)}]}
        with patch.object(tickets, "hc_command", side_effect=[listed, self.terminal()]):
            result = self.store.list_tickets()
        self.assertEqual(result["agents"][0]["title"], "Login agent")
        self.assertEqual(result["agents"][0]["status"], "idle")

    def test_remote_addresses_cannot_be_routed_to_local_core(self):
        ticket = self.ticket()
        for mode, source, tab in [("fresh", "", "pc/tab1"), ("existing", "pc/t7", "tab1")]:
            with self.subTest(mode=mode), patch.object(tickets, "hc_command") as command:
                with self.assertRaises(ValueError):
                    self.store.start(ticket["id"], mode, source, tab)
                command.assert_not_called()

    def test_json_flag_is_not_forwarded_to_pi(self):
        response = subprocess.CompletedProcess([], 0, '{"address":"t9"}', '')
        with patch.object(tickets.subprocess, "run", return_value=response) as run:
            tickets.hc_command("run", "--bg", "--", "pi", "ticket prompt")
        self.assertEqual(run.call_args.args[0], ["hc", "run", "--json", "--bg", "--", "pi", "ticket prompt"])


if __name__ == "__main__":
    unittest.main()
