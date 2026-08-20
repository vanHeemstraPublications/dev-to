---
title: "🤖 Finally Asking the Question Out Loud"
series: "What has changed, LikeC4?"
part: 12
organization: "the-software-s-journey"
tags: [likec4, mcp, ai, agent-skills]
---

## 🤖 Finally Asking the Question Out Loud

This is the episode where the series title stops being a rhetorical device and becomes something I can literally type into a chat window. LikeC4 provides two complementary pieces for AI-powered work: Agent Skills, which teach a coding assistant the DSL syntax so it stops hallucinating attributes that don't exist, and an MCP Server, which exposes my actual, current model to an LLM as queryable knowledge — not a snapshot, not a summary someone wrote by hand, the live model.

Agent Skills install into any project with one command, using the Agent Skills Discovery protocol:

```bash
npx skills add https://likec4.dev/
```

That pulls in `likec4-dsl` — a complete DSL reference covering specification, model, views, deployment, and predicates — and it works with Claude Code, Cursor, Windsurf, and any other agent supporting the protocol. Once it's loaded, asking an agent to "add a new container called `notification_service` under `ecommerce`, with a relationship to `order_service`" produces syntactically correct DSL on the first attempt, because the agent isn't guessing at LikeC4's grammar from general training — it's reading the actual reference.

The MCP Server is the half I use more, honestly, because it's what turns "what has changed?" into a question I can just ask. Three ways to run it — through the VSCode extension automatically, through the `likec4` CLI directly:

```bash
likec4 mcp
# or
likec4 mcp --stdio

# http transport, useful for editors that need a URL
likec4 mcp --http ./src
```

or via the lighter standalone package, wired into an editor's MCP config:

```json
{
  "mcpServers": {
    "likec4": {
      "command": "npx",
      "args": ["-y", "@likec4/mcp"],
      "env": {
        "LIKEC4_WORKSPACE": "${workspaceFolder}"
      }
    }
  }
}
```

Once it's connected, the questions I actually ask start sounding less like database queries and more like the questions I'd ask a colleague who happened to have perfect memory of the entire codebase:

> *"Lookup LikeC4 model and list all incoming relationships of the backend api"*
> *"What nested elements of the 'Backend' have relations with the legacy api"*
> *"List all elements tagged legacy from team1 project"*
> *"Export to CSV all relationships between Backend and Amazon SQS"*

Underneath, that natural language resolves to real, structured tools — `search-element` for finding things by id, kind, shape, or tag; `find-relationships` for direct and indirect connections between two named elements; `query-incomers-graph` and `query-outgoers-graph` for recursively walking upstream dependencies or downstream consumers; `query-by-tags` for exactly the kind of tag filtering Episode 6 set up; and, genuinely the one I reach for most when writing this series' own premise into practice, `element-diff` — compare two elements and show differences in properties, tags, metadata, and relationships. That's "what has changed?" as an actual, callable tool, not a metaphor.

I want to be precise about what this replaces and what it doesn't. It doesn't replace `likec4 validate` in CI — that's still the hard, mechanical gate blocking a bad merge. What it replaces is the part of my Monday morning that used to involve me personally re-reading diagrams, trying to hold last week's mental model up against this week's file tree. Now I ask, and the model — the actual, current, just-validated-in-CI model — answers.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `npx skills add https://likec4.dev/` | The Agent Skills Discovery protocol | Install the `likec4-dsl` reference into the AI coding agent's context | An agent that writes syntactically correct LikeC4 DSL on the first attempt | Any AI-assisted editing of `.c4` files |
| The LikeC4 MCP Server | A running, current LikeC4 workspace | Expose structured query tools (`search-element`, `find-relationships`, `element-diff`, and more) | Natural-language-answerable architecture queries | The architect (me), asking questions instead of re-reading diagrams |
| `element-diff` specifically | Two named elements or two points in time | Compare properties, tags, metadata, and relationships | A direct, tool-level answer to "what has changed?" | This series' entire premise, made literal |

Next stop: the final episode — standing back and looking at the whole habit this series has built, from a blank specification file to a question I can ask out loud.
