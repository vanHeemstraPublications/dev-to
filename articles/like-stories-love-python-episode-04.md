---
title: "Like Stories? Love Python! 📖🐍 Ep.4"
published: true
description: "Learn the Adapter design pattern through The Martian’s survival ingenuity - because sometimes you need to make incompatible systems work together!"
tags: [python, beginners, tutorial, designpatterns]
series: "Like Stories? Love Python!"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/like-stories-love-python-episode-04.png"
canonical_url: “"
organization: "the-software-s-journey"
---

## Episode 4: Duct Tape Engineering (Adapter Pattern)

Accompanying source code repository: [`Learning Python Object-Oriented`](https://github.com/vanHeemstraSystems/learning-python-object-oriented)

*Alright storytellers, settle in. Today we’re talking about survival. About ingenuity. About making things work that were never meant to work together. This is MacGyver territory. This is Apollo 13. This is pure problem-solving cinema.*

### The One-Line Logline

**“Convert the interface of a class into another interface clients expect - make incompatible interfaces work together through a wrapper.”**

This is your **translation layer**, your **compatibility bridge**, your **duct tape and ingenuity solution**. When System A and System B speak different languages, the Adapter is your **universal translator**.

-----

### The Short Story (The Elevator Pitch)

Picture this: You’ve got a European power plug. You’re in an American hotel room. The wall outlet doesn’t fit your plug. Do you rewire the hotel? Do you buy a new laptop? No. You buy a **$5 adapter** that bridges the gap - same electricity, different interface, problem solved.

The adapter - our **interface converter** - doesn’t change what either side does. It just **translates** between them. Both sides remain unchanged. The adapter does all the work.

That’s your **premise**. Sometimes the best solution isn’t changing the systems - it’s **bridging between them**.

-----

### The Fictional Match 🎬

**Mark Watney’s Ingenuity from *The Martian* ([IMDB: tt3659388](https://www.imdb.com/title/tt3659388/))**

*Folks, Ridley Scott and Drew Goddard created a MASTERCLASS in the Adapter Pattern.*

Mark Watney is stranded on Mars. He’s got equipment designed for 30-day missions. He needs to survive for years. The systems around him weren’t built to work together the way he needs them to work.

So what does he do? He **adapts**. He doesn’t rebuild the Hab from scratch. He doesn’t redesign the rover. He creates **adapters** - clever interfaces that make existing systems work in new ways:

- Uses the RTG (radioisotope thermoelectric generator) as a heater - **adapting** a power source into a climate control system
- Harvests hydrogen from rocket fuel to create water - **adapting** propulsion chemistry for life support
- Modifies rover panels to extract Pathfinder - **adapting** mobility equipment for communication recovery
- Creates a potato farm in Martian soil + human waste - **adapting** waste management into agriculture

Every solution is the same pattern: **take what exists, don’t change its core function, but wrap it in a new interface that serves a different purpose**.

That iconic scene where he’s explaining his plan to the camera? “I’m going to have to **science the shit out of this**”? That’s Adapter Pattern as survival strategy. That’s **interface compatibility** as life-or-death problem-solving.

Ridley Scott frames these moments brilliantly - close-ups on Watney’s hands **jury-rigging connections**, wide shots showing **incompatible systems** working together. The **visual storytelling** emphasizes the bridge, the connection, the adaptation.

**Incompatible systems. Limited resources. Clever bridges. Survival.**

-----

### The Robert McKee Story Breakdown

Robert McKee teaches in “*Story*” about **constraint driving creativity** - how limitations force protagonists to be ingenious. The Adapter Pattern embodies this principle in code architecture.

Let’s break this down using McKee’s **narrative structure**:

- **Protagonist**: The Client Code (needs to use a legacy system or third-party library)
- **Desire (objective)**: Seamless integration without rewriting existing, tested code - the *want* is compatibility, the *need* is preservation
- **Antagonistic force**: **Interface mismatch** and **incompatible contracts** - when System A expects method `foo()` but System B only provides method `bar()`
- **Central conflict**: The **gap between expectation and reality** - “I need this functionality but the interface is all wrong”
- **Turning point** (The **Inciting Incident**): The moment you realize neither system can be changed - one is legacy production code, the other is a locked third-party library
- **Resolution** (The **Climax**): The adapter bridges both interfaces successfully - **translation achieved**, **integration complete**
- **Controlling idea** (The **Thematic Statement**): *Innovation comes through adaptation, not replacement* - sometimes the smartest move is working with what exists

McKee calls this **resourcefulness under pressure**. The Adapter Pattern is your protagonist using available tools creatively rather than demanding new tools. It’s **constraint-based problem solving**.

-----

### Real-World Implementations (The Production Examples)

The Adapter Pattern is **battle-tested** in production systems everywhere. These are your **practical applications**, your **proven techniques**:

- **Legacy system integration** - Wrap old SOAP APIs to look like modern REST interfaces
- **Database abstraction layers** - Make PostgreSQL, MySQL, SQLite all look identical to application code
- **Third-party library wrappers** - Adapt external APIs to match your internal conventions
- **Hardware interfaces** - Make different printer models all use the same print() interface
- **Payment gateway adapters** - Unified interface for Stripe, PayPal, Square despite different APIs
- **Cloud provider abstractions** - AWS, Azure, GCP adapted to common interface
- **Logging adapters** - Route Python’s logging to external systems (Sentry, CloudWatch, etc.)

Every time you’ve written “let me wrap this library to make it easier to use,” you were creating an **adapter**. Every abstraction layer? Adapter Pattern.

-----

### The Minimal Python Example (The Visual Effects Sequence)

*Time to build this bridge. Let’s go from blueprint to working prototype.*

Here’s the Adapter Pattern in **pure form** - elegant, effective, **production-ready**:

```python
# ACT ONE: THE OLD WORLD - Legacy system we can't change
class OldPrinter:
    """
    LEGACY SYSTEM - been in production for years.
    Thousands of documents depend on this interface.
    We CANNOT modify this class.
    """
    def print_document(self, text):
        """The old interface - simple, reliable"""
        return f"[OLD PRINTER] Printing: {text}"

# ACT TWO: THE NEW WORLD - Modern system with different interface
class NewPrinter:
    """
    MODERN SYSTEM - way more features, totally different API.
    This is the FUTURE, but it speaks a different language.
    """
    def advanced_print(self, text, color="black", duplex=False, quality="normal"):
        """
        The new interface - powerful but incompatible.
        Notice: different method name, different parameters.
        """
        mode = "duplex" if duplex else "simplex"
        return f"[NEW PRINTER] {color.upper()} {quality} {mode}: {text}"

# ACT THREE: THE BRIDGE - Adapter makes them compatible
class PrinterAdapter:
    """
    The DUCT TAPE SOLUTION. The INTERFACE TRANSLATOR.
    
    This adapter makes NewPrinter look like OldPrinter.
    Client code sees the old interface, gets new functionality.
    
    This is Mark Watney connecting incompatible systems.
    """
    
    def __init__(self, new_printer):
        """
        Wrap the new printer - we're ENCAPSULATING it,
        not changing it. The new printer remains untouched.
        """
        self.printer = new_printer
    
    def print_document(self, text):
        """
        ADAPT the interface - same method signature as OldPrinter,
        but internally calls the NewPrinter's different interface.
        
        This is the TRANSLATION LAYER. The BRIDGE.
        """
        # Use sensible defaults to adapt the simpler interface
        # to the more complex one
        return self.printer.advanced_print(
            text,
            color="black",      # Default values
            duplex=False,       # maintain compatibility
            quality="normal"
        )

# ACT FOUR: THE PAYOFF - Client code unchanged, new functionality gained
def print_report(printer, report_text):
    """
    CLIENT CODE - uses the old interface.
    This function was written years ago.
    It has NO IDEA if it's using old or new hardware.
    
    That's the BEAUTY of the adapter - TRANSPARENT COMPATIBILITY.
    """
    result = printer.print_document(report_text)
    print(result)

# THE ORIGINAL WORKFLOW - works perfectly
old_printer = OldPrinter()
print_report(old_printer, "Q4 Financial Report")
# Output: [OLD PRINTER] Printing: Q4 Financial Report

# THE ADAPTED WORKFLOW - same interface, new implementation
new_printer = NewPrinter()
adapted_printer = PrinterAdapter(new_printer)
print_report(adapted_printer, "Q4 Financial Report")
# Output: [NEW PRINTER] BLACK normal simplex: Q4 Financial Report

# BOTH work with the SAME client code!
# The client doesn't know. Doesn't care. Shouldn't need to.

# We can even iterate over different printer types - POLYMORPHISM
printers = [
    OldPrinter(),
    PrinterAdapter(NewPrinter())
]

for printer in printers:
    print_report(printer, "Test Document")
    # Both work! Same interface, different implementations.
```

**The Director’s Commentary:**

Here’s the **technical breakdown**, the **production secrets**:

1. **Target Interface** (`OldPrinter`) - This is what client code expects, the **established contract**
1. **Adaptee** (`NewPrinter`) - The incompatible system with different methods/parameters, the **new technology**
1. **Adapter** (`PrinterAdapter`) - The bridge class that implements the target interface while wrapping the adaptee, the **compatibility layer**
1. **Composition over Inheritance** - The adapter **contains** the new printer, doesn’t inherit from it. This is **delegation**, the superior approach.
1. **Transparent Integration** - Client code sees no difference, requires zero modifications. This is **backward compatibility** at its finest.

-----

### The Advanced Technique: Two-Way Adapter (The Bilingual Interpreter)

*Now let me show you the SOPHISTICATED VERSION - bi-directional adaptation.*

Sometimes you need the adapter to work both ways - old-to-new AND new-to-old:

```python
class BidirectionalAdapter:
    """
    The UNIVERSAL TRANSLATOR - speaks both languages fluently.
    Can adapt old interface to new, or new interface to old.
    """
    
    def __init__(self, printer):
        self.printer = printer
    
    def print_document(self, text):
        """Old interface - for legacy clients"""
        if isinstance(self.printer, OldPrinter):
            return self.printer.print_document(text)
        elif isinstance(self.printer, NewPrinter):
            return self.printer.advanced_print(text)
    
    def advanced_print(self, text, color="black", duplex=False, quality="normal"):
        """New interface - for modern clients"""
        if isinstance(self.printer, NewPrinter):
            return self.printer.advanced_print(text, color, duplex, quality)
        elif isinstance(self.printer, OldPrinter):
            # Simulate advanced features with old printer
            # (obviously limited, but provides interface compatibility)
            return self.printer.print_document(f"[{color}] {text}")

# Now ANY client can use ANY printer through ANY interface
adapter = BidirectionalAdapter(NewPrinter())
adapter.print_document("Old style")            # Works
adapter.advanced_print("New style", "blue")    # Also works
```

This is your **international co-production** - serves both markets simultaneously.

-----

### When Should You Use Adapter? (The Green Light Decision)

McKee teaches: **constraints breed creativity**. Use Adapter when constraints force you to be clever:

**✅ Green-lit projects (Good use cases):**

- **Integrating legacy code** you can’t modify (The museum pieces that still work)
- **Third-party libraries** with incompatible interfaces (External dependencies out of your control)
- **Multiple implementations** need unified interface (Database drivers, payment processors)
- **Testing substitution** - adapt complex dependencies for unit tests (Mock adapters, stub adapters)
- **API versioning** - support old and new API versions simultaneously (Backward compatibility requirements)

**❌ Development hell (When to avoid):**

- You control both systems - just align the interfaces! (Don’t adapt what you can refactor)
- The adaptation is complex and fragile (If the bridge needs its own architecture diagram, rethink)
- Performance is critical - adapters add indirection (Every layer costs clock cycles)
- You’re just being lazy about interface design (Plan your contracts, don’t paper over them)

-----

### The Plot Twist (The Third Act Reversal)

*Here’s what the textbooks don’t tell you.*

Adapters are **technical debt in disguise** if you’re not careful. They’re meant to be **temporary bridges** while you migrate systems, not **permanent architecture**. Every adapter is a layer of indirection, a translation overhead, a maintenance burden.

The best adapter is the one you **eventually remove** by aligning interfaces properly.

But sometimes adapters ARE the right permanent solution:

- When you genuinely can’t control the external system
- When multiple competing standards must coexist
- When migration isn’t worth the risk/cost

Modern Python gives us elegant adapter techniques:

**Protocol-based adaptation** (Python 3.8+):

```python
from typing import Protocol

class Printable(Protocol):
    """Define the expected interface - the CONTRACT"""
    def print_document(self, text: str) -> str: ...

# Now ANY class matching this interface works
# No inheritance needed - DUCK TYPING formalized
```

This is **structural typing** - if it has the right methods, it’s compatible. Adapters become optional.

-----

**🎯 Key Takeaways (The Trailer Moments):**

- Adapter Pattern **bridges incompatible interfaces** without changing either side
- Uses **composition** to wrap the adaptee and translate calls
- Perfect for **legacy integration** and **third-party library** wrappers
- *The Martian* is Adapter Pattern as survival strategy - **make it work**
- McKee’s **constraint-driven creativity** - limits force clever solutions
- **Transparent to clients** - they don’t know adaptation is happening
- Can be **bidirectional** - translate both ways
- Best used as **temporary bridge** during migration
- Python’s **protocols** and **duck typing** sometimes eliminate need

-----

**🎬 Coming Up Next: (The Post-Credits Tease)**

In Episode 5, we’re unwrapping the **Decorator Pattern** - and I’m going to explain it through *Iron Man*.

How do you add functionality without changing the core? How do you layer capabilities on top of existing objects? How does Tony Stark go from Mark I to Mark L armor?

We’re talking **runtime enhancement**, **wrapper chains**, and why each Iron Man suit upgrade is actually a decorator wrapping the previous version.

Same hero. Enhanced capabilities. **Layered power.**

Suit up, folks. It’s going to be spectacular.

-----

*If this adapter bridged the gap for you, hit that ❤️! Share your gnarliest integration challenge in the comments - let’s engineer some solutions together. Got a movie that perfectly illustrates a pattern? I’m all ears!*

*You’re not just coding. You’re **sciencing the shit** out of incompatible systems.*

**Cut. Print. That’s a wrap on Adapter.**

-----

**Further Reading (The Bonus Features):**

- [Learning Python Object-Oriented - Design Patterns](https://github.com/vanHeemstraSystems/learning-python-object-oriented/tree/main/800) - *The technical manual*
- Robert McKee - [*Story: Substance, Structure, Style, and the Principles of Screenwriting*](https://www.mckee.com/story/) - **Constraint and creativity chapter**
- [Gang of Four Design Patterns](https://en.wikipedia.org/wiki/Design_Patterns) - **Adapter Pattern** (The definitive source)
- [Python Protocols](https://docs.python.org/3/library/typing.html#typing.Protocol) - **Structural typing in Python**
- [Duck Typing](https://en.wikipedia.org/wiki/Duck_typing) - **Python’s interface philosophy**
- [The Martian on IMDB](https://www.imdb.com/title/tt3659388/) - **Adaptation as survival** - Scott’s engineering masterpiece
