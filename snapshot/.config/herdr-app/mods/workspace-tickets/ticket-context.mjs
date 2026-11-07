/** Local workspace and tab IDs are sent only to that workspace's own machine. */
export function localTicketId(id, machine) {
  return machine && id.startsWith(`${machine}/`) ? id.slice(machine.length + 1) : id;
}

/** Resolve a saved local terminal address into the viewing client's machine namespace. */
export function ticketTerminalAddress(address, machine) {
  return machine ? `${machine}/${address}` : address;
}

/** Capture the workspace identity before an asynchronous request can change UI focus. */
export function ticketWorkspaceContext(space) {
  if (!space) return null;
  const tab = space.tabs.find((entry) => entry.active);
  return {
    key: JSON.stringify([space.machine, space.id]),
    workspace: localTicketId(space.id, space.machine),
    folder: space.folder,
    machine: space.machine,
    tab: tab ? localTicketId(tab.id, space.machine) : "",
    name: space.name,
  };
}
