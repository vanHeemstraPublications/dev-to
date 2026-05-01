---
title: "Michelangelo on Markdown ✍️ Ep.2"
part: 2
published: false
description: "Episode 2: The Sistine Chapel ceiling was not one painting — it was nine central scenes unified by architectural trompe l’oeil borders, prophets, sibyls, and ancestors. Quarkdown’s document types, themes, metadata, page margins, table of contents, and footnotes are that same discipline: a unified compositional system applied before the first word."
tags: [quarkdown, markdown, documentation, writing]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/michelangelo_on_markdown_series/michelangelo-on-markdown-episode-02.png"
series: "Michelangelo on Markdown Series"
canonical_url: ""
organization: "the-software-s-journey"
part: 1
---

## Episode 2: The Grand Ceiling

> *“A man paints with his brains and not with his hands.”*
> — Michelangelo Buonarroti

-----

## The Ceiling Before the Painting 🎨

Before Michelangelo painted a single prophet on the Sistine ceiling, he spent months designing the architectural framework — the illusionistic marble borders, the thrones, the medallions, the ignudi. The framework defined the relationship between every scene. Without it, nine separate paintings. With it, one unified statement.

Document composition works identically. Before the first paragraph is written, decisions about format, page structure, typography, and navigation shape how every sentence will be received. A paper without page numbers feels like a draft. A presentation without a consistent theme feels amateur. A documentation site without a sidebar feels like an unindexed pile.

Quarkdown’s document setup functions are that architectural framework — declared at the top of the file, applying their effect throughout.

-----

## 🗂️ SIPOC — The Grand Ceiling

|**Suppliers**     |**Inputs**                                                                  |**Process**                                                    |**Outputs**                                                                              |**Customers**                                    |
|------------------|----------------------------------------------------------------------------|---------------------------------------------------------------|-----------------------------------------------------------------------------------------|-------------------------------------------------|
|Document author   |Choices: document type, theme, author name, language, page format           |Metadata functions declared at the top of `main.qd`            |A consistently styled, correctly formatted document with proper navigation               |Any reader opening the compiled HTML or PDF      |
|Quarkdown compiler|`.doctype`, `.theme`, `.docauthor`, `.numbering`, `.tableofcontents`        |Applied globally at compile time — affects every page          |Page layout, navigation elements, numbering, and cross-references generated automatically|The final document — nothing hand-positioned     |
|Reader            |Navigation needs: “Where am I? What chapter is this? How long is the paper?”|Table of contents, page counter, persistent headings, footnotes|Immediate orientation in the document                                                    |Reader — finds what they need without frustration|

-----

## The Four Document Types: Choosing Your Commission Format 📜

Every Quarkdown document begins with a type declaration. The type determines the fundamental output format.

```quarkdown
.doctype {paged}
```

### `.doctype {paged}` — The Printed Work

For papers, books, reports, theses. The output is paginated — content flows across discrete pages with automatic page breaks, page numbers, and margin content. The equivalent of a LaTeX or Typst document.

```quarkdown
.doctype {paged}
.doctitle {On the Geometry of Renaissance Composition}
.docauthor {Giorgio Vasari}
.theme {paperwhite} layout:{latex}
```

### `.doctype {plain}` — The Living Document

A continuous flow layout — no page breaks, no page numbers. Scrolls like a web page or Notion document. Ideal for knowledge bases, notes published as static sites, and reference material.

```quarkdown
.doctype {plain}
.doctitle {Field Notes on Florentine Marble}
.theme {galactic} layout:{hyperlegible}
```

### `.doctype {docs}` — The Technical Reference

A documentation site with a sidebar, table of contents, and multiple navigable sections. Replaces GitBook, MkDocs, VitePress, and Docusaurus. This Quarkdown wiki itself is a `docs` document.

```quarkdown
.doctype {docs}
.doctitle {Quarkdown Reference}
.theme {paperwhite} layout:{minimal}
```

### `.doctype {slides}` — The Presentation

Interactive slides with keyboard navigation. Replaces Beamer and Google Slides. Each heading becomes a slide separator.

