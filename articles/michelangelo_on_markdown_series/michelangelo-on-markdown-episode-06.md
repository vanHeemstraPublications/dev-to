-----

## title: “Michelangelo on Markdown! Ep.6: The Great Commission”
published: false
description: “Episode 6: Michelangelo did not design St. Peter’s as a single sketch — he organised it into coordinated architectural drawings, each section developed independently but governed by the unified plan. Multi-file Quarkdown works identically: .include, subdocuments, the Paper and Docs built-in libraries, cross-references, bibliography, and the slides document type.”
tags: [quarkdown, markdown, multifile, documentation]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/michelangelo-markdown-episode-06.png”
series: “Michelangelo on Markdown Series”
canonical_url: “”
organization: “the-software-s-journey”
part: 1

# Michelangelo on Markdown! ✍️

## Episode 6: The Great Commission

> *“The greatest danger for most of us is not that our aim is too high and we miss it, but that it is too low and we reach it.”*
> — Michelangelo Buonarroti

-----

## The Architecture That Outlived Its Architect 🏛️

Michelangelo became the chief architect of St. Peter’s Basilica in 1546, at the age of 71. He worked on it for eighteen years until his death in 1564 — the dome was completed posthumously by Giacomo della Porta. The project was too large for any single page of drawings. It was organised into a coordinated system of plans, sections, elevations, and details — each independently developed, each governed by the unified overall scheme.

A research paper has an introduction, methodology, results, and discussion. A textbook has chapters. A documentation site has sections, subsections, and an API reference. These are St. Peter’s Basilica — too large for a single file, governed by a coordinated plan.

Quarkdown’s multi-file system allows any project of any scale to be structured exactly as needed, with each file focused on its own content while the whole remains coherent.

-----

## 🗂️ SIPOC — The Great Commission

|**Suppliers**              |**Inputs**                                                       |**Process**                                                                                |**Outputs**                                                                |**Customers**                                                   |
|---------------------------|-----------------------------------------------------------------|-------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|----------------------------------------------------------------|
|Multiple `.qd` source files|Content split across chapter files, section files, appendix files|`main.qd` uses `.include` or `.sub` to assemble the parts at compile time                  |One compiled output: the assembled document, as if written in a single file|Readers who never see the file structure — only the unified work|
|Paper library              |`use paper` at the top of a scientific document                  |Library functions available: `.abstract`, `.definition`, `.theorem`, `.proof`, `.lemma`    |Properly formatted academic blocks matching journal standards              |Academic readers expecting conventional scientific formatting   |
|Docs library               |`use docs` for documentation projects                            |Library functions: sections with permalinks, sidebar navigation, code examples with headers|A navigable documentation website with sidebar, search-ready structure     |Developers reading technical documentation                      |
|Bibliography data          |`.bib` file or inline `@cite` references                         |Quarkdown resolves citation keys to formatted references                                   |In-text citations and bibliography section at the document end             |Academic and research readers requiring citation standards      |

-----

## Including Files: The Floor Plan References the Details `.include` 📐

The `.include` function reads another Quarkdown file and inserts its content at that point in the document — as if it were written inline:

```quarkdown
// main.qd — the master plan
.doctype {paged}
.doctitle {Renaissance Proportional Systems}
.docauthor {Giorgio Vasari}
.theme {paperwhite} layout:{latex}

.numbering
    - headings: 1.1.1
    - figures: 1.1

.tableofcontents

.include {chapters/introduction.qd}
.include {chapters/methodology.qd}
.include {chapters/results.qd}
.include {chapters/discussion.qd}
.include {appendix/data-tables.qd}
```

Each chapter file is a standalone `.qd` file that can be compiled independently for proofing, then assembled via `main.qd` for the final output.

```quarkdown
// chapters/introduction.qd
# Introduction

The systematic study of proportion in Renaissance sculpture...
```

The file tree:

```
renaissance-study/
├── main.qd                    ← entry point
├── chapters/
│   ├── introduction.qd
│   ├── methodology.qd
│   ├── results.qd
│   └── discussion.qd
├── appendix/
│   └── data-tables.qd
├── img/
│   ├── david.jpg
│   └── pieta.jpg
├── data/
│   └── measurements.csv
└── output/
    └── main.html
```

