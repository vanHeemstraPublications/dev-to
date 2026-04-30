---
title: "Michelangelo on Markdown ✍️ Ep.1"
published: false
description: "Episode 1: Michelangelo saw the David already waiting inside the marble. The writing begins the same way — raw material, a single vision, and the right tools. Meet Quarkdown (Markdown with superpowers) and Tolaria (your knowledge vault), install both, carve your first document, and understand why these two tools belong in the same studio."
tags: [quarkdown, markdown, writing, beginners]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/michelangelo_on_markdown_series/michelangelo-on-markdown-episode-01.png
series: "Michelangelo on Markdown Series"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 1: The Master Confronts the Block

> *“The sculpture is already complete within the marble block, before I start my work. It is already there, I just have to chisel away the superfluous material.”*
> — Michelangelo Buonarroti

-----

## The Marble Is Already There 🗿

In 1501, Michelangelo was given a block of marble that had defeated two previous sculptors. Too tall, too narrow, badly quarried. Other masters had touched it and walked away. Michelangelo looked at it for weeks. Then he began.

The David that emerged — 5.17 metres of perfect human form — was not created. It was revealed. The material was always sufficient. The vision was always present. What was required was the right technique, the right tools, and the discipline to remove everything that was not the David.

Writing works the same way. The ideas are already there — in your notes, your thinking, your knowledge. What stands between your thoughts and a beautiful, well-composed document is technique and tooling. This series covers both.

**Quarkdown** is a modern typesetting system that extends Markdown with function calls, scripting, layout controls, and multi-output support. One syntax produces scientific papers, slide decks, documentation sites, and knowledge bases. It is open-source, made in Italy, and has over 10,000 GitHub stars.

**Tolaria** is a desktop knowledge vault. Your notes are plain Markdown files with YAML frontmatter, stored in a local git repository. Files-first. Offline-first. Zero lock-in. AI-ready. Keyboard-first. When you leave Tolaria, you take your files with you and lose nothing.

Together: Tolaria is the studio where ideas accumulate. Quarkdown is the chisel that shapes them into finished works.

-----

## 🗂️ SIPOC — The Master Confronts the Block

|**Suppliers**     |**Inputs**                                                 |**Process**                                                                        |**Outputs**                                                   |**Customers**                                        |
|------------------|-----------------------------------------------------------|-----------------------------------------------------------------------------------|--------------------------------------------------------------|-----------------------------------------------------|
|You (the writer)  |Ideas, research, drafts, knowledge                         |Write `.qd` Quarkdown source in the Tolaria vault or any text editor               |Compiled HTML, PDF, or presentation                           |Readers, students, collaborators, publication venues |
|Quarkdown compiler|A `.qd` source file with standard Markdown + function calls|Lexing → Parsing → Function expansion → Tree traversal → Rendering → Post-rendering|HTML output in `output/` directory; optionally PDF via `--pdf`|Browser, PDF readers, any document consumer          |
|Tolaria vault     |Plain `.md` files with YAML frontmatter in a git repository|The app indexes and navigates the vault; BlockNote edits; wikilinks connect notes  |A navigable, searchable knowledge base of interconnected ideas|You — ready to pull notes into Quarkdown compositions|

-----

## The Metaphor Table: Renaissance Workshop Meets Modern Tooling 🎨

|Renaissance / Michelangelo concept     |Technical concept                                           |
|---------------------------------------|------------------------------------------------------------|
|The marble block — raw, unformed       |`.md` files and `.qd` files — the raw material              |
|The master’s atelier / bottega         |**Tolaria vault** — the studio where everything lives       |
|The master’s sketchbook (*cartone*)    |Individual notes in Tolaria                                 |
|Workshop assistants (*garzone*)        |AI agents (Claude Code, Codex CLI, Gemini CLI) via AGENTS.md|
|Moving a sketch to the marble          |Moving Tolaria notes into a `.qd` Quarkdown source file     |
|The chisel’s first mark                |`.doctype {paged}` — choosing the form of the work          |
|Choosing marble grain and colour       |Theme selection: color + layout theme                       |
|The patron’s required format           |Document type: paged / plain / slides / docs                |
|The preparatory cartoon (*cartone*)    |`.function {name}` — a reusable compositional template      |
|Systematic scale grid                  |`.numbering` — ordered elements throughout                  |
|Chips revealing the form               |Quarkdown’s compilation pipeline                            |
|Viewing the fresco from scaffolding    |Live preview `-p -w`                                        |
|The commission delivered               |PDF export `--pdf`                                          |
|The bottega’s archives                 |Tolaria vault’s git history                                 |
|The David (one block, one vision)      |A single `.qd` file compiled to one output                  |
|The Sistine ceiling (grand unification)|Multi-file Quarkdown with `.include`                        |

-----

## Installing Quarkdown 🔧

Quarkdown v2.0.0 was released on 23 April 2026. Install it with one command:

**Linux / macOS:**

```bash
curl -fsSL https://raw.githubusercontent.com/quarkdown-labs/get-quarkdown/refs/heads/main/install.sh \
  | sudo env "PATH=$PATH" bash
```

**macOS with Homebrew:**

