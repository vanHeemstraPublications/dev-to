---
title: "Like Stories? Love Python! 📖🐍 Ep.2"
published: false
description: "Learn the Factory design pattern through magical sorting and cinematic character creation - because sometimes objects need to cast themselves!"
tags: [python, beginners, tutorial, designpatterns]
series: "Like Stories? Love Python!"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/like-stories-love-python-episode-02.png"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 2: The Sorting Hat (Factory Pattern)

Accompanying source code repository: [`Learning Python Object-Oriented`](https://github.com/vanHeemstraSystems/learning-python-object-oriented)

*Welcome back, storytellers. Last time we talked about the One Ring - the Singleton. Today? Today we’re talking about something even more magical: the art of character creation itself.*

### The One-Line Logline

**“Create objects without specifying their exact class - delegate the decision to a factory that knows which type to instantiate.”**

This is your **casting agency**, your **character generator**, your **type system on steroids**. Instead of hardcoding “create a Warrior,” you say “create whatever makes sense for this situation” and let the Factory decide.

-----

### The Short Story (The Elevator Pitch)

Picture this: A master craftsman’s workshop receives orders by description, not by blueprint. “I need something to cut wood,” says one customer. “I need something to drive nails,” says another. The craftsman - our **factory foreman** - doesn’t ask them to specify “Model X Saw, Serial AZ-500” or “Type 3 Hammer, Edition 2.1.” No. He *interprets the need* and hands them the right tool. Same workshop, different outputs, intelligent selection.

That’s your **premise**. The factory knows what to create so you don’t have to.

-----

### The Fictional Match 🎬

**The Sorting Hat from *Harry Potter and the Philosopher’s Stone* ([IMDB: tt0241527](https://www.imdb.com/title/tt0241527/))**

*Folks, this is PERFECT. Let me paint you the scene.*

It’s the Great Hall at Hogwarts. Scared first-years line up. They don’t choose their house - they don’t say “I hereby instantiate myself as a Gryffindor object.” No! They sit down, the Sorting Hat goes on their head, and the Hat - the **FACTORY** - examines their attributes, their **character traits**, their internal state, and *decides* which type of student-object they should become.

Chris Columbus and Steve Kloves understood something profound when they adapted J.K. Rowling’s work: **character typing shouldn’t be self-assigned**. The protagonist doesn’t know what they are yet. They need an **external intelligence**, a **higher-order function**, to make that determination.

Harry could have chosen Slytherin. The Hat offered it. But the Factory Pattern - embodied in that sentient sorting mechanism - took Harry’s inputs (“not Slytherin, not Slytherin”) and produced the correct output type: Gryffindor.

That close-up on the Hat’s face (brilliant practical effects, by the way - no CGI, just puppetry and voice acting) shows us the **decision-making process** externalized. The Factory thinking. The Factory choosing.

**One input pipeline. Four possible output types. Perfect abstraction.**

-----

### The Robert McKee Story Breakdown

Robert McKee teaches us in “*Story*” that great narratives often feature a **mentor figure** who recognizes the protagonist’s true nature before the protagonist does themselves. Gandalf sees Frodo’s courage. Obi-Wan sees Luke’s potential. The Factory Pattern is your **narrative mentor** in code form.

Let’s break it down using McKee’s **story architecture**:

- **Protagonist**: The Client Code (needs an object but doesn’t know which specific type)
- **Desire (objective)**: Acquire the right tool for the job without hardcoding dependencies - the *want* is convenience, the *need* is flexibility
- **Antagonistic force**: **Tight coupling** and **rigid type systems** - the forces that demand “you must know exactly what you want before you ask for it”
- **Central conflict**: The **gap between abstraction and implementation** - needing to work with a concept (“something that processes payments”) without committing to a specific implementation (“PayPal version 2.3.1”)
- **Turning point** (The **Inciting Incident**): The moment you realize hardcoding `new PayPal()` everywhere makes your code brittle and inflexible - the crisis that demands a better way
- **Resolution** (The **Climax**): The factory returns the perfect object type based on runtime conditions - **dynamic casting** achieved, flexibility restored
- **Controlling idea** (The **Thematic Statement**): *Wisdom comes from delegation* - sometimes the smartest decision is letting someone else make the decision

This is McKee’s **principle of progressive complication** in action. The Factory Pattern doesn’t simplify object creation - it *sophisticates* it, adding a layer of intelligence between need and fulfillment.

-----

### Real-World Implementations (The Production Examples)

You know what’s brilliant? Factories are *everywhere* in **production systems** once you start looking. These are your **marquee applications**, your **tent-pole implementations**:

- **Cloud resource provisioners** - “Give me compute” becomes VM, container, or serverless function based on context
- **Payment gateways** - One interface, multiple processors (PayPal, Stripe, crypto) selected at runtime
- **Logging frameworks** - ConsoleLogger, FileLogger, CloudLogger - factory picks based on environment
- **Database connections** - PostgreSQL, MySQL, SQLite - factory chooses based on configuration
- **UI component libraries** - Button factory returns different implementations for web, mobile, desktop
- **Plugin systems** - Load the right plugin class based on file type or user selection

Every good **production pipeline** has a factory somewhere in its **workflow**.

-----

### The Minimal Python Example (The Visual Effects Sequence)

*Alright, time to go from storyboard to principal photography. Let me show you the magic.*

Here’s the Factory Pattern in pure Python - no special effects, just **solid craft**:

```python
# ACT ONE: THE SETUP - Define your character archetypes
class CloudResource:
    """Base class - our CHARACTER PROTOTYPE"""
    def describe(self):
        raise NotImplementedError("Subclasses must implement describe()")

class VM(CloudResource):
    """Virtual Machine - the WARRIOR archetype"""
    def __init__(self, cpu, memory):
        self.cpu = cpu
        self.memory = memory
    
    def describe(self):
        return f"VM with {self.cpu} CPUs and {self.memory}GB RAM"

class Storage(CloudResource):
    """Cloud Storage - the SUPPORT CHARACTER archetype"""
    def __init__(self, size):
        self.size = size
    
    def describe(self):
        return f"Storage with {self.size}GB capacity"

class Database(CloudResource):
    """Database Instance - the SAGE archetype"""
    def __init__(self, engine, size):
        self.engine = engine
        self.size = size
    
    def describe(self):
        return f"{self.engine} database with {self.size}GB"

# ACT TWO: THE FACTORY - Your casting director
class ResourceFactory:
    """
    The SORTING HAT. The CASTING AGENCY. The DECISION MAKER.
    
    This is your intelligence layer - it knows what to create
    based on the input parameters. The client code doesn't need
    to know about VM vs Storage vs Database classes.
    """
    
    @staticmethod
    def create_resource(resource_type, **kwargs):
        """
        The factory method - your INSTANTIATION LOGIC
        
        This is where the magic happens. Based on a simple string,
        we return completely different object types. It's like
        method acting - same stage, different characters.
        """
        if resource_type == "vm":
            # The warrior enters stage left
            return VM(kwargs['cpu'], kwargs['memory'])
        elif resource_type == "storage":
            # The support character takes their mark
            return Storage(kwargs['size'])
        elif resource_type == "database":
            # The sage joins the ensemble
            return Database(kwargs['engine'], kwargs['size'])
        else:
            # The casting director rejects the audition
            raise ValueError(f"Unknown resource type: {resource_type}")

# ACT THREE: THE PAYOFF - Watch the factory work its magic
# Client code doesn't know about specific classes - ABSTRACTION ACHIEVED
resources = [
    ResourceFactory.create_resource("vm", cpu=4, memory=16),
    ResourceFactory.create_resource("storage", size=1000),
    ResourceFactory.create_resource("database", engine="PostgreSQL", size=500)
]

# The ensemble performs - each character plays their role
for resource in resources:
    print(resource.describe())

# Output:
# VM with 4 CPUs and 16GB RAM
# Storage with 1000GB capacity
# PostgreSQL database with 500GB
```

**The Director’s Commentary:**

Here’s your **behind-the-scenes breakdown**, the **making-of documentary**:

1. **Base class** (`CloudResource`) - Your **character prototype**, the fundamental archetype
1. **Concrete classes** (VM, Storage, Database) - Your **specific character types**, each with unique attributes
1. **Factory class** - The **intelligent selector**, the sorting mechanism that interprets needs
1. **Static method** - No instance required, pure **utility function** - this is your **standalone casting call**
1. **Client code** - Works with the **abstract interface**, never touches concrete classes directly

This is **composition over inheritance** in action. This is **loose coupling**. This is **Hollywood magic** where the audience (client code) doesn’t see the casting director (factory) working behind the scenes.

-----

### When Should You Use Factory? (The Green Light Decision)

McKee would tell you: not every story needs the same narrative structure. Same with patterns. Know when to deploy the **Factory Pattern** in your **production environment**:

**✅ Green-lit projects (Good use cases):**

- Object creation is **complex** with multiple decision points (multi-step casting process)
- You need to **decouple** client code from concrete classes (avoid tight coupling, the death of flexibility)
- The exact type depends on **runtime conditions** (environment variables, user input, configuration)
- You’re building a **plugin system** or **extensible framework** (future casting calls for characters not yet written)
- Multiple related classes share a common interface (the ensemble cast model)

**❌ Development hell (When to avoid):**

- Simple object creation that won’t change (Don’t hire a casting director for a one-person show)
- Only one concrete type exists (Factory with one product is **over-engineering**)
- The type decision is obvious and won’t vary (No need for the Sorting Hat if everyone’s a Gryffindor)

-----

### The Advanced Technique: Factory Method Pattern (The Auteur Approach)

*Now let me show you the sophisticated version - this is your **art-house cinema** approach.*

Instead of a static factory, you can use **inheritance** to let subclasses decide what to create. This is the **Factory Method Pattern** - a close cousin, slightly different **narrative structure**:

```python
from abc import ABC, abstractmethod

class Application(ABC):
    """Abstract creator - the PRODUCTION COMPANY blueprint"""
    
    @abstractmethod
    def create_document(self):
        """Factory method - each studio creates different content"""
        pass
    
    def new_document_workflow(self):
        """Template method - the STANDARD PRODUCTION WORKFLOW"""
        doc = self.create_document()  # Let subclass decide the type
        doc.open()
        return doc

class WordProcessor(Application):
    """Concrete creator - produces TEXT DOCUMENTS"""
    def create_document(self):
        return TextDocument()

class SpreadsheetApp(Application):
    """Concrete creator - produces SPREADSHEETS"""
    def create_document(self):
        return Spreadsheet()

class Document(ABC):
    """Product interface - the CONTENT ARCHETYPE"""
    @abstractmethod
    def open(self):
        pass

class TextDocument(Document):
    """Concrete product - the NARRATIVE MEDIUM"""
    def open(self):
        return "Opening text document..."

class Spreadsheet(Document):
    """Concrete product - the DATA MEDIUM"""
    def open(self):
        return "Opening spreadsheet..."

# Each app type creates its own document type - POLYMORPHIC CREATION
word_app = WordProcessor()
doc1 = word_app.new_document_workflow()  # Creates TextDocument

excel_app = SpreadsheetApp()
doc2 = excel_app.new_document_workflow()  # Creates Spreadsheet
```

This is your **auteur theory** in code - each director (subclass) puts their own spin on the creative process while following the same **production framework**.

-----

### The Plot Twist (The Third Act Reversal)

*Here’s what they don’t tell you in film school.*

The Factory Pattern is brilliant, but it can become a **bureaucratic nightmare** if you’re not careful. That factory class can grow into a **monolithic decision tree** with hundreds of if-statements - what we call a “God Factory” in the business. It’s like having one casting director for every film ever made. Eventually, they collapse under the weight.

Modern Python gives us **better tools** for some use cases:

**Dictionary-based factories** (The **lookup table** approach):

```python
RESOURCE_TYPES = {
    'vm': VM,
    'storage': Storage,
    'database': Database
}

def create_resource(resource_type, **kwargs):
    resource_class = RESOURCE_TYPES.get(resource_type)
    if not resource_class:
        raise ValueError(f"Unknown type: {resource_type}")
    return resource_class(**kwargs)
```

Cleaner. More **scalable**. Easier to extend. This is your **modular production system**.

But you need to understand the classic Factory Pattern because:

1. You’ll see it in **legacy codebases** everywhere (The film archives demand it)
1. The **concept** transcends the implementation (Silent film principles still apply in the streaming era)
1. It teaches you about **abstraction layers** and **delegation** (The fundamentals of architectural storytelling)
1. Job interviews love asking about it (The audition circuit expects fluency)

-----

**🎯 Key Takeaways (The Trailer Moments):**

- Factory Pattern **delegates object creation** to a specialized method or class
- Client code works with **abstract interfaces**, never concrete classes directly
- Perfect for situations where the **exact type depends on runtime conditions**
- The Sorting Hat is the perfect metaphor - **intelligent type selection**
- Use **dictionary-based factories** for simpler, more maintainable code in Python
- McKee’s mentor archetype applies - **the factory knows what you need before you do**
- Every good **plugin system** has a factory at its heart
- **Composition over inheritance** - build your ensemble cast dynamically

-----

**🎬 Coming Up Next: (The Post-Credits Tease)**

In Episode 3, we’re tackling the **Builder Pattern** - and I’m going to explain it through the lens of *Inception*.

How do you construct complex objects step-by-step? How do you build layered reality? How do you ensure each level is complete before moving to the next?

We’re going into **recursive construction**, **fluent interfaces**, and why Christopher Nolan’s dream-within-a-dream architecture is actually the perfect metaphor for the Builder Pattern.

Dreams within dreams. Objects within objects. **Nested construction**. It’s going to be wild.

Stay tuned, folks. We’re going deeper.

-----

*Hit that ❤️ if the Sorting Hat would put you in House Python! Drop a comment below with your favorite factory pattern use case - or suggest a movie metaphor I should explore next. Remember: every great film has a casting director. Every great codebase has a factory.*

*You’re not just writing code. You’re **assembling the ensemble cast** for your application’s epic saga.*

**Cut to black. Queue the theme music.**

-----

**Further Reading (The Bonus Features):**

- [Learning Python Object-Oriented - Design Patterns](https://github.com/vanHeemstraSystems/learning-python-object-oriented/tree/main/800) - *The source material, the original screenplay*
- Robert McKee - [*Story: Substance, Structure, Style, and the Principles of Screenwriting*](https://www.mckee.com/story/) - **Chapter on mentor archetypes**
- [Gang of Four Design Patterns](https://en.wikipedia.org/wiki/Design_Patterns) - **Factory Method and Abstract Factory patterns** (The definitive reference)
- [Python’s `abc` module](https://docs.python.org/3/library/abc.html) - **Abstract base classes** documentation
- [Harry Potter and the Philosopher’s Stone on IMDB](https://www.imdb.com/title/tt0241527/) - **The Sorting Hat scene** - character typing perfected
