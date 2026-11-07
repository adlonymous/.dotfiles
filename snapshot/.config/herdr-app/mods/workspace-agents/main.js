// A machine-grouped attention queue, with stable session schematics and real state clocks.
import { View, div, svg } from "gpui-kit";
import { v_flex, h_flex } from "gpui-base";
import { agents, terminals, spaces, run, theme, setAgentOrder } from "herdr";
import { agentPanelMode, groupMachineAgents, wrapAgentLabel } from "./agent-groups.js";
import { AGENT_CARD_STATES, agentCardData, agentMachineGlyph, cleanAgentText } from "./agent-card.js";

const initials = text => Array.from(cleanAgentText(text).replace(/^[^\p{L}\p{N}]+/u, "")).slice(0, 2).join("").toUpperCase();

export default class WorkspaceAgents extends View {
  init(_props, cx) {
    this.width = 268;
    this.folded = new Set();
    this.expandedIdle = new Set();
    // This updates elapsed labels, never animation frames or an invented progress meter.
    cx.timer.every(30000, cx => cx.notify());
  }

  status(status, t, age = "", compact = false) {
    const state = AGENT_CARD_STATES[status];
    const skinny = !compact && this.width < 140;
    const lamp = h_flex().min_w(0).gap(5).items_center().text_color(status === "idle" ? t.dim : t[status])
      .child(svg("mods/workspace-agents/schematics/" + state.icon).size(12).flex_none())
      .when(!compact, el => el.child(div().flex_1().min_w(0).text_size(skinny ? 8 : 9).font_semibold().whitespace_normal().child(state.label)));
    const clock = div().flex_none().text_size(10).text_color(t.dim).child(age);
    return skinny ? v_flex().gap(3).child(lamp).when(Boolean(age), el => el.child(clock.pl(17)))
      : lamp.when(Boolean(age) && !compact, el => el.child(clock));
  }

  schematic(glyph, size, t) {
    return div().size(size).flex_none().flex().items_center().justify_center().rounded(3)
      .bg(t.chrome).border_1().border_color(t.border).accessibility_label("Session marker: " + glyph)
      .child(svg("mods/workspace-agents/schematics/" + glyph + ".svg").size(size - 8).text_color(t.muted));
  }

  agentCard(agent, t, mode, allTerminals, allSpaces, now) {
    const card = agentCardData(agent, allTerminals, allSpaces, now);
    const rail = mode === "rail", skinny = this.width < 140, wide = mode === "wide";
    const metadata = `${card.project} · ${card.machine}`;
    const tooltip = `${card.name}\n${metadata}\n${card.status.label}${card.age ? " · " + card.age : ""}\n${card.activityLabel}: ${card.activity}`;
    const row = v_flex().id(`attention-agent-${agent.address}`).w_full().min_w(0).flex_none()
      .p(rail ? 3 : 8).gap(6).rounded(4).overflow_hidden().bg(agent.focused ? t.selected : t.surface)
      .border_1().border_color(agent.focused ? t.accent : t.border)
      .when(rail, el => el.items_center())
      .cursor_pointer().hover(el => el.bg(t.hover)).tooltip(tooltip).accessibility_label(tooltip)
      .on_click(() => run("pane.focus", { pane: agent.pane }));
    if (rail) return row.child(this.schematic(card.glyph, 26, t)).child(this.status(agent.status, t, "", true))
      .child(div().text_size(9).text_color(t.foreground).child(initials(card.name)));
    const header = skinny ? v_flex().gap(6) : h_flex().min_w(0).gap(8).items_center();
    header.child(this.schematic(card.glyph, wide ? 40 : 28, t))
      .child(div().flex_1().min_w(0).text_size(12).font_semibold().whitespace_normal().child(wrapAgentLabel(card.name,
        Math.max(3, (this.width - (skinny ? 36 : wide ? 86 : 74)) / 7.5), 2)));
    return row.child(header)
      .when(!skinny, el => el.child(div().text_size(10).text_color(t.dim).whitespace_normal()
        .child(wrapAgentLabel(metadata, Math.max(3, (this.width - 36) / 6), 2))))
      .child(this.status(agent.status, t, card.age))
      .when(!skinny, el => el.child(div().text_size(11).text_color(t.muted).whitespace_normal()
        .child(wrapAgentLabel(`${card.activityLabel}: ${card.activity}`, Math.max(3, (this.width - 36) / 6.5), 2))));
  }

