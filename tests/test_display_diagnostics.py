import json
import os
import socket
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from tools import display_diagnostics as diagnostics
from tools.install_display_diagnostics import (
    BIND_PATH,
    BINDING,
    HELPER_PATH,
    SERVICE_PATH,
    install_display_diagnostics,
)
from tools.sync_config import ROOT


class DisplayDiagnosticsTests(unittest.TestCase):
    def test_session_selection_never_guesses_between_users_sessions(self):
        instances = [{"instance": "one"}, {"instance": "two"}]
        with patch.object(diagnostics, "hypr_request", return_value=instances), patch.dict(os.environ, {"HYPRLAND_INSTANCE_SIGNATURE": ""}):
            self.assertIsNone(diagnostics.display_instance())
        with patch.object(diagnostics, "hypr_request", return_value=instances), patch.dict(os.environ, {"HYPRLAND_INSTANCE_SIGNATURE": "two"}):
            self.assertEqual(diagnostics.display_instance(), "two")
        with patch.object(diagnostics, "hypr_request", return_value=instances[:1]), patch.dict(os.environ, {"HYPRLAND_INSTANCE_SIGNATURE": "stale"}):
            self.assertEqual(diagnostics.display_instance(), "one")

    def test_snapshots_exclude_window_titles_and_command_lines(self):
        monitors = [{"name": "HDMI-A-2", "dpmsStatus": True, "description": "PRIVATE MONITOR NAME"}]
        clients = [{"mapped": True, "hidden": False, "title": "PRIVATE WINDOW TITLE", "initialTitle": "PRIVATE COMMAND"}]
        with patch.object(diagnostics, "hypr_request", side_effect=[monitors, clients]):
            snapshot = diagnostics.display_snapshot("test")
        self.assertNotIn("PRIVATE", json.dumps(snapshot))
        self.assertEqual(snapshot["windows"], {"total": 1, "mapped": 1, "hidden": 0})
        self.assertTrue(snapshot["monitors"][0]["dpmsStatus"])

    def test_event_logs_are_synced_and_rotated(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.log"
            handler = diagnostics.DisplayLogHandler(path, maxBytes=64, backupCount=2)
            self.addCleanup(handler.close)
            with patch.object(diagnostics.os, "fsync", wraps=os.fsync) as sync:
                for _ in range(4):
                    handler.emit(diagnostics.logging.makeLogRecord({"msg": "a" * 60}))
                self.assertEqual(sync.call_count, 4)
            self.assertEqual(len(list(Path(directory).glob("events.log*"))), 3)

    def test_hung_compositor_produces_a_bounded_failure_record(self):
        with patch.object(diagnostics.subprocess, "run", side_effect=subprocess.TimeoutExpired("hyprctl", 4)):
            self.assertEqual(diagnostics.hypr_request("test", "reload"), {"error": "ipc_timeout"})

    def test_recovery_saves_before_state_and_only_wakes_and_reloads(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"XDG_STATE_HOME": directory}), \
                patch.object(diagnostics, "display_instance", return_value="test"), \
                patch.object(diagnostics, "display_snapshot", side_effect=[{"state": "before"}, {"state": "after"}]), \
                patch.object(diagnostics, "hypr_request", return_value={"ok": True}) as request:
            path = diagnostics.capture_display(True)
            data = json.loads(path.read_text())
            self.assertEqual(data["before"], {"state": "before"})
            self.assertEqual(data["after"], {"state": "after"})
            self.assertEqual([call.args for call in request.call_args_list], [
                ("test", "dispatch", 'hl.dsp.dpms({ action = "enable" })'), ("test", "reload"),
            ])

    def test_missing_session_captures_without_attempting_recovery(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"XDG_STATE_HOME": directory}), \
                patch.object(diagnostics, "display_instance", return_value=None), \
                patch.object(diagnostics, "hypr_request") as request:
            for index in range(20):
                (diagnostics.diagnostic_directory() / f"capture-{index:04d}.json").write_text("{}")
            with self.assertRaisesRegex(RuntimeError, "No unambiguous Hyprland session"):
                diagnostics.capture_display(True)
            request.assert_not_called()
            self.assertEqual(len(list(Path(directory).rglob("capture-*.json"))), 20)

    def test_watcher_seeds_old_kernel_matches_before_following_new_events(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"XDG_STATE_HOME": directory}), \
                patch.object(diagnostics.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "GPU fixture\n", "")), \
                patch.object(diagnostics.subprocess, "Popen") as process, \
                patch.object(diagnostics.threading.Thread, "start"), \
                patch.object(diagnostics, "display_instance", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                diagnostics.watch_displays()
            log = (Path(directory) / "display-diagnostics/events.log").read_text()
            self.assertIn("GPU fixture", log)
            command = process.call_args.args[0]
            self.assertIn("-f", command)
            self.assertEqual(command[-2:], ["-n", "0"])

    def test_real_event_socket_records_monitor_events_but_not_titles(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"XDG_RUNTIME_DIR": directory}), \
                patch.object(diagnostics, "display_snapshot", return_value={"state": "fixture"}):
            path = Path(directory) / "hypr/test/.socket2.sock"
            path.parent.mkdir(parents=True)
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
                server.bind(str(path))
                server.listen(1)
                def send_events():
                    connection, _ = server.accept()
                    with connection:
                        connection.sendall(b"windowtitle>>PRIVATE TITLE\nmonitorremoved>>PRIVATE NAME\n")
                worker = threading.Thread(target=send_events)
                worker.start()
                logger = Mock()
                diagnostics.watch_display_session(logger, "test")
                worker.join(timeout=3)
            records = [json.loads(call.args[0]) for call in logger.info.call_args_list]
            self.assertEqual([record["event"] for record in records], ["heartbeat", "monitorremoved"])
            self.assertNotIn("PRIVATE", json.dumps(records))

    def test_installed_cli_capture_is_private_and_never_changes_the_session(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            binary = home / "bin"
            binary.mkdir()
            fake = binary / "hyprctl"
            fake.write_text('#!/usr/bin/env python3\nimport json,sys\n'
                            'if "instances" in sys.argv: print(json.dumps([{"instance":"test"}]))\n'
                            'elif "monitors" in sys.argv: print(json.dumps([{"name":"HDMI-test","dpmsStatus":True}]))\n'
                            'elif "clients" in sys.argv: print(json.dumps([{"title":"PRIVATE","mapped":True}]))\n'
                            'else: raise SystemExit("unexpected mutation")\n')
            fake.chmod(0o755)
            environment = dict(os.environ, HOME=str(home), XDG_STATE_HOME=str(home / "state"), PATH=str(binary) + os.pathsep + os.environ["PATH"])
            subprocess.run(["python3", str(ROOT / "tools/display_diagnostics.py"), "capture"], env=environment, check=True, capture_output=True, timeout=10)
            capture = next((home / "state").rglob("capture-*.json"))
            self.assertEqual(capture.stat().st_mode & 0o777, 0o600)
            self.assertNotIn("PRIVATE", capture.read_text())


class DisplayDiagnosticsInstallTests(unittest.TestCase):
    def test_preview_scoped_backup_and_idempotence(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            binds = home / BIND_PATH
            binds.parent.mkdir(parents=True)
            original = '-- existing bindings\nhl.bind("SUPER + W", hl.dsp.window.close())\n'
            binds.write_text(original)
            idle = binds.parent.parent / "hypridle.conf"
            idle.write_text("existing idle settings")
            changes = install_display_diagnostics(home, ROOT, "Linux", False)
            self.assertIn(HELPER_PATH, changes)
            self.assertEqual(binds.read_text(), original)
            self.assertFalse((home / HELPER_PATH).exists())
            install_display_diagnostics(home, ROOT, "Linux", True)
            self.assertEqual(binds.read_text(), original.rstrip() + "\n\n" + BINDING)
            self.assertEqual(idle.read_text(), "existing idle settings")
            self.assertEqual((home / HELPER_PATH).stat().st_mode & 0o777, 0o755)
            self.assertTrue((home / SERVICE_PATH).is_file())
            self.assertTrue(any(path.read_text() == original for path in (home / ".local/state/dotfiles/backups").rglob("binds.lua")))
            self.assertEqual(install_display_diagnostics(home, ROOT, "Linux", True), [])

    def test_other_platforms_and_binding_conflicts_fail_before_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            with self.assertRaisesRegex(ValueError, "require Linux"):
                install_display_diagnostics(home, ROOT, "Darwin", True)
            binds = home / BIND_PATH
            binds.parent.mkdir(parents=True)
            binds.write_text('hl.bind("SUPER + CTRL + F12", other_action)\n')
            with self.assertRaisesRegex(ValueError, "conflicts"):
                install_display_diagnostics(home, ROOT, "Linux", True)
            self.assertFalse((home / HELPER_PATH).exists())

    def test_destination_symlinks_are_rejected_before_changing_bindings(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            binds = home / BIND_PATH
            binds.parent.mkdir(parents=True)
            binds.write_text("original")
            helper = home / HELPER_PATH
            helper.parent.mkdir(parents=True)
            elsewhere = home / "elsewhere"
            elsewhere.write_text("untouched")
            helper.symlink_to(elsewhere)
            with self.assertRaisesRegex(ValueError, "symlink"):
                install_display_diagnostics(home, ROOT, "Linux", True)
            self.assertEqual(binds.read_text(), "original")
            self.assertEqual(elsewhere.read_text(), "untouched")
