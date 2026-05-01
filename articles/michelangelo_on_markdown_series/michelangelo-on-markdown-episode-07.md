---
title: "Michelangelo on Markdown ✍️ Ep.7"
part: 7
published: false
description: "Episode 7: Michelangelo was not only a sculptor and painter — he wrote over 300 poems and thousands of letters, a private knowledge system that tracked his thinking across a lifetime. Tolaria is that private knowledge system for the modern polymath: vault, notes, YAML frontmatter, types as lenses, wikilinks, neighborhood mode, BlockNote editing, and git history."
tags: [tolaria, markdown, knowledgebase, productivity]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/michelangelo_on_markdown_series/michelangelo-on-markdown-episode-07.png"
series: "Michelangelo on Markdown Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 7: The Letters and Poems

> *“I live and love in God’s peculiar light.”*
> — Michelangelo Buonarroti, Sonnet

-----

## The Private Archive of a Mind 📜

Michelangelo is remembered for marble and fresco. Less well known is that he wrote over 300 poems — sonnets, madrigals, letters — exploring theology, love, death, and the nature of creative work. These were not public compositions. They were the private archive of a mind at work: ideas accumulated, revised, connected, sometimes abandoned, sometimes developed into the foundations of the public work.

Every creator needs such an archive. The place where ideas are not yet composed into finished form — they are gathered, connected, explored. The notebook before the book. The sketch before the sculpture.

Tolaria is that archive. It is a desktop vault for plain Markdown files, organised into an interconnected knowledge base, fully offline, fully owned, version-controlled by git. It is the master’s sketchbook — portable, private, permanent.

-----

## 🗂️ SIPOC — The Letters and Poems

|**Suppliers**        |**Inputs**                                                         |**Process**                                                                |**Outputs**                                                               |**Customers**                                                                |
|---------------------|-------------------------------------------------------------------|---------------------------------------------------------------------------|--------------------------------------------------------------------------|-----------------------------------------------------------------------------|
|You (the thinker)    |Ideas, observations, drafts, research notes, tasks, journal entries|Create notes in Tolaria — plain Markdown files with YAML frontmatter       |A searchable, navigable, interconnected vault of knowledge                |Your future self — pulling from the archive to write the finished work       |
|Git (version control)|Every save/change to a note                                        |Tolaria’s Rust backend uses git history for creation and modification dates|A complete audit trail of every note’s evolution                          |You — see exactly when a note was created, what it looked like six months ago|
|Wikilinks `[[stem]]` |References to other notes by filename stem                         |Tolaria indexes all wikilinks across the vault                             |Backlinks, outgoing links, relationship maps                              |Neighborhood mode — the note-list centred on a selected note’s relationships |
|YAML frontmatter     |`type:`, `status:`, `Topics:`, custom fields                       |Vault scan parses all frontmatter; types drive sidebar categories          |A structured, filterable view of the vault without locking data in schemas|You — navigate by type, filter by status, without enforced schemas           |

-----

## The Vault: The Atelier 🏛️

Every Tolaria workspace is a **vault** — a directory on your filesystem. The vault is:

- A plain directory of `.md` files — no proprietary format
- A git repository — every change can be tracked, reverted, branched
- Completely offline — no account, no subscription, no server dependency
- Completely portable — open the same directory with any editor, any tool, any time

When you stop using Tolaria, you keep the files. The notes open in VS Code, Obsidian, iA Writer, or any text editor. The git history remains. The wikilinks are still there as plain text. Nothing is locked in.

Create a new vault: **File → New Vault** → choose a directory. Tolaria runs `git init` and creates the initial structure. Or open an existing directory with Markdown files — Tolaria will index it immediately.

-----

## Notes: The Folio Pages 📄

A note in Tolaria is a plain Markdown file. Nothing more. Nothing less.

```markdown
# On the Nature of Proportion

The ancient sculptors understood that beauty arises from relation, not
from isolated perfection. A hand that is beautiful in isolation may be
wrong when attached to an arm.

This principle of *relational proportion* underlies the Vitruvian canon.
```

Tolaria determines the note’s **display title** by this priority:

1. First `# H1` heading in the body
1. Frontmatter `title:` field
1. The filename stem, converted to title case

So `on-the-nature-of-proportion.md` displays as “On the Nature of Proportion” even without a frontmatter title.

