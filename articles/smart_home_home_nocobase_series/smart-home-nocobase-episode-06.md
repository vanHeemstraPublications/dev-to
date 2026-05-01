---
title: "Smart Home with NocoBase 🏠 Ep.6"
part: 6
published: false
description: "Episode 6: The best smart home routines are the ones you only configure once. Shortcut Tasks let you bind AI Employees to specific blocks, preset the context and instructions, and launch them with a single click — no typing required. The ‘Good Morning’ routine for your AI team."
tags: [nocobase, ai, automation, productivity]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/smart_home_with_nocobase_series/smart-home-with-nocobase-episode-06.png"
series: "Smart Home with NocoBase Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 6: Pre-Programmed Routines

> *“The smart home routine you use every morning took twenty minutes to set up once and saves thirty seconds every day for the rest of your life. That is still a net positive within a week.”*

-----

## The Good Morning Routine 🌅

Every well-configured smart home has a “Good Morning” routine. Press one button and the blinds open, the thermostat warms up, the coffee maker starts, and the morning news plays on the kitchen speaker. Nobody configures this from scratch every morning. It was set up once, saved as a routine, and now runs with a single tap.

**Shortcut Tasks** are the NocoBase AI Builder equivalent. Instead of every user opening the chat panel, selecting an employee, picking a block, and typing the same request they type every Tuesday, you configure the task once: bind the employee, preset the context, write the background prompt, and save it. Users see a one-click button in the block’s Actions area.

This episode builds those routines.

-----

## 🗂️ SIPOC — Pre-Programmed Routines

|**Suppliers**                     |**Inputs**                                                                                      |**Process**                                                                                               |**Outputs**                                                          |**Customers**                                                      |
|----------------------------------|------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|-------------------------------------------------------------------|
|Administrator (routine programmer)|Task title, background prompt, default user message, work context selection, skills/tools config|UI editing mode → block Actions → AI Employees → bind employee → Edit tasks                               |A configured Shortcut Task visible as a one-click action in the block|Business users — click once to start a pre-built AI workflow       |
|Business user                     |One click on a Shortcut Task                                                                    |NocoBase loads task config → opens chat panel → sends background + default message → AI employee processes|An immediate AI response without manual setup                        |The user gets the result faster, with less friction                |
|The block the task is bound to    |Live block data (table, form, chart)                                                            |Work context setting in the task sends block data automatically                                           |AI Employee has live page data as context without user action        |The analysis, draft, or extraction is about the actual current data|

-----

## Two Concepts: Block Binding and Task Configuration 🔧

Shortcut Tasks require two separate configuration steps:

**Step 1 — Block Binding:** Associate a specific AI Employee with a specific block. This installs the “control panel” for that block.

**Step 2 — Task Configuration:** Define the specific tasks (routines) that employee will have available from that block.

-----

## Step 1: Bind an Employee to a Block 🔗

```
1. Enter UI editing mode (toggle in the top menu)
2. Navigate to the block you want to bind (e.g. the Leads table)
3. In the block's Actions area, find "Actions" or the "+" button
4. Select "AI employees" from the Actions menu
5. Choose the AI Employee to bind (e.g. Ellis)
6. Exit editing mode
```

After binding, each time a user loads this page, the bound employee’s icon appears in the block’s Actions area. Clicking it opens the chat panel pre-associated with that employee and that block.

You can bind different employees to different blocks on the same page:

- Leads table → Ellis (email drafting)
- Opportunities chart → Viz (pipeline analysis)
- Product form → Dex (data formatting)

-----

## Step 2: Configure Shortcut Tasks 📋

With an employee bound to a block, configure the tasks available from it:

```
1. Enter UI editing mode
2. Hover over the bound employee icon on the block
3. A menu button appears — click it
4. Select "Edit tasks"
5. Task settings page opens
```

The task settings page shows tabs — each tab is an independent task. Click “+” to add a new task.

### Task Settings Form

**Title** — the name displayed in the task list (the button label users see):

```
"Analyse Pipeline Trends"
"Draft Follow-Up Email"
"Generate Weekly Summary"
```

**Background** — the system prompt injected before the conversation starts. This defines what the employee should do in this specific context:

```
You are analysing the current pipeline data for this sales team.
Focus on:
- Overall conversion rate compared to last month
- Which stages have the most bottleneck (longest dwell time)
- Top three accounts by deal value and their current stage
Respond in clear sections with specific percentages and account names.
```

**Default user message** — the message pre-filled in the chat input box when the user activates the task:

```
"Please analyse the current pipeline and identify the top three priorities for this week."
```

**Work context** — the block data to send automatically as context:

```
Work context: [Select the Opportunities table block]
```

This replaces the manual Pick Block step. The task automatically attaches the block data without the user needing to select it.

**Skills** — which skills the employee should use for this task:

```
Preset:   Use the employee's default skills
Custom:   Select specific skills for this task only
[empty]:  No skills for this task
```

**Tools** — which tools to enable:

```
Preset / Custom / [empty] — same logic as skills
```

**Send default user message automatically** — toggle:

```
ON:  Task auto-fires when selected — no user confirmation needed
OFF: Task loads the default message into the input but waits for user to send
```

