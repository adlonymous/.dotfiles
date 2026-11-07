import { View, div } from "gpui-kit";
import { v_flex, h_flex, InputState, Input } from "gpui-base";
import { spaces, exec, theme, props, openOverlay, closeOverlay, run, window, layout, shared, appHome, readTextFile, writeTextFile } from "herdr";
import { gitWorkspaceContext, gitTerminalAddress, gitLayoutNode, gitPanelVisible, gitViewportPlaceholder } from "./git-context.mjs";

const context = () => gitWorkspaceContext(spaces().find(space => space.active));
const HELPER = 'exec python3 "${XDG_CONFIG_HOME:-$HOME/.config}/herdr-app/mods/changes-readable/git_backend.py" "$1"';

async function gitRequest(workspace, action) {
  const result = await exec("sh", ["-c", HELPER, "workspace-git", JSON.stringify({ folder: workspace?.folder ?? "", workspace: workspace?.workspace ?? "", ...action })], { on: workspace?.machine ?? null });
  let data;
  try { data = JSON.parse(result.stdout); }
  catch { throw new Error("Git helper unavailable. Apply the dotfiles on this workspace's machine first."); }
  if (result.code !== 0 || data.error) throw new Error(data.error || "Workspace Git action failed");
  return data;
}

export default class Changes extends View {
  init(_props, cx) {
    this.error = ""; this.state = null; this.key = ""; this.attempted = new Set(); this.fields = {};
    this.form = props()?.form;
    this.target = props()?.target || { machine: props()?.machine || null };
    if (props()?.placeholder) return;
    if (this.form) {
      const values = this.form === "project" ? { name: "", parent: "", description: "" }
        : { owner: "", name: props().root.split("/").pop(), description: "", homepage: "" };
      for (const [name, value] of Object.entries(values)) {
        this.fields[name] = InputState.new({ value });
        this.fields[name].on("change", (_event, cx) => cx.notify());
      }
      this.visibility = "";
      cx.spawn(async cx => {
        try {
          const data = await gitRequest(this.target, { action: this.form === "project" ? "project-info" : "github-info" });
          const field = this.form === "project" ? this.fields.parent : this.fields.owner;
          if (!field.value()) field.set_value(this.form === "project" ? data.parent : data.owner);
        } catch (error) { this.error = error.message; }
        finally { cx.notify(); }
      });
      return;
    }
    this.sync(cx);
    cx.timer.every(10000, cx => this.sync(cx));
  }

  async viewport(content, workspace) {
    if (context()?.key !== workspace.key) return;
    const name = shared("layout");
    if (name !== "wide-panels") throw new Error("Lazygit embedding needs the wide-panels layout.");
    const path = appHome() + "/layouts/" + name + ".json";
    const original = await readTextFile(path);
    const tree = JSON.parse(original), node = gitLayoutNode(tree, "git-terminal");
    if (!node) throw new Error("Update the wide-panels layout to add its Lazygit viewport.");
    if (JSON.stringify(node.content) === JSON.stringify(content) || context()?.key !== workspace.key) return;
    node.content = content;
    await writeTextFile(path, JSON.stringify(tree, null, 2) + "\n", original);
  }

  sync(cx, force = false) {
    const workspace = context();
    if (!workspace || this.busy || !gitPanelVisible(layout())) return;
    const changed = this.key !== workspace.key;
    this.key = workspace.key;
    this.busy = true;
    if (changed) { this.state = null; this.error = ""; }
    cx.spawn(async cx => {
      try {
        if (changed) await this.viewport(gitViewportPlaceholder, workspace);
        const start = force || !this.attempted.has(workspace.key);
        this.attempted.add(workspace.key);
        const state = await gitRequest(workspace, { action: start ? "open" : "session" });
        if (context()?.key !== workspace.key) return;
        this.state = state; this.error = "";
        await this.viewport(state.terminal ? { terminal: gitTerminalAddress(workspace, state.terminal) } : gitViewportPlaceholder, workspace);
      } catch (error) { if (context()?.key === workspace.key) this.error = error.message; }
      finally {
        this.busy = false;
        if (context()?.key !== workspace.key) this.sync(cx);
        cx.notify();
      }
    });
  }

  button(id, label, action, enabled = true) {
    const t = theme(), ready = enabled && !this.busy;
    return div().id(id).h(30).flex_none().px(8).flex().items_center().rounded(6).border_1().border_color(t.border).disabled(!ready).accessibility_label(label)
      .text_size(12).text_color(ready ? t.foreground : t.dim)
      .when(ready, el => el.cursor_pointer().hover(style => style.bg(t.hover)))
      .on_mouse_down("left", (_event, cx) => cx.stop_propagation())
      .on_click((_event, cx) => { if (ready) action(cx); }).child(label);
  }

  field(name, label) {
    const t = theme();
    return v_flex().flex_none().gap(4).child(div().text_size(11).text_color(t.muted).child(label))
      .child(Input.new(this.fields[name]).id("git-field-" + name).accessibility_label(label).h(32).px(8).border_1().border_color(t.border).rounded(6));
  }

  openURL(url, cx) {
    cx.spawn(async cx => {
      try {
        const result = await exec(window()?.platform === "macos" ? "open" : "xdg-open", [url]);
        if (result.code !== 0) this.error = "Open in your browser: " + url;
      } catch { this.error = "Open in your browser: " + url; }
      cx.notify();
    });
  }

