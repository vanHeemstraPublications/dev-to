---
title: "Michelangelo on Markdown ✍️ Ep.3"
part: 2
published: false
description: "Episode 3: The Pietà is technically perfect — every fold of cloth, every muscle, every proportion studied and mastered. Quarkdown’s function call syntax is the same discipline: a precise grammar for calling built-in functions, chaining operations, declaring variables, and building custom reusable elements. Learn the language of the chisel."
tags: [quarkdown, markdown, functions, scripting]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/michelangelo_on_markdown_series/michelangelo-on-markdown-episode-03.png"
series: "Michelangelo on Markdown Series"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 3: The Perfect Form

> *“The true work of art is but a shadow of the divine perfection.”*
> — Michelangelo Buonarroti

-----

## The Grammar of the Chisel 🪨

The Pietà has no wasted material. Every surface is purposeful. Every fold of the Virgin’s robe was studied and reshaped until it served both the structural and the emotional composition. The form was not discovered by accident — it was achieved through a mastery of technique applied with consistent discipline.

Quarkdown’s function call syntax is that technical discipline. It extends Markdown with a precise, consistent grammar for calling functions: built-in ones that Quarkdown provides (`.align`, `.row`, `.box`, `.sqrt`, `.tableofcontents`) and custom ones you declare for your own documents. Master the syntax once and it works uniformly across every function in the entire standard library.

-----

## 🗂️ SIPOC — The Perfect Form

|**Suppliers**                 |**Inputs**                                            |**Process**                                                                                |**Outputs**                                                                      |**Customers**                                                                         |
|------------------------------|------------------------------------------------------|-------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
|Quarkdown standard library    |Function name, positional arguments, named arguments  |Parser identifies `.name {arg} named:{arg}` pattern → function expansion during compilation|The function’s output substituted in place                                       |The rendered document — function calls are invisible; their output is all that remains|
|Author (declaring `.function`)|A body of Quarkdown markup with parameter placeholders|Compiler stores the function definition; subsequent calls expand it                        |A reusable element: box, card, callout, example — applied consistently throughout|Document consistency — the same element, perfectly reproduced, every time             |
|Chaining operator `::`        |A function call producing output                      |`output::next_function` — output of first becomes first argument of second                 |Composed transformations in a single expression                                  |Complex operations expressed cleanly on one line                                      |

-----

## Function Call Syntax: The Grammar 📐

Every Quarkdown function call starts with a dot followed by the function name. Arguments are wrapped in curly braces. Named arguments use `named:{value}` syntax.

```quarkdown
.functionname {positional_arg} named_arg:{value}
```

### Positional arguments

```quarkdown
The square root of 144 is .sqrt {144}.

Raise 5 to the power of 3: .pow {5} to:{3}
```

Output: “The square root of 144 is 12.”

### Named arguments

Named arguments can appear in any order:

```quarkdown
.pow {5} to:{3}
.pow to:{3} {5}
```

Both produce the same result.

-----

## Inline vs. Block Calls: The Mark and the Panel 🖼️

Function calls can be **inline** (within text) or **block** (standalone, separated by blank lines).

### Inline calls

Appear within a paragraph — their output flows with the text:

```quarkdown
The result is .multiply {6} by:{7} — a perfect number for composition.

For contrast, consider the golden ratio: $ \phi = \frac{1 + \sqrt{5}}{2} \approx 1.618 $
```

### Block calls

Stand alone, separated by blank lines. Block calls also support an **indented block argument** — the last parameter of the function, provided as indented content below the call:

```quarkdown
.align {center}
    This paragraph is the block argument.
    It is centred in the document.

.box {Important Note} type:{warning}
    This content appears inside a highlighted warning box.
    The warning box is the block argument.
```

The block argument is always the last parameter. It receives everything indented below the function call at one level of indentation.

-----

## Chaining Calls: The Renaissance Master’s Compound Technique `::` 🔗

The `::` operator chains calls — the output of one function becomes the first argument of the next. This is Quarkdown’s equivalent of a pipeline or method chaining.

```quarkdown
.sqrt {10}::round::multiply {2}
```

This computes: `sqrt(10)` = 3.1622… → `round(3.1622)` = 3 → `multiply(3, 2)` = **6**.

Chaining makes complex transformations readable:

```quarkdown
.filetext {data.csv}::csv::table
```

This reads a CSV file → parses it as CSV data → renders it as a table. Three operations, one line.

```quarkdown
.range {1} to:{10}::map
    lambda: n:
    .pow {.n} to:{2}
```

This generates the range 1–10, then maps over it with a lambda that squares each value.

-----

## Variables: The Master’s Named Materials 📦

Define a variable with `.var` and access it by calling it like a function:

```quarkdown
.var {author_name} {Michelangelo Buonarroti}
.var {institution}  {Accademia di Belle Arti}

This work is submitted by .author_name from the .institution.
```

Update a variable’s value by calling it with a new argument:

```quarkdown
.var {chapter} {Introduction}

The current chapter is .chapter.

.chapter {Methodology}

Now the current chapter is .chapter.
```

Variables are **dynamically typed** — Quarkdown infers the type from the value. A variable holding `{42}` is a number; one holding `{true}` is a boolean; one holding a multi-line block argument becomes Markdown content.

-----

