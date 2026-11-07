import { View, div } from "gpui-kit";
import { v_flex, h_flex, InputState, Input, TextareaState, Textarea } from "gpui-base";
import { exec, spaces, theme, run } from "herdr";
import { ticketWorkspaceContext, ticketTerminalAddress } from "./ticket-context.mjs";

const context = () => ticketWorkspaceContext(spaces().find((space) => space.active));
const HELPER = 'exec python3 "$HOME/.config/herdr-app/mods/workspace-tickets/ticket_store.py" "$1"';

async function ticketRequest(workspace, action) {
  const request = { workspace: workspace.workspace, folder: workspace.folder, ...action };
  const result = await exec("sh", ["-c", HELPER, "workspace-tickets", JSON.stringify(request)], { on: workspace.machine });
  let data;
  try { data = JSON.parse(result.stdout); }
  catch { throw new Error("Ticket helper unavailable. Apply the dotfiles on this workspace's machine first."); }
  if (result.code !== 0) throw new Error(data.error || "Ticket request failed");
  return data;
}

export default class WorkspaceTickets extends View {
  init(_props, cx) {
    this.tickets = []; this.sessions = []; this.agents = []; this.drafts = new Map();
    this.mode = "fresh"; this.source = ""; this.error = ""; this.loadError = ""; this.contextKey = "";
    this.title = InputState.new({ placeholder: "Ticket title" });
    this.description = TextareaState.new({ placeholder: "Describe the work and what success looks like", rows: 6 });
    for (const input of [this.title, this.description]) {
      input.on("change", (_event, cx) => {
        if (this.contextKey) this.drafts.set(this.contextKey, [this.title.value(), this.description.value()]);
        cx.notify();
      });
    }
    this.refresh(cx);
    cx.timer.every(10000, (cx) => this.refresh(cx));
  }

  refresh(cx) {
    const workspace = context();
    if (!workspace) return;
    if (workspace.key !== this.contextKey) {
      this.contextKey = workspace.key; this.tickets = []; this.sessions = []; this.agents = [];
      this.selected = null; this.source = ""; this.mode = "fresh"; this.error = ""; this.loadError = ""; this.creating = false;
      const draft = this.drafts.get(workspace.key) || ["", ""];
      this.title.set_value(draft[0]); this.description.set_value(draft[1]);
    }
    if (this.loading || this.busy) return;
    this.loading = true;
    cx.spawn(async (cx) => {
      try {
        const data = await ticketRequest(workspace, { action: "list" });
        if (context()?.key !== workspace.key) return;
        this.tickets = data.tickets; this.sessions = data.sessions; this.agents = data.agents; this.loadError = "";
        if (!this.selected && data.tickets.length) this.selected = data.tickets[0].id;
      } catch (error) { if (context()?.key === workspace.key) this.loadError = error.message; }
      finally {
        this.loading = false;
        if (context()?.key !== workspace.key) this.refresh(cx);
        cx.notify();
      }
    });
  }

  act(action, cx) {
    const workspace = context();
    if (!workspace || this.busy || this.loading) return;
    this.busy = true; this.error = "";
    cx.spawn(async (cx) => {
      try {
        const result = await ticketRequest(workspace, action);
        if (context()?.key === workspace.key) {
          this.selected = result.id;
          if (action.action === "create") {
            this.creating = false;
            this.title.set_value(""); this.description.set_value("");
            this.drafts.delete(workspace.key);
          }
        }
      } catch (error) { if (context()?.key === workspace.key) this.error = error.message; }
      finally { this.busy = false; this.refresh(cx); cx.notify(); }
    });
    cx.notify();
  }

  button(id, text, callback, enabled = true) {
    const t = theme();
    return div().id(id).h(34).flex_none().px(10).flex().items_center().truncate().rounded(6).border_1().border_color(t.border)
      .text_size(12).text_color(enabled ? t.foreground : t.dim)
      .when(enabled, (element) => element.cursor_pointer().hover((style) => style.bg(t.hover)))
      .on_click((_event, cx) => { if (enabled && !this.busy && !this.loading) callback(cx); })
      .child(text);
  }

