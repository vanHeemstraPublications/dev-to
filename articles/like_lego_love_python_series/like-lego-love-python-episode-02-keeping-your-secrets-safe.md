---
title: "Like LEGO? Love Python! 🧱🐍 Ep.2"
published: false
part: 2
description: "Just like LEGO bricks hide their inner mechanisms, Python’s encapsulation keeps your data safe and your code clean. Let’s build some privacy into our Python creations!"
tags: [python, beginners, oop, tutorial]
series: "Like LEGO? Love Python!"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/like-lego-love-python-episode-02.png"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 2: Keeping Your Secrets Safe

## Welcome Back, Master Builder! 🏗️

Remember in Episode 1 when we built our first LEGO brick in Python? Well, grab your hard hat again because today we’re learning something super important: how to keep the inner workings of our bricks hidden and protected. Just like a real LEGO brick!

Think about it: when you pick up a LEGO brick, you don’t see the exact molecular structure of the plastic, the precise injection molding patterns, or the secret sauce that makes those studs click together so satisfyingly. You just see a nice, clean brick with a predictable interface. That’s **encapsulation** in action!

## The LEGO Philosophy: Hide the Gears ⚙️

Ever opened up a LEGO Technic motor? From the outside, it’s just a compact black box with a couple of connection points. But inside, there’s a whole symphony of gears, circuits, and magnets doing their thing. LEGO keeps all that complexity hidden so you don’t accidentally stick your finger in the wrong place and break something important.

Python does the same thing with encapsulation. We hide the “gears and circuits” of our code so that:

1. **Users can’t accidentally break stuff** (like changing your brick’s color to “transparent gravity-defying purple”)
1. **We can change the inner workings later** without breaking everyone’s builds
1. **Our code looks cleaner** than a perfectly organized LEGO storage system

## Building a Private Vault 🔐

Let’s upgrade our LEGO brick from Episode 1. This time, we’ll give it some privacy settings!

```python
class LegoBrick:
    """A LEGO brick that guards its secrets like a dragon guards treasure"""
    
    def __init__(self, color, size):
        # Public attributes - everyone can see these
        self.studs = 8
        self.bottom_tubes = 6
        
        # "Private" attributes - Python's polite request for privacy
        self._internal_color_code = self._convert_to_color_code(color)
        self._manufacturing_batch = "2025-B7"
        
        # "Really private" attributes - Python's serious privacy mode
        self.__secret_formula = "ABS_PLASTIC_BLEND_v3.2"
        self.__quality_check_passed = True
        
        # Public property - controlled access!
        self.size = size
    
    def _convert_to_color_code(self, color):
        """Private helper method - internal use only!"""
        color_codes = {
            "red": "R01",
            "blue": "B05",
            "yellow": "Y03"
        }
        return color_codes.get(color.lower(), "X00")
    
    def get_color(self):
        """Public getter - the approved way to check color"""
        return f"Color code: {self._internal_color_code}"
    
    def set_color(self, new_color):
        """Public setter - the bouncer at the color-change club"""
        allowed_colors = ["red", "blue", "yellow", "green"]
        if new_color.lower() in allowed_colors:
            self._internal_color_code = self._convert_to_color_code(new_color)
            print(f"✅ Color changed to {new_color}!")
        else:
            print(f"❌ Sorry, {new_color} is not in the LEGO color catalog!")
```

Look at all those underscores! In Python:

- **No underscores** (`studs`): “Come on in, everyone! Touch away!”
- **Single underscore** (`_internal_color_code`): “Please don’t touch, but I can’t stop you” (like a wet paint sign)
- **Double underscore** (`__secret_formula`): “Python will literally mangle the name to make it harder to access” (like hiding the cookie jar on top of the fridge)

## The Property Decorator: Your Personal Butler 🎩

Getters and setters are great, but typing `get_` and `set_` everywhere is about as fun as stepping on a LEGO brick barefoot. Enter Python’s `@property` decorator - the butler of the programming world!

```python
class FancyLegoBrick:
    """A LEGO brick with a butler. Fancy!"""
    
    def __init__(self, color):
        self._color = color
        self._click_quality = 10  # Out of 10, obviously perfect
    
    @property
    def color(self):
        """Getting the color is as easy as asking nicely"""
        return f"This brick is {self._color}"
    
    @color.setter
    def color(self, new_color):
        """Setting the color... with validation!"""
        if len(new_color) < 3:
            raise ValueError("Color names must be at least 3 characters! "
                           "'Rd' is not a color, it's a typo!")
        self._color = new_color
        print(f"🎨 Brick repainted to {new_color}!")
    
    @property
    def click_quality(self):
        """Read-only property - no setter allowed!"""
        return self._click_quality
    
    # Notice: no @click_quality.setter - this property is read-only!
    # Like trying to change how satisfying the LEGO click sound is.
    # It's perfect. It's always been perfect. It will always be perfect.
```

Now you can use it like this:

