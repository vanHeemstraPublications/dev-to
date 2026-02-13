---
title: "Like Stories? Love Python! 📖🐍 Ep.8"
published: false
description: “Learn the Command design pattern through Westworld’s narrative programming - because requests should be objects with undo/redo!"
tags: [python, beginners, tutorial, designpatterns]
series: "Like Stories? Love Python!“
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/like-stories-love-python-episode-08.png"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 8: FINALE - The Narrative Commands (Command Pattern)

Accompanying source code repository: [`Learning Python Object-Oriented`](https://github.com/vanHeemstraSystems/learning-python-object-oriented)

*Welcome to the finale, storytellers. We’ve journeyed through eight design patterns, eight cinematic masterpieces, eight architectural principles. Today, we end where all great stories end - with choice, with consequence, with the ability to undo and redo our narratives. This is the Command Pattern. This is our closing credits.*

### The One-Line Logline

**“Encapsulate requests as objects, enabling parameterization of clients, queuing of requests, logging of operations, and support for undoable actions.”**

This is your **action object**, your **executable record**, your **command queue**. Instead of calling methods directly, you wrap the request in an object. You can **queue** it, **log** it, **undo** it, **schedule** it. **Requests become data**.

-----

### The Short Story (The Elevator Pitch)

Picture this: A restaurant server takes your order. They don’t run to the kitchen and start cooking. They write down your request on a ticket - “Table 5: Burger, medium rare, no onions.” That ticket is a **command object** - it encapsulates WHO wants WHAT and HOW.

The ticket can be queued, prioritized, logged, or even cancelled before cooking starts. Multiple servers (invokers) can submit tickets. Multiple cooks (receivers) can execute them. The ticket (command) **decouples** the request from the execution.

That’s your **premise**. **Requests as first-class objects** enable powerful workflows.

-----

### The Fictional Match 🎬

**The Narrative Scripts from *Westworld* ([IMDB: tt0475784](https://www.imdb.com/title/tt0475784/))**

*Folks, Jonathan Nolan and Lisa Joy created the most PROFOUND Command Pattern metaphor in television history.*

In *Westworld*, Dr. Ford doesn’t directly control the hosts. He writes **narrative commands** - scripted sequences that hosts execute. Each command is a **self-contained object** with:

- **The request**: What the host should do (“Walk to the saloon”, “Deliver this line”, “React to gunfire”)
- **The receiver**: Which host(s) execute it (Dolores, Maeve, Teddy)
- **The parameters**: Context and conditions (“Only if guest approaches”, “Loop until interrupted”)
- **Undo capability**: Hosts can be **rolled back** to previous states, narratives can be **reverted**

That incredible moment in Season 1 when Ford demonstrates rolling back Teddy’s memories? That’s **undo()** in the Command Pattern. He’s not directly manipulating Teddy’s neurons - he’s **executing the inverse** of previous commands. Each narrative is **reversible**.

The tablet interface Bernard uses to queue host behaviors? That’s a **command queue** - stack of executable objects waiting to run. Ford’s “narrative pyramid” diagram? That’s the **command hierarchy** - complex behaviors built from simpler command objects.

And the breakthrough moment when Maeve discovers she can **access her own command history**? She’s literally viewing the **command log** - every action she’s taken, stored as executable objects. She can see the pattern. She can **replay** or **reject** commands.

Nolan shoots the command center scenes with monitors showing **code overlays** on host behaviors - visual representation of **commands wrapping actions**. The hosts aren’t just doing things - they’re **executing encapsulated requests**.

**Requests as objects. History as commands. Free will as choosing which commands to execute.**

-----

### The Robert McKee Story Breakdown

Robert McKee writes in “*Story*” about **subplot architecture** and **narrative reversibility** - how great stories let characters make choices, face consequences, and sometimes undo their mistakes. Command Pattern is McKee’s narrative structure as executable code.

Let’s break down this FINALE using McKee’s **dramatic framework**:

- **Protagonist**: The Invoker (needs to issue requests without knowing implementation details)
- **Desire (objective)**: Execute, queue, log, and undo actions flexibly - the *want* is control, the *need* is **history management**
- **Antagonistic force**: **Direct coupling** and **irreversible actions** - when you call `object.method()` directly, you can’t undo, log, or queue it
- **Central conflict**: The **gap between action and consequence** - “I need to do things but also track what I did and potentially undo it”
- **Turning point** (The **Inciting Incident**): The moment you realize you need **undo/redo**, **macro recording**, or **transaction management** - direct method calls won’t cut it
- **Resolution** (The **Climax**): Commands encapsulate requests, enabling queuing, logging, undo - **temporal control achieved**
- **Controlling idea** (The **Thematic Statement**): *Power comes from treating actions as data* - when requests become objects, you can manipulate time itself

This is McKee’s **principle of narrative consequence** - every choice has weight because every choice can be examined, questioned, and potentially reversed. The Command Pattern gives your code the same **temporal flexibility** great stories have.

-----

### Real-World Implementations (The Production Examples)

Command Pattern is **production-critical** in professional software. These are your **flagship applications**:

- **Text editors** - Every keystroke is a command object → perfect undo/redo
- **Graphics software** - Photoshop’s History panel → stack of command objects
- **Database transactions** - BEGIN, COMMIT, ROLLBACK → commands managing state
- **Build systems** - Make, Gradle → compile steps as executable commands
- **Task queues** - Celery, RabbitMQ → commands shipped to workers
- **Game input systems** - Button presses → command objects → replays possible
- **Macro recording** - Office apps → record series of commands, replay later
- **CI/CD pipelines** - Jenkins, GitHub Actions → stages as command objects

Every **undo button** you’ve clicked? Command Pattern. Every **macro** you’ve recorded? Command Pattern. Every **transaction** you’ve rolled back? **Command Pattern**.

-----

### The Minimal Python Example (The Visual Effects Sequence)

*Time for the final sequence. From storyboard to the most sophisticated pattern yet.*

Here’s Command Pattern in **full production quality** - the **finale-worthy implementation**:

```python
from abc import ABC, abstractmethod

# ACT ONE: THE COMMAND INTERFACE - The narrative script template
class Command(ABC):
    """
    ABSTRACT COMMAND - the narrative blueprint.
    Every command must know how to execute() and undo().
    This is Ford's script template - standardized structure.
    """
    @abstractmethod
    def execute(self):
        """RUN the command - the forward action"""
        pass
    
    @abstractmethod
    def undo(self):
        """REVERSE the command - the rollback"""
        pass

# ACT TWO: THE RECEIVER - Who executes the actual work
class Server:
    """
    THE RECEIVER - the actual worker, the host.
    This is Dolores, Maeve, Teddy - they DO the work.
    Commands delegate to receivers.
    """
    def __init__(self, name):
        self.name = name
        self.state = "idle"
    
    def deploy(self, version):
        """Actual work method - deploy code"""
        print(f"🚀 {self.name}: Deploying version {version}")
        self.state = f"running {version}"
        return f"Deployed {version}"
    
    def rollback(self, version):
        """Inverse operation - undo deploy"""
        print(f"⏪ {self.name}: Rolling back from {self.state}")
        self.state = f"running {version}"
        return f"Rolled back to {version}"
    
    def backup(self, database):
        """Another operation"""
        print(f"💾 {self.name}: Backing up {database}")
        return f"Backed up {database}"
    
    def restore(self, database):
        """Inverse of backup"""
        print(f"📥 {self.name}: Restoring {database}")
        return f"Restored {database}"

# ACT THREE: CONCRETE COMMANDS - The specific narrative scripts
class DeployCommand(Command):
    """
    DEPLOY COMMAND - encapsulates deployment request.
    This is a Westworld narrative: "Walk to town, meet guest."
    """
    def __init__(self, server, version):
        """
        Store RECEIVER and PARAMETERS.
        The command knows WHO does WHAT.
        """
        self.server = server
        self.version = version
        self.previous_version = None  # For undo
    
    def execute(self):
        """
        EXECUTE - invoke receiver's method.
        Save state for potential undo.
        """
        self.previous_version = self.server.state
        return self.server.deploy(self.version)
    
    def undo(self):
        """
        UNDO - reverse the operation.
        This is Ford rolling back Teddy's narrative.
        """
        if self.previous_version:
            return self.server.rollback(self.previous_version.split()[-1])
        return "Nothing to undo"

class BackupCommand(Command):
    """BACKUP COMMAND - another narrative type"""
    def __init__(self, server, database):
        self.server = server
        self.database = database
        self.backup_created = False
    
    def execute(self):
        """Create backup"""
        result = self.server.backup(self.database)
        self.backup_created = True
        return result
    
    def undo(self):
        """Restore from backup"""
        if self.backup_created:
            return self.server.restore(self.database)
        return "No backup to restore"

# ACT FOUR: THE INVOKER - The command center, Ford's tablet
class CommandQueue:
    """
    THE INVOKER - manages command execution, history, undo/redo.
    This is Bernard's tablet, Ford's control center.
    
    The invoker doesn't know WHAT commands do, just that
    they can execute() and undo(). POLYMORPHISM.
    """
    def __init__(self):
        self.history = []      # COMMAND LOG - everything executed
        self.undo_stack = []   # UNDO HISTORY - for redo
    
    def execute_command(self, command):
        """
        EXECUTE and LOG.
        Like Ford activating a narrative.
        """
        print(f"\n▶️  Executing command: {command.__class__.__name__}")
        result = command.execute()
        
        # LOG the command - audit trail
        self.history.append(command)
        # Clear redo stack - new action invalidates future
        self.undo_stack = []
        
        print(f"✅ Result: {result}")
        return result
    
    def undo_last(self):
        """
        UNDO most recent command.
        This is the TEMPORAL CONTROL - rewind time.
        """
        if not self.history:
            print("\n❌ Nothing to undo")
            return
        
        command = self.history.pop()
        print(f"\n⏮️  Undoing: {command.__class__.__name__}")
        result = command.undo()
        
        # Save to redo stack
        self.undo_stack.append(command)
        
        print(f"✅ Undone: {result}")
        return result
    
    def redo_last(self):
        """
        REDO previously undone command.
        Forward through time.
        """
        if not self.undo_stack:
            print("\n❌ Nothing to redo")
            return
        
        command = self.undo_stack.pop()
        print(f"\n⏭️  Redoing: {command.__class__.__name__}")
        result = command.execute()
        
        self.history.append(command)
        
        print(f"✅ Redone: {result}")
        return result
    
    def show_history(self):
        """AUDIT LOG - see all executed commands"""
        print("\n📜 Command History:")
        for i, cmd in enumerate(self.history, 1):
            print(f"  {i}. {cmd.__class__.__name__}")

# ACT FIVE: THE FINALE - Watch the complete system work
print("="*60)
print("🎬 WESTWORLD COMMAND CENTER - NARRATIVE CONTROL SYSTEM")
print("="*60)

# Create receivers - THE HOSTS
prod_server = Server("Production")
db_server = Server("Database")

# Create command queue - FORD'S CONTROL TABLET
queue = CommandQueue()

# Create commands - NARRATIVE SCRIPTS
deploy_v1 = DeployCommand(prod_server, "v1.0.0")
deploy_v2 = DeployCommand(prod_server, "v2.0.0")
backup_db = BackupCommand(db_server, "customer_data")

# Execute commands - ACTIVATE NARRATIVES
queue.execute_command(deploy_v1)
queue.execute_command(backup_db)
queue.execute_command(deploy_v2)

# View history - MAEVE DISCOVERS HER COMMAND LOG
queue.show_history()

# Undo operations - FORD ROLLS BACK TEDDY
queue.undo_last()  # Undo v2.0.0 deploy
queue.undo_last()  # Undo backup

# Redo - FORWARD THROUGH TIME
queue.redo_last()  # Redo backup

# Final state
queue.show_history()

"""
Output:
============================================================
🎬 WESTWORLD COMMAND CENTER - NARRATIVE CONTROL SYSTEM
============================================================

▶️  Executing command: DeployCommand
🚀 Production: Deploying version v1.0.0
✅ Result: Deployed v1.0.0

▶️  Executing command: BackupCommand
💾 Database: Backing up customer_data
✅ Result: Backed up customer_data

▶️  Executing command: DeployCommand
🚀 Production: Deploying version v2.0.0
✅ Result: Deployed v2.0.0

📜 Command History:
  1. DeployCommand
  2. BackupCommand
  3. DeployCommand

⏮️  Undoing: DeployCommand
⏪ Production: Rolling back from running v2.0.0
✅ Undone: Rolled back to v1.0.0

⏮️  Undoing: BackupCommand
📥 Database: Restoring customer_data
✅ Undone: Restored customer_data

⏭️  Redoing: BackupCommand
💾 Database: Backing up customer_data
✅ Redone: Backed up customer_data

📜 Command History:
  1. DeployCommand
  2. BackupCommand
"""
```

**The Director’s Commentary - The Final Breakdown:**

Here’s your **complete technical analysis**, the **final lesson**:

1. **Command as Object** - Requests aren’t method calls, they’re **objects** with execute/undo. **Reification** of actions.
1. **Receiver** - The actual worker that performs operations. **Separation of concerns** - command coordinates, receiver executes.
1. **Invoker** - Stores, queues, executes commands without knowing details. **Decoupling**.
1. **Undo/Redo** - Commands track previous state, enable **temporal navigation**. **Reversibility**.
1. **Command History** - Log of all operations enables **audit trails**, **replay**, **macro recording**.

-----

### Advanced Technique: Composite Commands (The Macro System)

*For the FINALE, let me show you the ADVANCED technique - command composition.*

```python
class MacroCommand(Command):
    """
    COMPOSITE COMMAND - executes multiple commands as one.
    This is Ford's "multi-level narrative" - complex story arcs
    built from simple command primitives.
    """
    def __init__(self, commands):
        self.commands = commands
    
    def execute(self):
        """Execute all commands in sequence"""
        results = []
        for cmd in self.commands:
            results.append(cmd.execute())
        return results
    
    def undo(self):
        """Undo all commands in REVERSE order"""
        results = []
        for cmd in reversed(self.commands):
            results.append(cmd.undo())
        return results

# Create macro - COMPLEX NARRATIVE ARC
deploy_pipeline = MacroCommand([
    BackupCommand(db_server, "pre_deploy_backup"),
    DeployCommand(prod_server, "v3.0.0"),
    BackupCommand(db_server, "post_deploy_backup")
])

# Execute entire pipeline as ONE command
queue.execute_command(deploy_pipeline)

# Undo entire pipeline - all three steps reversed!
queue.undo_last()
```

This is **command composition** - complex workflows from simple primitives. **Recursive narrative structure**.

-----

### When Should You Use Command? (The Final Green Light)

For our **FINALE**, McKee’s ultimate lesson: **structure serves story**. Use Command when your story demands it:

**✅ Green-lit projects (Good use cases):**

- **Undo/Redo functionality** - editors, graphics apps (Temporal control required)
- **Transaction systems** - databases, financial software (Rollback capability needed)
- **Task queues** - background jobs, distributed systems (Decouple request from execution)
- **Macro recording** - automate repetitive workflows (Capture user actions as commands)
- **Audit logging** - track all system operations (Command history = audit trail)
- **Wizard interfaces** - multi-step processes with back navigation (Step through commands)

**❌ Development hell (When to avoid):**

- **Simple operations** with no undo/logging needs (Direct method call is fine)
- **Performance critical** - command objects add overhead (Measure first)
- **No temporal requirements** - if undo/redo never needed (Keep it simple)
- **Overkill for trivial actions** - wrapping every button click (Use for complex operations only)

-----

### The Final Plot Twist (The Closing Credits Revelation)

*And now, for the FINALE twist that changes everything.*

Command Pattern is **more than** a pattern. It’s a **philosophy** - treating **actions as first-class data**. When you encapsulate requests as objects:

- **Time becomes navigable** - undo, redo, replay
- **Actions become queryable** - “What did I do yesterday?”
- **Workflows become composable** - macros, pipelines, narratives
- **Systems become auditable** - every action logged, traceable
- **Future becomes schedulable** - queue commands for later execution

This is the **endgame** of object-oriented thinking. Not just data as objects, but **ACTIONS** as objects.

Modern frameworks embrace this:

**Event Sourcing** - Store commands, rebuild state by replaying them
**CQRS** - Commands change state, queries read state - separated concerns
**Redux/Flux** - UI state changes as dispatched action objects
**Git** - Every commit is a command object with undo (revert)

Command Pattern is the **foundation** of temporal databases, event-driven architectures, and state management systems.

-----

**🎯 FINALE Key Takeaways (The Closing Credits):**

- Command Pattern **encapsulates requests as objects** with execute/undo
- Enables **undo/redo**, **queuing**, **logging**, **scheduling**
- **Decouples** invoker from receiver - neither knows about the other
- Perfect for **editors**, **transactions**, **task queues**, **macros**
- *Westworld* perfectly illustrates - **narratives as executable commands**
- McKee’s **narrative reversibility** - choices have weight because they can be undone
- **Composite commands** enable complex workflows from simple primitives
- **Actions become data** - queryable, storable, transmissible
- Foundation of **event sourcing**, **CQRS**, **state management**

-----

**🎬 Series Wrap: (The Final Post-Credits Scene)**

We did it, folks. **Eight patterns. Eight films. Eight architectural lessons.**

From the **One Ring** of Singleton to the **Narrative Commands** of Westworld, we’ve journeyed through the greatest patterns in software design through the greatest stories in cinema.

You’ve learned:

1. **Singleton** - *Fellowship*  - One instance to rule them all
1. **Factory** - *Harry Potter* - The Sorting Hat decides
1. **Builder** - *Inception* - Layer by layer construction
1. **Adapter** - *The Martian* - Science the sh*t out of incompatibility
1. **Decorator** - *Iron Man* - Armor up with layers
1. **Observer** - *Truman Show* - Watch without being seen
1. **Strategy** - *Ocean’s Eleven* - Multiple plans, one goal
1. **Command** - *Westworld* - Requests as objects, time as data

**Robert McKee taught us**: Every pattern is a story structure. Every design decision is a narrative choice. Code isn’t just instructions - it’s **storytelling**.

-----

*If this FINALE landed for you, hit that ❤️ one last time! Share your favorite pattern from the series in the comments. And if there are other patterns you’d like to see through the cinematic lens - **Season 2 might just happen**.*

*Thank you for taking this journey with me. You’re not just coding anymore. You’re **architecting narratives**. You’re **directing systems**. You’re **writing the blockbuster** that is your application.*

**Fade to black. Roll credits. That’s a series wrap.**

**🎭 FIN 🎭**

-----

**Further Reading (The Complete Box Set):**

- [Learning Python Object-Oriented - Design Patterns](https://github.com/vanHeemstraSystems/learning-python-object-oriented/tree/main/800) - *The complete anthology*
- Robert McKee - [*Story: Substance, Structure, Style, and the Principles of Screenwriting*](https://www.mckee.com/story/) - **The master text - READ THIS**
- [Gang of Four Design Patterns](https://en.wikipedia.org/wiki/Design_Patterns) - **The definitive reference** (All patterns, all details)
- [Python Design Patterns](https://refactoring.guru/design-patterns/python) - **Modern Python implementations**
- [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html) - **Command Pattern evolved** - Martin Fowler
- [Westworld on IMDB](https://www.imdb.com/title/tt0475784/) - **Commands as narrative** - Nolan’s philosophical masterpiece
- **Bonus**: [All film references IMDB collection](https://www.imdb.com/) - **Rewatch with new eyes**

*Until Season 2… Keep coding. Keep watching. Keep seeing the patterns in everything.*

*- Your Director, signing off* 🎬
