"""Workspace tickets live on the workspace's machine, never in the dotfiles repo."""

import fcntl
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class Ticket:
    id: str
    title: str
    description: str
    folder: str
    status: str = "todo"
    terminal: str = ""
    context: str = ""
    source: str = ""
    created_at: str = ""


def ticket_prompt(ticket: Ticket) -> str:
    """The ticket's exact title and description are included in every launch mode."""
    return f"Ticket: {ticket.title}\n\n{ticket.description}"


def hc_command(*args: str):
    """Use argv, never shell interpolation, for core commands and ticket content."""
    result = subprocess.run(
        ["hc", args[0], "--json", *args[1:]], capture_output=True, text=True, timeout=20, check=False
    )
    if result.returncode:
        raise ValueError(result.stderr.strip() or "herdr-core command failed")
    return json.loads(result.stdout)


def pi_terminal(terminal: dict) -> bool:
    """Only status-reporting live Pi programs can receive an existing-session prompt."""
    return (terminal.get("state") == "live" and "/" not in terminal.get("address", "")
            and (terminal.get("status") or {}).get("app") == "pi")


def session_metadata(path: Path, folder: Path):
    """Read names and headers only into the result, never conversation messages."""
    try:
        with path.open() as stream:
            header = json.loads(next(stream))
            if header.get("type") != "session" or Path(header.get("cwd", "")).resolve() != folder:
                return None
            name = ""
            for line in stream:
                if '"session_info"' in line:
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue  # A live session may still be appending its final line.
                    if entry.get("type") == "session_info":
                        name = entry.get("name", "")
        return {
            "path": str(path), "name": name or f"Session {header['id'][:8]}",
            "timestamp": header.get("timestamp", ""),
        }
    except (OSError, ValueError, StopIteration):
        return None


