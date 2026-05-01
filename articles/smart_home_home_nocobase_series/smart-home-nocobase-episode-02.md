---
title: "Smart Home with NocoBase 🏠 Ep.2"
part: 1
published: false
description: "Episode 2: Before any smart device works, the home needs electricity. Before any AI Employee works, NocoBase needs an LLM service. Configure OpenAI, Gemini, Claude, DeepSeek, Qwen, Kimi, or local Ollama models — the power grid that every AI capability in your smart home draws from."
tags: [nocobase, ai, llm, configuration]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/smart_home_with_nocobase_series/smart-home-with-nocobase-episode-02.png"
series: "Smart Home with NocoBase Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 2: Connecting to the Power Grid

> *“Every appliance in your home is useless without electricity. The smarter the appliance, the more precisely you need to configure the circuit.”*

-----

## Before the Devices Come the Cables 🔌

Walk into any new smart home and the first job is not configuring the thermostat or setting up the security camera. The first job is connecting the home to the power grid. Without electricity, every smart device is just an expensive plastic box.

NocoBase AI Builder works the same way. Before any AI Employee can answer a question, analyse data, or draft an email, NocoBase needs a connection to an LLM service — the AI model that provides the intelligence. The LLM service is the power grid. The API key is the meter. The available models are the different voltages your devices can run on.

This episode configures that connection.

-----

## 🗂️ SIPOC — The Power Grid

|**Suppliers**                               |**Inputs**                                      |**Process**                                                        |**Outputs**                                                    |**Customers**                                                 |
|--------------------------------------------|------------------------------------------------|-------------------------------------------------------------------|---------------------------------------------------------------|--------------------------------------------------------------|
|LLM providers (OpenAI, Gemini, Claude, etc.)|Provider selection, API key, base URL, model IDs|System Settings → AI Employees → LLM service → Add New             |A named, tested LLM service available to all AI Employees      |AI Employees — each picks a model from the configured services|
|Network infrastructure                      |Outbound HTTPS to provider APIs                 |NocoBase backend calls the provider API with the stored credentials|Successful responses from the LLM model                        |Workflow LLM Nodes, Knowledge Base embedding, AI Employee chat|
|Optional: Ollama instance (local)           |Ollama URL (localhost or remote host)           |NocoBase connects to Ollama’s OpenAI-compatible API                |Local model inference — no API key, no data leaving the network|Privacy-sensitive or offline deployments                      |

-----

## Supported Providers: Your Choice of Electricity Supplier 🌐

NocoBase AI Builder supports all major LLM providers, plus local model serving via Ollama. Think of each provider as a different electricity supplier — the voltage is slightly different, the pricing differs, but every smart device (AI Employee) in the house works with any of them.

|Provider            |Models available                        |Notes                                                                |
|--------------------|----------------------------------------|---------------------------------------------------------------------|
|**OpenAI**          |GPT-4o, GPT-4.1, o3, etc.               |Two sub-providers: Completions API and Responses API (for web search)|
|**Google Gemini**   |gemini-2.5-pro, gemini-3, etc.          |Recommended: gemini-3                                                |
|**Anthropic Claude**|claude-opus-4-5, claude-sonnet-4-6, etc.|Strong at reasoning and long-context                                 |
|**DeepSeek**        |deepseek-chat, deepseek-reasoner        |Recommended: deepseek-chat. Cost-effective                           |
|**Qwen (Alibaba)**  |qwen3-max, qwen-plus, etc.              |Recommended: qwen3-max                                               |
|**Kimi**            |moonshot-v1-128k, etc.                  |Long-context specialist                                              |
|**Ollama (local)**  |Any model pulled to your Ollama instance|Enterprise edition; no data leaves your network                      |

Recommended starting models for testing: **gemini-3**, **deepseek-chat**, **qwen3-max** — all tested and working well with the built-in AI Employees.

-----

## Step 1: Open LLM Service Management ⚙️

Navigate to:

```
System Settings → AI Employees → LLM service
```

This page shows all configured LLM services, their enabled status, and the drag-reorder control that affects model display order throughout the application.

-----

## Step 2: Add a New Service 🔧

Click **Add New** in the top-right corner of the LLM service list. The creation dialog opens.

### Select Provider

Choose your provider from the dropdown. The form adapts to show the fields required for that provider.

### Configure the Connection

```
Title:    [A memorable name, e.g. "OpenAI Production" or "DeepSeek Chat"]
API Key:  [Your provider API key — kept encrypted in the database]
Base URL: [Optional — required for self-hosted or third-party OpenAI-compatible APIs]
```

**About Base URL:**

- For OpenAI, Gemini, Claude, DeepSeek, Qwen directly: leave blank
- For a third-party OpenAI-compatible endpoint (e.g. Azure OpenAI, LiteLLM proxy): enter the base URL
- For Ollama: enter `http://localhost:11434` (or your Ollama host)

### Configure Enabled Models

Two options:

