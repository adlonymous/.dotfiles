/** Status lamp labels and shapes describe attention, not ticket completion. */
export const AGENT_CARD_STATES = {
  working: { label: "WORKING", icon: "status-working.svg" },
  blocked: { label: "NEEDS INPUT", icon: "status-blocked.svg" },
  done: { label: "REPORT READY", icon: "status-ready.svg" },
};
const SCHEMATICS = ["turbine", "circuit", "arm", "optics", "relay", "press"];

/** Normalize reported text for cards without inferring what the agent is doing. */
export function cleanAgentText(text) {
  return String(text ?? "").replace(/[\p{Cc}\s]+/gu, " ").trim();
}

/** Keep the session marker stable across title/status changes and local/remote viewers. */
export function agentMachineGlyph(terminal) {
  const address = terminal.address.split("/").at(-1);
  const identity = `${terminal.created_ms ?? ""}:${address}`;
  let hash = 2166136261;
  for (const character of identity) hash = Math.imul(hash ^ character.codePointAt(0), 16777619) >>> 0;
  return SCHEMATICS[hash % SCHEMATICS.length];
}

/** Format only the core's actual status timestamp; missing or future timestamps stay unknown. */
export function agentStateAge(since, now) {
  if (!Number.isFinite(since) || since <= 0 || since > now) return "";
  const minutes = Math.floor((now - since) / 60000);
  return minutes < 1 ? "<1m" : minutes < 60 ? `${minutes}m` : minutes < 1440 ? `${Math.floor(minutes / 60)}h` : `${Math.floor(minutes / 1440)}d`;
}

/** Build card metadata from live core records; promoted child status uses that child's report/clock. */
export function agentCardData(agent, terminalList, spaceList, now) {
  const terminal = terminalList.find(record => record.address === agent.address) || agent;
  const space = spaceList.find(entry => entry.id === agent.space);
  const tab = space?.tabs?.find(entry => entry.id === agent.tab);
  const matches = record => record && (record.status === agent.status || (record.status === "error" && agent.status === "blocked")
    || (["idle", "done"].includes(record.status) && agent.status === "done"));
  const source = matches(terminal) ? terminal : (agent.subs || []).find(matches);
  const child = source && source.address !== agent.address;
  const report = source?.report;
  const message = cleanAgentText(report?.msg) || cleanAgentText(report?.title);
  const title = cleanAgentText(source?.title) || cleanAgentText(terminal.title) || cleanAgentText(agent.title);
  const name = cleanAgentText(terminal.name || (tab?.named ? tab.name : "") || agent.title || agent.program?.name || agent.address);
  const machine = space ? space.machine ?? "Local" : agent.address.includes("/") ? agent.address.split("/")[0] : "Local";
  const hasTitle = title && ![name, terminal.address, source?.address, terminal.address.split("/").at(-1), source?.address?.split("/").at(-1)].includes(title);
  return {
    name, machine, project: cleanAgentText(space?.name || agent.space_name || "Workspace"),
    glyph: agentMachineGlyph(terminal), status: AGENT_CARD_STATES[agent.status],
    activity: message || (hasTitle ? title : "No activity reported"),
    activityLabel: child ? "SUB-AGENT" : message ? "REPORTED" : hasTitle ? "TERMINAL" : "STATUS",
    age: agentStateAge(source?.status_ms, now),
  };
}
