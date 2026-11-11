---
title: Post actions
slug: post-actions
status: published
description: "The row under a post (Open in MCP marks, Discuss, Copy link, Copy text, Sound); hidden on the live site; steps out while the post changes."
chips:
  - Pattern
  - Actions
created: 2026-11-09T21:04:27Z
updated: 2026-11-11T16:08:52Z
---

Under the post, `.post-meta` (16px gap, Inter Display 16/16) holds:

1. **Open in**: three app marks (Claude, Codex, Grokbot) that open a sheet with the MCP steps.
2. **Discuss**: a link with a count.
3. **Copy link**: copies the share URL, then shows "copied" (a single green check) for 1.6s.
4. **Copy text**: the post as plain text: the title, the paragraphs as shown, then its link.
5. **Sound**: an `aria-pressed` toggle of `sd:sound`.

The icons are [icon buttons](../components/icon-button.md).

**On the live site every action is `hidden`**, and with every action switched off the row takes no room (`.post-meta[hidden] { display: none }`). MCP moved to Settings › MCP. Rebuild the row hidden. Its motion is still specified: it steps out while the body changes (`.is-away`: opacity 0, translateY 4px, blur 3px over 90ms) and settles back when the stream ends (opacity and filter 260ms, transform 320ms, land). See [resolve](../../foundations/motion/resolve.md).

Source: `site/css/site.css`, lines 295 to 307

```css
/* ---------- actions under the post: Open in, then link and sound ---------- */
.post-meta {
  flex-direction: row; align-items: center; gap: 16px;
  margin-top: calc(var(--para) * 1.5);
  font: 400 16px/16px var(--ui); letter-spacing: var(--track);
}
.post-meta .openin { margin-right: 4px; }

/* the actions row steps out while the post changes and settles back once the text lands */
.post-meta { transition: opacity 260ms var(--ease-land), transform 320ms var(--ease-land), filter 260ms var(--ease-land); }
.post-meta.is-away { opacity: 0; transform: translateY(4px); filter: url(#ink-ui) blur(3px); pointer-events: none; transition-duration: 90ms; }
@media (prefers-reduced-motion: reduce) { .post-meta, .post-meta.is-away { transition: opacity 120ms linear; transform: none; filter: url(#ink-ui); } }
.post-meta[hidden] { display: none; }
```


Source: `site/css/site.css`, lines 314 to 353