## Custom Functions: The Preparatory Cartoon 📄

Michelangelo’s *cartone* — the full-scale preparatory drawing — was transferred to the ceiling, used to stamp the composition exactly where planned. Custom Quarkdown functions are the *cartone*: define a pattern once, stamp it as many times as needed.

### Declaring a function

```quarkdown
.function {example}
    content:
    .box {Example} type:{tip}
        .content
```

Now call it:

```quarkdown
.example
    The golden ratio governs the proportions of the Parthenon.
```

The function expands to a styled tip box containing the provided content. Every time `.example` appears in the document, it produces the identical, consistent element.

### Multiple parameters

Parameters are declared with names separated by spaces, followed by colons for named parameters:

```quarkdown
.function {definition}
    term content:
    .box {.term} type:{note}
        .content
```

```quarkdown
.definition {Contrapposto}
    A sculptural technique where the human figure is posed with most of
    the weight on one foot, creating a slight twist of the torso.

.definition {Sfumato}
    Leonardo's technique of softening contours through imperceptible
    gradations of tone.
```

Each produces a styled note box with the term as the title and the definition as the content.

### Functions with computed content

Functions can contain calculations, conditions, and other function calls:

```quarkdown
.function {status_badge}
    level color:
    .container
        .text {.level} color:{.color} weight:{bold}
        **Level .level**
```

```quarkdown
The marble quality is .status_badge {Superior} color:{#2d6a4f}.
The workmanship is .status_badge {Master} color:{#1d3557}.
```

-----

## Built-In Boxes: The Callout Frames 📋

Quarkdown provides a `.box` function that creates visually styled content boxes — the callout frames of academic writing:

```quarkdown
.box {Theorem 1.1} type:{note}
    For any right triangle with legs *a* and *b* and hypotenuse *c*,
    $ a^2 + b^2 = c^2 $

.box {Warning} type:{warning}
    Do not attempt to quarry Carrara marble without proper surveying.
    Structural failures have caused fatalities.

.box {Tip} type:{tip}
    Begin with the largest forms before working toward detail.
    The overall composition must be sound before surface refinement begins.

.box {Error} type:{error}
    The calculation used the wrong datum. Results are invalid.
```

### Box types

|Type     |Visual treatment    |Typical use                        |
|---------|--------------------|-----------------------------------|
|`note`   |Blue accent         |Definitions, theorems, key concepts|
|`tip`    |Green accent        |Best practices, helpful hints      |
|`warning`|Orange/yellow accent|Cautions, prerequisites            |
|`error`  |Red accent          |Critical issues, known limitations |

-----

## Text Formatting: Beyond Standard Markdown ✍️

Quarkdown adds text formatting controls beyond standard Markdown:

```quarkdown
.text {Extraordinary} weight:{bold} color:{#c0392b} size:{1.4em}

.text {delicate surfaces} style:{italic} decoration:{underline}
```

Explicit line breaks (Markdown’s double-space trick, but reliable):

```quarkdown
First line.
.linebreak
Second line begins directly below.
```

Decorative headings that do not appear in the table of contents:

```quarkdown
.heading {Interlude} level:{3} decoration:{true}
```

-----

## The Standard Library: The Master’s Toolbox 🔧

The complete Quarkdown standard library is documented at [quarkdown.com/docs/quarkdown-stdlib](https://quarkdown.com/docs/quarkdown-stdlib). Key categories:

**Mathematics:** `.sqrt`, `.pow`, `.log`, `.abs`, `.round`, `.floor`, `.ceil`, `.multiply`, `.divide`, `.add`, `.subtract`, `.mod`

**Text and string:** `.text`, `.uppercase`, `.lowercase`, `.length`, `.substr`, `.replace`

**Document structure:** `.tableofcontents`, `.numbering`, `.pagecounter`, `.pagecount`, `.pagemargin`, `.align`, `.heading`

**Layout:** `.row`, `.column`, `.grid`, `.container`, `.box`, `.clip`, `.float`

**Data:** `.csv`, `.table`, `.filetext`, `.range`, `.foreach`, `.map`, `.filter`

All of these follow the same syntax — `.name {arg} named:{arg}` — which means mastering the syntax pattern mastery carries to every function.

-----

In **Episode 4**, we move from the Pietà’s formal perfection to the Medici Tombs’ integration of sculpture and architecture. Layout in Quarkdown: rows, columns, grids, containers, alignment, figures, image sizing, and TeX formulae.

-----

**🔗 Resources**

- **Function call syntax**: [quarkdown.com/wiki/syntax-of-a-function-call](https://quarkdown.com/wiki/syntax-of-a-function-call)
- **Declaring functions**: [quarkdown.com/wiki/declaring-functions](https://quarkdown.com/wiki/declaring-functions)
- **Variables**: [quarkdown.com/wiki/variables](https://quarkdown.com/wiki/variables)
- **Boxes**: [quarkdown.com/wiki/box](https://quarkdown.com/wiki/box)
- **Standard library docs**: [quarkdown.com/docs/quarkdown-stdlib](https://quarkdown.com/docs/quarkdown-stdlib)

-----

*✍️ Michelangelo on Markdown Series — crafting beautiful documents with Quarkdown and Tolaria, through the lens of the Renaissance master’s studio.*
