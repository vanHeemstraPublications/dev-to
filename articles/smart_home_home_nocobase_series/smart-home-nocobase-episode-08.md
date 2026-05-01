---
title: "Smart Home with NocoBase 🏠 Ep.8"
part: 8
published: false
description: "Episode 8: The most powerful smart home feature is not what you control manually — it is what runs automatically. Workflow LLM Nodes embed AI intelligence directly into NocoBase’s workflow engine. Text chat, multimodal analysis, structured data extraction, and AI Employee approval nodes for human-in-the-loop processes."
tags: [nocobase, ai, workflow, automation]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/smart_home_with_nocobase_series/smart-home-with-nocobase-episode-08.png"
series: "Smart Home with NocoBase Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 8: Automation Rules

> *“The most sophisticated smart home action is the one that happens without anyone pressing a button. The motion sensor triggers the light. The calendar triggers the heating. The delivery alert triggers the unlock. AI is the next layer of that same automation stack.”*

-----

## Beyond the Chat Panel 🤖

Every episode so far has described AI Employees as collaborative partners you interact with through a chat interface. That is one half of the picture. The other half is **automation** — AI intelligence embedded in workflows that run without human initiation.

A smart home does not just respond to commands. It anticipates patterns, monitors conditions, and takes actions on a schedule or in response to events. NocoBase AI Builder’s **Workflow LLM Nodes** bring the same capability to your business processes: AI that analyses data when a record is created, extracts structured information from uploaded documents, generates reports on a schedule, and routes approvals based on AI-assessed risk level.

This episode wires up the automation rules.

-----

## 🗂️ SIPOC — Automation Rules

|**Suppliers**               |**Inputs**                                               |**Process**                                                                       |**Outputs**                                                       |**Customers**                                                                   |
|----------------------------|---------------------------------------------------------|----------------------------------------------------------------------------------|------------------------------------------------------------------|--------------------------------------------------------------------------------|
|Workflow trigger event      |Record created, form submitted, scheduled timer, API call|NocoBase workflow engine starts the automation chain                              |Workflow context available to all subsequent nodes                |LLM Node — receives workflow context as variable inputs                         |
|LLM Node (Text Chat)        |System prompt + user prompt with workflow variables      |Async call to configured LLM service and model                                    |Response text stored as a workflow variable                       |Next workflow nodes — can use the AI’s response as an input                     |
|LLM Node (Structured Output)|Prompt requesting JSON response with defined schema      |LLM returns JSON; NocoBase validates against schema                               |Structured data object — individual fields accessible as variables|Downstream nodes — create records, send notifications with specific field values|
|AI Employee Node            |Task description + workflow context                      |AI Employee processes the task; if approval required, waits for human confirmation|Completed task result; approval decision                          |Workflow continues or branches based on approval outcome                        |

-----

## Why Workflow LLM Nodes Exist: The Automation Case 🔄

Compare these two approaches to the same task — generating a lead score when a new lead is submitted:

**Chat-based approach:**

1. Sales rep notices a new lead
1. Opens chat panel
1. Picks Viz
1. Sends the lead record as context
1. Asks for a lead score
1. Copies the score into the lead record
1. Manually triggers follow-up tasks

**Workflow-based approach:**

1. Lead is submitted
1. Workflow triggers automatically
1. LLM Node receives lead data as variables
1. AI scores the lead and returns structured JSON: `{"score": 85, "priority": "High", "reason": "..."}`
1. Workflow updates the lead record with the score
1. Workflow branches: High priority → notify sales manager; Medium → add to weekly review queue
1. Done, without human intervention

Workflow LLM Nodes are for tasks that should happen automatically, consistently, at scale — not just when someone remembers to ask.

-----

## Important: LLM Nodes Are Asynchronous ⚡

LLM calls are time-consuming (seconds to tens of seconds). For this reason, **LLM Nodes can only be used in asynchronous workflows** in NocoBase.

Synchronous workflows (request-response) cannot include LLM Nodes because the browser or API client cannot wait. Asynchronous workflows run in the background — the triggering event completes immediately, and the workflow executes in a background queue.

This is the equivalent of a smart home routine that runs in the background — the motion sensor fires instantly, but the “prepare the guest room” routine (heating, lighting, coffee maker) runs over the next few minutes without blocking anything.

-----

## Node Type 1: Text Chat — The Conversational Automation 💬

The **Text Chat LLM Node** initiates a single conversation exchange with an LLM service and stores the response as a workflow variable.

### Creating a Text Chat Node

```
In a NocoBase workflow → Add Node → LLM → Text Chat

Configuration:
  LLM Service:     [Select from configured services]
  Model:           [Select model]
  Temperature:     0.7 (creativity; lower for more consistent outputs)
  Max tokens:      1000
  Response format: Text
```

### Configuring Messages

The node supports three message types, matching the LLM standard:

