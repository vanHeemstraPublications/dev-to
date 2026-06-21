---
title: "Luxo Jr. with Palmier! Ep.4: Plugging In Luxo Jr."
published: false
description: "Episode 4: A lamp without a cord is just a sculpture. This episode opens the wiring underneath Palmier Pro's desk — the local MCP server running at http://127.0.0.1:19789/mcp — and walks through connecting four different doorways an AI agent can bounce in through: Claude Code, Codex, Cursor, and Claude Desktop."
tags: [mcp, ai, claudecode, cursor]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/luxo-jr-palmier-episode-04.png"
series: "Luxo Jr. with Palmier"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

# Luxo Jr. with Palmier! 💡
## Episode 4: Plugging In Luxo Jr.

---

## A Lamp Without a Cord Is Just a Sculpture

Luxo Jr. doesn't bounce because it's a lamp. It bounces because something underneath the desk is supplying it with the energy to move — wiring we never see in the actual short, taken entirely for granted, but absolutely load-bearing. Without it, both lamps are just well-designed metal sitting still.

For Palmier Pro, that hidden wiring is the **Model Context Protocol (MCP)** server every open project quietly runs. It's the difference between "an editor with some AI features" and "an editor your actual coding agent can walk into and use." This episode is about the cord, the socket, and the four doors through which an agent can plug in.

---

## SIPOC — The MCP Connection Layer

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| Palmier Pro (running, with a project open) | An open project's timeline, media pool, and generative tools | Expose all of it as an MCP server over local HTTP | A live endpoint at `http://127.0.0.1:19789/mcp` | Any MCP-capable client running on the same machine |
| The Model Context Protocol | A standardized schema for tools, resources, and prompts | Define how clients discover and call tools without bespoke integration code per app | A common language every agent and every tool-providing app can speak | The whole AI-agent ecosystem, not just Palmier Pro |
| MCP clients (Claude Code, Codex, Cursor, Claude Desktop) | The endpoint URL, a short config entry | Register Palmier Pro as a tool source; list and call its tools on request | An agent that can read your project and act on your timeline | You, directing the agent's work from inside your usual coding tool |

---

## What MCP Actually Is, in One Paragraph

The Model Context Protocol is an open standard for letting an AI agent discover and call tools exposed by some other piece of software, without that software needing a bespoke integration written specifically for that one agent. Instead of Palmier Pro shipping a "Claude plugin" and a separate "Cursor plugin" and a separate "Codex plugin," it ships *one* MCP server, and any client that speaks MCP — present or future — can talk to it. This is precisely why the same `http://127.0.0.1:19789/mcp` endpoint works identically whether Luxo Jr. walks in wearing a Claude Code costume or a Cursor costume. The wiring underneath the desk doesn't care which lamp plugs in.

```
WITHOUT MCP (the world before a shared standard)

  Palmier Pro  --bespoke integration-->  Claude Code
  Palmier Pro  --bespoke integration-->  Cursor
  Palmier Pro  --bespoke integration-->  Codex
  Palmier Pro  --bespoke integration-->  Claude Desktop

  Four separate integrations to build and maintain.
  A fifth agent shows up next year? A fifth integration.


WITH MCP (the actual Palmier Pro architecture)

  Palmier Pro  --MCP server-->  http://127.0.0.1:19789/mcp
                                          |
                +-------------+----------+----------+-------------+
                v             v          v          v             v
          Claude Code      Codex      Cursor   Claude Desktop  (anything
                                                                 future)

  ONE server. As many doors as there are MCP clients, present and future.
```

---

## Where the Server Actually Lives

```
Per Palmier Pro project, while the app is open:

  Protocol:   HTTP
  Host:       127.0.0.1  (localhost only -- never exposed to your network)
  Port:       19789
  Path:       /mcp
  Full URL:   http://127.0.0.1:19789/mcp

  Lifecycle:  starts when the project opens, stops when it closes.
              No project open -> no server running -> nothing to connect to.
```

That `127.0.0.1` matters enormously and is worth a sentence of its own: this is a loopback address. It is not reachable from any other device on your network, let alone the internet. The wiring under the desk stays under the desk; it's local to the same machine running both the editor and the agent, by design.

---

## Door One: Claude Code

```bash
claude mcp add --transport http palmier-pro http://127.0.0.1:19789/mcp
```

One line. Claude Code now treats Palmier Pro's project as a tool source for the duration of your session, alongside whatever else you've already wired up: your filesystem tools, your git tools, anything else on your MCP roster.

