---
title: "Like LEGO? Love Python! 🧱🐍 Ep.3"
published: false
description: "Episode 3: Building Brick Families (Inheritance) - When bricks inherit superpowers from their parents!"
tags: [python, beginners, oop, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/like-lego-love-python-episode-03.png"
series: "Like LEGO? Love Python!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 3: Building Brick Families (Inheritance)

### Welcome Back, Architecture Extraordinaire! 🏰

Remember Episodes 1 and 2 where we learned to build basic bricks and keep their secrets safe? Well, grab your family tree chart because today we’re talking about **inheritance** - or as I like to call it, “How LEGO bricks get their genetics!”

Think about it: A 2x4 LEGO brick shares a LOT with a 2x2 brick. They’re both made of the same ABS plastic, they both have those satisfying studs on top, they both hurt equally when you step on them at 3 AM. But they’re also *different* - different sizes, different stud counts, different uses in your builds.

In Python, we don’t have to rewrite all that shared code. We can create a “parent brick” and have “child bricks” inherit all the good stuff!

## The LEGO Family Tree 🌳

Imagine LEGO headquarters has a master “BasicBrick” blueprint. Every other brick - from tiny 1x1s to massive baseplates - starts with this blueprint and adds its own special features.

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
```

Now, this `BasicBrick` is cool, but it’s pretty generic. Let’s create some specialized bricks that **inherit** from it!

## Single Inheritance: The Classic 2x4 🧱

The classic 2x4 brick is basically a `BasicBrick` with extra features - like knowing its dimensions and calculating studs.

```python
class StandardBrick(BasicBrick):
    """A standard rectangular brick - inherits from BasicBrick!"""
    
    def __init__(self, color, length, width):
        # Call the parent's __init__ - give credit where credit is due!
        super().__init__(color)
        
        # Add our own special attributes
        self.length = length
        self.width = width
        self.studs = length * width
    
    def describe(self):
        """Override the parent's describe method with more detail"""
        # We can still use the parent's version if we want!
        basic_description = super().describe()
        return f"{basic_description} ({self.length}x{self.width}, {self.studs} studs)"
    
    def calculate_volume(self):
        """New method that BasicBrick doesn't have!"""
        # Standard LEGO brick height is ~9.6mm, but let's simplify to 1 unit
        return self.length * self.width * 1

# Create a standard brick
red_brick = StandardBrick("red", 2, 4)

# Inherited methods work!
print(red_brick.color)          # "red" (from BasicBrick)
print(red_brick.material)       # "ABS Plastic" (from BasicBrick)
red_brick.connect(red_brick)    # *satisfying click* 🔊 (from BasicBrick)

# New methods work too!
print(red_brick.describe())     # "A red LEGO brick (2x4, 8 studs)"
print(red_brick.calculate_volume())  # 8

# It's BOTH a StandardBrick AND a BasicBrick!
print(isinstance(red_brick, StandardBrick))  # True
print(isinstance(red_brick, BasicBrick))     # True! 🤯
```

**What’s happening here?**

1. `StandardBrick` **inherits** from `BasicBrick` (see the parentheses?)
1. `super().__init__(color)` calls the parent’s initialization
1. We add NEW attributes (`length`, `width`, `studs`)
1. We OVERRIDE the `describe()` method (rebellion! But polite rebellion)
1. We can access parent methods through `super()`

## The Magic of `super()`: Calling Your Parents 📞

The `super()` function is like calling your parents for advice. You’re independent, but sometimes mom and dad know best!

```python
class TechnicBrick(BasicBrick):
    """LEGO Technic - with holes for axles!"""
    
    def __init__(self, color, holes):
        # "Hey Mom (BasicBrick), can you handle the color?"
        super().__init__(color)
        
        # "Cool, I'll handle the holes myself"
        self.holes = holes
        self.cross_axle_compatible = True
    
    def describe(self):
        # Get parent's description
        parent_desc = super().describe()
        # Add our own flair
        return f"{parent_desc} with {self.holes} axle holes ⚙️"
    
    def connect(self, other_brick):
        # Call parent's connect
        super().connect(other_brick)
        # Add our own behavior
        print("Also connected via axle! 🔩")

technic = TechnicBrick("black", 5)
print(technic.describe())  # "A black LEGO brick with 5 axle holes ⚙️"
technic.connect(technic)   
# *satisfying click* 🔊
# Also connected via axle! 🔩
```

## Multiple Inheritance: The Minifigure Dilemma 🤔

Now things get weird. What if you want to combine features from MULTIPLE parent classes? Enter multiple inheritance - which is like having divorced parents who both want input on your life choices.

```python
class HasStuds:
    """Mixin class for things with studs"""
    
    def __init__(self):
        self.has_studs = True
    
    def count_studs(self):
        return getattr(self, 'studs', 0)

class IsHinged:
    """Mixin class for things that can hinge"""
    
    def __init__(self):
        self.can_hinge = True
        self.hinge_angle = 0
    
    def rotate_hinge(self, degrees):
        self.hinge_angle = degrees
        print(f"Rotated to {degrees}° 🔄")

class WindowFrame(BasicBrick, HasStuds, IsHinged):
    """A window frame - has studs AND can hinge! 🪟"""
    
    def __init__(self, color, studs):
        # Call ALL parent __init__ methods
        BasicBrick.__init__(self, color)
        HasStuds.__init__(self)
        IsHinged.__init__(self)
        
        self.studs = studs
        self.is_transparent = False
    
    def describe(self):
        base = super().describe()
        return f"{base} - Window Frame with {self.studs} studs (hinges {self.hinge_angle}°)"

# Create a window
window = WindowFrame("white", 4)
print(window.describe())        # "A white LEGO brick - Window Frame with 4 studs (hinges 0°)"
window.rotate_hinge(90)         # Rotated to 90° 🔄
print(window.count_studs())     # 4
print(window.connect(window))   # *satisfying click* 🔊
```

**WARNING**: Multiple inheritance is powerful but can get messy FAST. Like building a LEGO castle while your little sibling is “helping.”

## Method Resolution Order (MRO): The Family Reunion Seating Chart 🪑

When you have multiple parents, Python needs to know who to ask first. This is called Method Resolution Order, or “who gets to talk at the family reunion.”

```python
class GrandparentBrick:
    def speak(self):
        return "Back in my day, bricks were just rectangles!"

class ParentBrickA(GrandparentBrick):
    def speak(self):
        return "I'm Parent A - I add colors!"

class ParentBrickB(GrandparentBrick):
    def speak(self):
        return "I'm Parent B - I add studs!"

class ChildBrick(ParentBrickA, ParentBrickB):
    """Child inherits from BOTH parents"""
    pass

# Who speaks when child.speak() is called?
child = ChildBrick()
print(child.speak())  # "I'm Parent A - I add colors!"

# Python's MRO (Method Resolution Order)
print(ChildBrick.__mro__)
# (<class 'ChildBrick'>, <class 'ParentBrickA'>, <class 'ParentBrickB'>, 
#  <class 'GrandparentBrick'>, <class 'object'>)
```

Python checks in THIS order:

1. ChildBrick (the kid gets to speak first)
1. ParentBrickA (left-to-right in the inheritance list)
1. ParentBrickB
1. GrandparentBrick
1. object (the ultimate ancestor of everything in Python)

It’s like a family dinner - the youngest speaks first (because they’re cute), then parents from left to right, then grandparents, then the universe itself.

## Real-World Example: The LEGO City Vehicle Family 🚗

Let’s build a complete vehicle hierarchy like LEGO City sets!

```python
class Vehicle(BasicBrick):
    """Base class for all LEGO vehicles"""
    
    def __init__(self, color, wheels):
        super().__init__(color)
        self.wheels = wheels
        self.speed = 0
    
    def describe(self):
        return f"{self.color} vehicle with {self.wheels} wheels"
    
    def accelerate(self, amount):
        self.speed += amount
        print(f"🏎️ Vroom! Now going {self.speed} studs/second")
    
    def brake(self):
        self.speed = 0
        print("🛑 Screeech! Stopped.")

class Car(Vehicle):
    """A standard LEGO car"""
    
    def __init__(self, color, doors=4):
        super().__init__(color, wheels=4)  # Cars have 4 wheels
        self.doors = doors
    
    def describe(self):
        parent_desc = super().describe()
        return f"{parent_desc}, {self.doors} doors 🚗"
    
    def honk(self):
        print("BEEP BEEP! 📯")

class Truck(Vehicle):
    """A LEGO truck - bigger and slower"""
    
    def __init__(self, color, cargo_capacity):
        super().__init__(color, wheels=6)  # Trucks have 6 wheels
        self.cargo_capacity = cargo_capacity
        self.cargo = []
    
    def describe(self):
        parent_desc = super().describe()
        return f"{parent_desc}, carries {self.cargo_capacity} items 🚚"
    
    def load_cargo(self, item):
        if len(self.cargo) < self.cargo_capacity:
            self.cargo.append(item)
            print(f"Loaded {item}! 📦")
        else:
            print("Cargo full! 📦❌")
    
    def accelerate(self, amount):
        # Trucks are slower (method override)
        super().accelerate(amount // 2)  # Half the acceleration
        print("(Trucks are heavy! 🐌)")

class RaceCar(Car):
    """A LEGO race car - specialized car!"""
    
    def __init__(self, color, team):
        super().__init__(color, doors=2)  # Race cars have 2 doors
        self.team = team
        self.turbo_mode = False
    
    def describe(self):
        parent_desc = super().describe()
        return f"{parent_desc} - {self.team} Racing Team 🏁"
    
    def activate_turbo(self):
        self.turbo_mode = True
        print("💨 TURBO ACTIVATED! 💨")
    
    def accelerate(self, amount):
        if self.turbo_mode:
            super().accelerate(amount * 3)  # Triple speed!
            print("TURBOOOO! 🔥")
            self.turbo_mode = False  # Turbo runs out
        else:
            super().accelerate(amount)

# Let's test our vehicle family!
city_car = Car("red")
print(city_car.describe())       # "red vehicle with 4 wheels, 4 doors 🚗"
city_car.accelerate(10)          # 🏎️ Vroom! Now going 10 studs/second
city_car.honk()                  # BEEP BEEP! 📯

delivery_truck = Truck("yellow", cargo_capacity=5)
print(delivery_truck.describe()) # "yellow vehicle with 6 wheels, carries 5 items 🚚"
delivery_truck.load_cargo("pizza")  # Loaded pizza! 📦
delivery_truck.accelerate(10)    # 🏎️ Vroom! Now going 5 studs/second
                                 # (Trucks are heavy! 🐌)

race_car = RaceCar("blue", "Lightning Squad")
print(race_car.describe())       # "blue vehicle with 4 wheels, 2 doors 🚗 - Lightning Squad Racing Team 🏁"
race_car.activate_turbo()        # 💨 TURBO ACTIVATED! 💨
race_car.accelerate(10)          # 🏎️ Vroom! Now going 30 studs/second
                                 # TURBOOOO! 🔥

# They're all related!
print(isinstance(race_car, RaceCar))    # True
print(isinstance(race_car, Car))        # True
print(isinstance(race_car, Vehicle))    # True
print(isinstance(race_car, BasicBrick)) # True! 🤯
```

## Composition vs Inheritance: The Great Debate 🥊

Sometimes inheritance isn’t the answer. Sometimes you want to BUILD with other objects instead of inheriting from them. It’s like the difference between saying “I AM a brick” vs “I HAVE bricks.”

```python
class Wheel:
    """A LEGO wheel - composition component"""
    
    def __init__(self, diameter):
        self.diameter = diameter
    
    def roll(self):
        print(f"🔄 Rolling {self.diameter}mm wheel...")

class CarWithComposition:
    """A car built using composition instead of inheritance"""
    
    def __init__(self, color, wheel_diameter):
        # HAS-A relationship instead of IS-A
        self.color = color
        self.wheels = [Wheel(wheel_diameter) for _ in range(4)]
        self.speed = 0
    
    def drive(self):
        print(f"Driving {self.color} car...")
        for wheel in self.wheels:
            wheel.roll()

# Composition in action
composed_car = CarWithComposition("green", 30)
composed_car.drive()
# Driving green car...
# 🔄 Rolling 30mm wheel...
# 🔄 Rolling 30mm wheel...
# 🔄 Rolling 30mm wheel...
# 🔄 Rolling 30mm wheel...
```

**When to use Inheritance:**

- “IS-A” relationship (a RaceCar IS-A Car)
- Shared behavior and attributes
- Natural hierarchy exists

**When to use Composition:**

- “HAS-A” relationship (a Car HAS wheels)
- Mix and match components
- More flexibility to change

It’s like LEGO itself! You don’t inherit from a baseplate - you BUILD ON it!

## Abstract Base Classes: The Blueprint Blueprint 📋

Sometimes you want to create a parent class that says “ALL my children MUST implement these methods!” - like LEGO corporate mandating that every brick must have a `connect()` method.

```python
from abc import ABC, abstractmethod

class AbstractVehicle(ABC):
    """Abstract vehicle - can't be instantiated directly!"""
    
    def __init__(self, color):
        self.color = color
    
    @abstractmethod
    def move(self):
        """All vehicles MUST implement this!"""
        pass
    
    @abstractmethod
    def make_sound(self):
        """All vehicles MUST make a sound!"""
        pass

class Boat(AbstractVehicle):
    """A LEGO boat"""
    
    def move(self):
        print("⛵ Sailing smoothly...")
    
    def make_sound(self):
        print("TOOT TOOT! 📯")

class Helicopter(AbstractVehicle):
    """A LEGO helicopter"""
    
    def move(self):
        print("🚁 WHIRRRR - taking off!")
    
    def make_sound(self):
        print("THWOP THWOP THWOP! 🚁")

# Can't create an abstract vehicle directly!
# vehicle = AbstractVehicle("red")  # ❌ TypeError: Can't instantiate abstract class

# But concrete vehicles work!
boat = Boat("blue")
boat.move()         # ⛵ Sailing smoothly...
boat.make_sound()   # TOOT TOOT! 📯

heli = Helicopter("red")
heli.move()         # 🚁 WHIRRRR - taking off!
heli.make_sound()   # THWOP THWOP THWOP! 🚁
```

## The LEGO Inheritance Philosophy 🧘

Just like LEGO’s design philosophy:

1. **Start Simple**: Build a good base class (BasicBrick)
1. **Extend Thoughtfully**: Add features through inheritance (StandardBrick, TechnicBrick)
1. **Specialize Wisely**: Create specialized subclasses only when needed (RaceCar)
1. **Respect the Studs**: Don’t break the parent’s interface (super() is your friend)
1. **Compose When Confused**: If inheritance feels wrong, try composition instead!

## Your Mission, Should You Choose to Accept It 🎯

Build a LEGO Minifigure family hierarchy! Create:

1. `Minifigure` base class with head, torso, legs
1. `Worker` class (construction worker with tool belt)
1. `Astronaut` class (with helmet and jetpack)
1. `Pirate` class (with peg leg and parrot!)
1. Make them all inherit from `Minifigure`
1. Add unique methods for each (worker can `build()`, astronaut can `float()`, pirate can `say_arr()`)

Bonus points if you use `super()` properly and add a `pose()` method to the base class!

## Next Time on “Like LEGO, Love Python” 🎬

In Episode 4, we’ll tackle **Polymorphism** - or as I like to call it, “How Different Bricks Can Do the Same Thing in Different Ways!” We’ll learn about duck typing (if it clicks like a LEGO, it’s a LEGO), method overriding in depth, and how to make your code as flexible as a LEGO Technic joint.

Until then, keep your inheritance trees pruned, your `super()` calls respectful, and your MRO crystal clear!

Happy building! 🏗️✨

-----

*P.S. - If you’re arguing with your team about inheritance vs composition, just remember: LEGO uses BOTH. You inherit from brick designs, but you compose buildings from bricks. Don’t overthink it! Build something awesome!* 🧱🚀

-----

**🎯 Key Takeaways:**

- **Inheritance** lets child classes reuse parent code (DRY principle!)
- `super()` calls parent methods without repeating code
- **MRO** determines which parent speaks first in multiple inheritance
- **Abstract classes** force children to implement certain methods
- **Composition** (HAS-A) is often better than inheritance (IS-A)
- `isinstance()` checks the family tree
- LEGO vehicles > real vehicles 🏎️
