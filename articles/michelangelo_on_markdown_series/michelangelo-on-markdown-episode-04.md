-----

## title: “Michelangelo on Markdown! Ep.4: Stone and Space”
published: false
description: “Episode 4: The Medici Tombs integrate sculpture and architecture — the figures of Dawn, Dusk, Day, and Night do not decorate the space, they ARE the space. Quarkdown’s layout system works the same way: rows, columns, grids, containers, alignment, float, clip, figures with captions, image sizing, and TeX formulae are not decorations — they ARE the document structure.”
tags: [quarkdown, markdown, layout, design]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/michelangelo-markdown-episode-04.png”
series: “Michelangelo on Markdown Series”
canonical_url: “”
organization: “the-software-s-journey”
part: 1

# Michelangelo on Markdown! ✍️

## Episode 4: Stone and Space

> *“In every block of marble I see a statue as plain as though it stood before me, shaped and perfect in attitude and action.”*
> — Michelangelo Buonarroti

-----

## When Structure and Content Are One 🏛️

The Medici Tombs in the Sacrestia Nuova of San Lorenzo are not sculptures placed in a room. They are sculptures that are the room. The figures of Dawn and Dusk, Day and Night, rest on sarcophagi that are architectural elements of the walls. Remove the sculptures and the architectural programme collapses. The layout and the content are identical.

Quarkdown’s layout system has the same integration. A `.row` with two columns containing a figure and a description is not a styled container around content — it is the content itself, positioned and related. A `.float` element allows text to flow around an image the same way text flows around a stone figure in an illuminated manuscript. Layout is not cosmetic. Layout is meaning.

-----

## 🗂️ SIPOC — Stone and Space

|**Suppliers**   |**Inputs**                                                     |**Process**                                                                                 |**Outputs**                                                       |**Customers**                                                                  |
|----------------|---------------------------------------------------------------|--------------------------------------------------------------------------------------------|------------------------------------------------------------------|-------------------------------------------------------------------------------|
|Author          |Content to be positioned: text, images, formulae, code, tables |Layout function calls: `.row`, `.column`, `.grid`, `.align`, `.float`, `.clip`, `.container`|Elements positioned according to the layout definition            |Readers who perceive structure and spatial relationships in the rendered output|
|Images / figures|Image files referenced in `!(size)[alt](path "caption")` syntax|Quarkdown renders isolated images as figures with captions; inline images flow with text    |Centred, captioned figures with automatic numbering (when enabled)|Academic readers who need captioned, numbered figures                          |
|TeX expressions |`$ expression $` inline; standalone equations become block     |MathJax rendering — inline in text or centred as display equations                          |Beautifully typeset mathematical notation                         |Technical and scientific document readers                                      |

-----

## Image Sizing: The Controlled Proportion !(W)[alt](src) 📐

Standard Markdown images have a fundamental problem: no size control. The image renders at its natural dimensions, often too large.

Quarkdown fixes this with a size prefix:

```quarkdown
!(50%)[The David](img/david.jpg)
```

The exclamation mark, followed by the size in parentheses, controls the width while maintaining the aspect ratio.

### Supported units

|Unit|Example   |Meaning                               |
|----|----------|--------------------------------------|
|`%` |`!(50%)`  |Percentage of available width         |
|`px`|`!(400)`  |Pixels (also default if no unit given)|
|`cm`|`!(12cm)` |Centimetres                           |
|`mm`|`!(120mm)`|Millimetres                           |
|`pt`|`!(32pt)` |Points                                |
|`in`|`!(4in)`  |Inches                                |

### Width and height

Specify both dimensions:

```quarkdown
!(12cm 8cm)[Sistine ceiling detail](img/sistine.jpg)
```

Specify only height (auto width):

```quarkdown
!(_ 6cm)[Portrait of Vittoria Colonna](img/colonna.jpg)
```

-----

## Figures and Captions: The Numbered Illustration 🖼️

