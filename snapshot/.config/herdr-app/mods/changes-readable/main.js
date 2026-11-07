import { View, div } from "gpui-kit";
import { v_flex, h_flex, InputState, Input, Scrollbar, v_virtual_list } from "gpui-base";
import { spaces, panes, exec, theme, settings, props, openOverlay, closeOverlay, run, window } from "herdr";
import { gitWorkspaceContext, gitPushProtected } from "./git-context.mjs";

const context = () => gitWorkspaceContext(spaces().find(space => space.active), panes());
const HELPER = 'exec python3 "${XDG_CONFIG_HOME:-$HOME/.config}/herdr-app/mods/changes-readable/git_backend.py" "$1"';

async function gitRequest(workspace, action) {
  const result = await exec("sh", ["-c", HELPER, "workspace-git", JSON.stringify({ folder: workspace?.folder ?? "", ...action })], { on: workspace?.machine ?? null });
  let data;
  try { data = JSON.parse(result.stdout); }
  catch { throw new Error("Git helper unavailable. Apply the dotfiles on this workspace's machine first."); }
  if (result.code !== 0 || data.error) throw new Error(data.error || "Git action failed");
  return data;
}

function diffRows(lines) {
  let old = 0, next = 0;
  return lines.map((line) => {
    const match = /^@@ -(\d+)(?:,\d+)? \+(\d+)/.exec(line);
    if (match) { old = +match[1]; next = +match[2]; return { kind: "@", text: line }; }
    const kind = line[0];
    if (kind === "-") return { kind, number: old++, text: line.slice(1) || " " };
    if (kind === "+") return { kind, number: next++, text: line.slice(1) || " " };
    if (kind === " ") { old++; return { kind, number: next++, text: line.slice(1) || " " }; }
    return { kind: "", text: line };
  });
}

export default class Changes extends View {
  init(_props, cx) {
    this.state = null; this.rows = []; this.diffWidth = 300; this.error = ""; this.loadError = ""; this.note = "";
    this.contextKey = ""; this.mode = ""; this.fields = {}; this.drafts = new Map();
    this.handle = cx.focus_handle();
    this.input = InputState.new({ placeholder: "Commit message" });
    this.input.on("change", (_event, cx) => {
      if (this.contextKey) this.drafts.set(this.contextKey, this.input.value());
      cx.notify();
    });
    this.project = Boolean(props()?.project);
    if (this.project) {
      this.projectMachine = props().machine || null;
      this.mode = "project";
      this.setupFields({ name: "", parent: "", description: "" }, cx);
      cx.spawn(async cx => {
        try {
          const data = await gitRequest({ machine: this.projectMachine }, { action: "project-info" });
          if (!this.fields.parent.value()) this.fields.parent.set_value(data.parent);
        } catch (error) { this.error = error.message; }
        finally { cx.notify(); }
      });
    } else {
      this.refresh(cx);
      cx.timer.every(10000, cx => this.refresh(cx));
    }
  }

  setupFields(values, cx) {
    this.fields = {};
    for (const [name, value] of Object.entries(values)) {
      this.fields[name] = InputState.new({ value });
      this.fields[name].on("change", (_event, cx) => cx.notify());
    }
    cx.notify();
  }

  refresh(cx) {
    if (this.project) return;
    const workspace = context();
    if (workspace?.key !== this.contextKey) {
      this.contextKey = workspace?.key; this.state = null; this.selected = null;
      this.mode = ""; this.formExpected = null; this.remote = ""; this.rows = []; this.error = ""; this.loadError = ""; this.note = "";
      this.input.set_value(this.drafts.get(workspace?.key) || "");
    }
    if (!workspace || this.loading || this.busy) return;
    this.loading = true;
    cx.spawn(async cx => {
      try {
        const data = await gitRequest(workspace, { action: "status" });
        if (context()?.key !== workspace.key) return;
        this.state = data;
        this.loadError = "";
        if (data.is_repo) {
          if (!data.remotes.some(remote => remote.name === this.remote)) {
            this.remote = data.remotes.find(remote => data.upstream.startsWith(remote.name + "/"))?.name || data.remotes.find(remote => remote.name === "origin")?.name || data.remotes[0]?.name || "";
          }
          if (this.selected && !data.files.some(file => file.path === this.selected.path && (this.selected.staged ? ![" ", "?"].includes(file.index) : file.worktree !== " "))) this.selected = null;
          if (!this.selected && data.files.length) {
            const file = data.files[0];
            this.selected = { path: file.path, staged: ![" ", "?"].includes(file.index) };
          }
          if (this.selected) await this.loadDiff(workspace, data, this.selected);
          else this.rows = [];
        }
      } catch (error) { if (context()?.key === workspace.key) this.loadError = error.message; }
      finally {
        this.loading = false;
        if (context()?.key !== workspace.key) this.refresh(cx);
        cx.notify();
      }
    });
  }

