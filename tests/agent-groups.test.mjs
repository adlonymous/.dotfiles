import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const source = readFileSync(new URL("../snapshot/.config/herdr-app/mods/workspace-agents/agent-groups.js", import.meta.url), "utf8");
const { agentPanelMode, groupMachineAgents, wrapAgentLabel } = await import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`);
const spaces = [{ id: "local", machine: null }, { id: "remote", machine: "lombaxMac" }, { id: "empty", machine: "empty-machine" }];
const agent = (address, status, space = "local", seq = 1) => ({ address, status, space, seq });

test("idle agents keep their machine visible; unknown agents and empty machines stay hidden", () => {
  const groups = groupMachineAgents([
    agent("t1", "idle"), agent("t2", "unknown"), agent("t3", "working"),
    agent("lombaxMac/t1", "done", "remote"), agent("empty-machine/t1", "idle", "empty"),
  ], [], spaces);
  assert.deepEqual(groups.map(group => [group.machine, group.members.map(a => a.address)]),
    [[null, ["t3", "t1"]], ["lombaxMac", ["lombaxMac/t1"]], ["empty-machine", ["empty-machine/t1"]]]);
  assert.equal(groupMachineAgents([agent("t1", "unknown")], [], spaces).length, 0);
  assert.equal(groupMachineAgents([], [], spaces).length, 0);
});

test("needs-input, done, working, then idle within each machine; newest first on ties", () => {
  const groups = groupMachineAgents([
    agent("t1", "working", "local", 10), agent("t2", "done"), agent("t5", "idle", "local", 100),
    agent("t3", "blocked"), agent("t4", "working", "local", 20), agent("t6", "idle", "local", 200),
  ], [], spaces);
  assert.deepEqual(groups[0].members.map(a => a.address), ["t3", "t2", "t4", "t1", "t6", "t5"]);
});

test("a visited completed agent moves to idle instead of disappearing", () => {
  const done = groupMachineAgents([agent("t1", "done")], [], spaces)[0].members[0];
  const idle = groupMachineAgents([agent("t1", "idle")], [], spaces)[0].members[0];
  assert.equal(done.address, idle.address);
  assert.equal(done.status, "done");
  assert.equal(idle.status, "idle");
});

test("active nested sub-agents promote idle parents; settled children leave the parent idle", () => {
  const parent = agent("t1", "idle");
  const terminals = [
    { address: "t2", parent: "t1", state: "live", status: "idle" },
    { address: "t3", parent: "t2", state: "live", status: "error" },
    { address: "t4", parent: "t1", state: "live", status: "done" },
    { address: "t5", parent: "t1", state: "exited", status: "working" },
  ];
  const groups = groupMachineAgents([parent], terminals, spaces);
  assert.equal(groups[0].members[0].status, "blocked");
  assert.deepEqual(groups[0].members[0].subs.map(sub => sub.address), ["t3"]);
  const settled = groupMachineAgents([parent], terminals.filter(t => t.address !== "t3"), spaces)[0].members[0];
  assert.equal(settled.status, "idle");
  assert.deepEqual(settled.subs, []);
});

test("sub-agents with their own panes are not duplicated beneath parents", () => {
  const groups = groupMachineAgents([agent("t1", "idle"), agent("t2", "working")], [
    { address: "t2", parent: "t1", state: "live", status: "working" },
  ], spaces);
  assert.deepEqual(groups[0].members.map(a => a.address), ["t2", "t1"]);
  assert.deepEqual(groups[0].members[1].subs, []);
});

test("machine association uses spaces, with remote address fallback", () => {
  const groups = groupMachineAgents([agent("other/t1", "working", "missing")], [], spaces);
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
  assert.equal(wrapAgentLabel("Portfolio fixture · Local", 24, 2), "Portfolio fixture ·\nLocal");
  assert.equal(wrapAgentLabel("", 0), "");
});