```python
fancy_brick = FancyLegoBrick("red")

# Getting is easy
print(fancy_brick.color)  # "This brick is red"

# Setting looks natural
fancy_brick.color = "blue"  # 🎨 Brick repainted to blue!

# But try to set an invalid color...
fancy_brick.color = "uv"  # 💥 ValueError: Color names must be at least 3 characters!

# Read-only property
print(fancy_brick.click_quality)  # 10
fancy_brick.click_quality = 7  # 💥 AttributeError: can't set attribute
# Nice try, but LEGO quality is non-negotiable!
```

## Name Mangling: Python’s Witness Protection Program 🕵️

Remember those double underscores (`__secret_formula`)? Python does something sneaky called “name mangling.” It’s like putting your attribute in witness protection:

```python
class SecretBrick:
    def __init__(self):
        self.__secret = "The secret is... there is no secret!"
    
    def reveal_secret(self):
        return self.__secret

brick = SecretBrick()

# Try to access the secret directly
print(brick.__secret)  # 💥 AttributeError: 'SecretBrick' has no attribute '__secret'

# Python renamed it to _SecretBrick__secret
print(brick._SecretBrick__secret)  # "The secret is... there is no secret!"
# (You found it, but you had to work for it!)

# The approved way
print(brick.reveal_secret())  # "The secret is... there is no secret!"
```

Python’s name mangling is like LEGO hiding their injection molding techniques. Sure, you *could* reverse-engineer it, but they’re politely asking you not to. And honestly, why would you want to mess with perfection?

## Data Validation: The Quality Control Inspector 🔍

One of the best parts of encapsulation is adding validation. It’s like having a quality control inspector who checks every brick before it leaves the factory:

```python
class ValidatedLegoBrick:
    """A brick with STRICT quality standards"""
    
    def __init__(self, color, studs):
        self.color = color  # Using the property setter
        self.studs = studs  # Using the property setter
    
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        approved_colors = ["red", "blue", "yellow", "green", "black", "white"]
        if value.lower() not in approved_colors:
            raise ValueError(f"❌ {value} is not an approved LEGO color! "
                           f"We have standards here!")
        self._color = value.lower()
    
    @property
    def studs(self):
        return self._studs
    
    @studs.setter
    def studs(self, value):
        if not isinstance(value, int):
            raise TypeError("❌ Studs must be a whole number! "
                          "We don't do fractional studs here!")
        if value < 1 or value > 100:
            raise ValueError("❌ Studs must be between 1 and 100! "
                           "This is a brick, not a baseplate!")
        self._studs = value
    
    def __repr__(self):
        return f"ValidatedLegoBrick(color='{self.color}', studs={self.studs})"

# Let's test the quality control
try:
    brick1 = ValidatedLegoBrick("red", 8)  # ✅ Perfect!
    print(brick1)
    
    brick2 = ValidatedLegoBrick("neon-pink", 8)  # ❌ Invalid color!
except ValueError as e:
    print(e)

try:
    brick3 = ValidatedLegoBrick("blue", 8.5)  # ❌ Fractional studs!
except TypeError as e:
    print(e)

try:
    brick4 = ValidatedLegoBrick("yellow", 150)  # ❌ Too many studs!
except ValueError as e:
    print(e)
```

## The LEGO Technic Gear Example 🔩

Let’s build something more complex - a LEGO Technic gear system where the internal gear ratios are encapsulated:

```python
class TechnicGear:
    """A LEGO Technic gear with hidden complexity"""
    
    # Class constant - public but conventionally "don't change this"
    MAX_RPM = 1000
    
    def __init__(self, teeth, gear_type="standard"):
        self._teeth = teeth
        self._gear_type = gear_type
        self._current_rpm = 0
        self.__wear_level = 0  # Internal tracking
        self._validate_configuration()
    
    def _validate_configuration(self):
        """Private validation method"""
        valid_teeth = [8, 16, 24, 40]
        if self._teeth not in valid_teeth:
            raise ValueError(f"Invalid gear size! Must be one of {valid_teeth}")
    
    @property
    def teeth(self):
        """Number of teeth - read only after creation"""
        return self._teeth
    
    @property
    def rpm(self):
        """Current rotation speed"""
        return self._current_rpm
    
    def spin(self, input_rpm):
        """Spin the gear at a given RPM"""
        if input_rpm > self.MAX_RPM:
            print(f"⚠️ Warning: {input_rpm} RPM exceeds safe limit!")
            self._current_rpm = self.MAX_RPM
        else:
            self._current_rpm = input_rpm
        
        # Internal tracking
        self.__wear_level += input_rpm * 0.001
        print(f"🔄 Gear spinning at {self._current_rpm} RPM")
    
    def mesh_with(self, other_gear, input_rpm):
        """Mesh with another gear and calculate output RPM"""
        # The magic ratio calculation is hidden from users
        ratio = self._calculate_gear_ratio(other_gear)
        output_rpm = input_rpm * ratio
        
        self.spin(input_rpm)
        other_gear.spin(output_rpm)
        
        return output_rpm
    
    def _calculate_gear_ratio(self, other_gear):
        """Private method - the secret sauce of gear calculations"""
        return self._teeth / other_gear._teeth
    
    def _check_wear(self):
        """Private diagnostic method"""
        if self.__wear_level > 100:
            return "🔴 High wear - consider replacement"
        elif self.__wear_level > 50:
            return "🟡 Moderate wear - monitor closely"
        else:
            return "🟢 Low wear - gear is healthy"
    
    def get_diagnostic_report(self):
        """Public method exposing curated internal data"""
        return {
            "teeth": self._teeth,
            "type": self._gear_type,
            "current_rpm": self._current_rpm,
            "health_status": self._check_wear()
        }

# Using our encapsulated gear system
gear_small = TechnicGear(8)
gear_large = TechnicGear(24)

# Public interface is clean
output_rpm = gear_small.mesh_with(gear_large, 300)
print(f"Output RPM: {output_rpm}")

# Get diagnostic without exposing internals
print(gear_small.get_diagnostic_report())

# Can't directly access private stuff
# print(gear_small.__wear_level)  # ❌ AttributeError
```

