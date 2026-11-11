---
title: Agents
slug: agents
status: published
description: AI agents for content, development, research, and design.
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

# Agents Overview

Saleh Digital uses specialized AI agents for different tasks. Each agent has a defined role, capabilities, tools, skills, and memory.

## Agent Roster

**Ada**: Content management and publishing. Drafts, edits, tags, and publishes articles and library entries.

**Dev**: Development and build. Implements components, writes shaders, optimizes performance, deploys changes.

**Web**: Research and content-gathering. Searches the web, fetches book metadata, summarizes sources, fact-checks.

**Wren**: Design and visual refinement. Imports Figma designs, maintains design harness, validates visual consistency.

## Agent Architecture

Each agent has:

1. **Role**: What the agent is responsible for
2. **Capabilities**: What the agent can do
3. **Tools**: APIs and services the agent can invoke
4. **Skills**: Procedures and workflows the agent follows
5. **Memory**: Project-specific facts and rules the agent must remember
6. **Voice**: How the agent speaks (all use owner's voice)

## Coordination

Agents can hand off work:
- Ada drafts an article → Dev implements the interactive demo → Web researches sources → Wren validates design
- User requests are routed to the appropriate agent
- Agents reference the same harness for consistency

## Common Principles

All agents:
- Write in owner's voice (first person, plain sentences)
- Reference the design harness for specs
- Follow project memory rules (em-dashes, no modals, etc.)
- Produce owner-quality output (no placeholders)
- Cite sources and document decisions

## Usage

Invoke agents explicitly:
- "Ada, write an article about..."
- "Dev, implement the..."
- "Web, find sources on..."
- "Wren, import this Figma design..."

Or let the system route implicitly based on task type.
