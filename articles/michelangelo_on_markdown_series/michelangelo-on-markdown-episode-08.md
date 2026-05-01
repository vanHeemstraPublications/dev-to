-----

## title: “Michelangelo on Markdown! Ep.8: The Aging Master’s Studio”
published: false
description: “Episode 8: In his final years, Michelangelo worked with assistants who executed his vision at scale. Tolaria’s AI integration does the same: AGENTS.md teaches Claude Code, Codex CLI, and Gemini CLI how your vault works. The MCP server connects any AI agent to your notes. The complete workflow: from vault notes to finished Quarkdown document.”
tags: [tolaria, ai, workflow, markdown]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/michelangelo-markdown-episode-08.png”
series: “Michelangelo on Markdown Series”
canonical_url: “”
organization: “the-software-s-journey”
part: 1

# Michelangelo on Markdown! ✍️

## Episode 8: The Aging Master’s Studio

> *“I am still learning.”*
> — Michelangelo Buonarroti (attributed)

-----

## The Master and His Assistants 🏛️

In his seventies and eighties, Michelangelo worked increasingly with assistants — not to diminish his vision, but to extend it. Tiberio Calcagni finished portions of the Rondanini Pietà. Assistants managed the logistics of the St. Peter’s construction site. The master directed; the assistants executed. The vision was Michelangelo’s. The hands were many.

Tolaria’s AI integration follows the same logic. The vault — the knowledge, the organisation, the wikilinks, the types — is yours. The AI agents are your assistants: Claude Code, Codex CLI, Gemini CLI. They understand the vault’s structure through the AGENTS.md instruction file. They can read notes, create connections, draft compositions, and reorganise the archive. The vision remains yours.

-----

## 🗂️ SIPOC — The Aging Master’s Studio

|**Suppliers**                     |**Inputs**                                                              |**Process**                                                                                       |**Outputs**                                                               |**Customers**                                                            |
|----------------------------------|------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|-------------------------------------------------------------------------|
|AGENTS.md (vault instruction file)|Your vault’s note conventions, frontmatter schema, relationship patterns|AI agent reads AGENTS.md at session start to understand how this specific vault is organised      |An AI that understands your vault’s structure without repeated explanation|You — the AI asks informed questions and makes structurally correct notes|
|Tolaria MCP server                |Active vault path; WebSocket port 9711                                  |MCP server exposes vault notes as a tool surface for any MCP-compatible AI agent                  |External AI agents can read, search, and create notes in the vault        |Claude Code, Codex CLI, Gemini CLI, or any agent with MCP support        |
|The complete workflow             |Tolaria notes + Quarkdown source                                        |(1) Gather in Tolaria → (2) Organise and connect → (3) Write Quarkdown → (4) Compile → (5) Deliver|A published document grounded in your accumulated knowledge               |Readers who receive a finished, composed work                            |

-----

## AGENTS.md: The Workshop Instructions 📜

Every Tolaria vault has (or should have) an `AGENTS.md` file at the root. This is the master’s instructions to the assistants: how this vault is organised, what the types mean, how notes are named, what conventions are used.

When an AI agent starts a session in the vault, it reads `AGENTS.md` first. This gives it the context it needs to work effectively without repeated explanation.

A good `AGENTS.md` for a writing vault:

```markdown
# Vault Guide for AI Agents

This vault belongs to [Author Name] and contains research, drafts, and
published work on Renaissance art history and Quarkdown documentation.

## Note Conventions

- All notes use plain Markdown with YAML frontmatter
- Filenames are lowercase, hyphen-separated stems
- The display title comes from the first `# H1` heading
- Never add proprietary syntax; keep all notes valid Markdown

## Types in This Vault

- `essay` — draft or published essays; check `status:` for draft/published
- `research-note` — source reading notes with `source:` frontmatter
- `concept` — definitions and explanations of concepts
- `person` — biographical notes on historical figures
- `quarkdown-draft` — `.qd` source files being developed

## Relationship Conventions

- Use `Topics: ["[[concept]]"]` for thematic connections
- Use `Key People: ["[[person-slug]]"]` for biographical connections
- Use `Sources: ["[[book-slug]]"]` for source connections

## What to Do

- When creating a note, always include `type:` and at least one relationship
- When asked to research a topic, create a `research-note` with sources cited
- When asked to draft an essay, create a `quarkdown-draft` and use `.include`
  to pull in relevant research-note content
- Never delete notes — mark status as `archived` if obsolete

## What Not to Do

