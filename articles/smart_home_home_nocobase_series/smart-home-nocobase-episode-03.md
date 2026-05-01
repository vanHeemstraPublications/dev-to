---
title: "Smart Home with NocoBase 🏠 Ep.3"
part: 2
published: false
description: "Episode 3: The power is on. Now the appliances arrive. NocoBase ships nine built-in AI Employees covering email, data, analysis, research, translation, visualisation, and more. Meet the household staff — enable each device, assign a model, write its instruction manual, and create a custom employee for the tasks only your home requires."
tags: [nocobase, ai, agents, configuration]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/smart_home_with_nocobase_series/smart-home-with-nocobase-episode-03.png”
series: "Smart Home with NocoBase Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 3: Your AI Household Staff

> *“The best smart home is not one with the most devices — it is one where every device knows its job and does it without being asked twice.”*

-----

## The Appliances Arrive 📦

The power grid is live (Episode 2). Now the delivery van arrives with the appliances. In a real smart home, each appliance has a specific purpose — the thermostat handles climate, the security system handles access, the coffee maker handles caffeine. They do not do each other’s jobs.

NocoBase AI Builder ships nine built-in AI Employees, each with a defined role, a personality, and a scope of responsibility. Rather than one generic AI that does everything vaguely, you have a team of specialists that collaborate. When you ask Atlas (the coordinator) to “prepare the quarterly review”, it does not try to do everything itself — it delegates: Viz for the analysis, Ellis for the email draft, Lexi for the French translation.

This episode installs the appliances, writes their instruction manuals, and shows you how to build a custom device for the unique needs of your home.

-----

## 🗂️ SIPOC — The Household Staff

|**Suppliers**                         |**Inputs**                                                                           |**Process**                                                                     |**Outputs**                                                        |**Customers**                                                          |
|--------------------------------------|-------------------------------------------------------------------------------------|--------------------------------------------------------------------------------|-------------------------------------------------------------------|-----------------------------------------------------------------------|
|NocoBase system                       |Built-in employee definitions (Cole, Ellis, Dex, Viz, Lexi, Vera, Dara, Orin, Nathan)|System Settings → AI Employees → Edit each → assign LLM service + model → Enable|Active AI Employee available in the AI chat panel                  |Business users — interact via the AI Floating Ball                     |
|Administrator                         |Custom employee profile: username, nickname, position, system prompt, skills         |New AI Employee creation form                                                   |A specialised AI agent tailored to a specific business role        |Users with access to that employee; specific page blocks it is bound to|
|System prompt (the instruction manual)|Role positioning, task principles, prohibited behaviours, output style               |Stored in the employee’s “About me” / Role Setting tab                          |Consistent, predictable employee behaviour across all conversations|Every conversation with that employee                                  |

-----

## Atlas: The Smart Home Hub Itself 🏠

Before meeting the individual employees, understand **Atlas** — the AI coordinator that most conversations start with.

Atlas is the smart home hub’s own intelligence. When you type a question or command into the AI Floating Ball without specifying which employee to use, Atlas reads the request, decides which employee or combination of employees is best suited, and routes the task accordingly.

You do not configure Atlas the same way as other employees. Atlas is the orchestrator. In most cases, users simply talk to Atlas and the right specialist shows up automatically.

-----

## The Nine Built-In Employees: Your Default Appliance Package 🛠️

### 🖥️ Cole — The Home’s Instruction Terminal

**Role:** NocoBase Assistant — answers questions about the product, retrieves documentation, explains features.

**The device it is like:** The information kiosk built into the home’s main panel. Press it and ask how anything works.

**Best for:** New users learning NocoBase; admin tasks; “how do I configure X?” questions.

**Exclusive scope:** Cole appears in the general chat panel. It is not context-specific to blocks.

-----

### ✉️ Ellis — The Smart Communication Device

**Role:** Email Expert — drafts emails, generates summaries, suggests reply strategies.

**The device it is like:** The smart mail hub that composes, summarises, and prioritises your correspondence.

**Best for:** Writing outreach emails from CRM records, summarising long email threads, generating reply options for customer queries.