  async loadDiff(workspace, state, selected) {
    const data = await gitRequest(workspace, { action: "diff", expected: state.fingerprint, ...selected });
    if (context()?.key !== workspace.key || this.selected !== selected || this.state?.fingerprint !== state.fingerprint) return;
    const all = (data.text || "No text diff available").split("\n"), first = Math.max(0, all.findIndex(line => line.startsWith("@@")));
    const lines = all.slice(first, first + 1500).map(line => line.slice(0, 4000));
    this.rows = diffRows(lines);
    this.diffWidth = Math.max(300, ...lines.map(line => line.length * (7 * 13 / 11) + 50));
  }

  pick(path, staged, cx) {
    if (this.busy || this.loading || !this.state) return;
    this.selected = { path, staged }; this.rows = []; this.error = ""; this.note = "";
    const workspace = context(), selected = this.selected, state = this.state;
    cx.spawn(async cx => {
      try { await this.loadDiff(workspace, state, selected); }
      catch (error) { if (context()?.key === workspace.key) this.error = error.message; }
      cx.notify();
    });
    cx.notify();
  }

  act(action, cx) {
    const workspace = context();
    if (!workspace || this.contextKey !== workspace.key || !this.state?.is_repo || this.busy || this.loading) return;
    const expected = this.formExpected || this.state.fingerprint;
    this.busy = true; this.error = ""; this.note = "";
    cx.spawn(async cx => {
      try {
        const result = await gitRequest(workspace, { expected, ...action });
        if (context()?.key === workspace.key) {
          this.mode = ""; this.formExpected = null; this.note = result.message;
          if (action.action === "commit") { this.input.set_value(""); this.drafts.delete(workspace.key); }
          if (result.url) this.openURL(result.url, cx);
        }
      } catch (error) { if (context()?.key === workspace.key) this.error = error.message; }
      finally { this.busy = false; this.refresh(cx); cx.notify(); }
    });
    cx.notify();
  }

  openURL(url, cx) {
    cx.spawn(async cx => {
      try {
        const result = await exec(window()?.platform === "macos" ? "open" : "xdg-open", [url]);
        if (result.code !== 0) this.note = "Open in your browser: " + url;
      } catch { this.note = "Open in your browser: " + url; }
      cx.notify();
    });
  }

  openForm(mode, cx) {
    if (this.busy || this.loading || !this.state?.is_repo) return;
    this.mode = mode; this.formExpected = this.state.fingerprint; this.error = "";
    const values = mode === "github" ? { owner: "", name: this.state.root.split("/").pop(), description: "", homepage: "" }
      : mode === "identity" ? this.state.identity : { branch: "" };
    this.setupFields(values, cx);
    this.visibility = "";
    if (mode === "github") {
      const workspace = context();
      const ownerField = this.fields.owner;
      cx.spawn(async cx => {
        try {
          const data = await gitRequest(workspace, { action: "github-info" });
          if (context()?.key === workspace.key && this.mode === "github" && this.fields.owner === ownerField && !ownerField.value()) ownerField.set_value(data.owner);
        } catch { if (context()?.key === workspace.key && this.mode === "github" && this.fields.owner === ownerField) this.error = `Sign in with gh auth login on ${workspace.machine || "this computer"}, then enter the GitHub owner.`; }
        finally { cx.notify(); }
      });
    }
  }