- Do not use HTML in notes
- Do not add proprietary frontmatter fields not listed above
- Do not create files outside the vault boundary
```

Tolaria seeds a starter `AGENTS.md` when you initialise a Getting Started vault. Edit it to match your specific vault conventions.

-----

## The Tolaria MCP Server: The Workshop’s Communication System 📡

Tolaria bundles an MCP (Model Context Protocol) server. When activated, it exposes the active vault as a tool surface that any MCP-compatible AI agent can query and operate:

### Activating the MCP server

From the status bar at the bottom of the Tolaria window, or via the command palette (`Cmd/Ctrl-K`):

```
> Set Up External AI Tools
```

Select your agent (Claude Code, Codex CLI, Gemini CLI). Tolaria:

1. Verifies that Node.js is available (required for the MCP server)
1. Generates the MCP configuration for that agent
1. Writes the configuration to the agent’s config directory

For Claude Code, this writes to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "tolaria": {
      "command": "node",
      "args": ["/path/to/tolaria/mcp-server/index.js"],
      "env": {
        "VAULT_PATH": "/Users/you/vault",
        "WS_UI_PORT": "9711"
      }
    }
  }
}
```

### What the MCP server exposes

Once connected, an AI agent can:

- **Read notes** — by filename, by type, or by search query
- **Create notes** — following the vault’s convention from AGENTS.md
- **Search the vault** — full-text search across all notes
- **Read the vault structure** — available types, note count, recent activity
- **Follow wikilinks** — navigate from note to related notes

The vault boundary is enforced: the MCP server cannot read or write files outside the active vault directory.

-----

## AI Agent Workflows: The Assistants at Work 🤖

### Supported agents

|Agent            |Setup                                                    |Notes                                            |
|-----------------|---------------------------------------------------------|-------------------------------------------------|
|**Claude Code**  |`CLAUDE.md` in vault; MCP server config in `~/.claude/`  |CLAUDE.md is a shim that imports AGENTS.md       |
|**Codex CLI**    |`AGENTS.md` in vault; MCP server config                  |Direct — reads AGENTS.md                         |
|**Gemini CLI**   |`GEMINI.md` (optional); MCP via `~/.gemini/settings.json`|Created only by explicit “Set Up AI Tools” action|
|**Any MCP agent**|Standard MCP stdio connection                            |Works with any client supporting MCP protocol    |

### Practical AI workflows in the vault

**Research gathering:**

```
In Claude Code session, inside the vault directory:

> Read my existing notes on Carrara marble (type: research-note).
> Search the web for recent papers on marble grain size and strength.
> Create a new research-note summarising the findings, with
  Sources frontmatter linking to my existing marble notes.
```

**Cross-reference building:**

```
> Find all my concept notes.
> For each concept note, check whether the related concept notes
  it should link to actually have backlinks to it.
> Add missing wikilinks to complete the bidirectional web.
```

**Draft assistance:**

```
> I want to write an essay on contrapposto.
> Gather all research-notes with Topics: [[contrapposto]].
> Create a Quarkdown draft at quarkdown-drafts/contrapposto-essay.qd
  that uses .include to pull in the relevant research notes
  and structures them into introduction, analysis, and conclusion.
```

-----

## The AI Floating Panel 🤖

Inside the Tolaria app, the AI panel (`Cmd-Option-I`) opens the integrated AI agent panel:

- Select the active CLI agent (Claude Code, Codex CLI, Gemini CLI, OpenCode, pi CLI)
- The agent session runs inside Tolaria with access to the vault via MCP
- Tool execution is shown in the panel — you see what files the agent reads and writes
- Permission mode controls what the agent can do autonomously vs. what it must ask for

This is the equivalent of the assistant working at a desk in the studio — visible, supervised, operating in the same space as the master.

-----

## The Complete Workflow: From First Thought to Published Work 🗿

Here is the complete integrated workflow — from initial idea to finished Quarkdown document:

### Phase 1: Capture (Tolaria)

```
Tolaria → Cmd-N → New note
type: concept
---
# Contrapposto

The sculptural principle of dynamic balance.
Weight concentrated on one leg, creating
opposing tilts of hips and shoulders.

Links: [[classical-sculpture]] [[proportion]] [[michelangelo]]
```

### Phase 2: Accumulate (Tolaria)

Over days, weeks, months: more notes connecting to this concept.

```
research-note: Vitruvius on standing postures
  Topics: [[contrapposto]] [[vitruvian-canon]]

research-note: The Doryphoros of Polykleitos
  Topics: [[contrapposto]] [[classical-sculpture]]

research-note: Contrapposto in the David
  Topics: [[contrapposto]] [[the-david]]
  Key People: [[michelangelo]]
```

### Phase 3: Organise (Tolaria — Neighborhood mode)

Open the `contrapposto` note. Activate Neighborhood mode. See all connected notes:

- Vitruvius on standing postures
- The Doryphoros of Polykleitos
- Contrapposto in the David
- classical-sculpture (backlink)
- proportion (backlink)

The web of knowledge is visible. The essay’s structure is already implicit in the connections.

### Phase 4: Compose (Quarkdown)

Create the Quarkdown source — a new file in the vault or in a separate compositions directory:

