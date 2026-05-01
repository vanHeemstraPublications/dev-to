-----

## title: “Smart Home with NocoBase! Ep.4: The Control Panel”
published: false
description: “Episode 4: The appliances are installed. Now you need the control panels — the ways you interact with your AI household staff. The AI Floating Ball, Block Action entries, Block Context, in-chat employee switching, model selection, and file uploads. Everything a smart home resident needs to work with their AI team.”
tags: [nocobase, ai, collaboration, workflow]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/smart-home-nocobase-episode-04.png”
series: “Smart Home with NocoBase Series”
canonical_url: “”
organization: “the-software-s-journey”

# Smart Home with NocoBase! 🏠

## Episode 4: The Control Panel

> *“The most sophisticated smart home is useless if the control panel is confusing. The interface is the product — not the technology behind it.”*

-----

## Every Device Needs a Remote 🎮

You have connected the power grid (Episode 2) and installed the appliances (Episode 3). But a smart thermostat without a control panel is just a digital thermometer. To actually use your AI household staff, you need the control panels — the interfaces that let you communicate with each employee in the right context.

NocoBase AI Builder provides two entry points and several ways to enrich the conversation. This episode covers all of them.

-----

## 🗂️ SIPOC — The Control Panel

|**Suppliers**             |**Inputs**                                        |**Process**                                                            |**Outputs**                                                            |**Customers**                                                     |
|--------------------------|--------------------------------------------------|-----------------------------------------------------------------------|-----------------------------------------------------------------------|------------------------------------------------------------------|
|Business user             |Natural language request typed in the chat panel  |AI Employee reads request + any attached context → processes → responds|An answer, a draft, an analysis, a formatted record, or an action taken|The user — sees the response in the chat panel                    |
|Block Context (Pick Block)|A selected page block (table, chart, form, kanban)|Block data serialised and attached to the conversation as context      |AI Employee has the actual data from the page — not a description of it|The AI Employee — can make specific, data-grounded decisions      |
|Uploaded file             |PDF, image, spreadsheet, or text file             |File attached to the chat message                                      |AI Employee can read and reason over the file contents                 |Vera (research), Ellis (email from a brief), Dex (data extraction)|
|Model Switcher            |User selects a different model mid-conversation   |Next messages sent to the newly selected model                         |Same employee, different underlying intelligence                       |Useful for switching from a fast cheap model to a more capable one|

-----

## Entry Point 1: The AI Floating Ball 🎱

The AI Floating Ball is the primary control panel. It appears in the **bottom-right corner** of every NocoBase application page. Clicking it opens the AI chat panel.

The AI Floating Ball is the equivalent of a universal smart home remote — it works from any room in the house, and from it you can control any device.

### Opening the chat panel

Click the AI Floating Ball icon in the bottom-right corner of any page. The chat panel slides open on the right side of the screen.

### What the chat panel shows

- **Conversation history** — previous messages with the current employee
- **Employee identity** — the current employee’s avatar, name, and position
- **Greeting message** — the employee’s configured welcome text
- **Message composer** — where you type your request

### Basic operations

The chat panel supports:

- **Sending messages** — type and press Enter
- **Uploading attachments** — click the attachment icon to add files
- **Viewing history** — scroll up to see previous messages
- **Creating new chats** — start a fresh conversation (clears context)
- **Editing system prompts** — advanced override of the employee’s instructions for this session

-----

## Entry Point 2: Block Action Entry 🔲

The second entry point is the **Block Action entry** — an AI Employee bound directly to a specific page block. This is the room-specific control panel, mounted on the wall of one room for that room’s specific devices.

Block Action entries appear as an AI Employee icon in the Actions area of a block (table, form, chart, etc.). Clicking it opens a chat panel that is pre-associated with that block’s data.

When is Block Action better than the Floating Ball?

- When the task is always about the data in that specific block
- When you want to show a pre-configured employee to users rather than Atlas
- When you want to preset shortcut tasks for that block (Episode 6)

-----

## Selecting the Right Employee: The Room Selector 🏠

Within the chat panel (both entry points), you can switch between AI Employees via the **employee dropdown** in the message composer area.

```
[Employee avatar] [Employee name ▼] | [Model name ▼]

Click employee name → dropdown shows all enabled employees
Select the one you want → next message goes to that employee
```

In most cases, you can start with Atlas and let it delegate. But if you know you need Viz specifically, select Viz directly and skip the routing step.

**Model preferences are saved per employee.** If you switch Viz to gemini-3 during a session, the next time you open the chat with Viz, it will still be on gemini-3. You do not need to reconfigure every time.

-----

## The Model Switcher: Changing the Engine Mid-Drive 🚗

Next to the employee dropdown is the **Model Switcher**. This lets you change which underlying LLM model handles the current conversation, without changing which employee you are talking to.

Practical use cases:

- Start with deepseek-chat (fast, cheap) for initial exploration
- Switch to gemini-3 (more capable) when the response quality is not sufficient
- Switch to a local Ollama model when the content becomes sensitive