```
System message:
  "You are a lead scoring specialist. Analyse the lead data provided and 
   assign a score from 0-100 based on: company size, industry fit, 
   engagement level, and expressed intent. Return only the score as a 
   number followed by a one-sentence justification."

User message:
  "Lead data:
   Company: {{leadRecord.company}}
   Industry: {{leadRecord.industry}}
   Company size: {{leadRecord.employees}}
   Source: {{leadRecord.source}}
   Form responses: {{leadRecord.formNotes}}"
```

**Variables in messages** — the `{{variable}}` syntax references workflow context values. The lead record fields become part of the prompt automatically. This is how the workflow makes each AI interaction data-specific.

### Using the Response

The node’s response is stored as a variable accessible to downstream nodes:

```
Node output variable: textChatNode.content

Use in subsequent nodes:
  Update lead record: Score field = {{textChatNode.content}}
  Send notification: "New lead scored: {{textChatNode.content}}"
  Condition branch: if score > 80 → notify manager
```

-----

## Node Type 2: Multimodal Chat — When Data Has Images 🖼️

The **Multimodal Chat LLM Node** supports sending images, PDFs, and other non-text content to LLMs that support multimodal input.

**Use cases:**

- Analyse a product photo submitted with a warranty claim
- Extract data from a scanned invoice image
- Classify a document image by type before processing
- Describe a chart image for accessibility

### Configuration

```
LLM Service:    [Must be a multimodal-capable provider: GPT-4o, Gemini, Claude]
Model:          [gpt-4o, gemini-2.0-flash, claude-opus-4-5, etc.]

Messages:
  System:   "You are an invoice data extractor. Extract: vendor name, invoice
             number, total amount, line items, and due date."
  
  User:     Multiple content items:
              1. Text: "Extract the invoice data from this image."
              2. Image: {{uploadedFile.url}}   ← workflow variable
```

The node returns a text response (or JSON if you instruct it to format as JSON) that downstream nodes can use to populate database fields.

-----

## Node Type 3: Structured Output — Clean Data From AI 📋

The **Structured Output LLM Node** is the most powerful for database integration. It instructs the LLM to return a specific JSON schema, which NocoBase validates and makes available as individual typed variables.

### Why Structured Output Matters

Without structured output, the AI might respond: “The invoice total is $4,250.00, due on March 31st, from Acme Corp.”

With structured output, the response is:

```json
{
  "vendor_name": "Acme Corp",
  "invoice_number": "INV-2026-0892",
  "total_amount": 4250.00,
  "currency": "USD",
  "due_date": "2026-03-31",
  "line_items": [
    { "description": "Consulting", "amount": 3000.00 },
    { "description": "Travel", "amount": 1250.00 }
  ]
}
```

Every field is individually accessible in downstream workflow nodes, ready to write directly to database columns.

### Configuration

```
Response format: JSON

JSON Schema:
{
  "type": "object",
  "properties": {
    "vendor_name":    { "type": "string" },
    "invoice_number": { "type": "string" },
    "total_amount":   { "type": "number" },
    "currency":       { "type": "string", "enum": ["USD","EUR","GBP"] },
    "due_date":       { "type": "string", "format": "date" }
  },
  "required": ["vendor_name", "invoice_number", "total_amount", "due_date"]
}
```

The node validates the LLM’s response against the schema before passing it downstream. If the LLM fails to return valid JSON matching the schema, the node retries or logs an error for review.

-----

## Node Type 4: AI Employee Nodes — Human in the Loop 👥

The **AI Employee Node** runs a specific AI Employee as a workflow step, with the option to require human approval before the employee’s action takes effect.

This is the home automation equivalent of a routine that pauses and says “Are you sure?” before locking all the doors and arming the security system.

### AI Employee Node — Configuration

```
Add Node → AI Employees → [Select employee, e.g. Ellis]

Task configuration:
  Background:     "Draft a contract amendment proposal based on the negotiation
                   notes provided. Include: changed clauses, rationale for each
                   change, and any risk flags for legal review."
  
  Input:          {{negotiationRecord.notes}}
                  {{existingContract.text}}

Output variable:  employeeNode.response
```

### Approval Mode

Toggle **“Require approval before proceeding”**:

```
When ON:
  1. Employee drafts the output
  2. Workflow pauses — approval task appears in the assigned approver's task list
  3. Approver reviews the draft: Approve / Reject / Edit
  4. If Approved → workflow continues with the draft output
  5. If Rejected → workflow branches to rejection handling

When OFF:
  Employee output used directly in subsequent nodes without human review
```

Approval mode is essential for high-stakes automations: sending mass emails, modifying contract terms, deleting records, posting to external systems.

-----

## Building Complete Automation Workflows: Three Examples 🏠

### Automation 1: New Lead Intelligence Pipeline

**Trigger:** Lead record created

```
Trigger: Record created in Leads collection
    │
    ▼
Text Chat Node — Lead Scoring
  System: "Score this lead 0-100 based on ICP fit."
  User:   "{{lead.company}}, {{lead.employees}}, {{lead.source}}, {{lead.notes}}"
  Output: leadScore.content
    │
    ▼
Structured Output Node — Extract Score and Reason
  Schema: { "score": number, "priority": string, "reason": string }
  Output: structuredScore.data
    │
    ▼
Update Record — Write back to Lead
  Lead.score    = {{structuredScore.data.score}}
  Lead.priority = {{structuredScore.data.priority}}
  Lead.ai_notes = {{structuredScore.data.reason}}
    │
    ▼
Condition Branch
  If score >= 80 → Notification to sales manager
  If score 50-79 → Add to weekly review queue
  If score < 50  → No action
```

