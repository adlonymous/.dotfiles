// An attention queue grouped by machine, from wrapping cards down to a compact rail.
import { View, div, image, svg } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { agents, terminals, spaces, run, theme, setAgentOrder } from "herdr";
import { agentPanelMode, groupActiveAgents, wrapAgentLabel } from "./agent-groups.js";

const STATUS_LABEL = { blocked: "Needs you", done: "Done", working: "Working" };
const clean = text => (text ?? "").replace(/\s+/g, " ").trim();
const initials = text => Array.from(clean(text).replace(/^[^\p{L}\p{N}]+/u, "")).slice(0, 2).join("").toUpperCase();

export default class WorkspaceAgents extends View {
  init() {
    this.width = 268;
    this.folded = new Set();
  }

  status(status, t, compact) {
    if (status === "working") return svg("mods/workspace-chrome/spinner.svg").size(12).flex_none().text_color(t.working).spin(900);
    return div().flex_none().text_size(compact ? 11 : 10).text_color(t[status])
      .child(compact ? status === "blocked" ? "!" : "●" : STATUS_LABEL[status]);
  }

  agentIcon(program, t) {
    if (!program?.icon) return div().w(14).flex_none();
    return program.tint ? svg(program.icon).size(14).flex_none().text_color(t.muted)
      : image(program.icon).w(14).h(14).flex_none();
  }

  agentRow(agent, t, mode) {
    const rail = mode === "rail", stacked = mode === "stacked";
    const tab = spaces().flatMap(space => space.tabs).find(tab => tab.id === agent.tab);
    const name = clean(tab?.named ? tab.name : `${agent.space_name || agent.program?.name || agent.address} · ${agent.tab_index}`);
    const detail = clean(agent.title || agent.program?.name);
    const columns = Math.max(2, Math.floor((this.width - (rail ? 12 : 48)) / 7));
    const tooltip = `${name}\n${detail}\n${STATUS_LABEL[agent.status]}`;
    const row = (rail ? v_flex() : h_flex()).id(`attention-agent-${agent.address}`)
      .w_full().flex_none().px(rail ? 2 : 6).py(6).gap(rail ? 3 : 6).rounded(7)
      .when(rail, el => el.items_center())
      .when(agent.focused, el => el.bg(t.selected))
      .cursor_pointer().hover(el => el.bg(t.hover)).tooltip(tooltip)
      .on_click(() => run("pane.focus", { pane: agent.pane }));
    if (rail) return row.child(this.status(agent.status, t, true))
      .child(div().text_size(10).text_color(t.foreground).child(initials(name)));
    const content = v_flex().flex_1().min_w(0).gap(3)
      .child(div().text_size(12).text_color(t.foreground).whitespace_normal().child(wrapAgentLabel(name, columns)))
      .when(detail !== name, el => el.child(div().text_size(11).text_color(t.muted).whitespace_normal().child(wrapAgentLabel(detail, columns))));
    if (stacked) content.child(div().text_size(10).text_color(t[agent.status]).child(STATUS_LABEL[agent.status]));
    return row.child(this.agentIcon(agent.program, t)).child(content).child(this.status(agent.status, t, stacked));
  }

  subRow(sub, t, mode) {
    const name = clean(sub.name || sub.template || sub.program?.name || sub.address);
    const rail = mode === "rail";
    return h_flex().id(`attention-sub-${sub.address}`).w_full().flex_none().px(rail ? 2 : 10).py(4).gap(4).rounded(5)
      .cursor_pointer().hover(el => el.bg(t.hover)).tooltip(`${name}\n${STATUS_LABEL[sub.status]}`)
      .on_click(() => run("terminal.peek", { terminal: sub.address }))
      .child(this.status(sub.status, t, true))
      .child(div().flex_1().min_w(0).text_size(10).text_color(t.muted).whitespace_normal()
        .child(rail ? initials(name) : wrapAgentLabel(name, Math.max(2, (this.width - 40) / 6))));
  }

  machineGroup(group, t, mode) {
    const label = group.machine ?? "Local";
    const id = `attention-machine-${group.machine ?? "local"}`;
    const open = !this.folded.has(id), rail = mode === "rail";
    const header = (rail ? v_flex() : h_flex()).id(id).w_full().flex_none().px(rail ? 2 : 6).py(6).gap(4)
      .when(rail, el => el.items_center()).cursor_pointer().tooltip(`${label} · ${group.members.length} agents`)
      .hover(el => el.bg(t.hover)).on_click((_event, cx) => {
        if (open) this.folded.add(id);
        else this.folded.delete(id);
        cx.notify();
      })
      .when(!rail, el => el.child(svg(`mods/workspace-chrome/chevron-${open ? "down" : "right"}.svg`).size(10).flex_none().text_color(t.dim)))
      .child(div().flex_1().min_w(0).text_size(10).font_semibold().text_color(t.dim).whitespace_normal()
        .child(rail ? initials(label) : wrapAgentLabel(label, Math.max(2, (this.width - 55) / 6))))
      .child(div().text_size(10).text_color(t.dim).child(String(group.members.length)))
      .when(!open, el => el.child(this.status(group.members[0].status, t, true)));
    return v_flex().w_full().flex_none().border_t(1).border_color(t.border).child(header)
      .when(open, el => el.children(group.members.flatMap(agent => [this.agentRow(agent, t, mode), ...agent.subs.map(sub => this.subRow(sub, t, mode))])));
  }

  render() {
    const t = theme(), mode = agentPanelMode(this.width), rail = mode === "rail";
    const groups = groupActiveAgents(agents(), terminals(), spaces());
    setAgentOrder(groups.flatMap(group => group.members.map(agent => agent.address)));
    return v_flex().id("attention-agents").size_full().min_w(0).min_h(0).bg(t.chrome).text_color(t.foreground)
      .on_size_change((size, cx) => {
        if (this.width === size.width) return;
        this.width = size.width;
        cx.notify();
      })
      .child(div().flex_none().px(rail ? 2 : 12).py(8).text_size(11).text_color(t.dim).child(rail ? "A" : "Agents"))
      .child(v_flex().id("attention-agent-list").flex_1().min_h(0).min_w(0).px(rail ? 2 : 6).overflow_y_scrollbar()
        .children(groups.map(group => this.machineGroup(group, t, mode)))
        .when(groups.length === 0, el => el.child(div().px(rail ? 0 : 6).py(6).text_size(11).text_color(t.dim)
          .tooltip("No agents working or awaiting attention").child(rail ? "·" : "No active agents"))));
  }
}
