/** Bind Lazygit to the workspace's own machine and folder, independent of terminal focus. */
export function gitWorkspaceContext(space) {
  if (!space) return null;
  const machine = space.machine ?? null;
  const workspace = machine && space.id.startsWith(machine + "/") ? space.id.slice(machine.length + 1) : space.id;
  return { machine, workspace, folder: space.folder, name: space.name,
    key: JSON.stringify([machine, space.id, space.folder]) };
}

/** Qualify a workspace machine's local terminal address for the viewing client. */
export function gitTerminalAddress(workspace, address) {
  if (address.includes("/")) throw new Error("Lazygit helper returned a non-local terminal address");
  return workspace.machine ? workspace.machine + "/" + address : address;
}

/** Locate the owned viewport without changing any other layout blocks. */
export function gitLayoutNode(tree, id) {
  if (tree?.id === id) return tree;
  for (const child of tree?.children ?? []) {
    const found = gitLayoutNode(child, id);
    if (found) return found;
  }
  return null;
}

/** Hidden panels must never start a Lazygit process. */
export function gitPanelVisible(tree) {
  return !gitLayoutNode(tree, "panel")?.hidden && gitLayoutNode(tree, "panel-body")?.active === "changes";
}

/** Runtime terminal IDs belong on the screen, never in a captured layout. */
export const gitViewportPlaceholder = { mod: "changes-readable", props: { placeholder: true } };