```quarkdown
.doctype {slides}
.doctitle {Renaissance Typography for the Modern Age}
.docauthor {Michelangelo Buonarroti}
.theme {beaver} layout:{beamer}
```

-----

## Themes: Marble Grain and Pigment 🎨

Themes in Quarkdown are split into two independent dimensions: **color themes** define the palette; **layout themes** define structural rules. Combine them freely.

```quarkdown
.theme {paperwhite} layout:{latex}
```

### Color Themes

|Color theme |Character                                               |
|------------|--------------------------------------------------------|
|`paperwhite`|Clean white background — classic academic look          |
|`darko`     |Dark background — low-light reading and presentations   |
|`galactic`  |Deep space aesthetic — the theme of the Quarkdown wiki  |
|`beaver`    |Earthy academic tones — common in academic presentations|

### Layout Themes

|Layout theme  |Character                                         |
|--------------|--------------------------------------------------|
|`latex`       |Traditional academic proportions and spacing      |
|`minimal`     |Stripped-back, generous whitespace                |
|`hyperlegible`|Maximally legible typography — accessibility focus|
|`beamer`      |Academic presentation conventions                 |

### Recommended combinations

|Use case          |Combination                   |
|------------------|------------------------------|
|Academic paper    |`paperwhite + latex` (default)|
|Dark-mode reading |`darko + minimal`             |
|Documentation wiki|`galactic + hyperlegible`     |
|Academic talk     |`beaver + beamer`             |

-----

## Document Metadata: The Inscription on the Base 📛

Every finished Renaissance work was inscribed with its title and maker. Quarkdown metadata serves the same function — it also powers the document’s header, footers, bibliographic references, and PDF metadata.

```quarkdown
.doctype {paged}
.doctitle {Meditations on Geometric Form}
.docauthor {Michelangelo Buonarroti}
```

For multiple authors:

```quarkdown
.docauthors
    - Michelangelo Buonarroti
    - Giorgio Vasari
    - Leonardo da Vinci
```

Set the document language (affects hyphenation, date formatting, and localization):

```quarkdown
.doclang {english}
```

-----

## Numbering: The Systematic Grid 📐

The Renaissance master used precise grids to transfer a small *cartone* sketch to the full-scale fresco. Quarkdown’s `.numbering` function applies the same systematic ordering to headings, figures, tables, equations, and code blocks.

```quarkdown
.numbering
    - headings: 1.1.1
    - figures: 1.1
    - tables: 1.1
    - equations: 1
    - code: A.1
```

Valid symbols:

|Symbol             |Format                     |
|-------------------|---------------------------|
|`1`                |Decimal: 1, 2, 3           |
|`A`                |Uppercase letters: A, B, C |
|`a`                |Lowercase letters: a, b, c |
|`I`                |Uppercase Roman: I, II, III|
|`i`                |Lowercase Roman: i, ii, iii|
|Any other character|Literal (separator)        |

So `1.1.1` produces `1.1.1`, `1.1.2`, `1.2.1` etc. The format `A.1` produces `A.1`, `A.2`, `B.1`.

> Documents with `paged` type enable default numbering automatically.

-----

## Table of Contents: The Chapel’s Guide Map 🗺️

A reader approaching the Sistine ceiling for the first time needs a guide. A long document needs a table of contents.

```quarkdown
.numbering
    - headings: 1.1.1
    - figures: 1.1

.tableofcontents

# Introduction

...
```

Place `.tableofcontents` exactly where it should appear in the document — typically before the first section. Quarkdown generates it automatically from all headings, with the numbering applied.

For `docs` type, the table of contents also populates the sidebar navigation.

-----

## Page Margins: The Prophets in the Borders 🖼️

The Sistine ceiling’s border prophets and sibyls are not decoration — they are structural elements that anchor the narrative. Page margin content serves the same purpose: running titles, author names, page numbers, and section references that orient the reader on every page.

```quarkdown
.pagemargin {topright}
    .docauthor | Meditations on Geometric Form

.pagemargin {bottomcenter}
    .pagecounter
```