---

## Door Two: Codex

```bash
codex mcp add palmier-pro --url http://127.0.0.1:19789/mcp
```

Functionally identical to the Claude Code line above: same endpoint, same registration concept, different CLI vocabulary. This is the MCP standard doing exactly what it's supposed to: the *server* doesn't change at all between these two doors, only the *client-side incantation* to walk through them does.

---

## Door Three: Cursor

Two paths, both ending at the same place.

**The easy way: let the app write the config for you**

```
Inside Palmier Pro:
  Help -> MCP Instructions -> Install in Cursor
```

**The manual way: edit Cursor's config directly**

```json
// ~/.cursor/mcp.json
{
  "mcpServers": {
    "palmier-pro": {
      "type": "http",
      "url": "http://127.0.0.1:19789/mcp"
    }
  }
}
```

Save that file, restart or reload Cursor, and the same endpoint from Doors One and Two is now reachable from a third room entirely.

---

## Door Four: Claude Desktop

This door doesn't even ask you to type anything. Palmier Pro bundles an `.mcpb` file (a Desktop Extension) directly with the app, which means a one-click install straight into Claude Desktop. Open the extension, click install, and Claude Desktop registers the same `http://127.0.0.1:19789/mcp` endpoint without you ever touching a JSON file or a terminal.

```
mcpb/  <- the bundled Desktop Extension, shipped inside Palmier Pro's repo

Install flow:
  1. Open the .mcpb file from inside the app, or from the repo's mcpb/ folder
  2. Claude Desktop prompts: "Install this extension?"
  3. Click install
  4. Claude Desktop now lists palmier-pro as an available tool source
```

---

## All Four Doors, One Floor Plan

```
+-----------------------------------------------------------------------+
|                          YOUR macOS MACHINE                          |
|                                                                       |
|   +------------------------------------------------------------+    |
|   |   Palmier Pro (project open)                                |    |
|   |                                                              |    |
|   |   MCP server: http://127.0.0.1:19789/mcp                    |    |
|   |   (loopback only -- never leaves this machine)               |    |
|   +---------------------------+----------------------------------+    |
|                               |                                       |
|         +---------------------+---------------------+---------------+|
|         |                     |                     |               ||
|         v                     v                     v               v|
|  +------------+      +-------------+       +-------------+  +----------+
|  |claude mcp  |      |codex mcp    |       |~/.cursor/   |  |.mcpb     |
|  |add --http  |      |add --url    |       |mcp.json     |  |one-click |
|  +-----+------+      +------+------+       +------+------+  +----+-----+
|        v                    v                     v              v     |
|  +------------+      +-------------+       +-------------+  +----------+
|  |Claude Code |      |   Codex     |       |   Cursor    |  | Claude   |
|  |            |      |             |       |             |  | Desktop  |
|  +------------+      +-------------+       +-------------+  +----------+
|                                                                       |
|         Four different lamps. One socket. Same light underneath.      |
+-----------------------------------------------------------------------+
```

---

## Confirming the Lamp Is Actually Plugged In

After connecting through any of the four doors, the simplest sanity check is asking your agent to list what it sees:

```
You (in Claude Code, Codex, or Cursor):
  "What tools do you have available from palmier-pro?"

Expected kind of response (the specific tool names are explored in
full in Episode 5):
  - generate_video
  - generate_image
  - generate_audio
  - trim_clip
  - organize_footage
  - transcribe_audio
  - ... and more, depending on the project's current state
```

If that list comes back empty, the most common culprits are mundane and worth checking in order: is Palmier Pro actually open with a project loaded (no project, no server), is the port `19789` free on your machine, and did the client config actually get saved and reloaded.

---

## What's Next: Teaching the Small Lamp to Bounce

The cord is plugged in. The socket has power. But a lamp that's merely *connected* isn't yet a lamp that's *doing* anything. In **Episode 5**, we put real weight on these wires: calling Palmier Pro's actual MCP tools to generate footage, edit the timeline, organize a media pool, and transcribe audio, with real tool-call examples for each.

---

**Resources**
- **Palmier Pro -- MCP server section**: [github.com/palmier-io/palmier-pro#mcp-server](https://github.com/palmier-io/palmier-pro#mcp-server)
- **Model Context Protocol**: [modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Claude Code MCP docs**: [docs.claude.com/en/docs/claude-code/mcp](https://docs.claude.com/en/docs/claude-code/mcp)

---

*Luxo Jr. with Palmier -- one big lamp, one small lamp, one timeline lit together.*
