import assert from "node:assert/strict";
import test from "node:test";
import {
  localTicketId,
  ticketTerminalAddress,
  ticketWorkspaceContext,
} from "../snapshot/.config/herdr-app/mods/workspace-tickets/ticket-context.mjs";

test("remote workspace requests use remote-local IDs, not the Mac's IDs", () => {
  const workspace = ticketWorkspaceContext({
    id: "pc/s1", machine: "pc", folder: "/home/mous/repo", name: "Project",
    tabs: [{ id: "pc/tab2", active: true }],
  });
  assert.equal(workspace.workspace, "s1");
  assert.equal(workspace.tab, "tab2");
  assert.equal(workspace.machine, "pc");
  assert.equal(workspace.folder, "/home/mous/repo");
  assert.equal(ticketTerminalAddress("t7", workspace.machine), "pc/t7");
});

test("local workspace IDs stay local", () => {
  assert.equal(localTicketId("s1", null), "s1");
  assert.equal(ticketTerminalAddress("t7", null), "t7");
});

test("two machines with the same local space ID have distinct UI draft keys", () => {
  const space = { id: "pc/s1", machine: "pc", folder: "/repo", name: "Project", tabs: [] };
  const remote = ticketWorkspaceContext(space);
  const local = ticketWorkspaceContext({ ...space, id: "s1", machine: null });
  assert.notEqual(remote.key, local.key);
  assert.equal(remote.tab, "");
  assert.equal(ticketWorkspaceContext(null), null);
});
