---
title: "Smart Home with NocoBase 🏠 Ep.5"
part: 5
published: false
description: "Episode 5: A smart thermostat that can only display temperature is not very smart. Skills and Tools give your AI Employees the ability to act — not just respond. MCP Integration connects third-party smart devices to your hub. Web search gives Vera live access to the internet. Permission control decides who can operate which device."
tags: [nocobase, ai, mcp, tools]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/smart_home_with_nocobase_series/smart-home-with-nocobase-episode-05.png"
series: "Smart Home with NocoBase Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 5: Teaching Devices New Skills

> *“A smart thermostat that can only read temperature is interesting. One that can also order more heating oil when levels are low is genuinely useful.”*

-----

## The Difference Between Talking and Acting 🔧

So far, your AI household staff can receive questions and provide answers. That is the conversational baseline — useful, but limited. A genuinely smart home does not just tell you the front door is unlocked; it locks it. It does not just report the heating is off; it turns it on.

**Skills and Tools** are the capabilities that let AI Employees act on the world rather than merely describe it. An employee with a Knowledge Base skill can retrieve specific documents. An employee with an MCP tool can trigger a webhook, query an external API, or create a calendar event. Vera with web search does not just reason from context you provide — it fetches current information from the internet.

This episode installs those capability upgrades.

-----

## 🗂️ SIPOC — Teaching Devices New Skills

|**Suppliers**           |**Inputs**                                                     |**Process**                                                        |**Outputs**                                              |**Customers**                                                             |
|------------------------|---------------------------------------------------------------|-------------------------------------------------------------------|---------------------------------------------------------|--------------------------------------------------------------------------|
|Administrator           |Skill selection per employee (Knowledge Base, web search, etc.)|Employee → Skills tab → assign skills and permissions              |An employee with defined action capabilities             |Users — the employee can now do more than just answer questions           |
|MCP service (external)  |MCP server URL or command; tool definitions                    |AI Employees → MCP settings → Add MCP service → availability test  |A set of external tools available to AI Employees        |Employees — can call external services as part of their task handling     |
|Permission configuration|Role assignments, employee enable/disable per role             |System Settings → Permissions → assign role access to each employee|Controlled access — not every role can use every employee|Security: sensitive employees (Vera, Orin) restricted to appropriate roles|

-----

## What Are Skills? The Device Capability Manual 📋

A **Skill** is a defined capability that an AI Employee can use during a conversation. Think of it as a specific function a smart device can perform — a coffee maker has a “brew” skill, a security camera has a “record” skill, a smart lock has a “lock” and “unlock” skill.

In NocoBase, Skills are categorised permissions that control what an employee can access and invoke:

**Knowledge Base skill** — grants the employee access to the RAG-powered knowledge base (Episode 7). With this skill, the employee can search your document library for relevant information before responding.

**Web search skill** — grants the employee (specifically Vera) the ability to perform live internet searches via the OpenAI Responses API. Without this skill, Vera is a research analyst with no access to current information.

**File reading skill** — allows the employee to read uploaded files and extract information from them.

**Page operation skills** — Dex and similar employees have skills that allow them to interact with form fields on the current page — reading values, suggesting entries, and populating fields.

### Assigning Skills to an Employee

```
System Settings → AI Employees → [Edit employee] → Skills tab

Available skills (depending on your plugins):
  □ Knowledge Base    [Preview / Allow]
  □ Web Search       [Preview / Allow]
  □ File Reading     [Preview / Allow]
  □ Page Operations  [Preview / Allow]

For each skill, set the permission level:
  Ask:    Employee asks for confirmation before using the skill
  Allow:  Employee uses the skill automatically when relevant

→ Submit
```

The **Ask vs Allow** distinction is important for sensitive operations. An employee that can modify records should be set to “Ask” — it will describe what it intends to do and wait for confirmation. An employee that only reads data can be “Allow” — it can proceed without interruption.

-----

## What Are Tools? The Smart Plugs 🔌

**Tools** are more specific action capabilities than Skills — individual functions an employee can invoke. While Skills represent categories of capability (knowledge access, web search), Tools are the specific actions available within those categories.

Tool examples:

- Search the knowledge base for documents matching a query
- Read a specific file by ID
- Execute a web search query
- Format and return data from a block in a specific structure

Tools can also come from **MCP Integration** — external services you connect to the hub.

### Configuring Tools

```
System Settings → AI Employees → [Edit employee] → Tools tab

Tools available from:
  - Built-in NocoBase tools (block reading, field manipulation)
  - Installed skill packs (knowledge base search, web search)
  - MCP services you have connected

Set permission for each tool: Ask / Allow
```

The key design decision: which employees get which tools, and whether they can use them automatically or must ask permission first.

-----

## MCP Integration: The Third-Party Smart Devices 🔗

**MCP** (Model Context Protocol) is an open standard for connecting AI models to external tools and services. In the smart home analogy, MCP integration is like adding smart devices from brands that were not in the original home package — a Philips Hue light system, a Nest thermostat, a Ring doorbell — all connected through your central hub’s open integration layer.

NocoBase AI Employees can connect to any MCP service, giving them access to tools those services provide.

### Configuring an MCP Service

```
System Settings → AI Employees → MCP (tab) → Add

Two transport protocols:

Stdio (local process):
  Command:    npx
  Arguments:  @modelcontextprotocol/server-github
  Env vars:   GITHUB_TOKEN=ghp_xxxxx

HTTP (remote service):
  URL:        https://api.my-mcp-service.com/mcp
  Headers:    Authorization: Bearer xxxxx
  Type:       Streamable (recommended) or SSE
```