**Select models:** NocoBase attempts to retrieve the model list from the provider’s API. Choose from the dropdown. This works for most providers.

**Manual input:** If the provider’s model list API does not conform to the standard format, enter the model ID and display name manually. Example: `gpt-4.1-mini | GPT-4.1 Mini`.

-----

## Step 3: Test the Connection 🧪

Before saving, use the **Test flight** button at the bottom of the dialog. NocoBase sends a minimal test request to the provider and reports whether the connection is valid and the model responds.

```
Test result: SUCCESS
  Provider:  OpenAI (Completions)
  Model:     gpt-4.1-mini
  Response:  "Hello! I'm ready to assist."
  Latency:   1.2s
```

If the test fails, check:

- API key is correct and not expired
- Base URL is correct (or blank for direct providers)
- The selected model ID exists on this account
- Outbound HTTPS from your NocoBase server is not blocked

Do not proceed to Episode 3 until at least one service passes the test. Without a working LLM service, no AI Employee can function.

-----

## Step 4: Enable and Order Services 📋

Back on the LLM service list:

**Enable switch:** Toggle each service on or off. Disabled services are invisible to AI Employees and workflow nodes. If you configure a service for testing and want to prevent it being used in production, disable it here.

**Drag to reorder:** The order in the list affects the order models appear in the Model Switcher inside the AI chat panel. Put your preferred default service at the top.

-----

## Connecting Multiple Services: The Multi-Grid Home 🔌

A real smart home often has multiple circuits — one for heavy appliances, one for lighting, one for the garden. NocoBase supports multiple LLM services simultaneously, and different AI Employees can use different services.

Practical configuration examples:

|Use case                                |Service                        |Why                                   |
|----------------------------------------|-------------------------------|--------------------------------------|
|General employee chat (Ellis, Lexi, Dex)|DeepSeek Chat                  |Fast, cost-effective for routine tasks|
|Data analysis (Viz, Orin)               |gemini-3                       |Strong reasoning for complex analysis |
|Long-document processing                |Kimi moonshot-v1-128k          |Handles very long context windows     |
|Knowledge base embedding                |text-embedding-3-small (OpenAI)|Dedicated embedding model for RAG     |
|Privacy-sensitive data                  |Ollama (local)                 |Data never leaves the network         |

-----

## Ollama: The Off-Grid Solar Installation ☀️

For organisations where data privacy is paramount — healthcare, legal, defence — Ollama allows NocoBase AI Builder to run entirely on local infrastructure. No API key. No data sent to any external service. The AI runs inside your network.

```
# On your Ollama host
ollama pull deepseek-r1:7b
ollama pull llama3.2:3b
ollama serve    # starts the API on port 11434
```

In NocoBase:

```
Provider:  Ollama
Title:     Local DeepSeek R1
Base URL:  http://your-ollama-host:11434
Models:    deepseek-r1:7b | DeepSeek R1 7B
```

The Ollama integration uses Ollama’s OpenAI-compatible API, so the same NocoBase configuration interface works without modification.

**Tradeoff vs cloud providers:** Local models are generally less capable than frontier cloud models for complex reasoning tasks. For routine data formatting (Dex), translation (Lexi), and simple Q&A (Cole), a 7B local model is often sufficient. For deep analysis (Viz) and creative writing (Ellis), a frontier cloud model produces noticeably better results.

-----

## The Connection in Context: What Gets Configured Here Powers Everything Else 🔗

Every subsequent episode in this series depends on what you configure here:

- **Episode 3** — Each built-in AI Employee needs a model assigned from this service list
- **Episode 5** — Vera’s web search requires the OpenAI Responses API provider specifically
- **Episode 7** — The Knowledge Base embedding step uses a dedicated embedding model from this list
- **Episode 8** — Workflow LLM Nodes select a service and model from this list per node

The LLM Service configuration is not a one-time setup — it evolves as you add providers, swap models for better ones, or separate responsibilities across services.

-----

## Practical Checklist Before Moving On ✅

```
□ At least one LLM service configured
□ Test flight passed (green) for that service
□ At least one model enabled in the service
□ Service is toggled Enabled in the list
□ (Optional) Second service added for a different use case
□ (Optional) Ollama configured for local/private data scenarios
```

In **Episode 3**, the appliances arrive. Nine built-in AI Employees, their roles, their system prompts, how to enable them and assign a model — and how to create a custom employee for scenarios the built-in team does not cover.

-----

**🔗 Resources**

- **LLM Service docs**: [docs.nocobase.com/ai-employees/features/llm-service](https://docs.nocobase.com/ai-employees/features/llm-service)
- **Ollama**: [ollama.com](https://ollama.com)
- **DeepSeek API**: [platform.deepseek.com](https://platform.deepseek.com)
- **Google AI Studio (Gemini)**: [aistudio.google.com](https://aistudio.google.com)

-----

*🏠 Smart Home with NocoBase Series — building a fully connected AI-powered business application, one smart device at a time.*
