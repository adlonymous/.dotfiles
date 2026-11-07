const AGENT_PRIORITY = { blocked: 3, done: 2, working: 1 };

// Group the attention queue by machine; idle parents remain only for active sub-agents.
export function groupActiveAgents(agents, terminals, spaces) {
  const listed = new Map(agents.map(agent => [agent.address, agent]));
  const machineBySpace = new Map(spaces.map(space => [space.id, space.machine]));
  const children = parent => terminals.filter(terminal => terminal.parent === parent && terminal.state === "live" && !listed.has(terminal.address))
    .flatMap(terminal => {
      const status = terminal.status === "error" ? "blocked" : terminal.status;
      return [
        ...(status === "blocked" || status === "working" ? [{ ...terminal, status }] : []),
        ...children(terminal.address),
      ];
    });
  const groups = new Map();
  for (const agent of agents) {
    const subs = children(agent.address);
    const status = [agent.status, ...subs.map(sub => sub.status)]
      .sort((a, b) => (AGENT_PRIORITY[b] ?? 0) - (AGENT_PRIORITY[a] ?? 0))[0];
    if (!AGENT_PRIORITY[status]) continue;
    const machine = machineBySpace.has(agent.space) ? machineBySpace.get(agent.space)
      : agent.address.includes("/") ? agent.address.split("/")[0] : null;
    if (!groups.has(machine)) groups.set(machine, { machine, members: [] });
    groups.get(machine).members.push({ ...agent, status, subs });
  }
  for (const group of groups.values()) group.members.sort((a, b) => AGENT_PRIORITY[b.status] - AGENT_PRIORITY[a.status] || b.seq - a.seq);
  return [...groups.values()];
}

// Wrap even unbroken machine names and cap task labels without dropping the whole row.
export function wrapAgentLabel(text, columns, maxLines = 3) {
  const characters = Array.from((text ?? "").replace(/\s+/g, " ").trim());
  const width = Math.max(1, Math.floor(columns));
  const lines = [];
  while (characters.length && lines.length < maxLines) {
    const space = characters.slice(0, width + 1).lastIndexOf(" ");
    const take = characters.length > width && space > 0 ? space : width;
    lines.push(characters.splice(0, take).join(""));
    while (characters[0] === " ") characters.shift();
  }
  if (characters.length) lines[lines.length - 1] = Array.from(lines.at(-1)).slice(0, -1).join("") + "…";
  return lines.join("\n");
}

// Read the actual panel width, not the sidebar's saved or collapsed state.
export function agentPanelMode(width) {
  return width < 80 ? "rail" : width < 240 ? "stacked" : "wide";
}