After adding the service, run the **availability test**. If the MCP service is reachable and the credentials are correct, the test returns a success message and lists the available tools.

### Viewing MCP Tools

Click **View** on any MCP service in the list to see all tools it provides. For each tool, configure:

```
Tool: create_calendar_event
  Permission: Ask   ← will ask confirmation before creating
  Description: Creates a new calendar event from the provided details

Tool: search_github_issues
  Permission: Allow ← can search automatically when relevant
  Description: Searches GitHub issues by query
```

### Using MCP Services

Once an MCP service is enabled, AI Employees can use its tools automatically during conversations. The employee decides when a tool is relevant, uses it (with Ask confirmation if configured), and incorporates the result into its response.

**Practical MCP examples:**

|MCP service        |What employees can do                 |Use case                                                  |
|-------------------|--------------------------------------|----------------------------------------------------------|
|GitHub MCP         |Search issues, read PRs, create issues|Ellis drafts release notes from closed issues             |
|Google Calendar MCP|Create/read/update events             |Schedule follow-up meetings from CRM records              |
|Slack MCP          |Post messages, read channels          |Vera posts research summaries to #strategy                |
|Jira MCP           |Create/update tickets                 |Ellis generates tickets from user feedback records        |
|Custom REST MCP    |Any API you wrap                      |Connect your ERP, your accounting system, your IoT devices|

-----

## Web Search: Vera Goes Online 🌐

Vera, the Research Analyst, has one capability that distinguishes her from the rest of the household staff: **live web search**. While every other employee reasons from data you provide or documents in your knowledge base, Vera can search the current internet.

**Prerequisite:** Web search requires the OpenAI **Responses API** provider (not the standard Completions API). In your LLM service list, add a second OpenAI service and select “OpenAI (Responses API)” as the provider type. Assign this provider to Vera’s model settings.

**Using web search:**

Open Vera in the chat panel and ask:

```
"What are the latest trends in B2B SaaS pricing models for 2025?"
"Find me the current contact details for [company]'s procurement team."
"What regulatory changes in GDPR enforcement have occurred this year?"
```

Vera will:

1. Formulate search queries based on your request
1. Execute web searches via OpenAI’s web search tool
1. Synthesise the results into a coherent response
1. Cite sources where appropriate

Vera is the research appliance with a live internet connection — the smart terminal that can go beyond your home’s library and pull current information from the web.

-----

## Permission Control: The Guest Access System 🔒

Not every person in the organisation should access every AI Employee. The intern should not be able to run Vera’s live web searches. The customer support team does not need Orin’s data modelling capabilities. The executive assistant needs Ellis but not Nathan.

Permission Control is the guest access system of your smart home — different keys for different rooms.

### Configuring Permissions

```
System Settings → Roles → [Select a role, e.g. "Sales Rep"]
→ AI Employees tab
→ Enable or disable specific employees for this role

Example:
  Sales Rep role:
    ✓ Atlas     (coordinator — always on)
    ✓ Ellis     (email expert — core to sales)
    ✓ Viz       (insight analyst — sales performance)
    ✓ Lexi      (translation — multilingual customers)
    ✗ Orin      (data modelling — not needed)
    ✗ Nathan    (frontend code — not relevant)
    ✗ Vera      (web search — restricted to analysts)
```

Users only see the employees they have permission to use. The employee dropdown in the chat panel shows only their permitted team.

### Per-Employee Skill Permissions

Beyond role-level access, you can configure which skills a given employee can use when accessed by different roles. An analyst might get “Allow” for all of Viz’s skills; a standard user might only get “Ask” mode, requiring confirmation for each analysis step.

-----

## The Upgraded Household: What Employees Can Do Now 🏠

After this episode, your AI household staff has moved from conversational assistants to capable collaborators:

|Employee    |Skills enabled              |Can now                                                   |
|------------|----------------------------|----------------------------------------------------------|
|Cole        |Knowledge Base              |Search your NocoBase documentation library for answers    |
|Ellis       |File reading                |Read a brief you uploaded and draft an email from it      |
|Dex         |Page operations             |Read and populate form fields directly on the page        |
|Viz         |Knowledge Base              |Cross-reference chart data with your company strategy docs|
|Vera        |Web search                  |Research current market data and competitive intelligence |
|Rex (custom)|Knowledge Base, file reading|Search legal precedents + read uploaded contract PDFs     |

-----

In **Episode 6**, we program the routines. Shortcut Tasks — binding employees to blocks, presetting task configurations, and enabling one-click AI workflows for the most common recurring scenarios.

-----

**🔗 Resources**

- **Use Skills**: [docs.nocobase.com/ai-employees/features/skills](https://docs.nocobase.com/ai-employees/features/skills)
- **Use Tools**: [docs.nocobase.com/ai-employees/features/tools](https://docs.nocobase.com/ai-employees/features/tools)
- **MCP Integration**: [docs.nocobase.com/ai-employees/features/mcp](https://docs.nocobase.com/ai-employees/features/mcp)
- **Web Search**: [docs.nocobase.com/ai-employees/features/web-search](https://docs.nocobase.com/ai-employees/features/web-search)
- **Permission Control**: [docs.nocobase.com/ai-employees/permission](https://docs.nocobase.com/ai-employees/permission)

-----

*🏠 Smart Home with NocoBase Series — building a fully connected AI-powered business application, one smart device at a time.*
