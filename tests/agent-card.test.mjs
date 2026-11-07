import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import test from "node:test";

const root = new URL("../snapshot/.config/herdr-app/mods/workspace-agents/", import.meta.url);
const source = readFileSync(new URL("agent-card.js", root), "utf8");
const { AGENT_CARD_STATES, agentCardData, agentMachineGlyph, agentStateAge, cleanAgentText } = await import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`);
const now = 1800000000000;
const agent = { address: "t1", status: "working", space: "s1", tab: "a1", title: "Pi", subs: [] };
const terminal = { address: "t1", created_ms: now - 900000, status: "working", status_ms: now - 180000, name: "Builder", title: "Pi", report: { msg: "Running tests", progress: 42 } };
const spaces = [{ id: "s1", name: "Portfolio", machine: null, tabs: [{ id: "a1", named: true, name: "Named tab" }] }];

test("cards show actual names, project, host, report, and core state age", () => {
  const card = agentCardData(agent, [terminal], spaces, now);
  assert.equal(card.name, "Builder");
  assert.equal(card.project, "Portfolio");
  assert.equal(card.machine, "Local");
  assert.equal(card.activity, "Running tests");
  assert.equal(card.activityLabel, "REPORTED");
  assert.equal(card.age, "3m");
  assert.equal(card.status.label, "WORKING");
  assert.equal("progress" in card, false);
});

test("session schematics survive status/title changes and viewer address prefixes", () => {
  const glyph = agentMachineGlyph(terminal);
  assert.equal(agentMachineGlyph({ ...terminal, name: "Renamed", title: "New title", status: "blocked" }), glyph);
  assert.equal(agentMachineGlyph({ ...terminal, address: "lombaxPC/t1" }), glyph);
  assert.ok(existsSync(new URL(`schematics/${glyph}.svg`, root)));
  const markers = new Set(Array.from({ length: 40 }, (_, index) => agentMachineGlyph({ ...terminal, address: `t${index}` })));
  assert.equal(markers.size, 6);
});

test("needs-input and report-ready have distinct non-color status shapes", () => {
  assert.equal(AGENT_CARD_STATES.blocked.label, "NEEDS INPUT");
  assert.equal(AGENT_CARD_STATES.done.label, "REPORT READY");
  assert.equal(new Set(Object.values(AGENT_CARD_STATES).map(state => state.icon)).size, 3);
  for (const state of Object.values(AGENT_CARD_STATES)) assert.ok(existsSync(new URL(`schematics/${state.icon}`, root)));
});

test("state age is epoch milliseconds, never connection age or guessed runtime", () => {
  assert.equal(agentStateAge(now - 1000, now), "<1m");
  assert.equal(agentStateAge(now - 2 * 3600000, now), "2h");
  assert.equal(agentStateAge(now - 3 * 86400000, now), "3d");
  for (const since of [undefined, null, 0, -1, NaN, "1800000000000", now + 1000]) assert.equal(agentStateAge(since, now), "");
  const card = agentCardData(agent, [{ ...terminal, status_ms: null }], spaces, now);
  assert.equal(card.age, "");
});

test("a promoted sub-agent supplies its own activity and status clock, not its parent's", () => {
  const sub = { address: "t2", created_ms: now - 300000, status: "blocked", status_ms: now - 60000, report: { msg: "Permission needed" } };
  const card = agentCardData({ ...agent, status: "blocked", subs: [sub] }, [terminal, sub], spaces, now);
  assert.equal(card.name, "Builder");
  assert.equal(card.glyph, agentMachineGlyph(terminal));
  assert.equal(card.activity, "Permission needed");
  assert.equal(card.activityLabel, "SUB-AGENT");
  assert.equal(card.age, "1m");
  assert.equal(card.status.label, "NEEDS INPUT");
});

test("raw error maps to needs-input; unvisited idle completion uses its reported clock", () => {
  assert.equal(agentCardData({ ...agent, status: "blocked" }, [{ ...terminal, status: "error" }], spaces, now).age, "3m");
  const card = agentCardData({ ...agent, status: "done" }, [{ ...terminal, status: "idle" }], spaces, now);
  assert.equal(card.status.label, "REPORT READY");
  assert.equal(card.age, "3m");
});

test("missing reports use clearly labeled terminal titles, never invented task text", () => {
  const card = agentCardData(agent, [{ ...terminal, report: null, title: "Responsive navigation" }], spaces, now);
  assert.equal(card.activity, "Responsive navigation");
  assert.equal(card.activityLabel, "TERMINAL");
  assert.equal(agentCardData(agent, [{ ...terminal, title: "Builder", report: null }], spaces, now).activity, "No activity reported");
  assert.equal(agentCardData(agent, [{ ...terminal, title: "t1", report: null }], spaces, now).activity, "No activity reported");
  assert.equal(agentCardData(agent, [], [], now).age, "");
});

test("blank report messages can fall back to an actual reported title", () => {
  const card = agentCardData(agent, [{ ...terminal, report: { msg: " \n ", title: "Reviewing navigation" } }], spaces, now);
  assert.equal(card.activity, "Reviewing navigation");
  assert.equal(card.activityLabel, "REPORTED");
});

test("named tabs and remote machines remain truthful fallbacks", () => {
  assert.equal(agentCardData(agent, [{ ...terminal, name: null }], spaces, now).name, "Named tab");
  const remote = { ...agent, address: "Mac/t1", space: "missing" };
  assert.equal(agentCardData(remote, [], spaces, now).machine, "Mac");
  assert.equal(cleanAgentText(" Long\n名\t😀\u0000 value "), "Long 名 😀 value");
});