-----

## Subdocuments vs Including: The Fresco Panel vs the Blueprint `.sub` 📜

`.include` merges the file’s content into the parent — the result is one document with shared numbering, table of contents, and page counter.

`.sub` (subdocument) treats the referenced file as a semi-autonomous document — it can have its own setup functions while still being rendered as part of the parent:

```quarkdown
.sub {appendix-b.qd}
```

The choice:

|Situation                                   |Use                                         |
|--------------------------------------------|--------------------------------------------|
|Chapters of a book                          |`.include` — shared numbering, seamless flow|
|A separate appendix with distinct formatting|`.sub` — can have its own partial setup     |
|A reusable library of functions             |`.include` — pull in function definitions   |
|A separately maintainable reference section |`.sub` — can be compiled standalone         |

-----

## Importing External Libraries: The Guild’s Shared Techniques 📚

Quarkdown supports importing community-created libraries:

```quarkdown
.import {https://example.com/quarkdown-lib/chemistry.qd}
```

The library is downloaded once and cached. Its functions become available for use in the document.

The built-in libraries (Paper and Docs) are accessed with `use`:

```quarkdown
use paper
```

-----

## The Paper Library: Academic Conventions 🎓

The Paper library provides functions that follow academic paper conventions — the same structures that appear in LaTeX’s `\begin{abstract}`, `\begin{theorem}`, and `\begin{proof}` environments, but in Quarkdown’s cleaner syntax.

```quarkdown
use paper

.doctype {paged}
.doctitle {On the Stress Distribution in Carrara Marble}
.docauthor {M. Buonarroti}
.theme {paperwhite} layout:{latex}
```

### The abstract

```quarkdown
.abstract
    We present a quantitative analysis of the structural behaviour of Carrara
    marble under compressive loading. The results demonstrate that grain size
    significantly affects crack propagation under sustained load. Implications
    for monumental sculpture are discussed.
```

### Definitions and theorems

```quarkdown
.definition {Contrapposto}
    A sculptural principle in which the human figure is posed with the weight
    predominantly on one leg, causing the hips and shoulders to tilt in
    opposite directions and producing a natural S-curve of the spine.

.theorem {Proportion of the Human Form}
    For any ideally proportioned human figure, the navel divides the standing
    height in the ratio of the golden section.

.proof
    By measurement of 47 idealised figures from classical and Renaissance sources:
    $ h_{navel} / H = 0.618 \pm 0.023 $ where $ H $ is total standing height. □

.lemma {Vitruvian Constraint}
    The span of the outstretched arms equals the standing height.

.corollary
    For any figure of height $ H $, the arm span is also $ H $.
```

### Scientific formatting in context

```quarkdown
use paper

## Materials and Methods

Marble samples were sourced from the Fantiscritti quarry, Carrara.
Samples were prepared to standard test specimens per ASTM C170[^1].

.definition {Compressive Strength}
    The maximum compressive stress a material can withstand before failure.
    Expressed in megapascals (MPa).

### Statistical Model

Let $ \sigma_c $ be compressive strength and $ G $ be mean grain size:

$ \sigma_c = \alpha - \beta \log(G) $

.theorem {Grain Size Relationship}
    Marble compressive strength decreases monotonically with mean grain size
    for samples with grain sizes in the range 0.2–2.0 mm.

.proof
    Regression analysis of 23 specimen pairs. $ R^2 = 0.94 $. See Figure 3.1. □

[^1]: ASTM International, *Standard Test Method for Compressive Strength of
      Dimension Stone*, C170/C170M-17, West Conshohocken, PA, 2017.
```

-----

## The Docs Library: Technical Documentation 🖥️

The Docs library targets documentation sites — wikis, technical references, and large knowledge bases:

```quarkdown
use docs

.doctype {docs}
.doctitle {Quarkdown CLI Reference}
.theme {galactic} layout:{hyperlegible}
```

With the Docs library, section headings automatically receive permalink anchors, the sidebar is populated from the heading structure, and code blocks receive language-specific syntax highlighting with optional captions.

-----

## Cross-References: The Master’s Reference System 🔖

In long documents, cross-references link to specific sections, figures, tables, or equations by label — automatically updating when content moves.

### Defining a cross-reference label

