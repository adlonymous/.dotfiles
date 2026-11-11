#!/usr/bin/env python3
"""Private Hyprland display diagnostics and a non-destructive recovery attempt."""

import argparse
import json
import logging
import os
import select
import socket
import subprocess
import threading
import time
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

DISPLAY_EVENTS = {"monitoradded", "monitoraddedv2", "monitorremoved", "monitorremovedv2", "configreloaded"}
KERNEL_PATTERN = "amdgpu|NVRM|Xid|drm.*(error|fail|timeout)|PM: suspend|PM: resume|suspend entry|suspend exit"


class DisplayLogHandler(RotatingFileHandler):
    """Sync each record so a forced reboot is less likely to lose the failure evidence."""

    def emit(self, record):
        super().emit(record)
        self.flush()
        os.fsync(self.stream.fileno())


def hypr_request(instance: str | None, *args: str):
    """Bound IPC waits so a hung compositor still leaves a diagnostic record."""
    command = ["hyprctl", *(["--instance", instance] if instance else []), *args]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=4)
    except subprocess.TimeoutExpired:
        return {"error": "ipc_timeout"}
    if result.returncode:
        return {"error": "ipc_failed", "code": result.returncode}
    if "-j" in args:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"error": "invalid_ipc_json"}
    return {"ok": True}


def display_instance() -> str | None:
    """Prefer the calling session; never guess between multiple graphical sessions."""
    instances = hypr_request(None, "instances", "-j")
    if not isinstance(instances, list):
        return None
    selected = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    if any(item["instance"] == selected for item in instances):
        return selected
    return instances[0]["instance"] if len(instances) == 1 else None


def display_snapshot(instance: str | None) -> dict:
    """Keep display state and window counts, never titles, command lines, or screenshots."""
    snapshot = {"time": datetime.now(UTC).isoformat(), "session_available": instance is not None}
    snapshot["connectors"] = {}
    for path in Path("/sys/class/drm").glob("card*-*/status"):
        try:
            snapshot["connectors"][path.parent.name] = path.read_text().strip()
        except FileNotFoundError:
            snapshot["connectors"][path.parent.name] = "removed_during_read"
    if instance is None:
        return snapshot
    monitors = hypr_request(instance, "-j", "monitors", "all")
    snapshot["monitors"] = [{key: monitor.get(key) for key in (
        "name", "width", "height", "refreshRate", "dpmsStatus", "disabled")}
        for monitor in monitors] if isinstance(monitors, list) else monitors
    clients = hypr_request(instance, "-j", "clients")
    snapshot["windows"] = {
        "total": len(clients), "mapped": sum(bool(client.get("mapped")) for client in clients),
        "hidden": sum(bool(client.get("hidden")) for client in clients),
    } if isinstance(clients, list) else clients
    return snapshot


def diagnostic_directory() -> Path:
    """Runtime captures stay outside source configuration and dotfiles snapshots."""
    directory = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "display-diagnostics"
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    return directory


def save_display_capture(path: Path, record: dict):
    """Sync the before-state to disk before a recovery command touches the display."""
    with path.open("w") as stream:
        stream.write(json.dumps(record, indent=2) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def capture_display(recover: bool = False) -> Path:
    """Capture before recovery; only request DPMS enable and a Hyprland config reload."""
    instance = display_instance()
    record = {"before": display_snapshot(instance)}
    directory = diagnostic_directory()
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    path = directory / f"capture-{stamp}.json"
    save_display_capture(path, record)
    for old in sorted(directory.glob("capture-*.json"))[:-20]:
        old.unlink()
    if recover:
        if instance is None:
            raise RuntimeError(f"No unambiguous Hyprland session; capture saved: {path}")
        record["recovery"] = [hypr_request(instance, "dispatch", 'hl.dsp.dpms({ action = "enable" })'),
                              hypr_request(instance, "reload")]
        record["after"] = display_snapshot(instance)
        save_display_capture(path, record)
    print(f"Capture saved: {path}")
    if recover:
        print("Display wake/reload attempted. Confirm visually; applications and locks were not terminated.")
        if any("error" in result for result in record["recovery"]):
            raise RuntimeError("Display recovery IPC failed; see the saved capture")
    return path


def record_kernel_lines(logger, process):
    """Persist only GPU/suspend kernel messages before the small system journal rotates."""
    for line in process.stdout:
        logger.info(json.dumps({"kernel": line.strip()[:4096]}))
    logger.warning(json.dumps({"event": "kernel_log_stream_ended", "code": process.wait()}))


def watch_display_session(logger, instance: str):
    """Record display hotplug events immediately, plus a state heartbeat every 30 seconds."""
    runtime = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
    path = runtime / "hypr" / instance / ".socket2.sock"
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(4)
        connection.connect(str(path))
        buffer = b""
        heartbeat = 0
        while True:
            if time.monotonic() >= heartbeat:
                logger.info(json.dumps({"event": "heartbeat", "state": display_snapshot(instance)}))
                heartbeat = time.monotonic() + 30
            ready, _, _ = select.select([connection], [], [], max(0, heartbeat - time.monotonic()))
            if not ready:
                continue
            chunk = connection.recv(65536)
            if not chunk:
                return
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                event = line.partition(b">>")[0].decode("utf-8", errors="replace")
                if event in DISPLAY_EVENTS:
                    # Event payloads can contain names; store only the event type and sanitized state.
                    logger.info(json.dumps({"event": event, "state": display_snapshot(instance)}))


def watch_displays():
    """Keep bounded private logs across monitor power cycles and machine reboots."""
    logger = logging.getLogger("display-diagnostics")
    logger.setLevel(logging.INFO)
    handler = DisplayLogHandler(diagnostic_directory() / "events.log", maxBytes=5 * 1024 * 1024, backupCount=2)
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(handler)
    logger.info(json.dumps({"event": "watch_started"}))
    kernel_command = ["journalctl", "-k", "-b", "--no-pager", "-o", "short-iso", "--grep", KERNEL_PATTERN]
    # With --follow, journalctl did not emit older matches on this host; seed them separately.
    recent = subprocess.run([*kernel_command, "-n", "30"], capture_output=True, text=True, timeout=5)
    for line in recent.stdout.splitlines():
        logger.info(json.dumps({"kernel": line[:4096]}))
    kernel = subprocess.Popen([*kernel_command, "-f", "-n", "0"], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True)
    threading.Thread(target=record_kernel_lines, args=(logger, kernel), daemon=True).start()
    try:
        while True:
            instance = display_instance()
            if instance:
                try:
                    watch_display_session(logger, instance)
                except OSError as error:
                    logger.warning(json.dumps({"event": "display_event_socket_failed", "errno": error.errno}))
            else:
                logger.info(json.dumps({"event": "session_unavailable", "state": display_snapshot(None)}))
            time.sleep(5)
    finally:
        kernel.terminate()
        kernel.wait(timeout=5)
        logger.removeHandler(handler)
        handler.close()


if __name__ == "__main__":
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("watch", "capture", "recover"))
    args = parser.parse_args()
    if args.action == "watch":
        watch_displays()
    else:
        capture_display(args.action == "recover")
