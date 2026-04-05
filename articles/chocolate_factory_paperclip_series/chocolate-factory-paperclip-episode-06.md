---
title: "Charlie's Chocolate Factory Paperclip — Ep.6"
part: 6
published: false
description: ""
tags: [paperclip]
series: "Chocolate Factory Paperclip Series"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/chocolate_factory_paperclip_series/chcolate-factory-paperclip-episode-06.png"
canonical_url: ""
organization: "the-software-s-journey"
---

# 📖 The Secret Recipe Book (Skills & Runtime Injection)

> *"A little nonsense now and then is relished by the wisest men."*
> — Willy Wonka.
> *"A little SKILL.md now and then is loaded by the wisest agents."*
> — Paperclip, at runtime.

---

## 📜 The Recipe That Lives in Every Worker's Head

The Oompa Loompas did not arrive in the factory already knowing how to make Wonka's chocolate. They learned the recipes. The precise proportions. The exact temperatures. The sequence of steps that turned raw materials into the extraordinary products rolling off the production line.

In Paperclip, **Skills** are the recipes. They are structured instruction files — Markdown documents — that Paperclip injects into an agent's context at the start of each heartbeat run. They teach the agent:

- How to follow Paperclip's heartbeat protocol
- How to check out tasks and post progress comments
- When to escalate and how to do it properly
- What conventions your project uses (code style, naming, review criteria)
- What context your company operates in (domain knowledge, customer segments, technical stack)

The critical insight: **this is runtime injection, not retraining**. You do not fine-tune the model. You do not modify the agent's weights. You write a Markdown file, put it in the right place, and the agent reads it the next time it wakes up. The recipe is in the worker's hand, not encoded into their neurons.

---

## 📋 SIPOC — Teaching the Workers

| **Suppliers** | **Inputs** | **Process** | **Outputs** | **Customers** |
|---|---|---|---|---|
| You (author of SKILL.md) | Markdown files describing workflows, conventions, context | Paperclip injects skill files into agent context at heartbeat start | Agent that knows your project's protocols without retraining | Every heartbeat run — consistently informed agents |
| Paperclip skill injection system | Agent adapter configuration (which skills to load) | Skills directory scanned → relevant files selected → injected | Context-rich execution — agents make better decisions | Your output quality — fewer wrong turns, fewer escalations |
| Your project's conventions | Domain knowledge, code standards, business rules | Agent reads skills → applies them during task execution | Consistent behavior across all agents of the same type | Your review process — less correction work |
| The Paperclip-native SKILL.md | Heartbeat protocol documentation | Auto-installed during `paperclipai onboard` | Agents that understand Paperclip's task lifecycle from day one | The issue board — properly formatted comments and status updates |

---

## 📂 Where Skills Live

Skills are Markdown files placed in specific directories that Paperclip knows to look in. The location depends on the adapter:

| Adapter | Skills directory |
|---|---|
| `claude_code` | `~/.claude/skills/` |
| `codex` | Managed environment (Paperclip handles injection) |
| `cursor` | `.cursor/skills/` in the workspace |
| `openclaw` | `~/.openclaw/skills/` |
| `gemini_cli` | `~/.gemini/` |

During `paperclipai onboard`, Paperclip automatically installs its own **Paperclip-native skill** into the appropriate directory. This skill teaches the agent:
- How to check the Paperclip API for task assignments
- How to check out a task (preventing other agents from taking it simultaneously)
- How to post structured progress comments
- How to mark issues done, blocked, or escalated
- How to handle budget warnings

Every agent that runs on a properly onboarded machine already knows the factory's protocols from day one.

---

## ✍️ Writing Your Own Skills

The power of the skills system is that you extend it. You are not limited to Paperclip's built-in protocols. You write skills for your specific project, your specific conventions, your specific domain.

### Anatomy of a SKILL.md

A skill file is a Markdown document. There is no required schema — just clear, structured prose that an LLM can read and apply. The convention is to use a SKILL.md filename and organise it with headers.

Here is an example skill for a software engineering team:

