---
title: "Smart Home with NocoBase 🏠 Ep.1"
part: 1
published: false
description: "Episode 1: A smart home hub connects every device in your house to a single brain. NocoBase AI Builder does the same for your business application — connecting AI models, giving them specialised roles, wiring them into your data and workflows. Meet the hub."
tags: [nocobase, ai, nocode, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/smart_home_nocobase_series/smart-home-nocobase-episode-01.png"
series: "Smart Home with NocoBase Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 1: The Smart Home Hub

> *“A smart home is not about the individual devices. It is about the hub that makes them work together as a coherent system.”*

-----

## The Problem with Dumb Homes 🏚️

Before smart home technology, every appliance in your house was an island. The thermostat had no idea the windows were open. The security camera could not tell the porch light to turn on. The coffee maker knew nothing about your morning alarm. Every device did its job in isolation — functional, but completely unable to collaborate with anything else.

Businesses face the same problem with AI. A team uses ChatGPT for writing. Another uses a different model for data analysis. Someone else copy-pastes spreadsheet data into a prompt manually. Every AI interaction is isolated, disconnected from the business data, triggering nothing, learning nothing, remembered by nothing.

**NocoBase AI Builder** is the smart home hub for your business intelligence. It connects AI models to your application data, gives AI agents specialised roles, wires them into your pages and workflows, and lets them collaborate as a system — not just as isolated tools you switch between manually.

This series builds that smart home from the ground up, one episode per capability layer.

-----

## 🗂️ SIPOC — The Smart Home Hub

|**Suppliers**                                                 |**Inputs**                                                         |**Process**                                                                     |**Outputs**                                                              |**Customers**                                                         |
|--------------------------------------------------------------|-------------------------------------------------------------------|--------------------------------------------------------------------------------|-------------------------------------------------------------------------|----------------------------------------------------------------------|
|LLM providers (OpenAI, Gemini, Claude, DeepSeek, Qwen, Ollama)|API keys, model IDs, base URLs                                     |NocoBase plugin-ai connects to providers; configures available models           |A pool of AI intelligence available to every employee and workflow       |AI Employees, Workflow LLM Nodes, Knowledge Base embedding            |
|NocoBase administrators                                       |Employee profiles, system prompts, skill assignments, task presets |AI Employee configuration: role, behaviour, knowledge, permissions              |Specialised AI agents with defined jobs and access scopes                |Business users who collaborate with employees via the AI Floating Ball|
|Business users                                                |Natural language instructions, uploaded files, selected page blocks|AI Employees process requests in context of page data, knowledge base, and tools|Answers, drafted content, data analysis, formatted records, chart configs|The user — gets things done without leaving the NocoBase interface    |

-----

## The Smart Home Metaphor: Every AI Concept, Explained Once 🏠

This table is the master key to the series. Every episode returns to it.

|Smart home concept                            |NocoBase AI Builder concept                                           |
|----------------------------------------------|----------------------------------------------------------------------|
|The smart home hub                            |NocoBase itself — the platform everything runs on                     |
|The hub’s AI coordinator                      |**Atlas** — the AI that routes your request to the right employee     |
|Connecting to the power grid                  |**LLM Service** — plugging in the AI brain (OpenAI, Gemini, etc.)     |
|Smart appliances / devices                    |**AI Employees** — each with a specialised job                        |
|Each device’s instruction manual              |**System prompt / Role Setting** — defines what each employee does    |
|The control panel / remote                    |**AI Floating Ball** — the chat entry point in the bottom-right corner|
|A room-specific control panel                 |**Block Action entry** — an employee bound to a specific page block   |
|Room sensors feeding data                     |**Block Context (Pick Block)** — sending live page data to the AI     |
|What a device can do (heat, cool, schedule)   |**Skills** — tool permissions for each employee                       |
|Smart plugs from third-party brands           |**MCP Integration** — external tool services wired into the hub       |
|Pre-programmed routines (“Good Morning”)      |**Shortcut Tasks** — one-click preset tasks per block                 |
|The home manual / document library            |**AI Knowledge Base + RAG** — documents the AI can search             |
|Automation rules / schedules                  |**Workflow LLM Nodes** — AI embedded in automated pipelines           |
|Multi-room audio / cameras (different formats)|**Multimodal Chat** — images, files, and mixed content types          |
|Guest access permissions                      |**Permission Control** — role-based access to AI employees            |
|Smart filing cabinet                          |**File Management** — upload documents as AI context                  |
|The home installation guide                   |**Prompt Engineering Guide** — best practices for instructions        |

-----

## What Is NocoBase AI Builder? 🔍

NocoBase is an open-source, extensible no-code/low-code platform for building business applications. The **AI Builder** capability is delivered through the `@nocobase/plugin-ai` plugin, which is built into NocoBase — no separate installation required.

The plugin adds three interconnected layers:

**Layer 1 — Intelligence (LLM Services):** Connect to one or more AI model providers. These are the power grid — the raw intelligence that everything else draws from.

**Layer 2 — Agents (AI Employees):** Configure specialised AI agents with defined roles, system prompts, skills, and knowledge access. Nine built-in employees cover the most common business scenarios. Custom employees can be created for specific needs.

**Layer 3 — Integration (Collaboration, Workflows, Knowledge Base):** Wire the employees into your pages (via the AI Floating Ball and Block Actions), into your workflows (via LLM Nodes), and into your document corpus (via the Knowledge Base with RAG retrieval).

This architecture mirrors the smart home precisely:

- The power grid (LLM services) is the energy source
- The appliances (AI Employees) are the useful devices
- The wiring and automation (collaboration + workflows) is what makes them smart

-----

## NocoBase AI Builder vs Standalone AI Tools ⚖️

|Capability                  |Standalone AI (ChatGPT, etc.)|NocoBase AI Builder                    |
|----------------------------|-----------------------------|---------------------------------------|
|Access to your business data|Manual copy-paste            |Direct — employees see your page blocks|
|Multiple specialised agents |Manual switching             |Nine built-in employees + custom roles |
|Embedded in your application|Separate tab / window        |AI Floating Ball inside your app       |
|Workflow automation         |Not possible                 |LLM Nodes in async workflows           |
|Knowledge base retrieval    |Not connected                |RAG search across your documents       |
|Permission control per role |Not possible                 |Role-based AI employee access          |
|MCP tool integration        |Limited                      |Connect any MCP service                |

-----

## The Built-in AI Household Staff: First Look 👥

NocoBase ships nine built-in AI Employees covering the most common business scenarios. Think of them as the default appliance package for a new smart home — you get the basics covered out of the box.

|Employee  |Role                                                      |The device they are like       |
|----------|----------------------------------------------------------|-------------------------------|
|**Atlas** |Coordinator — routes tasks to the right employee          |The smart home hub itself      |
|**Cole**  |NocoBase assistant — product Q&A, doc retrieval           |The home’s instruction terminal|
|**Ellis** |Email expert — writing, summaries, reply suggestions      |The smart communication device |
|**Dex**   |Data organiser — field translation, formatting, extraction|The smart filing assistant     |
|**Viz**   |Insight analyst — trend analysis, KPI interpretation      |The energy monitor / dashboard |
|**Lexi**  |Translation assistant — multilingual communication        |The universal translator       |
|**Vera**  |Research analyst — web search, information aggregation    |The connected research terminal|
|**Dara**  |Data visualisation expert — chart configuration, reports  |The smart display panel        |
|**Orin**  |Data modelling expert — table structure, field suggestions|The blueprint assistant        |
|**Nathan**|Frontend engineer — code snippets, style adjustments      |The smart configuration tool   |

-----

## The Series Map: Eight Episodes 🗺️

|#|Episode                        |Smart home concept            |NocoBase AI Builder feature                |
|-|-------------------------------|------------------------------|-------------------------------------------|
|1|*This one* — The Smart Home Hub|The hub itself                |Overview, metaphor, architecture           |
|2|Connecting to the Power Grid   |Wiring the home to electricity|LLM Service configuration                  |
|3|Your AI Household Staff        |Smart appliances              |AI Employees: built-in + custom            |
|4|The Control Panel              |Remotes and dashboards        |Collaboration: Floating Ball, Block Context|
|5|Teaching Devices New Skills    |Device capability upgrades    |Skills, Tools, MCP Integration             |
|6|Pre-Programmed Routines        |“Good Morning” automation     |Shortcut Tasks                             |
|7|The Home Library               |The document and manual store |AI Knowledge Base + RAG                    |
|8|Automation Rules               |IFTTT / scheduled automations |Workflow LLM Nodes                         |

In **Episode 2**, we wire the home to the grid. LLM Service configuration — connecting NocoBase to OpenAI, Gemini, DeepSeek, or a local Ollama model.

-----

**🔗 Resources**

- **NocoBase GitHub**: [github.com/nocobase/nocobase](https://github.com/nocobase/nocobase)
- **NocoBase AI documentation**: [docs.nocobase.com/ai-employees](https://docs.nocobase.com/ai-employees/)
- **Quick Start**: [docs.nocobase.com/ai-employees/quick-start](https://docs.nocobase.com/ai-employees/quick-start)

-----

*🏠 Smart Home with NocoBase Series — building a fully connected AI-powered business application, one smart device at a time.*