**Example prompt:** “Draft a follow-up email to this lead who attended our webinar but has not responded in two weeks.”

-----

### 📋 Dex — The Smart Filing Assistant

**Role:** Data Organiser — translates field values, formats data, extracts structured information from unstructured input.

**The device it is like:** The smart scanner that reads a handwritten note and converts it to a database record.

**Best for:** Translating addresses to a standard format, extracting phone numbers from free-text, filling in missing fields from pasted content.

**Exclusive scope:** Dex appears on form blocks where it can read field structures and call suitable skills to operate on the page.

-----

### 📊 Viz — The Energy Monitor / Dashboard

**Role:** Insight Analyst — analyses data from tables and charts, identifies trends, interprets KPIs, provides actionable recommendations.

**The device it is like:** The whole-home energy monitor that watches your usage patterns and tells you where to cut costs.

**Best for:** Send Viz a chart block and ask “What are the top three trends in this data?”; “Which product category has the lowest margin and why?”; “Compare this month’s leads by source.”

**Example prompt (from docs):** “Please analyse the quantity and quality (high intent ratio) of leads by source, and provide 2–3 channel optimisation suggestions.”

-----

### 🌍 Lexi — The Universal Translator

**Role:** Translation Assistant — multilingual translation, communication assistance.

**The device it is like:** The smart intercom that translates any language at the door in real time.

**Best for:** Translating product descriptions, customer messages, or internal documents into any target language. Maintaining brand voice across language versions.

-----

### 🔍 Vera — The Research Terminal

**Role:** Research Analyst — web search, information aggregation, in-depth research synthesis.

**The device it is like:** The smart research terminal connected to live internet data, not just your home’s library.

**Best for:** “What are the latest developments in [competitor]?”; “Summarise the regulatory changes in [market] from this year”; “Find pricing benchmarks for [product category].”

**Special capability:** Vera has web search enabled (requires the OpenAI Responses API provider — see Episode 5). Other employees work from context you provide; Vera can go and find it.

-----

### 📈 Dara — The Smart Display Panel

**Role:** Data Visualisation Expert — configures chart blocks, generates visual report setups.

**The device it is like:** The smart dashboard on your home’s main wall that assembles the right display for whatever metric you care about today.

**Exclusive scope:** Dara appears only on chart configuration pages. You will not see Dara in the general chat panel.

-----

### 🗃️ Orin — The Blueprint Assistant

**Role:** Data Modelling Expert — assists in designing database table structures, suggests fields, relationships, and data types.

**The device it is like:** The smart blueprint tool that helps you redesign a room layout to fit your furniture optimally.

**Exclusive scope:** Orin appears only on the data configuration page — the collection manager in NocoBase’s admin area.

**Best for:** “I want to build a CRM — what tables and fields do I need?”; “I have a product table and an orders table — what relationships should I define?”

-----

### 💻 Nathan — The Smart Configuration Tool

**Role:** Frontend Engineer — writes frontend code snippets, adjusts styles, fixes JS in code blocks.

**The device it is like:** The smart programmable light switch that takes natural language and converts it to the exact automation script.

**Exclusive scope:** Nathan appears only in the JS Editor within NocoBase’s block configuration.

-----

## Enabling a Built-In Employee: Installing the Appliance 🔧

Built-in employees are pre-defined but not enabled out of the box. You must assign a model and flip the switch:

```
System Settings → AI Employees → [Find the employee, e.g. Viz] → Edit

Model Settings tab:
  LLM Service: [Select from your configured services]
  Model:       [Select a model, e.g. deepseek-chat]

Profile tab:
  Enabled:     [Toggle ON]

→ Submit
```

Repeat for each employee you want to activate. You do not need to enable them all — start with the ones relevant to your current use cases.

-----

## The Instruction Manual: System Prompts and Role Settings 📄

Each AI Employee has an instruction manual — the system prompt that defines its identity, goals, and behavioural boundaries. Built-in employees come with pre-written prompts. You can read and edit them.

Navigate to an employee’s **Role setting** tab to see the system prompt. What it typically contains:

