---
title: "Code Smell Detective Solves Gilded Rose Kata"
published: false
description: "A systematic approach to solving the Gilded Rose refactoring kata by identifying and fixing code smells one by one"
tags: ["python", "refactoring", "codesmells", "tutorial"]
series: ""
canonical_url: ""
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/windows-1694867_1920.jpg"
organization: "the-software-s-journey"
---

The [Gilded Rose refactoring kata](https://github.com/emilybache/GildedRose-Refactoring-Kata) is a classic coding exercise that challenges developers to refactor legacy code while adding new functionality. Instead of jumping straight to a design pattern, let's take a methodical approach: **identify code smells and fix them systematically**.

In this article, I'll walk you through solving the Gilded Rose kata by acting as the Code Smell Detective—identifying each smell, understanding its impact, and refactoring it step by step. By the end, you'll have a clean, maintainable solution and a better understanding of how to approach legacy code refactoring. Note that I've previously published a solution to this kata using [composition over inheritance](https://dev.to/the-software-s-journey/the-gilded-rose-kata-composition-over-inheritance-537p), which manually applies the Strategy pattern. This article takes a different approach by using automated code smell detection to guide our refactoring process.

Credit to [Emily Bache's GitHub repository](https://github.com/emilybache?tab=repositories&q=kata&type=&language=&sort=) for the excellent kata resources.

## The Problem

Here's the legacy code we need to refactor:

```python
class GildedRose(object):
    def __init__(self, items):
        self.items = items

    def update_quality(self):
        for item in self.items:
            if item.name != "Aged Brie" and item.name != "Backstage passes to a TAFKAL80ETC concert":
                if item.quality > 0:
                    if item.name != "Sulfuras, Hand of Ragnaros":
                        item.quality = item.quality - 1
            else:
                if item.quality < 50:
                    item.quality = item.quality + 1
                    if item.name == "Backstage passes to a TAFKAL80ETC concert":
                        if item.sell_in < 11:
                            if item.quality < 50:
                                item.quality = item.quality + 1
                        if item.sell_in < 6:
                            if item.quality < 50:
                                item.quality = item.quality + 1
            if item.name != "Sulfuras, Hand of Ragnaros":
                item.sell_in = item.sell_in - 1
            if item.sell_in < 0:
                if item.name != "Aged Brie":
                    if item.name != "Backstage passes to a TAFKAL80ETC concert":
                        if item.quality > 0:
                            if item.name != "Sulfuras, Hand of Ragnaros":
                                item.quality = item.quality - 1
                    else:
                        item.quality = item.quality - item.quality
                else:
                    if item.quality < 50:
                        item.quality = item.quality + 1


class Item:
    def __init__(self, name, sell_in, quality):
        self.name = name
        self.sell_in = sell_in
        self.quality = quality

    def __repr__(self):
        return "%s, %s, %s" % (self.name, self.sell_in, self.quality)
```

The task is to:

- Refactor this nested conditional nightmare
- Add support for "Conjured" items that degrade twice as fast
- Cannot modify the `Item` class
- Cannot modify the `items` property

## The Code Smell Detective Approach

Instead of immediately reaching for design patterns, let's systematically identify and fix code smells. This approach helps us understand *why* the code is problematic before deciding *how* to fix it.

### Step 1: Identify the Code Smells

Before we start refactoring, let's use the [code-smell-detector](https://github.com/code-smell-detective/code-smell-detective) tool—the Code Smell Detective's automated analysis tool—to systematically identify all code smells in the Gilded Rose code. This automated analysis will give us a comprehensive view of what needs to be fixed.

The `code-smell-detector` is a Python application that performs static analysis on codebases, detecting code smells based on configurable thresholds. It analyzes metrics like cyclomatic complexity, nesting depth, lines of code, and more. Think of it as the Code Smell Detective's trusty sidekick that helps identify problems before we dive into fixing them.

#### Setting Up the Gilded Rose Code

First, let's set up the code we'll be analyzing. Create a new directory called `gilded-rose-kata`:

```bash
mkdir gilded-rose-kata
cd gilded-rose-kata
```

Then create `gilded_rose.py` and copy all the code from the code block in "The Problem" section above (both the `GildedRose` and `Item` classes). Note that `GildedRose` takes a list of `Item` objects via the `items` parameter in its constructor—this is the `items` property that we cannot modify according to the kata constraints.

#### Installing the Code Smell Detector

First, we need to download and install the tool. Head over to the [Code Smell Detective releases page](https://github.com/code-smell-detective/code-smell-detective/releases) and download the latest release. Once you've extracted the codebase, navigate to the directory and install it:

```bash
cd code-smell-detective
pip install -e .
```

This installs the `code-smell-detector` command-line tool in editable mode, so you can use it from anywhere on your system.

#### Running the Analysis

Now let's run it on our Gilded Rose code. Make sure you're in a directory above `gilded-rose-kata` (not inside it). The config file `code_smell_config.yaml` is located in the `code-smell-detective/code_smell_detector/samples/` directory. You can either:

1. Run the command from the `code-smell-detective` directory:
```bash
cd code-smell-detective
code-smell-detector analyze ../gilded-rose-kata --config code_smell_detector/samples/code_smell_config.yaml
```

2. Or use the full path to the config file from wherever you are:
```bash
code-smell-detector analyze ./gilded-rose-kata --config /path/to/code-smell-detective/code_smell_detector/samples/code_smell_config.yaml
```

Note: The `code-smell-detector` analyzes entire directories, so we point it to the directory containing our `gilded_rose.py` file.

Here's what the detector found:

#### Analysis Results

**Health Score: 15/100** (Critical - needs immediate attention)

**Detected Smells:**

1. **Long Method** (HIGH severity)
   - Location: `GildedRose.update_quality()` (lines 8-36)
   - Metrics:
     - Lines of Code: 28 (threshold: 20)
     - Cyclomatic Complexity: 12 (threshold: 10)
     - Max Nesting Depth: 5 (threshold: 3)
   - SOLID Violations: SRP (Single Responsibility Principle)
   - Recommended Patterns: Extract Method, Template Method, Strategy
   - Description: The `update_quality` method is doing too much—it handles multiple item types with different rules all in one place.

2. **Complex Conditional** (CRITICAL severity)
   - Location: `GildedRose.update_quality()` (lines 8-36)
   - Metrics:
     - Max Nesting Depth: 5 (threshold: 3)
     - Conditional Branches: 11
     - Boolean Operators: 4
   - SOLID Violations: OCP (Open/Closed Principle)
   - Recommended Patterns: Strategy, State, Chain of Responsibility, Specification
   - Description: Deeply nested conditionals make the code hard to understand and extend. Adding new item types requires modifying this method.

3. **Duplicated Code** (MEDIUM severity)
   - Location: Multiple locations
   - Metrics:
     - Duplicate blocks: 3 instances
     - Pattern: Repeated checks for `item.name != "Sulfuras, Hand of Ragnaros"`
   - SOLID Violations: DRY (Don't Repeat Yourself)
   - Recommended Patterns: Extract Method
   - Description: The same conditional check appears multiple times throughout the method.

#### Summary Table

| Smell | Severity | Location | Key Metric | SOLID Violation |
|-------|----------|----------|------------|-----------------|
| Long Method | HIGH | `update_quality()` | 28 LOC, CC: 12 | SRP |
| Complex Conditional | CRITICAL | `update_quality()` | Nesting: 5 levels | OCP |
| Duplicated Code | MEDIUM | Multiple | 3 duplicate blocks | DRY |

#### What This Tells Us

The automated analysis confirms what we can see with our eyes: the `update_quality` method is a code smell factory! The critical issues are:

1. **Too many responsibilities**: The method handles normal items, Aged Brie, Backstage passes, and Sulfuras all in one place
2. **Impossible to extend**: Adding "Conjured" items will make this worse
3. **Hard to test**: The nested conditionals make it difficult to test all code paths
4. **Violates Open/Closed Principle**: We must modify the method to add new item types

Now that we have the Code Smell Detective's report, let's start fixing these smells systematically, starting with the most critical one.

### Step 2: Fix the First Smell

[Your content here - fix the first identified smell with code examples]

### Step 3: Continue the Investigation

[Your content here - continue identifying and fixing smells]

### Step 4: Extract Methods

[Your content here - show how to extract methods to reduce complexity]

### Step 5: Replace Conditional with Polymorphism

[Your content here - show the final refactoring step]

## The Refactored Solution

Here's the complete refactored solution:

```python
# [Your complete solution code here]
```

## Key Takeaways

The Code Smell Detective approach teaches us:

1. **Start with smells, not solutions**: Identify problems before choosing patterns
2. **Refactor incrementally**: Fix one smell at a time, test, then move on
3. **Understand the why**: Each smell has a reason and a fix
4. **Test-driven refactoring**: Ensure behavior doesn't change as you refactor

## Common Code Smells Found

| Smell | Description | Impact |
|-------|-------------|--------|
| Long Method | Method exceeds 20 LOC with high cyclomatic complexity | Makes code hard to understand, test, and maintain |
| Complex Conditional | Deep nesting (5 levels) with 11 conditional branches | Violates OCP, makes extension difficult |
| Duplicated Code | Repeated conditional checks throughout the method | Violates DRY, increases maintenance burden |

## Conclusion

By systematically identifying and fixing code smells, we transformed a complex, nested conditional nightmare into clean, maintainable code. The Code Smell Detective approach ensures we understand the problems before applying solutions, leading to better refactoring decisions.

The next time you encounter legacy code, put on the Code Smell Detective's hat: identify the smells, understand their impact, and fix them one by one. Your future self (and your teammates) will thank you.

## Resources

- [Gilded Rose Kata on GitHub](https://github.com/emilybache/GildedRose-Refactoring-Kata)
- [:octocat: Code Smell Detective](https://github.com/code-smell-detective/code-smell-detective)
- [Refactoring: Improving the Design of Existing Code](https://refactoring.com/)
- [Code Smells Catalog](https://refactoring.guru/refactoring/smells)

Happy refactoring, and remember: be a Code Smell Detective, not just a pattern matcher!

*What code smells have you encountered in legacy code? How did you approach fixing them? I'd love to hear your detective stories in the comments!*

