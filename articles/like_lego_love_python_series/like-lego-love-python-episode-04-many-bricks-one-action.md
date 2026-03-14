---
title: "Like LEGO? Love Python! 🧱🐍 Ep.4"
published: false
part: 4
description: "Episode 4: Many Bricks, One Action (Polymorphism) - When different bricks all click together, but in their own special way!"
tags: [python, beginners, oop, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/like-lego-love-python-episode-04.png"
series: "Like LEGO? Love Python!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 4: Many Bricks, One Action (Polymorphism)

### Welcome Back, Master Builder! 🏗️

Remember in Episode 3 when we learned about inheritance and how bricks can be part of a family tree? Well, buckle up because today we’re diving into **polymorphism** - which is just a fancy Greek word meaning “many forms.”

Think about it: Every LEGO brick can **connect** to another brick. Whether it’s a tiny 1x1, a massive baseplate, a Technic gear, or even a minifigure’s head - they all *click together*. But they each do it in their own unique way! That’s polymorphism in a nutshell.

The beauty? You don’t need to know WHAT kind of brick you’re connecting - you just know it CAN connect. It’s like the universal language of LEGO studs and tubes! 🧱✨

## The Universal Language of LEGO Studs 🌍

Imagine you’re at a massive LEGO convention. People from all over the world are building together. Nobody speaks the same language, but everyone understands one thing: *click* means *connect*.

```python
class StandardBrick:
    """A standard 2x4 LEGO brick"""
    
    def __init__(self, color):
        self.color = color
    
    def connect(self):
        return f"*Standard CLICK!* 🔊 {self.color} brick connected"

class TechnicBrick:
    """A LEGO Technic brick with holes"""
    
    def __init__(self, color):
        self.color = color
    
    def connect(self):
        return f"*CLICK-SNAP!* ⚙️ {self.color} Technic brick locked in with axle!"

class Baseplate:
    """A massive LEGO baseplate"""
    
    def __init__(self, color):
        self.color = color
    
    def connect(self):
        return f"*HEAVY THUD!* 🏗️ {self.color} baseplate providing foundation!"

class MinifigureHead:
    """A minifigure head (yes, it connects too!)"""
    
    def __init__(self, expression):
        self.expression = expression
    
    def connect(self):
        return f"*gentle click* 😊 {self.expression} head attached to torso!"

# The magic of polymorphism - one function, many types!
def attach_brick(brick):
    """Works with ANY brick that has a connect() method!"""
    print(brick.connect())

# Let's test with different brick types
standard = StandardBrick("red")
technic = TechnicBrick("black")
base = Baseplate("green")
head = MinifigureHead("happy")

# Same function call - different behaviors!
attach_brick(standard)  # *Standard CLICK!* 🔊 red brick connected
attach_brick(technic)   # *CLICK-SNAP!* ⚙️ black Technic brick locked in with axle!
attach_brick(base)      # *HEAVY THUD!* 🏗️ green baseplate providing foundation!
attach_brick(head)      # *gentle click* 😊 happy head attached to torso!
```

**What just happened?!** 🤯

The `attach_brick()` function doesn’t care WHAT type of brick it receives. It just knows that whatever comes in has a `connect()` method. That’s polymorphism! Same interface, different implementations.

## Duck Typing: If It Looks Like a LEGO… 🦆

Python has something called “duck typing.” The name comes from the saying:

> “If it walks like a duck and quacks like a duck, then it must be a duck.”

In LEGO terms:

> “If it has studs like a LEGO and clicks like a LEGO, then it must be a LEGO!”

Python doesn’t check if something IS a certain type - it checks if it CAN DO what you’re asking.

```python
class OfficialLEGOBrick:
    """An official LEGO brick"""
    
    def __init__(self, color):
        self.color = color
        self.manufacturer = "LEGO Group"
    
    def connect(self):
        return f"Official {self.color} LEGO brick - connected! ✅"
    
    def make_sound(self):
        return "*satisfying LEGO click* 🔊"

class OffBrandBrick:
    """A non-LEGO brick (gasp!) but it still works!"""
    
    def __init__(self, color):
        self.color = color
        self.manufacturer = "Definitely Not LEGO Inc."
    
    def connect(self):
        return f"Off-brand {self.color} brick - connected (kinda)! ⚠️"
    
    def make_sound(self):
        return "*slightly less satisfying click* 🔇"

class WoodenBlock:
    """A wooden building block - totally different!"""
    
    def __init__(self, color):
        self.color = color
    
    def connect(self):
        return f"{self.color} wooden block - just stacking, no studs! 🪵"
    
    def make_sound(self):
        return "*clunk* 🪵"

def build_tower(bricks):
    """Build a tower with ANY bricks that can connect!"""
    tower = []
    for brick in bricks:
        tower.append(brick.connect())
        print(brick.make_sound())
    
    return tower

# Mix and match - Python doesn't care!
my_bricks = [
    OfficialLEGOBrick("red"),
    OffBrandBrick("blue"),
    WoodenBlock("yellow"),
    OfficialLEGOBrick("green")
]

tower = build_tower(my_bricks)
# *satisfying LEGO click* 🔊
# *slightly less satisfying click* 🔇
# *clunk* 🪵
# *satisfying LEGO click* 🔊

# They all connected! Duck typing in action! 🦆
```

Notice how `build_tower()` works with ALL these objects, even though they’re completely different types? That’s the power of duck typing. If it has a `connect()` method and a `make_sound()` method, it works!

## Method Overriding: Same Name, Different Game 🎮

Remember inheritance from Episode 3? When child classes override parent methods, that’s polymorphism too! Same method name, but each class does its own thing.

```python
class Vehicle:
    """Base LEGO vehicle class"""
    
    def __init__(self, color):
        self.color = color
    
    def move(self):
        return f"{self.color} vehicle is moving..."
    
    def make_noise(self):
        return "vrrrm"  # Generic vehicle noise

class Car(Vehicle):
    """LEGO car - overrides movement"""
    
    def move(self):
        return f"🚗 {self.color} car is driving on roads!"
    
    def make_noise(self):
        return "VROOM VROOM! 🏎️"

class Boat(Vehicle):
    """LEGO boat - different movement entirely!"""
    
    def move(self):
        return f"⛵ {self.color} boat is sailing on water!"
    
    def make_noise(self):
        return "TOOT TOOT! 📯"

class Helicopter(Vehicle):
    """LEGO helicopter - flying high!"""
    
    def move(self):
        return f"🚁 {self.color} helicopter is flying in the air!"
    
    def make_noise(self):
        return "THWOP THWOP THWOP! 🚁"

class Submarine(Vehicle):
    """LEGO submarine - underwater adventure!"""
    
    def move(self):
        return f"🤿 {self.color} submarine is diving underwater!"
    
    def make_noise(self):
        return "*silent running* 🔇 *PING* 📡"

# Polymorphic function - works with ALL vehicles!
def start_chase_scene(vehicles):
    """Epic LEGO movie chase scene!"""
    print("🎬 ACTION! 🎬\n")
    
    for vehicle in vehicles:
        print(vehicle.make_noise())
        print(vehicle.move())
        print()

# Assemble the cast!
fleet = [
    Car("red"),
    Boat("blue"),
    Helicopter("white"),
    Submarine("yellow"),
    Car("black")  # The villain's car!
]

start_chase_scene(fleet)
# 🎬 ACTION! 🎬
# 
# VROOM VROOM! 🏎️
# 🚗 red car is driving on roads!
# 
# TOOT TOOT! 📯
# ⛵ blue boat is sailing on water!
# 
# THWOP THWOP THWOP! 🚁
# 🚁 white helicopter is flying in the air!
# 
# *silent running* 🔇 *PING* 📡
# 🤿 yellow submarine is diving underwater!
# 
# VROOM VROOM! 🏎️
# 🚗 black car is driving on roads!
```

Same method names (`move()` and `make_noise()`), completely different behaviors! That’s polymorphism making your code clean and flexible. You can add new vehicle types without changing `start_chase_scene()`!

## Operator Overloading: When Bricks Do Math! ➕

Here’s where it gets REALLY fun. In Python, you can make your LEGO bricks work with operators like `+`, `-`, `*`, and even `==`. It’s like teaching your bricks to do arithmetic!

```python
class BrickSet:
    """A collection of LEGO bricks"""
    
    def __init__(self, brick_count, color="mixed"):
        self.brick_count = brick_count
        self.color = color
    
    def __add__(self, other):
        """Override the + operator - combine brick sets!"""
        total_bricks = self.brick_count + other.brick_count
        return BrickSet(total_bricks, "combined")
    
    def __sub__(self, other):
        """Override the - operator - remove some bricks!"""
        remaining = max(0, self.brick_count - other.brick_count)
        return BrickSet(remaining, self.color)
    
    def __mul__(self, multiplier):
        """Override the * operator - multiply brick sets!"""
        return BrickSet(self.brick_count * multiplier, self.color)
    
    def __eq__(self, other):
        """Override the == operator - are sets equal?"""
        return self.brick_count == other.brick_count
    
    def __lt__(self, other):
        """Override the < operator - is this set smaller?"""
        return self.brick_count < other.brick_count
    
    def __str__(self):
        """Override str() - readable description"""
        return f"{self.brick_count} {self.color} bricks"
    
    def __repr__(self):
        """Override repr() - technical description"""
        return f"BrickSet(brick_count={self.brick_count}, color='{self.color}')"
    
    def __len__(self):
        """Override len() - get brick count"""
        return self.brick_count

# Let's do some brick math! 🧮
small_set = BrickSet(50, "red")
medium_set = BrickSet(100, "blue")
large_set = BrickSet(200, "yellow")

# Addition - combine sets!
combined = small_set + medium_set
print(combined)  # 150 combined bricks

# Subtraction - remove some bricks!
remaining = large_set - small_set
print(remaining)  # 150 yellow bricks

# Multiplication - buy multiple sets!
bulk_order = small_set * 5
print(bulk_order)  # 250 red bricks

# Comparison - which is bigger?
print(small_set < medium_set)  # True
print(small_set == BrickSet(50, "green"))  # True (same count!)

# Length - how many bricks?
print(len(large_set))  # 200

# String representation
print(f"I have {small_set} and {medium_set}")
# I have 50 red bricks and 100 blue bricks
```

**Magic Methods Cheat Sheet:**

|Operator|Method       |Example       |
|--------|-------------|--------------|
|`+`     |`__add__`    |`set1 + set2` |
|`-`     |`__sub__`    |`set1 - set2` |
|`*`     |`__mul__`    |`set1 * 3`    |
|`/`     |`__truediv__`|`set1 / 2`    |
|`==`    |`__eq__`     |`set1 == set2`|
|`<`     |`__lt__`     |`set1 < set2` |
|`>`     |`__gt__`     |`set1 > set2` |
|`len()` |`__len__`    |`len(set1)`   |
|`str()` |`__str__`    |`str(set1)`   |
|`repr()`|`__repr__`   |`repr(set1)`  |

## Real-World Example: The Multi-Cloud LEGO Factory 🏭

Let’s build something practical! Imagine you’re deploying LEGO factories to different cloud providers (Azure, AWS, GCP). Each cloud works differently, but you want ONE deployment script.

```python
class CloudProvider:
    """Base cloud provider - polymorphic interface"""
    
    def __init__(self, name):
        self.name = name
        self.deployments = []
    
    def deploy_factory(self, factory_name):
        """Each cloud deploys differently!"""
        raise NotImplementedError("Subclass must implement deploy_factory()")
    
    def get_cost(self, hours):
        """Each cloud prices differently!"""
        raise NotImplementedError("Subclass must implement get_cost()")
    
    def __str__(self):
        return f"{self.name} Cloud Provider"

class AzureCloud(CloudProvider):
    """Microsoft Azure - LEGO factories on Azure!"""
    
    def __init__(self):
        super().__init__("Azure")
        self.rate_per_hour = 10.0
    
    def deploy_factory(self, factory_name):
        deployment = f"🔵 Deploying {factory_name} to Azure West Europe"
        self.deployments.append(deployment)
        return deployment
    
    def get_cost(self, hours):
        return f"€{self.rate_per_hour * hours:.2f} (Azure pricing)"

class AWSCloud(CloudProvider):
    """Amazon AWS - LEGO factories on AWS!"""
    
    def __init__(self):
        super().__init__("AWS")
        self.rate_per_hour = 9.50
    
    def deploy_factory(self, factory_name):
        deployment = f"🟧 Deploying {factory_name} to AWS eu-west-1"
        self.deployments.append(deployment)
        return deployment
    
    def get_cost(self, hours):
        return f"€{self.rate_per_hour * hours:.2f} (AWS pricing)"

class GCPCloud(CloudProvider):
    """Google Cloud Platform - LEGO factories on GCP!"""
    
    def __init__(self):
        super().__init__("GCP")
        self.rate_per_hour = 9.00
    
    def deploy_factory(self, factory_name):
        deployment = f"🔴 Deploying {factory_name} to GCP europe-west4"
        self.deployments.append(deployment)
        return deployment
    
    def get_cost(self, hours):
        return f"€{self.rate_per_hour * hours:.2f} (GCP pricing + sustained use discount)"

class MultiCloudDeployer:
    """
    Polymorphic deployer - works with ANY cloud provider!
    This is the power of polymorphism in action! 🚀
    """
    
    def __init__(self, providers):
        self.providers = providers
    
    def deploy_to_all_clouds(self, factory_name):
        """Deploy to multiple clouds - polymorphism makes this easy!"""
        print(f"🏭 Deploying {factory_name} to all clouds...\n")
        
        for provider in self.providers:
            # Same method call - different behavior per cloud!
            result = provider.deploy_factory(factory_name)
            print(result)
        
        print("\n✅ Multi-cloud deployment complete!")
    
    def cost_comparison(self, hours):
        """Compare costs across clouds"""
        print(f"\n💰 Cost comparison for {hours} hours:\n")
        
        for provider in self.providers:
            # Same method call - different pricing per cloud!
            cost = provider.get_cost(hours)
            print(f"{provider.name}: {cost}")
    
    def find_cheapest(self, hours):
        """Find the cheapest cloud - polymorphism + algorithms!"""
        costs = {}
        for provider in self.providers:
            # Extract numeric cost (hacky but demonstrates polymorphism)
            cost_str = provider.get_cost(hours)
            cost = float(cost_str.split('€')[1].split()[0])
            costs[provider.name] = cost
        
        cheapest = min(costs, key=costs.get)
        return f"🏆 Cheapest option: {cheapest} at €{costs[cheapest]:.2f}"

# Assemble your multi-cloud fleet!
azure = AzureCloud()
aws = AWSCloud()
gcp = GCPCloud()

# Create multi-cloud deployer
deployer = MultiCloudDeployer([azure, aws, gcp])

# Deploy to all clouds with ONE command!
deployer.deploy_to_all_clouds("LEGO-Factory-Europe")
# 🏭 Deploying LEGO-Factory-Europe to all clouds...
# 
# 🔵 Deploying LEGO-Factory-Europe to Azure West Europe
# 🟧 Deploying LEGO-Factory-Europe to AWS eu-west-1
# 🔴 Deploying LEGO-Factory-Europe to GCP europe-west4
# 
# ✅ Multi-cloud deployment complete!

# Compare costs
deployer.cost_comparison(720)  # 30 days
# 💰 Cost comparison for 720 hours:
# 
# Azure: €7200.00 (Azure pricing)
# AWS: €6840.00 (AWS pricing)
# GCP: €6480.00 (GCP pricing + sustained use discount)

# Find the best deal
print(deployer.find_cheapest(720))
# 🏆 Cheapest option: GCP at €6480.00
```

**The Magic Here:**

- ONE `MultiCloudDeployer` class works with ALL cloud providers
- Adding a new cloud provider? Just create a new class with `deploy_factory()` and `get_cost()`
- No changes needed to `MultiCloudDeployer`!
- That’s polymorphism making your code **flexible** and **maintainable**! 🎯

## The LEGO Sorting Machine: Polymorphism in Action 🔍

Let’s build a LEGO sorting machine that can handle ANY type of brick!

```python
class SortableBrick:
    """Base class for sortable items"""
    
    def get_sort_key(self):
        """Each brick type defines how it should be sorted"""
        raise NotImplementedError

class ColorBrick(SortableBrick):
    """Sort by color"""
    
    def __init__(self, color, size):
        self.color = color
        self.size = size
    
    def get_sort_key(self):
        return self.color
    
    def __str__(self):
        return f"{self.color} {self.size}x{self.size} brick"

class SizeBrick(SortableBrick):
    """Sort by size"""
    
    def __init__(self, color, size):
        self.color = color
        self.size = size
    
    def get_sort_key(self):
        return self.size
    
    def __str__(self):
        return f"{self.size}x{self.size} {self.color} brick"

class SpecialBrick(SortableBrick):
    """Sort by special category"""
    
    def __init__(self, category, name):
        self.category = category
        self.name = name
    
    def get_sort_key(self):
        return self.category
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class BrickSorter:
    """Polymorphic sorter - works with ANY SortableBrick!"""
    
    def __init__(self, bricks):
        self.bricks = bricks
    
    def sort_bricks(self):
        """Sort using each brick's own sorting logic"""
        return sorted(self.bricks, key=lambda b: b.get_sort_key())
    
    def group_by_key(self):
        """Group bricks by their sort key"""
        groups = {}
        for brick in self.bricks:
            key = brick.get_sort_key()
            if key not in groups:
                groups[key] = []
            groups[key].append(brick)
        return groups

# Create a chaotic pile of bricks!
pile = [
    ColorBrick("red", 2),
    ColorBrick("blue", 4),
    SizeBrick("yellow", 1),
    SizeBrick("green", 2),
    SpecialBrick("technic", "Gear wheel"),
    SpecialBrick("wheels", "Race car wheel"),
    ColorBrick("red", 4),
    SpecialBrick("technic", "Axle"),
]

# Sort them!
sorter = BrickSorter(pile)

print("🔀 Sorted bricks:")
for brick in sorter.sort_bricks():
    print(f"  • {brick}")

print("\n📦 Grouped by sort key:")
groups = sorter.group_by_key()
for key, bricks in groups.items():
    print(f"\n{key.upper()}:")
    for brick in bricks:
        print(f"  • {brick}")
```

**Why This Works:**

Each brick class decides HOW it wants to be sorted (by color, size, or category), but the `BrickSorter` doesn’t care! It just calls `get_sort_key()` on everything. Polymorphism for the win! 🏆

## When Polymorphism Goes Wrong: The LEGO Mixing Disaster 🚨

Not everything should be polymorphic. Sometimes you NEED to know the exact type:

```python
class LegoSet:
    def build(self):
        return "Building awesome LEGO creation! 🏗️"

class PuzzlePiece:
    def build(self):
        return "Putting puzzle together... 🧩"

class PlayDoh:
    def build(self):
        return "Squishing Play-Doh into... something? 🎨"

def construct_project(item):
    """
    Polymorphic function - but maybe too polymorphic?
    Everything has build() but they're VERY different!
    """
    return item.build()

# This works, but is it RIGHT?
construct_project(LegoSet())      # Building awesome LEGO creation! 🏗️
construct_project(PuzzlePiece())  # Putting puzzle together... 🧩
construct_project(PlayDoh())      # Squishing Play-Doh into... something? 🎨

# Sometimes you need to check types!
def construct_lego_only(item):
    if not isinstance(item, LegoSet):
        raise TypeError("Sorry, LEGO only! No Play-Doh allowed! 🚫")
    return item.build()

construct_lego_only(LegoSet())    # ✅ Works!
# construct_lego_only(PlayDoh())  # ❌ TypeError!
```

**Lesson:** Polymorphism is powerful, but don’t force it where it doesn’t make sense. Sometimes type checking is the right call! 🎯

## The LEGO Philosophy of Polymorphism 🧘

Just like LEGO’s design:

1. **Universal Interface**: All bricks connect (studs + tubes = magic)
1. **Specialized Behavior**: Each brick type has unique features
1. **Mix & Match**: Combine any bricks without knowing their exact types
1. **Extend Freely**: Add new brick types without breaking existing builds
1. **Keep It Simple**: If it clicks, it works! 🔊

## Your Mission, Should You Choose to Accept It 🎯

Build a polymorphic LEGO theme park! Create:

1. `Attraction` base class with `operate()` and `describe()` methods
1. `RollerCoaster` - makes people scream
1. `FerrisWheel` - spins slowly with great views
1. `WaterSlide` - splashes everyone
1. `HauntedHouse` - spooky scary!
1. Create a `ThemePark` class that can operate ALL attractions polymorphically
1. Add operator overloading so you can `+` attractions together to create bigger parks!

Bonus: Make each attraction return a different emoji when operated! 🎢🎡💦👻

## Next Time on “Like LEGO, Love Python” 🎬

In Episode 5, we’ll explore **Abstract Base Classes and Protocols** - or as I like to call it, “How LEGO Headquarters Enforces the Rules!” We’ll learn about contracts, interfaces, and making sure every brick follows the master plan.

Until then, keep your interfaces clean, your duck typing quacking, and your operators overloaded with joy!

Happy building! 🏗️✨

-----

*P.S. - Polymorphism is like the Universal LEGO Stud System. It doesn’t matter if you’re building with 1958 bricks or 2026 bricks - they all click together! That’s 68 years of backward compatibility. THAT’S the power of a good interface!* 🧱🚀

-----

**🎯 Key Takeaways:**

- **Polymorphism** = same method name, different behaviors for different types
- **Duck typing** = if it has the method, it works (no type checking needed!)
- **Method overriding** = child classes customize parent methods
- **Operator overloading** = make your classes work with `+`, `-`, `*`, etc.
- Use polymorphism to write **flexible, extensible** code
- Don’t force polymorphism where it doesn’t belong
- Real-world use: multi-cloud deployments, plugin systems, game entities
- LEGO studs > everything 🏆
