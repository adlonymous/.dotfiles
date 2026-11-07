"""Exercise the real core with an isolated HOME/session and a fake Pi, never a model."""

import importlib.util
import json
import os
import shlex
import shutil
import subprocess
import tempfile
import time
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

HELPER = (Path(__file__).resolve().parents[1]
          / "snapshot/.config/herdr-app/mods/workspace-tickets/ticket_store.py")
SPEC = importlib.util.spec_from_file_location("integration_ticket_store", HELPER)
tickets = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tickets)

FAKE_PI = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys
import tty

tty.setraw(0)
record = Path(os.environ["TICKET_TEST_RECORD"]) / (os.environ["HC_TERMINAL_ID"] + ".json")
received = ""
def save():
    record.write_text(json.dumps({"argv": sys.argv[1:], "received": received}))
save()
os.write(1, b"\x1b[?2004h\x1b]7501;state=idle:app=pi\x1b\\")
while True:
    chunk = os.read(0, 4096)
    if not chunk:
        break
    received += chunk.decode()
    save()
    os.write(1, b"\x1b]7501;state=done:app=pi\x1b\\")
'''


@unittest.skipUnless(shutil.which("hc"), "herdr-core is not installed")
class TicketCoreIntegrationTests(unittest.TestCase):
    def test_real_core_fresh_fork_and_existing_without_model_calls(self):
        hc = shutil.which("hc")
        with tempfile.TemporaryDirectory(prefix="ticket-core-test-") as temporary:
            home = Path(temporary)
            folder, records, binary = home / "project", home / "records", home / "bin"
            for path in (folder, records, binary, home / "runtime"):
                path.mkdir(mode=0o700)
            fake_pi = binary / "pi"
            fake_pi.write_text(FAKE_PI)
            fake_pi.chmod(0o755)
            environment = {key: value for key, value in os.environ.items()
                           if not key.startswith(("HC_", "HERDR_", "XDG_"))}
            environment.update({
                "HOME": str(home), "HC_SESSION": "ticket-test-" + uuid.uuid4().hex[:12],
                "XDG_RUNTIME_DIR": str(home / "runtime"),
                "XDG_STATE_HOME": str(home / "state"), "XDG_DATA_HOME": str(home / "data"),
                "PATH": str(binary) + os.pathsep + environment["PATH"],
                "TICKET_TEST_RECORD": str(records),
            })
            with patch.dict(os.environ, environment, clear=True):
                subprocess.run([hc, "server", "start"], check=True, capture_output=True, timeout=15)
                try:
                    store = tickets.TicketStore(home, "s-test", str(folder))
                    first = store.create("Fresh title", "Fresh description")
                    started = store.start(first["id"], "fresh", "", "tab-test")
                    first_record = self.wait_record(records, started["terminal"])
                    self.assertEqual(first_record["argv"][-1], "Ticket: Fresh title\n\nFresh description")
                    detail = tickets.hc_command("get", started["terminal"])
                    self.assertEqual(detail["labels"]["herdr.space"], "s-test")
                    self.assertEqual(detail["labels"]["herdr.tab"], "tab-test")
                    self.assertTrue(detail["keep"])
                    store.set_status(first["id"], "done")

                    source = home / ".pi/agent/sessions/project/source.jsonl"
                    source.parent.mkdir(parents=True)
                    source.write_text(json.dumps({"type": "session", "version": 3, "id": "source-id",
                                                 "cwd": str(folder), "timestamp": "2026-11-07T00:00:00Z"}) + "\n")
                    second = store.create("Fork title", "Fork description")
                    forked = store.start(second["id"], "fork", str(source), "tab-test")
                    fork_record = self.wait_record(records, forked["terminal"])
                    self.assertIn("--fork", fork_record["argv"])
                    self.assertIn(str(source), fork_record["argv"])
                    self.assertEqual(fork_record["argv"][-1], "Ticket: Fork title\n\nFork description")
                    store.set_status(second["id"], "done")

                    self.wait_idle(forked["terminal"])
                    third = store.create("Continue title", "Continue description")
                    continued = store.start(third["id"], "existing", forked["terminal"], "tab-test")
                    self.assertEqual(continued["terminal"], forked["terminal"])
                    received = self.wait_record(records, forked["terminal"], "Continue description")["received"]
                    self.assertIn("Ticket: Continue title", received)
                    self.assertIn("Continue description", received)
                    listed = store.list_tickets()
                    self.assertEqual(len(listed["tickets"]), 3)
                    self.assertTrue(listed["agents"])
                    store.set_status(third["id"], "done")
                    self.assertEqual(tickets.hc_command("get", forked["terminal"])["status"]["state"], "done")
                    followup = store.create("Continue completed turn", "Use the same conversation again")
                    store.start(followup["id"], "existing", forked["terminal"], "tab-test")
                    self.wait_record(records, forked["terminal"], "Use the same conversation again")
                    store.set_status(followup["id"], "done")
                    self.check_remote_client(hc, home, environment, store)
                finally:
                    subprocess.run([hc, "server", "stop"], check=True, capture_output=True, timeout=15)

    def check_remote_client(self, hc, home, pc_environment, store):
        viewer = home / "viewer"
        viewer.mkdir()
        (viewer / "runtime").mkdir(mode=0o700)
        environment = dict(pc_environment)
        environment.update(HOME=str(viewer), HC_SESSION="viewer-" + uuid.uuid4().hex[:8],
                           XDG_STATE_HOME=str(viewer / "state"), XDG_DATA_HOME=str(viewer / "data"),
                           XDG_RUNTIME_DIR=str(viewer / "runtime"))
        connector = home / "connect-pc"
        exports = "\n".join(f"export {key}={shlex.quote(pc_environment[key])}" for key in (
            "HOME", "HC_SESSION", "XDG_STATE_HOME", "XDG_DATA_HOME", "XDG_RUNTIME_DIR", "PATH"
        ))
        connector.write_text('#!/bin/sh\n' + exports + '\nexec sh -c "$1"\n')
        connector.chmod(0o755)
        helper = home / ".config/herdr-app/mods/workspace-tickets/ticket_store.py"
        helper.parent.mkdir(parents=True)
        shutil.copy2(HELPER, helper)
        subprocess.run([hc, "server", "start"], env=environment, check=True, capture_output=True, timeout=15)
        try:
            subprocess.run([hc, "machine", "add", "--name", "pc", "--via", str(connector)],
                           env=environment, check=True, capture_output=True, timeout=15)
            def remote(action):
                request = {"workspace": "s-test", "folder": str(store.folder), **action}
                result = subprocess.run([
                    hc, "exec", "--on", "pc", "--", "sh", "-c",
                    'exec python3 "$HOME/.config/herdr-app/mods/workspace-tickets/ticket_store.py" "$1"',
                    "workspace-tickets", json.dumps(request),
                ], env=environment, check=True, capture_output=True, text=True, timeout=20)
                return json.loads(result.stdout)
            created = remote({"action": "create", "title": "Remote task", "description": "From the viewer"})
            started = remote({"action": "start", "id": created["id"], "mode": "fresh", "tab": "tab-test"})
            detail = subprocess.run([hc, "get", "pc/" + started["terminal"], "--json"],
                                    env=environment, check=True, capture_output=True, text=True, timeout=15)
            self.assertEqual(json.loads(detail.stdout)["cwd"], str(store.folder))
            self.assertEqual(len(remote({"action": "list"})["tickets"]), 5)
            self.assertFalse((viewer / "data/herdr-tickets").exists())
        finally:
            subprocess.run([hc, "server", "stop"], env=environment, check=True, capture_output=True, timeout=15)

    def wait_record(self, records, address, contains=""):
        path = records / (address + ".json")
        for _ in range(100):
            try:
                record = json.loads(path.read_text())
                if contains in record["received"]:
                    return record
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            time.sleep(0.05)
        self.fail("Fake Pi did not receive the expected arguments or input")

    def wait_idle(self, address):
        for _ in range(100):
            terminal = tickets.hc_command("get", address)
            if (terminal.get("status") or {}).get("state") == "idle":
                return
            time.sleep(0.05)
        self.fail("Fake Pi did not report idle")