When an image is separated from other content by blank lines, Quarkdown automatically treats it as a **figure** — centred, potentially numbered, and captionable.

Add a caption by appending it as the title attribute in quotes:

```quarkdown
!(70%)[The David](img/david.jpg "Michelangelo, David, 1501–1504, Carrara marble,
height 5.17m. Accademia Gallery, Florence.")
```

With `.numbering` enabled:

```quarkdown
.numbering
    - figures: 1.1
```

The figure becomes “Figure 1.1: Michelangelo, David, …” — automatically numbered and cross-referenceable.

-----

## Alignment: Placing the Figure Precisely 📏

```quarkdown
.align {center}
    This text is centred.

.align {right}
    This text aligns to the right margin.

.align {left}
    This text aligns to the left margin — the default.
```

For block content — figures, formulae, quotations — centring is the most common choice:

```quarkdown
.align {center}
    !(40%)[Sketch for the Sistine ceiling](img/sketch.jpg "Preparatory drawing, c. 1508")
```

-----

## Float: Text Flowing Around the Form 📖

The `.float` function allows content to float — text flows around it, as in a magazine layout or an illuminated manuscript:

```quarkdown
.float {left}
    !(35%)[Carrara marble quarry](img/quarry.jpg)

Carrara marble has been quarried since Roman times. The quarries in the Apuan Alps
produce a white marble of exceptional purity and workability. Michelangelo visited
the quarries personally to select the blocks for his major commissions...
```

The image floats left; the paragraph text wraps around its right side.

```quarkdown
.float {right}
    !(30%)[Bronze casting method](img/casting.jpg "Lost-wax casting process")

The lost-wax casting process (*cire perdue*) allows for extraordinary surface detail.
The sculptor first creates a model in wax over a clay core...
```

-----

## Stacks: The Compositional Grid 🏗️

Stacks are Quarkdown’s core layout primitives — they arrange content in rows, columns, and grids.

### `.row` — Horizontal arrangement

```quarkdown
.row
    !(45%)[Dawn](img/dawn.jpg "Dawn, Medici tombs")
    !(45%)[Dusk](img/dusk.jpg "Dusk, Medici tombs")
```

Two figures side by side. Each takes 45% of the width, with a small gap between.

### `.column` — Vertical stack

```quarkdown
.column
    # Primary Heading
    ## Secondary Heading
    The content below the headings.
```

### `.grid` — The full compositional grid

```quarkdown
.grid columns:{3}
    !(100%)[Dawn](img/dawn.jpg)
    !(100%)[Dusk](img/dusk.jpg)
    !(100%)[Day](img/day.jpg)
    !(100%)[Night](img/night.jpg)
    *(Four Seasons of a Life)*
    *(Medici Chapel, 1520–1534)*
```

Four images in a three-column grid, with two text cells in the second row.

### Named parameters for spacing

```quarkdown
.row gap:{1.5cm}
    .column
        **Name:** Michelangelo Buonarroti
        **Born:** 1475, Caprese
        **Died:** 1564, Rome

    .column
        **Specialties:** sculpture, painting, architecture, poetry
        **Patrons:** Medici family, Pope Julius II, Pope Paul III
```

-----

## Container: The Frame 🖼️

The `.container` function wraps content with specific width and padding:

```quarkdown
.container width:{60%} padding:{1em}
    This is a contained block. It occupies 60% of the available width
    and has padding on all sides.
```

Combined with `.align {center}`:

```quarkdown
.align {center}
    .container width:{70%}
        > The goal of the artist is not the mastery of technique
        > but the expression of truth through technique.
```

-----

## Clip: The Shaped Frame 🔵

The `.clip` function applies a shape mask to its content:

```quarkdown
.clip {circle}
    !(100%)[Portrait of Michelangelo](img/portrait.jpg)
```

Available shapes: `circle`, `rounded` (for rectangular content with rounded corners).