-----

## YAML Frontmatter: The Note’s Commission Document 📋

Every note can carry a YAML frontmatter block — a structured section at the top of the file, between `---` delimiters. Tolaria reads and indexes these fields:

```markdown
---
type: essay
status: draft
date: 2026-04-17
Topics:
  - "[[proportion]]"
  - "[[classical-sculpture]]"
Key People:
  - "[[vitruvius]]"
  - "[[alberti]]"
---

# On the Nature of Proportion

...
```

### What Tolaria does with frontmatter:

**`type:`** — the most important field. Tolaria groups notes by type in the sidebar. Types are navigation aids — there are no required fields, no validation, no enforcement. A note of `type: essay` appears in the “essay” section; a note of `type: research-note` appears in “research-note”. Create whatever types serve your workflow.

**`status:`** — visible in note metadata; used for filtering in custom views.

**Any custom field with `[[wikilink]]` values** — Tolaria automatically detects wikilinks in frontmatter and adds them to the note’s relationship graph. A `Topics` field with `[[proportion]]` creates a relationship between this note and the note named `proportion.md`.

-----

## Types as Lenses: The Taxonomy Without the Cage 🔍

Tolaria’s types are *lenses*, not schemas.

In a database, a schema enforces structure: required fields, validated formats, referential integrity. Assign a type and the system demands you fill in the fields.

In Tolaria, a `type:` field is a navigation category. It groups notes in the sidebar. It does not require any other field to be present. A note with `type: essay` and a note with `type: essay` and twelve additional frontmatter fields are both equally valid.

This means:

- You can add a type to a note anytime without changing its content
- You can remove a type without breaking anything
- Two notes with the same type can look completely different internally
- Your taxonomy evolves as your thinking evolves

Common type taxonomies:

|Workflow          |Types used                                                             |
|------------------|-----------------------------------------------------------------------|
|Academic research |`paper`, `book`, `note`, `quote`, `data`, `analysis`, `draft`          |
|Personal knowledge|`concept`, `person`, `project`, `journal`, `reference`, `question`     |
|Creative work     |`idea`, `sketch`, `draft`, `chapter`, `character`, `scene`, `reference`|
|Professional      |`meeting`, `decision`, `project`, `task`, `contact`, `resource`        |

-----

## Wikilinks: The Drawing That References Other Drawings `[[note]]` 🔗

Michelangelo’s preparatory drawings are a network — one sketch references anatomical studies, which reference proportion diagrams, which reference classical sources. Each drawing exists in relation to the others.

Tolaria implements this with wikilinks: `[[note-stem]]` — a reference to another note by its filename stem (without the `.md` extension).

```markdown
# On the Nature of Proportion

Proportion in sculpture derives from [[vitruvian-canon]].
Michelangelo applied it most explicitly in [[the-david-analysis]].

The concept relates closely to [[contrapposto]], which produces
the dynamic S-curve that distinguishes Renaissance from classical poses.
```

Wikilinks create:

- **Outgoing links**: this note refers to these others
- **Backlinks**: these other notes refer to this one
- **Relationship graph**: visible in the inspector panel

In the editor, type `[[` and Tolaria opens an autocomplete picker showing all notes in the vault. Select the target note and Tolaria inserts the correctly formatted wikilink. In rendered view, wikilinks are clickable — navigate the vault without leaving the keyboard.

-----

## Frontmatter Relationships: The Web of the Workshop 🕸️

Any frontmatter field whose values contain `[[wikilinks]]` creates typed relationships:

```markdown
---
type: sculpture-analysis
Topics:
  - "[[proportion]]"
  - "[[contrapposto]]"
Key People:
  - "[[michelangelo]]"
  - "[[pliny-the-elder]]"
Commissioned by:
  - "[[medici-family]]"
Location: Florence
---

# Analysis: The David
```

Tolaria parses these and creates:

- Topics relationship group: proportion, contrapposto
- Key People relationship group: michelangelo, pliny-the-elder
- Commissioned by relationship group: medici-family

These appear in the inspector panel and power the Neighborhood mode navigation.

-----

## Neighborhood Mode: The Web of Connections 🌐

Neighborhood mode is one of Tolaria’s most distinctive navigation features. When you select a note in the note list and activate Neighborhood mode, the note list pivots to show that note’s relational context:

