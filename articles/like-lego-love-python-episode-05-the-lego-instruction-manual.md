---
title: "Like LEGO? Love Python! 🧱🐍 Ep.5"
published: true
description: "Episode 5: The LEGO Instruction Manual (Abstraction) - When LEGO HQ tells you WHAT to build, but not HOW to build it!"
tags: [python, beginners, oop, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/like-lego-love-python-episode-05.png"
series: "Like LEGO? Love Python!»"
canonical_url: "»"
organization: "the-software-s-journey"
---

## Episode 5: The LEGO Instruction Manual (Abstraction)

### Welcome Back, Master Builder! 📋

Remember those iconic LEGO instruction manuals? You know, the ones that show you **WHAT** the final creation should look like and **WHAT** pieces you need, but don’t care about **HOW** you physically pick up each brick or **WHERE** you store them while building?

That’s **abstraction** in a nutshell! 🥜

Think about it: Every LEGO set has an instruction manual that says “You MUST have a base,” “You MUST have walls,” and “You MUST have a roof.” But whether you build those walls with red bricks, blue bricks, or even use Technic pieces? That’s YOUR implementation detail!

LEGO HQ doesn’t care HOW you build it, as long as it WORKS and looks like the picture on the box. That’s the magic of abstraction - defining the WHAT without dictating the HOW! 🎯

## The LEGO Headquarters Blueprint 📐

Imagine you work at LEGO Headquarters in Billund, Denmark. Your job? Create the ULTIMATE building standard that EVERY LEGO factory worldwide MUST follow.

You don’t care if the factory in Hungary uses robots or the factory in Mexico uses conveyor belts - you just care that they ALL make bricks that connect perfectly!

```python
from abc import ABC, abstractmethod

class LEGOFactory(ABC):
    """
    The OFFICIAL LEGO factory blueprint from HQ!
    Every factory MUST follow this, no exceptions! 📋
    """
    
    @abstractmethod
    def produce_brick(self, color, size):
        """
        MANDATORY: Every factory must make bricks!
        HOW you make them? Your problem! 🏭
        """
        pass
    
    @abstractmethod
    def quality_check(self, brick):
        """
        MANDATORY: Every brick must pass quality control!
        LEGO's reputation depends on it! ✅
        """
        pass
    
    @abstractmethod
    def package_product(self, bricks):
        """
        MANDATORY: Products must be packaged!
        Can't ship loose bricks in a truck! 📦
        """
        pass
    
    def print_lego_logo(self):
        """
        OPTIONAL: HQ provides this for free!
        All factories get the same logo printer! 🏷️
        """
        return "🧱 LEGO® - Official LEGO Group Product"

class DenmarkFactory(LEGOFactory):
    """The original LEGO factory - high-tech robots! 🤖"""
    
    def __init__(self):
        self.location = "Billund, Denmark"
        self.method = "Robotic Assembly"
    
    def produce_brick(self, color, size):
        return f"🤖 Robot in {self.location} molding {color} {size} brick with PRECISION!"
    
    def quality_check(self, brick):
        return f"🔬 Laser scanner checking {brick} - within 0.002mm tolerance!"
    
    def package_product(self, bricks):
        return f"📦 Automated packaging system boxing {len(bricks)} bricks - Denmark style!"

class MexicoFactory(LEGOFactory):
    """LEGO factory in Mexico - efficient conveyor system! 🚂"""
    
    def __init__(self):
        self.location = "Monterrey, Mexico"
        self.method = "Conveyor Assembly"
    
    def produce_brick(self, color, size):
        return f"🚂 Conveyor belt in {self.location} producing {color} {size} brick at high speed!"
    
    def quality_check(self, brick):
        return f"👀 Quality inspector checking {brick} - looks perfect, ¡excelente!"
    
    def package_product(self, bricks):
        return f"📦 Manual packaging with care - {len(bricks)} bricks ready for América!"

class ChinaFactory(LEGOFactory):
    """LEGO factory in China - massive scale production! 🏭"""
    
    def __init__(self):
        self.location = "Jiaxing, China"
        self.method = "Hybrid Assembly"
    
    def produce_brick(self, color, size):
        return f"⚙️ Hybrid system in {self.location} mass-producing {color} {size} brick!"
    
    def quality_check(self, brick):
        return f"🎯 Multi-stage QC checking {brick} - meeting global standards!"
    
    def package_product(self, bricks):
        return f"📦 High-volume packaging - {len(bricks)} bricks sealed for 亚洲 market!"

# Here's the MAGIC - LEGO HQ doesn't care about implementation!
def manufacture_product(factory: LEGOFactory, color: str, quantity: int):
    """
    This function works with ANY LEGO factory!
    It doesn't know (or care) HOW each factory works! 🎯
    """
    print(f"\n{'='*60}")
    print(f"Manufacturing {quantity} {color} bricks...")
    print(f"{'='*60}")
    
    bricks = []
    for i in range(quantity):
        # Each factory produces differently!
        brick = factory.produce_brick(color, "2x4")
        print(brick)
        
        # Each factory quality checks differently!
        qc_result = factory.quality_check(f"brick #{i+1}")
        print(qc_result)
        
        bricks.append(f"{color} brick #{i+1}")
    
    # Each factory packages differently!
    package_result = factory.package_product(bricks)
    print(package_result)
    
    # But the logo is the SAME everywhere!
    print(factory.print_lego_logo())
    print(f"{'='*60}\n")

# Let's run all three factories!
denmark = DenmarkFactory()
mexico = MexicoFactory()
china = ChinaFactory()

# Same function - THREE different implementations!
manufacture_product(denmark, "red", 2)
manufacture_product(mexico, "blue", 2)
manufacture_product(china, "yellow", 2)
```

**What just happened?!** 🤯

The `manufacture_product()` function doesn’t care if it’s talking to Denmark, Mexico, or China! It just knows:

- “You can make bricks? Great!”
- “You can check quality? Perfect!”
- “You can package? Excellent!”

The **WHAT** is defined (those three methods), but the **HOW** is left to each factory. That’s abstraction! 🎯

## Can’t Skip Leg Day… Or Abstract Methods! 🏋️

Here’s where Python gets strict (in a good way). If LEGO HQ says “You MUST have quality control,” you can’t just… not have quality control!

```python
from abc import ABC, abstractmethod

class LEGOFactory(ABC):
    @abstractmethod
    def produce_brick(self, color, size):
        pass
    
    @abstractmethod
    def quality_check(self, brick):
        pass

# This lazy factory forgot quality check!
class LazyFactory(LEGOFactory):
    """Uh oh... someone didn't read the manual! 📋"""
    
    def produce_brick(self, color, size):
        return f"Making {color} brick... kinda... 🤷"
    
    # Oops! Forgot quality_check()!

# Try to create it...
try:
    lazy = LazyFactory()
except TypeError as e:
    print(f"❌ ERROR: {e}")
    # TypeError: Can't instantiate abstract class LazyFactory 
    # with abstract method quality_check
```

Python literally REFUSES to create your factory if you skip the required methods! 🚫

It’s like showing up to build a LEGO Millennium Falcon but forgetting the cockpit. LEGO HQ says: “Nope! Not a complete Millennium Falcon! Try again!” 🚀

## The LEGO Set Box: Abstraction in Real Life 📦

Every LEGO set box shows you:

- **WHAT** the final creation looks like ✅
- **WHAT** pieces are included ✅
- **WHAT** age range it’s for ✅

But it DOESN’T show you:

- **HOW** to physically pick up each piece ❌
- **WHERE** you should sit while building ❌
- **WHEN** you should take breaks ❌

That’s abstraction! The box is an “abstract base class” for the building experience!

```python
from abc import ABC, abstractmethod

class LEGOSet(ABC):
    """The abstract concept of a LEGO set - defines WHAT, not HOW!"""
    
    def __init__(self, set_number, name, pieces):
        self.set_number = set_number
        self.name = name
        self.pieces = pieces
        self.is_built = False
    
    @abstractmethod
    def get_theme(self):
        """WHAT theme is this set? MUST be defined!"""
        pass
    
    @abstractmethod
    def get_age_range(self):
        """WHAT age range? MUST be defined!"""
        pass
    
    @abstractmethod
    def build_instructions(self):
        """WHAT are the building steps? MUST be defined!"""
        pass
    
    def print_box_info(self):
        """HOW to print? We define this for ALL sets!"""
        return f"""
        ╔══════════════════════════════════════╗
        ║  LEGO® Set #{self.set_number}
        ║  {self.name}
        ║  {self.pieces} pieces
        ║  Theme: {self.get_theme()}
        ║  Age: {self.get_age_range()}
        ╚══════════════════════════════════════╝
        """

class MillenniumFalcon(LEGOSet):
    """The legendary Star Wars ship! 🚀"""
    
    def __init__(self):
        super().__init__("75257", "Millennium Falcon", 1351)
    
    def get_theme(self):
        return "Star Wars ⭐"
    
    def get_age_range(self):
        return "9+ (but really for adults 😅)"
    
    def build_instructions(self):
        return [
            "Step 1: Build the cockpit with Han and Chewie",
            "Step 2: Add the iconic radar dish",
            "Step 3: Complete the legendary ship!",
            "Step 4: Make 'pew pew' sounds (mandatory! 🔫)"
        ]

class HogwartsCastle(LEGOSet):
    """The magical castle from Harry Potter! 🏰"""
    
    def __init__(self):
        super().__init__("71043", "Hogwarts Castle", 6020)
    
    def get_theme(self):
        return "Harry Potter ⚡"
    
    def get_age_range(self):
        return "16+ (this is SERIOUS magic!)"
    
    def build_instructions(self):
        return [
            "Step 1: Lay the foundation of Hogwarts",
            "Step 2: Build the Great Hall",
            "Step 3: Add the towers and turrets",
            "Step 4: Place the minifigs (including Dumbledore!)",
            "Step 5: Wave your wand (not included 🪄)"
        ]

class CreatorRocket(LEGOSet):
    """A 3-in-1 space shuttle! 🚀"""
    
    def __init__(self):
        super().__init__("31134", "Space Shuttle", 510)
    
    def get_theme(self):
        return "Creator 3-in-1 🌟"
    
    def get_age_range(self):
        return "6-12 (perfect for future astronauts!)"
    
    def build_instructions(self):
        return [
            "BUILD 1: Space Shuttle with landing gear",
            "BUILD 2: Astronaut figure (same pieces!)",
            "BUILD 3: Futuristic spaceship (most pieces!)",
            "Rebuild as many times as you want! ♻️"
        ]

# Function that works with ANY LEGO set!
def present_set(lego_set: LEGOSet):
    """Display any LEGO set - abstraction makes this work!"""
    print(lego_set.print_box_info())
    
    print("📋 Building Instructions:")
    for step in lego_set.build_instructions():
        print(f"   {step}")
    print()

# Works with ALL sets!
falcon = MillenniumFalcon()
hogwarts = HogwartsCastle()
rocket = CreatorRocket()

present_set(falcon)
present_set(hogwarts)
present_set(rocket)
```

Notice how `present_set()` doesn’t care WHAT kind of set it receives? As long as it’s a `LEGOSet` with the required methods, it works! 🎯

## Abstract Properties: The LEGO Brick Dimensions 📏

Some things about LEGO bricks are ALWAYS required, like their dimensions! That’s what abstract properties are for.

```python
from abc import ABC, abstractmethod

class LEGOBrick(ABC):
    """Every LEGO brick MUST have these properties!"""
    
    @property
    @abstractmethod
    def stud_count(self):
        """How many studs on top? REQUIRED!"""
        pass
    
    @property
    @abstractmethod
    def height(self):
        """How tall is it? REQUIRED!"""
        pass
    
    @abstractmethod
    def connect_sound(self):
        """What sound does it make? REQUIRED!"""
        pass
    
    def description(self):
        """We can implement this for ALL bricks!"""
        return f"LEGO brick with {self.stud_count} studs, {self.height}mm tall"

class StandardBrick(LEGOBrick):
    """Your classic 2x4 brick!"""
    
    @property
    def stud_count(self):
        return 8  # 2x4 = 8 studs
    
    @property
    def height(self):
        return 9.6  # Standard LEGO height in mm
    
    def connect_sound(self):
        return "*SATISFYING CLICK* 🔊"

class TechnicBrick(LEGOBrick):
    """A Technic brick with holes!"""
    
    @property
    def stud_count(self):
        return 8  # Also 2x4
    
    @property
    def height(self):
        return 9.6
    
    def connect_sound(self):
        return "*CLICK-SNAP* (with axle sound) ⚙️"

class Baseplate(LEGOBrick):
    """A massive 32x32 baseplate!"""
    
    @property
    def stud_count(self):
        return 1024  # 32 x 32 = HUGE!
    
    @property
    def height(self):
        return 1.6  # Much flatter than regular bricks
    
    def connect_sound(self):
        return "*HEAVY FOUNDATION THUD* 🏗️"

def test_brick(brick: LEGOBrick):
    """Test any LEGO brick - abstraction at work!"""
    print(f"Testing: {brick.description()}")
    print(f"Sound when connecting: {brick.connect_sound()}")
    print()

# All three work with the same function!
test_brick(StandardBrick())
test_brick(TechnicBrick())
test_brick(Baseplate())
```

## The Multi-Factory Notification System 🏭📢

Let’s build something REALLY practical - a notification system that LEGO factories use to alert staff!

```python
from abc import ABC, abstractmethod
from typing import List

class Notification(ABC):
    """
    Abstract notification system for LEGO factories!
    Defines WHAT notifications must do, not HOW they do it!
    """
    
    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        """WHAT: Send a notification - MUST be implemented!"""
        pass
    
    @abstractmethod
    def validate_recipient(self, recipient: str) -> bool:
        """WHAT: Validate recipient format - MUST be implemented!"""
        pass
    
    def prepare_message(self, message: str) -> str:
        """HOW: We provide default message formatting!"""
        return f"🧱 [LEGO Alert] {message}"
    
    def log_notification(self, recipient: str, status: str):
        """HOW: We provide default logging!"""
        print(f"📝 Log: Notification to {recipient} - {status}")

class EmailNotification(Notification):
    """Send alerts via email - for office workers! 📧"""
    
    def send(self, recipient: str, message: str) -> bool:
        if not self.validate_recipient(recipient):
            self.log_notification(recipient, "FAILED - invalid email")
            return False
        
        formatted_message = self.prepare_message(message)
        print(f"📧 Email to {recipient}:")
        print(f"   Subject: LEGO Factory Alert")
        print(f"   Body: {formatted_message}")
        self.log_notification(recipient, "SUCCESS")
        return True
    
    def validate_recipient(self, recipient: str) -> bool:
        return "@lego.com" in recipient

class SMSNotification(Notification):
    """Send alerts via SMS - for warehouse workers! 📱"""
    
    def send(self, recipient: str, message: str) -> bool:
        if not self.validate_recipient(recipient):
            self.log_notification(recipient, "FAILED - invalid phone")
            return False
        
        # SMS needs shorter messages!
        short_message = message[:100]  # Max 100 chars
        formatted_message = self.prepare_message(short_message)
        print(f"📱 SMS to {recipient}:")
        print(f"   {formatted_message}")
        self.log_notification(recipient, "SUCCESS")
        return True
    
    def validate_recipient(self, recipient: str) -> bool:
        return recipient.startswith("+") and len(recipient) >= 10

class FactoryScreenNotification(Notification):
    """Display on factory floor screens - for all workers! 🖥️"""
    
    def send(self, recipient: str, message: str) -> bool:
        if not self.validate_recipient(recipient):
            self.log_notification(recipient, "FAILED - invalid screen ID")
            return False
        
        formatted_message = self.prepare_message(message)
        print(f"🖥️  FACTORY SCREEN {recipient}:")
        print(f"   {'='*50}")
        print(f"   ⚠️  {formatted_message}")
        print(f"   {'='*50}")
        self.log_notification(recipient, "SUCCESS")
        return True
    
    def validate_recipient(self, recipient: str) -> bool:
        return recipient.startswith("SCREEN-") and len(recipient) == 9

class EmergencyAlertSystem:
    """
    The main alert system - uses ABSTRACTION!
    Doesn't care HOW notifications work, just that they DO!
    """
    
    def __init__(self):
        self.channels: List[Notification] = []
    
    def register_channel(self, channel: Notification):
        """Add a notification channel (email, SMS, screen, etc.)"""
        self.channels.append(channel)
        print(f"✅ Registered: {channel.__class__.__name__}")
    
    def broadcast_alert(self, alert_type: str, message: str, recipients: dict):
        """
        Send emergency alert through ALL channels!
        Thanks to abstraction, we don't care about implementation details!
        """
        print(f"\n{'🚨 '*20}")
        print(f"EMERGENCY BROADCAST: {alert_type}")
        print(f"{'🚨 '*20}\n")
        
        for channel in self.channels:
            channel_name = channel.__class__.__name__.replace("Notification", "").lower()
            recipient = recipients.get(channel_name)
            
            if recipient:
                success = channel.send(recipient, message)
                if success:
                    print(f"   ✅ {channel_name.upper()} alert sent!")
                else:
                    print(f"   ❌ {channel_name.upper()} alert failed!")
            print()

# Set up the emergency alert system!
alert_system = EmergencyAlertSystem()

# Register all notification channels
alert_system.register_channel(EmailNotification())
alert_system.register_channel(SMSNotification())
alert_system.register_channel(FactoryScreenNotification())

# Define recipients for each channel
recipients = {
    "email": "safety.manager@lego.com",
    "sms": "+4512345678",
    "factoryscreen": "SCREEN-01"
}

# EMERGENCY! Broadcast to everyone!
alert_system.broadcast_alert(
    "PRODUCTION HALT",
    "Quality control detected defective molds in production line 3. All production stopped for inspection.",
    recipients
)

# Another alert!
alert_system.broadcast_alert(
    "SAFETY DRILL",
    "Fire drill in 10 minutes. Please evacuate to assembly point B.",
    recipients
)
```

**The Power Here:** 🎯

The `EmergencyAlertSystem` doesn’t know (or care) about:

- Email servers
- SMS gateways
- Factory screen protocols

It just knows: “You can send notifications? Great! Do your thing!” That’s the beauty of abstraction!

## Protocols: The Unofficial LEGO Compatible System 🔄

Python 3.8+ introduced **Protocols** - a way to say “if it looks like a LEGO brick and clicks like a LEGO brick, it IS a LEGO brick” WITHOUT needing inheritance!

```python
from typing import Protocol

class Connectable(Protocol):
    """
    Protocol: Anything that can connect to LEGO!
    No inheritance required - just implement the methods!
    """
    
    def connect(self) -> str:
        """Must have a connect method!"""
        ...
    
    def disconnect(self) -> str:
        """Must have a disconnect method!"""
        ...

# Official LEGO brick
class LEGOBrick:
    def connect(self) -> str:
        return "Official LEGO brick connected! *CLICK* ✅"
    
    def disconnect(self) -> str:
        return "LEGO brick removed! *POP* 🔓"

# Compatible third-party brick (not inheriting anything!)
class MegaBloksBrick:
    def connect(self) -> str:
        return "Mega Bloks brick connected! *click* ⚠️"
    
    def disconnect(self) -> str:
        return "Mega Bloks brick removed! *pop* 🔓"

# Even non-brick things can be "connectable"!
class USBBrick:
    """A weird USB brick device that connects to bricks!"""
    def connect(self) -> str:
        return "USB brick connected! Ready to transfer builds! 🔌"
    
    def disconnect(self) -> str:
        return "USB safely ejected! 💾"

def attach_to_build(item: Connectable) -> None:
    """
    Works with ANYTHING that matches the Connectable protocol!
    Doesn't care about inheritance - just behavior!
    """
    print(item.connect())

# All three work - they match the protocol!
attach_to_build(LEGOBrick())
attach_to_build(MegaBloksBrick())
attach_to_build(USBBrick())
```

**The Protocol Philosophy:** If it walks like a LEGO and talks like a LEGO, Python treats it like a LEGO! 🦆

## When Abstraction Goes Wrong: Too Many Rules! 📜

Just like you can have TOO MANY LEGO building restrictions, you can over-abstract!

```python
from abc import ABC, abstractmethod

# ❌ BAD: Way too abstract!
class OverengineeredBrick(ABC):
    @abstractmethod
    def get_color(self): pass
    
    @abstractmethod
    def get_size(self): pass
    
    @abstractmethod
    def get_weight(self): pass
    
    @abstractmethod
    def get_material(self): pass
    
    @abstractmethod
    def get_manufacturing_date(self): pass
    
    @abstractmethod
    def get_factory_location(self): pass
    
    @abstractmethod
    def get_batch_number(self): pass
    
    @abstractmethod
    def get_quality_score(self): pass
    
    # 😫 30 more abstract methods...
    # NOBODY wants to implement all of these!

# ✅ GOOD: Just enough abstraction!
class SimpleBrick(ABC):
    @abstractmethod
    def connect(self): pass
    
    @abstractmethod
    def get_dimensions(self): pass
    
    # That's it! Easy to implement!
```

**LEGO’s Golden Rule:** Keep it simple! If builders need a PhD to understand your instructions, you’ve abstracted too much! 🎓

## The LEGO Abstraction Philosophy 🧘

Just like LEGO’s design principles:

1. **Universal Interface** - All bricks MUST connect (abstract method)
1. **Specialized Implementation** - Each brick connects uniquely (concrete implementation)
1. **Quality Standards** - Non-negotiable requirements (abstract properties)
1. **Flexibility** - Builders choose HOW to use bricks (duck typing)
1. **Simplicity** - Instructions are clear, not overwhelming (good abstraction)

## Your Mission, Should You Choose to Accept It 🎯

Build an abstract LEGO Theme Park system!

Create:

1. `Attraction` abstract base class with:
- `operate()` method (abstract)
- `get_capacity()` method (abstract)
- `safety_check()` method (abstract)
- `print_ticket()` method (concrete - same for all!)
1. Implement at least 3 attractions:
- `RollerCoaster` - thrilling and fast! 🎢
- `FerrisWheel` - slow and scenic! 🎡
- `WaterSlide` - wet and wild! 💦
1. Create a `ThemePark` class that:
- Manages multiple attractions (using abstraction!)
- Runs safety checks on all attractions
- Can operate all attractions at once

Bonus: Add a `Protocol` for things that can play music (attractions, food stands, etc.) 🎵

## Next Time on “Like LEGO? Love Python” 🎬

In Episode 6, we’ll explore **Composition vs Inheritance** - or as I like to call it, “Building with Bricks vs Building with Pre-Made Sections!” We’ll learn when to inherit from classes and when to just… stick objects together!

Until then, keep your abstractions clean, your interfaces simple, and your implementation details hidden!

Happy building! 🏗️✨

-----

*P.S. - Abstraction is like the LEGO clutch power specification. Every brick since 1958 MUST have it. You don’t care HOW each brick achieves perfect clutch power - you just need to know it WORKS. That’s 68 years of perfect abstraction!* 🧱🔒

-----

**🎯 Key Takeaways:**

- **Abstraction** = defining WHAT without specifying HOW
- **ABC (Abstract Base Class)** = Python’s way to enforce contracts
- **@abstractmethod** = “you MUST implement this!”
- **Abstract properties** = required attributes for all subclasses
- **Protocols** = structural typing without inheritance (duck typing++)
- Use abstraction to create **flexible, maintainable** systems
- Don’t over-abstract - keep it simple and practical!
- Real-world use: plugin systems, multi-cloud providers, notification systems
- LEGO clutch power > everything 🏆