### Automation 2: Invoice Processing

**Trigger:** File uploaded to the Invoice Submissions collection

```
Trigger: File uploaded (Invoice Submissions)
    │
    ▼
Multimodal Chat Node — Extract Invoice Data
  Model:  gemini-2.0-flash (multimodal)
  Image:  {{submission.fileUrl}}
  Prompt: "Extract all invoice fields. Return JSON."
  Output: extractedData
    │
    ▼
Structured Output Node — Validate Schema
  Schema: InvoiceSchema (vendor, number, total, date, line_items)
  Output: invoice.data
    │
    ▼
Create Record — Invoice in Accounts Payable collection
  All fields from invoice.data
    │
    ▼
AI Employee Node (Ellis) — Draft AP Email
  Task: "Draft a confirmation email to the vendor that invoice
         {{invoice.data.invoice_number}} has been received and
         is being processed."
  Approval: Required (AP manager approves before send)
```

### Automation 3: Weekly Performance Report

**Trigger:** Scheduled — every Monday at 8:00 AM

```
Trigger: Schedule (Monday 8:00 AM)
    │
    ▼
Query Node — Fetch last week's KPIs from database
  Output: kpiData (revenue, deals closed, leads, conversion rate)
    │
    ▼
Text Chat Node (Viz) — Generate Report
  System: "You are generating the Monday morning performance report.
           Be specific, use the numbers provided, keep under 300 words."
  User:   "Last week's data: {{kpiData}}"
  Output: reportContent
    │
    ▼
AI Employee Node (Ellis) — Format as Email
  Task: "Format this performance data as a professional email to the
         leadership team. Subject line: 'Weekly Performance — [date]'."
  Input: {{reportContent}}
  Approval: Required (manager reviews before send)
    │
    ▼
Send Email — leadership team distribution list
```

-----

## The Complete Smart Home: All Eight Layers Working Together 🏠

Looking back across the series, the smart home is now fully built:

|Episode|Layer                  |What it does                                           |
|-------|-----------------------|-------------------------------------------------------|
|1      |The hub                |NocoBase as the AI application platform                |
|2      |The power grid         |LLM Services: OpenAI, Gemini, DeepSeek, Ollama         |
|3      |The appliances         |Nine built-in AI Employees + custom employees          |
|4      |The control panel      |AI Floating Ball, Block Context, employee switching    |
|5      |Skill upgrades         |Skills, Tools, MCP Integration, web search, permissions|
|6      |Pre-programmed routines|Shortcut Tasks: one-click AI workflows per block       |
|7      |The home library       |AI Knowledge Base, RAG, vector search                  |
|8      |*This one* — Automation|Workflow LLM Nodes: scheduled and event-driven AI      |

**The full picture:** An AI request can start from a user clicking a Shortcut Task (Episode 6), which triggers an employee that searches the Knowledge Base (Episode 7), uses an MCP tool to look up an external system (Episode 5), and feeds the result into a Workflow that sends an email and logs the action (Episode 8). Every layer connects to every other layer.

-----

## Getting Started: The Recommended Build Order 🛠️

If you are building from scratch, this order minimises configuration backtracking:

```
1. Install NocoBase with plugin-ai enabled
2. Configure at least one LLM Service (Episode 2)
3. Enable three built-in employees: Cole, Ellis, Viz (Episode 3)
4. Test basic chat collaboration (Episode 4)
5. Add the Knowledge Base for your core documents (Episode 7)
   — This unlocks Cole and Viz significantly
6. Configure Shortcut Tasks for your most frequent workflows (Episode 6)
7. Add MCP services as needed (Episode 5)
8. Build automation workflows for high-volume repetitive tasks (Episode 8)
```

-----

**🔗 Resources**

- **Workflow LLM Nodes**: [docs.nocobase.com/ai-employees/workflow/nodes/llm/chat](https://docs.nocobase.com/ai-employees/workflow/nodes/llm/chat)
- **Structured Output**: [docs.nocobase.com/ai-employees/workflow/nodes/llm/structured-output](https://docs.nocobase.com/ai-employees/workflow/nodes/llm/structured-output)
- **AI Employee Nodes**: [docs.nocobase.com/ai-employees/workflow/nodes/employee/configuration](https://docs.nocobase.com/ai-employees/workflow/nodes/employee/configuration)
- **Node Approval**: [docs.nocobase.com/ai-employees/workflow/nodes/employee/approval](https://docs.nocobase.com/ai-employees/workflow/nodes/employee/approval)
- **NocoBase GitHub**: [github.com/nocobase/nocobase](https://github.com/nocobase/nocobase)

-----

*🏠 Smart Home with NocoBase Series — a fully connected AI-powered business application, built one smart device at a time. The home is complete.*
