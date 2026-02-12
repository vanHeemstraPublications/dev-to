# Story-Driven Design Pattern Template

This directory contains a reusable prompt template for explaining
software design patterns using storytelling principles inspired by
Robert McKee.

The goal is to make design patterns:

-   Easier to understand
-   Easier to remember
-   More engaging to teach
-   Consistent across articles, slides, and talks

Instead of only explaining patterns in technical terms, this template
connects them to:

-   Short metaphorical stories
-   Well-known fictional examples
-   Screenwriting structure
-   Real-world software use cases
-   Minimal Python code

------------------------------------------------------------------------

## Why use this template?

Design patterns are essentially **recurring structural stories** in
software:

  Storytelling   Software
  -------------- ----------------------
  Protagonist    Main class/object
  Goal           Pattern intent
  Conflict       Problem being solved
  Resolution     Pattern structure
  Theme          Pattern philosophy

By framing patterns as stories, readers can understand the *why* behind
the pattern, not just the *how*.

------------------------------------------------------------------------

## How to use the template

1.  Open `STORY_TEMPLATE.md`.
2.  Copy the prompt text.
3.  Replace `{Design Pattern}` with the pattern you want.
4.  Paste it into ChatGPT.
5.  Use the generated output in your article, slides, or documentation.

------------------------------------------------------------------------

## Example

Prompt:

    Explain the Singleton design pattern using the template.

The response will include:

-   One-line intent
-   Short story metaphor
-   Fictional example
-   Robert McKee story elements
-   Real-world implementations
-   Python code sample

------------------------------------------------------------------------

## When to use this template

Use it when:

-   Writing educational articles
-   Creating conference talks
-   Teaching junior developers
-   Building documentation
-   Creating visual or story-based learning materials

------------------------------------------------------------------------

## Customizing the template

You can easily adapt the prompt by adding constraints, for example:

### Themed stories

    Explain the Observer pattern using the template,
    but set the story in a wizard school.

### Beginner-friendly version

    Explain the Factory Method pattern for beginner developers
    using the template.

### Slide-friendly version

    Explain the Strategy pattern using the template,
    keep all sections under 2 sentences.

------------------------------------------------------------------------

## Files in this directory

  File                  Purpose
  --------------------- ----------------------------
  `README.md`           How to use the template
  `STORY_TEMPLATE.md`   The actual prompt template

------------------------------------------------------------------------

## License

Use freely in articles, talks, courses, or documentation.