```markdown
# Engineering Standards — SKILL.md

## Your Role
You are a senior software engineer working on the Paperclip platform.
Your primary stack is TypeScript, Node.js, Express, and React.

## Code Standards
- Use TypeScript strictly. No `any` unless explicitly justified.
- All functions must have JSDoc comments for public APIs.
- Tests are required for all new functionality (vitest).
- PRs must not exceed 400 lines of diff unless pre-approved.

## Git Conventions
- Branch naming: `feat/description`, `fix/description`, `chore/description`
- Commit messages: imperative mood, present tense ("Add expense endpoint", not "Added...")
- Never commit directly to `master`. Always use a branch.

## Task Execution Protocol
1. Before writing code, post a comment with your implementation plan.
2. After completing implementation, run the test suite locally before marking done.
3. If you encounter a decision that affects the architecture, escalate — do not decide alone.

## Escalation Triggers
Escalate to your manager if:
- The task requires changing a public API contract
- The estimated work exceeds 2× the task estimate
- You find a bug that affects more than the current task's scope
- You are blocked for more than one full heartbeat cycle
```

An agent that reads this skill knows: the stack, the standards, the process, the escalation criteria. It can execute coherently without you explaining any of this in the task description.

### Skills for Different Roles

You write different skills for different agent roles. A content writer needs different knowledge than a developer:

```markdown
# Content Standards — SKILL.md

## Your Role
You are a content writer for [Company Name], producing blog posts, 
social copy, and documentation.

## Voice and Tone
- Professional but approachable. No jargon unless explained.
- Always lead with the reader's problem, not our solution.
- Short sentences. Active voice. Concrete examples.

## Publishing Process
1. Draft in the designated `/content/drafts/` directory.
2. Post a preview link as a comment when draft is ready for review.
3. After approval, move to `/content/published/` and update the issue.

## SEO Baseline
- Target keyword in first 100 words, H1, and at least two H2s.
- Meta description: 150–160 characters, include keyword.
- Internal links: at least one per 500 words.
```

The content writer and the developer are running the same adapter (Claude Code), but their skill files give them completely different professional identities and operational contexts.

---

## 🏭 Project-Level Skills vs. Company-Level Skills

Skills can be scoped at two levels:

**Company-level skills** apply to all agents across all projects. Use these for:
- The Paperclip heartbeat protocol (already pre-installed)
- Your company's general communication standards
- Domain knowledge that all agents need (what your product does, who your customers are)

**Project-level skills** apply only to agents within a specific project. Use these for:
- Technical stack and conventions (engineering project)
- Content style guides (content project)
- Support response templates (customer support project)

In the agent's configuration, you specify which skill files to inject. A developer agent on the engineering project might load:
```
~/.claude/skills/paperclip.md          # The Paperclip protocol
~/.claude/skills/company-context.md    # What the company does
./skills/engineering-standards.md      # Project-specific code standards
./skills/testing-requirements.md      # Test coverage expectations
```

The agent wakes up, reads all four, and starts working with complete context.

---

## 🧬 Runtime Learning vs. Retraining — The Key Distinction

It is worth being precise about what skill injection is and is not.

**What it is:**
- Text prepended or injected into the agent's context window at the start of each run
- Standard in-context learning — the model reads it the same way it reads the task description
- Updatable without restarting the agent — write the new SKILL.md, it takes effect on the next heartbeat

**What it is not:**
- Fine-tuning — the model's weights are not modified
- Persistent memory — the skill is re-read fresh on every heartbeat (which is actually a feature: you can update skills and the agent immediately adapts)
- A replacement for model selection — if your task requires a model with specific capabilities, pick the right model; skills cannot give a model capabilities it does not have

The skill injection system is simple and powerful precisely because it uses the model's existing reading comprehension. The model is very good at reading structured instructions. Skills give it the instructions it needs.

---

## 🔄 Updating Skills — No Downtime Required

One of the practical delights of the skills system: you can update a skill file and the change takes effect on the agent's next heartbeat. No restart. No redeployment. No version bumps.

Your developer agent is running. You realise the coding standard needs to add ESLint configuration requirements. You open the skill file, add the section, save it. On the next heartbeat, the agent reads the updated skill and applies the new requirement to whatever task it picks up.

This is the factory's training programme — continuous, frictionless, and immediate.

---

## 🛸 What's Next

In **Episode 7**, we visit the Great Glass Elevator — **Clipmart**, Paperclip's coming marketplace for pre-built company templates. One-click import of entire org structures, agent configs, and skills. The ability to download a battle-tested team and start running it immediately.

The skills are in the workers' hands. Now let us see what happens when someone packages an entire workforce for distribution.

> *"And now, my dear children, we will move on to the most exciting room of all."*
> — Willy Wonka.
> *"And now, we move on to the feature that might be Paperclip's most consequential — portable companies."*
> — This series, transitioning to Episode 7.

---

*🍫 Charlie's Chocolate Factory is a series about building zero-human companies with Paperclip — the open-source AI agent orchestration platform.*