### Margin positions

|Position      |Description                              |
|--------------|-----------------------------------------|
|`topleft`     |Top-left of every page                   |
|`topcenter`   |Top-centre (classic running title)       |
|`topright`    |Top-right (author name, section title)   |
|`bottomleft`  |Bottom-left                              |
|`bottomcenter`|Bottom-centre (page number — most common)|
|`bottomright` |Bottom-right                             |

### Page counter

```quarkdown
.pagemargin {bottomcenter}
    .pagecounter
```

Produces the current page number. For `Page 3 of 12` style:

```quarkdown
.pagemargin {bottomcenter}
    Page .pagecounter of .pagecount
```

### Persistent headings

In long paged documents, show the current chapter title in the margin:

```quarkdown
.pagemargin {topcenter}
    .currentheading {1}
```

This automatically updates to show the current level-1 heading on each page — the equivalent of a book’s running header.

-----

## Footnotes: The Marginal Annotations 📝

Michelangelo’s preparatory drawings carry extensive marginal notes — technical reminders, material lists, measurements. Footnotes serve the same purpose in documents: supplementary information that would interrupt the main argument but is valuable to a careful reader.

Standard Markdown footnote syntax works in Quarkdown:

```quarkdown
The proportion of the golden ratio[^1] was central to Renaissance composition.

Structural integrity depends on the load-bearing capacity of the marble[^2].

[^1]: The golden ratio φ ≈ 1.618 appears throughout classical and Renaissance architecture.
[^2]: Carrara marble has a compressive strength of approximately 150 MPa.
```

Quarkdown renders footnotes at the bottom of the page in `paged` mode, or at the end of the section in `plain` and `docs` modes.

-----

## A Complete Document Header: The Full Commission Document 📜

Putting it all together — the complete document setup for a formal academic paper:

```quarkdown
.doctype {paged}
.doctitle {On the Mathematical Proportions of the Human Form}
.docauthors
    - Michelangelo Buonarroti
    - Florence, Italy
.doclang {english}
.theme {paperwhite} layout:{latex}

.numbering
    - headings: 1.1.1
    - figures: 1.1
    - tables: 1.1
    - equations: 1

.pagemargin {topright}
    Buonarroti | On the Mathematical Proportions of the Human Form

.pagemargin {bottomcenter}
    .pagecounter

.tableofcontents

# Introduction

The human form, properly understood, is a study in proportion...
```

This header — eighteen lines — produces a document with automatic numbering throughout, a generated table of contents, running headers with the author name, page numbers centred at the bottom, and the paperwhite/latex visual style applied to every element.

-----

## The Book Cover: The Frontispiece 📖

For book-format documents, add a cover page:

```quarkdown
.bookcover
    .doctitle
    .docauthor
    !(80%)[Cover image](img/cover.png)
```

Or use the function to generate a styled cover:

```quarkdown
.doctype {paged}
.doctitle {The Lives of the Artists}
.docauthor {Giorgio Vasari}

.bookcover
```

-----

In **Episode 3**, we study the Pietà — Michelangelo’s most formally perfect work. The function call syntax, block vs. inline calls, chaining, and the art of writing custom functions that become compositional building blocks.

-----

**🔗 Resources**

- **Document types**: [quarkdown.com/wiki/document-types](https://quarkdown.com/wiki/document-types)
- **Themes**: [quarkdown.com/wiki/themes](https://quarkdown.com/wiki/themes)
- **Document metadata**: [quarkdown.com/wiki/document-metadata](https://quarkdown.com/wiki/document-metadata)
- **Table of contents**: [quarkdown.com/wiki/table-of-contents](https://quarkdown.com/wiki/table-of-contents)
- **Page margin content**: [quarkdown.com/wiki/page-margin-content](https://quarkdown.com/wiki/page-margin-content)
- **Numbering**: [quarkdown.com/wiki/numbering](https://quarkdown.com/wiki/numbering)

-----

*✍️ Michelangelo on Markdown Series — crafting beautiful documents with Quarkdown and Tolaria, through the lens of the Renaissance master’s studio.*