This is particularly useful for author portraits, team photos in documentation, and medallion-style illustrations.

-----

## Collapsible: The Hidden Room 🚪

For long documents, collapsible sections prevent visual overload while keeping content accessible:

```quarkdown
.collapsible {Technical Appendix: Marble Composition Analysis}
    The chemical composition of Carrara marble (Calacatta bianco):
    - CaCO₃: 97–99%
    - MgCO₃: 0.5–1.5%
    - Fe₂O₃: trace amounts
    - SiO₂: trace amounts

    These proportions contribute to the marble's characteristic whiteness
    and workability.
```

In rendered output, this appears as a clickable heading that expands to reveal the content.

-----

## TeX Formulae: The Mathematical Notation 🧮

Quarkdown renders TeX equations through MathJax — the standard for mathematical typesetting on the web.

### Inline equations

Surrounded by `$ ... $` with whitespace:

```quarkdown
The golden ratio is $ \phi = \frac{1 + \sqrt{5}}{2} \approx 1.618 $ and appears
throughout classical architecture.

Einstein's mass-energy equivalence: $ E = mc^2 $.
```

### Display equations

An equation separated from other content by blank lines automatically becomes a centred display equation:

```quarkdown
The area of a circle with radius $ r $ satisfies:

$ A = \pi r^2 $

This relationship was understood in antiquity.
```

### Numbered equations

With numbering enabled:

```quarkdown
.numbering
    - equations: 1
```

Each isolated equation receives a number: **(1)**, **(2)**, etc. — cross-referenceable with standard reference syntax.

-----

## A Complete Compositional Example: The Scholar’s Page 📄

Bringing layout together — a typical page from an academic paper with all layout elements:

```quarkdown
## Proportional Systems in Renaissance Sculpture

The Vitruvian system of proportions[^1] — as codified by Alberti and applied by
Michelangelo — holds that the ideal human figure is eight head-heights tall.

.float {right}
    .container width:{40%}
        !(100%)[Vitruvian Man](img/vitruvian.jpg "Leonardo da Vinci, c. 1490")

This proportion derives from the geometric relationship between the square and
the circle, expressed mathematically as:

$ H = 8h $

where $ H $ is total standing height and $ h $ is the height of the head from
chin to crown.

### Visual Comparison: Dawn and Night

.row gap:{1cm}
    .column
        !(100%)[Dawn](img/dawn.jpg "Dawn, 1524–1531")
        The figure leans forward with the left arm raised.

    .column
        !(100%)[Night](img/night.jpg "Night, 1526–1531")
        The figure rests with the head bowed downward.

.box {Observation} type:{note}
    Both figures demonstrate the *contrapposto* principle — the weight
    concentrated on one side creates a serpentine visual rhythm that
    leads the eye across the composition.

[^1]: Vitruvius Pollio, *De architectura*, c. 30–15 BCE. Book III, Chapter 1.
```

-----

In **Episode 5**, we face the Last Judgement — the most complex work. Quarkdown’s scripting system: variables, conditionals, loops, math operations, data tables from CSV, and charts.

-----

**🔗 Resources**

- **Stacks (rows, columns, grids)**: [quarkdown.com/wiki/stacks](https://quarkdown.com/wiki/stacks)
- **Container**: [quarkdown.com/wiki/container](https://quarkdown.com/wiki/container)
- **Figures and image size**: [quarkdown.com/wiki/figure](https://quarkdown.com/wiki/figure)
- **Float**: [quarkdown.com/wiki/float](https://quarkdown.com/wiki/float)
- **Clip**: [quarkdown.com/wiki/clip](https://quarkdown.com/wiki/clip)
- **TeX formulae**: [quarkdown.com/wiki/tex-formulae](https://quarkdown.com/wiki/tex-formulae)

-----

*✍️ Michelangelo on Markdown Series — crafting beautiful documents with Quarkdown and Tolaria, through the lens of the Renaissance master’s studio.*