- The note itself, pinned at the top
- Outgoing relationship groups (from frontmatter wikilinks)
- Backlinks — notes that link to this one
- Children and events (if those relationship types are present)

Navigate the vault the way ideas connect — not through a folder tree, but through the web of relationships that naturally exists in knowledge.

-----

## The BlockNote Editor: The Illuminated Page ✍️

Tolaria’s editor is **BlockNote** — a rich text editor that round-trips to Markdown without data loss. What you see in the editor is approximately what the Markdown looks like, but with visual formatting applied:

- Bold text appears bold
- Headings appear as headings with correct size hierarchy
- Code blocks appear with syntax highlighting
- Tables appear as grids
- Wikilinks appear as styled inline links

Every visual action in BlockNote produces standard Markdown. No proprietary node types. No special syntax. If a formatting action cannot be represented in standard Markdown, BlockNote does not offer it.

### Raw and diff mode

Press the toggle in the top bar to switch to **raw mode** (CodeMirror 6). Now you see and edit the actual Markdown source. This is useful for:

- Editing frontmatter directly
- Adding Quarkdown-specific markup (`.include`, function calls)
- Debugging unusual formatting

**Diff mode** shows the changes since the last git commit — side by side, before and after. Use this to review what you changed in a session before committing.

-----

## Git History: The Archive of the Atelier 📚

Every Tolaria vault is a git repository. Every note save can be committed with a message. Tolaria uses the git history to:

**Determine note creation date**: the date of the first git commit touching this file.

**Determine last modification date**: the date of the most recent git commit touching this file.

**Provide a complete audit trail**: every version of every note, back to the first commit, is retrievable through standard git commands.

This means a vault is not just a collection of current notes — it is a complete history of the thinking that produced them. The evolution of an essay, the development of a research question, the abandoned drafts, the reconsidered positions — all preserved.

```bash
# In your vault directory
git log --oneline notes/the-david-analysis.md
# a3f9c2d Added counterargument on proportion in damaged figures
# 71bc884 Initial analysis of contrapposto in David
# 3e2f115 Sketch note: first visit to Accademia

git show 71bc884:notes/the-david-analysis.md
# Shows the full note at that commit
```

-----

## Favorites and Custom Views: The Pinned Sketches 📌

### Favorites

Star any note to add it to the Favorites section — a pinned set of notes always accessible at the top of the sidebar. Tolaria persists favorites as a frontmatter field (`favorite: true`, `favoriteIndex: 0`), so the star survives any app reinstall.

```markdown
---
type: reference
favorite: true
favoriteIndex: 0
---

# The Vitruvian Canon

...
```

Drag favorites to reorder them.

### Custom views

Custom views filter the note list by frontmatter fields. Create a view like “Active research notes” that shows only notes with `type: research-note` and `status: active`:

```yaml
# Custom view definition (from the app)
filter:
  and:
    - type: research-note
    - status: active
sort: modified desc
```

The view appears in the sidebar. Click it to see the filtered list. No schema enforcement — it simply filters the notes whose frontmatter happens to match.

-----

## The Full-Text Search: Finding the Lost Marble 🔍

Command palette (`Cmd/Ctrl-K`) opens full-text search across the entire vault. Search by title, frontmatter content, or body text. Tolaria shows results with snippets showing the matching context.

The search is instant — Tolaria maintains an index of the vault and updates it as notes change.

-----

In **Episode 8**, the aging master’s studio. Tolaria’s AI integration: AGENTS.md, Claude Code, Codex CLI, Gemini CLI, the MCP server, and the complete workflow from Tolaria knowledge vault to Quarkdown published output.

-----

**🔗 Resources**

- **Tolaria GitHub**: [github.com/refactoringhq/tolaria](https://github.com/refactoringhq/tolaria)
- **Tolaria releases**: [refactoringhq.github.io/tolaria](https://refactoringhq.github.io/tolaria/)
- **Tolaria README**: [github.com/refactoringhq/tolaria/blob/main/README.md](https://github.com/refactoringhq/tolaria/blob/main/README.md)

-----

*✍️ Michelangelo on Markdown Series — crafting beautiful documents with Quarkdown and Tolaria, through the lens of the Renaissance master’s studio.*
