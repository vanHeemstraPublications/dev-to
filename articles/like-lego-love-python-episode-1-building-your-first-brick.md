---
title: "Like LEGO? Love Python! 🧱🐍"
published: false
description: "Learn Python classes through the lens of LEGO bricks - because object-oriented programming is just building blocks with extra steps"
tags: [python, beginners, tutorial, oop]
cover_image: https://raw.githubusercontent.com/vanHeemstraSystems/learning-python-object-oriented/main/assets/lego-python-cover.png
series: "Like LEGO? Love Python!"
cover_image: ""
canonical_url: https://dev.to/vanheemstrasystems/like-lego-love-python-episode-1-building-your-first-brick
organization: "the-software-s-journey"
---

## Episode 1: Building Your First Brick (Defining Classes)

Remember when you were a kid and got your first LEGO set? That moment of pure possibility, staring at a pile of colorful bricks, the instruction manual mocking you with its deceptively simple Step 1?

Well, buckle up, because Python classes are basically LEGO instruction manuals that you get to write yourself. Except instead of losing the tiny pieces in your carpet, you’ll lose them in your codebase. Progress!

### The Blueprint Before the Brick

In LEGO-land, someone at corporate HQ designs the molds for each brick type. A 2x4 red brick isn’t just *a* brick - it’s one of potentially thousands of identical 2x4 red bricks, all stamped from the same master design.

Python classes work exactly the same way (minus the Danish engineering precision):

```python
class LegoBrick:
    """Our master blueprint for LEGO bricks"""
    pass
```

Congratulations! You’ve just designed… absolutely nothing useful. It’s the LEGO equivalent of a smooth 1x1 tile - technically a brick, practically useless for building anything interesting.

### Adding the Studs (Attributes)

Real LEGO bricks have characteristics: color, size, those satisfying little studs on top. In Python, we call these **attributes**, and we define them in a special method called `__init__()` - which I pronounce as “dunder init” because saying “double underscore” repeatedly makes me sound like a malfunctioning robot.

```python
class LegoBrick:
    def __init__(self, color, length, width):
        self.color = color
        self.length = length
        self.width = width
        self.studs = length * width  # Auto-calculate studs!
```

**What’s happening here?**

- `self` is Python’s way of saying “this specific brick we’re building right now” (more on this later)
- We’re giving each brick a color, dimensions, and calculating its studs
- The `__init__()` method runs automatically when we create a new brick (like injection molding in the factory)

### Actually Building Some Bricks (Creating Instances)

Now the fun part - let’s manufacture some actual bricks:

```python
my_red_brick = LegoBrick("red", 2, 4)
my_blue_brick = LegoBrick("blue", 2, 2)
my_weird_green_brick = LegoBrick("green", 1, 8)  # That one piece nobody uses
```

Each of these is an **instance** of our `LegoBrick` class - a real, tangible brick stamped from our blueprint. They all share the same structure (color, length, width, studs) but have different values.

### The Mysterious `self` Revealed

Here’s where it gets slightly mind-bendy: when Python runs `my_red_brick = LegoBrick("red", 2, 4)`, it:

1. Creates a new, blank brick object
1. Automatically passes that brick as `self` to `__init__()`
1. You only provide the other arguments (color, length, width)

So `self` is literally “yourself” from the brick’s perspective. It’s like each brick has a tiny internal monologue: “I am red, I am 2 units long, I am 4 units wide…”

### Giving Your Bricks Behaviors (Methods)

LEGO bricks don’t just sit there (well, mostly they do, but work with me). They can *do* things - like snap together, or hide under your foot at 3 AM. Let’s add some behaviors:

```python
class LegoBrick:
    def __init__(self, color, length, width):
        self.color = color
        self.length = length
        self.width = width
        self.studs = length * width
    
    def describe(self):
        return f"A {self.color} {self.length}x{self.width} brick with {self.studs} studs"
    
    def can_connect_to(self, other_brick):
        # Simplified logic: bricks can connect if dimensions match
        return (self.length == other_brick.width or 
                self.width == other_brick.length)

# Let's try it out:
red_brick = LegoBrick("red", 2, 4)
print(red_brick.describe())  
# Output: "A red 2x4 brick with 8 studs"

blue_brick = LegoBrick("blue", 4, 2)
print(red_brick.can_connect_to(blue_brick))  
# Output: True - they can snap together!
```

### The Punchline

Classes are just blueprints. Instances are the actual LEGO bricks you build from those blueprints. Methods are what your bricks can do. Attributes are what your bricks know about themselves.

And just like real LEGO, once you understand the basics, you can build anything - from simple houses to elaborate Death Stars that take 4,000 pieces and three weeks of your life.

-----

**🎯 Key Takeaways:**

- `class` keyword creates the blueprint (like a LEGO mold design)
- `__init__()` method runs when you create a new instance (manufacturing process)
- `self` refers to the specific instance being created or used
- Attributes are characteristics (color, size) stored with `self.attribute_name`
- Methods are behaviors (functions that belong to the class)
- Instances are actual objects created from the class blueprint

-----

**Next Episode**: “Inheritance: When Child Bricks Rebel Against Their Parent Classes”

Spoiler: `class SpecializedBrick(LegoBrick)` is just fancy LEGO with extra steps.

-----

*Want to dive deeper into the technical details? Check out the [full documentation on GitHub](https://github.com/vanHeemstraSystems/learning-python-object-oriented/blob/main/200/100-defining-classes.md).*

*Have questions or spotted a bug in my LEGO metaphor? Drop a comment below! And if you’re enjoying this series, smash that ❤️ button - it’s like stepping on a LEGO but in a good way.*
