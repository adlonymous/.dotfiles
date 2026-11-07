import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import * as gitContext from "../snapshot/.config/herdr-app/mods/changes-readable/git-context.mjs";

const source = readFileSync(new URL("../snapshot/.config/herdr-app/mods/changes-readable/main.js", import.meta.url), "utf8");

// Run real view callbacks with native elements stubbed; screenshots check actual layout.
function gitPanelHarness(respond) {
  const elements = new Map(), requests = [], commands = [], pending = [];
  let space = { id: "pc/s1", name: "Project", machine: "pc", folder: "/pc/project" };
  let tree = { id: "root", children: [{ id: "panel", children: [{ id: "panel-body", active: "changes", children: [{ id: "git-terminal", content: gitContext.gitViewportPlaceholder }] }] }] };
  const cx = { notify() {}, timer: { every() {} }, spawn(callback) { pending.push(callback(cx)); } };
  function element() {
    let proxy;
    const handlers = {};
    proxy = new Proxy(handlers, { get(target, method) {
      if (method === "click") return target.click;
      return (...args) => {
        if (method === "id") elements.set(args[0], proxy);
        if (method === "on_click") target.click = args[0];
        if (method === "when" && args[0]) args[1](proxy);
        return proxy;
      };
    } });
    return proxy;
  }
  const InputState = { new: ({ value = "" } = {}) => {
    let text = value;
    return { value: () => text, set_value(value) { text = value; }, on() {} };
  } };
  const dependencies = {
    ...gitContext, View: class {}, div: element, v_flex: element, h_flex: element, InputState, Input: { new: element },
    spaces: () => [{ ...space, active: true }],
    exec: async (_command, args, options) => {
      const request = JSON.parse(args[3]);
      requests.push({ request, on: options.on });
      return respond(request, options);
    },
    theme: () => ({}), props: () => dependencies.viewProps, layout: () => tree,
    shared: () => "wide-panels", appHome: () => "/viewer/.config/herdr-app",
    readTextFile: async () => JSON.stringify(tree),
    writeTextFile: async (_path, text) => { tree = JSON.parse(text); },
    openOverlay() {}, closeOverlay() {}, run: (name, args) => commands.push({ name, args }),
    window: () => ({ platform: "macos" }), viewProps: {},
  };
  const body = source.replace(/^import .*;\n/gm, "").replace("export default class Changes", "return class Changes");
  const Changes = new Function(...Object.keys(dependencies), body)(...Object.values(dependencies));
  return { view: new Changes(), cx, requests, commands, elements, dependencies,
    select(value) { space = value; }, tree: () => tree,
    async settle() { while (pending.length) await Promise.all(pending.splice(0)); } };
}
const reply = data => ({ stdout: JSON.stringify(data), code: 0 });
const session = request => reply({ is_repo: true, root: request.folder, terminal: "t1", head: "", has_remotes: false });

test("PC workspace starts through PC and embeds a machine-qualified terminal", async () => {
  const h = gitPanelHarness(session);
  h.view.init({}, h.cx);
  await h.settle();
  assert.equal(h.requests[0].on, "pc");
  assert.equal(h.requests[0].request.workspace, "s1");
  assert.equal(gitContext.gitLayoutNode(h.tree(), "git-terminal").content.terminal, "pc/t1");
});

test("Mac-local workspace starts locally and never gets the PC prefix", async () => {
  const h = gitPanelHarness(session);
  h.select({ id: "s2", name: "Mac", machine: null, folder: "/mac/project" });
  h.view.init({}, h.cx);
  await h.settle();
  assert.equal(h.requests[0].on, null);
  assert.equal(h.requests[0].request.folder, "/mac/project");
  assert.equal(gitContext.gitLayoutNode(h.tree(), "git-terminal").content.terminal, "t1");
});

test("hidden Changes does not launch anything", async () => {
  const h = gitPanelHarness(session);
  gitContext.gitLayoutNode(h.tree(), "panel-body").active = "tickets";
  h.view.init({}, h.cx);
  await h.settle();
  assert.equal(h.requests.length, 0);
});

test("late PC response cannot replace the Mac workspace's terminal", async () => {
  let complete;
  const first = new Promise(resolve => { complete = resolve; });
  const h = gitPanelHarness((request, options) => options.on === "pc" ? first : session(request));
  h.view.init({}, h.cx);
  await Promise.resolve(); await Promise.resolve();
  h.select({ id: "local", machine: null, name: "Mac", folder: "/mac/project" });
  complete(session({ folder: "/pc/project" }));
  await h.settle();
  assert.equal(h.view.state.root, "/mac/project");
  assert.equal(gitContext.gitLayoutNode(h.tree(), "git-terminal").content.terminal, "t1");
});

test("quitting Lazygit is not automatically undone by polling", async () => {
  const h = gitPanelHarness(request => request.action === "open" ? session(request) : reply({ is_repo: true, terminal: null }));
  h.view.init({}, h.cx);
  await h.settle();
  h.view.sync(h.cx);
  await h.settle();
  assert.deepEqual(h.requests.map(entry => entry.request.action), ["open", "session"]);
  assert.equal(gitContext.gitLayoutNode(h.tree(), "git-terminal").content.props.placeholder, true);
});

test("new-project confirmation preserves local machine even when PC becomes active", async () => {
  const h = gitPanelHarness(request => reply(request.action === "project-info"
    ? { parent: "/mac/Projects" } : { folder: "/mac/Projects/new-project", name: "new-project" }));
  Object.assign(h.dependencies.viewProps, { form: "project", target: { machine: null } });
  h.view.init({}, h.cx);
  await h.settle();
  h.view.fields.name.set_value("new-project");
  h.view.render(h.cx);
  h.elements.get("git-form-submit").click({}, h.cx);
  await h.settle();
  assert.equal(h.requests.at(-1).on, null);
  assert.deepEqual(h.commands, [{ name: "space.new", args: { folder: "/mac/Projects/new-project", name: "new-project", machine: "" } }]);
});
