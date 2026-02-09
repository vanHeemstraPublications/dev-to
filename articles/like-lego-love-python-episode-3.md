---
title: "Like LEGO? Love Python! 🧱🐍 Ep.3"
published: true
description: "Episode 3: Building Brick Families (Inheritance) - When bricks inherit superpowers from their parents!"
tags: [python, beginners, oop, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/like-lego-love-python-episode-03.png"
series: "Like LEGO? Love Python!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 3: Building Brick Families (Inheritance)

### Welcome Back, Architecture Extraordinaire! 🏰

Remember Episodes 1 and 2 where we learned to build basic bricks and keep their secrets safe? Well, grab your family tree chart because today we're talking about **inheritance** - or as I like to call it, "How LEGO bricks get their genetics!"

Think about it: A 2x4 LEGO brick shares a LOT with a 2x2 brick. They're both made of the same ABS plastic, they both have those satisfying studs on top, they both hurt equally when you step on them at 3 AM. But they're also *different* - different sizes, different stud counts, different uses in your builds.

In Python, we don't have to rewrite all that shared code. We can create a "parent brick" and have "child bricks" inherit all the good stuff!

## The LEGO Family Tree 🌳

Imagine LEGO headquarters has a master "BasicBrick" blueprint. Every other brick - from tiny 1x1s to massive baseplates - starts with this blueprint and adds its own special features.

```python
class BasicBrick:
    """The ancestor of all LEGO bricks - the Original Progenitor!"""
    
    def __init__(self, color):
        self.color = color
        self.material = "ABS Plastic"  # All LEGO bricks share this
        self.manufacturer = "LEGO Group"
        self.clutch_power = 10  # That satisfying click!
    
    def describe(self):
        """Every brick can describe itself"""
        return f"A {self.color} LEGO brick"
    
    def connect(self, other_brick):
        """All bricks can connect!"""
        print(f"*satisfying click* 🔊")
        return True
    
    def __repr__(self):
        return f"BasicBrick(color='{self.color}')"

# Create a basic brick
basic = BasicBrick("red")
print(basic.describe())  # "A red LEGO brick"
basic.connect(basic)     # *satisfying click* 🔊