class TicketStore:
    def __init__(self, home: Path, workspace: str, folder: str):
        if not workspace or "/" in workspace:
            raise ValueError("Use the workspace's local ID on its own machine")
        self.workspace = workspace
        folder_path = Path(folder) if folder else home
        self.folder = folder_path.resolve()
        if not folder_path.is_absolute() or not self.folder.is_dir():
            raise ValueError("The workspace folder must exist and be absolute")
        self.sessions = home / ".pi/agent/sessions"
        data_home = Path(os.environ.get("XDG_DATA_HOME", str(home / ".local/share")))
        self.root = data_home / "herdr-tickets"
        self.file = self.root / (hashlib.sha256(workspace.encode()).hexdigest() + ".json")

    @contextmanager
    def locked(self):
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        with self.file.with_suffix(".lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if self.file.exists():
                state = json.loads(self.file.read_text())
                if state["version"] != 1 or state["workspace"] != self.workspace:
                    raise ValueError("Unsupported ticket store; no changes were made")
                tickets = [Ticket(**record) for record in state["tickets"]]
            else:
                tickets = []
            yield tickets

    def save(self, tickets: list[Ticket]) -> None:
        descriptor, temporary = tempfile.mkstemp(dir=self.root, prefix=".tickets-")
        try:
            with os.fdopen(descriptor, "w") as stream:
                json.dump({"version": 1, "workspace": self.workspace,
                           "tickets": [asdict(ticket) for ticket in tickets]}, stream)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.file)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def sessions_in_folder(self) -> list[dict]:
        sessions = [session_metadata(path, self.folder) for path in self.sessions.glob("*/*.jsonl")]
        return sorted((session for session in sessions if session),
                      key=lambda session: session["timestamp"], reverse=True)

    def list_tickets(self) -> dict:
        with self.locked() as tickets:
            records = [asdict(ticket) for ticket in tickets]
        terminals = hc_command("ls").get("terminals", [])
        agents = []
        for terminal in terminals:
            if (terminal["state"] == "live" and terminal.get("agent") == "pi"
                    and "/" not in terminal["address"] and Path(terminal["cwd"]).resolve() == self.folder):
                detail = hc_command("get", terminal["address"])
                agents.append({"address": terminal["address"],
                               "title": detail.get("name") or detail.get("title") or terminal["address"],
                               "status": terminal.get("status") or "unknown"})
        by_address = {terminal["address"]: terminal for terminal in terminals}
        for ticket in records:
            terminal = by_address.get(ticket["terminal"])
            ticket["agent_status"] = (terminal.get("status") or "unknown") if terminal else "offline"
        return {"tickets": records, "agents": agents, "sessions": self.sessions_in_folder()}

    def create(self, title: str, description: str) -> dict:
        if not title.strip() or not description.strip():
            raise ValueError("A title and description are required")
        ticket = Ticket(uuid.uuid4().hex, title.strip(), description.strip(), str(self.folder),
                        created_at=datetime.now(UTC).isoformat())
        with self.locked() as tickets:
            tickets.append(ticket)
            self.save(tickets)
        return asdict(ticket)

    def set_status(self, ticket_id: str, status: str) -> dict:
        if status not in {"todo", "running", "done"}:
            raise ValueError("Unknown ticket status")
        with self.locked() as tickets:
            ticket = self.find(tickets, ticket_id)
            if status == "running":
                raise ValueError("Use Start to run a ticket")
            if status == "todo" and ticket.terminal:
                raise ValueError("A started ticket keeps its terminal; create a new ticket for new work")
            ticket.status = status
            self.save(tickets)
            return asdict(ticket)

    @staticmethod
    def find(tickets: list[Ticket], ticket_id: str) -> Ticket:
        for ticket in tickets:
            if ticket.id == ticket_id:
                return ticket
        raise ValueError("Ticket not found in this workspace")

    def start(self, ticket_id: str, mode: str, source: str, tab: str) -> dict:
        if mode not in {"fresh", "fork", "existing"}:
            raise ValueError("Choose fresh, fork, or existing context")
        if not tab or "/" in tab:
            raise ValueError("Choose a tab on this workspace's machine")
        with self.locked() as tickets:
            ticket = self.find(tickets, ticket_id)
            if ticket.status != "todo" or ticket.terminal:
                raise ValueError("This ticket was already started")
            if Path(ticket.folder) != self.folder:
                raise ValueError("The workspace folder changed since this ticket was created")
            if any(other.status == "running" for other in tickets):
                raise ValueError("Finish the running ticket first; this version shares workspace files")
            prompt = ticket_prompt(ticket)
            if mode == "existing":
                if "/" in source:
                    raise ValueError("Choose a terminal on this workspace's machine")
                terminal = hc_command("get", source)
                if (not pi_terminal(terminal) or terminal["status"]["state"] not in {"idle", "done"}
                        or Path(terminal["cwd"]).resolve() != self.folder):
                    raise ValueError("Choose a ready Pi terminal in this workspace folder")
                # Core 0.1.17 cannot express --if done. Never force through a dialog.
                guard = ["--if", "idle"] if terminal["status"]["state"] == "idle" else []
                hc_command("send", *guard, source, prompt)
                address = source
            else:
                argv = ["pi", "--name", ticket.title]
                if mode == "fork":
                    path = Path(source).resolve()
                    if not path.is_relative_to(self.sessions.resolve()) or not session_metadata(path, self.folder):
                        raise ValueError("Choose a saved Pi session from this workspace folder")
                    argv += ["--fork", str(path)]
                result = hc_command(
                    "run", "--bg", "--keep", "--no-parent", "--cwd", str(self.folder),
                    "--label", f"herdr.space={self.workspace}", "--label", f"herdr.tab={tab}",
                    "--label", f"dotfiles.ticket={ticket.id}", "--", *argv, prompt,
                )
                address = result["address"]
            ticket.status, ticket.terminal = "running", address
            ticket.context, ticket.source = mode, source if mode != "fresh" else ""
            self.save(tickets)
            return asdict(ticket)


def handle_request(request: dict, home: Path) -> dict:
    """The UI routes this request to the workspace machine before calling the helper."""
    store = TicketStore(home, request["workspace"], request["folder"])
    action = request["action"]
    if action == "list":
        return store.list_tickets()
    if action == "create":
        return store.create(request["title"], request["description"])
    if action == "status":
        return store.set_status(request["id"], request["status"])
    if action == "start":
        return store.start(request["id"], request["mode"], request.get("source", ""), request["tab"])
    raise ValueError("Unknown ticket action")


if __name__ == "__main__":
    try:
        print(json.dumps(handle_request(json.loads(sys.argv[1]), Path.home())))
    except (ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"error": str(error)}))
        sys.exit(1)