  render(cx) {
    const workspace = context();
    if (workspace?.key !== this.contextKey) this.refresh(cx);
    const t = theme(), ticket = this.tickets.find((entry) => entry.id === this.selected);
    const ready = !this.busy && !this.loading;
    const sources = this.mode === "fork" ? this.sessions.map((session) => ({
      value: session.path, label: session.name, detail: session.timestamp.slice(0, 16), enabled: true,
    })) : this.agents.map((agent) => ({
      value: agent.address, label: agent.title, detail: `${agent.address} / ${agent.status}`, enabled: agent.status === "idle" || agent.status === "done",
    }));
    return v_flex().id("workspace-tickets").size_full().min_h(0).rounded(10).overflow_hidden()
      .bg(t.background).border_1().border_color(t.border).text_color(t.foreground).text_size(13)
      .child(h_flex().flex_none().px(12).py(10).gap(8).items_center().border_b(1).border_color(t.border)
        .child(div().font_semibold().child("Tasks"))
        .child(div().flex_1().min_w(0).truncate().text_color(t.dim).text_size(11).child(workspace?.name || "No workspace"))
        .child(this.button("ticket-new", this.creating ? "Cancel" : "+ New", (cx) => {
          this.creating = !this.creating;
          if (this.creating) this.title.focus();
          cx.notify();
        }, Boolean(workspace))))
      .child(v_flex().id("ticket-body").flex_1().min_h(0).overflow_y_scrollbar().p(12).gap(10)
        .when(Boolean(this.error || this.loadError), (element) => element.child(div().text_color(t.ansi1).child(this.error || this.loadError)))
        .when(this.creating, (element) => element
          .child(Input.new(this.title).h(34).px(8).border_1().border_color(t.border).rounded(6))
          .child(Textarea.new(this.description).h(150).p(8).border_1().border_color(t.border).rounded(6))
          .child(this.button("ticket-create", "Create ticket", (cx) => this.act({
            action: "create", title: this.title.value(), description: this.description.value(),
          }, cx), Boolean(this.title.value().trim() && this.description.value().trim()))))
        .child(v_flex().id("ticket-list").flex_none().h(Math.min(220, this.tickets.length * 60)).overflow_y_scrollbar().gap(4)
          .children(this.tickets.map((entry) => div().id(`ticket-${entry.id}`).h(56).flex_none().p(8).rounded(7).cursor_pointer()
            .when(entry.id === this.selected, (element) => element.bg(t.selected))
            .hover((style) => style.bg(t.hover)).on_click((_event, cx) => {
              this.selected = entry.id; this.source = ""; this.mode = "fresh"; cx.notify();
            })
            .child(div().font_medium().truncate().child(entry.title))
            .child(div().text_size(11).text_color(t.dim).child(entry.status === "running"
              ? `In progress / agent ${entry.agent_status}` : entry.status === "done" ? "Done" : "To do")))))
        .when(!this.tickets.length && !this.creating, (element) => element.child(div().text_color(t.dim)
          .child(this.loading ? "Loading tickets…" : "No tickets yet. Create one for this workspace.")))
        .when(Boolean(ticket) && !this.creating, (element) => element
          .child(div().h(1).bg(t.border).my(4))
          .child(div().text_size(16).font_semibold().child(ticket.title))
          .child(div().child(ticket.description))
          .when(ticket.status === "todo", (element) => element
            .child(div().text_size(11).text_color(t.dim).child("Choose the conversation context"))
            .child(h_flex().gap(5).children([["fresh", "Fresh"], ["fork", "Fork"], ["existing", "Existing"]].map(([mode, label]) =>
              this.button(`ticket-mode-${mode}`, this.mode === mode ? `[${label}]` : label, (cx) => {
                this.mode = mode; this.source = ""; cx.notify();
              }))))
            .when(this.mode !== "fresh", (element) => element.child(v_flex().id("ticket-sources").flex_none().h(Math.min(150, Math.max(36, sources.length * 38))).overflow_y_scrollbar().gap(4)
              .children(sources.map((source, index) => this.button(`ticket-source-${index}`,
                `${this.source === source.value ? "● " : ""}${source.label} / ${source.detail}`,
                (cx) => { this.source = source.value; cx.notify(); }, source.enabled)))
              .when(!sources.length, (element) => element.child(div().text_color(t.dim).text_size(11)
                .child(this.mode === "fork" ? "No saved Pi sessions in this workspace folder." : "No live Pi terminals in this workspace folder.")))))
            .child(div().text_size(11).text_color(t.dim).child(this.mode === "fork"
              ? "Fork copies saved conversation history, not files or running processes. Use /name in Pi to identify sessions."
              : this.mode === "existing" ? "Continues a ready Pi conversation (idle or done). Do not type into it simultaneously."
                : "Starts a new conversation with the ticket title and description."))
            .child(div().text_size(11).text_color(t.dim).child("Shared workspace files: one running ticket at a time. Other agents may still edit them."))
            .child(this.button("ticket-start", this.busy ? "Starting…" : "Start ticket", (cx) => this.act({
              action: "start", id: ticket.id, mode: this.mode, source: this.source, tab: workspace.tab,
            }, cx), Boolean(ready && workspace?.tab && (this.mode === "fresh" || this.source)
              && !this.tickets.some((entry) => entry.status === "running")))))
          .when(Boolean(ticket.terminal), (element) => element
            .child(div().text_size(11).text_color(t.dim).child(`Context: ${ticket.context} / ${ticket.terminal}`))
            .child(this.button("ticket-open", "Open Pi terminal", () => run("terminal.peek", {
              terminal: ticketTerminalAddress(ticket.terminal, workspace.machine),
            })))
            .when(ticket.status !== "done", (element) => element
              .child(this.button("ticket-done", "Mark done", (cx) => this.act({ action: "status", id: ticket.id, status: "done" }, cx)))
              .child(div().text_size(11).text_color(t.dim).child("Done is manual and does not stop the agent."))))));
  }
}