## Why Encapsulation Matters: The Baseplate Philosophy 📐

Imagine if LEGO changed the size of their studs by 0.5mm. Every single LEGO set ever made would become incompatible. Chaos! Tears! Ruined childhoods!

But what if they changed the *internal structure* of the studs while keeping the outside exactly the same? You’d never notice! Your builds would still work perfectly!

That’s encapsulation:

- **Public interface** (studs and tubes): NEVER CHANGE (or at least, change very carefully)
- **Private implementation** (plastic blend, internal structure): CHANGE FREELY

```python
class LegoBrickV1:
    """Original brick design"""
    def __init__(self):
        self._internal_structure = "hollow_cylinder"
    
    @property
    def studs(self):
        return 8  # Public interface - sacred!
    
    def connect_to(self, other_brick):
        # Implementation details hidden
        return self._internal_structure == "hollow_cylinder"

class LegoBrickV2:
    """Improved brick design with better grip"""
    def __init__(self):
        self._internal_structure = "reinforced_hollow_cylinder"  # Changed!
    
    @property
    def studs(self):
        return 8  # Same public interface!
    
    def connect_to(self, other_brick):
        # Improved implementation, same interface
        return self._internal_structure == "reinforced_hollow_cylinder"

# Both versions work the same from the outside!
v1_brick = LegoBrickV1()
v2_brick = LegoBrickV2()

print(f"V1 studs: {v1_brick.studs}")  # 8
print(f"V2 studs: {v2_brick.studs}")  # 8
# Users don't need to know about internal changes!
```

## The Three Laws of LEGO Encapsulation ⚖️

1. **Make it hard to break**: Use validation in setters
1. **Hide implementation details**: Use single underscore for “internal” stuff
1. **Provide a clean interface**: Use properties and well-named public methods

```python
class PerfectlyEncapsulatedBrick:
    """Following all three laws"""
    
    def __init__(self, color, studs):
        # Law 1: Validate in setters
        self.color = color
        self.studs = studs
        # Law 2: Hide implementation
        self._batch_number = "2025-001"
        self.__quality_score = 100
    
    # Law 3: Clean public interface
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        if not isinstance(value, str):
            raise TypeError("Color must be a string!")
        self._color = value.lower()
    
    @property
    def studs(self):
        return self._studs
    
    @studs.setter
    def studs(self, value):
        if not isinstance(value, int) or value < 1:
            raise ValueError("Studs must be a positive integer!")
        self._studs = value
    
    def inspect(self):
        """Public method with clean interface"""
        return f"{self._color} brick with {self._studs} studs (Batch: {self._batch_number})"
```

## Your Mission, Should You Choose to Accept It 🎯

Here’s a challenge: create a `LegoMinifigure` class that:

1. Has private attributes for `_head_type`, `_torso_design`, and `_leg_color`
1. Uses `@property` decorators for accessing these attributes
1. Validates that hair types are in an approved list
1. Tracks how many times the arms have been moved (hidden counter)
1. Has a public method `pose()` that reports the current pose

Try it out! And remember: keep the studs public, but hide the manufacturing secrets! 🏗️

## Next Time on “Like LEGO, Love Python” 🎬

In Episode 3, we’ll explore **Inheritance** - or as I like to call it, “How baby bricks inherit the DNA of their parent bricks!” We’ll build families of LEGO pieces, learn about method overriding (rebellious teenage bricks), and discover the magical `super()` function.

Until then, keep your code clean, your interfaces public, and your implementations private!

Happy building! 🧱✨

-----

*P.S. - If you try to access `self.__secret_formula` directly, the LEGO lawyers will find you. Just kidding! But seriously, use the properties.* 😄