```css
/* ---------- Open in MCP: three app marks, then a sheet with the steps ---------- */
.mcp-apps { display: flex; align-items: center; gap: 8px; }
.mcp-app { display: grid; place-items: center; width: 16px; height: 16px; padding: 0; border: 0; background: none; color: color-mix(in srgb, var(--ink) 62%, var(--paper)); cursor: pointer; transition: color 160ms var(--ease-land), transform 160ms var(--ease-land); }
.mcp-app svg { width: 16px; height: 16px; display: block; }
.mcp-app:hover, .mcp-app:focus-visible { color: var(--ink); outline: none; }
.mcp-app:focus-visible { box-shadow: 0 0 0 2px var(--paper), 0 0 0 3px var(--ring); border-radius: 3px; }
.mcp-app:active { transform: scale(0.88); }

.mcp-modal { width: min(440px, calc(100vw - 32px)); max-height: calc(100dvh - 48px); padding: 0; border: 0; border-radius: 14px; background: var(--paper); color: var(--ink); overflow: auto;
  box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 10%, transparent), 0 2px 6px color-mix(in srgb, var(--shadow) calc(6% * var(--shadow-k)), transparent), 0 24px 64px -12px color-mix(in srgb, var(--shadow) calc(22% * var(--shadow-k)), transparent);
  font: 400 14px/20px var(--ui); letter-spacing: -0.2px; }
.mcp-modal::backdrop { background: color-mix(in srgb, var(--paper) 78%, transparent); }
.mcp-sheet { display: flex; flex-direction: column; gap: 20px; padding: 20px 20px 18px; margin: 0; }
.mcp-head { display: grid; grid-template-columns: 28px 1fr 24px; gap: 12px; align-items: start; }
.mcp-logo { display: grid; place-items: center; width: 28px; height: 28px; border-radius: 8px; box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--ink) 12%, transparent); }
.mcp-logo svg { width: 16px; height: 16px; }
.mcp-head h2 { margin: 0; font: 400 16px/20px var(--ui); letter-spacing: -0.64px; }
.mcp-lede { margin: 2px 0 0; color: color-mix(in srgb, var(--ink) 56%, var(--paper)); }
.mcp-close { width: 24px; height: 24px; display: grid; place-items: center; padding: 0; border: 0; border-radius: 6px; background: none; color: color-mix(in srgb, var(--ink) 50%, var(--paper)); cursor: pointer; }
.mcp-close svg { width: 14px; height: 14px; }
.mcp-close:hover, .mcp-close:focus-visible { color: var(--ink); background: color-mix(in srgb, var(--ink) 6%, transparent); outline: none; }
.mcp-field, .mcp-code { display: flex; align-items: center; gap: 10px; padding: 8px 8px 8px 12px; border-radius: 9px; background: color-mix(in srgb, var(--ink) 4%, var(--paper)); box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--ink) 7%, transparent); }
.mcp-label { color: color-mix(in srgb, var(--ink) 50%, var(--paper)); }
.mcp-field code, .mcp-code code { flex: 1; min-width: 0; font: 400 13px/18px ui-monospace, "SF Mono", Menlo, monospace; letter-spacing: 0; overflow-wrap: break-word; }
.mcp-code { align-items: flex-start; }
.mcp-code[hidden] { display: none; }
.mcp-copy { flex: none; height: 24px; padding: 0 9px; border: 0; border-radius: 6px; background: var(--paper); color: var(--ink); font: inherit; font-size: 13px; cursor: pointer; box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 12%, transparent), 0 1px 1px color-mix(in srgb, var(--shadow) calc(5% * var(--shadow-k)), transparent); transition: box-shadow 160ms var(--ease-land); }
.mcp-copy:hover { box-shadow: 0 0 0 1px color-mix(in srgb, var(--ink) 24%, transparent), 0 1px 2px color-mix(in srgb, var(--shadow) calc(8% * var(--shadow-k)), transparent); }
.mcp-copy.is-done, .mcp-go.is-done { color: color-mix(in srgb, var(--ink) 60%, var(--paper)); }
.mcp-steps { margin: 0; padding: 0; list-style: none; counter-reset: s; display: flex; flex-direction: column; gap: 10px; }
.mcp-steps li { counter-increment: s; display: grid; grid-template-columns: 20px 1fr; gap: 8px; }
.mcp-steps li::before { content: counter(s); font-variant-numeric: tabular-nums; color: color-mix(in srgb, var(--ink) 40%, var(--paper)); }
.mcp-foot { display: flex; align-items: center; gap: 16px; padding-top: 16px; border-top: 1px solid color-mix(in srgb, var(--ink) 8%, transparent); }
.mcp-note { flex: 1; min-width: 0; font-size: 12px; line-height: 16px; color: color-mix(in srgb, var(--ink) 50%, var(--paper)); overflow-wrap: anywhere; }
.mcp-go { flex: none; height: 32px; display: inline-flex; align-items: center; padding: 0 14px; border-radius: 8px; background: var(--ink); color: var(--paper); text-decoration: none; cursor: pointer; white-space: nowrap; transition: transform 120ms var(--ease-land), background 160ms var(--ease-land); }
.mcp-go:hover { background: color-mix(in srgb, var(--ink) 84%, var(--paper)); }
.mcp-go:active { transform: scale(0.97); }
.mcp-go:focus-visible { outline: none; box-shadow: 0 0 0 2px var(--paper), 0 0 0 3px var(--ring); }
@media (max-width: 480px) { .mcp-foot { flex-direction: column; align-items: stretch; } .mcp-go { justify-content: center; } .mcp-label { display: none; } .mcp-field code, .mcp-code code { font-size: 12px; } }
```


Source: `site/css/site.css`, lines 900 to 903

```css
/* with every action switched off, the actions row takes no room */
.meta-ico[hidden] { display: none; }
.post-meta:not(:has(> :not([hidden]))) { display: none; }
```