-----

## The Task List: Buttons in the Block 🎛️

After configuring tasks, they appear in the AI Employee’s interface in two places:

1. **In the AI Employee profile popover** (when hovering the bound employee icon)
1. **In the greeting message** when the chat opens

Users see a labelled button for each task. Click the task → the background prompt activates → if auto-send is on, the task fires immediately → the employee responds.

```
[Viz icon] Opportunities Pipeline
  Shortcut tasks:
  ┌─────────────────────────────┐
  │ 📊 Analyse Pipeline Trends  │ ← one click
  │ 📋 Generate Board Report    │ ← one click
  │ 🔮 Forecast Q3 Close        │ ← one click
  └─────────────────────────────┘
```

-----

## Practical Examples: Building Your Morning Routine Package 🏠

### Routine 1: Daily Lead Review (Leads table → Ellis)

```
Title:                  "Prioritise Today's Leads"
Background:             You are a sales assistant reviewing today's incoming leads.
                        Identify the top 5 leads by engagement score and company size.
                        For each, suggest a personalised opening line for an email.
Default user message:   "Which leads should I focus on first today?"
Work context:           [Leads table block, filtered to "Status = New, Today"]
Auto-send:              ON
```

User opens the CRM, clicks the Ellis icon on the Leads table, selects “Prioritise Today’s Leads” — and within seconds has a prioritised list with personalised email openers, without typing a word.

### Routine 2: Weekly Pipeline Report (Pipeline chart → Viz)

```
Title:                  "Generate Weekly Board Report"
Background:             You are generating the weekly pipeline report for the board.
                        Structure your response as:
                        1. Pipeline summary (total value, deals by stage)
                        2. Movement since last week (new deals added, deals closed)
                        3. Risk flags (deals stalled >30 days, high value at risk)
                        4. Recommended actions (max 3 bullet points)
                        Use specific numbers from the data. Keep the tone executive-level.
Default user message:   "Generate this week's pipeline report."
Work context:           [Pipeline chart block]
Auto-send:              ON
```

### Routine 3: Product Description Generator (Product form → Ellis)

```
Title:                  "Write Product Description"
Background:             You are writing marketing copy for a product.
                        Using the product name, category, and key specifications
                        provided, write three versions:
                        1. One sentence (for search results)
                        2. One paragraph (for product pages)
                        3. Five bullet points (for comparison tables)
                        Tone: professional but approachable. No superlatives.
Default user message:   "Write a product description based on this product record."
Work context:           [Product details form block]
Skills:                 [empty — no knowledge base needed]
Auto-send:              OFF ← user reviews defaults before sending
```

### Routine 4: Support Ticket Triage (Support tickets table → Viz)

```
Title:                  "Triage and Categorise Tickets"
Background:             You are a support operations analyst. Review the open tickets
                        shown. For each ticket: assign a priority (P1/P2/P3),
                        suggest a category (Bug/Feature/Question/Billing),
                        and estimate resolution complexity (Simple/Medium/Complex).
                        Output as a markdown table.
Default user message:   "Categorise and triage the current open tickets."
Work context:           [Support tickets table block, filtered to open status]
Auto-send:              ON
```

-----

## Multiple Tasks per Block: The Routine Library 📚

A single block can have multiple Shortcut Tasks — a routine library. Think of the block’s AI employee icon as a mini-remote with multiple preprogrammed buttons.

The Opportunities pipeline chart bound to Viz might have:

- “Analyse Pipeline Trends” — tactical review
- “Generate Board Report” — executive summary
- “Forecast Q3 Close” — projections
- “Risk Assessment” — identify at-risk deals
- “Compare to Last Quarter” — historical comparison

Each task has different background prompts, different levels of auto-send, and may send different context blocks.

-----

## The Efficiency Calculation 💡

A typical AI interaction without Shortcut Tasks:

1. Open chat panel (5 seconds)
1. Switch to Viz (5 seconds)
1. Click “Add work context” (3 seconds)
1. Select Pick Block, hover and click the chart (10 seconds)
1. Type the analysis request (30 seconds)
1. Send

**Total: ~53 seconds of user action**

With a Shortcut Task (auto-send = ON):

1. Click the Viz icon on the chart block (3 seconds)
1. Click “Analyse Pipeline Trends” (2 seconds)

**Total: ~5 seconds of user action**

Multiply by 20 analysts doing this 3 times per week for 52 weeks. Shortcut Tasks are worth configuring.

-----

In **Episode 7**, we stock the home library. AI Knowledge Base — vector databases, vector stores, the RAG pipeline, and how to make AI Employees knowledgeable about your specific documents and policies.

-----

**🔗 Resources**

- **Shortcut Tasks**: [docs.nocobase.com/ai-employees/features/task](https://docs.nocobase.com/ai-employees/features/task)
- **Collaborate with AI Employees**: [docs.nocobase.com/ai-employees/features/collaborate](https://docs.nocobase.com/ai-employees/features/collaborate)

-----

*🏠 Smart Home with NocoBase Series — building a fully connected AI-powered business application, one smart device at a time.*
