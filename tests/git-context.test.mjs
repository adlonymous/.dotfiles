import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { gitWorkspaceContext, gitTerminalAddress, gitLayoutNode, gitPanelVisible } from "../snapshot/.config/herdr-app/mods/changes-readable/git-context.mjs";

test("workspace machine determines execution, not the viewing computer", () => {
  const pc = gitWorkspaceContext({ id: "pc/s1", machine: "pc", folder: "/pc/project", name: "PC" });
  const mac = gitWorkspaceContext({ id: "s1", machine: null, folder: "/mac/project", name: "Mac" });
  assert.equal(pc.workspace, "s1");
  assert.equal(pc.machine, "pc");
  assert.equal(mac.machine, null);
  assert.equal(gitTerminalAddress(pc, "t1"), "pc/t1");
  assert.equal(gitTerminalAddress(mac, "t1"), "t1");
  assert.notEqual(pc.key, mac.key);
  assert.throws(() => gitTerminalAddress(pc, "other/t1"));
  assert.equal(gitWorkspaceContext(null), null);
});

test("the terminal viewport shares Changes and launches only when visible", () => {
  const tree = JSON.parse(readFileSync(new URL("../snapshot/.config/herdr-app/layouts/wide-panels.json", import.meta.url), "utf8"));
  assert.equal(gitLayoutNode(tree, "changes").type, "column");
  assert.equal(gitLayoutNode(tree, "git-controls").content.mod, "changes-readable");
  assert.equal(gitLayoutNode(tree, "git-terminal").content.props.placeholder, true);
  assert.equal(gitPanelVisible(tree), false);
  gitLayoutNode(tree, "panel-body").active = "changes";
  assert.equal(gitPanelVisible(tree), true);
  gitLayoutNode(tree, "panel").hidden = true;
  assert.equal(gitPanelVisible(tree), false);
});

test("the wrapper delegates Git to Lazygit without ticket coupling or automatic commits", () => {
  const source = readFileSync(new URL("../snapshot/.config/herdr-app/mods/changes-readable/main.js", import.meta.url), "utf8");
  assert.doesNotMatch(source, /workspace-tickets|ticketWorkspaceContext|panes\(|focused\(|action: "commit"|action: "push"/);
  assert.match(source, /gitWorkspaceContext\(spaces\(\).find/);
  assert.match(source, /this.target.machine \|\| ""/);
});
