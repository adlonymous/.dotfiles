// Pi's bash tool has no TTY, so sudo cannot collect a password there.
// Block it and direct the agent to pkexec, which uses the graphical Polkit agent.
export default function (pi) {
  pi.on("tool_call", (event) => {
    if (event.toolName !== "bash" || typeof event.input?.command !== "string") {
      return;
    }

    if (/\bsudo\b/.test(event.input.command)) {
      return {
        block: true,
        reason: "Pi's bash tool has no terminal for sudo. Use pkexec for a single privileged command instead. It opens the graphical Polkit password prompt. Do not pass a password through stdin, arguments, or environment variables.",
      };
    }
  });
}
