---
title: "Like Stories? Love Python! 📖🐍 Ep.1"
published: false
description: "Learn the Singleton design pattern through epic tales and code - because there can be only one!"
tags: [python, beginners, tutorial, designpatterns]
series: "Like Stories? Love Python!"
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/like-stories-love-python-episode-01.png"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 1: The One Ring (Singleton Pattern)

Accompanying source code repository: [`Learning Python Object-Oriented`](https://github.com/vanHeemstraSystems/learning-python-object-oriented)

*Listen, folks. Pull up a chair. Let me tell you a story about the most powerful pattern in all of programming - and I’m going to tell it the way stories are MEANT to be told.*

### The One-Line Logline

**“Ensure only one instance of a class exists, no matter how many times someone tries to create it.”**

Think of it as the “highlander pattern” - there can be only one! This is your **high concept**. This is the pitch that gets the greenlight from the Python interpreter.

-----

### The Short Story (The Elevator Pitch)

Picture this: A kingdom’s ancient vault contains only one Master Key that opens all doors. Guards may come and go, requesting “the key,” but the vault keeper - our **gatekeeper character** - always hands them the same singular key, never a duplicate. If the key is already out, they wait. There’s only ever *one* Master Key in existence.

That’s your **premise**. That’s your **setup**. Now let me show you the **payoff**.

-----

### The Fictional Match 🎬

**The One Ring from *The Lord of the Rings: The Fellowship of the Ring* ([IMDB: tt0120737](https://www.imdb.com/title/tt0120737/))**

*Now here’s where it gets good.*

Sauron didn’t craft twenty rings of power for maximum evil - he made *one*. **One ring to rule them all.** Every character obsessing over it, fighting for it, questing for it - Frodo, Gollum, Boromir, Saruman - they’re all after the *same exact ring*. Not a copy. Not Ring Instance #47. THE Ring.

Peter Jackson understood something profound when he adapted Tolkien’s work: the **MacGuffin** - that’s Hitchcock’s term, by the way - isn’t just *a* ring. It’s THE ring. The **irreplaceable object** that drives the entire narrative engine. The **unity of the artifact** creates the unity of purpose across nine hours of cinematic storytelling.

That’s Singleton energy right there, compressed into pure narrative gold. (Though hopefully your database connection has better intentions than enslaving Middle-earth and corrupting hobbits.)

The **visual metaphor** is perfect: one ring, one dark lord, one object of power. Jackson even gives us that iconic **close-up shot** - the ring filling the frame, singular and terrible. THAT is production design serving story structure, my friends.

-----

### The Robert McKee Story Breakdown

Now, if you’ve read Robert McKee’s seminal work “*Story: Substance, Structure, Style, and the Principles of Screenwriting*” (and if you haven’t, close this tab right now and go get it - I’ll wait), you know that every story is built on **dramatic structure**. McKee teaches us that story is about a protagonist pursuing an object of desire against antagonistic forces.

So let’s break down the Singleton pattern using McKee’s **story spine**:

- **Protagonist**: The Application (our **hero’s journey** begins here - trying to access a shared resource, facing the chaos of the digital realm)
- **Desire (objective)**: Reliable access to a single, consistent resource (database connection, configuration, logging system) - this is the **want vs. need**. The app *wants* convenience but *needs* consistency.
- **Antagonistic force**: Chaos from multiple competing instances - the **forces of antagonism** that McKee describes: connection pool exhaustion, conflicting configurations, duplicate log files creating narrative entropy
- **Central conflict**: The **gap** between expectation and reality - the tension between the need for “just create another one!” convenience and the harsh truth that some things *must* be singular. This is your **inciting incident** right here.
- **Turning point** (McKee calls this the **Crisis Decision**): The moment when the application realizes that getting “the same object” is *fundamentally different* from getting “a new object with the same values” - this is your **act break**, your **revelation scene**
- **Resolution** (The **Climax**): All parts of the application share the one true instance harmoniously - equilibrium restored, **catharsis** achieved
- **Controlling idea** (McKee’s **thematic premise**): *Unity is achieved through singularity* - some problems require a single source of truth, not multiple competing voices. This is the **thematic statement** that echoes through your entire codebase architecture.

See what McKee taught us? Every design pattern is a three-act structure waiting to happen. The Singleton pattern follows classical **dramatic progression**: setup (multiple instances cause problems), confrontation (we need only one), resolution (we enforce singularity).

It’s *Jaws* for your database connection. You don’t need multiple sharks - one perfect apex predator gets the job done.

-----

### Real-World Implementations (The Production Examples)

You know what’s beautiful about this pattern? You’ve already seen it in the **production environment** - you’ve probably used Singleton patterns without realizing it. These are your **practical applications**, your **proof of concept**:

- **Database connection pools** - You don’t want 500 connections; you want THE connection manager
- **Configuration managers** - One source of truth for app settings
- **Logging systems** - All modules write to THE logger, not their own separate logs
- **Cache managers** - One shared cache, not fragmented memory chaos
- **Thread pools** - One pool managing all workers
- **Application state** - Single source for runtime state (like Redux in React-land)

-----

### The Minimal Python Example (The Visual Effects Sequence)

*Okay, okay. Enough theory. Let me show you the money shot. This is where we go from storyboard to actual footage.*

Here’s Singleton in its simplest form - no CGI, no post-production magic, just pure **practical effects**:

```python
class DatabaseConnection:
    _instance = None  # The "one ring" lives here - our SINGULAR ARTIFACT
    
    def __new__(cls):
        """
        The __new__ method is called BEFORE __init__.
        It's where Python creates the actual object.
        
        Think of __new__ as your CASTING DIRECTOR.
        We hijack it to ensure only ONE actor ever plays this role.
        Every audition returns the SAME performer.
        """
        if cls._instance is None:
            # First time? This is the ORIGIN STORY
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        # Return the SAME instance every time - THE CONTINUITY
        return cls._instance
    
    def __init__(self):
        """
        This still gets called each time, so we use a flag
        to prevent re-initialization.
        
        Think of this as the actor's MAKEUP AND WARDROBE.
        We only apply it once - the first time they step on set.
        """
        if self._initialized:
            return  # Already in costume - we're good to go!
        self._initialized = True
        self.connection = "Connected to database"
        print("🔌 Database connection established!")

# The magic happens here - THIS IS YOUR REVEAL MOMENT:
db1 = DatabaseConnection()  # THE PROTAGONIST enters the scene
db2 = DatabaseConnection()  # Wait... is this a different character?

print(db1 is db2)           # True - PLOT TWIST! Same character!
print(id(db1) == id(db2))   # True - same actor, same memory address

# Both variables point to the SAME instance - THE SHARED REALITY
db1.connection = "Modified connection"
print(db2.connection)       # "Modified connection" - CONTINUITY MAINTAINED!
                            # Change one, change all. Spooky action at a distance!
```

**The Director’s Commentary:**

This is your **behind-the-scenes breakdown**. Let me walk you through the **production workflow**:

1. `__new__` is the **gatekeeper** - your studio security guard. It creates objects BEFORE `__init__` runs. This is **pre-production**.
1. We store the first (and only) instance in `_instance` class variable - this is our **master copy**, our **original negative**.
1. Every subsequent call returns that same instance - perfect **continuity editing**. No jump cuts, no mistakes.
1. The `_initialized` flag prevents re-running initialization code - we don’t re-shoot scenes we’ve already captured.

-----

### When Should You Use Singleton? (The Green Light Decision)

You know what separates a **box office hit** from a **direct-to-video disaster**? Knowing when to use the right technique for the right story.

**✅ Green-lit projects (Good use cases):**

- Database connection pools - *The ensemble cast that needs ONE director*
- Configuration management - *The production bible, the single source of truth*
- Logging systems - *The dailies, all footage goes to ONE editor*
- Caching layers - *The prop department - ONE warehouse, many retrievals*
- Hardware interface managers - *One printer driver, not ten* (one camera operator, not a mob)

**❌ Development hell (When to avoid):**

- “Just because” - don’t use it for everything! (Don’t cast Tom Cruise in EVERY role)
- When you actually need multiple instances - most of the time (Sometimes you need an ensemble, not a one-man show)
- When it makes testing harder - spoiler: it usually does (Can’t test the lead actor if they won’t leave the set)
- When shared global state will cause confusion (Too many cooks, kitchen chaos, you know the drill)

-----

### The Pythonic Alternative: Module-Level Singleton (The Indie Approach)

*Here’s the secret the big studios don’t want you to know.*

You know what’s beautiful? Python modules are *already* singletons! When you import a module, Python caches it - this is **built-in continuity**. Every import returns the same module object. It’s like casting the same actor across multiple films in a **shared universe**.

This is your **guerrilla filmmaking** approach - simple, effective, no complex rigging required:

```python
# config.py - This is your MASTER SCRIPT
class Config:
    def __init__(self):
        self.database_url = "postgresql://localhost/mydb"
        self.debug_mode = True

# Create ONE instance at module level - THE CANONICAL VERSION
config = Config()
```

```python
# anywhere in your app - EVERY SCENE references the same prop
from config import config

print(config.database_url)  # Same object everywhere! CONTINUITY MAGIC!
```

This is simpler, more Pythonic, and you avoid the `__new__` gymnastics. The module system does the singleton work for you - it’s like having **built-in production management**. Python is your assistant director, maintaining consistency across all your scenes.

No complex camera rigs. No elaborate lighting setups. Just pure, simple, effective storytelling.

-----

### The Plot Twist (The Third Act Reversal)

*Now here’s where I need to level with you.*

Singletons are powerful but dangerous - like the One Ring itself, like the Ark of the Covenant, like any **artifact of immense power** in cinema. They introduce **global state** (the villain of clean architecture), make testing harder (how do you reset “the one” between unit test takes?), and create **hidden dependencies** that lurk in your codebase like the shark in *Jaws* - you don’t see it until it’s too late.

In many modern Python applications, **dependency injection frameworks** have largely replaced raw Singleton patterns. But here’s the thing - and McKee would tell you this too - understanding the classic structure makes you appreciate the modern innovations.

You need to understand Singleton because:

1. You’ll see it in **legacy codebases** - a lot (The film archives are full of this technique)
1. The *concept* still matters even if the **production methods** change (Silent films taught us storytelling principles that still apply in the age of CGI)
1. It teaches you how Python object creation works **under the hood** (Understanding practical effects makes you appreciate digital magic)

This is your **film education**. This is your **foundation**.

-----

**🎯 Key Takeaways (The Trailer Moments):**

- Singleton ensures **only one instance** of a class exists - *One ring to rule them all*
- Use `__new__` to **intercept object creation** - Your casting director, your gatekeeper
- Perfect for **shared resources** - Database connections, configs, loggers - the production essentials
- Python modules are **natural singletons** - Built-in continuity, leverage the system
- “There can be only one” - but that doesn’t mean there *should* be (Choose your moments)
- Great power, great responsibility - This isn’t just Spider-Man wisdom, this is **core architectural philosophy**
- McKee’s **story spine** applies to code architecture - Protagonist, desire, antagonism, resolution
- Every pattern is a **three-act structure** waiting to happen

-----

**🎬 Coming Up Next: (The Post-Credits Tease)**

In Episode 2, we’ll explore the **Factory Pattern** - or as I like to call it, “The Sorting Hat of object creation.”

Why decide what type of object to create when you can delegate that decision to something smarter? It’s like casting directors in Hollywood - they don’t ask actors to cast themselves. There’s a **system**, a **process**, a **creative decision-making framework**.

We’re going to talk about *Harry Potter*, we’re going to talk about **character archetypes**, and we’re going to blow your mind with how **factory methods** mirror the **hero’s journey**. Trust me on this one.

Stay tuned, folks. The best is yet to come.

-----

*Enjoying this series? Hit that ❤️ button - it’s like applauding at a premiere! Got thoughts, corrections, or better movie metaphors? The comments section below is your Q&A panel. And if you have a favorite design pattern you’d like to see explained through the lens of cinema, let me know - I’m always looking for the next **story arc**!*

*Remember: Code is storytelling. Every class is a character. Every method is a scene. Every design pattern is a **narrative structure** refined over decades of collective experience. You’re not just writing code - you’re crafting the next great epic.*

**Fade to black. Roll credits.**

-----

**Further Reading (The Bonus Features):**

- [Learning Python Object-Oriented - Design Patterns](https://github.com/vanHeemstraSystems/learning-python-object-oriented/tree/main/800) - *The source material*
- Robert McKee - [*Story: Substance, Structure, Style, and the Principles of Screenwriting*](https://www.mckee.com/story/) - **The master text, required reading**
- [Gang of Four Design Patterns](https://en.wikipedia.org/wiki/Design_Patterns) - The classic tome (heavy reading, but foundational - like studying Citizen Kane)
- [Python’s `__new__` vs `__init__`](https://docs.python.org/3/reference/datamodel.html#object.__new__) - **Official documentation** on object creation (the technical manual)
- [The Lord of the Rings: The Fellowship of the Ring on IMDB](https://www.imdb.com/title/tt0120737/) - **The cinematic reference**, the visual storytelling masterclass