  submit(cx) {
    if (this.busy) return;
    const values = Object.fromEntries(Object.entries(this.fields).map(([name, field]) => [name, field.value().trim()]));
    const request = this.form === "project" ? { action: "project-create", ...values }
      : { action: "github-create", expected: props().expected, visibility: this.visibility, ...values };
    this.busy = true; this.error = "";
    cx.spawn(async cx => {
      try {
        const result = await gitRequest(this.target, request);
        if (this.form === "project") run("space.new", { folder: result.folder, name: result.name, machine: this.target.machine || "" });
        else this.openURL(result.url, cx);
        closeOverlay(props().overlay);
      } catch (error) { this.error = error.message; }
      finally { this.busy = false; cx.notify(); }
    });
    cx.notify();
  }

  renderForm() {
    const t = theme(), project = this.form === "project";
    return v_flex().id("git-creation-form").size_full().min_h(0).p(18).gap(12).bg(t.background).text_color(t.foreground).text_size(13)
      .child(div().font_semibold().text_size(16).child(project ? "New project workspace" : "Create GitHub.com repository"))
      .child(v_flex().id("git-form-fields").flex_1().min_h(0).overflow_y_scrollbar().gap(10)
        .child(div().text_color(t.muted).child("Create on " + (this.target.machine || "this computer")))
        .when(!project, el => el.child(div().text_size(11).text_color(t.dim).child(this.target.folder)).child(this.field("owner", "Owner (user or organization)")))
        .child(this.field("name", project ? "Project folder name" : "Repository name"))
        .when(project, el => el.child(this.field("parent", "Parent folder on that machine")))
        .child(this.field("description", "Description (optional)"))
        .when(!project, el => el.child(this.field("homepage", "Homepage URL (optional)"))
          .child(h_flex().gap(8).child(this.button("github-private", (this.visibility === "private" ? "● " : "○ ") + "Private", cx => { this.visibility = "private"; cx.notify(); }))
            .child(this.button("github-public", (this.visibility === "public" ? "● " : "○ ") + "Public", cx => { this.visibility = "public"; cx.notify(); }))))
        .child(div().text_size(12).text_color(t.dim).child(project
          ? "Creates a new folder and initializes Git, or uses its parent repository. Existing folders are never initialized. No commit or push."
          : "Adds origin. Does not push. Public repositories are visible to everyone."))
        .when(Boolean(this.error), el => el.child(div().text_color(t.ansi1).child(this.error))))
      .child(h_flex().gap(8).child(this.button("git-form-cancel", "Cancel", () => closeOverlay(props().overlay)))
        .child(this.button("git-form-submit", this.busy ? "Creating…" : project ? "Create project" : "Create repository", cx => this.submit(cx),
          Boolean(this.fields.name.value().trim() && (project ? this.fields.parent.value().trim() : this.fields.owner.value().trim() && this.visibility)))));
  }

  render(cx) {
    if (props()?.placeholder) return div().size_full().p(16).text_color(theme().dim).child("Open Lazygit using the controls above. Expand the panel for more room.");
    if (this.form) return this.renderForm();
    if (context()?.key !== this.key || (!this.state && !this.attempted.has(this.key))) this.sync(cx);
    const t = theme(), workspace = context(), state = this.state, expanded = Boolean(gitLayoutNode(layout(), "main")?.hidden);
    return v_flex().id("changes").size_full().min_h(0).p(10).gap(7).overflow_y_scrollbar().bg(t.background).text_color(t.foreground).text_size(12)
      .child(h_flex().gap(6).items_center().child(div().font_semibold().flex_1().child("Changes · Lazygit"))
        .child(this.button("git-expand", expanded ? "Collapse" : "Expand", () => {
          if (!expanded) this.panelWidth = gitLayoutNode(layout(), "panel")?.size?.px || 480;
          run(expanded ? "layout.show" : "layout.hide", { id: "main" });
          run("layout.resize", { id: "panel", ...(expanded ? { px: this.panelWidth || 480 } : { weight: 1 }) });
        })))
      .child(div().truncate().text_color(t.muted).child(`${workspace?.name || "No workspace"} · ${workspace?.machine || "This computer"}`))
      .child(div().truncate().text_size(11).text_color(t.dim).child(state?.root || workspace?.folder || ""))
      .child(h_flex().gap(6)
        .child(this.button("git-open", this.busy ? "Loading…" : state?.terminal ? "Refresh" : "Open Lazygit", cx => this.sync(cx, true), Boolean(workspace)))
        .child(this.button("git-new-project", "New project…", () => openOverlay({ mod: "changes-readable", kind: "dialog", width: 500, height: 460, props: { form: "project", target: { machine: workspace?.machine || null } } }))))
      .when(Boolean(state?.is_repo && state.head && !state.has_remotes), el => el.child(this.button("git-create-github", "Create GitHub repository…", () => openOverlay({ mod: "changes-readable", kind: "dialog", width: 500, height: 560,
        props: { form: "github", target: workspace, root: state.root, expected: state.fingerprint } }))))
      .when(Boolean(state?.github_url), el => el.child(this.button("git-open-github", "GitHub ↗", cx => this.openURL(state.github_url, cx))))
      .when(Boolean(this.error || (state && !state.is_repo)), el => el.child(div().text_size(11).text_color(t.ansi1).child(this.error || "Existing folder is not a repository. Use New project to create a Git-backed workspace.")));
  }
}