```bash
brew install quarkdown-labs/quarkdown/quarkdown
```

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/quarkdown-labs/get-quarkdown/refs/heads/main/install.ps1 | iex
```

**Windows with Scoop:**

```powershell
scoop bucket add java
scoop bucket add quarkdown https://github.com/quarkdown-labs/scoop-quarkdown
scoop install quarkdown
```

Verify:

```bash
quarkdown --version
# quarkdown 2.0.0
```

If you use VS Code, install the official Quarkdown extension from the marketplace — it provides syntax highlighting, live preview, and compile shortcuts.

-----

## Installing Tolaria 🖥️

Download the latest release from [refactoringhq.github.io/tolaria](https://refactoringhq.github.io/tolaria/).

Available for:

- macOS Silicon (`.dmg`)
- macOS Intel (`.dmg`)
- Linux (`.AppImage`, `.deb`)
- Windows (`.exe` setup)

After installation, launch Tolaria and create a new vault: **File → New Vault** → choose a directory. Tolaria initialises a git repository there automatically.

-----

## Your First Quarkdown Document: The David in Miniature 🗿

Create your first project:

```bash
quarkdown create my-first-work
cd my-first-work
```

The project creator creates a folder with `main.qd` and a default setup. Open `main.qd` and replace its contents:

```quarkdown
.doctype {paged}
.doctitle {My First Work}
.docauthor {Your Name}
.theme {paperwhite} layout:{latex}

# The Beginning

Every great work starts with a single mark.

Quarkdown extends **Markdown** with function calls,
scripting, and layout controls.

## A Simple Function Call

The square root of 144 is .sqrt {144}.

Let us also see a centred element:

.align {center}
    *Everything becomes possible with the right tools.*
```

Compile and preview:

```bash
# Compile to HTML
quarkdown c main.qd

# Compile with live preview and file watching
quarkdown c main.qd -p -w
```

Your browser opens automatically to the rendered document. Change anything in `main.qd`, save, and the preview updates instantly.

Export to PDF:

```bash
quarkdown c main.qd --pdf
```

-----

## The Project Structure 📂

```
my-first-work/
├── main.qd          ← the primary source file (the marble)
├── output/          ← compiled output (HTML, assets)
│   └── main.html
└── [assets/]        ← images, CSVs, other files you reference
```

For multi-file works, the structure grows naturally:

```
my-book/
├── main.qd          ← entry point, calls .include on chapters
├── chapter-1.qd
├── chapter-2.qd
├── img/
│   └── figure.png
└── output/
```

-----

## What Quarkdown Replaces (and What It Does Not) ⚖️

|Quarkdown does this|Replaces this                         |With what output                    |
|-------------------|--------------------------------------|------------------------------------|
|`.doctype {paged}` |LaTeX, Typst                          |Papers, books, reports              |
|`.doctype {plain}` |Notion, Obsidian                      |Notes, knowledge bases, simple sites|
|`.doctype {docs}`  |GitBook, MkDocs, Docusaurus, VitePress|Wikis, technical documentation      |
|`.doctype {slides}`|Beamer (LaTeX), Google Slides         |Lectures, talks, presentations      |

Quarkdown does not replace your note-taking tool — that is what Tolaria is for.

-----

## What Tolaria Is Not 🚫

Tolaria is not a publishing tool. It does not compile anything. It does not produce PDFs or presentations. Tolaria is the studio, not the foundry.

What Tolaria does: it organises the marble. It keeps your knowledge interconnected, versioned, searchable, and accessible. When you are ready to compose a Quarkdown document, you draw from the vault.

The workflow is:

1. Think and capture in Tolaria (sketchbook)
1. Organise and connect in Tolaria (cartone)
1. Write and compose in Quarkdown (chisel)
1. Compile and deliver (the finished work)

-----

## The Series: Eight Works by the Master 🎨

|#|Episode               |Michelangelo work        |Theme                                  |
|-|----------------------|-------------------------|---------------------------------------|
|1|*This one* — The Block|The David                |Introduction, install, first document  |
|2|The Grand Ceiling     |The Sistine Chapel       |Document types, themes, metadata       |
|3|The Perfect Form      |The Pietà                |Function syntax, custom functions      |
|4|Stone and Space       |The Medici Tombs         |Layout: stacks, containers, figures    |
|5|The Last Judgement    |The Last Judgement       |Scripting, variables, data, charts     |
|6|The Great Commission  |St. Peter’s Basilica     |Multi-file, built-in libraries         |
|7|Letters and Poems     |Michelangelo’s writings  |Tolaria: vault, notes, types, wikilinks|
|8|The Aging Master      |The late unfinished works|Tolaria AI, MCP, full workflow         |

In **Episode 2**, we look up at the Sistine ceiling — the grandest compositional challenge, solved by disciplined structure. Document types, themes, metadata, and the page layout controls that make a document feel intentional.

-----

**🔗 Resources**

- **Quarkdown home**: [quarkdown.com](https://quarkdown.com)
- **Quarkdown Wiki**: [quarkdown.com/wiki](https://quarkdown.com/wiki)
- **Quarkdown GitHub**: [github.com/iamgio/quarkdown](https://github.com/iamgio/quarkdown)
- **Tolaria releases**: [refactoringhq.github.io/tolaria](https://refactoringhq.github.io/tolaria/)
- **Tolaria GitHub**: [github.com/refactoringhq/tolaria](https://github.com/refactoringhq/tolaria)

-----

*✍️ Michelangelo on Markdown Series — crafting beautiful documents with Quarkdown and Tolaria, through the lens of the Renaissance master’s studio.*
