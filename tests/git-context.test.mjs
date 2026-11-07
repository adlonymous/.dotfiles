import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { gitWorkspaceContext, gitPushProtected } from "../snapshot/.config/herdr-app/mods/changes-readable/git-context.mjs";

test("Git uses the workspace host and its first terminal, not keyboard focus", () => {
  const space = { id: "pc/s1", machine: "pc", folder: "/pc/home", name: "PC", tabs: [{ id: "pc/tab1" }, { id: "pc/tab2" }] };
  const panes = [
    { tab: "other/tab1", terminal: "other/t1", cwd: "/unrelated", focused: true },
    { tab: "pc/tab2", terminal: "pc/t2", cwd: "/second" },
    { tab: "pc/tab1", terminal: "pc/t1", cwd: "/project" },
  ];
  assert.equal(gitWorkspaceContext(space, panes).folder, "/project");
  assert.equal(gitWorkspaceContext(space, panes).machine, "pc");
  assert.equal(gitWorkspaceContext(space, []).folder, "/pc/home");
  assert.equal(gitWorkspaceContext({ ...space, machine: null }).machine, null);
  assert.equal(gitWorkspaceContext(null), null);
});

test("default, detached and unborn branches are not pushable", () => {
  for (const branch of ["main", "master", "production", ""]) {
    assert.equal(gitPushProtected({ head: "abc", branch, default_branch: "production" }), true);
  }
  assert.equal(gitPushProtected({ head: "", branch: "feat/work" }), true);
  assert.equal(gitPushProtected({ head: "abc", branch: "feat/work", default_branch: "main" }), false);
});

test("Changes is one native mod with no embedded terminal or ticket coupling", () => {
  const tree = JSON.parse(readFileSync(new URL("../snapshot/.config/herdr-app/layouts/wide-panels.json", import.meta.url), "utf8"));
  const text = JSON.stringify(tree);
  assert.doesNotMatch(text, /git-terminal|git-controls/);
  const source = readFileSync(new URL("../snapshot/.config/herdr-app/mods/changes-readable/main.js", import.meta.url), "utf8");
  assert.doesNotMatch(source, /lazygit|workspace-tickets|focused\(|writeTextFile|terminal\.open|terminal\.keep/);
  assert.match(source, /action: "commit", message: this.input.value\(\)/);
  assert.match(source, /git-confirm-/);
  assert.doesNotMatch(source, /"add", "-A"|--force|--no-verify/);
});