  button(id, label, action, enabled = true) {
    const t = theme(), ready = enabled && !this.busy && !this.loading;
    return div().id(id).h(30).flex_none().px(9).flex().items_center().rounded(6).border_1().border_color(t.border).disabled(!ready).accessibility_label(label)
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

  projectForm() {
    const t = theme();
    return v_flex().id("git-project-form").size_full().min_h(0).p(18).gap(12).bg(t.background).text_color(t.foreground).text_size(13)
      .child(div().font_semibold().text_size(16).child("New project workspace"))
      .child(v_flex().id("git-project-fields").flex_1().min_h(0).overflow_y_scrollbar().gap(12)
      .child(div().text_color(t.muted).child("Create on " + (this.projectMachine || "this computer")))
      .child(this.field("name", "Project folder name"))
      .child(this.field("parent", "Parent folder on that machine"))
      .child(this.field("description", "Description (optional)"))
      .child(div().text_size(12).text_color(t.dim).child("Creates a new folder and initializes Git, or uses its parent repository. Existing folders are never initialized. No commit, GitHub repository, or push."))
      .when(Boolean(this.error), el => el.child(div().text_color(t.ansi1).child(this.error))))
      .child(h_flex().gap(8).child(this.button("project-cancel", "Cancel", () => closeOverlay(props().overlay)))
        .child(this.button("project-create", this.busy ? "Creating…" : "Create project", cx => {
          this.busy = true; this.error = "";
          const values = Object.fromEntries(Object.entries(this.fields).map(([name, field]) => [name, field.value()]));
          cx.spawn(async cx => {
            try {
              const result = await gitRequest({ machine: this.projectMachine }, { action: "project-create", ...values });
              run("space.new", { folder: result.folder, name: result.name, machine: this.projectMachine || "" });
              closeOverlay(props().overlay);
            } catch (error) { this.error = error.message; }
            finally { this.busy = false; cx.notify(); }
          });
          cx.notify();
        }, Boolean(this.fields.name.value().trim() && this.fields.parent.value().trim()))));
  }

  form() {
    const t = theme(), mode = this.mode;
    if (!mode) return div();
    const values = () => Object.fromEntries(Object.entries(this.fields).map(([name, field]) => [name, field.value().trim()]));
    const row = v_flex().id("git-action-form").flex_none().p(10).gap(8).border_b(1).border_color(t.border);
    if (mode === "github") row
      .child(div().font_semibold().child("Create GitHub.com repository"))
      .child(this.field("owner", "Owner (user or organization)"))
      .child(this.field("name", "Repository name"))
      .child(this.field("description", "Description"))
      .child(this.field("homepage", "Homepage URL (optional)"))
      .child(h_flex().gap(8).child(this.button("github-private", (this.visibility === "private" ? "● " : "○ ") + "Private", cx => { this.visibility = "private"; cx.notify(); }))
        .child(this.button("github-public", (this.visibility === "public" ? "● " : "○ ") + "Public", cx => { this.visibility = "public"; cx.notify(); })))
      .child(div().text_color(t.dim).text_size(11).child("Adds origin. Does not push. Public repositories are visible to everyone."))
      .child(this.button("github-create", "Create " + (this.visibility || "GitHub") + " repository", cx => this.act({ action: "github-create", visibility: this.visibility, ...values() }, cx), Boolean(this.visibility && values().owner && values().name)));
    if (mode === "identity") row.child(div().font_semibold().child("Identity for this repository only"))
      .child(this.field("name", "Commit author name")).child(this.field("email", "Commit author email"))
      .child(this.button("identity-save", "Save local identity", cx => this.act({ action: "identity", ...values() }, cx), Boolean(values().name && values().email)));
    if (mode === "branch") row.child(this.field("branch", "New branch name"))
      .child(div().text_size(11).text_color(t.dim).child(this.state.files.length ? "Uncommitted changes stay with the new branch. Nothing is stashed or committed." : "Creates and switches to the new branch."))
      .child(this.button("branch-create", this.state.files.length ? "Create branch and keep changes" : "Create branch", cx => this.act({ action: "branch", carry_changes: true, ...values() }, cx), Boolean(values().branch)));
    if (mode === "branches") row.child(this.button("branch-new", "Create branch…", cx => this.openForm("branch", cx)))
      .child(v_flex().id("git-branches").h(Math.min(160, this.state.branches.length * 32)).overflow_y_scrollbar().gap(2)
        .children(this.state.branches.map(branch => this.button("switch-" + branch, branch + (branch === this.state.branch ? " · current" : ""), cx => this.act({ action: "switch", branch }, cx), branch !== this.state.branch && !this.state.files.length))))
      .when(this.state.files.length > 0, el => el.child(div().text_size(11).text_color(t.dim).child("Commit or stash changes in a terminal before switching an existing branch.")));
    if (mode === "remotes") row.children(this.state.remotes.map(remote => this.button("remote-" + remote.name, remote.name, cx => {
      this.remote = remote.name; this.mode = ""; this.formExpected = null; cx.notify();
    })));
    if (["push", "pull", "fetch"].includes(mode)) {
      const remote = this.state.remotes.find(remote => remote.name === this.remote);
      row.child(div().font_semibold().child(mode === "push" ? `Push ${this.state.branch} to ${this.remote}` : `${mode === "pull" ? "Pull (fast-forward only)" : "Fetch"} from ${this.remote}`))
        .child(div().text_size(11).text_color(t.dim).child(mode === "push" ? remote?.push_urls.join("\n") : remote?.url))
        .when(mode === "push", el => el.child(div().text_size(11).text_color(t.dim).child(`Commit: ${this.state.head.slice(0, 7)}. Destination: refs/heads/${this.state.branch}. No force push.`)))
        .child(this.button("git-confirm-" + mode, "Confirm " + mode, cx => this.act({ action: mode, remote: this.remote }, cx)));
    }
    return row.child(this.button("git-cancel", "Cancel", cx => { this.mode = ""; this.formExpected = null; cx.notify(); }));
  }

  fileSection(staged) {
    const t = theme(), files = this.state.files.filter(file => staged ? ![" ", "?"].includes(file.index) : file.worktree !== " ");
    return v_flex().flex_none().gap(3)
      .child(div().px(8).py(4).font_semibold().text_color(t.muted).text_size(11).child(`${staged ? "Staged" : "Changes"} (${files.length})`))
      .children(files.slice(0, 1000).map(file => h_flex().id(`git-file-${staged ? "staged" : "working"}-${file.path}`).h(32).flex_none().px(8).gap(8).items_center().rounded(6)
        .when(this.selected?.path === file.path && this.selected.staged === staged, el => el.bg(t.selected))
        .child(div().flex_1().min_w(0).truncate().cursor_pointer().on_click((_event, cx) => this.pick(file.path, staged, cx)).child((file.conflict ? "Conflict · " : "") + file.path))
        .child(this.button(`git-${staged ? "unstage" : "stage"}-${file.path}`, staged ? "−" : "+", cx => this.act({ action: staged ? "unstage" : "stage", path: file.path }, cx), !this.state.operation).tooltip((staged ? "Unstage " : "Stage ") + file.path).accessibility_label((staged ? "Unstage " : "Stage ") + file.path))))
      .when(files.length > 1000, el => el.child(div().px(8).text_color(t.dim).child("Showing the first 1,000 files")));
  }

  diffRow({ kind, number, text }, t) {
    if (kind === "@") return div().w_full().px(12).h(24).flex_none().truncate().bg(t.raised).text_color(t.dim).child(text);
    return h_flex().w_full().h(24).flex_none().gap(10).when(kind === "+", el => el.bg(t.ansi2 + "18")).when(kind === "-", el => el.bg(t.ansi1 + "18"))
      .child(div().w(30).flex_none().text_right().text_color(t.dim).child(number === undefined ? "" : String(number)))
      .child(div().flex_1().min_w(0).truncate().child(text));
  }

  render(cx) {
    if (this.project) return this.projectForm();
    if (context()?.key !== this.contextKey) this.refresh(cx);
    const t = theme(), workspace = context(), state = this.state;
    const staged = state?.files?.filter(file => ![" ", "?"].includes(file.index)) || [];
    return v_flex().id("changes").size_full().min_h(0).rounded(10).overflow_hidden().bg(t.background).border_1().border_color(t.border).text_color(t.foreground).text_size(13).track_focus(this.handle)
      .child(h_flex().h(44).flex_none().px(12).gap(8).items_center().border_b(1).border_color(t.border)
        .child(div().font_semibold().flex_1().child("Changes"))
        .child(this.button("git-refresh", "Refresh", cx => { this.mode = ""; this.formExpected = null; this.error = ""; this.refresh(cx); cx.notify(); }))
        .child(this.button("git-new-project", "New project…", () => openOverlay({ mod: "changes-readable", kind: "dialog", width: 500, height: 460, props: { project: true, machine: workspace?.machine || "" } }))))
      .child(div().flex_none().px(12).py(6).text_size(11).text_color(t.dim).child(`${workspace?.name || "No workspace"} · ${workspace?.machine || "This computer"}`))
      .child(div().flex_none().px(12).pb(6).text_size(11).text_color(t.dim).truncate().child(state?.root || workspace?.folder || ""))
      .when(Boolean(state?.is_repo), el => el
        .child(h_flex().flex_none().px(10).pb(8).gap(6).items_center()
          .child(div().flex_1().min_w(0).child(this.button("git-branch", (state.branch || "Detached " + state.head.slice(0, 7)) + " ▾", cx => this.openForm("branches", cx)).w_full().truncate()))
          .child(div().flex_none().text_size(11).text_color(t.dim).child(!state.head ? "No commits yet" : state.upstream ? `↑${state.ahead ?? "?"} ↓${state.behind ?? "?"}` : "Local branch"))
          .when(state.remotes.length > 0, el => el.child(this.button("git-remote", this.remote + " ▾", cx => this.openForm("remotes", cx)))))
        .when(state.remotes.length > 0, el => el.child(h_flex().flex_none().px(10).pb(8).gap(6)
          .child(this.button("git-fetch", "Fetch", cx => this.openForm("fetch", cx)))
          .child(this.button("git-pull", "Pull", cx => this.openForm("pull", cx), Boolean(state.upstream.startsWith(this.remote + "/") && !state.files.length && !state.operation)))
          .child(this.button("git-push", gitPushProtected(state) ? "New branch…" : "Push…", cx => this.openForm(gitPushProtected(state) ? "branch" : "push", cx), !state.operation))
          .when(Boolean(state.remotes.find(remote => remote.name === this.remote)?.github_url), el => el.child(this.button("git-open-github", "GitHub ↗", cx => this.openURL(state.remotes.find(remote => remote.name === this.remote).github_url, cx))))))
        .when(!state.remotes.length && Boolean(state.head), el => el.child(div().flex_none().px(10).pb(8).child(this.button("git-publish", "Create GitHub repository…", cx => this.openForm("github", cx)))))
        .when(Boolean(state.operation), el => el.child(div().px(12).pb(8).text_color(t.ansi1).child("Finish the current Git operation in a terminal: " + state.operation)))
        .when(state.remotes.length > 0 && gitPushProtected(state), el => el.child(div().flex_none().px(12).pb(6).text_size(11).text_color(t.dim).child("Create a feature branch before pushing. Default-branch pushes are blocked.")))
        .when(Boolean(this.mode), el => el.child(div().flex_1().min_h(0).overflow_y_scrollbar().id("git-form-scroll").child(this.form())))
        .when(!this.mode, el => el.child(v_flex().id("changes-list").flex_none().h(Math.min(200, Math.max(50, (state.files.length + staged.length) * 32 + 60))).overflow_y_scrollbar().px(4).pb(6).border_b(1).border_color(t.border)
          .child(this.fileSection(true)).child(this.fileSection(false))
          .when(!state.files.length, el => el.child(div().px(8).py(8).text_color(t.dim).child("Working tree clean"))))
        .child(div().flex_none().px(12).py(4).text_size(11).text_color(t.dim).truncate().child(this.selected ? `${this.selected.staged ? "Staged" : "Unstaged"} · ${this.selected.path}` : "Select a file to review its diff"))
        .child(div().flex_1().min_h(0).relative().font_family(settings().font_family ?? "JetBrains Mono").text_size(13)
          .child(div().id("changes-diff-x").size_full().overflow_x_scrollbar()
            .child(div().w_full().min_w(this.diffWidth).h_full().child(v_virtual_list("changes-diff", this.rows.length, 24, i => String(i), range => this.rows.slice(range.start, range.end).map(row => this.diffRow(row, t))).size_full())))
          .child(Scrollbar.vertical("changes-diff").viewport_from_layout().absolute().inset_0()))
        .when(!state.identity.name || !state.identity.email, el => el.child(div().flex_none().px(10).py(6).child(this.button("git-identity", "Configure commit identity…", cx => this.openForm("identity", cx)))))
        .child(v_flex().flex_none().p(10).gap(8).border_t(1).border_color(t.border)
          .child(Input.new(this.input).id("commit-message").accessibility_label("Commit message").h(32).px(8).border_1().border_color(t.border).rounded(6))
          .child(this.button("git-commit", this.busy ? "Working…" : state.head ? "Commit staged changes" : "Create first commit", cx => this.act({ action: "commit", message: this.input.value() }, cx), Boolean(staged.length && this.input.value().trim() && state.identity.name && state.identity.email && !state.operation))))))
      .when(!state?.is_repo, el => el.child(div().flex_1().p(12).text_color(t.dim).child(this.loading ? "Loading repository…" : "This workspace isn't a Git repository. Existing folders are left unchanged; use New project to create a Git-backed workspace.")))
      .when(Boolean(this.error || this.loadError || this.note), el => el.child(div().flex_none().h(64).overflow_y_scrollbar().id("git-result").px(10).py(8).text_size(12).text_color(this.error || this.loadError ? t.ansi1 : t.ansi2).child(this.error || this.loadError || this.note)));
  }
}