  subRow(sub, t, mode) {
    const name = cleanAgentText(sub.name || sub.template || sub.program?.name || sub.address);
    const rail = mode === "rail";
    return h_flex().id(`attention-sub-${sub.address}`).w_full().min_w(0).flex_none().px(rail ? 2 : 10).py(5).gap(5).rounded(3)
      .cursor_pointer().hover(el => el.bg(t.hover)).tooltip(`${name}\n${AGENT_CARD_STATES[sub.status].label}`)
      .accessibility_label(`${name}, ${AGENT_CARD_STATES[sub.status].label}, open sub-agent`)
      .on_click(() => run("terminal.peek", { terminal: sub.address }))
      .when(!rail, el => el.child(svg("mods/workspace-agents/schematics/" + agentMachineGlyph(sub) + ".svg").size(16).flex_none().text_color(t.muted)))
      .child(this.status(sub.status, t, "", true))
      .child(div().flex_1().min_w(0).text_size(10).text_color(t.muted).whitespace_normal()
        .child(rail ? initials(name) : wrapAgentLabel(name, Math.max(2, (this.width - 65) / 6))));
  }

  idleSection(group, t, mode, allTerminals, allSpaces, now) {
    const idle = group.members.filter(agent => agent.status === "idle");
    if (!idle.length) return null;
    const id = `idle-machine-${group.machine ?? "local"}`;
    const open = this.expandedIdle.has(id), rail = mode === "rail";
    return v_flex().w_full().min_w(0).flex_none().gap(6)
      .child(h_flex().id(id).w_full().min_w(0).flex_none().px(rail ? 2 : 6).py(6).gap(4)
        .cursor_pointer().text_color(t.dim).tooltip(`Idle · ${idle.length} agents`)
        .accessibility_label(`Idle, ${idle.length} agents, ${open ? "expanded" : "collapsed"}`)
        .hover(el => el.bg(t.hover)).on_click((_event, cx) => {
          if (open) this.expandedIdle.delete(id);
          else this.expandedIdle.add(id);
          cx.notify();
        })
        .when(!rail, el => el.child(svg(`mods/workspace-chrome/chevron-${open ? "down" : "right"}.svg`).size(10).flex_none()))
        .child(div().flex_1().min_w(0).text_size(10).child(rail ? "I" : "Idle"))
        .child(div().text_size(10).child(String(idle.length))))
      .when(open, el => el.children(idle.map(agent => this.agentCard(agent, t, mode, allTerminals, allSpaces, now))));
  }

  machineGroup(group, t, mode, allTerminals, allSpaces, now) {
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
      .when(!open, el => el.child(this.status(group.members[0].status, t, "", true)));
    return v_flex().w_full().flex_none().border_t(1).border_color(t.border).child(header)
      .when(open, el => el.child(v_flex().w_full().min_w(0).gap(6).pb(8)
        .children(group.members.filter(agent => agent.status !== "idle").flatMap(agent => [
          this.agentCard(agent, t, mode, allTerminals, allSpaces, now), ...agent.subs.map(sub => this.subRow(sub, t, mode)),
        ]))
        .child(this.idleSection(group, t, mode, allTerminals, allSpaces, now))));
  }

  render() {
    const t = theme(), mode = agentPanelMode(this.width), rail = mode === "rail";
    const allTerminals = terminals(), allSpaces = spaces();
    const groups = groupMachineAgents(agents(), allTerminals, allSpaces), now = Date.now();
    setAgentOrder(groups.flatMap(group => group.members.map(agent => agent.address)));
    return v_flex().id("attention-agents").size_full().min_w(0).min_h(0).bg(t.chrome).text_color(t.foreground)
      .on_size_change((size, cx) => {
        if (this.width === size.width) return;
        this.width = size.width;
        cx.notify();
      })
      .child(div().flex_none().px(rail ? 2 : 12).py(8).text_size(11).text_color(t.dim).child(rail ? "A" : "Agents"))
      .child(v_flex().id("attention-agent-list").flex_1().min_h(0).min_w(0).px(rail ? 2 : 6).overflow_y_scrollbar()
        .children(groups.map(group => this.machineGroup(group, t, mode, allTerminals, allSpaces, now)))
        .when(groups.length === 0, el => el.child(div().px(rail ? 0 : 6).py(6).text_size(11).text_color(t.dim)
          .tooltip("No agents in connected workspaces").child(rail ? "·" : "No agents"))));
  }
}
