"""Verify both workspace-local and remote Lazygit through isolated real cores."""

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

MOD = Path(__file__).resolve().parents[1] / "snapshot/.config/herdr-app/mods/changes-readable"


@unittest.skipUnless(shutil.which("hc") and shutil.which("lazygit"), "hc and lazygit are required")
class GitCoreIntegrationTests(unittest.TestCase):
    def test_lazygit_runs_on_each_workspaces_machine_and_reuses_live_sessions(self):
        hc = shutil.which("hc")
        with tempfile.TemporaryDirectory(prefix="git-core-test-") as temporary:
            root = Path(temporary)
            environments = []
            for name in ("pc", "viewer"):
                home = root / name
                home.mkdir()
                (home / "runtime").mkdir(mode=0o700)
                environment = {key: value for key, value in os.environ.items()
                               if not key.startswith(("HC_", "HERDR_", "XDG_", "GIT_", "GH_", "GITHUB_"))}
                environment.update(HOME=str(home), HC_SESSION="git-test-" + uuid.uuid4().hex[:12],
                                   XDG_CONFIG_HOME=str(home / ".config"), XDG_RUNTIME_DIR=str(home / "runtime"),
                                   XDG_STATE_HOME=str(home / "state"), XDG_DATA_HOME=str(home / "data"),
                                   GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
                destination = home / ".config/herdr-app/mods/changes-readable"
                destination.mkdir(parents=True)
                for filename in ("git_backend.py", "lazygit.yml"):
                    shutil.copy2(MOD / filename, destination / filename)
                environments.append(environment)
            pc, viewer = environments
            connector = root / "connect-workspace"
            exports = "\n".join(f"export {key}={shlex.quote(value)}" for key, value in pc.items()
                                if key in {"HOME", "HC_SESSION", "XDG_CONFIG_HOME", "XDG_RUNTIME_DIR", "XDG_STATE_HOME",
                                           "XDG_DATA_HOME", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM", "PATH"})
            connector.write_text('#!/bin/sh\n' + exports + '\nexec sh -c "$1"\n')
            connector.chmod(0o755)
            started = []
            try:
                for environment in environments:
                    subprocess.run([hc, "server", "start"], env=environment, check=True, capture_output=True, timeout=15)
                    started.append(environment)
                subprocess.run([hc, "machine", "add", "--name", "pc", "--via", str(connector)],
                               env=viewer, check=True, capture_output=True, timeout=15)
                def request(machine, action, **values):
                    result = subprocess.run([
                        hc, "exec", *(["--on", machine] if machine else []), "--", "sh", "-c",
                        'exec python3 "$XDG_CONFIG_HOME/herdr-app/mods/changes-readable/git_backend.py" "$1"',
                        "workspace-git", json.dumps({"action": action, "workspace": "s1", **values}),
                    ], env=viewer, check=False, capture_output=True, text=True, timeout=35)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    return json.loads(result.stdout)
                addresses = []
                for machine, environment in [("pc", pc), (None, viewer)]:
                    project = request(machine, "project-create", name="project", parent=str(Path(environment["HOME"]) / "Projects"))
                    folder = project["folder"]
                    self.assertTrue(Path(folder).is_relative_to(Path(environment["HOME"])))
                    session = request(machine, "open", folder=folder)
                    address = (machine + "/" if machine else "") + session["terminal"]
                    addresses.append(address)
                    self.assertEqual(request(machine, "open", folder=folder)["terminal"], session["terminal"])
                    subfolder = Path(folder) / "src"
                    subfolder.mkdir()
                    self.assertEqual(request(machine, "open", folder=str(subfolder))["terminal"], session["terminal"])
                    for _ in range(100):
                        screen = subprocess.run([hc, "read", address, "--lines", "100"], env=viewer,
                                                capture_output=True, text=True, timeout=10)
                        if "README.md" in screen.stdout:
                            break
                        time.sleep(0.05)
                    else:
                        self.fail("Lazygit did not render the new project's README: " + screen.stdout)
                    detail = subprocess.run([hc, "get", address, "--json"], env=viewer,
                                            check=True, capture_output=True, text=True, timeout=10)
                    self.assertEqual(json.loads(detail.stdout)["cwd"], folder)
                    subprocess.run([hc, "keys", address, "2", "down", "space"], env=viewer,
                                   check=True, capture_output=True, timeout=10)
                    for _ in range(100):
                        staged = subprocess.run(["git", "ls-files"], cwd=folder, env=environment,
                                                check=True, capture_output=True, text=True).stdout.splitlines()
                        if staged:
                            break
                        time.sleep(0.05)
                    self.assertEqual(len(staged), 1, "Lazygit must stage only the selected file")
                    subprocess.run([hc, "keys", address, "q"], env=viewer, check=True, capture_output=True, timeout=10)
                    for _ in range(100):
                        if request(machine, "session", folder=folder)["terminal"] is None:
                            break
                        time.sleep(0.05)
                    else:
                        self.fail("Quitting Lazygit left the session live")
                self.assertTrue(addresses[0].startswith("pc/"))
                self.assertNotIn("/", addresses[1])
            finally:
                for environment in reversed(started):
                    subprocess.run([hc, "server", "stop"], env=environment, check=True, capture_output=True, timeout=15)