```quarkdown
!(60%)[The David](img/david.jpg "Michelangelo, David, 1501–1504") {#fig:david}

| Sample | Grain Size (mm) | Strength (MPa) |
|--------|-----------------|----------------|
| C-01   | 0.3             | 162            |
| C-02   | 0.8             | 148            | {#tab:marble}

$ \sigma_c = \alpha - \beta \log(G) $ {#eq:strength}
```

### Referencing

```quarkdown
As shown in Figure [#fig:david], the contrapposto stance...

The data in Table [#tab:marble] demonstrates the grain size effect...

Equation [#eq:strength] predicts the strength reduction...
```

Quarkdown resolves each reference to the correct number: “Figure 1.1”, “Table 2.3”, “Equation (4)”.

-----

## Bibliography: The Source Records 📖

Quarkdown supports bibliography with citation keys:

```quarkdown
The Vitruvian system is described extensively in De architectura [@vitruvius30bc]
and later interpreted by Alberti [@alberti1452].
```

Define references inline or in a `.bib`-style file:

```quarkdown
.bibliography
    vitruvius30bc:
        author: Vitruvius Pollio
        title: De architectura
        year: c. 30 BCE
        type: book

    alberti1452:
        author: Leon Battista Alberti
        title: De re aedificatoria
        year: 1452
        type: book
```

The bibliography section is generated at the document end, with in-text citations formatted according to the document’s citation style.

-----

## Slides: The Presentation Commission 🎭

The `slides` document type transforms Quarkdown into a presentation tool. Each level-1 heading creates a new slide section; level-2 headings create individual slides within sections.

```quarkdown
.doctype {slides}
.doctitle {Michelangelo's Compositional Principles}
.docauthor {Art History Department}
.theme {galactic} layout:{minimal}

# Proportion

## The Human Canon

The classical canon divides the body into 8 head-heights.

!(50%)[Human proportion diagram](img/canon.png)

## The Golden Section

$ \phi = \frac{1+\sqrt{5}}{2} \approx 1.618 $

.align {center}
    !(60%)[Fibonacci spiral](img/fibonacci.png)

# Contrapposto

## Definition

.box {Contrapposto} type:{note}
    Weight on one leg. Hips and shoulders tilt in opposition.
    Creates organic, naturalistic movement.
```

### Interactive fragments

Fragments reveal content step by step — press the right arrow to show each item:

```quarkdown
## The Four Statues of the Medici Chapel

.fragment
    1. **Dawn** — waking, uncertain

.fragment
    2. **Dusk** — fading, reflective

.fragment
    3. **Day** — vigorous, unfinished

.fragment
    4. **Night** — sleeping, completed
```

### Speaker notes

```quarkdown
## Key Points

- Contrapposto as dynamic balance
- The serpentine line in sculpture

.speakernotes
    Emphasise the contrast with the static frontality of Egyptian sculpture.
    Reference the Doryphoros of Polykleitos as a prior example.
    Note that the David is the culmination of this tradition, not its beginning.
```

-----

In **Episode 7**, Michelangelo the writer enters. His letters, poems, and notebooks — the private knowledge management system of a Renaissance polymath. Tolaria: the vault, notes, YAML frontmatter, types as lenses, wikilinks, neighborhood mode, BlockNote, raw mode, and git history.

-----

**🔗 Resources**

- **Including files**: [quarkdown.com/wiki/including-other-quarkdown-files](https://quarkdown.com/wiki/including-other-quarkdown-files)
- **Subdocuments**: [quarkdown.com/wiki/subdocuments](https://quarkdown.com/wiki/subdocuments)
- **Paper library**: [quarkdown.com/wiki/paper-library](https://quarkdown.com/wiki/paper-library)
- **Docs library**: [quarkdown.com/wiki/docs-library](https://quarkdown.com/wiki/docs-library)
- **Cross-references**: [quarkdown.com/wiki/cross-references](https://quarkdown.com/wiki/cross-references)
- **Slides**: [quarkdown.com/wiki/slides-configuration](https://quarkdown.com/wiki/slides-configuration)

-----

*✍️ Michelangelo on Markdown Series — crafting beautiful documents with Quarkdown and Tolaria, through the lens of the Renaissance master’s studio.*
