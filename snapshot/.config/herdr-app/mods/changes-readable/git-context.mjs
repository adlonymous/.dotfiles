/** Resolve a workspace's first terminal folder, never whichever terminal has keyboard focus. */
export function gitWorkspaceContext(space, paneList = []) {
  if (!space) return null;
  const first = (space.tabs || []).flatMap(tab => paneList.filter(pane => pane.tab === tab.id && pane.terminal))[0];
  const folder = first?.cwd || space.folder;
  const machine = space.machine ?? null;
  return { machine, folder, name: space.name, key: JSON.stringify([machine, space.id, folder]) };
}

/** Block default-branch pushes in the UI; the backend also verifies the actual remote default. */
export function gitPushProtected(state) {
  return !state?.head || !state.branch || ["main", "master", state.default_branch].includes(state.branch);
}