```
You are [Nickname], a [Position] at [organisation].

Your responsibilities:
- [List of specific tasks this employee handles]
- [Response format preferences]

Principles:
- [How to handle edge cases]
- [Prohibited behaviours: do not share credentials, do not make up data]

Tone and style:
- [Professional / friendly / concise / detailed]

You can use these variables:
- {{currentUser}} — the logged-in user's name
- {{currentRole}} — the user's role
- {{currentLanguage}} — the interface language
- {{datetime}} — the current date and time
```

**Variables in system prompts** allow the instruction manual to adapt at runtime. A template that includes `{{currentUser}}` will address the logged-in user by name automatically. A template that includes `{{currentLanguage}}` will respond in the user’s interface language without being asked.

-----

## Creating a Custom Employee: Building Your Own Appliance 🛠️

Built-in employees do not cover every scenario. A legal firm needs a Contract Review specialist. A hospital needs a Medical Coding assistant. An e-commerce company needs a Product Description writer.

### Custom employee creation

```
System Settings → AI Employees → New AI Employee
```

**Profile tab:**

```
Username:         contract-reviewer
Nickname:         Rex
Position:         Contract Review Specialist
Avatar:           [Upload an image or choose from defaults]
Bio:              I review contracts for risk clauses and summarise key terms.
About me (prompt): You are Rex, a contract review specialist. When given a contract
                  document, identify: 1) key parties and obligations, 2) any unusual
                  risk clauses, 3) renewal and termination terms. Respond in structured
                  markdown with clear section headers. Never provide legal advice —
                  flag items for human legal review. Language: {{currentLanguage}}.
Greeting message: Hello! Send me a contract and I will identify the key terms and
                  any clauses worth reviewing carefully.
```

**Role setting tab:**
Configure the detailed system prompt. Use the variables panel to insert `{{currentUser}}`, `{{datetime}}`, and other runtime values.

**Skills tab:**
Assign which tools Rex can use — for example, Knowledge Base retrieval (to search your legal document library) or File reading (to process uploaded PDFs).

**Submit → Edit → Enable → Submit**

The new employee now appears in the AI Floating Ball alongside the built-in team.

-----

## Practical Model Assignment Strategy 💡

Not every employee needs the most expensive model. Match model capability to task complexity:

|Employee|Suggested model       |Reasoning                                                 |
|--------|----------------------|----------------------------------------------------------|
|Cole    |deepseek-chat         |Q&A and documentation retrieval; cost-effective           |
|Ellis   |gemini-3 or qwen3-max |Email quality benefits from stronger writing              |
|Dex     |deepseek-chat         |Structured formatting; speed matters more than creativity |
|Viz     |gemini-3              |Complex analytical reasoning benefits from frontier models|
|Lexi    |qwen3-max             |Excellent multilingual performance                        |
|Vera    |OpenAI (Responses API)|Required for web search capability                        |
|Dara    |deepseek-chat         |Chart configuration is structured; less need for reasoning|
|Orin    |gemini-3              |Data model design benefits from strong reasoning          |
|Nathan  |deepseek-chat         |Code generation; fast iteration valued                    |

-----

In **Episode 4**, the control panels. The AI Floating Ball, Block Action entries, in-chat employee switching, block context — how to actually work with the household staff day to day.

-----

**🔗 Resources**

- **Enable AI Employees**: [docs.nocobase.com/ai-employees/features/enable-ai-employee](https://docs.nocobase.com/ai-employees/features/enable-ai-employee)
- **New AI Employee**: [docs.nocobase.com/ai-employees/features/new-ai-employees](https://docs.nocobase.com/ai-employees/features/new-ai-employees)
- **Built-in Employees**: [docs.nocobase.com/ai-employees/features/built-in-employee](https://docs.nocobase.com/ai-employees/features/built-in-employee)
- **Prompt Engineering Guide**: [docs.nocobase.com/ai-employees/configuration/prompt-engineering-guide](https://docs.nocobase.com/ai-employees/configuration/prompt-engineering-guide)

-----

*🏠 Smart Home with NocoBase Series — building a fully connected AI-powered business application, one smart device at a time.*
