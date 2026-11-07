import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const source = readFileSync(new URL("../snapshot/.config/herdr-app/mods/workspace-agents/agent-groups.js", import.meta.url), "utf8");
const { agentPanelMode, groupActiveAgents, wrapAgentLabel } = await import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`);
const spaces = [{ id: "local", machine: null }, { id: "remote", machine: "lombaxMac" }, { id: "empty", machine: "empty-machine" }];
const agent = (address, status, space = "local", seq = 1) => ({ address, status, space, seq });

test("only attention-worthy agents keep their machine visible", () => {
  const groups = groupActiveAgents([
    agent("t1", "idle"), agent("t2", "unknown"), agent("t3", "working"),
    agent("lombaxMac/t1", "done", "remote"), agent("empty-machine/t1", "idle", "empty"),
  ], [], spaces);
  assert.deepEqual(groups.map(group => [group.machine, group.members.map(a => a.address)]), [[null, ["t3"]], ["lombaxMac", ["lombaxMac/t1"]]]);
});

test("needs-input, done, then working within each machine; newest first on ties", () => {
  const groups = groupActiveAgents([
    agent("t1", "working", "local", 10), agent("t2", "done"),
    agent("t3", "blocked"), agent("t4", "working", "local", 20),
  ], [], spaces);
  assert.deepEqual(groups[0].members.map(a => a.address), ["t3", "t2", "t4", "t1"]);
});

test("a completed agent disappears when Herdr acknowledges its visit", () => {
  assert.equal(groupActiveAgents([agent("t1", "done")], [], spaces).length, 1);
  assert.equal(groupActiveAgents([agent("t1", "idle")], [], spaces).length, 0);
});

test("active nested sub-agents keep an idle parent reachable; settled children do not", () => {
  const parent = agent("t1", "idle");
  const terminals = [
    { address: "t2", parent: "t1", state: "live", status: "idle" },
    { address: "t3", parent: "t2", state: "live", status: "error" },
    { address: "t4", parent: "t1", state: "live", status: "done" },
    { address: "t5", parent: "t1", state: "exited", status: "working" },
  ];
  const groups = groupActiveAgents([parent], terminals, spaces);
  assert.equal(groups[0].members[0].status, "blocked");
  assert.deepEqual(groups[0].members[0].subs.map(sub => sub.address), ["t3"]);
  assert.equal(groupActiveAgents([parent], terminals.filter(t => t.address !== "t3"), spaces).length, 0);
});

test("sub-agents with their own panes are not duplicated beneath parents", () => {
  const groups = groupActiveAgents([agent("t1", "idle"), agent("t2", "working")], [
    { address: "t2", parent: "t1", state: "live", status: "working" },
  ], spaces);
  assert.deepEqual(groups[0].members.map(a => a.address), ["t2"]);
});

test("machine association uses spaces, with remote address fallback", () => {
  const groups = groupActiveAgents([agent("other/t1", "working", "missing")], [], spaces);
  assert.equal(groups[0].machine, "other");
});

test("actual widths select full, wrapping, and rail layouts", () => {
  assert.equal(agentPanelMode(268), "wide");
  assert.equal(agentPanelMode(160), "stacked");
  assert.equal(agentPanelMode(80), "stacked");
  assert.equal(agentPanelMode(76), "rail");
  assert.equal(agentPanelMode(44), "rail");
});

test("long unbroken labels wrap and cap without splitting surrogate pairs", () => {
  assert.equal(wrapAgentLabel("long-machine-name", 5), "long-\nmachi\nne-n…");
  assert.equal(wrapAgentLabel("😀😀😀", 2), "😀😀\n😀");
  assert.equal(wrapAgentLabel("a\n b", 8), "a b");
  assert.equal(wrapAgentLabel("", 0), "");
});