The Model Switcher also provides a shortcut to add a new LLM service if none are configured — useful during initial setup.

-----

## Adding Context: The Room Sensors 📡

A smart thermostat is useful. A smart thermostat that knows the current temperature in every room is better. Context transforms a generic AI into one that can reason about your specific situation.

NocoBase provides two context mechanisms: Block Context and File uploads.

### Block Context — Pick Block

The most powerful context mechanism. Rather than describing your data to the AI, you show it the data directly.

**How to use:**

1. Open the AI chat panel
1. Click the **“Add work context”** button in the lower left corner of the composer
1. Select **“Pick Block”**
1. The page enters block selection mode — blocks you can share turn highlighted as you hover
1. Click the block you want to send
1. The block data is attached to the composer (you can see it as a preview chip)
1. Type your message and send — the AI receives both your question and the block data

**What Block Context includes:**

- For table blocks: the visible records (with current filter/sort applied)
- For form blocks: the current field structure and values
- For chart blocks: the chart configuration and data
- For kanban blocks: the visible columns and cards

**Example:** You are on the Leads page, looking at a filtered table showing 47 leads from the trade show last month. You open Viz via the Floating Ball, send the leads table as Block Context, and ask: “Which lead segments have the highest conversion potential, and what follow-up actions do you recommend?” Viz analyses the actual data — not a hypothetical.

### Ending Block Selection Without Sending

If you enter block selection mode but change your mind, click the **Stop** icon at the bottom of the screen to exit without selecting any block.

-----

## Uploading Files: Adding the Document Pile 📄

Beyond live page data, you can upload static documents as context:

- **PDFs** — contracts, reports, research papers
- **Images** — screenshots, product photos (multimodal-capable employees)
- **Spreadsheets** — Excel or CSV data for analysis
- **Text files** — plain text documents

Click the **attachment / file upload icon** in the message composer and select your file. The file is attached to the next message you send.

**Employee-specific file use cases:**

|Employee    |File type          |What to ask                                                   |
|------------|-------------------|--------------------------------------------------------------|
|Vera        |PDF research paper |“Summarise the key findings and implications for our industry”|
|Ellis       |Word document brief|“Draft a sales email based on this product brief”             |
|Dex         |CSV export         |“Clean and reformat this data into our standard fields”       |
|Rex (custom)|PDF contract       |“Identify the termination clause and any unusual risk items”  |

-----

## AI Employees That Know the Page Structure Automatically 🤖

Some employees are context-aware by design — they read the page structure automatically without you needing to pick a block manually.

**Dex** on a form block reads the form’s field structure automatically. It knows which fields exist, their types, and which are empty. You can ask it to “fill in the missing address fields from the notes text” and it understands which fields to target.

This auto-context is an extension of the Block Action entry model — when the employee is bound to a specific block, it already has that block’s structure as background knowledge.

-----

## A Practical Day-in-the-Life Workflow 📅

Here is a complete example of how a sales manager might use the control panels in a typical morning:

```
9:00 — Open NocoBase CRM
  → AI Floating Ball opens (Atlas)
  → "Good morning! Which leads should I prioritise today?"
  → Atlas delegates to Viz with the leads table as context
  → Viz: "Based on last week's activity, focus on [3 companies] — 
          they have high engagement but no meeting scheduled."

9:15 — Open the Leads table, filter to those 3 companies
  → Click Block Action entry on the leads table
  → [Ellis is bound to this block for email tasks]
  → Select task: "Write follow-up email" (Shortcut Task — Episode 6)
  → Ellis drafts a personalised follow-up for each lead

9:30 — One lead responded in French
  → Open the email, pick the email block as context
  → Switch to Lexi in the chat panel
  → "Translate this into English and draft a reply"
  → Lexi translates + drafts the reply

10:00 — Weekly pipeline review meeting preparation
  → Open the Opportunities chart
  → Send chart as Block Context to Viz
  → "What should I highlight in my 10-minute pipeline review?"
  → Viz generates talking points with specific numbers from the chart
```

Every interaction happens inside NocoBase. No switching to a browser tab. No copy-pasting data into a separate AI tool. The control panel is embedded in the workflow.

-----

In **Episode 5**, we upgrade the devices. Skills, Tools, MCP Integration, and Vera’s web search — how to extend what each employee can do beyond conversation alone.

-----

**🔗 Resources**

- **Collaborate with AI Employees**: [docs.nocobase.com/ai-employees/features/collaborate](https://docs.nocobase.com/ai-employees/features/collaborate)
- **Add Context - Blocks**: [docs.nocobase.com/ai-employees/features/pick-block](https://docs.nocobase.com/ai-employees/features/pick-block)
- **File Management**: [docs.nocobase.com/ai-employees/file-manager](https://docs.nocobase.com/ai-employees/file-manager)
- **Quick Start**: [docs.nocobase.com/ai-employees/quick-start](https://docs.nocobase.com/ai-employees/quick-start)

-----

*🏠 Smart Home with NocoBase Series — building a fully connected AI-powered business application, one smart device at a time.*
