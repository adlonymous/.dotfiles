import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const root = new URL("../snapshot/.config/herdr-app/mods/workspace-agents/", import.meta.url);
const load = name => import(`data:text/javascript;base64,${Buffer.from(readFileSync(new URL(name, root))).toString("base64")}`);
const helpers = { ...await load("agent-groups.js"), ...await load("agent-card.js") };

// Record descriptions/events; the native mod check validates the real builder API.
function element() {
  const node = { nodes: [], attributes: {} };
  const proxy = new Proxy(node, {
    get(target, key) {
      if (key in target) return target[key];
      return (...args) => {
        if (key === "child" && args[0] != null) target.nodes.push(args[0]);
        else if (key === "children") target.nodes.push(...args[0]);
        else if (key === "when") { if (args[0]) args[1](proxy); }
        else target.attributes[key] = args.length ? args[0] : true;
        return proxy;
      };
    },
  });
  return proxy;
}
function find(node, id) {
  if (typeof node !== "object" || node === null) return null;
  if (node.attributes.id === id) return node;
  for (const child of node.nodes) {
    const found = find(child, id);
    if (found) return found;
  }
  return null;
}
function sidebar() {
  const list = [
    { address: "t1", status: "idle", space: "local", pane: "p1", seq: 1 },
    { address: "t2", status: "working", space: "local", pane: "p2", seq: 2 },
  ];
  const calls = [];
  const environment = {
    ...helpers, View: class {}, div: element, svg: element, v_flex: element, h_flex: element,
    agents: () => list, terminals: () => list, spaces: () => [{ id: "local", machine: null }],
    theme: () => ({ dim: "muted", working: "working" }),
    run: (...args) => calls.push(args), setAgentOrder: () => {},
  };
  const source = readFileSync(new URL("main.js", root), "utf8").replace(/^import .*;$/gm, "").replace("export default class", "return class");
  const Sidebar = new Function(...Object.keys(environment), source)(...Object.values(environment));
  const view = new Sidebar();
  const cx = { timer: { every() {} }, notify() {} };
  view.init({}, cx);
  return { view, list, calls, cx };
}

test("idle starts collapsed, expands to clickable cards, and collapses again", () => {
  const { view, cx, calls } = sidebar();
  let tree = view.render();
  assert.ok(find(tree, "attention-agent-t2"));
  assert.equal(find(tree, "attention-agent-t1"), null);
  assert.equal(find(tree, "attention-agent-list").attributes.overflow_y_scrollbar, true);
  find(tree, "idle-machine-local").attributes.on_click({}, cx);
  tree = view.render();
  const idle = find(tree, "attention-agent-t1");
  assert.ok(idle);
  idle.attributes.on_click();
  assert.deepEqual(calls, [["pane.focus", { pane: "p1" }]]);
  find(tree, "idle-machine-local").attributes.on_click({}, cx);
  assert.equal(find(view.render(), "attention-agent-t1"), null);
});

test("idle-only machines remain visible and waking agents leave the idle section", () => {
  const { view, list } = sidebar();
  list.pop();
  assert.ok(find(view.render(), "attention-machine-local"));
  assert.ok(find(view.render(), "idle-machine-local"));
  list[0].status = "working";
  assert.equal(find(view.render(), "idle-machine-local"), null);
  assert.ok(find(view.render(), "attention-agent-t1"));
});

test("acknowledging a report moves its card into the folded idle section", () => {
  const { view, list } = sidebar();
  list[0].status = "done";
  assert.ok(find(view.render(), "attention-agent-t1"));
  list[0].status = "idle";
  assert.equal(find(view.render(), "attention-agent-t1"), null);
  assert.ok(find(view.render(), "idle-machine-local"));
});
