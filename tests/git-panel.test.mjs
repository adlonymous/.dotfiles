import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import * as gitContext from "../snapshot/.config/herdr-app/mods/changes-readable/git-context.mjs";

const source = readFileSync(new URL("../snapshot/.config/herdr-app/mods/changes-readable/main.js", import.meta.url), "utf8");

// Exercise actual view callbacks without a GPU. Native screenshots check rendering separately.
function gitPanelHarness(respond) {
  const elements = new Map(), requests = [], commands = [], pending = [], browsers = [];
  let space = { id: "pc/s1", name: "Project", machine: "pc", folder: "/pc/project" };
  const cx = { notify() {}, focus_handle: () => ({}), timer: { every() {} }, spawn(callback) { pending.push(callback(cx)); } };
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
    Scrollbar: { vertical: element }, v_virtual_list: element,
    spaces: () => [{ ...space, active: true }], panes: () => [],
    exec: async (command, args, options) => {
      if (command !== "sh") { browsers.push({ command, args, options }); return { code: 0 }; }
      const request = JSON.parse(args[3]);
      requests.push({ request, on: options.on });
      return respond(request, options);
    },
    theme: () => ({}), settings: () => ({}), props: () => dependencies.viewProps,
    openOverlay() {}, closeOverlay() {}, run: (name, args) => commands.push({ name, args }),
    window: () => ({ platform: "macos" }), viewProps: {},
  };
  const body = source.replace(/^import .*;\n/gm, "").replace("export default class Changes", "return class Changes");
  const Changes = new Function(...Object.keys(dependencies), body)(...Object.values(dependencies));
  return { view: new Changes(), cx, requests, commands, elements, dependencies, browsers,
    select(value) { space = value; },
    async settle() { while (pending.length) await Promise.all(pending.splice(0)); } };
}
const state = folder => ({ is_repo: true, folder, root: folder, head: "abcdef", branch: "feat/work",
  fingerprint: "reviewed-state", upstream: "", remotes: [], files: [], branches: ["main", "feat/work"],
  identity: { name: "Example", email: "example@example.invalid" }, operation: "" });
const reply = (data, code = 0) => ({ stdout: JSON.stringify(data), code });
const respond = request => reply(request.action === "status" ? state(request.folder) : { message: "Done" });

test("commit sends only the commit action, captured folder, host and reviewed snapshot", async () => {
  const h = gitPanelHarness(respond);
  h.view.init({}, h.cx); await h.settle();
  h.view.input.set_value("feat: explicit commit");
  h.view.act({ action: "commit", message: h.view.input.value() }, h.cx); await h.settle();
  const mutation = h.requests.find(entry => entry.request.action === "commit");
  assert.equal(mutation.on, "pc");
  assert.equal(mutation.request.folder, "/pc/project");
  assert.equal(mutation.request.expected, "reviewed-state");
  assert.equal(mutation.request.message, "feat: explicit commit");
  assert.equal(h.view.input.value(), "");
  assert.equal(h.requests.some(entry => entry.request.action === "stage"), false);
});

test("failed commit preserves the draft and error after refreshing status", async () => {
  const h = gitPanelHarness(request => request.action === "commit" ? reply({ error: "Hook rejected commit" }, 1) : respond(request));
  h.view.init({}, h.cx); await h.settle();
  h.view.input.set_value("fix: keep draft");
  h.view.act({ action: "commit", message: h.view.input.value() }, h.cx); await h.settle();
  assert.equal(h.view.input.value(), "fix: keep draft");
  assert.equal(h.view.error, "Hook rejected commit");
});

test("late PC response cannot populate a newly selected Mac workspace", async () => {
  let complete;
  const first = new Promise(resolve => { complete = resolve; });
  const h = gitPanelHarness((request, options) => options.on === "pc" ? first : respond(request));
  h.view.init({}, h.cx);
  h.view.formExpected = "old-form";
  h.select({ id: "local", machine: null, name: "Mac", folder: "/mac/project" });
  h.view.refresh(h.cx); complete(reply(state("/pc/project"))); await h.settle();
  assert.equal(h.view.state.folder, "/mac/project");
  assert.equal(h.view.formExpected, null);
  assert.deepEqual(h.requests.map(entry => entry.on), ["pc", null]);
});

test("network actions require a separate confirmation button", async () => {
  const h = gitPanelHarness(request => reply({ ...state(request.folder), remotes: [{ name: "origin", url: "https://example.invalid/repo", push_urls: ["https://example.invalid/repo"] }] }));
  h.view.init({}, h.cx); await h.settle();
  h.view.openForm("push", h.cx); h.view.render(h.cx);
  assert.equal(h.requests.some(entry => entry.request.action === "push"), false);
  h.elements.get("git-confirm-push").click({}, h.cx); await h.settle();
  assert.equal(h.requests.find(entry => entry.request.action === "push").on, "pc");
});

test("GitHub creation requires explicit visibility and opens the link on the viewer", async () => {
  const h = gitPanelHarness(request => reply(request.action === "status" ? state(request.folder)
    : request.action === "github-info" ? { owner: "example" } : { url: "https://github.com/example/project" }));
  h.view.init({}, h.cx); await h.settle();
  h.view.openForm("github", h.cx); await h.settle(); h.view.render(h.cx);
  h.elements.get("github-create").click({}, h.cx); await h.settle();
  assert.equal(h.requests.some(entry => entry.request.action === "github-create"), false);
  h.elements.get("github-private").click({}, h.cx); h.view.render(h.cx);
  h.elements.get("github-create").click({}, h.cx); await h.settle();
  assert.equal(h.requests.find(entry => entry.request.action === "github-create").request.visibility, "private");
  assert.equal(h.browsers[0].command, "open");
  assert.equal(h.browsers[0].options, undefined);
});

test("a Mac project dialog stays local even when PC is the active workspace", async () => {
  const h = gitPanelHarness(request => reply(request.action === "project-info" ? { parent: "/mac/Projects" } : { folder: "/mac/Projects/new-project", name: "new-project" }));
  Object.assign(h.dependencies.viewProps, { project: true, machine: "" });
  h.view.init({}, h.cx); await h.settle();
  h.view.fields.name.set_value("new-project"); h.view.render(h.cx);
  h.elements.get("project-create").click({}, h.cx); await h.settle();
  assert.equal(h.requests.at(-1).on, null);
  assert.deepEqual(h.commands, [{ name: "space.new", args: { folder: "/mac/Projects/new-project", name: "new-project", machine: "" } }]);
});