```quarkdown
// compositions/contrapposto-essay.qd
.doctype {paged}
.doctitle {Contrapposto: Dynamic Balance in Renaissance Sculpture}
.docauthor {[Author]}
.theme {paperwhite} layout:{latex}
.numbering
    - headings: 1.1.1
    - figures: 1.1

.tableofcontents

# Introduction

The concept of contrapposto — dynamic balance through opposing directional
forces in the figure — represents one of the central formal achievements
of Renaissance sculpture.

## Origins: Classical Precedents

.include {../notes/doryphoros-analysis.qd}

## Development: The Vitruvian Framework

.include {../notes/vitruvian-contrapposto.qd}

# The David as Culmination

.include {../notes/contrapposto-in-the-david.qd}

!(60%)[The David, Accademia Gallery](img/david-detail.jpg "Michelangelo,
       detail of the David showing contrapposto stance, 1501–1504")

# Conclusion

.box {The Principle Summarised} type:{note}
    Contrapposto is not an anatomical observation but a compositional
    philosophy: meaning arises from opposition in tension, not from
    isolated perfection.
```

### Phase 5: Compile (Quarkdown CLI)

```bash
cd compositions
quarkdown c contrapposto-essay.qd -p -w
# Live preview opens — edit and refine

quarkdown c contrapposto-essay.qd --pdf
# PDF generated: output/contrapposto-essay.pdf
```

### Phase 6: Deliver

The PDF is the finished work. The Tolaria vault is the living knowledge system that produced it — and continues to grow. The next commission draws from the same archive, now richer by everything the current work required.

-----

## The Combined Tool Stack: The Complete Master’s Workshop 🔧

|Layer               |Tool                                    |Purpose                                        |
|--------------------|----------------------------------------|-----------------------------------------------|
|Capture and organise|**Tolaria**                             |Notes, wikilinks, types, git history           |
|Scripted assistance |**Claude Code / Codex CLI / Gemini CLI**|AI agents operating in the vault via MCP       |
|Composition         |**Quarkdown**                           |Typeset documents from `.qd` source files      |
|Preview             |`quarkdown c -p -w`                     |Live browser preview during editing            |
|Output              |`quarkdown c --pdf`                     |PDF export for distribution                    |
|IDE                 |**VS Code + Quarkdown extension**       |Syntax highlighting, preview, compile shortcuts|

-----

## Michelangelo’s Final Word 🗿

Michelangelo died on 18 February 1564, at 88 years old, still working. The Rondanini Pietà, found in his studio after his death, was unfinished. The figure of Christ had been reworked so many times that the original arms survive as a separate column of marble beside the current form — a ghost of earlier thinking made permanent.

That is the creative process. It is never finished. There is always another revision, another connection discovered, another better expression of the idea. The vault grows. The document evolves. The finished work is a moment of imposed completion, not a natural terminus.

Tolaria holds the accumulation. Quarkdown renders the moment.

-----

## The Complete Series: Eight Works by the Master 🎨

|#|Episode                       |Michelangelo work   |What we built                                      |
|-|------------------------------|--------------------|---------------------------------------------------|
|1|The Master Confronts the Block|The David           |Install Quarkdown + Tolaria, first document        |
|2|The Grand Ceiling             |The Sistine Chapel  |Document types, themes, metadata, footnotes, TOC   |
|3|The Perfect Form              |The Pietà           |Function syntax, custom functions, variables, boxes|
|4|Stone and Space               |The Medici Tombs    |Layout: stacks, float, clip, figures, TeX          |
|5|The Last Judgement            |The Last Judgement  |Scripting, conditionals, loops, data, charts       |
|6|The Great Commission          |St. Peter’s Basilica|Multi-file, Paper + Docs libraries, slides         |
|7|The Letters and Poems         |The private writings|Tolaria vault, notes, types, wikilinks, git        |
|8|*This one* — The Aging Master |The final studio    |AI integration, MCP, AGENTS.md, full workflow      |

-----

**🔗 Resources**

- **Tolaria AGENTS.md documentation**: [github.com/refactoringhq/tolaria](https://github.com/refactoringhq/tolaria)
- **Tolaria releases**: [refactoringhq.github.io/tolaria](https://refactoringhq.github.io/tolaria/)
- **Quarkdown home**: [quarkdown.com](https://quarkdown.com)
- **Quarkdown Wiki**: [quarkdown.com/wiki](https://quarkdown.com/wiki)
- **VS Code Quarkdown extension**: [quarkdown.com/vs-code](https://quarkdown.com/vs-code)
- **Quarkdown standard library**: [quarkdown.com/docs/quarkdown-stdlib](https://quarkdown.com/docs/quarkdown-stdlib)

-----

*✍️ Michelangelo on Markdown Series — eight episodes on crafting beautiful documents with Quarkdown and Tolaria, through the lens of the Renaissance master’s studio. The series is complete. The vault continues.*
